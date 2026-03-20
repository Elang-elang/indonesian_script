# transformer.py
from lark import Transformer, v_args
from .AST_node.ast_nodes import *
from .Exceptions.exceptions import *
from .Builtins.builtins import get_builtin_type

class ASTBuilder(Transformer):
    def __init__(self):
        self._scope_stack = []  # optional, untuk validasi semantik (misal cek duplikat)
    
    # --- Program & Blocks ---
    
    def program(self, items):
        # items: list dari hasil top_stmt
        if not items:
            return Program(statements=[])
        all_stmts = []
        for item in items:
            if isinstance(item, list):
                all_stmts.extend(item)      # jika item adalah list (dari non_block)
            elif isinstance(item, Statement):
                all_stmts.append(item)       # jika item adalah Statement tunggal (block/ctrl_flow)
                
            # Abaikan None
        return Program(statements=all_stmts)
        
    def top_stmt(self, items):
        # items: [hasil dari non_block/block/ctrl_flow]
        return items[0]  # bisa berupa list, Statement, atau None
    
    def non_block(self, items):
        # items: list of hasil buttom_stmt (bisa None jika buttom_stmt kosong)
        # Kembalikan list statement yang tidak None
        return [item for item in items if item is not None]
        
    def block(self, items):
        # items adalah list of buttom_stmt
        if not items:
            return Block(statements=[])
        statements = [item for item in items if item is not None]
        return Block(statements=statements)
    
    def stmt(self, items):
        return items[0]
    
    def buttom_stmt(self, items):
        return items[0] if items else None
    
    def ctrl_flow(self, items):
        return items[0]
    
    def if_ctrl(self, items):
        index = 0
        if_stmt = items[index]
        index += 1
        
        if len(items) < 2:
            return IfCtrl(if_stmt=if_stmt, elif_stmt=[], else_stmt=None)
        
        elif_stmt = []
        else_stmt = None
        for item in items[1:]:
            if isinstance(item, ElifStmt):
                elif_stmt.append(item)
            elif isinstance(item, ElseStmt):
                else_stmt = item
        
        
        return IfCtrl(if_stmt=if_stmt, elif_stmt=elif_stmt, else_stmt=else_stmt)
        
    def if_stmt(self, items):
        cond, body = items
        return IfStmt(condition=cond, body=body)
        
    def elif_stmt(self, items):
        cond, body = items
        return ElifStmt(condition=cond, body=body)
        
    def else_stmt(self, items):
        return ElseStmt(body=items[0])
    
    def while_ctrl(self, items):
        return items[0]
    
    def while_stmt(self, items):
        cond, body = items
        return WhileStmt(condition=cond, body=body)
    
    def for_ctrl(self, items):
        return items[0]
        
    def for_stmt(self, items):
        expr, body = items
        return ForStmt(expr=expr, body=body)
    
    def for_expr(self, items):
        name, target = items
        return ForExpr(name=str(name), target=target)
    
    def try_ctrl(self, items):
        try_stmt, catch_stmt = items[0], items[1]
        finally_stmt = None
        
        if len(items) == 3:
            finally_stmt = items[2]
        return TryCtrl(try_stmt=try_stmt, catch_stmt=catch_stmt, finally_stmt=finally_stmt)
    
    def try_stmt(self, items):
        return TryStmt(body=items[0])
    
    def catch_stmt(self, items):
        return CatchStmt(name=str(items[0]), body=items[1])
    
    def finally_stmt(self, items):
        return FinallyStmt(body=items[0])
    
    def switch_ctrl(self, items):
        return items[0]
    
    def switch_stmt(self, items):
        pass
    
    # --- Statements ---
    def vars_stmt(self, items):
        return items[0]
    
    def var_decl(self, items):
        type_ann, name, value = items
        return VarDecl(type_ann=type_ann, name=str(name), value=value)
    
    def final_decl(self, items):
        type_ann, name, value = items
        return FinalDecl(type_ann=type_ann, name=str(name), value=value)
    
    def def_decl(self, items):
        type_ann, name = items
        return DefDecl(type_ann=type_ann, name=str(name))
    
    def alias_decl(self, items):
        target, alias = items
        return AliasDecl(alias=str(alias), target=str(target))
    
    def redecl(self, items):
        name, value = items
        return Redecl(name=str(name), value=value)
    
    def setobj(self, items):
        obj = items[0]
        
        idx = 1
        while idx < len(items[:-1]) and items[idx]:
            if isinstance(items[idx], GetObj):
                obj = GetObj(obj=obj, target=items[idx].target)
            else:
                obj = GetObj(obj=obj, target=items[idx])
            idx += 1
        
        value = items[idx]
        
        return SetObj(obj=obj, value=value)
    
    def decoreted_stmt(self, items):
        """# [decorator] function_definition """
        # items: [ decorator, postfix*, '\n', func_def]
        
        # Ambil decorator (ID)
        decorator = items[0]
        postfixes = []
        idx = 1
        while idx < len(items) - 2 and items[idx] not in (']', '{'):
            if items[idx] not in (']', '{'):
                postfixes.append(items[idx])
            idx += 1
        
        # Ambil function definition
        func_def = None
        for item in items:
            if isinstance(item, Function):
                func_def = item
                break
        
        if not func_def:
            raise PenulisanGalat("Decorated statement harus berisi definisi fungsi")
        
        # Buat base decorator
        base = Variable(name=str(decorator))
        
        # Terapkan postfixes
        for post in postfixes:
            if isinstance(post, GetAttr):
                base = GetAttr(obj=base, attr=post.attr)
            elif isinstance(post, GetIndex):
                base = GetIndex(obj=base, index=post.index)
            elif isinstance(post, CallParameter):
                # Ini adalah pemanggilan decorator dengan parameter
                base = CallFunc(func=base, params=post)
        
        if isinstance(base, Variable):
            base = CallFunc(
                func=base, params=CallParameter(
                    args=[]
                )
            )
        
        # Sekarang base adalah decorator yang sudah diproses
        # Kita perlu membuat AST untuk: @decorator
        # yaitu: decorator(function_definition)
        
        # Buat CallArgument untuk fungsi
        # Panggil decorator dengan fungsi sebagai argumen
        return Decoreted(
            func_call=base,
            func_target=func_def
        )
    
    def func_def(self, items):
        index = 0
        
        type_ann = items[index]
        index += 1
        
        name = items[index]
        index += 1
        
        # Untuk update nanti (hanya peranti)
        generic_params = []
        if isinstance(items[index], Generic):
            generic_params.extend(items[index])
            index += 1
        
        params = items[index]
        index += 1
        
        inner = items[index]
        return Function(
            type_ann=type_ann,
            name=str(name),
            params=params,
            inner=inner
        )
    
    def block_func(self, items):
        return [item for item in items if item is not None]
    
    def func_stmts(self, items):
        return items[0]
        
    def func_stmt(self, items):
        return items[0]

    def return_stmt(self, items):
        expr = items[0]
        return Return(expr=expr)  # Langsung Return node

    def throw_stmt(self, items):
        name, expr = items
        return Throw(name=str(name), expr=expr)
    
    def cli_stmt(self, items):
        return items[0]
    
    def write_stmt(self, items):
        return WriteStmt(target=items[0])
    
    def read_stmt(self, items):
        return ReadStmt(expr=items[0])
    
    # --- Module ---
    def module_stmt(self, items):
        return items[0]
    
    def export_stmt(self, items):
        return Export(exports=items[0])
    
    def exp_params(self, items):
        return items
    
    def exp_arg(self, items):
        name = items[0].name
        alias = None
        if len(items) == 2:
            alias = str(items[1])
        
        return ExportArgument(name=name, alias=alias)
    
    def import_stmt(self, items):
        imports, _from = items
        return Import(imports=imports, from_path=_from)
    
    def imp_params(self, items):
        return items
    
    def imp_arg(self, items):
        name = str(items[0])
        alias = None
        if len(items) == 2:
            alias = str(items[1])
        
        return ImportArgument(name=name, alias=alias)
    
    def path_stmt(self, items):
        return PathID(path=items[0])
    
    def path_params(self, items):
        return items
    
    def path_args(self, items):
        return PathArg(arg=str(items[0]))
        
    def path_arg(self, items):
        return '.'.join(items)
    
    def parent_path(self, items):
        return str(items[0])
    
    def once_dot(self, items):
        return str(".")
        
    def two_dot(self, items):
        return str("..")
    
    # --- Expressions (Binary, Unary, etc.) ---
    def expression(self, items):
        return items[0]
        
    def equal(self, items):
        return self._binop(items, '==')
    
    def not_equal(self, items):
        return self._binop(items, '!=')
    
    def great_equal(self, items):
        return self._binop(items, '>=')
    
    def great_than(self, items):
        return self._binop(items, '>')
    
    def less_equal(self, items):
        return self._binop(items, '<=')
    
    def less_than(self, items):
        return self._binop(items, '<')
    
    def or_bool(self, items):
        return self._binop(items, 'atau')
    
    def and_bool(self, items):
        return self._binop(items, 'dan')
    
    def in_bool(self, items):
        return self._binop(items, 'dalam')
    
    def not_in(self, items):
        # items: [left, 'tidak', 'dalam', right]? perlu disesuaikan dengan grammar
        # Di grammar: not_in: add ("tidak" "dalam" add)? -> ini menghasilkan dua node jika ada
        if len(items) == 1:
            return items[0]
        else:
            # items[0] adalah left, items[1] adalah right (karena 'tidak dalam' dianggap token?)
            # Tergantung bagaimana Lark mem-parsing. Kita asumsikan items = [left, right]
            return BinaryOp(op='tidak dalam', left=items[0], right=items[1])
    
    def add(self, items):
        return self._binop(items, '+')
    
    def minus(self, items):
        return self._binop(items, '-')
    
    def multi(self, items):
        return self._binop(items, '*')
    
    def divide(self, items):
        return self._binop(items, '/')
    
    def modular(self, items):
        return self._binop(items, '%')
        
    def pow(self, items):
        return self._binop(items, '**')
        
    def floor_divide(self, items):
        return self._binop(items, '//')
    
    def _binop(self, items, op):
        if len(items) == 1:
            return items[0]
        # Asumsikan items bergantian: [left, op, right, op, right2, ...] tapi di grammar menggunakan *
        # Biasanya Lark untuk aturan seperti "add: minus ('+' minus)*" akan menghasilkan flat list:
        # [minus, '+', minus, '+', minus] -> kita perlu menggabungkan secara berurutan.
        # Cara mudah: iterasi dan buat binary tree kiri-assosiatif.
        left = items[0]
        for i in range(len(items) - 1):
            right = items[i+1]
            left = BinaryOp(op=op, left=left, right=right)
        return left
    
    def not_bool(self, items):
        if len(items) == 1:
            return items[0]
        else:
            # items: ['tidak', expr]
            return UnaryOp(op='tidak', expr=items[1])
    
    def term(self, items):
        # items: [prefix, postfix1, postfix2, ...]
        if len(items) == 1:
            return items[0]
        
        base = items[0]
        for post in items[1:]:
            if isinstance(post, GetObj):
                base = GetObj(obj=base, target=post.target)
            elif isinstance(post, CallParameter):
                base = CallFunc(func=base, params=post)
        return base
    
    def prefix(self, items):
        # items: bisa '(' expression ')' atau literal atau expr_id
        # Setelah filter '(', ')', ambil yang bukan tanda kurung
        for item in items:
            if item not in ('(', ')'):
                return item
        return None
    
    def postfix(self, items):
        return items[0]
    
    def getobj(self, items):
        return items[0]
    
    def getattr(self, items):
        # items: [ID] setelah titik
        return GetObj(obj=object, target=items[0])
    
    def getindex(self, items):
        # items: [expression]
        return GetObj(obj={}, target=items[0])
    
    def crement(self, items):
        return Crement(obj=items[1], negated=items[0].negated)
    
    def decrement(self, items):
        return Crement(obj=0, negated=True)
    
    def increment(self, items):
        return Crement(obj=0, negated=False)
    
    def call_params(self, items):
        # items adalah list of call_args atau None
        if items:
            # items[0] adalah hasil dari call_args (list of CallArgument)
            if isinstance(items[0], list):
                return CallParameter(args=items[0])
            else:
                return CallParameter(args=[items[0]])
        else:
            return CallParameter(args=[])
    
    def call_args(self, items):
        # items adalah list of call_arg
        return items  # Sudah berupa list
    
    def call_arg(self, items):
        name, value = None, None
        if len(items) > 1:
            name, value = items
        else:
            value = items[0]
        
        return CallArgument(name=name, value=value)
    
    def lambda_func(self, items):
        params, expr = items
        return LambdaFunc(params=params, expr=expr)
    
    def type_of(self, items):
        return TypeOf(var=items[0])
    
    def pointer(self, items):
        return GetAddr(var=str(items[0]), negated=False)
    
    def unpointer(self, items):
        return GetAddr(var=str(items[0]), negated=True)
    
    def is_stmt(self, items):
        return items[0]
    
    def is_bool(self, items):
        # items: [ID, 'adalah', ID]
        return IsStmt(left=str(items[0]), right=str(items[1]), negated=False)
    
    def is_not_bool(self, items):
        # items: [ID, 'bukanlah', ID]
        return IsStmt(left=str(items[0]), right=str(items[1]), negated=True)
    
    def VAR_NAME(self, items):
        return Variable(name=str(items))
    
    # --- Literals ---
    def literal(self, items):
        return items[0]
    
    def basic_literal(self, items):
        return items[0]
        
    def object_literal(self, items):
        return items[0]
        
    def string(self, items):
        # items[0] adalah token string dengan quotes
        s = items[0][1:-1]  # buang quotes
        return Literal(value=s)
    
    def integer(self, items):
        return Literal(value=int(items[0]))
    
    def float(self, items):
        return Literal(value=float(items[0]))
    
    def boolean(self, items):
        return Literal(value=(items[0] == 'benar'))
    
    def array(self, items):
        return Literal(value=Array(values=list(items)))
    
    def array_body(self, items):
        return items[0]
    
    def dictinary(self, items):
        return items[0]
    
    def dict_body(self, items):
        # items adalah list of dict_bodies yang masing-masing punya satu pasang
        key = []
        value = []
        for body in items:
            if isinstance(body, Variable):
                key.append(body.name)
                value.append(body)
            elif isinstance(body, Unpacking):
                key.append(None)
                value.append(body.value)
            else:
                for k, v in body.items():
                    key.append(k)
                    value.append(v)
        return Literal(value=Dictionary(
            keys=key, values=value
        ))
    
    def dict_bodies(self, items):
        return items[0]
    
    def dict_items(self, items):
        key, value = items
        if isinstance(key, Literal):
            key = key.value
        return {key: value}
    
    def key_params(self, items):
        # bisa basic_literal atau [expr_id] atau ID
        return items[0]  # sudah berupa nilai literal atau string
    
    def value_params(self, items):
        return items[0]
    
    def unpacking(self, items):
        return Unpacking(value=items[0])
    # --- Types ---
    def type_ann(self, items):
        return items[0]
    
    def basic_type(self, items):
        # items[0] adalah ID dari tipe (misal 'teks')
        type_name = str(items[0])
        # Dapatkan tipe Python dari builtins
        return BasicType(name=type_name)
    
    # --- IDs ---
    def ID(self, token):
        return str(token)
    
    # --- Params ---
    def params(self, items):
        if items:
            return items[0]
        else:
            return items
        
    def param(self, items):
        return Parameter(args=items)
    
    def args(self, items):
        type_ann, name, value = None, None, None
        
        if len(items) > 2:
            type_ann, name, value = items
        else:
            type_ann, name = items
            
        return Argument(type_ann=type_ann, name=str(name), value=value)
    
    # --- help ---
    def _del_list(self, items):
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(self._del_list(item))
            else:
                result.append(item)
        
        return result