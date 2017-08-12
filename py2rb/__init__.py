#! /usr/bin/env python

import ast
import six
import inspect
#import formater
from . import formater
import re
import yaml

def scope(func):
    func.scope = True
    return func

class RubyError(Exception):
    pass

class RB(object):

    f = open('ruby.yaml', 'r')
    func_map = yaml.load(f) 
    f.close()

    f = open('module.yaml', 'r')
    module_map = yaml.load(f) 
    f.close()
    #module_map = {
    #    'numpy' : {'id': 'numo/narray', 'order_methods': {'array' : 'Numo::NArray'}, 'reverse_methods': {'sum': 'sum'}}
    #}

    # python 3
    name_constant_map = {
        True  : 'true',
        False : 'false',
        None  : 'nil',
    }
    name_map = {
        #'self'   : 'this',
        'True'  : 'true',  # python 2.x
        'False' : 'false', # python 2.x
        'None'  : 'nil',   # python 2.x
        'zip'   : 'zip_p',
        #'print' : 'puts',
        '__file__' : '__FILE__',
        # ideally we should check, that this name is available:
        #'py_builtins' : '___py_hard_to_collide',
    }

    # isinstance(foo, String) => foo.is_a?(String)
    methods_map_middle = {
        'isinstance' : 'is_a?',
        'hasattr'   : 'respond_to?',
    }
    # np.array([x1, x2]) => Numo::NArray[x1, x2]
    order_methods_without_bracket = {}
    order_methods_with_bracket_2_1_x = {}
    order_methods_with_bracket = {}
    order_methods_with_bracket_1 = {}
    ignore = {}
    range_methods = {}
    mod_class_name = {}
    order_inherited_methods = {}

    # float(foo) => foo.to_f
    reverse_methods = {
        'int'   : 'to_i',
        'float' : 'to_f',
        'str'   : 'to_s',
        'len'   : 'size',
        'max'   : 'max',            # Array
        'min'   : 'min',            # Array
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
        'items'    : '',            # Hash
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

    builtin = set([
        'NotImplementedError',
        'ZeroDivisionError',
        'AssertionError',
        'AttributeError',
        'RuntimeError',
        'ImportError',
        'TypeError',
        'ValueError',
        'NameError',
        'IndexError',
        'KeyError',
        'StopIteration',

        '_int',
        '_float',
        #'max',
        #'min',
        'sum',
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
            'IsNot' : "is not", # Not implemented yet
        }

    def __init__(self):
        self.__formater = formater.Formater()
        self.write = self.__formater.write
        self.read = self.__formater.read
        self.clear = self.__formater.clear
        self.indent = self.__formater.indent
        self.dedent = self.__formater.dedent
        self.dummy = 0
        self.classes = ['dict', 'list', 'tuple']
        # This is the name of the class that we are currently in:
        self._class_name = None
        # This is use () case of the tuple that we are currently in:
        self._is_tuple = False # True : "()" , False : "[]", None: "%s => %s" (Hash)
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
        for method_key, method_value in six.iteritems(self.func_map):
            if method_value != None:
                for key, value in six.iteritems(method_value):
                    RB.__dict__[method_key][key] = value
        try:
            visitor = getattr(self, 'visit_' + self.name(node))
        except AttributeError:
            raise RubyError("syntax not supported (%s)" % node)

        if hasattr(visitor, 'statement'):
            return visitor(node, scope)
        else:
            return visitor(node)

    def visit_Module(self, node):
        """
        Module(stmt* body)
        """
        for stmt in node.body:
            self.visit(stmt)


    @scope
    def visit_FunctionDef(self, node):
        """ [Function Define] :
        FunctionDef(identifier name, arguments args,stmt* body, expr* decorator_list, expr? returns) 
        """
        self._function.append(node.name)
        self._function_args = []
        is_static = False
        is_javascript = False
        if node.decorator_list:
            if len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name) and \
                    node.decorator_list[0].id == "JavaScript":
                is_javascript = True # this is our own decorator
            elif self._class_name and \
                    len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name) and \
                    node.decorator_list[0].id == "staticmethod":
                is_static = True
            else:
                raise RubyError("decorators are not supported")
            if self._class_name and not is_static and not is_javascript:
                raise RubyError("decorators are not supported")

        defaults = [None]*(len(node.args.args) - len(node.args.defaults)) + node.args.defaults
        """ Class Method """
        if self._class_name:
            #if node.decorator_list and not is_static and not is_javascript:
            #    raise RubyError("decorators are not supported")
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
        if self._class_name:
            if not is_static:
                if not (rb_args[0] == "self"):
                    raise NotImplementedError("The first argument must be 'self'.")
                del rb_args[0]
                del rb_args_default[0]

        if '__init__' == node.name:
            func_name = 'initialize'
        elif '__str__' == node.name:
            func_name = 'to_s'
        elif is_static:
            #If method is static, we also add it directly to the class method
            func_name = "self." + node.name
        else:
            # Function Method
            func_name = node.name

        if self._class_name:
            self.indent()

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
            self.dedent()
            self._scope = []
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
                self.indent()
                for t in stmt.targets:
                    var = self.visit(t)
                    self.write("@@%s = %s" % (var, value))
                    self._class_variables.append(var)
                self.dedent()
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

        if len(self._class_self_variables) != 0:
            self.indent()
            self.write("attr_accessor :%s" % ', :'.join(set(self._class_self_variables)))
            self.dedent()

        for func in self._self_functions:
            self.indent()
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
        assert len(node.targets) == 1
        target = node.targets[0]
        #~ if self._class_name:
            #~ target = self._class_name + '.' + target
        # ast.Tuple, ast.List, ast.*
        value = self.visit(node.value)
        #if isinstance(node.value, (ast.Tuple, ast.List)):
        #    value = "[%s]" % self.visit(node.value)
        #else:
        #    value = self.visit(node.value)
        if isinstance(target, (ast.Tuple, ast.List)):
            # multiassign.py
            """ x, y, z = [1, 2, 3] """
            x = [self.visit(t) for t in target.elts]
            self.write("%s = %s" % (','.join(x), value))
        elif isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Index):
            # found index assignment # a[0] = xx
            #self.write("%s%s = %s" % (self.visit(target.value), # a[0] = xx
            name = self.visit(target.value)
            for arg in self._function_args:
                if arg == ("**%s" % name):
                    self._is_string_symbol = True
            self.write("%s[%s] = %s" % (name, self.visit(target.slice), value))
            self._is_string_symbol = False
        elif isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Slice):
            # found slice assignmnet
            self.write("%s[%s...%s] = %s" % (self.visit(target.value),
                self.visit(target.slice.lower), self.visit(target.slice.upper),
                value))
        else:
            if isinstance(target, ast.Name):
                var = self.visit(target)
                if not (var in self._scope):
                    self._scope.append(var)
                    #declare = "var "
                    declare = ""
                else:
                    declare = ""
                if value in self._class_names:
                    """ [create instance] : 
                    <Python> a = foo()
                    <Ruby>   a = Foo.new()
                    """
                    value = (value[0]).upper() + value[1:] + '.new'
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id in self._class_names:
                            self._classes_self_functions_args[var] = self._classes_self_functions_args[node.value.func.id]
                # set lambda functions
                if isinstance(node.value, ast.Lambda):
                    self._lambda_functions.append(var)
                    #print var
                    self.write("%s%s = lambda %s" % (declare, var, value))
                else:
                    self.write("%s%s = %s" % (declare, var, value))
            elif isinstance(target, ast.Attribute):
                var = self.visit(target)
                """ [instance variable] : 
                <Python> self.foo = hoge
                <Ruby>   @foo     = hoge
                """
                if var == 'self':
                    self.write("@%s = %s" % (str(target.attr), value))
                    self._class_self_variables.append(str(target.attr))
                else:
                    self.write("%s = %s" % (var, value))
            else:
                raise RubyError("Unsupported assignment type")

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
            raise RubyError("argument decomposition in 'for' loop is not supported")
        #if isinstance(node.target, ast.Tuple):

        #print self.visit(node.iter) #or  Variable (String case)
        #if isinstance(node.iter, ast.Str):

        self._is_tuple = True
        for_target = self.visit(node.target)
        self._is_tuple = False
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
            <Ruby>   File.open("hello.txt", "w") do |f|
                         f.write("Hello, World!")
                     end
        """
        item_str = ''
        for stmt in node.items:
            item_str += self.visit(stmt)
        self.write(item_str)
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write("end")

    @scope
    def visit_withitem(self, node):
        """
        withitem = (expr context_expr, expr? optional_vars)
        """
        func = self.visit(node.context_expr)
        if isinstance(node.context_expr, (ast.Call)):
            self.visit(node.context_expr)
        val = self.visit(node.optional_vars)
        return "%s do |%s|" % (func, val)

    @scope
    def _visit_Raise(self, node):
        pass

    @scope
    def visit_ExceptHandler(self, node):
        """
        <Python 2> ExceptHandler(expr? type, expr? name, stmt* body)
        <Python 3> ExceptHandler(expr? type, identifier? name, stmt* body)
        """
        if node.type is None:
            self.write("rescue")
        elif node.name is None:
            self.write("rescue %s" % node.type.id)
        else:
            if six.PY2:
                self.write("rescue %s => %s" % (node.type.id, node.name.id))
            else:
                self.write("rescue %s => %s" % (node.type.id, node.name))
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
        test = self.visit(node.test)

        if node.msg is not None:
            self.write("assert(%s, %s);" % (test, self.visit(node.msg)))
        else:
            self.write("assert(%s);" % test)

    def visit_Import(self, node):
        """
        Import(alias* names)

        e.g.
        import imported.module as abc
          => require_relative 'abc'
          => require 'foo'
        Module(body=[Import(names=[alias(name='imported.module', asname='abc')])])
        """
        mod_name = node.names[0].name
        if mod_name not in self.module_map:
            self._import_files.append(mod_name)
            mod_name = node.names[0].name.replace('.', '/')
            self.write("require_relative '%s'" % mod_name)
            return

        if node.names[0].asname == None:
            mod_as_name = mod_name
        else:
            mod_as_name = node.names[0].asname

        for method_key, method_value in six.iteritems(self.module_map[mod_name]):
            if method_value != None:
                if method_key == 'id':
                    self.write("require '%s'" % method_value)
                #elif method_key == 'order_inherited_methods':
                #    # no use mod_as_name (Becase Inherited Methods)
                #    for key, value in six.iteritems(method_value):
                #        RB.__dict__[method_key][key] = value
                else:
                    for key, value in six.iteritems(method_value):
                        mod_org_method = "%s.%s" % (mod_as_name, key)
                        RB.__dict__[method_key][mod_org_method] = value

    def visit_ImportFrom(self, node):
        """
        ImportFrom(identifier? module, alias* names, int? level)

        e.g.
        from foo import bar
          => require 'foo'
             include 'Foo'
        Module(body=[ImportFrom(module='foo', names=[ alias(name='bar', asname=None)], level=0), 
        """
        if node.module not in self.module_map:
            mod_name = node.module.replace('.', '/')
            self.write("require_relative '%s'" % mod_name)
            #self.write("include '%s'" % mod_name[0]upper() + mod_name[1:]) # T.B.D
            return

        mod_name = self.module_map[node.module]
        self.write("require '%s'" % mod_name)

        """ T.B.D
        for method_key, method_value in six.iteritems(self.module_map[node.module]):
            if method_value != None:
                if method_key == 'id':
                    self.write("require '%s'" % method_value)
                    self.write("include '%s'" % method_value)
                else:
                    for key, value in six.iteritems(method_value):
                        RB.__dict__[method_key][key] = value
        """

    def _visit_Exec(self, node):
        pass

    def visit_Global(self, node):
        """
        Global(identifier* names)
        """
        #return self.visit(node.names.upper)
        self._scope.extend(node.names)

    def visit_Expr(self, node):
        self.write(self.visit(node.value))

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
        return ", ".join([self.visit(arg) for arg in node.args])

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
        t = self.visit(node.generators[0].target)
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

    def visit_Lambda(self, node):
        """
        Lambda(arguments args, expr body)
        """
        """ [Lambda Definition] : 
        <Python> lambda x:x*x
        <Ruby>   lambda{|x| x*x}
        """
        #return "function(%s) {return %s}" % (self.visit(node.args), self.visit(node.body))
        #return "lambda{|%s| %s}" % (self.visit(node.args), self.visit(node.body))
        return "{|%s| %s}" % (self.visit(node.args), self.visit(node.body))

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
        assert len(node.ops) == 1
        assert len(node.comparators) == 1
        op = node.ops[0]
        comp = node.comparators[0]
        if isinstance(op, ast.In):
            #return "%s.__contains__(%s)" % (
            return "%s.include?(%s)" % (
                    self.visit(comp),
                    self.visit(node.left),
                    )
        elif isinstance(op, ast.NotIn):
            #return "!(%s.__contains__(%s))" % (
            return "!%s.include?(%s)" % (
                    self.visit(comp),
                    self.visit(node.left),
                    )
        elif isinstance(op, ast.Eq):
            #return "py_builtins.eq(%s, %s)" % (
            return "%s == %s" % (
                    self.visit(node.left),
                    self.visit(comp),
                    )
        elif isinstance(op, ast.NotEq):
            #In fact, we'll have to override this too:
            #return "!(py_builtins.eq(%s, %s))" % (
            return "%s != %s" % (
                    self.visit(node.left),
                    self.visit(comp),
                    )
        else:
            return "%s %s %s" % (self.visit(node.left),
                    self.get_comparison_op(op),
                    self.visit(comp)
                    )

    # python 3
    def visit_Starred(self, node):
        """
        Starred(expr value, expr_context ctx)
        """
        return node.value

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
            id = self.name_map[id]
        except KeyError:
            pass

        #if id in self.builtin:
        #    id = "py_builtins." + id;

        #~ if id in self._classes:
            #~ id = '_' + id;

        return id

    def visit_Num(self, node):
        return str(node.n)

    # Python 3
    def visit_Bytes(self, node):
        """
        Bytes(bytes s)
        """
        return node.s

    def visit_Str(self, node):
        """
        Str(string s)
        """
        # Uses the Python builtin repr() of a string and the strip string type from it.
        txt = re.sub(r'"', '\\"', repr(node.s)[1:-1])
        if self._is_string_symbol:
            txt = ':' + txt
        else:
            txt = '"' + txt + '"'
        return txt

    def visit_Call(self, node):
        """
        Call(expr func, expr* args, keyword* keywords)
        """
        rb_args = [ self.visit(arg) for arg in node.args ]
        self._func_args_len = len(rb_args)
        func = self.visit(node.func)
        for f in self._import_files:
            if func.startswith(f):
                func = func.replace(f + '.', '')

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
        if is_static == False:
            if ((len(rb_args) != 0 ) and (rb_args[0] == 'self')):
                del rb_args[0]
                self._func_args_len = len(rb_args)
        if func_arg != None:
            if ((len(rb_args) != 0 ) and (rb_args[0] == 'self')):
               args = rb_args[1:]
            else:
               args = rb_args
            for i in range(len(args)):
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
        if node.keywords:
            """ [Keyword Argument] : 
            <Python> foo(1, fuga=2):
            <Ruby>   foo(1, fuga:2)
            """
            for kw in node.keywords:
                rb_args.append("%s: %s" % (kw.arg, self.visit(kw.value)))

        if len(rb_args) == 0:
            rb_args_s = ''
        elif len(rb_args) == 1:
            rb_args_s = rb_args[0]
        else:
            rb_args_s = ", ".join(rb_args)

        """ [Class Instance Create] :
        <Python> foo()
        <Ruby>   Foo.new()
        """
        if func in self._class_names:
            func = (func[0]).upper() + func[1:] + '.new'

        #if len(rb_args) == 1:
        #    if func in self.order_methods_with_bracket_1.keys():
        #        if (type(rb_args[0]) == int) or (type(rb_args[0]) == str):
        #            """ [Function convert to Method]
        #            <Python> print(-x)
        #            <Ruby>   puts(-x)
        #            """
        #            return "%s(%s)" % (self.order_methods_with_bracket_1[func], rb_args[0])
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
            return "(%s).%s" % (rb_args_s, self.reverse_methods[func])
        elif func in self.methods_map_middle.keys():
            """ [Function convert to Method]
            <Python> isinstance(foo, String)
            <Ruby>   foo.is_a?String
            """
            return "%s.%s%s" % (rb_args[0], self.methods_map_middle[func], rb_args[1])
        elif func in self.order_methods_without_bracket.keys():
            """ [Function convert to Method]
            <Python> np.array([x1, x2])
            <Ruby>   Numo::NArray[x1, x2]
            """
            return "%s%s" % (self.order_methods_without_bracket[func], rb_args[0])
        elif func in self.order_methods_with_bracket.keys():
            """ [Function convert to Method]
            <Python> np.exp(-x)
            <Ruby>   Numo::NMath.exp(-x)
            """
            return "%s(%s)" % (self.order_methods_with_bracket[func], ','.join(rb_args))
        elif func in self.iter_map:
            """ [map] """
            if isinstance(node.args[0], ast.Lambda):
                """ [Lambda Call with map] :
                <Python> map(lambda x: x**2, [1,2])
                <Ruby>   [1, 2].map{|x| x**2}
                """
                #return "%s.%s{%s}" % (rb_args[1], func, rb_args[0])
                return "%s.%s%s" % (rb_args[1], func, rb_args[0])
            else:
                """ <Python> map(foo, [1, 2])
                    <Ruby>   [1, 2].map{|_|foo(_)} """
                return "%s.%s{|_| %s(_)}" % (rb_args[1], func, rb_args[0])
        elif func in self.range_methods.keys():
            """ [range Function convert to Method]
            <Python> np.arange(-1.0, 1.0, 0.1)
            <Ruby>   Numo::DFloat.new(20).seq(-1,0.1)
            """
            if len(node.args) == 1:
                """ [0, 1, 2, 3, 4, 5] <Python> np.range(6)
                                       <Ruby>   Numo::DFloat.new(6).seq(0) """
                return "%s(%s).seq(0)" % (self.range_methods[func], rb_args[0])
            elif len(node.args) == 2:
                """ [1, 2, 3, 4, 5] <Python> np.range(1,6) # s:start, e:stop
                                    <Ruby>   Numo::DFloat.new(6-1).seq(1) """
                return "%(m)s(%(e)s-(%(s)s)).seq(%(s)s)" % {'m':self.range_methods[func], 's':rb_args[0], 'e':rb_args[1]}
            else:
                """ [1, 3, 5] <Python> np.range(1,6,2) # s:start, e:stop, t:step
                              <Ruby>   Numo::DFloat.new(((6-1)/2.to_f).ceil).seq(1,2) """
                return "%(m)s(((%(e)s-(%(s)s))/(%(t)s).to_f).ceil).seq(%(s)s,%(t)s)" % {'m':self.range_methods[func], 's':rb_args[0], 'e':rb_args[1], 't':rb_args[2]}
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
                return "%s" % (rb_args_s)
        elif func in self.dict_map:
            """ [dict]
            <Python> dict([('foo', 1), ('bar', 2)])
            <Ruby>   {'foo' => 1, 'bar' => 2}
            """
            if len(node.args) == 0:
                return "{}"
            elif len(node.args) == 1:
                rb_args = []
                if isinstance(node.args[0], ast.List):
                    for elt in node.args[0].elts:
                        self._is_tuple = None
                        rb_args.append(self.visit(elt))
                        self._is_tuple = False
            else:
                 raise RubyError("dict in argument list Error")
            return "{%s}" % (", ".join(rb_args))
        elif isinstance(node.func, ast.Lambda):
            """ [Lambda Call] :
            <Python> (lambda x:x*x)(4)
            <Ruby>    lambda{|x| x*x}.call(4)
            """
            return "lambda%s.call(%s)" % (func, rb_args_s)
        elif isinstance(node.func, ast.Attribute) and (node.func.attr in self.call_attribute_map):
            """ [Function convert to Method]
            <Python> ' '.join(['a', 'b'])
            <Ruby>   ['a', 'b'].join(' ')
            """
            return "%s.%s" % (rb_args_s, func)
        elif (func in self._lambda_functions):
            """ [Lambda Call] :
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
                if base_func in self.order_methods_with_bracket.keys():
                    """ [Inherited Instance Method] :
                    <Python> self.assertEqual()
                    <Ruby>   assert_equal()
                    """
                    return "%s(%s)" % (self.order_methods_with_bracket[base_func], ','.join(rb_args))
                if base_func in self.order_methods_with_bracket_2_1_x.keys():
                    """ [Inherited Instance Method] :
                    <Python> self.assertIn('foo', ['foo', 'bar'], 'message test')
                    <Ruby>   assert_include(['foo', 'bar'],'foo','message test')
                    """
                    args_arr = [rb_args[1], rb_args[0]]
                    if len(rb_args) > 2:
                        args_arr += (rb_args[2:])
                    return "%s(%s)" % (self.order_methods_with_bracket_2_1_x[base_func], ','.join(args_arr))
            else:
                if len(rb_args) == 0:
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
            else:
                self.write("raise %s" % self.visit(node.exc))

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
        if not (isinstance(node.value, ast.Name) and (node.value.id == 'self')):
            if attr in self.attribute_map.keys():
                """ [Attribute method converter]
                <Python> fuga.append(bar)
                <Ruby>   fuga.push(bar)   """
                attr = self.attribute_map[attr]
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
                        if func in self.order_methods_with_bracket.keys():
                            return "%s" % (attr)
                        if func in self.order_methods_with_bracket_2_1_x.keys():
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
        # True : () , False : []
        if self._is_tuple == True:
             return "(%s)" % (", ".join(els))
        elif self._is_tuple == False:
             return "[%s]" % (", ".join(els))
        elif self._is_tuple == None:
             return "%s => %s" % (els[0], els[1])
        else:
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
        #return "list([%s])" % (", ".join(els))
        return "[%s]" % (", ".join(els))
        #return ", ".join(els)

    #def bracket(value):
    #    # True : "()" , False : "[]" , None: ""
    #    if self._is_tuple == None:
    #        return value
    #    elif self._is_tuple == True:
    #        return "(%s)" % value
    #    if self._is_tuple == False:
    #        return "[%s]" % value

    #@bracket
    def visit_Slice(self, node):
        """
        Slice(expr? lower, expr? upper, expr? step)
        """
        if node.lower and node.upper and node.step:
            """ <Python> [8, 9, 10, 11, 12, 13, 14][1:6:2]
                <Ruby>   [8, 9, 10, 11, 12, 13, 14][1...6].each_slice(2).map(&:first) """
            return "%s...%s,each_slice(%s).map(&:first)" % (self.visit(node.lower),
                    self.visit(node.upper), self.visit(node.step))
        if node.lower and node.upper:
            #return "slice(%s, %s)" % (self.visit(node.lower),
            #return "[%s...%s]" % (self.visit(node.lower),
            return "%s...%s" % (self.visit(node.lower),
                    self.visit(node.upper))
        if node.upper and not node.step:
            #return "slice(%s)" % (self.visit(node.upper))
            return "0...%s" % (self.visit(node.upper))
            #return "[0...%s]" % (self.visit(node.upper))
        if node.lower and not node.step:
            #return "slice(%s, null)" % (self.visit(node.lower))
            return "%s..-1" % (self.visit(node.lower))
            #return "[%s..-1]" % (self.visit(node.lower))
        if not node.lower and not node.upper and not node.step:
            #return "slice(null)"
            return "0..-1"
            #return "[0..-1]"
        raise NotImplementedError("Slice")

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

def convert_py2rb(s, modules = []):
    """
    Takes Python code as a string 's' and converts this to Ruby.

    Example:

    >>> convert_py2rb("x[3:]")
    'x[3..-1]'

    """
    v = RB()
    for m in modules:
        t = ast.parse(m)
        v.visit(t)
    v.clear()
    t = ast.parse(s)
    v.visit(t)
    return v.read()
