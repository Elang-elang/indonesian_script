# builtins.py
from ..Exceptions.exceptions import VariabelGalat, FinalGalat, TipeGalat
from ..AST_node.ast_nodes import BasicType
from decimal import Decimal
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

def get_builtin_type(name):
    return TYPES.get(name, object)

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

BUILTINS_FUNCTIONS = {
    'Fungsi': builtins_fungsi,
    'Variabel': builtins_vars
}

import inspect

class Fungsi:
    __value__ = None
    __name__ = 'Fungsi'
    __id__ = id('Fungsi')
    __hex__ = hex(id('Fungsi'))
    __dict__ = {}
    
    def __init__(self, func):
        self.__value__ = func
        self.__name__ = func.__name__
        self.__id__ = id(func)
        self.__hex__ = hex(self.__id__)
        self.__dict__ = dict(getattr(func, '__dict__', {}))
    
    def __call__(self, *args, **kwargs):
        return self.__value__(*args, **kwargs)
    
    def __repr__(self):
        return f"<Fungsi {self.__name__!r} pada {self.__hex__}>"