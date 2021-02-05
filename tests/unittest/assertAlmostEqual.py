import unittest

class TestRunnable(unittest.TestCase):

    def test_almeq(self):
        #(first, second, places=7, msg=None, delta=None)
        self.assertAlmostEqual(1.0, 1.00000001, 7)
        self.assertAlmostEqual(1.0, 1.00000001, 7, '''comment test''')
        self.assertAlmostEqual(1.0, 1.00000001, msg='''comment test''', delta=1e-8)
    def test_notalmeq(self):
        #(first, second, places=7, msg=None, delta=None)
        self.assertNotAlmostEqual(1.5, 1.00000001, 7)
        self.assertNotAlmostEqual(1.5, 1.00000001, 7, '''comment test''')
        self.assertNotAlmostEqual(1.5, 1.00000001, msg='''comment test''', delta=1e-8)

unittest.main()
