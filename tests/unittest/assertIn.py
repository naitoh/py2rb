import unittest

class Test_Unit(unittest.TestCase):

    def test_hoge(self):
        self.assertIn('foo', ['foo', 'bar'], 'message test')
        self.assertIn('foo', ['foo', 'bar'])

    def test_notin(self):
        self.assertNotIn('baz', ['foo', 'bar'], 'message test')
        self.assertNotIn('baz', ['foo', 'bar'])

unittest.main()
