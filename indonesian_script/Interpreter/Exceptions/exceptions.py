# Exceptions.py
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
    def __init__(self, message):
        self.message = message
        super().__init__(message)

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

def get_exc(name, message):
    """Buat exception class dinamis"""
    # Buat class exception baru
    exc_class = type(
        name,
        (ThrowSignal,),
        {
            '__init__': lambda self, msg: ThrowSignal.__init__(self, msg),
            '__str__': lambda self: f"{name}: {self.message}"
        }
    )
    return exc_class(message)

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