import unittest

class TestRunnable(unittest.TestCase):

    def test_eq(self):
        self.assertEqual('test', 'test', '''comment test''')
        self.assertEqual(1, 1)
    def test_neq(self):
        self.assertNotEqual(7, 8, '''comment test''')
        self.assertNotEqual(1, 2)

unittest.main()
