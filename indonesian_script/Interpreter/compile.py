from .interpreter import Interpreter
from .transformer import ASTBuilder

class Compile:
    def __init__(self, filename='<is-stdout>', code='', ismodule=False):
        builder = ASTBuilder()
        self._code = str(code)
        self._filename = str(filename)
        self._ast = builder.load(code)
        self._interp = Interpreter(filename, ismodule, builder.object)
    
    def __call__(self):
        return self._interp.load(self._ast)
    
    def get_interp(self): return self._interp
    def get_scope(self): return self._interp.current_scope
    def get_vars(self): return self._interp.current_scope.vars
    def get_ast(self): return self._ast
    
    def __repr__(self): return f"Compile(filename={self._filename}, code=\"{str(self._code)}\")"