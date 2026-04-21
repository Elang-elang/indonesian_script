# ==================== exceptions.py ====================
from colorama import Fore as F, Style as S, Back as BK, init
init()

class Style:
    R = reset = S.RESET_ALL
    D = dim = S.DIM
    B = bold = BH = bright = S.BRIGHT
    N = normal = S.NORMAL
    br = red_back = BK.RED
    gr = green_back = BK.GREEN
    b = blue = F.BLUE
    g = green = F.GREEN
    r = red = F.RED
    c = cyan = F.CYAN
    y = yellow = F.YELLOW
    m = magenta = F.MAGENTA

from ..Interpreter.utils import Object
from lark.exceptions import LarkError
s = Style()
_object_store = Object(True)  # global store untuk meta

def init_except(Obj):
    global _object_store
    _object_store = Obj

class ControlSignal(Exception):
    pass

class ReturnSignal(ControlSignal):
    def __init__(self, value):
        self.value = value
        super().__init__(f"Return: {value}")

class ThrowSignal(ControlSignal):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ContinueSignal(ControlSignal):
    def __init__(self):
        super().__init__("Continue")

class BreakSignal(ControlSignal):
    def __init__(self):
        super().__init__("Break")

class Galat(Exception):
    def __init__(self, message, ast):
        self.message = message
        self.meta = _object_store.get(hex(id(ast))) if _object_store else None
        print(f"obj = {ast}, {self.meta}")
        super().__init__(message)

    def get_context(self, code):
        if not self.meta:
            return []
        lines = code.split('\n')
        start_line = self.meta.get('line', 0) - 1  # ke 0-index
        if start_line < 0 or start_line >= len(lines):
            return []
        start_pos = self.meta.get('start_pos', 0)
        end_pos = self.meta.get('end_pos', start_pos)
        if end_pos <= start_pos:
            end_pos = start_pos + 1
        return [
            lines[start_line],
            ' ' * start_pos + '^' * (end_pos - start_pos - 1)
        ]

# Semua turunan Galat
class PenulisanGalat(Galat): pass
class VariabelGalat(Galat): pass
class PengulanganGalat(Galat): pass
class MemoriGalat(Galat): pass
class ModulGalat(Galat): pass
class TitikKomaGalat(PenulisanGalat): pass
class IndeksGalat(PenulisanGalat): pass
class AtributGalat(PenulisanGalat): pass
class KarakterGalat(PenulisanGalat): pass
class IterasiGalat(PengulanganGalat): pass
class EkspresiGalat(PenulisanGalat): pass
class FinalGalat(VariabelGalat): pass
class AlamatMemoriGalat(MemoriGalat): pass
class JalurGalat(PenulisanGalat): pass
class EksporGalat(ModulGalat): pass
class BerkasGalat(ModulGalat): pass
class DirektoriGalat(ModulGalat): pass
class PaketGalat(ModulGalat): pass
class ImporGalat(ModulGalat): pass
class TipeGalat(EkspresiGalat): pass
class KataKunciGalat(KarakterGalat): pass
class IsiGalat(KarakterGalat): pass

def get_exc_text(exception, code, path='__main__'):
    lines = [f'Pada: {path}']
    if hasattr(exception, 'get_context'):
        ctx = exception.get_context(code)
        if ctx:
            lines.extend(ctx)
    if hasattr(exception, 'line') and hasattr(exception, 'column'):
        if exception.line > 0:
            lines.append(f'Baris: {exception.line}, Kolom: {exception.column}')
    return '\n'.join(lines)

class ExceptionContext:
    def __init__(self, code="", func=lambda: None):
        self._code = code
        self.is_error = False
        self._exception = None
        try:
            self.output = func()
        except Exception as e:
            self._exception = e
            self.is_error = True

    def get_context(self):
        ctx = []
        if isinstance(self._exception, Galat):
            ctx.append(self._exception.get_context(self._code))
        elif isinstance(self._exception, LarkError):
            ctx.append(self._exception.get_context(self._code))
        
        if getattr(self._exception, 'meta', None) and isinstance(self._exception, Galat):
            ctx.extend(self.get_dest())
        elif isinstance(self._exception, LarkError):
            ctx.extend(self.get_dest())
            
        if ctx:
            return "\n".join(ctx)
        
        return self._exception

    def get_output(self, default=None):
        return default if self.is_error else self.output
    
    def get_dest(self):
        dest = []
        line = column = -1
        ctx = []
        if isinstance(self._exception, Galat):
            line = self._exception.meta['line']
            column = self._exception.meta['column']
            ctx.append(" "*4 + str(self._exception))
        elif isinstance(self._exception, LarkError):
            if line := getattr(self._exception, 'line', 0):
                pass
            if column := getattr(self._exception, 'column', 0):
                pass
            if txts := getattr(self._exception, 'allowed', False):
                ctx.extend([f"{" "*4}{txt}" for txt in txts if txt])
            if char := getattr(self._exception, 'char', None):
                ctx.extend(["", f"Dan Dikarenakan Karakter: {str(char)!r}"])
        
        if line > 1 and column > 1:
            dest.append(f"Kegalatan pada baris: {line}, kolom: {column} dan karena:")
        dest.extend(ctx)
        dest.append(f"Tampilan Exception: {repr(self._exception)}")
        return dest
    
    def __repr__(self):
        return f"ExceptionContext(is_error={self.is_error}, output={type(self.output).__name__ if not self.is_error else 'None'})"