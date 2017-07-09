import unittest

class Test_Unit(unittest.TestCase):

    def test_hoge(self):
        self.assertIn('foo', ['foo', 'bar'], 'message test')

unittest.main()
