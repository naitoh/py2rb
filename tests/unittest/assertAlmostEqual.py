import unittest

class TestRunnable(unittest.TestCase):

    def test_runnable(self):
        #(first, second, places=7, msg=None, delta=None)
        self.assertAlmostEqual(1.0, 1.00000001, 7)
        self.assertAlmostEqual(1.0, 1.00000001, 7, '''comment test''')
        self.assertAlmostEqual(1.0, 1.00000001, msg='''comment test''', delta=1e-8)

unittest.main()
