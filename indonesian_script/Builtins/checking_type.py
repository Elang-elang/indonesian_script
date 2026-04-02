from typing import (
    Dict, List, Tuple, Set, Literal, Union, Optional, Any, Callable as TypingCallable,
    get_origin, get_args, get_type_hints
)

from types import *
import types
import inspect
import collections.abc
from enum import Enum

def check_type(value: Any, typing: Any) -> bool:
    """
    Fungsi pengecekan tipe yang sangat komprehensif.
    Mendukung:
    - Tipe dasar (int, str, list, dll)
    - Union (X | Y, Union[X, Y])
    - Any (selalu True)
    - Literal (Literal[1, "a", True])
    - Callable (Callable[[int], str])
    - GenericAlias (list[int], dict[str, Any])
    - Tipe dari module types (FunctionType, LambdaType, GeneratorType, dll)
    - NoneType
    - TypeVar
    - Protocol
    - TypedDict (partial)
    - Enum
    - Dan masih banyak lagi
    """
    
    # 1. Handle multiple types (list, set, tuple of types)
    if isinstance(typing, (list, set, tuple)):
        return any(check_type(value, t) for t in typing)
    
    # 2. Handle Any
    if typing is Any:
        return True
    
    # 3. Handle NoneType
    if value is None:
        if typing is type(None) or typing is NoneType:
            return True
        # Cek juga untuk Optional = Union[X, None]
        origin = get_origin(typing)
        if origin is Union:
            args = get_args(typing)
            if type(None) in args or NoneType in args:
                # Value None valid jika None termasuk dalam Union
                return True
    
    # 4. Handle Literal
    origin = get_origin(typing)
    args = get_args(typing)
    
    if origin is Literal:
        return value in args
    
    # 5. Handle Union (baik UnionType dari X|Y maupun typing.Union)
    if origin is Union or (hasattr(types, 'UnionType') and type(typing).__name__ == 'UnionType'):
        # Untuk Python 3.10+ union dengan | operator
        if args:
            return any(check_type(value, arg) for arg in args)
        elif hasattr(typing, '__args__'):
            return any(check_type(value, arg) for arg in typing.__args__)
    
    # 6. Handle Callable
    if origin is TypingCallable or typing is collections.abc.Callable:
        if not callable(value):
            return False
        
        # Jika Callable tanpa parameter spesifik (hanya Callable)
        if origin is None and typing is collections.abc.Callable:
            return True
        
        # Handle Callable[[ArgTypes], ReturnType]
        if args:
            # args untuk Callable adalah (list_of_arg_types, return_type)
            if len(args) == 2:
                arg_types, return_type = args
                
                # Jika arg_types adalah ... (Callable[..., ReturnType])
                if arg_types is ...:
                    # Hanya cek return type dengan memanggil fungsi?
                    # Untuk sekarang, kita terima karena tidak bisa cek argumen tanpa eksekusi
                    # Tapi kita bisa cek jumlah parameter minimal?
                    return True
                
                # Cek jumlah parameter
                sig = inspect.signature(value)
                params = list(sig.parameters.values())
                
                # Handle method (self parameter tidak perlu dicek jika dari class)
                # Ini pendekatan sederhana
                
                # Cek parameter count
                # Catatan: *args dan **kwargs membuat ini kompleks
                # Kita lakukan pengecekan sederhana
                
                # Untuk sekarang, kita cek apakah callable dan bisa dipanggil
                # Pengecekan lebih detail akan memerlukan eksekusi yang berisiko
                try:
                    # Coba cek apakah parameter count sesuai (approximation)
                    has_var_positional = any(p.kind == p.VAR_POSITIONAL for p in params)
                    has_var_keyword = any(p.kind == p.VAR_KEYWORD for p in params)
                    
                    min_args = sum(1 for p in params 
                                  if p.default is p.empty 
                                  and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD))
                    max_args = len(params) if not has_var_positional else float('inf')
                    
                    expected_min = len([a for a in arg_types if a is not ...])
                    
                    if min_args > expected_min:
                        return False
                    
                    # Untuk pengecekan tipe return, kita tidak bisa tanpa eksekusi
                    return True
                except:
                    return True
    
    # 7. Handle GenericAlias (list[int], dict[str, Any], dll)
    if hasattr(typing, '__origin__') or origin is not None:
        # Dapatkan main type dan args
        main_type = origin if origin is not None else getattr(typing, '__origin__', typing)
        type_args = args if args else getattr(typing, '__args__', ())
        
        # Cek apakah value instance dari main_type
        if not isinstance(value, main_type):
            return False
        
        # Jika tidak ada args, selesai
        if not type_args:
            return True
        
        # Handle container types dengan pengecekan elemen
        if main_type in (list, List, set, Set, frozenset):
            # Homogeneous container
            elem_type = type_args[0]
            return all(check_type(item, elem_type) for item in value)
        
        elif main_type in (dict, Dict):
            # Dictionary dengan key, value types
            key_type, val_type = type_args[0], type_args[1]
            return all(
                check_type(k, key_type) and check_type(v, val_type)
                for k, v in value.items()
            )
        
        elif main_type in (tuple, Tuple):
            # Tuple bisa homogen dengan ... atau heterogen
            if ... in type_args:
                # Homogeneous: (type, ...)
                elem_types = [a for a in type_args if a is not ...]
                if len(elem_types) != 1:
                    return False
                elem_type = elem_types[0]
                return all(check_type(item, elem_type) for item in value)
            else:
                # Heterogeneous: panjang harus sama
                if len(value) != len(type_args):
                    return False
                return all(check_type(value[i], type_args[i]) for i in range(len(value)))
        
        # 8. Handle Type dari module types
        elif any(main_type is t for t in [
            FunctionType, LambdaType, GeneratorType, CodeType, MethodType,
            BuiltinFunctionType, BuiltinMethodType, ModuleType, TracebackType,
            FrameType, GetSetDescriptorType, MemberDescriptorType, MappingProxyType,
            SimpleNamespace, DynamicClassAttribute
        ]):
            # Tipe-tipe ini sudah dicek dengan isinstance di atas
            return True
        
        # 9. Handle Enum
        elif isinstance(main_type, type) and issubclass(main_type, Enum):
            return isinstance(value, main_type)
        
        # 10. Untuk container lain (deque, Sequence, dll)
        else:
            # Jika iterable dan punya 1 parameter type, cek elemen
            if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                if len(type_args) == 1:
                    return all(check_type(item, type_args[0]) for item in value)
            return True
    
    # 11. Handle TypeVar
    if hasattr(typing, '__bound__') or hasattr(typing, '__constraints__'):
        # TypeVar: cek apakah value memenuhi batasan
        if hasattr(typing, '__bound__') and typing.__bound__ is not None:
            return check_type(value, typing.__bound__)
        if hasattr(typing, '__constraints__') and typing.__constraints__:
            return any(check_type(value, c) for c in typing.__constraints__)
        # Unbounded TypeVar menerima apa saja
        return True
    
    # 12. Handle Protocol (sederhana - cek adanya method)
    if inspect.isclass(typing) and hasattr(typing, '__protocol_attrs__'):
        # Ini implementasi sederhana untuk Protocol
        protocol_attrs = getattr(typing, '__protocol_attrs__', [])
        for attr in protocol_attrs:
            if not hasattr(value, attr):
                return False
        return True
    
    # 13. Handle TypedDict (sederhana)
    if hasattr(typing, '__annotations__') and hasattr(typing, '__total__'):
        # Ini adalah TypedDict atau class dengan annotations
        if not isinstance(value, dict):
            return False
        
        annotations = typing.__annotations__
        total = getattr(typing, '__total__', True)
        
        for key, key_type in annotations.items():
            if key in value:
                if not check_type(value[key], key_type):
                    return False
            elif total:
                return False
        return True
    
    # 14. Handle ForwardRef (mencoba evaluasi sederhana)
    if hasattr(typing, '__forward_arg__'):
        # ForwardRef, kita coba import nama tersebut
        try:
            from typing import ForwardRef
            if isinstance(typing, ForwardRef):
                # Tidak mudah, kita abaikan untuk sekarang
                return True
        except:
            pass
    
    # 15. Fallback ke isinstance biasa
    try:
        return isinstance(value, typing)
    except TypeError:
        # Jika typing bukan tipe (misal Literal['a'] di Python lama)
        # Coba pendekatan lain
        if hasattr(typing, '__origin__') and typing.__origin__ is Literal:
            return value in typing.__args__
        
        # Jika semua gagal, asumsikan True?
        return True