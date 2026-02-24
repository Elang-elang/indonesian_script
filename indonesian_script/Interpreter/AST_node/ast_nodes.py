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
class VarDecl(Statement):
    type_ann: 'Type'
    name: str
    value: Optional['Expression']

@dataclass
class FinalDecl(Statement):
    type_ann: 'Type'
    name: str
    value: 'Expression'

@dataclass
class DefDecl(Statement):
    type_ann: 'Type'
    name: str

@dataclass
class AliasDecl(Statement):
    alias: str
    target: str

@dataclass
class Redecl(Statement):
    name: str
    value: 'Expression'

@dataclass
class PointerDecl(Statement):
    name: str
    target: str

@dataclass
class UnpointerDecl(Statement):
    name: str
    target: str

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
class Variable(Expression):
    name: str

@dataclass
class GetAttr(Expression):
    obj: Expression
    attr: str

@dataclass
class GetIndex(Expression):
    obj: Expression
    index: Expression

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
class IsStmt(Expression):  # sebenarnya ini expression boolean
    left: str
    right: str
    negated: bool = False


# --- Functions ---
@dataclass
class FunctionNode(Node):
    "Untuk attribute dan kerangka function"
    pass

@dataclass
class Function(FunctionNode):
    type_ann: 'Type'
    name: str
    params: 'Parameter'
    inner: 'FuncStmt'

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
    value: Optional[Expression]

@dataclass
class Return(Expression):
    expr: Expression

@dataclass
class Throw(Expression):
    name: str
    expr: Expression

# --- Types ---
class Type(Node):
    pass

@dataclass
class BasicType(Type):
    name: str  # 'teks', 'angka', dll.

@dataclass
class ArrayType(Type):
    length: int  # 0 untuk dinamis
    element_type: Type