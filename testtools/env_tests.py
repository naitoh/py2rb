"""\
Includes tests that check the setup for the tests.
If the library is compiled and if there is a ruby interpreter.
"""
import os
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import tempfile
class EnviromentTest(unittest.TestCase):
    "Test case that makes sure that the environment is up and working"
    def reportProgres(self):
        """Should be overloaded by the test result class"""

    def stop(self):
        """Should be overloaded by the test result class"""

    def runTest(self):
        """The actual test goes here."""
        if os.system(
            "ruby --help > %s" %
            os.path.join(
                tempfile.gettempdir(),
                tempfile.gettempprefix()
                )
            ):
            self.stop()
            raise RuntimeError("""Can't find the "ruby" command.""")
        self.reportProgres()
        if not os.path.exists("py-builtins.rb"):
            self.stop()
            raise RuntimeError("""Can't find the "py-builtins.rb" command.""")
        if not os.path.exists("py-builtins-using.rb"):
            self.stop()
            raise RuntimeError("""Can't find the "py-builtins-using.rb" command.""")
        if not os.path.exists("py-builtins-require.rb"):
            self.stop()
            raise RuntimeError("""Can't find the "py-builtins-require.rb" command.""")
        self.reportProgres()

    def __str__(self):
        return 'Looking for "ruby", "py-builtins", "py-builtins-using.rb", "py-builtins-require.rb" [4]: '


