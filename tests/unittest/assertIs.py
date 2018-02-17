import unittest

class Test_Unit(unittest.TestCase):

    def test_hoge(self):
        self.assertIs('foo', 'foo', 'message test')

unittest.main()
