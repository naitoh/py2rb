import unittest

class Test_Unit(unittest.TestCase):

    def test_hoge(self):
        self.assertIsInstance('foo', str)
        self.assertIsInstance(1, int, 'message test')

unittest.main()
