import unittest

class MyException(Exception):
    pass

class Foo:
    def test(self):
        raise MyException

class TestRunnable(unittest.TestCase):

    def test_runnable(self):
        ''' NameError: name 'foo' is not defined '''
        with self.assertRaises(NameError):
            foo

        foo = Foo()
        self.assertRaises(MyException, foo.test)

unittest.main()
