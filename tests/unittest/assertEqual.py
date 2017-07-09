import unittest

class TestRunnable(unittest.TestCase):

    def test_runnable(self):
        self.assertEqual('test', 'test', '''comment test''')

unittest.main()
