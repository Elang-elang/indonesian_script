# transformer.py
from lark import Transformer, v_args, Token, Lark, UnexpectedInput, v_args
from .AST_node.ast_nodes import *
from ..Exceptions import *
from ..Builtins import get_builtin_type
from .utils import Object
from pathlib import Path as p

class ASTBuilder(Transformer):
    def __init__(self):
        self.object = Object(True)
    
    def load(self, code):
        gramm_path = p(__file__).parent / 'grammar.txt'
        gramm = None
        with open(gramm_path, 'r') as f:
            gramm = f.read()
        
        parser = Lark(
            gramm,
            regex=True,
            parser='earley', # 'earley',
            lexer="dynamic",
            start='program',
            ambiguity="resolve",
            propagate_positions=True,
        )
        
        def func():
            tree = parser.parse(code)
            ast = self.transform(tree)
            return ast
        
        res = func()
        return res
    
    # --- Program & Blocks ---
    @v_args(meta=True)
    def program(self, meta, items):
        # items: list dari hasil top_stmt
        if not items:
           res = Program(statements=[])
           self.object.set(res, meta.__dict__)
           return res
        all_stmts = []
        for item in items:
            if isinstance(item, list):
                all_stmts.extend(item)      # jika item adalah list (dari non_block)
            elif isinstance(item, Statement):
                all_stmts.append(item)       # jika item adalah Statement tunggal (block/ctrl_flow)
                
            # Abaikan None
        res = Program(statements=all_stmts)
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def top_stmt(self, meta, items):
        # items: [hasil dari non_block/block/ctrl_flow]
        return items[0]  # bisa berupa list, Statement, atau None
    
    @v_args(meta=True)
    def non_block(self, meta, items):
        # items: list of hasil buttom_stmt (bisa None jika buttom_stmt kosong)
        # Kembalikan list statement yang tidak None
        return [item for item in items if item is not None]
        
    @v_args(meta=True)
    def block(self, meta, items):
        # items adalah list of buttom_stmt
        if not items:
           res = Block(statements=[])
           self.object.set(res, meta.__dict__)
           return res
        statements = [item for item in items if item is not None]
        res = Block(statements=statements)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def stmt(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def buttom_stmt(self, meta, items):
        return items[0] if items else None
    
    @v_args(meta=True)
    def ctrl_flow(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def if_ctrl(self, meta, items):
        index = 0
        if_stmt = items[index]
        index += 1
        
        if len(items) < 2:
           res = IfCtrl(if_stmt=if_stmt, elif_stmt=[], else_stmt=None)
           self.object.set(res, meta.__dict__)
           return res
        
        elif_stmt = []
        else_stmt = None
        for item in items[1:]:
            if isinstance(item, ElifStmt):
                elif_stmt.append(item)
            elif isinstance(item, ElseStmt):
                else_stmt = item
        
        
        res = IfCtrl(if_stmt=if_stmt, elif_stmt=elif_stmt, else_stmt=else_stmt)
        
        
        self.object.set(res, meta.__dict__)
        
        
        return res
        
    @v_args(meta=True)
    def if_stmt(self, meta, items):
        cond, body = items
        res = IfStmt(condition=cond, body=body)
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def elif_stmt(self, meta, items):
        cond, body = items
        res = ElifStmt(condition=cond, body=body)
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def else_stmt(self, meta, items):
        res = ElseStmt(body=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def while_ctrl(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def while_stmt(self, meta, items):
        cond, body = items
        res = WhileStmt(condition=cond, body=body)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def for_ctrl(self, meta, items):
        return items[0]
        
    @v_args(meta=True)
    def for_stmt(self, meta, items):
        expr, body = items
        res = ForStmt(expr=expr, body=body)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def for_expr(self, meta, items):
        name, target = items
        res = ForExpr(name=str(name), target=target)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def try_ctrl(self, meta, items):
        try_stmt, catch_stmt = items[0], items[1]
        finally_stmt = None
        
        if len(items) == 3:
            finally_stmt = items[2]
        res = TryCtrl(try_stmt=try_stmt, catch_stmt=catch_stmt, finally_stmt=finally_stmt)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def try_stmt(self, meta, items):
        res = TryStmt(body=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def catch_stmt(self, meta, items):
        res = CatchStmt(name=str(items[0]), body=items[1])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def finally_stmt(self, meta, items):
        res = FinallyStmt(body=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def switch_ctrl(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def switch_stmt(self, meta, items):
        expr, body = items
        res = SwitchStmt(expr=expr, body=list(body))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def block_switch(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def body_switch(self, meta, items):
        return items
    
    @v_args(meta=True)
    def case_stmt(self, meta, items):
        expr, stmt = items
        res = CaseStmt(expr=list(expr), body=list(stmt))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def default_stmt(self, meta, items):
        res = CaseStmt(expr=['_'], body=list(items[0]))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def case_expr(self, meta, items):
        return items
    
    @v_args(meta=True)
    def body_case(self, meta, items):
        return items
    
    # --- Statements ---
    @v_args(meta=True)
    def vars_stmt(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def var_decl(self, meta, items):
        type_ann, name, value = items
        res = VarDecl(type_ann=type_ann, name=str(name), value=value)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def final_decl(self, meta, items):
        type_ann, name, value = items
        res = FinalDecl(type_ann=type_ann, name=str(name), value=value)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def def_decl(self, meta, items):
        type_ann, name = items
        res = DefDecl(type_ann=type_ann, name=str(name))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def alias_decl(self, meta, items):
        target, alias = items
        res = AliasDecl(alias=str(alias), target=str(target))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def redecl(self, meta, items):
        name, value = items
        res = Redecl(name=str(name), value=value)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def setobj(self, meta, items):
        obj = items[0]
        
        idx = 1
        while idx < len(items[:-1]) and items[idx]:
            if isinstance(items[idx], GetObj):
                obj = GetObj(obj=obj, target=items[idx].target)
            else:
                obj = GetObj(obj=obj, target=items[idx])
            idx += 1
        
        value = items[idx]
        
        res = SetObj(obj=obj, value=value)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def decoreted_stmt(self, meta, items):
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
    
    @v_args(meta=True)
    def func_def(self, meta, items):
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
    
    @v_args(meta=True)
    def block_func(self, meta, items):
        return [item for item in items if item is not None]
    
    @v_args(meta=True)
    def func_stmts(self, meta, items):
        return items[0]
        
    @v_args(meta=True)
    def func_stmt(self, meta, items):
        return items[0]

    @v_args(meta=True)
    def return_stmt(self, meta, items):
        expr = items[0]
        res = Return(expr=expr)
        self.object.set(res, meta.__dict__)
        return res  # Langsung Return node

    @v_args(meta=True)
    def throw_stmt(self, meta, items):
        expr = items
        res = Throw(expr=expr)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def cli_stmt(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def write_stmt(self, meta, items):
        res = WriteStmt(target=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def read_stmt(self, meta, items):
        res = ReadStmt(expr=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    # --- Module ---
    @v_args(meta=True)
    def module_stmt(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def export_stmt(self, meta, items):
        res = Export(exports=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def exp_params(self, meta, items):
        return items
    
    @v_args(meta=True)
    def exp_arg(self, meta, items):
        name = items[0].name
        alias = None
        if len(items) == 2:
            alias = str(items[1])
        
        res = ExportArgument(name=name, alias=alias)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def import_stmt(self, meta, items):
        imports, _from = items
        res = Import(imports=imports, from_path=_from)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def imp_params(self, meta, items):
        return items
    
    @v_args(meta=True)
    def imp_arg(self, meta, items):
        name = str(items[0])
        alias = None
        if len(items) == 2:
            alias = str(items[1])
        
        res = ImportArgument(name=name, alias=alias)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def path_stmt(self, meta, items):
        res = PathID(path=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def path_params(self, meta, items):
        return items
    
    @v_args(meta=True)
    def path_args(self, meta, items):
        res = PathArg(arg=str(items[0]))
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def path_arg(self, meta, items):
        return '.'.join(items)
    
    @v_args(meta=True)
    def parent_path(self, meta, items):
        res = str(items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def once_dot(self, meta, items):
        res = str(".")
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def two_dot(self, meta, items):
        res = str("..")
        self.object.set(res, meta.__dict__)
        return res
    
    # --- Expressions (Binary, Unary, etc.) ---
    @v_args(meta=True)
    def expression(self, meta, items):
        return items[0]
        
    @v_args(meta=True)
    def equal(self, meta, items):
        return self._binop(items, '==')
    
    @v_args(meta=True)
    def not_equal(self, meta, items):
        return self._binop(items, '!=')
    
    @v_args(meta=True)
    def great_equal(self, meta, items):
        return self._binop(items, '>=')
    
    @v_args(meta=True)
    def great_than(self, meta, items):
        return self._binop(items, '>')
    
    @v_args(meta=True)
    def less_equal(self, meta, items):
        return self._binop(items, '<=')
    
    @v_args(meta=True)
    def less_than(self, meta, items):
        return self._binop(items, '<')
    
    @v_args(meta=True)
    def or_bool(self, meta, items):
        return self._binop(items, 'atau')
    
    @v_args(meta=True)
    def and_bool(self, meta, items):
        return self._binop(items, 'dan')
    
    @v_args(meta=True)
    def in_bool(self, meta, items):
        return self._binop(items, 'dalam')
    
    @v_args(meta=True)
    def not_in(self, meta, items):
        # items: [left, 'tidak', 'dalam', right]? perlu disesuaikan dengan grammar
        # Di grammar: not_in: add ("tidak" "dalam" add)? -> ini menghasilkan dua node jika ada
        if len(items) == 1:
            return items[0]
        else:
            # items[0] adalah left, items[1] adalah right (karena 'tidak dalam' dianggap token?)
            # Tergantung bagaimana Lark mem-parsing. Kita asumsikan items = [left, right]
           res = BinaryOp(op='tidak dalam', left=items[0], right=items[1])
           self.object.set(res, meta.__dict__)
           return res
    
    @v_args(meta=True)
    def add(self, meta, items):
        return self._binop(items, '+')
    
    @v_args(meta=True)
    def minus(self, meta, items):
        return self._binop(items, '-')
    
    @v_args(meta=True)
    def multi(self, meta, items):
        return self._binop(items, '*')
    
    @v_args(meta=True)
    def divide(self, meta, items):
        return self._binop(items, '/')
    
    @v_args(meta=True)
    def modular(self, meta, items):
        return self._binop(items, '%')
        
    @v_args(meta=True)
    def pow(self, meta, items):
        return self._binop(items, '**')
        
    @v_args(meta=True)
    def floor_divide(self, meta, items):
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
    
    @v_args(meta=True)
    def not_bool(self, meta, items):
        if len(items) == 1:
            return items[0]
        else:
            # items: ['tidak', expr]
           res = UnaryOp(op='tidak', expr=items[1])
           self.object.set(res, meta.__dict__)
           return res
    
    @v_args(meta=True)
    def term(self, meta, items):
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
    
    @v_args(meta=True)
    def prefix(self, meta, items):
        # items: bisa '(' expression ')' atau literal atau expr_id
        # Setelah filter '(', ')', ambil yang bukan tanda kurung
        for item in items:
            if item not in ('(', ')'):
                return item
        return None
    
    @v_args(meta=True)
    def postfix(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def getobj(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def getattr(self, meta, items):
        # items: [ID] setelah titik
        res = GetObj(obj=object, target=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def getindex(self, meta, items):
        # items: [expression]
        res = GetObj(obj={}, target=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def crement(self, meta, items):
        res = Crement(obj=items[1], negated=items[0].negated)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def decrement(self, meta, items):
        res = Crement(obj=0, negated=True)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def increment(self, meta, items):
        res = Crement(obj=0, negated=False)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def call_params(self, meta, items):
        # items adalah list of call_args atau None
        if items:
            # items[0] adalah hasil dari call_args (list of CallArgument)
            if isinstance(items[0], list):
               res = CallParameter(args=items[0])
               self.object.set(res, meta.__dict__)
               return res
            else:
               res = CallParameter(args=[items[0]])
               self.object.set(res, meta.__dict__)
               return res
        else:
           res = CallParameter(args=[])
           self.object.set(res, meta.__dict__)
           return res
    
    @v_args(meta=True)
    def call_args(self, meta, items):
        # items adalah list of call_arg
        return items  # Sudah berupa list
    
    @v_args(meta=True)
    def call_arg(self, meta, items):
        name, value = None, None
        if len(items) > 1:
            name, value = items
        else:
            value = items[0]
        
        res = CallArgument(name=name, value=value)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def lambda_func(self, meta, items):
        params, expr = items
        res = LambdaFunc(params=params, expr=expr)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def type_of(self, meta, items):
        res = TypeOf(var=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def pointer(self, meta, items):
        res = GetAddr(var=str(items[0]), negated=False)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def unpointer(self, meta, items):
        res = GetAddr(var=str(items[0]), negated=True)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def is_stmt(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def is_bool(self, meta, items):
        # items: [ID, 'adalah', ID]
        res = IsStmt(left=str(items[0]), right=str(items[1]), negated=False)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def is_not_bool(self, meta, items):
        # items: [ID, 'bukanlah', ID]
        res = IsStmt(left=str(items[0]), right=str(items[1]), negated=True)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def continue_stmt(self, meta, items):
        res = Looping(is_continue=True)
        self.object.set(res, meta.__dict__)
        return res
        
    @v_args(meta=True)
    def break_stmt(self, meta, items):
        res = Looping(is_continue=False)
        self.object.set(res, meta.__dict__)
        return res
    
    def VAR_NAME(self, items):
        res = Variable(name=str(items))
        self.object.set(res, None)
        return res
    
    # --- Literals ---
    @v_args(meta=True)
    def literal(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def basic_literal(self, meta, items):
        return items[0]
        
    @v_args(meta=True)
    def object_literal(self, meta, items):
        return items[0]
        
    @v_args(meta=True)
    def string(self, meta, items):
        # items[0] adalah token string dengan quotes
        s = items[0][1:-1]  # buang quotes
        res = Literal(value=s)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def character(self, meta, items):
        char = items[0]
        try:
           res = Literal(value=Character(id=ord(char), char=str(char)))
           self.object.set(res, meta.__dict__)
           return res
        except:
           res = PenulisanGalat(f"Tipe karakter harus memiliki 1 karakter")
           self.object.set(res, meta.__dict__)
           return res
    
    @v_args(meta=True)
    def integer(self, meta, items):
        res = Literal(value=int(items[0]))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def float(self, meta, items):
        res = Literal(value=float(items[0]))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def boolean(self, meta, items):
        res = Literal(value=(items[0] == 'benar'))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def array(self, meta, items):
        res = Literal(value=Array(values=list(items)))
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def array_body(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def dictinary(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def dict_body(self, meta, items):
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
    
    @v_args(meta=True)
    def dict_bodies(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def dict_items(self, meta, items):
        key, value = items
        if isinstance(key, Literal):
            key = key.value
        return {key: value}
    
    @v_args(meta=True)
    def key_params(self, meta, items):
        # bisa basic_literal atau [expr_id] atau ID
        return items[0]  # sudah berupa nilai literal atau string
    
    @v_args(meta=True)
    def value_params(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def unpack(self, meta, items):
        res = Unpacking(value=items[0])
        self.object.set(res, meta.__dict__)
        return res
    # --- Types ---
    @v_args(meta=True)
    def type_ann(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def basic_type(self, meta, items):
        # items[0] adalah ID dari tipe (misal 'teks')
        name = items[0]
        if isinstance(name, Token):
            name = name.value
        res = BasicType(name=name)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def object_type(self, meta, items):
        return items[0]
    
    @v_args(meta=True)
    def dict_type(self, meta, items):
        length = items[0]
        key_type = items[1]
        value_type = items[2]
        
        res = DictType(length=int(length.value), key_type=key_type, value_type=value_type)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def array_type(self, meta, items):
        length = items[0]
        value_type = items[1]
        
        res = ArrayType(length=int(length.value), value_type=value_type)
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def func_type(self, meta, items):
        types = []
        if len(items) == 1:
           res = FunctionType(args_type=[], return_type=items[-1])
           self.object.set(res, meta.__dict__)
           return res
            
        for i in items[:-1]:
            types.append(i)
        
        res = FunctionType(args_type=types, return_type=items[-1])
        
        self.object.set(res, meta.__dict__)
        
        return res
    
    @v_args(meta=True)
    def union_type(self, meta, items):
        res = UnionType(types=items)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def literal_type(self, meta, items):
        res = LiteralType(literal=items)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def optional_type(self, meta, items):
        res = OptionalType(type_ann=items[0])
        self.object.set(res, meta.__dict__)
        return res
    
    # --- IDs ---
    def ID(self, token):
        res = str(token)
        self.object.set(res, meta.__dict__)
        return res
    
    # --- Params ---
    @v_args(meta=True)
    def params(self, meta, items):
        if items:
            return items[0]
        else:
            return items
        
    @v_args(meta=True)
    def param(self, meta, items):
        res = Parameter(args=items)
        self.object.set(res, meta.__dict__)
        return res
    
    @v_args(meta=True)
    def args(self, meta, items):
        type_ann, name, value = None, None, None
        
        if len(items) > 2:
            type_ann, name, value = items
        else:
            type_ann, name = items
            
        res = Argument(type_ann=type_ann, name=str(name), value=value)
            
        self.object.set(res, meta.__dict__)
            
        return res
    
    # --- help ---
    def _del_list(self, meta, items):
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(self._del_list(item))
            else:
                result.append(item)
        
        return result