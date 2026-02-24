# builtins.py
# Tipe dasar Python yang sesuai dengan nama di grammar
from ..Exceptions.Exceptions import VariabelGalat, FinalGalat
from ..AST_node.ast_nodes import *

TYPES = {
    'teks': str,
    'angka': int,
    'desimal': float,
    'boolean': bool,
    'kekosongan': type(None),
    'apapun': object,  # special
    'daftar': list,
    'kamus': dict,
    'fungsi': callable,
    'pointer': str,
}


# Konstanta built-in
BUILTINS = {
    'benar': True,
    'salah': False,
    'kosong': None,
    'enter': '\n',
    'tab': '\t',
    'format': lambda val, **kwargs: str(val).format(**kwargs),
    'tampilkan': print,
    **TYPES
}

def get_builtin_type(name):
    return TYPES.get(name, object)

def builtins_fungsi(self, function_name: str, /, *, type_ann: type = object, body: callable = lambda: None):
    try:
        self.current_scope.get(function_name)
        return callable(function_name)
    except VariabelGalat:
        def app(*args, **kwargs):
            result = body(*args, **kwargs)
            self._check_type(result, type_ann)
            
            return result
            
        self.current_scope.declare(
            function_name,
            app,
            BasicType(type_ann),
            hex(id(app)),
            True,
        )

def builtins_vars(self, name=None, /, *, value=None, type_ann=None, constant=False, cek=True):
    if not name:
        return self.current_scope.vars
    else:
        if not value:
            if cek:
                inputan = input('Apakah kamu yakin untuk menampilkannya Y[a] atau T[idak]: ')
                
                inputan_bool = True if inputan == 'Y' else False
                
                if inputan_bool:
                    return self.current_scope.has(name)
            return self.current_scope.has(name)
        else:
            if self.current_scope.has(name):
                obj = self.current_scope.get(name)
                
                if constant or obj['constant']:
                    raise FinalGalat(f'Variabel {name!r} memiliki ketidak konsistenan terhadap data dan nilai konstannya')
                
                self.current_scope.set(
                    name,
                    value,
                    obj['type'],
                    hex(id(value)),
                    obj['constant']
                )
            
            if not type_ann:
                raise TipeGalat(f'Variabel {name!r} tidak memiliki tipe yang ada')
            
            self._check_type(value, type_ann)
            
            self.current_scope.declare(
                name,
                value,
                BasicType(type_ann),
                hex(id(value)),
                constant
            )

BUILTINS_FUNCTIONS = {
    'Fungsi': builtins_fungsi,
    'Variabel': builtins_vars
}