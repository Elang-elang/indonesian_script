# Exceptions.py
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

from utils import Object

s = Style()
Ovject = Object(True)

def init_except(Obj):
    global Object
    Object = Obj

class ControlSignal(Exception):
    """Base class untuk sinyal kontrol (return/throw)"""
    pass

class ReturnSignal(ControlSignal):
    """Sinyal untuk return value"""
    def __init__(self, value):
        self.value = value
        super().__init__(f"Return: {value}")

class ThrowSignal(ControlSignal):
    """Sinyal untuk throw exception"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ContinueSignal(ControlSignal):
    """Sinyal untuk return value"""
    def __init__(self):
        super().__init__("Continue")

class BreakSignal(ControlSignal):
    """Sinyal untuk throw exception"""
    def __init__(self):
        super().__init__("Break")

# Galat dasar
class Galat(Exception):
    """Base class untuk semua error Indonesian Script"""
    def __init__(self, message, ast):
        self.message = message
        self.meta = Object.get(hex(id(ast)))
        super().__init__(message)
    
    def get_context(self, code):
        if not self.meta:
            return []
        code = code.split("\n")
        start_line = self.meta['line']
        start_pos, end_pos = self.meta['start_pos'], self.meta['end_pos']
        
        codes = []
        codes.append(code[start_line])
        codes.append(" "*start_pos + "^"*end_pos-start_pos)
        return codes

# Galat turunan pertama
class PenulisanGalat(Galat):
    """Error penulisan/syntax"""
    pass

class VariabelGalat(Galat):
    """Error terkait variabel"""
    pass

class PengulanganGalat(Galat):
    """Error terkait loop/iterasi"""
    pass

class MemoriGalat(Galat):
    """Error terkait memori/pointer"""
    pass

class ModulGalat(Galat):
    """Error terkait modul"""
    pass
    
# Galat turunan kedua
class TitikKomaGalat(PenulisanGalat):
    """Error titik koma"""
    pass

class IndeksGalat(PenulisanGalat):
    """Error indeks di luar jangkauan"""
    pass

class AtributGalat(PenulisanGalat):
    """Error atribut tidak ditemukan"""
    pass

class KarakterGalat(PenulisanGalat):
    """Error karakter tidak dikenal"""
    pass

class IterasiGalat(PengulanganGalat):
    """Error saat iterasi"""
    pass

class EkspresiGalat(PenulisanGalat):
    """Error ekspresi tidak valid"""
    pass

class FinalGalat(VariabelGalat):
    """Error mengubah variabel final"""
    pass

class AlamatMemoriGalat(MemoriGalat):
    """Error alamat memori tidak ditemukan"""
    pass

class JalurGalat(PenulisanGalat):
    """Error jalur file tidak ditemukan"""
    pass

class EksporGalat(ModulGalat):
    """Error ekpor modul"""
    pass

class BerkasGalat(ModulGalat):
    """Error terkair File/Berkas"""
    pass

class DirektoriGalat(ModulGalat):
    """Error terkair Direktori/Folder"""
    pass

class PaketGalat(ModulGalat):
    """Error terkair paket/package"""
    pass

class ImporGalat(ModulGalat):
    """Error terkair impor modul"""
    pass

# Galat turunan ketiga
class TipeGalat(EkspresiGalat):
    """Error tipe data tidak sesuai"""
    pass

class KataKunciGalat(KarakterGalat):
    """Error kata kunci tidak dikenal"""
    pass

class IsiGalat(KarakterGalat):
    """Error isi tidak valid"""
    pass

# Untuk kompatibilitas dengan kode lama
def get_exc_text(exception, code, path='__main__'):
    """Buat teks exception (untuk kompatibilitas)"""
    lines = []
    lines.append(f'Pada: {path}')
    
    if hasattr(exception, 'get_context'):
        syntax = exception.get_context(code)
        if syntax:
            lines.append(syntax)
    
    if hasattr(exception, 'line') and hasattr(exception, 'column'):
        line = getattr(exception, 'line', 0)
        column = getattr(exception, 'column', 0)
        if line > 0 and column > 0:
            lines.append(f'Baris: {line}, Kolom: {column}')
    
    return '\n'.join(lines)

class ExceptionContext:
    def __init__(self, code: str = "", func = lambda: None):
        self._exception = None
        self.is_error = False
        self._output = None
        self._code = code
        self._context = ""
        self._line = -1
        self._column = -1
        
        try:
            self.output = func()
        except Exception as e:
            self._exception = e
            self.is_error = True
    
    def get_line_column(self, codes, context) -> tuple[int]:
        line = column = -1
        if isinstance(self._exception, Galat):
            return (
                self._exception.meta['line'],
                self._exception.meta['column']
            )
        
        if context in codes:
            for line, c in enumerate(codes, start=1):
                if c == context:
                    break
            
            column = len(context[1].rstrip())
        return (line, column)
    
    def get_context(self):
        self._context = self.get_exc_context()
        codes = self._code.split('\n')
        code = [ctx.rstrip() for ctx in self._context[0:-1]]
        arrow = self._context[-1].rstrip()
        self._line, self._column = self.get_line_column(codes, code)
        
        syntax = self._get_syntax(codes, arrow, self._line, self._column)
        return syntax
    
    def get_exc_context(self):
        context = []
        if isinstance(self._exception, Galat):
            context.extend(self._exception.get_context())
        else:
            context.extend([ctx for ctx in self._context.split('\n') if ctx])
        
        return context
    
    def _get_syntax(self, codes, arrow, line, column):
        mid = line - 1
        
        start = 0
        end = 0
        if len(codes) < 3:
            start = line - 2
        if len(codes) > 3:
            start = line - 2
            end = line
        
        syntax = []
        syntax.append(f"{" "*10} {s.b}{s.N}|{s.R}")
        if start and end:
            for idx, code in enumerate(codes[start:end], start=start):
                if idx == mid:
                    syntax.extend(self._main_err(idx, code, arrow))
                else:
                    syntax.append(self._sub_err(idx, code))
        else:
            if start:
                for idx, code in enumerate(codes[start:mid], start=start):
                    if idx == mid:
                        syntax.extend(self._main_err(idx, code, arrow))
                    else:
                        syntax.append(self._sub_err(idx, code))
            elif end:
                for idx, code in enumerate(codes[mid:end], start=start):
                    if idx == mid:
                        syntax.extend(self._main_err(idx, code, arrow))
                    else:
                        syntax.append(self._sub_err(idx, code))
            else:
                syntax.extend(self._main_err(idx, codes[mid-1], arrow))
        
        syntax.append(f"{" "*10} {s.b}{s.N}|{s.R}")
        return syntax
    
    def get_output(self, default=None):
        if not self.is_error:
            return self.output
        return default
    
    def _main_err(self, idx, code, arrow):
        return [
            f"{s.m}{s.B}>>>{s.r}{str(idx):>7} {s.b}{s.N}|{s.B}{s.br}{code}{s.R}",
            f"{" "*10} {s.b}|{s.r}{s.B}{arrow}{s.R}
        ]
    
    def _sub_err(self, idx, code):
        return f"{s.y}{s.B}{str(idx):>10} {s.b}{s.N}|{s.R}{code}"
    
    def __repr__(self):
        output = None
        if self.is_error:
            output = self._exception
        else:
            output = self.output
        
        return f"ExceptionContext(is_error={self.is_error}, output={str(type(output))})"