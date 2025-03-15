#!/usr/bin/env python3

"""Unit-tests for just.timing"""


# standard imports
import unittest
import ast

# tested imports
# store a flag
try:
    import just.lint
    LINT_ENABLED = True
except ModuleNotFoundError:
    LINT_ENABLED = False


@unittest.skipIf(not LINT_ENABLED, "")
class TestLinterPlugin(unittest.TestCase):
    """Tests for class just.lint.LinterPlugin"""

    def test_function_imports(self):
        CODE = """
def function_with_import():
    import ast
    pass
        """.strip()
        linter = just.lint.LinterPlugin(ast.parse(CODE))
        errors = list(linter.run())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 2)
        self.assertEqual(errors[0].offset, 4)
        self.assertEqual(errors[0].msg, "JD001 function import")

    def test_class_imports(self):
        CODE = """
class ClassWithImport:
    import ast
    pass
        """.strip()
        linter = just.lint.LinterPlugin(ast.parse(CODE))
        errors = list(linter.run())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 2)
        self.assertEqual(errors[0].offset, 4)
        self.assertEqual(errors[0].msg, "JD002 class import")

    def test_eval_call(self):
        CODE = "eval('print(\"this should be a lint error!\")')".strip()
        linter = just.lint.LinterPlugin(ast.parse(CODE))
        errors = list(linter.run())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 1)
        self.assertEqual(errors[0].offset, 0)
        self.assertEqual(errors[0].msg, "JD003 eval call")

    def test_meta_class(self):
        CODE = """
class MyMeta(type):  # forbidden!
    pass
        """.strip()
        linter = just.lint.LinterPlugin(ast.parse(CODE))
        errors = list(linter.run())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 1)
        self.assertEqual(errors[0].offset, 13)
        self.assertEqual(errors[0].msg, "JD004 metaclass")

    def test_multiple_assign(self):
        CODE = "a, b = a[:] = [1, 2]"
        linter = just.lint.LinterPlugin(ast.parse(CODE))
        errors = list(linter.run())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 1)
        self.assertEqual(errors[0].offset, 0)
        self.assertEqual(errors[0].msg, "JD005 multiple assign")
