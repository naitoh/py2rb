import unittest

class TestRunnable(unittest.TestCase):

    def test_gt(self):
        self.assertGreater(10, 1, '''comment test''')
        self.assertGreater(10, 1)
    def test_lt(self):
        self.assertLess(1, 10, '''comment test''')
        self.assertLess(1, 10)
    def test_gte(self):
        self.assertGreaterEqual(11, 10, '''comment test''')
        self.assertGreaterEqual(11, 10)
        self.assertGreaterEqual(10, 10)
    def test_lte(self):
        self.assertLessEqual(1, 10, '''comment test''')
        self.assertLessEqual(1, 10)
        self.assertLessEqual(1, 1)

unittest.main()
