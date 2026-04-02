from .interpreter import Interpreter
from .transformer import ASTBuilder

class Compile:
    def __init__(self, filename='<is-stdout>', code='', ismodule=False):
        print(*Interpreter.__dict__.keys(), sep=', ')
        builder = ASTBuilder()
        self._ast = builder.load(code)
        self._interp = Interpreter(filename, ismodule, self._ast)
    
    def __call__(self):
        return self._interp.load()
    
    def get_interp(self): return self._interp
    def get_scope(self): return self._interp.current_scope
    def get_vars(self): return self._interp.current_scope.vars
    def get_ast(self): return self._ast
    