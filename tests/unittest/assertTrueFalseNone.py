import unittest

class TestRunnable(unittest.TestCase):

    def test_true(self):
        self.assertTrue(True, '''comment test''')
        self.assertTrue(True)

    def test_false(self):
        self.assertFalse(False, '''comment test''')
        self.assertFalse(False)

    def test_isnone(self):
        self.assertIsNone(None, '''comment test''')
        self.assertIsNone(None)

unittest.main()
