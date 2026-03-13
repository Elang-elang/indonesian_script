"""
Decorators untuk mendaftarkan fungsi Python ke Indonesian Script
"""

import inspect
import typing as T
from ..Interpreter.AST_node import ast_nodes as AST
from ..Interpreter.interpreter import Interpreter
from ..Interpreter.Exceptions import Exceptions as Exp
from decimal import Decimal

# @var
_isplace = False
_interp = Interpreter('<module>', False)

# @func
def _to_is_type(tipe: T.Type):
    kamusan = {
        str: AST.BasicType('teks'),
        int: AST.BasicType('angka'),
        bool: AST.BasicType('kondisi'),
        float: AST.BasicType('desimal'),
        list: AST.BasicType('daftar'),
        dict: AST.BasicType('kamus'),
        type(lambda: None): AST.BasicType('fungsi'),
        T.Any: AST.BasicType('apapun'),
        
        # alias
        Decimal: AST.BasicType('desimal'),
        
        tuple: AST.BasicType('daftar'),
        set: AST.BasicType('daftar'),
        T.Tuple: AST.BasicType('daftar'),
        T.Set: AST.BasicType('daftar'),
        
        T.Dict: AST.BasicType('kamus'),
        callable: AST.BasicType('fungsi'),
        T.Callable: AST.BasicType('fungsi'),
        object: AST.BasicType('apapun'),
    }
    
    return kamusan.get(tipe, AST.BasicType('kekosongan'))

def _get_from_val(value: T.Any):
    py_type = type(value)
    
    is_type = _to_is_type(py_type)
    
    return is_type

def _convert_val(value: T.Any):
    is_type = _get_from_val(value)
    
    kamusan = {
        'teks': str,
        'angka': int,
        'kondisi': bool,
        'desimal': Decimal,
        'daftar': list,
        'kamus': dict,
        'fungsi': callable,
        'apapun': object,
        'kekosongan': type(None)
    }
    
    py_type = kamusan.get(is_type.name)
    if py_type not in (callable, object):
        if py_type == type(None):
            return 'kekosongan'
        return py_type(value)
    elif py_type == callable:
        if callable(value):
            return value
        else:
            return None
    return value


# @cls
class Kembalikan(Exp.ReturnSignal):
    """
        Sinyal untuk mereturnkan nilai. Contoh:
        
        ```
        @Fungsi
        def app(Arg: int) -> int:
            raise Kembalikan(Arg)
        ```
        
        lebih baik gunakan metode ini ketimbang langsung mereturnkan saja.
        
        Argument:
            value: T.Any
    """
    pass

class Kegalatan(Exp.ThrowSignal):
    """
        Sinyal untuk exception sesuatu. Contoh:
        ```
        @Fungsi
        def app(Arg: int) -> int:
            if not isinstance(Arg, int):
                raise Kegalatan("<penjelasanError>")
            raise Kembalikan(Arg)
        ```
        
        Argument:
            message: T.Any
    """
    pass

class Pendaftaran:
    """
    Helper class untuk pendaftaran di decorator Modul
    Langsung digunakan saat dekorasi
    """
    
    def __init__(self, nama_modul=None):
        self._daftar = []
        self._terkunci = False
        self._bawaan = {}
        self._nama_modul = nama_modul
        
    def atur(self, func, nama=None):
        """Mendaftarkan fungsi ke modul"""
        if self._terkunci:
            raise RuntimeError("Modul sudah dikunci, tidak bisa menambah lagi")
        
        # Jika func adalah string, berarti itu nama fungsi di registry
        if not isinstance(func, Fungsi) and hasattr(func, '_func'):
            raise AttributeError(f"Function def yang dimaksud adalah function yang dideklarasikan dengan decorated Fungsi.")
        
        # Simpan info fungsi
        self._daftar.append({
            'content': AST.Variable(name=func.nama),
            'alias': nama
        })
        
        return self
    
    def ekspor(self, nama_var, alias_var):
        if _interp.current_scope.has(nama_var):
            raise Exp.VariabelGalat(f'Tidak ada variabel ini {nama_var!r}')
        
        self._daftar.append({
            'content': AST.Variable(name=nama_var),
            'alias': alias_var
        })
        
        return self
    
    def ok(self):
        """Mengunci modul, tidak bisa ditambah lagi"""
        self._terkunci = True
        return self
    
    def dapatkan_daftar(self):
        """Mengembalikan daftar fungsi yang sudah didaftarkan"""
        return self._daftar.copy()
    
    def __repr__(self):
        return f"<Pendaftaran Modul {self._nama_modul!r}>"
    
    def __iter__(self):
        return iter(self._daftar.copy())

class Variabel:
    def __init__(self, Name: str, Type: T.Type, Value: T.Any, ):
        self.nama = Name
        self.tipe = _to_is_type(Type)
        self.isi = _convert_val(Value)
        
        _interp.current_scope.declare(
            self.name,
            self.isi,
            self.tipe,
            hex(id(self.isi)),
            constant=False
        )
    
    @classmethod
    def Final(cls, nama, tipe, isi):
        isi = _convert_val(isi)
        tipe = _to_is_type(tipe)
        
        _interp._check_type(isi, tipe)
        
        _interp.current_scope.declare(
            nama,
            isi,
            tipe,
            hex(id(isi)),
            constant=True
        )
    
    @classmethod
    def Redeklarasi(cls, nama, isi):
        obj = _interp.current_scope.get(nama)
        isi = _convert_val(isi)
        
        _interp._check_type(isi, obj['type'])
        
        _interp.current_scope.declare(
            nama,
            isi,
            obj['type'],
            hex(id(isi)),
            obj['constant']
        )
    
    @classmethod
    def DefDeklarasi(cls, nama, tipe):
        tipe = _to_is_type(tipe)
        isi = _default_value(tipe)
        
        _interp.current_scope.declare(
            nama,
            isi,
            tipe,
            hex(id(isi)),
            constant=False
        )
    
    @classmethod
    def Pointer(cls, nama, isi):
        tipe = AST.BasicType('pointer')
        isi = hex(id(isi))
        
        _interp.current_scope.declare(
            nama,
            isi,
            tipe,
            hex(id(isi)),
            constant=False
        )
        
    @classmethod
    def Unpointer(cls, nama, isi):
        obj = _interp.current_scope.get(isi, 'address')
        
        _interp.current_scope.declare(
            nama,
            obj['value'],
            obj['type'],
            hex(id(obj['value'])),
            constant=False
        )
    
    @classmethod
    def Alias(cls, nama, var):
        obj = _interp.current_scope.get(var)
        
        _interp.current_scope.declare(
            nama,
            var['value'],
            var['type'],
            var['address'],
            var['constant']
        )
    
    
    def __repr__(self):
        return f"<Variabel({self.tipe} {self.nama} = {self.isi})"

class Fungsi:
    """
    Decorator untuk mendaftarkan fungsi Python menjadi fungsi Indonesian Script
    
    Contoh:
        @Fungsi
        def log(teks: str) -> None:
            print(f"LOG: {teks}")
    
    Tambahan:
        @Fungsi
        def kali(angka1: int, angka2: int) -> int: # utamakan indikator type
            return int(angka1 * angka2) # pengecekan ulang, agar tidak terjadi kesalahan
    
    Argument:
        func: Callable
    """
    
    _func = None
    nama: str = ""
    tipe: T.Any = type
    __loader__ = None
    _params_info = []  # Simpan info parameter
    
    def __init__(self, func: T.Callable):
        self._func = func
        self.nama = func.__name__
        self.tipe = func.__annotations__.get('return', T.Any)
        
        # Dapatkan signature
        signature = inspect.signature(func)
        self._params_info = []
        for name, param in signature.parameters.items():
            self._params_info.append({
                'name': name,
                'type': param.annotation if param.annotation != inspect.Parameter.empty else T.Any,
                'default': param.default if param.default != inspect.Parameter.empty else None
            })
        
        """Method ini dipanggil saat dekorasi"""
        target_func = self._func
        func_name = self.nama
        
        # Buat AST Argument untuk parameter
        args = []
        call_args = []  # Untuk pemanggilan di dalam wrapper
        
        for i, param in enumerate(self._params_info):
            # Argument untuk deklarasi parameter
            arg = AST.Argument(
                type_ann=_to_is_type(param['type']),
                name=param['name'],
                value=AST.Literal(value=_convert_val(param['default'])) if param['default'] is not None else None
            )
            args.append(arg)
            
            # CallArgument untuk pemanggilan fungsi (pake Variable agar diisi saat runtime)
            call_arg = AST.CallArgument(
                name=param['name'],
                value=AST.Variable(name=param['name'])  # Variable akan diisi dari scope
            )
            call_args.append(call_arg)
        
        # Dapatkan return type
        return_type = self.tipe
        
        # Buat wrapper function yang akan dipanggil
        wrapper_func = self._get_wrapper(target_func)
        
        # Daftarkan wrapper function sebagai variabel GLOBAL dulu
        # (ini penting agar bisa dipanggil dari dalam fungsi nanti)
        _interp.current_scope.declare(
            f"__wrapper_{func_name}",
            wrapper_func,
            _to_is_type(return_type),
            hex(id(wrapper_func)),
            constant=True
        )
        
        # Buat AST Function yang akan di-visit
        func_node = AST.Function(
            type_ann=_to_is_type(return_type),
            name=func_name,
            params=AST.Parameter(args=args),
            inner=[
                AST.Return(
                    expr=AST.CallFunc(
                        func=AST.Variable(name=f"__wrapper_{func_name}"),  # Panggil wrapper
                        params=AST.CallParameter(args=call_args)
                    )
                )
            ]
        )
        
        # Visit function node
        _interp.visit(func_node)
    
    def __repr__(self):
        return f"<Fungsi {self.nama!r} bertipe {self.tipe.__name__!r} di {hex(id(self._func))}>"
    
    @classmethod
    def _get_wrapper(self, func):
        def wrapper(*args, **kwargs):
            try:
                # Panggil fungsi asli dengan semua argumen
                result = func(*args, **kwargs)
                # Jika result sudah berupa sinyal, langsung raise
                if isinstance(result, (Kembalikan, Exp.ReturnSignal, Exp.ThrowSignal)):
                    raise result
                # Jika tidak, bungkus dengan Kembalikan
                raise Kembalikan(result)
            except (Kembalikan, Exp.ThrowSignal) as e:
                # Propagate sinyal yang sudah benar
                raise
            except Exception as e:
                # Bungkus error lain dengan Kegalatan
                raise Kegalatan(f'\n\nFungsi {func.__name__!r} mengalami galat:\n    {str(e)}\n')
        
        return wrapper
    

class Modul:
    """
    Decorator untuk membuat modul Indonesian Script dari kumpulan fungsi Python
    **Langsung dieksekusi saat dekorasi** dengan parameter Pendaftaran
    
    Contoh:
        @Modul
        def matematika(p):
            p.atur(tambah).atur(kurang).atur(kali).atur(bagi)
            p.ok()
            return p
    """
    
    def __init__(self, func: T.Callable):
        self._func = func
        self.nama = func.__name__
        
        target_func = func or self._func
        
        if globals()['_isplace']:
            raise RuntimeError(f"Decoreted Modul pernah digunakan!")
        
        # Dapatkan nama modul
        module_name = self.nama or target_func.__name__
        
        # BUAT INSTANCE PENDAFTARAN
        pendaftaran = Pendaftaran(module_name)
        
        # EKSEKUSI FUNGSI LANGSUNG dengan parameter pendaftaran
        hasil = target_func(pendaftaran)
        
        # Ambil daftar fungsi
        daftar_fungsi = []
        if hasil and hasattr(hasil, 'dapatkan_daftar'):
            daftar_fungsi.extend(hasil.dapatkan_daftar())
        
        daftar_ekspor = []
        for ekspor in daftar_fungsi:
            daftar_ekspor.append(
                AST.ExportArgument(
                    name = ekspor['content'].name,
                    alias = ekspor['alias']
                )
            ) # -> { args1, args2, ... }
        
        
        self._run_ast(
            AST.Export(
                exports=daftar_ekspor
            )
        ) # -> ekspor { ... }
        
        globals()['_isplace'] = True # -> for not replace
    
    def _run_ast(self, node: AST.Node):
        _interp.visit(node)
    
    def _get_interp(self):
        return _interp
    
    def __repr__(self):
        return f"<Modul {self.nama!r}>"
    
    __name__ = 'Modul'