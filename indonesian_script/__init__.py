"""
Indonesian Script - Bahasa pemrograman dalam Bahasa Indonesia
"""

__version__ = "0.1.14a2"
__status__ = '3 :: Alpha'
__author__ = "Elang Muhammad"

# from .Interpreter.interpreter import Interpreter
from .Interpreter.transformer import ASTBuilder as ISLoader
from .Interpreter.AST_node import ast_nodes as ISNodes
from .Interpreter.compile import Compile as ISCompile
from .Builtins import builtins as ISBuiltins
from .Exceptions import exceptions as ISExceptions
from .bridge import module as ISModuleBridge
from .Cli._repl import ISRepl
