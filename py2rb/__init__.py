#! /usr/bin/env python

import ast
import six
import inspect
import sys
import os.path
from optparse import OptionParser
from . import formater
import re
import yaml
import glob
import copy
from collections import OrderedDict

def scope(func):
    func.scope = True
    return func

class RubyError(Exception):
    pass

class RB(object):

    module_map = {}
    yaml_files = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'modules/*.yaml')
    for filename in glob.glob(yaml_files):
        with open(filename, 'r') as f:
            module_map.update(yaml.load(f))

    # python 3
    name_constant_map = {
        True  : 'true',
        False : 'false',
        None  : 'nil',
    }
    func_name_map = {
        'zip'   : 'zip_p',
        'set'   : 'Set.new',
        #'print' : 'p',
    }
    name_map = {
        #'self'   : 'this',
        'True'  : 'true',  # python 2.x
        'False' : 'false', # python 2.x
        'None'  : 'nil',   # python 2.x
        'str'   : 'String',
        'int'   : 'Integer',
        'float' : 'Float',
        'list'  : 'Array',
        'tuple' : 'Array',
        'dict'  : 'Hash',
        '__file__' : '__FILE__',
    }

    exception_map = {
        'AssertionError'      : 'RuntimeError', # assert => raise
        'AttributeError'      : 'NoMethodError',
        'EOFError'            : 'EOFError',
        'KeyboardInterrupt'   : 'Interrupt',
        'KeyError'            : 'KeyError',
        'MemoryError'         : 'NoMemoryError',
        'NameError'           : 'NameError',
        'ImportError'         : 'LoadError',
        'IndexError'          : 'IndexError',
        'ModuleNotFoundError' : 'LoadError',
        'NameError'           : 'NameError',
        #'NotImplementedError' : 'NotImplementedError',
        'OSError'             : 'IOError',
        'RecursionError'      : 'SystemStackError',
        'RuntimeError'        : 'RuntimeError',
        #'StopIteration'       : 'StopIteration',
        'SyntaxError'         : 'SyntaxError',
        'SystemError'         : 'ScriptError',
        'SystemExit'          : 'SystemExit',
        'TypeError'           : 'ArgumentError',
        'ValueError'          : 'TypeError',
        'ZeroDivisionError'   : 'ZeroDivisionError',
    }

    # isinstance(foo, String) => foo.is_a?(String)
    methods_map_middle = {
        'isinstance' : 'is_a?',
        'hasattr'    : 'instance_variable_defined?',
        #'getattr'    : 'send',
        #'getattr'    : 'method',
        'getattr'    : 'getattr',
    }
    # np.array([x1, x2]) => Numo::NArray[x1, x2]
    order_methods_with_bracket = {}
    methods_map = {}
    ignore = {}
    mod_class_name = {}
    order_inherited_methods = {}

    # float(foo) => foo.to_f
    reverse_methods = {
        'type'  : 'class',
        'abs'   : 'abs',            # Numeric
        'bin'   : 'to_s(2)',
        'oct'   : 'to_s(8)',
        'hex'   : 'to_s(16)',
        'int'   : 'to_i',
        'float' : 'to_f',
        'str'   : 'to_s',
        'len'   : 'size',
        'max'   : 'max',            # Array
        'min'   : 'min',            # Array
        'all'   : 'is_all?',        # Enumerable
        'any'   : 'is_any?',        # Enumerable
        'iter'  : 'each',
        'sum'   : 'sum', # if Ruby 2.3 or bufore is 'inject(:+)' method.
        #'sum'   : 'inject(:+)', # if Ruby 2.4 or later is better sum() method.
    }

    attribute_map = {
        'upper'    : 'upcase',      # String
        'lower'    : 'downcase',    # String
        'append'   : 'push',        # Array
        'sort'     : 'sort!',       # Array
        'reverse'  : 'reverse!',    # Array
        'find'     : 'index',       # String
        'rfind'    : 'rindex',      # String
        'endswith' : 'end_with?',   # String
        'extend'   : 'concat',      # Array
        'replace'  : 'gsub',        # String
        'items'    : 'to_a',        # Hash
    }
    attribute_not_arg = {
        'split'   : 'split',         # String
        'splitlines': 'split("\n")', # String
    }
    attribute_with_arg = {
        'split'   : 'split_p',       # String
    }

    call_attribute_map = set([       # Array
        'join',
    ])

    list_map = set([                 # Array
        'list',
        'tuple',
    ])

    dict_map = set([                 # Hash
        'dict',
    ])

    iter_map = set([                 # Array
        'map',
    ])

    range_map = set([                # Array
        'range',
        'xrange',
    ])

    bool_op = {
        'And'    : '&&',
        'Or'     : '||',
    }

    unary_op = {
        'Invert' : '~',
        'Not'    : '!',
        'UAdd'   : '+',
        'USub'   : '-',
    }

    binary_op = {
        'Add'    : '+',
        'Sub'    : '-',
        'Mult'   : '*',
        'Div'    : '/',
        'FloorDiv' : '/', #'//',
        'Mod'    : '%',
        'LShift' : '<<',
        'RShift' : '>>',
        'BitOr'  : '|',
        'BitXor' : '^',
        'BitAnd' : '&',
    }

    comparison_op = {
            'Eq'    : "==",
            'NotEq' : "!=",
            'Lt'    : "<",
            'LtE'   : "<=",
            'Gt'    : ">",
            'GtE'   : ">=",
            'Is'    : "===",
        }

    # Error Stop Mode
    def mode(self, mode):
        self._mode = mode

    # Convert Staus
    def set_result(self, result):
        if self._result < result:
            self._result = result

    def get_result(self):
        return self._result

    def __init__(self, path='', dir_path='', base_path_count=0, mod_paths = {}, verbose=False):
        self._verbose = verbose
        self._mode = 0 # Error Stop Mode : 0:stop(defalut), 1:warning(for all script mode), 2:no error(for module mode)
        self._result = 0 # Convert Staus : 0:No Error, 1:Include Warning, 2:Include Error
        paths = [x.capitalize() for x in path.split('/')]
        self._dir_path = dir_path
        self._path = []
        for p in paths:
            if p != '__init__':
                self._path.append(p)
        self._base_path_count = base_path_count
        self._module_functions = []
        self._is_module = False
        self.mod_paths = mod_paths
        self._rel_path = []
        for rel_path in self.mod_paths.values():
            self._rel_path.append(rel_path.replace('/', '.'))
        if self._verbose:
            print("base_path_count[%s] dir_path: %s, path : %s : %s" % (self._base_path_count, dir_path, path, self._path))
            print("mod_paths : %s" % self.mod_paths)
        self.__formater = formater.Formater()
        self.capitalize = self.__formater.capitalize
        self.write = self.__formater.write
        self.read = self.__formater.read
        self.clear = self.__formater.clear
        self.indent = self.__formater.indent
        self.dedent = self.__formater.dedent
        self.indent_string = self.__formater.indent_string
        self.dummy = 0
        self.classes = ['dict', 'list', 'tuple']
        # This is the name of the class that we are currently in:
        self._class_name = None
        # This is use () case of the tuple that we are currently in:
        self._tuple_type = '[]' # '()' : "(a, b)" , '[]' : "[a, b]", '=>': "%s => %s" (Hash), '': 'a, b'
        self._func_args_len = 0
        self._dict_format = False # True : Symbol ":", False : String "=>"

        self._is_string_symbol = False # True : ':foo' , False : '"foo"'
        # This lists all variables in the local scope:
        self._scope = []
        #All calls to names within _class_names will be preceded by 'new'
        # Python original class name
        self._class_names = set()
        # Ruby class name (first charcer Capitalize)
        self._rclass_names = set()
        self._classes = {}
        # This lists all function names:
        self._function = []
        # This lists all arguments in a function:
        self._function_args = []
        self._functions = {}
        self._functions_rb_args_default = {}
        # This lists all instance functions in the class scope:
        self._self_functions = []
        self._self_functions_args = {}
        # This lists all static functions (Ruby's class method) in the class scope:
        self._class_functions = []
        self._class_functions_args = {}
        self._classes_class_functions_args = {}
        self._classes_self_functions_args = {}
        self._classes_functions = {}
        self._classes_self_functions = {}
        # This lists all static variables (Ruby's class variables) in the class scope:
        self._class_variables = []
        # This lists all instance variables (Ruby's class variables) in the class scope:
        self._class_self_variables = []
        self._classes_variables = {}
        self._base_classes = []
        # This lists all lambda functions:
        self._lambda_functions = []
        self._import_files = []
        self._imports = []
        self._call = False
        self._conv = True # use YAML convert case.

    def new_dummy(self):
        dummy = "__dummy%d__" % self.dummy
        self.dummy += 1
        return dummy

    def name(self, node):
        return node.__class__.__name__

    def get_bool_op(self, node):
        return self.bool_op[node.op.__class__.__name__]

    def get_unary_op(self, node):
        return self.unary_op[node.op.__class__.__name__]

    def get_binary_op(self, node):
        return self.binary_op[node.op.__class__.__name__]

    def get_comparison_op(self, node):
        return self.comparison_op[node.__class__.__name__]

    def visit(self, node, scope=None):
        if self._mode == 2:
            node_name = self.name(node)
            if node_name not in ['Module', 'ImportFrom', 'Import', 'ClassDef', 'FunctionDef', 'Name', 'Attribute']:
                return ''

        try:
            visitor = getattr(self, 'visit_' + self.name(node))
        except AttributeError:
            if not self._mode:
                self.set_result(2)
                raise RubyError("syntax not supported (%s)" % node)
            else:
                if self._mode == 1:
                    self.set_result(1)
                    sys.stderr.write("Warning : syntax not supported (%s)\n" % node)
                return ''

        if hasattr(visitor, 'statement'):
            return visitor(node, scope)
        else:
            return visitor(node)

    def visit_Module(self, node):
        """
        Module(stmt* body)
        """
        self._module_functions = []
        if self._path != ['']:
            """
            <Python> imported/moduleb.py
            <Ruby>   module Imported (base_path_count=0)
                       module Moduleb (base_path_count=1)
            """
            for i in range(len(self._path)):
                if self._verbose:
                    print("base_path_count : %s, i : %s" % (self._base_path_count, i))
                if i < self._base_path_count:
                    continue
                p = self._path[i]
                if self._verbose:
                    print("p : %s" % p)
                self.write("module %s" % p)
                self._is_module = True
                self.indent()

        for stmt in node.body:
            self.visit(stmt)

        if self._path != ['']:
            if self._module_functions:
                self.write("module_function %s" % ', '.join([':' + x for x in self._module_functions]))
            for i in range(len(self._path)):
                if i < self._base_path_count:
                    continue
                self.dedent()
                self.write("end")

    @scope
    def visit_FunctionDef(self, node):
        """ [Function Define] :
        FunctionDef(identifier name, arguments args,stmt* body, expr* decorator_list, expr? returns) 
        """
        self._function.append(node.name)
        self._function_args = []
        is_static = False
        is_closure = False
        is_property = False
        is_setter = False
        if node.decorator_list:
            if self._class_name:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "classmethod":
                            is_static = True
                        elif decorator.id == "staticmethod":
                            is_static = True
                        elif decorator.id == "property":
                            is_property = True
                            """
                            <Python> @property
                                     def x(self):
                                         return self._x
                            <Ruby>   def x
                                         @_x
                                     end
                            """
                        else:
                            if self._mode == 1:
                                self.set_result(1)
                                sys.stderr.write("Warning : decorators are not supported : %s\n" % self.visit(decorator.id))
                    if isinstance(decorator, ast.Attribute):
                        if self.visit(node.decorator_list[0]) == (node.name + ".setter"):
                            is_setter = True
                            """
                            <Python> @x.setter
                                     def x(self, value):
                                         self._x = value
                            <Ruby>   def x=(val)
                                         @_x=val
                                     end
                            """
                if not is_static and not is_property and not is_setter:
                    if self._mode == 1:
                        self.set_result(1)
                        sys.stderr.write("Warning : decorators are not supported : %s\n" % self.visit(node.decorator_list[0]))

        defaults = [None]*(len(node.args.args) - len(node.args.defaults)) + node.args.defaults
        """ Class Method """
        if self._class_name:
            if six.PY2:
                self._scope = [arg.id for arg in node.args.args]
            else:
                self._scope = [arg.arg for arg in node.args.args]

        # get key for not keyword argument Call.
        rb_args_default = []
        # set normal and keyword argument Call.
        rb_args = []
        for arg, default in zip(node.args.args, defaults):
            if six.PY2:
                if not isinstance(arg, ast.Name):
                    self.set_result(2)
                    raise RubyError("tuples in argument list are not supported")
                arg_id = arg.id
            else:
                arg_id = arg.arg
            if default is None:
                rb_args.append(arg_id)
                rb_args_default.append(None)
            else:
                rb_args.append("%s: %s" % (arg_id, self.visit(default)))
                #rb_args.append("%s=%s" % (arg_id, self.visit(default)))
                rb_args_default.append(arg_id)

        """ [Function method argument with Muliti Variables] : 
        <Python> def foo(fuga, hoge):
                 def bar(fuga, hoge, *piyo):
        <Ruby>   def foo(fuga, hoge)
                 def bar(fuga, hoge, *piyo)
            [Class instance method] : 
        <Python> class foo:
                     def __init__(self, fuga):
                     def bar(self, hoge):
        <Ruby>   class Foo
                     def initialize(fuga)
                     def bar(hoge)
        """
        if len(self._function) != 1:
            is_closure = True
        if self._class_name:
            if not is_static and not is_closure:
                if not (rb_args[0] == "self"):
                    raise NotImplementedError("The first argument must be 'self'.")
                del rb_args[0]
                del rb_args_default[0]

        if '__init__' == node.name:
            func_name = 'initialize'
        elif '__call__' == node.name:
            func_name = 'call'
        elif '__str__' == node.name:
            func_name = 'to_s'
        elif is_static:
            #If method is static, we also add it directly to the class method
            func_name = "self." + node.name
        else:
            # Function Method
            func_name = node.name

        """ star arguments """
        if node.args.vararg:
            if six.PY2:
                vararg = "*%s" % node.args.vararg
            else:
                vararg = "*%s" % self.visit(node.args.vararg)
            rb_args.append(vararg)
            rb_args_default.append([None])

        """ keyword only arguments """
        for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            if six.PY2:
                if not isinstance(arg, ast.Name):
                    self.set_result(2)
                    raise RubyError("tuples in argument list are not supported")
                arg_id = arg.id
            else:
                arg_id = arg.arg
            rb_args.append("%s: %s" % (arg_id, self.visit(default)))
            rb_args_default.append(arg_id)

        """ double star arguments """
        if node.args.kwarg:
            if six.PY2:
                kwarg = "**%s" % node.args.kwarg
            else:
                kwarg = "**%s" % self.visit(node.args.kwarg)
            rb_args.append(kwarg)
            rb_args_default.append([])
        self._function_args = rb_args
        rb_args = ", ".join(rb_args)
        if self._class_name is None:
            self._functions[node.name] = rb_args_default
        else:
            self._functions_rb_args_default[node.name] = rb_args_default

        if is_setter:
            if self._is_module and not self._class_name:
                self._module_functions.append(func_name)
                #self.write("def self.%s=(%s)" % (func_name, rb_args))
            #else:
            #    self.write("def %s=(%s)" % (func_name, rb_args))
            self.write("def %s=(%s)" % (func_name, rb_args))
        elif is_closure:
            """ [function closure] :
            <Python> def foo(fuga):
                         def bar(fuga):

                         bar()
            <Ruby>   def foo(fuga)
                         bar = lambda do |fuga|
                         end
                         bar.()
                     end
            """
            if len(self._function_args) == 0:
                self.write("%s = lambda do" % func_name)
            else:
                self.write("%s = lambda do |%s|" % (func_name, rb_args))
            self._lambda_functions.append(func_name)
        else:
            if self._is_module and not self._class_name:
                self._module_functions.append(func_name)
                #self.write("def self.%s(%s)" % (func_name, rb_args))
            #else:
            #    self.write("def %s(%s)" % (func_name, rb_args))
            self.write("def %s(%s)" % (func_name, rb_args))

        if self._class_name is None:
            #
            #print self._scope
            #
            if six.PY2:
                self._scope = [arg.id for arg in node.args.args]
            else:
                self._scope = [arg.arg for arg in node.args.args]
            self._scope.append(node.args.vararg)

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write('end')

        if self._class_name:
            self._scope = []
        else:
            if node.decorator_list:
                """ [method argument set Method Objec] :
                <Python> @mydecorator
                         def describe():
                             pass
                <Ruby>   def describe()
                         end
                         describe = mydecorator(method(:describe))
                """
                if len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name):
                    self.write('%s = %s(method(:%s))' % (node.name, node.decorator_list[0].id, node.name))
                    #self.write('%s = %s(%s)' % (node.name, node.decorator_list[0].id, node.name))
                    self._scope.append(node.name)

        self._function.pop()
        self._function_args = []

    @scope
    def visit_ClassDef(self, node):
        """ [Class Define] : 
        ClassDef(identifier name,expr* bases, keyword* keywords, stmt* body,expr* decorator_list)
        """
        self._self_functions = []
        self._functions_rb_args_default = {}
        self._class_functions = []
        self._class_variables = []
        self._class_self_variables = []
        self._self_functions_args = {}
        self._class_functions_args = {}
        self._base_classes = []

        # [Inherited Class Name convert]
        # <Python> class Test(unittest.TestCase): => <Ruby> class Test < Test::Unit::TestCase
        bases = [self.visit(n) for n in node.bases]
        # no use Object class
        if 'Object' in bases:
            bases.remove('Object')
        if 'object' in bases:
            bases.remove('object')
        self._base_classes = bases

        base_classes = []
        for base in bases:
            if base in self.mod_class_name.keys():
                base_classes.append(self.mod_class_name[base])
            else:
                base_classes.append(base)

        # [Inherited Class Name] <Python> class foo(bar) => <Ruby> class Foo < Bar
        bases = [cls[0].upper() + cls[1:] for cls in base_classes]

        if not bases:
            bases = []
        class_name = node.name

        # self._classes remembers all classes defined
        self._classes[class_name] = node
        self._class_names.add(class_name)

        # [Class Name]  <Python> class foo: => <Ruby> class Foo
        class_name = class_name[0].upper() + class_name[1:]
        if len(bases) == 0:
            self.write("class %s" % (class_name))
        else:
            self.write("class %s < %s" % (class_name, ', '.join(bases)))
        self.indent()
        self._class_name = class_name
        self._rclass_names.add(class_name)

        from ast import dump
        #~ methods = []
        # set instance method in the class
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                if len(stmt.decorator_list) == 1 and \
                    isinstance(stmt.decorator_list[0], ast.Name) and \
                    stmt.decorator_list[0].id == "staticmethod":
                    self._class_functions.append(stmt.name)
                else:
                    self._self_functions.append(stmt.name)
        if len(self._class_functions) != 0:
            self.write("def method_missing(method, *args)")
            self.indent()
            self.write("self.class.__send__ method, *args")
            self.dedent()
            self.write("end")

        self._classes_functions[node.name] = self._class_functions
        self._classes_self_functions[node.name] = self._self_functions

        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                """ [Class Variable] : 
                <Python> class foo:
                             x
                <Ruby>   class Foo
                             @@x       """
                # ast.Tuple, ast.List, ast.*
                value = self.visit(stmt.value)
                #if isinstance(stmt.value, (ast.Tuple, ast.List)):
                #    value = "[%s]" % self.visit(stmt.value)
                #else:
                #    value = self.visit(stmt.value)
                for t in stmt.targets:
                    var = self.visit(t)
                    self.write("@@%s = %s" % (var, value))
                    self._class_variables.append(var)
            else:
                self.visit(stmt)
        if len(self._functions_rb_args_default) != 0:
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef):
                    if len(stmt.decorator_list) == 1 and \
                        isinstance(stmt.decorator_list[0], ast.Name) and \
                        stmt.decorator_list[0].id == "staticmethod":
                        self._class_functions_args[stmt.name] = self._functions_rb_args_default[stmt.name]
                    else:
                        self._self_functions_args[stmt.name] = self._functions_rb_args_default[stmt.name]

        self._classes_class_functions_args[node.name] = self._class_functions_args
        self._classes_self_functions_args[node.name] = self._self_functions_args
        self._classes_variables[node.name] = self._class_variables
        self._class_name = None

        for v in (self._class_variables):
            self.write("def self.%s; @@%s; end" % (v,v))
            self.write("def self.%s=(val); @@%s=val; end" % (v,v))
            self.write("def %s; @%s = @@%s if @%s.nil?; @%s; end" % (v,v,v,v,v))
            self.write("def %s=(val); @%s=val; end" % (v,v))

        for func in self._self_functions:
            if func in self.attribute_map.keys():
                self.write("alias :%s :%s" % (self.attribute_map[func], func))
        self.dedent()
        self.write("end")
        self._self_functions = []
        self._self_functions_args = {}
        self._functions_rb_args_default = {}
        self._class_functions = []
        self._class_functions_args = {}
        self._class_variables = []
        self._class_self_variables = []
        self._base_classes = []

    def visit_Return(self, node):
        if node.value is not None:
            self.write("return %s" % self.visit(node.value))
        else:
            self.write("return")

    def visit_Delete(self, node):
        """
        Delete(expr* targets)
        """
        id = ''
        num = ''
        key = ''
        slice = ''
        attr = ''
        for stmt in node.targets:
            if isinstance(stmt, (ast.Name)):
                id = self.visit(stmt)
            elif isinstance(stmt, (ast.Subscript)):
                if isinstance(stmt.value, (ast.Name)):
                    id = self.visit(stmt.value)
                if isinstance(stmt.slice, (ast.Index)):
                    if isinstance(stmt.slice.value, (ast.Str)):
                        key = self.visit(stmt.slice)
                    if isinstance(stmt.slice.value, (ast.Num)):
                        num = self.visit(stmt.slice)
                if isinstance(stmt.slice, (ast.Slice)):
                    slice = self.visit(stmt.slice)
            elif isinstance(stmt, (ast.Attribute)):
                if isinstance(stmt.value, (ast.Name)):
                    id = self.visit(stmt.value)
                attr = stmt.attr
        if num != '':
            """ <Python> del foo[0]
                <Ruby>   foo.delete_at[0] """
            self.write("%s.delete_at(%s)" % (id, num))
        elif key != '':
            """ <Python> del foo['hoge']
                <Ruby>   foo.delete['hoge'] """
            self.write("%s.delete(%s)" % (id, key))
        elif slice != '':
            """ <Python> del foo[1:3]
                <Ruby>   foo.slise!(1...3) """
            self.write("%s.slice!(%s)" % (id, slice))
        elif attr != '':
            """ <Python> del foo.bar
                <Ruby>   foo.instance_eval { remove_instance_variable(:@bar) } """
            self.write("%s.instance_eval { remove_instance_variable(:@%s) }" % (id, attr))
        else:
            """ <Python> del foo
                <Ruby>   foo = nil """
            self.write("%s = nil" % (id))

    @scope
    def visit_Assign(self, node):
        """
        Assign(expr* targets, expr value)
        """
        target_str = ''
        value = self.visit(node.value)
        for target in node.targets:
            if isinstance(target, (ast.Tuple, ast.List)):
                # multiassign.py
                """ x, y, z = [1, 2, 3] """
                x = [self.visit(t) for t in target.elts]
                target_str += "%s = " % ','.join(x)
            elif isinstance(target, ast.Subscript):
                name = self.visit(target.value)
                if isinstance(target.slice, ast.Index):
                    # found index assignment # a[0] = xx
                    for arg in self._function_args:
                        if arg == ("**%s" % name):
                            self._is_string_symbol = True
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
                    self._is_string_symbol = False
                elif isinstance(target.slice, ast.Slice):
                    # found slice assignmnet
                    target_str += "%s[%s...%s] = " % (name, self.visit(target.slice.lower), self.visit(target.slice.upper))
                elif isinstance(target.slice, ast.ExtSlice):
                    if self._mode == 1:
                        self.set_result(1)
                        sys.stderr.write("Warning : ExtSlice not supported (%s) in Assign(ast.Subscript)\n" % self.visit(target))
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
                else:
                    if self._mode == 1:
                        self.set_result(1)
                        sys.stderr.write("Warning : Unsupported assignment type (%s) in Assign(ast.Subscript)\n" % self.visit(target))
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
            elif isinstance(target, ast.Name):
                var = self.visit(target)
                if not (var in self._scope):
                    self._scope.append(var)
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id in self._class_names:
                            self._classes_self_functions_args[var] = self._classes_self_functions_args[node.value.func.id]
                # set lambda functions
                if isinstance(node.value, ast.Lambda):
                    self._lambda_functions.append(var)
                target_str += "%s = " % var
            elif isinstance(target, ast.Attribute):
                var = self.visit(target)
                """ [instance variable] : 
                <Python> self.foo = hoge
                <Ruby>   @foo     = hoge
                """
                if var == 'self':
                    target_str += "@%s = " % str(target.attr)
                    self._class_self_variables.append(str(target.attr))
                else:
                    target_str += "%s = " % var
            else:
                if self._mode == 1:
                    self.set_result(1)
                    sys.stderr.write("Warning : Unsupported assignment type (%s) in Assign\n" % self.visit(target))
                target_str += "%s[%s] = " % (name, self.visit(target))
        self.write("%s%s" % (target_str, value))

    def visit_AugAssign(self, node):
        """
        AugAssign(expr target, operator op, expr value)
        """
        # TODO: Make sure that all the logic in Assign also works in AugAssign
        target = self.visit(node.target)
        value = self.visit(node.value)

        if isinstance(node.op, ast.Pow):
            self.write("%s = %s ** %s" % (target, target, value))
        #elif isinstance(node.op, ast.FloorDiv):
        #    #self.write("%s = Math.floor((%s)/(%s));" % (target, target, value))
        #    self.write("%s = (%s/%s)" % (target, target, value))
        elif isinstance(node.op, ast.Div):
            if re.search(r"Numo::", target) or re.search(r"Numo::", value):
                self.write("%s = (%s)/(%s)" % (target, target, value))
            else:
                self.write("%s = (%s)/(%s).to_f" % (target, target, value))
        else:
            self.write("%s %s= %s" % (target, self.get_binary_op(node), value))

    @scope
    def visit_For(self, node):
        """
        For(expr target, expr iter, stmt* body, stmt* orelse)
        """
        if not isinstance(node.target, (ast.Name,ast.Tuple, ast.List)):
            self.set_result(2)
            raise RubyError("argument decomposition in 'for' loop is not supported")
        #if isinstance(node.target, ast.Tuple):

        #print self.visit(node.iter) #or  Variable (String case)
        #if isinstance(node.iter, ast.Str):

        self._tuple_type = '()'
        for_target = self.visit(node.target)
        self._tuple_type = '[]'
        #if isinstance(node.iter, (ast.Tuple, ast.List)):
        #    for_iter = "[%s]" % self.visit(node.iter)
        #else:
        #    for_iter = self.visit(node.iter)
        # ast.Tuple, ast.List, ast.*
        for_iter = self.visit(node.iter)

        iter_dummy = self.new_dummy()
        orelse_dummy = self.new_dummy()
        exc_dummy = self.new_dummy()

        self.write("for %s in %s" % (for_target, for_iter))
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write("end")

        if node.orelse:
            self.write("if (%s) {" % orelse_dummy)
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
            self.write("}")

    @scope
    def visit_While(self, node):
        """
        While(expr test, stmt* body, stmt* orelse)
        """

        if not node.orelse:
            self.write("while (%s)" % self.visit(node.test))
        else:
            orelse_dummy = self.new_dummy()

            self.write("var %s = false;" % orelse_dummy)
            self.write("while (1) {");
            self.write("    if (!(%s)) {" % self.visit(node.test))
            self.write("        %s = true;" % orelse_dummy)
            self.write("        break;")
            self.write("    }")

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()

        self.write("end")

        if node.orelse:
            self.write("if (%s) {" % orelse_dummy)
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
            self.write("}")

    def visit_IfExp(self, node):
        """
        IfExp(expr test, expr body, expr orelse)
        """
        body     = self.visit(node.body)
        or_else  = self.visit(node.orelse)
        if isinstance(node.test, (ast.NameConstant, ast.Compare)):
            return "(%s) ? %s : %s" % (self.visit(node.test), body, or_else)
        else:
            return "is_bool(%s) ? %s : %s" % (self.visit(node.test), body, or_else)

    @scope
    def visit_If(self, node):
        """
        If(expr test, stmt* body, stmt* orelse)
        """
        if isinstance(node.test, (ast.NameConstant, ast.Compare)):
            self.write("if %s" % self.visit(node.test))
        else:
            self.write("if is_bool(%s)" % self.visit(node.test))

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        if node.orelse:
            self.write("else")
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
        self.write("end")

    @scope
    def visit_With(self, node):
        """
        With(withitem* items, stmt* body)
        """
        """ <Python> with open("hello.txt", 'w') as f:
                         f.write("Hello, world!")
            <Ruby>   File.open("hello.txt", "w") {|f|
                         f.write("Hello, World!")
                     }
            <Python> with open("hello.txt", 'r'):
                         print("Hello, world!")
            <Ruby>   File.open("hello.txt", "r"){
                         print("Hello, world!")
                     }
        """
        item_str = ''
        for stmt in node.items:
            item_str += self.visit(stmt)
        self.write(item_str)
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write("}")

    @scope
    def visit_withitem(self, node):
        """
        withitem = (expr context_expr, expr? optional_vars)
        """
        func = self.visit(node.context_expr)
        if isinstance(node.context_expr, (ast.Call)):
            self.visit(node.context_expr)
        if node.optional_vars == None:
            return "%s {" % func
        else:
            val = self.visit(node.optional_vars)
            return "%s {|%s|" % (func, val)

    @scope
    def visit_ExceptHandler(self, node):
        """
        <Python 2> ExceptHandler(expr? type, expr? name, stmt* body)
        <Python 3> ExceptHandler(expr? type, identifier? name, stmt* body)
        """
        """ <Python> try:
                     except AttributeError as e:
            <Ruby>   begin
                     rescue AttributeError => e
                     end
            <Python> try:
                     except cuda.cupy.cuda.runtime.CUDARuntimeError as e:
            <Ruby>   begin
                     rescue AttributeError
                     end
        """

        if node.type is None:
            self.write("rescue")
        elif node.name is None:
            self.write("rescue %s" % self.visit(node.type))
        else:
            if six.PY2:
                self.write("rescue %s => %s" % (self.visit(node.type), node.name.id))
            else:
                self.write("rescue %s => %s" % (self.visit(node.type), node.name))
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()

    # Python 3
    @scope
    def visit_Try(self, node):
        """
        Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
        """
        self.write("begin")
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        for handle in node.handlers:
            self.visit(handle)
        if len(node.finalbody) != 0:
            self.write("ensure")
            self.indent()
            for stmt in node.finalbody:
                self.visit(stmt)
            self.dedent()
        self.write("end")

    # Python 2
    @scope
    def visit_TryExcept(self, node):
        """
        TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
        """
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        for handle in node.handlers:
            self.visit(handle)

    # Python 2
    @scope
    def visit_TryFinally(self, node):
        """
        TryFinally(stmt* body, stmt* finalbody)
        """
        self.write("begin")
        self.visit(node.body[0]) # TryExcept
        self.write("ensure")
        self.indent()
        for stmt in node.finalbody:
            self.visit(stmt)
        self.dedent()
        self.write("end")

    def visit_Assert(self, node):
        """
        Assert(expr test, expr? msg)
        """
        test = self.visit(node.test)

        if node.msg is not None:
            self.write("raise %s unless %s" % (self.visit(node.msg), test))
        else:
            self.write("raise unless %s" % test)

    def visit_Import(self, node):
        """
        Import(alias* names)

        e.g.
        <python> import imported.submodules.submodulea
        <ruby>   require_relative 'imported/submodules/submodulea'
        Module(body=[Import(names=[alias(name='imported.module', asname='abc')])])

        <python> import imported.submodules.submodulea (with foo.py, bar.py)
        <ruby>   require_relative 'imported/submodules/submodulea/foo'
                 require_relative 'imported/submodules/submodulea/bar'

        * Case 1. import module
        <python> * tests/modules/import.py
                   import imported.moduleb
                   foo.moduleb_fn()
                   mb = foo.moduleb_class()
        <ruby>   * tests/modules/import_as_module.rb
                   require_relative 'imported/moduleb'
                   Imported::Moduleb::moduleb_fn()
                   mb = Imported::Moduleb::Moduleb_class.new()
        * Case 2. import module with alias
        <python> * tests/modules/import_as_module.py
                   import imported.moduleb as foo
                   foo.moduleb_fn()
                   mb = foo.moduleb_class()
        <ruby>   * tests/modules/import_as_module.rb
                   require_relative 'imported/moduleb'
                   Foo = Imported::Moduleb
                   Foo::moduleb_fn()
                   mb = Foo::Moduleb_class.new()
        """
        mod_name = node.names[0].name
        if self._verbose:
            print("Import mod_name : %s mod_paths : %s" % (mod_name, self.mod_paths))
        if mod_name not in self.module_map:
            mod_name = node.names[0].name.replace('.', '/')
            for path, rel_path in self.mod_paths.items():
                if self._verbose:
                    print("Import mod_name : %s rel_path : %s" % (mod_name, rel_path))
                if (rel_path.startswith(mod_name + '/') or mod_name.endswith(rel_path)) and os.path.exists(path):
                    self._import_files.append(os.path.join(self._dir_path, rel_path).replace('/', '.'))
                    if self._verbose:
                         print("Import self._import_files: %s" % self._import_files)
                    self.write("require_relative '%s'" % rel_path)

            if node.names[0].asname != None:
                if node.names[0].name in self._import_files:
                    base = '::'.join([self.capitalize(x) for x in node.names[0].name.split('.')[self._base_path_count:]])
                    self.write("%s = %s" % (self.capitalize(node.names[0].asname), base))
                    self._import_files.append(node.names[0].asname)
                # No Use
                #elif node.names[0].name in self._class_names:
                #    self.write("%s = %s" % (self.capitalize(node.names[0].asname), self.capitalize(node.names[0].name)))
                #    self._class_names.add(node.names[0].asname)
                #    self._classes_self_functions_args[node.names[0].asname] = self._classes_self_functions_args[node.names[0].name]
                #else:
                #    self.write("alias %s %s" % (node.names[0].asname, node.names[0].name))
            return

        if node.names[0].asname == None:
            mod_as_name = mod_name
        else:
            mod_as_name = node.names[0].asname

        if 'mod_name' in self.module_map[mod_name]:
            _mod_name = self.module_map[mod_name]['mod_name']
        else:
            _mod_name = ''

        for method_key, method_value in six.iteritems(self.module_map[mod_name]):
            if method_value == None:
                continue
            if method_key == 'mod_name':
                continue

            if method_key == 'id':
                if not node.names[0].name in self._imports:
                    self.write("require '%s'" % method_value)
                    self._imports.append(node.names[0].name)
            elif method_key in ('range_map', 'dict_map'):
                for key, value in six.iteritems(method_value):
                    mod_org_method = "%s.%s" % (mod_as_name, key)
                    RB.__dict__[method_key].add(mod_org_method)
            #elif method_key == 'order_inherited_methods':
            #    # no use mod_as_name (Becase Inherited Methods)
            #    for key, value in six.iteritems(method_value):
            #        RB.__dict__[method_key][key] = value
            else: # method_key == 'methods_map', etc..
                for key, value in six.iteritems(method_value): # method_value: {'array':, 'prod': .. }
                    mod_org_method = "%s.%s" % (mod_as_name, key)
                    RB.__dict__[method_key][mod_org_method] = value
                    if isinstance(RB.__dict__[method_key][mod_org_method], dict):
                        RB.__dict__[method_key][mod_org_method]['mod'] = _mod_name + '::'

    def visit_ImportFrom(self, node):
        """
        ImportFrom(identifier? module, alias* names, int? level)

        e.g.
        * Case 1. import function
          <python> * tests/modules/import.py
                     from modules.modulea import modulea_fn
                     modulea_fn()
                   * tests/modules/imported/modulea.py
                     def modulea_fn():
          <ruby>   * tests/modules/import.rb
                     require_relative 'imported/modulea'
                     include Imported::Modulea
                     modulea_fn()
                   * tests/modules/imported/modulea.rb
                     module Imported
                       module Modulea
                         def modulea_fn()
          Module(body=[ImportFrom(module='modules.modulea', names=[ alias(name='modulea_fn', asname=None)], level=0)])

        * Case 2. import function with alias
          <python> * tests/modules/import_alias.py
                     from imported.alias_fns import foo as bar
                     bar()
                   * tests/modules/imported/alias_fns.py
                     def foo():
          <ruby>   * tests/modules/import_alias.rb
                     require_relative 'imported/alias_fns'
                     include Imported::Alias_fns
                     alias bar foo
                     bar()
                   * tests/modules/imported/alias_fns.rb
                     module Imported
                       module Alias_fns
                         def foo()
                         end
                         module_function :foo
          Module(body=[ImportFrom(module='imported.alias_fns', names=[ alias(name='foo', asname='bar')], level=0)])

        * Case 3. import module
          <Python> * tests/modules/imported/modulee.py
                     from imported.submodules import submodulea
                     def bar():
                         submodulea.foo()
                   * tests/modules/imported/submodules/submodulea.py
                     def foo():
          <Ruby>   * tests/modules/imported/modulee.rb
                     module Imported
                       module Modulee
                         require_relative 'submodules/submodulea'
                         include Imported::Submodules
                         def bar()
                           Submodulea::foo()
                   * tests/modules/imported/submodules/submodulea.rb
                     module Imported
                       module Submodules
                         module Submodulea
                           def foo()

        * Case 4. import module with alias
          <Python> * tests/modules/from_import_as_module.py
                     from imported import moduleb as foo
                     foo.moduleb_fn()
                   * tests/modules/imported/moduleb.py
                     def moduleb_fn():
          <Ruby>   * tests/modules/imported/modulee.rb
                     require_relative 'imported/moduleb'
                     include Imported
                     Foo = Moduleb
                     Foo::moduleb_fn()
                   * tests/modules/imported/moduleb.rb
                     module Imported
                       module Moduleb
                         def moduleb_fn()

        * Case 5. import class with alias
          <python> * tests/modules/import_alias.py
                     from imported.alias_classes import spam as eggs
                     e = eggs()
                   * tests/modules/imported/alias_classes.py
                     class spam:
          <ruby>   * tests/modules/import_alias.rb
                     require_relative 'imported/alias_classes'
                     include Imported::Alias_fns
                     Eggs = Spam
                     e = Eggs.new()
                   * tests/modules/imported/alias_classes.rb
                     module Imported
                       module Alias_classes
                         class Spam
        """
        if self._verbose:
            print("mod_paths : %s" % self.mod_paths)
        if node.module != None and \
           node.module not in self.module_map:
            self._import_files.append(node.module)
            mod_name = node.module.replace('.', '/')
            mod_name_i = node.module.replace('.', '/') + '/' + node.names[0].name
            #        from imported.submodules import submodulea
            # => require_relative 'submodules/submodulea'
            if self._verbose:
                print("ImportFrom mod_name : %s mod_name_i: %s" % (mod_name , mod_name_i))
            for path, rel_path in self.mod_paths.items():
                if self._verbose:
                    print("ImportFrom mod_name : %s rel_path : %s" % (mod_name, rel_path))
                if node.names[0].name != '*':
                    if path.endswith(mod_name_i + '.py'):
                        self.write("require_relative '%s'" % rel_path)
                        dir_path = os.path.relpath(mod_name, self._dir_path)
                        if dir_path != '.':
                            self._import_files.append(os.path.relpath(rel_path, dir_path).replace('/', '.'))
                        else:
                            self._import_files.append(rel_path.replace('/', '.'))
                        if self._verbose:
                            print("ImportFrom self._import_files: %s" % self._import_files)
                        break
                if path.endswith(mod_name + '.py'):
                    self.write("require_relative '%s'" % rel_path)
                    break
            else:
                self.write("require_relative '%s'" % mod_name)
            base = '::'.join([self.capitalize(x) for x in node.module.split('.')[self._base_path_count:]])
            self.write("include %s" % base)

            if node.names[0].asname != None:
                if node.names[0].name in self._import_files:
                    base = '::'.join([self.capitalize(x) for x in node.names[0].name.split('.')[self._base_path_count:]])
                    self.write("%s = %s" % (self.capitalize(node.names[0].asname), base))
                    self._import_files.append(node.names[0].asname)
                elif node.names[0].name in self._class_names:
                    self.write("%s = %s" % (self.capitalize(node.names[0].asname), self.capitalize(node.names[0].name)))
                    self._class_names.add(node.names[0].asname)
                    self._classes_self_functions_args[node.names[0].asname] = self._classes_self_functions_args[node.names[0].name]
                else:
                    self.write("alias %s %s" % (node.names[0].asname, node.names[0].name))
            return

        """
        <python> from numpy import array
                     array([1, 1])
        <ruby>   require 'numo/narray'
                 include Numo
                 NArray[1, 1]
        ImportFrom(module='numpy', names=[ alias(name='array', asname=None)], level=0),
        Expr( value= Call(
              func= Name(id='array', ctx= Load()),
              args=[ List(elts=[ Num(n=1), Num(n=1)], ctx= Load())], keywords=[]))
        """
        # Not Use?
        #if node.module == None:
        #    mod_name = node.names[0].name
        #else:
        #    mod_name = self.module_map[node.module]
        if node.module not in self.module_map:
            return

        if 'mod_name' in self.module_map[node.module].keys():
            _mod_name = self.module_map[node.module]['mod_name']
        else:
            _mod_name = ''

        for method_key, method_value in six.iteritems(self.module_map[node.module]):
            if method_key == 'id':
                if node.module not in self._imports:
                    self.write("require '%s'" % method_value)
                    self._imports.append(node.module)

        for method_key, method_value in six.iteritems(self.module_map[node.module]):
            if method_value == None:
                continue
            if method_key == 'id':
                continue

            if method_key == 'mod_name':
                self.write("include %s" % method_value)
            else: # method_key == 'methods_map', etc..
                for key, value in six.iteritems(method_value): # method_value: {'array':, 'prod': .. }
                    if type(RB.__dict__[method_key]) != dict:
                        continue
                    if key not in RB.__dict__[method_key].keys():
                        RB.__dict__[method_key][key] = value
                    if isinstance(RB.__dict__[method_key][key], dict):
                        if node.names[0].name == '*':
                            RB.__dict__[method_key][key]['mod'] = ''
                        elif node.names[0].name == key:
                            RB.__dict__[method_key][key]['mod'] = ''
                        else:
                            RB.__dict__[method_key][key]['mod'] = _mod_name + '::'

    def _visit_Exec(self, node):
        pass

    def visit_Global(self, node):
        """
        Global(identifier* names)
        """
        #return self.visit(node.names.upper)
        self._scope.extend(node.names)

    def visit_Expr(self, node):
        """
        Expr(expr value)
        """
        val =  self.visit(node.value)
        if isinstance(node.value, ast.Str):
            """
            <Python> "" * comment
                            * sub comment ""
            <Ruby>   # * comment
                     #     * sub comment
            """
            comment = val[1:-1]
            indent = self.indent_string()
            for s in comment.split('\n'):
                s = re.sub(r'^%s' % indent, '', s)
                self.write("# %s" % s)
        else:
            self.write(val)

    def visit_Pass(self, node):
        self.write("# pass")
        #self.write("/* pass */")

    def visit_Break(self, node):
        self.write("break")

    def visit_Continue(self, node):
        self.write("next")

    # Python 3
    def visit_arg(self, node):
        """
        (identifier arg, expr? annotation)
           attributes (int lineno, int col_offset)
        """
        return node.arg

    def visit_arguments(self, node):
        """
        <Python 2> (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
        <Python 3> (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults, arg? kwarg, expr* defaults)
        """
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        if node.vararg:
            if six.PY2:
                args.append("*%s" % node.vararg)
            else:
                args.append("*%s" % self.visit(node.vararg))
        return ", ".join(args)

    def visit_GeneratorExp(self, node):
        """
        GeneratorExp(expr elt, comprehension* generators)
        """
        #if isinstance(node.generators[0].iter, (ast.Tuple, ast.List)):
        #    i = "[%s]" % self.visit(node.generators[0].iter)
        #else:
        #    i = self.visit(node.generators[0].iter)
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        t = self.visit(node.generators[0].target)
        """ <Python> [x**2 for x in [1,2]]
            <Ruby>   [1, 2].map{|x| x**2}  """
        return "%s.map{|%s| %s}" % (i, t, self.visit(node.elt))

    def visit_ListComp(self, node):
        """
        ListComp(expr elt, comprehension* generators)
        """
        #if isinstance(node.generators[0].iter, (ast.Tuple, ast.List)):
        #    i = "[%s]" % self.visit(node.generators[0].iter)
        #else:
        #    i = self.visit(node.generators[0].iter)
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        if isinstance(node.generators[0].target, ast.Name):
            t = self.visit(node.generators[0].target)
        else:
            # ast.Tuple
            self._tuple_type = ''
            t = self.visit(node.generators[0].target)
            self._tuple_type = '[]'
        if len(node.generators[0].ifs) == 0:
            """ <Python> [x**2 for x in [1,2]]
                <Ruby>   [1, 2].map{|x| x**2}  """

            return "%s.map{|%s| %s}" % (i, t, self.visit(node.elt))
        else:
            """ <Python> [x**2 for x in [1,2] if x > 1]
                <Ruby>   [1, 2].select {|x| x > 1 }.map{|x| x**2}  """
            return "%s.select{|%s| %s}.map{|%s| %s}" % \
                    (i, t, self.visit(node.generators[0].ifs[0]), t, \
                     self.visit(node.elt))

    def visit_DictComp(self, node):
        """
        DictComp(expr key, expr value, comprehension* generators)
        """
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        if isinstance(node.generators[0].target, ast.Name):
            t = self.visit(node.generators[0].target)
        else:
            # ast.Tuple
            self._tuple_type = ''
            t = self.visit(node.generators[0].target)
            self._tuple_type = '[]'
        if len(node.generators[0].ifs) == 0:
            """ <Python> {key: data for key, data in {'a': 7}.items()}
                <Ruby>   {'a', 7}.to_a.map{|key, data| [key, data]}.to_h  """
            return "%s.map{|%s|[%s, %s]}.to_h" % (i, t, self.visit(node.key), self.visit(node.value))
        else:
            """ <Python> {key: data for key, data in {'a': 7}.items() if data > 6}
                <Ruby>   {'a', 7}.to_a.select{|key, data| data > 6}.map{|key, data| [key, data]}.to_h  """
            return "%s.select{|%s| %s}.map{|%s|[%s, %s]}.to_h" % \
                    (i, t, self.visit(node.generators[0].ifs[0]), t, \
                     self.visit(node.key), self.visit(node.value))

    def visit_Lambda(self, node):
        """
        Lambda(arguments args, expr body)
        """
        """ [Lambda Definition] : 
        <Python> lambda x,y :x*y
        <Ruby>   lambda{|x,y| x*y}
        <Python> lambda *x: print(x)
        <Ruby>   lambda {|*x| print(x)}
        <Python> def foo(x, y):
                     x(y)
                 foo(lambda x: print(a), a)
        <Ruby>   def foo(x, y)
                     x.(y)
                 end
                 foo(lambda{|x| print(a)}, a)
        """
        return "lambda{|%s| %s}" % (self.visit(node.args), self.visit(node.body))

    def visit_BoolOp(self, node):
        return self.get_bool_op(node).join([ "(%s)" % self.visit(val) for val in node.values ])

    def visit_UnaryOp(self, node):
        return "%s(%s)" % (self.get_unary_op(node), self.visit(node.operand))

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Str):
            left = self.visit(node.left)
            # 'b=%(b)0d and c=%(c)d and d=%(d)d' => 'b=%<b>0d and c=%<c>d and d=%<d>d'
            left = re.sub(r"(.+?%)\((.+?)\)(.+?)", r"\1<\2>\3", left)
            self._dict_format = True
            right = self.visit(node.right)
            self._dict_format = False
            return "%s %% %s" % (left, right)
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Pow):
            return "%s ** %s" % (left, right)
        if isinstance(node.op, ast.Div):
            if re.search(r"Numo::", left) or re.search(r"Numo::", right):
                return "(%s)/(%s)" % (left, right)
            else:
                return "(%s)/(%s).to_f" % (left, right)

        return "(%s)%s(%s)" % (left, self.get_binary_op(node), right)

    @scope
    def visit_Compare(self, node):
        """
        Compare(expr left, cmpop* ops, expr* comparators)
        """
        assert len(node.ops) == len(node.comparators)

        def compare_pair(left, comp, op):
            if (left == '__name__') and (comp == '"__main__"') or \
               (left == '"__main__"') and (comp == '__name__'):
                """ <Python>  __name__ == '__main__':
                    <Ruby>    __FILE__ == $0          """
                left = '__FILE__'
                comp = '$0'
            if isinstance(op, ast.In):
                return "%s.include?(%s)" % (comp, left)
            elif isinstance(op, ast.NotIn):
                return "!%s.include?(%s)" % (comp, left)
            elif isinstance(op, ast.Eq):
                return "%s == %s" % (left, comp)
            elif isinstance(op, ast.NotEq):
                return "%s != %s" % (left, comp)
            elif isinstance(op, ast.IsNot):
                return "!%s.equal?(%s)" % (left, comp)
            else:
                return "%s %s %s" % (left, self.get_comparison_op(op), comp)

        compare_list = []
        for i in range(len(node.ops)):
            if i == 0:
                left = self.visit(node.left)
            else:
                left = comp
            comp = self.visit(node.comparators[i])
            op = node.ops[i]
            pair = compare_pair(left, comp, op)
            if len(node.ops) == 1:
                return pair
            compare_list.append('(' + pair + ')')
        return ' and '.join(compare_list)

    # python 3
    def visit_Starred(self, node):
        """
        Starred(expr value, expr_context ctx)
        """
        return "*%s" % self.visit(node.value)

    # python 3
    def visit_NameConstant(self, node):
        """
        NameConstant(singleton value)
        """
        value = node.value
        value = self.name_constant_map[value]
        return value

    def visit_Name(self, node):
        """
        Name(identifier id, expr_context ctx)
        """
        id = node.id
        try:
            if self._call:
                id = self.func_name_map[id]
            else:
                if id in self.methods_map.keys():
                    rtn = self.get_methods_map(self.methods_map[id])
                    if rtn != '':
                        id = rtn
                else:
                    id = self.name_map[id]
        except KeyError:
            pass

        try:
            id = self.exception_map[id]
        except KeyError:
            pass

        return id

    def visit_Num(self, node):
        return str(node.n)

    # Python 3
    def visit_Bytes(self, node):
        """
        Bytes(bytes s)
        """
        return node.s

    # Python 3
    def visit_Ellipsis(self, node):
        """
        Ellipsis
        """
        return 'false'

    def visit_Str(self, node):
        """
        Str(string s)
        """
        # Uses the Python builtin repr() of a string and the strip string type from it.
        txt = re.sub(r'"', '\\"', repr(node.s)[1:-1])
        txt = re.sub(r'\\n', '\n', txt)
        if self._is_string_symbol:
            txt = ':' + txt
        else:
            txt = '"' + txt + '"'
        return txt

    # method_map : self.methods_map[func] # e.g. numpy[methods_map][prod]
    def get_methods_map(self, method_map, rb_args=False, ins=False):
        """ [Function convert to Method]
        <Python> np.prod(shape, axis=1, keepdims=True)
        <Ruby>   Numo::NArray[shape].prod(axis:1, keepdims:true)
        """
        if rb_args == False:
            if 'key' in method_map.keys():
                return ''

        key_list = False
        key_order_list = False
        if rb_args != False:
            if 'key' in method_map.keys():
                """ key: - ['stop']                           : len(rb_args) == 1
                         - ['start', 'stop', 'step', 'dtype'] : len(rb_args) != 1
                """
                for l in method_map['key']:
                    if len(rb_args) == len(l):
                        key_list = l
                        break
                else:
                    key_list = l
            if 'key_order' in method_map.keys():
                for l in method_map['key_order']:
                    if len(rb_args) == len(l):
                        key_order_list = l
                        break
                else:
                    key_order_list = l

        rtn = False
        if rb_args != False:
            if 'rtn' in method_map.keys():
                for i in range(len(method_map['rtn'])):
                    if len(rb_args) == i + 1:
                        rtn = method_map['rtn'][i]
                        break
                else:
                    rtn = method_map['rtn'][-1]

        mod = ''
        if 'mod' in method_map.keys():
            mod = method_map['mod']

        bracket = True
        if 'bracket' in method_map.keys():
            if method_map['bracket'] == False:
                bracket = False
        main_data = ''
        main_func = ''
        m_args = []
        args_hash = {}
        func_key = method_map.get('main_func_key', '')  # dtype
        if rb_args:
            for i in range(len(rb_args)):
                if ': ' in rb_args[i]:
                    key, value = rb_args[i].split(': ', 1)
                else:
                    key = key_list[i]
                    value = rb_args[i]
                args_hash[key] = value
            if key_order_list != False:
                key_list = key_order_list
            for key in key_list:
                if key == func_key:
                    continue
                if key not in args_hash:
                    continue
                value = args_hash[key]
                if key in method_map['val'].keys():
                    if method_map['val'][key] == True:
                        m_args.append(value)
                    elif type(method_map['val'][key]) == str:
                        m_args.append("%s: %s" % (key, value))
            if len(args_hash) == 0:
                self.set_result(2)
                raise RubyError("methods_map defalut argument Error : not found args")

            if 'main_data_key' in method_map:
                data_key = method_map['main_data_key']
                main_data = args_hash[data_key]

        if 'main_func' in method_map.keys():
            main_func = method_map['main_func'] % {'mod': mod, 'data': main_data}
        else:
            for kw, val in args_hash.items():
                if kw in method_map['val'].keys() and kw == func_key:
                    for key in method_map['main_func_hash'].keys():
                        """ [Function convert to Method]
                        <Python> dtype=np.int32
                        <Ruby>   Numo::Int32
                        """
                        if "%s" in key:
                            key2 = (key % ins) # key2: np.int32
                        if val == key2:
                            main_func = method_map['main_func_hash'][key] 
            else:
                if main_func == '' and 'main_func_hash_nm' in method_map.keys():
                    main_func = method_map['main_func_hash_nm']
            main_func = method_map['val'][func_key] % {'mod': mod, 'data': main_data, 'main_func': main_func}
        if main_func == '':
            self.set_result(2)
            raise RubyError("methods_map main function Error : not found args")

        if rtn:
            rtn = rtn % args_hash
            return "%s%s" % (main_func, rtn)

        if bracket:
            return "%s(%s)" % (main_func, ', '.join(m_args))
        else:
            return "%s%s" % (main_func, ', '.join(m_args))

    def visit_Call(self, node):
        """
        Call(expr func, expr* args, keyword* keywords)
        """
        rb_args = [ self.visit(arg) for arg in node.args ]
        """ [method argument set Method Object] :
        <Python> def describe():
                     return "world"
                 describe = mydecorator(describe)
        <Ruby>   def describe()
                     return "world"
                 end
                 describe = mydecorator(method(:describe))
        """
        self._func_args_len = len(rb_args)
        if not isinstance(node.func, ast.Call):
            self._call = True
        func = self.visit(node.func)
        if not isinstance(node.func, ast.Call):
            self._call = False
        if not func in self.iter_map:
            for i in range(len(rb_args)):
                if rb_args[i] in self._functions.keys():
                    if rb_args[i][-1] != ')' and \
                       not rb_args[i] in self._scope:
                        rb_args[i] = 'method(:%s)' % rb_args[i]

        for f in self._import_files:
            if self._verbose:
                print("Call func: %s : f %s" % (func, f))
            if func.startswith(f):
                if self._verbose:
                    print("Call func: %s " % func)
                func = func.replace(f + '.', '', 1)
                """ <Python> imported.moduleb.moduleb_class
                    <Ruby>   Imported::Moduleb::Moduleb_class (base_path_count=0)
                                       Moduleb::Moduleb_class (base_path_count=1)
                """
                if func in self._class_names:
                    func = self.capitalize(func) + '.new'
                """ <Python> * tests/modules/imported/modulec.py
                               import imported.submodules.submodulea
                               imported.submodules.submodulea.foo()
                    <Ruby>   * tests/modules/imported/modulec.rb
                               require_relative 'submodules/submodulea'
                               Submodules::Submodulea::foo()
                """
                base = '::'.join([self.capitalize(x) for x in f.split('.')[self._base_path_count:]])
                if base != '':
                    func = base + '::' + func
                if self._verbose:
                    print("Call func: %s" % func)
                break

            f = '.'.join(f.split('.')[self._base_path_count:])
            x = [x for x in self._rel_path if x.startswith(f + '.')]
            if len(x) != 0:
                f = x[0].replace(f + '.', '')

            if func.startswith(f):
                if self._verbose:
                    print("Call mod_paths : func : %s " % func)
                func = func.replace(f + '.', '')
                if func in self._class_names:
                    func = self.capitalize(func) + '.new'
                """ <Python> * tests/modules/imported/modulee.py
                               from imported.submodules import submodulea
                               submodulea.foo()
                    <Ruby>   * tests/modules/imported/modulee.rb
                               require_relative 'submodules/submodulea'
                               include Submodules
                               Submodulea::foo()
                """
                base = '::'.join([self.capitalize(x) for x in f.split('.')])
                if base != '':
                    func = base + '::' + func
                if self._verbose:
                    print("Call func: %s" % func)
                break

        """ [Class Instance Create] :
        <Python> foo()
        <Ruby>   Foo.new()
        """
        if func in self._class_names:
            func = self.capitalize(func) + '.new'

        """ [method argument set Keyword Variables] :
        <Python> def foo(a, b=3):
                 foo(a, 5)
        <Ruby>   def foo (a, b: 3)
                 foo(a, b:5)
        """
        func_arg = None
        is_static = False
        if func.find('.') == -1:
            if (func in self._functions) and \
               (not ([None] in self._functions[func])):
                func_arg = self._functions[func]
            ins = ''
        else:
            ins, method = func.split('.', 1)
            if (method in self._class_functions):
                is_static = True
            if (ins in self._classes_class_functions_args) and \
               (method in self._classes_class_functions_args[ins]) and \
               (not ([None] in self._classes_class_functions_args[ins][method])):
                func_arg = self._classes_class_functions_args[ins][method]
            if (ins in self._classes_self_functions_args) and \
               (method in self._classes_self_functions_args[ins]) and \
               (not ([None] in self._classes_self_functions_args[ins][method])):
                func_arg = self._classes_self_functions_args[ins][method]

        if func in self.methods_map_middle.keys():
            if func == 'hasattr':
                """ [Function convert to Method]
                <Python> hasattr(foo, bar)
                <Ruby>   foo.instance_variable_defined? :@bar
                """
                return "%s.%s :@%s" % (rb_args[0], self.methods_map_middle[func], rb_args[1][1:-1])
            elif func == 'getattr':
                if len(rb_args) == 2:
                    return "%s.%s(%s)" % (rb_args[0], self.methods_map_middle[func], rb_args[1])
                else:
                    return "%s.%s(%s, %s)" % (rb_args[0], self.methods_map_middle[func], rb_args[1], rb_args[2])
            else:
                """ [Function convert to Method]
                <Python> isinstance(foo, String)
                <Ruby>   foo.is_a?String
                """
                if len(rb_args) == 1:
                    return "%s.%s" % (rb_args[0], self.methods_map_middle[func])
                else:
                    return "%s.%s %s" % (rb_args[0], self.methods_map_middle[func], rb_args[1])

        if is_static == False:
            if ((len(rb_args) != 0 ) and (rb_args[0] == 'self')):
                del rb_args[0]
                self._func_args_len = len(rb_args)

        """ Use keywoard argments in function defined case."""
        if func_arg != None:
            if ((len(rb_args) != 0 ) and (rb_args[0] == 'self')):
               args = rb_args[1:]
            else:
               args = rb_args
            for i in range(len(args)):
                #print("i[%s]:%s" % (i, args[i]))
                if len(func_arg) <= i:
                    break
                if (func_arg[i] != None) and (func_arg[i] != []):
                    rb_args[i] = "%s: %s" % (func_arg[i], rb_args[i])

        self._func_args_len = 0

        #rb_args = []
        #for arg in node.args:
        #    if isinstance(arg, (ast.Tuple, ast.List)):
        #       rb_args.append("[%s]" % self.visit(arg))
        #    else:
        #       rb_args.append(self.visit(arg))
        # ast.Tuple, ast.List, ast.*
        rb_args_base = copy.deepcopy(rb_args)
        if node.keywords:
            """ [Keyword Argument] : 
            <Python> foo(1, fuga=2):
            <Ruby>   foo(1, fuga:2)
            """
            for kw in node.keywords:
                rb_args.append("%s: %s" % (kw.arg, self.visit(kw.value)))
                self._conv = False
                rb_args_base.append("%s: %s" % (kw.arg, self.visit(kw.value)))
                self._conv = True
        if len(rb_args) == 0:
            rb_args_s = ''
        elif len(rb_args) == 1:
            rb_args_s = rb_args[0]
        else:
            rb_args_s = ", ".join(rb_args)

        if isinstance(node.func, ast.Call):
            return "%s.(%s)" % (func, rb_args_s)

        if func in self.ignore.keys():
            """ [Function convert to Method]
            <Python> unittest.main()
            <Ruby>   ""
            """
            return ""
        elif func in self.reverse_methods.keys():
            """ [Function convert to Method]
            <Python> float(foo)
            <Ruby>   (foo).to_f
            """
            if not isinstance(self.reverse_methods[func],  dict):
                return "(%s).%s" % (rb_args_s, self.reverse_methods[func])
            if len(rb_args) == 1:
                if 'arg_count_1' in self.reverse_methods[func].keys():
                    return "(%s).%s" % (rb_args_s, self.reverse_methods[func]['arg_count_1'])
            else:
                if 'arg_count_2' in self.reverse_methods[func].keys():
                    return "(%s).%s(%s)" % (rb_args[0], self.reverse_methods[func]['arg_count_2'], ", ".join(rb_args[1:]))
        elif func in self.methods_map.keys():
            return self.get_methods_map(self.methods_map[func], rb_args_base, ins)
        elif func in self.order_methods_with_bracket.keys():
            """ [Function convert to Method]
            <Python> os.path.dirnam(name)
            <Ruby>   File.dirname(name)
            """
            return "%s(%s)" % (self.order_methods_with_bracket[func], ','.join(rb_args))
        elif func in self.iter_map:
            """ [map] """
            if isinstance(node.args[0], ast.Lambda):
                """ [Lambda Call with map] :
                <Python> map(lambda x: x**2, [1,2])
                <Ruby>   [1, 2].map{|x| x**2}
                """
                return "%s.%s%s" % (rb_args[1], func, rb_args[0].replace('lambda', ''))
            else:
                """ <Python> map(foo, [1, 2])
                    <Ruby>   [1, 2].map{|_|foo(_)} """
                return "%s.%s{|_| %s(_)}" % (rb_args[1], func, rb_args[0])
        elif func in self.range_map:
            """ [range] """
            if len(node.args) == 1:
                """ [0, 1, 2] <Python> range(3)
                              <Ruby>   [].fill(0...3) {|_| _} """
                return "[].fill(0...(%s)){|_| _}" % (rb_args[0])
            elif len(node.args) == 2:
                """ [1, 2] <Python> range(1,3)  # s:start, e:stop
                           <Ruby>   [].fill(0...3-1) {|_| _+1} """
                return "[].fill(0...(%(e)s)-(%(s)s)){|_| _ + %(s)s}" % {'s':rb_args[0], 'e':rb_args[1]}
            else:
                """ [1, 4, 7] <Python> range(1,10,3) # s:start, e:stop, t:step
                              <Ruby>   [].fill(0...10/3-1/3) {|_| _*3+1} """
                return "[].fill(0...(%(e)s)/(%(t)s)-(%(s)s)/(%(t)s)){|_| _*(%(t)s) + %(s)s}" % {'s':rb_args[0], 'e':rb_args[1], 't':rb_args[2]}
        elif func in self.list_map:
            """ [list]
            <Python> list(range(3))
            <Ruby>   [].fill(0...3) {|_| _}
            """
            #return "[].%s" % (rb_args_s)
            if len(node.args) == 0:
                return "[]"
            elif (len(node.args) == 1) and isinstance(node.args[0], ast.Str):
                return "%s.split('')" % (rb_args_s)
            else:
                return "%s.to_a" % (rb_args_s)
        elif func in self.dict_map:
            """ [dict]
            <Python> dict([('foo', 1), ('bar', 2)])
            <Ruby>   {'foo' => 1, 'bar' => 2}
            """
            if len(node.args) == 0:
                return "{}"
            elif len(node.args) == 1:
                if isinstance(node.args[0], ast.List):
                    rb_args = []
                    for elt in node.args[0].elts:
                        self._tuple_type = '=>'
                        rb_args.append(self.visit(elt))
                        self._tuple_type = '[]'
                elif isinstance(node.args[0], ast.Dict):
                    return rb_args[0]
                elif isinstance(node.args[0], ast.Name):
                    return "%s.dup" % rb_args[0]
            else:
                 self.set_result(2)
                 raise RubyError("dict in argument list Error")
            return "{%s}" % (", ".join(rb_args))
        elif isinstance(node.func, ast.Attribute) and (node.func.attr in self.call_attribute_map):
            """ [Function convert to Method]
            <Python> ' '.join(['a', 'b'])
            <Ruby>   ['a', 'b'].join(' ')
            """
            return "%s.%s" % (rb_args_s, func)
        elif isinstance(node.func, ast.Lambda) or \
           (func in self._lambda_functions):
            """ [Lambda Call] :
            <Python> (lambda x:x*x)(4)
            <Ruby>    lambda{|x| x*x}.call(4)
            <Python> foo = lambda x:x*x
                     foo(4)
            <Ruby>   foo = lambda{|x| x*x}
                     foo.call(4)
            """
            return "%s.call(%s)" % (func, rb_args_s)
        else:
            """ [Inherited Instance Method] """
            for base_class in self._base_classes:
                base_func = "%s.%s" % (base_class, func)
                if base_func in self.methods_map.keys():
                    return self.get_methods_map(self.methods_map[base_func], rb_args, ins)
                if base_func in self.order_methods_with_bracket.keys():
                    """ [Inherited Instance Method] :
                    <Python> self.assertEqual()
                    <Ruby>   assert_equal()
                    """
                    return "%s(%s)" % (self.order_methods_with_bracket[base_func], ','.join(rb_args))
            else:
                if (func in self._scope or func[0] == '@') and \
                   func.find('.') == -1: # Proc call
                    return "%s.(%s)" % (func, rb_args_s)

                if func[-1] == ')':
                    return "%s" % (func)
                else:
                    return "%s(%s)" % (func, rb_args_s)

    def visit_Raise(self, node):
        """
        <Python 2> Raise(expr? type, expr? inst, expr? tback)
        <Python 3> Raise(expr? exc, expr? cause)
        """
        if six.PY2:
            assert node.inst is None
            assert node.tback is None
            if node.type is None:
                self.write("raise")
            else:
                self.write("raise %s" % self.visit(node.type))
        else:
            if node.exc is None:
                self.write("raise")
            elif isinstance(node.exc, ast.Name):
                self.write("raise %s" % self.visit(node.exc))
            elif isinstance(node.exc, ast.Call):
                if len(node.exc.args) == 0:
                    self.write("raise %s" % self.visit(node.exc))
                else:
                    """ [Exception] :
                    <Python> raise ValueError('foo.')
                    <Ruby>   raise TypeError, "foo."
                    """
                    self.write("raise %s, %s" % (self.visit(node.exc.func), self.visit(node.exc.args[0])))

    # python 2.x
    def visit_Print(self, node):
        assert node.dest is None
        assert node.nl
        values = [self.visit(v) for v in node.values]
        values = ", ".join(values)
        self.write("print %s" % values)

    def visit_Attribute(self, node):
        """
        Attribute(expr value, identifier attr, expr_context ctx)
        """
        attr = node.attr
        if (attr != '') and isinstance(node.value, ast.Name) and (node.value.id != 'self'):
            mod_attr = "%s.%s" % (self.visit(node.value), attr)
        else:
            mod_attr = ''
        if not (isinstance(node.value, ast.Name) and (node.value.id == 'self')):
            if attr in self.attribute_map.keys():
                """ [Attribute method converter]
                <Python> fuga.append(bar)
                <Ruby>   fuga.push(bar)   """
                attr = self.attribute_map[attr]
            if mod_attr in self.attribute_map.keys():
                """ [Attribute method converter]
                <Python> six.PY3 # True
                <Ruby>   true   """
                return self.attribute_map[mod_attr]
            if self._conv and (attr in self.methods_map.keys()):
                rtn = self.get_methods_map(self.methods_map[attr])
                if rtn != '':
                    return rtn
            if self._conv and (mod_attr in self.methods_map.keys()):
                rtn =  self.get_methods_map(self.methods_map[mod_attr])
                if rtn != '':
                    return rtn
            if self._func_args_len == 0:
                """ [Attribute method converter without args]
                <Python> fuga.split()
                <Ruby>   fuga.split()   """
                if attr in self.attribute_not_arg.keys():
                    attr = self.attribute_not_arg[attr]
            else:
                """ [Attribute method converter with args]
                <Python> fuga.split(foo,bar)
                <Ruby>   fuga.split_p(foo,bar)   """
                if attr in self.attribute_with_arg.keys():
                    attr = self.attribute_with_arg[attr]

        if isinstance(node.value, ast.Call):
            """ [Inherited Class method call]
            <Python> class bar(object):
                         def __init__(self,name):
                             self.name = name
                     class foo(bar):
                         def __init__(self,val,name):
                             super(bar, self).__init__(name)

            <Ruby>   class Bar
                         def initialize(name)
                             @name = name
                         end
                     end
                     class Foo < Bar
                         def initialize(val, name)
                             super(name)
                         end
                     end
            """
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == 'super':
                    if attr == self._function[-1]:
                        return "super"
                    elif (attr in self._self_functions):
                        return "public_method(:%s).super_method.call" % attr
                    else:
                        return attr
        elif isinstance(node.value, ast.Name):
            if node.value.id == 'self':
                if (attr in self._class_functions):
                    """ [Class Method] : 
                    <Python> self.bar()
                    <Ruby>   Foo.bar()
                    """
                    return "%s.%s" % (self._class_name, attr)
                elif (attr in self._self_functions):
                    """ [Instance Method] : 
                    <Python> self.bar()
                    <Ruby>   bar()
                    """
                    return "%s" % (attr)
                else:
                    for base_class in self._base_classes:
                        func = "%s.%s" % (base_class, attr)
                        """ [Inherited Instance Method] : 
                        <Python> self.(assert)
                        <Ruby>   assert()
                        """
                        if func in self.methods_map.keys():
                            return "%s" % (attr)
                        if func in self.order_methods_with_bracket.keys():
                            return "%s" % (attr)
                        if (base_class in self._classes_self_functions) and \
                           (attr in self._classes_self_functions[base_class]):
                            """ [Inherited Instance Method] :
                            <Python> self.bar()
                            <Ruby>   bar()
                            """
                            return "%s" % (attr)
                    else:
                        """ [Instance Variable] : 
                        <Python> self.bar
                        <Ruby>   @bar
                            """
                        self._class_self_variables.append(attr)
                        return "@%s" % (attr)
            elif node.value.id in self._base_classes:
                """ [Inherited Class method call]
                <Python> class bar(object):
                             def __init__(self,name):
                                 self.name = name
                         class foo(bar):
                             def __init__(self,val,name):
                                 bar.__init__(self,name)

                <Ruby>   class Bar
                             def initialize(name)
                                 @name = name
                             end
                         end
                         class Foo < Bar
                             def initialize(val, name)
                                 super(name)
                             end
                         end
                """
                if attr == self._function[-1]:
                    return "super"
                elif (attr in self._self_functions):
                    return "public_method(:%s).super_method.call" % attr
                else:
                    return attr

            elif (node.value.id[0].upper() + node.value.id[1:]) == self._class_name:
                if (attr in self._class_variables):
                    """ [class variable] : 
                    <Python> foo.bar
                    <Ruby>   @@bar
                    """
                    return "@@%s" % (attr)
            elif node.value.id in self._class_names:
                if attr in self._classes_functions[node.value.id]:
                    """ [class variable] : 
                    <Python> foo.bar
                    <Ruby>   Foo.bar
                    """
                    return "%s.%s" % (node.value.id[0].upper() + node.value.id[1:], attr)
            #elif node.value.id in self.module_as_map:
            #    """ [module alias name] : 
            #    <Python> np.array([1, 1])
            #    <Ruby>   Numo::NArray[1, 1]
            #    """
            #    if attr in self.module_as_map[node.value.id].keys():
            #        return "%s" % (self.module_as_map[node.value.id][attr])
            #    """ [module alias name] : 
            #    <Python> np.sum(np.array([1,1]))
            #    <Ruby>   Numo::NArray[1, 1].sum
            #    """
        elif isinstance(node.value, ast.Str):
            if node.attr in self.call_attribute_map:
                """ [attribute convert]
                <Python> ' '.join(*)
                <Ruby>   *.join(' ')
                """
                return "%s(%s)" % (attr, self.visit(node.value))
        if attr != '':
            return "%s.%s" % (self.visit(node.value), attr)
        else:
            return "%s" % self.visit(node.value)

    def visit_Tuple(self, node):
        """
        Tuple(expr* elts, expr_context ctx)
        """
        els = [self.visit(e) for e in node.elts]
        if self._tuple_type == '()':
            return "(%s)" % (", ".join(els))
        elif self._tuple_type == '[]':
            return "[%s]" % (", ".join(els))
        elif self._tuple_type == '=>':
            return "%s => %s" % (els[0], els[1])
        elif self._tuple_type == '':
            return "%s" % (", ".join(els))
        else:
            self.set_result(2)
            raise RubyError("tuples in argument list Error")

    def visit_Dict(self, node):
        """
        Dict(expr* keys, expr* values)
        """
        els = []
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Name):
                els.append('"%s" => %s' % (self.visit(k), self.visit(v)))
            else: # ast.Str, ast.Num
                if self._dict_format == True: # ast.Str
                    els.append("%s: %s" % (self.visit(k), self.visit(v)))
                else: # ast.Str, ast.Num
                    els.append("%s => %s" % (self.visit(k), self.visit(v)))
        return "{%s}" % (", ".join(els))

    def visit_List(self, node):
        """
	List(expr* elts, expr_context ctx)
        """
        #els = []
        #for e in node.elts:
        #    if isinstance(e, (ast.Tuple, ast.List)):
        #        els.append("[%s]" % self.visit(e))
        #    else:
        #        els.append(self.visit(e))
        # ast.Tuple, ast.List, ast.*
        els = [self.visit(e) for e in node.elts]
        return "[%s]" % (", ".join(els))
        #return ", ".join(els)

    def visit_Slice(self, node):
        """
        Slice(expr? lower, expr? upper, expr? step)
        """
        if node.lower and node.upper:
            if node.step:
                """ <Python> [8, 9, 10, 11, 12, 13, 14][1:6:2]
                    <Ruby>   [8, 9, 10, 11, 12, 13, 14][1...6].each_slice(2).map(&:first) """
                return "%s...%s,each_slice(%s).map(&:first)" % (self.visit(node.lower),
                    self.visit(node.upper), self.visit(node.step))
            else:
                return "%s...%s" % (self.visit(node.lower), self.visit(node.upper))
        if node.upper:
            if node.step:
                return "0...%s,each_slice(%s).map(&:first)" % (self.visit(node.upper), self.visit(node.step))
            else:
                return "0...%s" % (self.visit(node.upper))
        if node.lower:
            if node.step:
                return "%s..-1,each_slice(%s).map(&:first)" % (self.visit(node.lower), self.visit(node.step))
            else:
                return "%s..-1" % (self.visit(node.lower))
        if node.step:
            return "0..-1,each_slice(%s).map(&:first)" % self.visit(node.step)
        else:
            return "0..-1"

    def visit_Subscript(self, node):
        self._is_string_symbol = False
        name = self.visit(node.value)
        if isinstance(node.slice, (ast.Index)):
            for arg in self._function_args:
                if arg == ("**%s" % name):
                    self._is_string_symbol = True
            index = self.visit(node.slice)
            self._is_string_symbol = False
            return "%s[%s]" % (name, index)
            #return "%s%s" % (name, index)
        else:
            # ast.Slice
            index = self.visit(node.slice)
            if ',' in index:
                """ [See visit_Slice]
                <Python> [8, 9, 10, 11, 12, 13, 14][1:6:2]
                <Ruby>   [8, 9, 10, 11, 12, 13, 14][1...6].each_slice(2).map(&:first)
                """
                indexs = index.split(',')
                return "%s[%s].%s" % (name, indexs[0], indexs[1])
            else:
                return "%s[%s]" % (name, index)

    def visit_Index(self, node):
        return self.visit(node.value)
        #return "[%s]" % (self.visit(node.value))

    def visit_Yield(self, node):
        """
        <Python> def func():
                     yield 1
                 gen = func()
                 gen.__next__()
        <Ruby>   func = Fiber.new {
                   Fiber.yield 1
                 }
                 func.resume
        """
        if node.value:
            if self._mode == 1:
                self.set_result(1)
                sys.stderr.write("Warning : yield is not supported : %s\n" % self.visit(node.value))
            return "yield %s" % (self.visit(node.value))
        else:
            if self._mode == 1:
                self.set_result(1)
                sys.stderr.write("Warning : yield is not supported : \n")
            return "yield"

def convert_py2rb(s, dir_path, path='', base_path_count=0, modules=[], mod_paths={}, no_stop=False, verbose=False):
    """
    Takes Python code as a string 's' and converts this to Ruby.

    Example:

    >>> convert_py2rb("x[3:]")
    'x[3..-1]'

    """

    # get modules information
    v = RB(path, dir_path, base_path_count, mod_paths, verbose=verbose)
    v.mode(2)
    for m in modules:
        t = ast.parse(m)
        v.visit(t)
    v.clear()

    # convert target file
    t = ast.parse(s)
    if no_stop:
        v.mode(1)
    else:
        v.mode(0)
    v.visit(t)
    return (v.get_result(), v.read())

def convert_py2rb_write(filename, base_path_count=0, subfilenames=[], base_path=None, require=None, builtins=None, output=None, force=None, no_stop=False, verbose=False):
    if output:
        if not force:
            if os.path.exists(output):
                sys.stderr.write('Skip : %s already exists.\n' % output)
                return 3
        output = open(output, "w")
    else:
        output = sys.stdout

    builtins_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'builtins')
    if require:
        if builtins_dir:
            require = open(os.path.join(builtins_dir, "require.rb"))
            using = open(os.path.join(builtins_dir, "using.rb"))
        else:
            require = open("require.rb")
            using = open("using.rb")
        output.write(require.read())
        output.write(using.read())
        require.close
        using.close

    if builtins:
        if builtins_dir:
            builtins = open(os.path.join(builtins_dir, "module.rb"))
            using = open(os.path.join(builtins_dir, "using.rb"))
        else:
            builtins = open("module.rb")
            using = open("using.rb")
        output.write(builtins.read())
        output.write(using.read())
        builtins.close
        using.close

    mods = []
    mod_paths = OrderedDict()
    for sf in subfilenames:
        #print(sf)
        rel_path = os.path.relpath(sf, os.path.dirname(filename))
        name_path, ext = os.path.splitext(rel_path)
        mod_paths[sf] = name_path
        with open(sf, 'r') as f:
            mods.append(f.read()) #unsafe for large files!
    name_path = ''
    dir_path = ''
    if base_path:
        # filename  : tests/modules/classname.py
        # base_path : tests/modules
        dir_path = os.path.relpath(os.path.dirname(filename), base_path)
        if dir_path != '.':
            rel_path = os.path.relpath(filename, base_path)
            name_path, ext = os.path.splitext(rel_path)
        else:
            dir_path = ''
    with open(filename, 'r') as f:
        s = f.read() #unsafe for large files!
        rtn, data = convert_py2rb(s, dir_path, name_path, base_path_count, mods, mod_paths, no_stop=no_stop, verbose=verbose)
        output.write(data)
    output.close
    return rtn

def main():
    parser = OptionParser(usage="%prog [options] filename.py\n" \
        + "    or %prog [-w [-f]] [-(r|b)] [-v] filename.py\n" \
        + "    or %prog -p foo/bar/ -m [-w [-f]] [-(r|b)] [-v] foo/bar/filename.py\n" \
        + "    or %prog -l lib_store_directory/ [-f]",
                          description="Python to Ruby compiler.")

    parser.add_option("-w", "--write",
                      action="store_true",
                      dest="output",
                      help="write output *.py => *.rb")

    parser.add_option("-f", "--force",
                      action="store_true",
                      dest="force",
                      default=False,
                      help="force write output to OUTPUT")

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="verbose option to get more information.")

    parser.add_option("-s", "--silent",
                      action="store_true",
                      dest="silent",
                      default=False,
                      help="silent option that does not output detailed information.")

    parser.add_option("-r", "--include-require",
                      action="store_true",
                      dest="include_require",
                      default=False,
                      help="require py2rb/builtins/module.rb library in the output")

    parser.add_option("-b","--include-builtins",
                      action="store_true",
                      dest="include_builtins",
                      default=False,
                      help="include py2rb/builtins/module.rb library in the output")

    parser.add_option("-p", "--base-path",
                      action="store",
                      dest="base_path",
                      default=False,
                      help="set default module target path")

    parser.add_option("-c", "--base-path-count",
                      action="store",
                      dest="base_path_count",
                      type="int",
                      default=0,
                      help="set default module target path nest count")

    parser.add_option("-m", "--module",
                      action="store_true",
                      dest="mod",
                      default=False,
                      help="convert all local import module files of specified Python file. *.py => *.rb")

    parser.add_option("-l", "--store-library-path",
                      action="store",
                      dest="store_library_path",
                      default=False,
                      help="store py2rb/builtins/module.rb library file in the specified directory")

    options, args = parser.parse_args()

    if options.store_library_path:
        if not os.path.isdir(options.store_library_path):
            sys.stderr.write('Error : %s directory is not exists.\n' % options.store_library_path)
            exit(1)
        builtins_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'builtins')
        output = os.path.join(options.store_library_path, "module.rb")
        if not options.force:
            if os.path.exists(output):
                sys.stderr.write('Error : %s already exists.\n' % output)
                exit(1)
        with open(output, 'w') as f:
            module_f = open(os.path.join(builtins_dir, "module.rb"))
            f.write(module_f.read())
            module_f.close
        sys.stderr.write('OK :  %s file was stored.\n' % output)
        exit(0)

    if len(args) == 0:
        parser.print_help()
        exit(1)

    filename = args[0]

    # base_dir_path : target python file dir path
    # filename: tests/modules/classname.py
    #  -> base_dir_path: tests/modules/
    if options.base_path:
        base_dir_path = options.base_path
    else:
        base_dir_path = os.path.dirname(filename)
    if options.verbose:
        print("base_dir_path: %s" % base_dir_path)
    mods = {}
    mods_all = {}

    # py_path       : python file path
    def get_mod_path(py_path):
        results = set()
        dir_path = os.path.dirname(py_path) if os.path.dirname(py_path) else '.'
        dir_path = os.path.relpath(dir_path, base_dir_path)
        with open(py_path, 'r') as f:
            text = f.read()
            results_f = re.findall(r"^from +([.\w]+) +import +([*\w]+)", text, re.M)
            for res_f in results_f:
                if options.verbose:
                    print("py_path: %s res_f: %s" % (py_path, ', '.join(res_f)))
                if res_f[0] == '.':
                    # from . import hoge
                    res = os.path.normpath(os.path.join(dir_path, res_f[0]))
                elif res_f[0][0] == '.':
                    # from .grandchildren import foo
                    res = os.path.normpath(os.path.join(dir_path, res_f[0][1:]))
                else:
                    # from modules.moda import ModA
                    # => (tests/modules/) modules/moda.py  # => class ModA
                    res = res_f[0]
                results.add(res)
                if res_f[1] != '*':
                    if res_f[0] == '.':
                        # from . import hoge
                        res = os.path.normpath(os.path.join(dir_path, res_f[0], res_f[1]))
                    elif res_f[0][0] == '.':
                        # from .grandchildren import foo
                        res = os.path.normpath(os.path.join(dir_path, res_f[0][1:], res_f[1]))
                    else:
                        # (tests/modules/) modules/moda/ModA.py
                        # (tests/modules/) modules/moda.py
                        res = os.path.normpath(os.path.join(res_f[0], res_f[1]))
                    results.add(res)
            results_f = re.findall(r"^import +([.\w]+)", text, re.M)
            for res_f in results_f:
                # from modules.moda import ModA
                # => (tests/modules/) modules/moda.py  # => class ModA
                # from imported.submodules import submodulea
                # => (tests/modules/) imported/submodules submodulea
                # => require_relative 'submodules/submodulea'
                if res_f == '.':
                    res = dir_path
                else:
                    res = res_f
                results.add(res)
            if options.verbose:
                print("py_path: %s, results: %s" % (py_path, results))
        subfilenames = set()
        if results:
            for result in results:
                sf = os.path.normpath(os.path.join(base_dir_path, result.replace('.', '/') + '.py'))
                if options.verbose:
                    print("sub_filename: %s" % sf)
                if sf in subfilenames:
                    continue
                if os.path.exists(sf):
                    subfilenames.add(sf)
                    if options.verbose:
                        print("[Found]     sub_filename: %s" % sf)
                    continue
                sf = os.path.join(base_dir_path, result.replace('.', '/'), '__init__.py')
                if sf in subfilenames:
                    continue
                if os.path.exists(sf):
                    subfilenames.add(sf)
                    if options.verbose:
                        print("[Found]     sub_filename: %s" % sf)
                    continue
                if options.verbose:
                    print("[Not Found] sub_filename: %s" % sf)
        if options.verbose:
            print("py_path: %s, subfilenames: %s" % (py_path, subfilenames))
        mods[py_path] = subfilenames
        mods_all[py_path] = list(subfilenames)
        for sf in subfilenames:
            if not sf in mods.keys():
                get_mod_path(sf)
                mods_all[py_path].extend(mods[sf])
        return

    # Get all the local import module file names of the target python file
    get_mod_path(filename)

    # Example:
    # tests/modules/classname.py : from modules.moda import ModA     => require_relative 'modules/moda' (Convert using AST)
    #                              => tests/modules/ + modules.moda
    #                              => tests/modules/modules/moda.py
    # -p tests/modules "tests/modules/classname.py"    > "tests/modules/classname.rb"
    # -p tests/modules "tests/modules/modules/moda.py" > "tests/modules/modules/moda.rb"
    if options.verbose:
        for py_path, subfilenames in mods_all.items():
            print("mods_all[%s] : %s" % (py_path, subfilenames))

    for py_path, subfilenames in mods_all.items():
        if not options.mod:
            if py_path != filename:
                continue
        subfilenames = set(subfilenames)
        if options.output:
            name_path, ext = os.path.splitext(py_path)
            output=name_path + '.rb'
        else:
            output=None

        if options.verbose:
            print('Try  : ' + py_path + ' : ')
        rtn = convert_py2rb_write(py_path, options.base_path_count, subfilenames,
            base_path=base_dir_path,
            require=options.include_require, builtins=options.include_builtins,
            output=output, force=options.force, no_stop=True, verbose=options.verbose)
        if not options.silent:
            if options.mod or output:
                if output:
                    print('Try  : ' + py_path + ' -> ' + output + ' : ', end='')
                else:
                    print('Try  : ' + py_path + ' : ', end='')
            if options.mod or output:
                if 0 == rtn:
                    print('[OK]')
                elif 1 == rtn:
                    print('[Warning]')
                elif 2 == rtn:
                    print('[Error]')
                elif 3 == rtn:
                    print('[Skip]')
                else:
                    print('[Not Defined]')

if __name__ == '__main__':
    main()
