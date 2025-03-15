#!/usr/bin/env python3

"""Custom linter rules.
TODO flake8 config
TODO not in just-utils, since it uses flake8 which is an external library?
"""


# mCoding: Python AST Parsing and Custom Linting
# see: https://youtu.be/OjPT15y2EpE


# standard imports
import ast
from typing import Iterator, NamedTuple

# library imports FIXME
import argparse  # only used when OptionManager is also used
from flake8.options.manager import OptionManager


# global constants
PREFIX = "JD"  # prefix to all linter messages, used in flake8 config file

# TODO check index being reused?
def make_message_str(index: int, message: str):
    return f"{PREFIX}{index:03d} {message}"


class Flake8ErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type  # unused but required


def lint_function_imports(node: ast.FunctionDef) -> Iterator[Flake8ErrorInfo]:
    """warn when import inside function scope"""
    MESSAGE = "JD001 function import"
    for child in ast.walk(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            yield Flake8ErrorInfo(child.lineno, child.col_offset, MESSAGE, type(None))


def lint_class_imports(node: ast.ClassDef) -> Iterator[Flake8ErrorInfo]:
    """warn when import inside class scope"""
    MESSAGE = "JD002 class import"
    for child in ast.walk(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            yield Flake8ErrorInfo(child.lineno, child.col_offset, MESSAGE, type(None))


def lint_eval_call(node: ast.Call) -> Iterator[Flake8ErrorInfo]:
    """warn when eval() is used"""
    MESSAGE = "JD003 eval call"
    if isinstance(node.func, ast.Name):
        if node.func.id == "eval":
            yield Flake8ErrorInfo(node.lineno, node.col_offset, MESSAGE, type(None))


def lint_meta_class(node: ast.ClassDef) -> Iterator[Flake8ErrorInfo]:
    """warn when metaclass is defined"""
    MESSAGE = "JD004 metaclass"
    for base in node.bases:
        if isinstance(base, ast.Name):
            if base.id == "type":
                yield Flake8ErrorInfo(base.lineno, base.col_offset, MESSAGE, type(None))


def lint_multiple_assign(node: ast.Assign) -> Iterator[Flake8ErrorInfo]:
    """warn when variable is on both sides of an assignment"""
    MESSAGE = "JD005 multiple assign"
    MESSAGE = make_message_str(5, "multiple assign")
    names = set()
    for target in node.targets:
        for child in ast.walk(target):
            if isinstance(child, ast.Name):
                name = child.id
                if name in names:
                    yield Flake8ErrorInfo(node.lineno, node.col_offset, MESSAGE, type(None))
                else:
                    names.add(name)


class LinterVisitor(ast.NodeVisitor):
    """"""

    def __init__(self):
        self.errors: list[Flake8ErrorInfo] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        self.errors.extend(lint_multiple_assign(node))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self.errors.extend(lint_eval_call(node))
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.errors.extend(lint_class_imports(node))
        self.errors.extend(lint_meta_class(node))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.errors.extend(lint_function_imports(node))
        self.generic_visit(node)


class LinterPlugin:
    name = "flake8_just_linter"
    version = "0.0.1"  # FIXME get library version?

    def __init__(self, tree: ast.AST):
        self.tree = tree

    def run(self) -> Iterator[Flake8ErrorInfo]:
        visitor = LinterVisitor()
        visitor.visit(self.tree)
        yield from visitor.errors

    @staticmethod
    def add_options(option_manager: OptionManager):
        option_manager.add_option(
            "--check-function-imports",
            type=bool,
            metavar="function-imports",
            default=False,
            parse_from_config=True,
            help="Report imports in functions (default =%(default)s)",
        )

    @staticmethod
    def parse_options(options: argparse.Namespace):
        if options.function_imports:
            pass


def main():
    # FIXME load test file
    with open("just/lint_tess.py") as python_file:
        python_text = python_file.read()
    node = ast.parse(python_text)

    plugin = LinterPlugin(node)
    for error in plugin.run():
        print(error)


if __name__ == "__main__":
    main()
