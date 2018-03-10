import unittest

class MyException(Exception):
    pass

class MyException2(Exception):
    pass

class MyException3(Exception):
    pass

class Foo:
    def test(self):
        raise MyException

class Bar:
    def test(self, a, b, c=1, d=2):
        if a != 'a':
            raise MyException

        if c == 1:
            raise MyException2
        else:
            raise MyException3

def test(a, b, c=1, d=2):
    if a != 'a':
        raise MyException

    if c == 1:
        raise MyException2
    else:
        raise MyException3

def test2():
    raise MyException

class TestRunnable(unittest.TestCase):

    def bar(self):
        assert False

    def test_runnable(self):
        ''' NameError: name 'foo' is not defined '''
        with self.assertRaises(NameError):
            foo

        foo = Foo()
        self.assertRaises(MyException, foo.test)

        bar = Bar()
        self.assertRaises(MyException, bar.test,'aa', 'b')
        self.assertRaises(MyException2, bar.test,'a', 'b')
        self.assertRaises(MyException2, bar.test,'a', 'b', d=20)
        self.assertRaises(MyException3, bar.test,'a', 'b', c=10, d=20)

        self.assertRaises(MyException, test, 'aa', 'b', c=10, d=20)
        self.assertRaises(MyException2, test, 'a', 'b')
        self.assertRaises(MyException3, test, 'a', 'b', c=10, d=20)
        self.assertRaises(MyException, test2)
        self.assertRaises(AssertionError, self.bar)

class TestRunnable2(TestRunnable):

    def test_runnable2(self):
        self.assertRaises(AssertionError, self.bar)

unittest.main()
