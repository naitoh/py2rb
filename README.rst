py2rb.py
========

A code translator using AST from Python to Ruby.
This is basically a NodeVisitor with ruby output.
See ast documentation (https://docs.python.org/3/library/ast.html) for more information.

Installation
------------

Execute the following::

    pip install py2rb

    or

    git clone git://github.com/naitoh/py2rb.git

Dependencies
------------

- Python 3.5, 3.6
- Ruby 2.4 or later


Usage
--------

Sample 1::

    $ cat tests/basic/oo_inherit_simple.py
    class bar(object):

        def __init__(self,name):
            self.name = name

        def setname(self,name):
            self.name = name

    class foo(bar):

        registered = []

        def __init__(self,val,name):
            self.fval = val
            self.register(self)
            self.name = name

        def inc(self):
            self.fval += 1

        def msg(self, a=None, b=None, c=None):
            txt = ''
            varargs = a, b, c
            for arg in varargs:
                if arg is None:
                    continue
                txt += str(arg)
                txt += ","
            return txt + self.name + " says:"+str(self.fval)

        @staticmethod
        def register(f):
            foo.registered.append(f)

        @staticmethod
        def printregistered():
            for r in foo.registered:
                print(r.msg())

    a = foo(10,'a')
    a.setname('aaa')
    b = foo(20,'b')
    c = foo(30,'c')

    a.inc()
    a.inc()
    c.inc()

    print(a.msg())
    print(b.msg())
    print(c.msg(2,3,4))

    print("---")

    foo.printregistered()

The above will result in ::

    $ py2rb tests/basic/oo_inherit_simple.py
    class Bar
      def initialize(name)
        @name = name
      end
      def setname(name)
        @name = name
      end
    end
    class Foo < Bar
      def method_missing(method, *args)
        self.class.__send__ method, *args
      end
      @@registered = []
      def initialize(val, name)
        @fval = val
        Foo.register(self)
        @name = name
      end
      def inc()
        @fval += 1
      end
      def msg(a: nil, b: nil, c: nil)
        txt = ""
        varargs = [a, b, c]
        for arg in varargs
          if arg === nil
            next
          end
          txt += (arg).to_s
          txt += ","
        end
        return (((txt)+(@name))+(" says:"))+((@fval).to_s)
      end
      def self.register(f)
        @@registered.push(f)
      end
      def self.printregistered()
        for r in @@registered
          print(r.msg())
        end
      end
      def self.registered; @@registered; end
      def self.registered=(val); @@registered=val; end
      def registered; @registered = @@registered if @registered.nil?; @registered; end
      def registered=(val); @registered=val; end
    end
    a = Foo.new(10, "a")
    a.setname("aaa")
    b = Foo.new(20, "b")
    c = Foo.new(30, "c")
    a.inc()
    a.inc()
    c.inc()
    print(a.msg())
    print(b.msg())
    print(c.msg(a: 2, b: 3, c: 4))
    print("---")
    Foo.printregistered()

Sample 2::

    $ cat tests/deep-learning-from-scratch/and_gate.py
    # coding: utf-8
    import numpy as np

    def AND(x1, x2):
        x = np.array([x1, x2])
        w = np.array([0.5, 0.5])
        b = -0.7
        tmp = np.sum(w*x) + b
        if tmp <= 0:
            return 0
        else:
            return 1

    if __name__ == '__main__':
        for xs in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            y = AND(xs[0], xs[1])
            print(str(xs) + " -> " + str(y))

The above will result in ::

    $ py2rb tests/deep-learning-from-scratch/and_gate.py
    require 'numo/narray'
    def AND(x1, x2)
      x = Numo::NArray.cast([x1, x2])
      w = Numo::NArray.cast([0.5, 0.5])
      b = -(0.7)
      tmp = (((w)*(x)).sum())+(b)
      if tmp <= 0
        return 0
      else
        return 1
      end
    end
    if __FILE__ == $0
      for xs in [[0, 0], [1, 0], [0, 1], [1, 1]]
        y = AND(xs[0], xs[1])
        print((((xs).to_s)+(" -> "))+((y).to_s))
      end
    end

Sample 3 (Convert all local dependent module files of specified Python file)::

    $ git clone git://github.com/chainer/chainer.git
    $ py2rb chainer/chainer/__init__.py -m -p chainer -r -w -f
    Try : chainer/chainer/__init__.py -> chainer/chainer/__init__.rb : [OK]
    Warning : yield is not supported :
    Warning : yield is not supported :
    Try  : chainer/chainer/configuration.py -> chainer/chainer/configuration.rb : [Warning]
    Try  : chainer/chainer/cuda.py -> chainer/chainer/cuda.rb : [OK]
          :
          :
    Try  : chainer/chainer/utils/array.py -> chainer/chainer/utils/array.rb : [OK]

Tests
-----

$ ./run_tests.py

Will run all tests, that are supposed to work. If any test fails, it's a bug.

$ ./run_tests.py -a

Will run all tests including those that are known to fail (currently). It
should be understandable from the output.

$ ./run_tests.py -x
or
$ ./run_tests.py --no-error

Will run tests but ignore if an error is raised by the test. This is not
affecting the error generated by the test files in the tests directory.

For more flags then described here

./run_tests.py -h


License
-------

MIT, see the LICENSE file for exact details.
