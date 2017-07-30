"""
Module that defines Tool functions and test runners/result for use with
the unittest library.
"""
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import posixpath

def get_posix_path(path):
    """translates path to a posix path"""
    heads = []
    tail = path
    while tail != '':
        tail, head = os.path.split(tail)
        heads.append(head)
    return posixpath.join(*heads[::-1])

def run_with_stdlib(file_path, file_name=None):
    """Creates a test that runs a ruby file with the stdlib."""
    file_name = file_name if file_name else file_path

    class TestStdLib(unittest.TestCase):
        """Tests ruby code with the stdlib"""
        templ = {
            "rb_path": file_path, 
            "rb_unix_path": get_posix_path(file_path), 
            "rb_out_path": file_path + ".out",
            "rb_error": file_path + ".err",
            "name": file_name,
        }
        def reportProgres(self):
            """Should be overloaded by the test result class."""
    
        def runTest(self):
            """The actual test goes here."""
            cmd = (
                  'ruby "py-builtins.rb" '
                  ' "%(rb_path)s" > "%(rb_out_path)s" 2> "%(rb_error)s"'
                  )% self.templ
            self.assertEqual(0, os.system(cmd))
            self.reportProgres()

        def __str__(self):
            return "%(rb_unix_path)s [1]: " % self.templ

    return TestStdLib

def compile_file_test(file_path, file_name=None):
    """Creates a test that tests if a file can be compiled by python"""
    file_name = file_name if file_name else file_path
    
    class CompileFile(unittest.TestCase):
        """Test if a file can be compiled by python."""

        templ = {
            "py_path": file_path, 
            "py_unix_path": get_posix_path(file_path), 
            "py_out_path": file_path + ".out",
            "py_error": file_path + ".err",
            "name": file_name,
        }
        def reportProgres(self):
            """Should be overloaded by the test result class"""

        def runTest(self):
            """The actual test goes here."""
            commands = (
                (
                'python "%(py_path)s" > '
                '"%(py_out_path)s" 2> "%(py_error)s"'
                ) % self.templ,
              )
            for cmd in commands:
                self.assertEqual(0, os.system(cmd))
                self.reportProgres()
        def __str__(self):
            return "%(py_unix_path)s [1]: " % self.templ
    return CompileFile




def compile_and_run_file_test(file_path, file_name=None):
    """Creates a test that compiles and runs the python file as ruby"""
    file_name = file_name if file_name else file_path

    class CompileAndRunFile(unittest.TestCase):
        """Tests that a file can be compiled and run as ruby"""
        templ = {
        "py_path": file_path, 
        "py_unix_path": get_posix_path(file_path),
        "py_out_path": file_path + ".out",
        "rb_path": file_path + ".rb",
        "rb_out_path": file_path + ".rb.out",
        "rb_out_expected_path": file_path + ".expected_out",
        "rb_out_expected_in_path": file_path + ".expected_in_out",
        "py_error": file_path + ".err",
        "rb_error": file_path + "rb.err",
        "compiler_error": file_path + ".comp.err",
        "name": file_name,
        }
        def reportProgres(self):
            """Should be overloaded by the test result class"""

        def runTest(self):
            """The actual test goes here."""
            python_command = (
                'python "%(py_path)s" > "%(py_out_path)s" 2> '
                '"%(py_error)s"'
                ) % self.templ
            compile_command = (
                'python py2rb.py --include-builtins '
                '"%(py_path)s" > "%(rb_path)s" 2> '
                '"%(compiler_error)s"'
                ) % self.templ 
            ruby_command = (
                'ruby "%(rb_path)s" > "%(rb_out_path)s" 2> '
                '"%(rb_error)s"' 
                ) % self.templ
            commands = (
                python_command,
                compile_command,
                ruby_command
                )
            for cmd in commands:
                self.assertEqual(0, os.system(cmd))
                self.reportProgres()
            # Partial Match
            if os.path.exists(self.templ["rb_out_expected_in_path"]):
                # Fixed statement partial match
                self.assertIn(
                    open(self.templ["rb_out_expected_in_path"]).read(),
                    open(self.templ["rb_out_path"]).read()
                    )
            else: # Full text match
                # Fixed sentence matching
                if os.path.exists(self.templ["rb_out_expected_path"]):
                    expected_file_path = self.templ["rb_out_expected_path"]
                else: # Dynamic sentence matching
                    expected_file_path = self.templ["py_out_path"]
                self.assertEqual(
                    open(expected_file_path).readlines(),
                    open(self.templ["rb_out_path"]).readlines()
                    )
            self.reportProgres()

        def __str__(self):
            return "%(py_unix_path)s [4]: " % self.templ

    return CompileAndRunFile

def compile_and_run_file_failing_test(*a, **k):
    """Turn a test to a failing test"""
    _class = compile_and_run_file_test(*a, **k)

    class FailingTest(_class):
        """Failing test"""
        @unittest.expectedFailure
        def runTest(self):
            return super(FailingTest, self).runTest()

    return FailingTest

