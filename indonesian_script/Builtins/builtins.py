# builtins.py
from ..Exceptions import VariabelGalat, FinalGalat, TipeGalat
from ..Interpreter.AST_node.ast_nodes import BasicType
from decimal import Decimal
import inspect

def builtins_fungsi(self, function_name=None, /, *, type_ann=None, body=None):
    """
    builtins_fungsi: untuk manipulasi fungsi
    - Jika hanya function_name: return apakah itu fungsi
    - Jika dengan type_ann dan body: buat fungsi baru
    """
    if function_name is None:
        # Return semua fungsi yang ada
        return {name: info for name, info in self.current_scope.vars.items() 
                if info['type'].name == 'fungsi'}
    
    try:
        obj = self.current_scope.get(function_name)
        is_func = callable(obj['value'])
        
        if type_ann is not None and body is not None:
            # Buat fungsi baru
            def new_func(*args, **kwargs):
                result = body(*args, **kwargs)
                if type_ann != 'apapun':
                    expected = TYPES.get(type_ann, object)
                    if not isinstance(result, expected):
                        raise TipeGalat(f"Fungsi harus mengembalikan tipe {type_ann}")
                return result
            
            self.current_scope.declare(
                function_name,
                new_func,
                BasicType('fungsi'),
                hex(id(new_func)),
                True
            )
            return True
        
        return is_func
        
    except VariabelGalat:
        return False

def builtins_vars(self, name=None, /, *, value=None, type_ann=None, constant=False):
    """
    builtins_vars: untuk manipulasi variabel
    - Tanpa argumen: return semua variabel
    - Dengan name saja: return apakah variabel ada
    - Dengan name dan value: buat/ubah variabel
    """
    if name is None:
        # Return semua variabel
        return {n: {
            'value': info['value'],
            'type': info['type'].name if isinstance(info['type'], BasicType) else str(info['type']),
            'constant': info['constant']
        } for n, info in self.current_scope.vars.items()}
    
    if value is None:
        # Cek apakah variabel ada
        ada = self.current_scope.has(name)
        return ada
    
    # Buat atau ubah variabel
    try:
        # Cek apakah sudah ada
        obj = self.current_scope.get(name)
        
        # Validasi konstanta
        if obj['constant'] and not constant:
            raise FinalGalat(f"Variabel '{name}' adalah final")
        
        # Validasi tipe
        if type_ann:
            expected = TYPES.get(type_ann, object)
            if not isinstance(value, expected):
                raise TipeGalat(f"Nilai tidak sesuai tipe {type_ann}")
        else:
            type_ann = obj['type'].name if isinstance(obj['type'], BasicType) else 'apapun'
        
        # Update
        self.current_scope.set(
            name,
            value,
            BasicType(type_ann),
            hex(id(value)),
            constant or obj['constant']
        )
        
    except VariabelGalat:
        # Buat baru
        if type_ann is None:
            type_ann = 'apapun'
        else:
            expected = TYPES.get(type_ann, object)
            if not isinstance(value, expected):
                raise TipeGalat(f"Nilai tidak sesuai tipe {type_ann}")
        
        self.current_scope.declare(
            name,
            value,
            BasicType(type_ann),
            hex(id(value)),
            constant
        )
    
    return True

class Fungsi:
    __value__ = None
    __annotations__ = None
    __name__ = 'Fungsi'
    __id__ = id('Fungsi')
    __hex__ = hex(id('Fungsi'))
    __dict__ = {}
    __origin__ = None
    
    def __init__(self, func):
        self.__value__ = func
        self.__name__ = func.__name__
        self.__id__ = id(func)
        self.__hex__ = hex(self.__id__)
        self.__dict__ = dict(getattr(func, '__dict__', {}))
        self.__origin__ = type(func)
        
        try:
            self.__annotations__ = inspect.signature(self.__value__)
        except:
            pass
        
    
    def __call__(self, *args, **kwargs):
        return self.__value__(*args, **kwargs)
    
    def __instancecheck__(self, instance, /):
        if isinstance(self.__value__, type):
            return isinstance(instance, self.__value__)
        return isinstance(instance, Fungsi)
    
    def __eq__(self, value, /):
        if isinstance(value, Fungsi):
            return self.__value__ == value.__value__
        else:
            if isinstance(value, type):
                return self.__value__ == value
            return NotImplemented
    
    def __ne__(self, value, /):
        return not self.__eq__(value)
    
    def __gt__(self, value, /): return NotImplemented
    def __lt__(self, value, /): return NotImplemented
    def __ge__(self, value, /): return NotImplemented
    def __le__(self, value, /): return NotImplemented
    
    def __repr__(self):
        return f"<Fungsi {self.__name__!r} pada {self.__hex__}>"

class Lambda(Fungsi):
    __value__ = None
    __annotations__ = None
    __name__ = 'Fungsi'
    __id__ = id('Fungsi')
    __hex__ = hex(id('Fungsi'))
    __dict__ = {}
    __origin__ = None
    
    def __init__(self, func):
        self.__value__ = func
        self.__name__ = func.__name__
        self.__id__ = id(func)
        self.__hex__ = hex(self.__id__)
        self.__dict__ = dict(getattr(func, '__dict__', {}))
        self.__origin__ = type(func)
        
        try:
            self.__annotations__ = inspect.signature(self.__value__)
        except:
            pass
    
    def __call__(self, *args, **kwargs):
        return self.__value__(*args, **kwargs)
    
    def __repr__(self):
        return f"<Fungsi <Lambda> 'anonimus' pada {self.__hex__}>"

class Karakter:
    __value__ = '\x00'
    __id__ = 0
    __hex__ = hex(ord('\x00'))
    
    isi = '\x00'
    id = 0
    hex = hex(ord('\x00'))
    
    def __init__(self, Chr):
        if isinstance(Chr, (int, float, bool)):
            Chr = chr(int(Chr))
        elif isinstance(Chr, str):
            if len(Chr) != 1:
                raise TipeGalat(f"Tipe karakter harus benar-benar berisi 1 karakter, jangan lebih")
        
        self.isi = Chr
        self.id = ord(Chr)
        self.hex = hex(self.id)
        
        self.__value__ = self.isi
        self.__id__ = self.id
        self.__hex__ = self.hex
    
    def __add__(self, val, /):
        if isinstance(val, Karakter):
            val = val.__id__
        elif isinstance(val, (str, int, float, bool)):
            if isinstance(val, str):
                if len(val) == 1:
                    val = ord(val)
                else:
                    raise TypeError()
            val = int(val)
        
        self.__id__ += val
        if self.__id__ < 0:
            self.__id__ = 0
        self.__value__ = chr(self.__id__)
        self.__hex__ = hex(self.__id__)
        return self
    
    def __sub__(self, val, /):
        self.__add__(-val)
    
    def __eq__(self, val, /):
        if isinstance(val, Karakter):
            return self.__value__ == val.__value__
        if isinstance(val, (int, float)):
            return self.__id__ == int(val)
        else:
            return NotImplemented
    
    def __ne__(self, val, /):
        return not self.__eq__(val)
    
    def __floordiv__(self, val, /):
        if isinstance(val, Karakter):
            return self.__id__ // val.__id__
        if isinstance(val, (int, float)):
            return self.__id__ // val
        else:
            return NotImplemented
    
    def __ge__(self, val, /):
        if isinstance(val, Karakter):
            return seld.__id__ >= val.__id__
        if isinstance(val, (int, float)):
            return self.__id__ >= val
        else:
            return NotImplemented
            
    def __gt__(self, val, /):
        if isinstance(val, Karakter):
            return seld.__id__ > val.__id__
        if isinstance(val, (int, float)):
            return self.__id__ > val
        else:
            return NotImplemented
    
    def __hash__(self):
        return self.__hex__
    
    def __int__(self):
        return self.__id__
    
    def __invert__(self):
        return NotImplemented
    
    def __le__(self, val: int, /):
        if isinstance(val, Karakter):
            return seld.__id__ <= val.__id__
        if isinstance(val, (int, float)):
            return self.__id__ <= val
        else:
            return NotImplemented
    
    def __lt__(self, val: int, /):
        if isinstance(val, Karakter):
            return seld.__id__ < val.__id__
        if isinstance(val, (int, float)):
            return self.__id__ < val
        else:
            return NotImplemented
    
    def __mod__(self, val, /):
        return NotImplemented
    
    def __mul__(self, val, /):
        return NotImplemented
    
    def __neg__(self, val, /):
        return NotImplemented
    
    def __setattribute__(self, name, value, /):
        return NotImplemented
    
    def __repr__(self):
        return self.__value__
    
    def __str__(self):
        return self.__value__
    
    def __format__(self, f, /):
        if f in ('%s', '%c'):
            return f'{str(self.__value__)}'
        elif f in ('%d', '%i'):
            return f'{str(self.__id__)}'
        elif f == '%h':
            return f'{str(self.__hex__)}'
        else:
            return NotImplemented
    
    def __instancecheck__(self, instance, /):
        if isinstance(instance, str):
            if len(instance) != 1:
                return False
            return True
        elif isinstance(instance, (int, bool, float)):
            instance = int(instance)
            if instance < 0:
                return False
            return True
        return type(instance) is Karakter


KEYWORD = {
    # CLI
    'tuliskan', 'bacakanlah',
    
    # VAR
    'alias', 'var', 'def', 'final', 'fungsi',
    
    # FLOW CTRL
    'jika', 'maka', 'kalau', 'tidak',
    'selama', 'untuk', 'lakukan', 'didalam',
    'coba', 'tangkap', 'akhiri', 'pilah',
    
    # MODULE
    'impor', 'ekspor', 'dari', 'sebagai',
    
    # EXPRS
    'atau', 'dan', 'termasuk', 'terkecuali',
    'lambda', 'kembalikan', 'kegalatan', 'lanjutkan',
    'berhentikan', 'adalah', 'bukanlah',
    
    # Tipe
    'tipe', 'teks', 'angka', 'desimal', 'boolean',
    'kekosongan', 'apapun', 'kamus', 'daftar',
    
}

SOFT_KEYWORD = {
    'var', 'fungsi', 'tipe', 'teks', 'angka', 'desimal', 'boolean',
    'kekosongan', 'apapun', 'kamus', 'daftar'
}

TYPES = {
    'teks': str,
    'angka': int,
    'desimal': Decimal,
    'boolean': bool,
    'kekosongan': type(None),
    'apapun': object,
    'daftar': list,
    'kamus': dict,
    'fungsi': callable,
    'pointer': str,
    'tipe': type,
    'karakter': Karakter
}

def format(string: str, /, **kwargs) -> str:
    return string.format(**kwargs)

BUILTINS = {
    'benar': True,
    'salah': False,
    'kosong': None,
    'enter': '\n',
    'tab': '\t',
    'format': format,
    'f': format,
    'tampilkan': print,
    **TYPES
}

BUILTINS_FUNCTIONS = {
    'Fungsi': builtins_fungsi,
    'Variabel': builtins_vars
}

def get_builtin_type(name):
    return TYPES.get(name, object)
