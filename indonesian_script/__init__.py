"""
Indonesian Script - Bahasa pemrograman dalam Bahasa Indonesia
"""

__version__ = "0.1.14"
__status__ = '3 :: Alpha'
__author__ = "Elang Muhammad"

from .main import IndonesianScriptInterpreter, isi
# from .Interpreter.interpreter import Interpreter
from .Interpreter.transformer import ASTBuilder as ISLoader
from .Interpreter.AST_node import ast_nodes as ISNodes
from .Interpreter.Builtins import builtins as ISBuiltins
from .Interpreter.Exceptions import exceptions as ISExceptions
from .bridge import module as ISModuleBridge
from .cli import ISRepl
