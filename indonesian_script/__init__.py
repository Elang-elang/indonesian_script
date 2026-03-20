"""
Indonesian Script - Bahasa pemrograman dalam Bahasa Indonesia
"""

__version__ = "0.1.11a4"
__author__ = "Elang Muhammad"

from .main import IndonesianScriptInterpreter, isi
# from .Interpreter.interpreter import Interpreter
from .Interpreter.transformer import ASTBuilder as Loader
from .Interpreter.AST_node import ast_nodes as AST
from .Interpreter.Builtins import builtins 
from .Interpreter.Exceptions import exceptions
from .bridge import module as ModuleBridge
