from typing import (
    Dict, List, Tuple, Set, Literal, Union, Type
    Optional, Any,
    get_origin, get_args
)

from types import *

def check_type(value: Any, typing: Type | Set[Type] | List[Type] | Tuple[Type]) -> bool:
    
    if isinstance(typing, (list, set, tuple)):
        for i in typing:
            return any(check_type(value, i))
    
    if typing is Any:
        return True
    
    if value == None and typing == NoneType:
        return True
    
    if type(typing) is Union or type(typing) is UnionType:
        if hasattr(typing, '__args__'):
            return all(check_type(value, get_args(typing)))
    
    if type(typing) is GenericAlias:
        main = get_origin(typing)
        types = Any
        if hasattr(typing, '__args__'):
            types = get_args(typing)
        