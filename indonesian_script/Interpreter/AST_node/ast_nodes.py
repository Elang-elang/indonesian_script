# ast_nodes.py
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List, Optional, Union

class Node:
    """Base class for all AST nodes."""
    pass

# --- Program & Blocks ---
@dataclass
class Program(Node):
    statements: Optional[List['Statement']]

@dataclass
class Block(Node):
    statements: Optional[List['Statement']]

# --- Statements ---
class Statement(Node):
    pass

@dataclass
class Declare(Statement):
    pass

@dataclass
class VarDecl(Declare):
    type_ann: 'Type'
    name: str
    value: Optional['Expression']

@dataclass
class FinalDecl(Declare):
    type_ann: 'Type'
    name: str
    value: 'Expression'

@dataclass
class DefDecl(Declare):
    type_ann: 'Type'
    name: str

@dataclass
class AliasDecl(Statement):
    alias: str
    target: str

@dataclass
class Redecl(Declare):
    name: str
    value: 'Expression'

@dataclass
class SetObj(Declare):
    obj: 'GetObj'
    value: 'Expression'

@dataclass
class WriteStmt(Statement):
    target: str

@dataclass
class ReadStmt(Statement):
    expr: 'Expression'

@dataclass
class CtrlFlow(Statement):
    pass

@dataclass
class IfCtrl(CtrlFlow):
    if_stmt: 'IfStmt'
    elif_stmt: Optional[List['ElifStmt']]
    else_stmt: Optional['ElseStmt']

@dataclass
class IfStmt(CtrlFlow):
    condition: 'Expression'
    body: Block
    
@dataclass
class ElifStmt(CtrlFlow):
    condition: 'Expression'
    body: Block

@dataclass
class ElseStmt(CtrlFlow):
    body: Block

@dataclass
class WhileStmt(CtrlFlow):
    condition: 'Expression'
    body: Block

@dataclass
class ForStmt(CtrlFlow):
    expr: 'ForExpr'
    body: Block

@dataclass
class ForExpr(CtrlFlow):
    name: str
    target: List[Any]

@dataclass
class TryCtrl(CtrlFlow):
    try_stmt: 'TryStmt'
    catch_stmt: 'CatchStmt'
    finnaly_stmt: Optional['FinnalyStmt']

@dataclass
class TryStmt(CtrlFlow):
    body: Block

@dataclass
class CatchStmt(CtrlFlow):
    name: str
    body: Block

@dataclass
class FinallyStmt(CtrlFlow):
    body: Block

@dataclass
class SwitchStmt(CtrlFlow):
    expr: 'Expression'
    body: List['CaseStmt']

@dataclass
class CaseStmt(CtrlFlow):
    expr: List['Expression']
    body: List[Statement]

# --- Expressions ---
class Expression(Node):
    pass

@dataclass
class BinaryOp(Expression):
    op: str  # '+', '-', '*', '/', '%', '==', '!=', '>=', '>', '<=', '<', 'dan', 'atau', 'dalam', 'tidak dalam'
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str  # 'tidak'
    expr: Expression

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class Unpacking(Expression):
    value: Union[Dict | List]

@dataclass
class Dictionary(Expression):
    keys: List[Any]
    values: List[Any]

@dataclass
class Array(Expression):
    values: List[Any]

@dataclass
class Variable(Expression):
    name: str
    value: Any = None

@dataclass
class Crement(Expression):
    obj: Variable
    negated: bool = False

@dataclass
class GetObj(Expression):
    obj: Expression
    target: str

@dataclass
class CallFunc(Expression):
    func: Expression
    params: 'CallParameter'

@dataclass
class CallParameter(Expression):
    args: List['CallArgument']

@dataclass
class CallArgument(Expression):
    name: Optional[str]
    value: Expression

@dataclass
class LambdaFunc(Expression):
    params: 'Parameter'
    expr: Expression

@dataclass
class TypeOf(Expression):
    var: Variable

@dataclass
class GetAddr(Expression):
    var: Variable
    negated: bool = False

@dataclass
class IsStmt(Expression):  # sebenarnya ini expression boolean
    left: str
    right: str
    negated: bool = False

@dataclass
class Return(Expression):
    expr: Expression

@dataclass
class Throw(Expression):
    name: str
    expr: Expression

@dataclass
class Looping(Expression):
    is_continue: bool

# --- Functions ---
class FunctionNode(Node):
    "Untuk attribute dan kerangka function"
    pass

@dataclass
class Function(FunctionNode):
    type_ann: 'Type'
    name: str
    params: 'Parameter'
    inner: 'Block'

@dataclass
class Parameter(FunctionNode):
    args: List['Argument']

@dataclass
class Generic(FunctionNode):
    args: Optional[List['Argument']]

@dataclass
class Argument(FunctionNode):
    type_ann: 'Type'
    name: str
    value: Optional[Expression] = None

@dataclass
class Decoreted(Statement):
    func_call: CallFunc
    func_target: Function

# --- Module ---
class Module(Node):
    """Dataclass terkait module"""
    pass

@dataclass
class Export(Module):
    exports: List['ExportArgument']

@dataclass
class ExportArgument(Module):
    name: Variable
    alias: Optional[str]

@dataclass
class Import(Module):
    imports: List['ImportArgument']
    from_path: 'PathID'

@dataclass
class ImportArgument(Module):
    name: str
    alias: Optional[str]

@dataclass
class PathID(Module):
    path: List['PathArg']

@dataclass
class PathArg(Module):
    arg: str

# --- Types ---
class Type(Node):
    pass

@dataclass
class BasicType(Type):
    name: str  # 'teks', 'angka', dll.

@dataclass
class ObjectType(Type):
    pass

@dataclass
class DictType(ObjectType):
    length: int
    key_type: BasicType
    value_type: BasicType
    name: str = 'tipe_objek[kamus]'

@dataclass
class ArrayType(ObjectType):
    length: int  # 0 untuk dinamis
    value_type: Type
    name: str = 'tipe_objek[daftar]'

@dataclass
class FunctionType(ObjectType):
    args_type: Optional[List[Type]]
    return_type: Type
    name: str = 'tipe_objek[fungsi]'

@dataclass
class UnionType(ObjectType):
    types: List[Type]
    name: str = 'tipe_objek[gabungan]'

@dataclass
class LiteralType(ObjectType):
    literal: List[Literal]
    name: str = 'tipe_objek[literal]'

@dataclass
class OptionalType(ObjectType):
    type_ann: Type
    name: str = 'tipe_objek[opsional]'