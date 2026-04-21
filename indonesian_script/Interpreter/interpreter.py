# ==================== interpreter.py ====================
from ..Exceptions import *
from .AST_node.ast_nodes import *
from .transformer import *
from ..Builtins import (
    BUILTINS, TYPES, BUILTINS_FUNCTIONS, Fungsi, Lambda,
    KEYWORD, SOFT_KEYWORD, Karakter,
)
from pathlib import Path
import types as T1
import typing as T2
import inspect as I

class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, attr, getindex='name'):
        if getindex == 'name':
            if attr in KEYWORD and attr not in SOFT_KEYWORD:
                raise SyntaxError(f'{attr!r} adalah kata kunci keras')
            if attr in self.vars:
                return self.vars[attr]
            if self.parent:
                return self.parent.get(attr, 'name')
            raise NameError(f"Variabel '{attr}' tidak ditemukan")
        elif getindex == 'address':
            for var in self.vars.values():
                if var['address'] == attr:
                    return var
            if self.parent:
                return self.parent.get(attr, 'address')
            raise MemoryError(f"Memory '{attr}' tidak ditemukan")
        else:
            raise AttributeError(f"getindex harus 'name' atau 'address'")

    def set(self, name, value, type_ann, address, constant=False):
        if name in KEYWORD and name not in SOFT_KEYWORD:
            raise SyntaxError(f'{name!r} adalah kata kunci keras')
        if name in self.vars:
            if self.vars[name]['constant']:
                raise TypeError(f"Variabel '{name}' adalah final")
            self.vars[name]['value'] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value, type_ann, address, constant)
            return
        self.vars[name] = {
            'type': type_ann,
            'value': value,
            'address': address,
            'constant': constant
        }

    def declare(self, name, value, type_ann, address, constant=False):
        if name in KEYWORD and name not in SOFT_KEYWORD:
            raise SyntaxError(f'{name!r} adalah kata kunci keras')
        if name in self.vars:
            raise NameError(f"Variabel '{name}' sudah dideklarasikan")
        self.vars[name] = {
            'type': type_ann,
            'value': value,
            'address': address,
            'constant': constant
        }

    def has(self, name):
        return name in self.vars

class Interpreter:
    def __init__(self, filename='<utama>', ismodule=False, ObjectDict=None):
        init_except(ObjectDict)
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self._init_builtins()
        self._module = {
            'ekspor': {},
            'impor': {},
            'berkas': 'utama' if not ismodule else filename
        }
        self._isloop = False
        self._infunction = False
        self._inclass = False
        self._filename = filename
        self.current_scope.declare(
            'modul', self._module['berkas'],
            BasicType('teks'), hex(id(self._module['berkas'])), False
        )

    def load_interp(self, interp):
        for name, obj in interp.global_scope.vars.items():
            if not self.global_scope.has(name):
                self.global_scope.declare(
                    name, obj['value'], obj['type'], obj['address'], obj['constant']
                )
        return self

    def _init_builtins(self):
        for name, value in BUILTINS.items():
            if callable(value):
                value = Fungsi(value)
                value.__name__ = name
                self.global_scope.declare(name, value, BasicType('fungsi'), hex(id(value)), True)
            else:
                type_name = type(value).__name__
                self.global_scope.declare(name, value, BasicType(type_name), hex(id(value)), True)
        for name, func_builtins in BUILTINS_FUNCTIONS.items():
            func = Fungsi(lambda *args, **kwargs: func_builtins(self, *args, **kwargs))
            func.__name__ = name
            func.__dict__.update({'nama': name, 'isi': func, 'tipe': 'fungsi', 'lokasi': hex(id(func))})
            func.__id__ = id(func)
            func.__hex__ = hex(id(func))
            self.current_scope.declare(name, func, BasicType('fungsi'), func.__hex__, True)

    def load(self, node: Node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)
            return None
        return self.visit(node)

    def visit(self, node):
        method = getattr(self, f'visit_{type(node).__name__}', self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f'Tidak ada visitor untuk {type(node).__name__}')

    # --- Statements ---
    def visit_VarDecl(self, node: VarDecl):
        try:
            value = self.visit(node.value) if node.value else None
            if value is None:
                value = self._default_value(node.type_ann)
            self._check_type(value, node.type_ann)
            self.current_scope.declare(node.name, value, node.type_ann, hex(id(value)), False)
        except SyntaxError as e:
            raise PenulisanGalat(str(e), node)
        except NameError as e:
            raise VariabelGalat(str(e), node)
        except TypeError as e:
            raise FinalGalat(str(e), node)

    def visit_FinalDecl(self, node: FinalDecl):
        try:
            value = self.visit(node.value)
            self._check_type(value, node.type_ann)
            self.current_scope.declare(node.name, value, node.type_ann, hex(id(value)), True)
        except SyntaxError as e:
            raise PenulisanGalat(str(e), node)
        except NameError as e:
            raise VariabelGalat(str(e), node)
            
    def visit_AliasDecl(self, node: AliasDecl):
        target = self.current_scope.get(node.target)
        self.current_scope.declare(node.alias, target['value'], target['type'], target['address'], False)

    def visit_Redecl(self, node: Redecl):
        try:
            value = self.visit(node.value)
            var_info = self.current_scope.get(node.name)
            self._check_type(value, var_info['type'])
            self.current_scope.set(node.name, value, var_info['type'], hex(id(value)), var_info['constant'])
        except SyntaxError as e:
            raise PenulisanGalat(str(e), node)
        except NameError as e:
            raise VariabelGalat(str(e), node)
        except TypeError as e:
            raise FinalGalat(str(e), node)

    def visit_SetObj(self, node: SetObj):
        obj = node.obj
        value = self.visit(node.value)
        target_arr = []
        while isinstance(obj, GetObj):
            target_arr.append(obj.target)
            obj = obj.obj
        target_arr.append(obj)
        base_name = target_arr[-1]
        target_arr = target_arr[:-1][::-1]
        base = self.current_scope.get(base_name)
        base_val = base['value']
        for i, target in enumerate(target_arr):
            if isinstance(target, Node):
                target = self.visit(target)
            if i != len(target_arr) - 1:
                if isinstance(base_val, dict):
                    base_val = base_val[target]
                else:
                    base_val = getattr(base_val, target)
            else:
                if isinstance(base_val, dict):
                    base_val[target] = value
                else:
                    setattr(base_val, target, value)
        self.current_scope.vars[base_name] = base

    def visit_Function(self, node: Function):
        type_ann = node.type_ann
        name = node.name
        params_func = None
        signature = I.Signature()
        if node.params and node.params.args:
            params_func = self.visit(node.params)
            signature = I.Signature(params_func.signature.values(), return_annotation=type_ann)
        inner_stmts = node.inner or []

        def func_wrapper(*args, **kwargs):
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
            self._infunction = True
            try:
                if params_func:
                    param_defs = params_func(*args, **kwargs)
                    for pdef in param_defs:
                        self.current_scope.declare(pdef['name'], pdef['value'], pdef['type'], pdef['address'], False)
                result = None
                try:
                    for stmt in inner_stmts:
                        try:
                            self.visit(stmt)
                        except ReturnSignal as ret:
                            raise ReturnSignal(ret.value)
                        except ThrowSignal:
                            raise
                        except Exception as e:
                            raise ThrowSignal(str(e))
                except ReturnSignal as ret:
                    result = ret.value
                except ThrowSignal:
                    raise
                if result is not None:
                    self._check_type(result, type_ann)
                elif type_ann.name != 'kekosongan' and inner_stmts:
                    raise TipeGalat(f"Fungsi {name!r} harus mengembalikan nilai tipe {type_ann.name}", node)
                return result
            finally:
                self.current_scope = old_scope
                self._infunction = False

        func_def = Fungsi(func_wrapper)
        func_def.__name__ = name
        func_def.__annotations__ = signature
        func_def.__dict__ = {
            'nama': name, 'isi': func_def,
            'tipe': {'kembalikan': type_ann.name},
            'lokasi': hex(id(func_def))
        }
        func_def.__id__ = id(func_def)
        func_def.__hex__ = hex(id(func_def))
        self.current_scope.declare(name, func_def, type_ann, func_def.__hex__, True)
        return func_def

    def visit_Return(self, node: Return):
        if not self._infunction:
            raise PenulisanGalat("'kembalikan' di luar fungsi", node)
        value = self.visit(node.expr)
        raise ReturnSignal(value)

    def visit_Throw(self, node: Throw):
        message = self.visit(node.expr)
        raise ThrowSignal(message)

    def visit_Decoreted(self, node: Decoreted):
        self.visit(node.func_target)
        func_def = self.current_scope.get(node.func_target.name)['value']
        call_arg = CallArgument(name=None, value=Literal(value=func_def.__dict__))
        node.func_call.params.args.append(call_arg)
        result = self.visit(node.func_call)
        self.current_scope.vars[node.func_target.name]['value'] = result

    def visit_WriteStmt(self, node: WriteStmt):
        print(self.visit(node.target), end="")

    def visit_ReadStmt(self, node: ReadStmt):
        if not isinstance(node.expr, Variable):
            raise PenulisanGalat("'bacalah' harus diikuti variabel", node)
        var_name = node.expr.name
        val = input()
        var_info = self.current_scope.get(var_name)
        try:
            converted = self._convert(val, var_info['type'])
        except:
            raise TipeGalat(f"Input tidak sesuai tipe {var_info['type'].name}", node)
        self.current_scope.set(var_name, converted, var_info['type'], hex(id(converted)), var_info['constant'])

    def visit_IfCtrl(self, node: IfCtrl):
        if self.visit(node.if_stmt):
            return
        for stmt in node.elif_stmt or []:
            if self.visit(stmt):
                return
        if node.else_stmt:
            self.visit(node.else_stmt)

    def visit_IfStmt(self, node: IfStmt):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.body)
        return cond

    def visit_ElifStmt(self, node: ElifStmt):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.body)
        return cond

    def visit_ElseStmt(self, node: ElseStmt):
        self.visit(node.body)

    def visit_WhileStmt(self, node: WhileStmt):
        self._isloop = True
        try:
            while self.visit(node.condition):
                try:
                    self.visit(node.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
                except (ReturnSignal, ThrowSignal) as e:
                    raise e
        finally:
            self._isloop = False

    def visit_ForStmt(self, node: ForStmt):
        self._isloop = True
        expr = self.visit(node.expr)
        if not hasattr(expr, 'name') or not hasattr(expr, 'get'):
            raise EkspresiGalat("Ekspresi for tidak valid", node)
        try:
            while expr.index < expr.max:
                value = expr.get()
                if value is None:
                    break
                self.current_scope.set(expr.name, value, BasicType('apapun'), hex(id(value)), False)
                try:
                    self.visit(node.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
                except (ReturnSignal, ThrowSignal) as e:
                    raise e
        finally:
            self._isloop = False

    def visit_ForExpr(self, node: ForExpr):
        name = node.name
        target = self.visit(node.target)
        if not isinstance(target, list):
            raise TipeGalat(f"Tipe {type(target).__name__} tidak mendukung iterasi", node)
        class IterHelper:
            __slots__ = ('name', 'target', 'index', 'max')
            def __init__(self, name, target):
                self.name = name
                self.target = target
                self.index = 0
                self.max = len(target)
            def get(self):
                if self.index < self.max:
                    val = self.target[self.index]
                    self.index += 1
                    return val
                return None
        return IterHelper(name, target)

    def visit_TryCtrl(self, node: TryCtrl):
        try_result = self.visit(node.try_stmt)()
        if try_result['success']:
            if node.finally_stmt:
                self.visit(node.finally_stmt)()
            return
        if node.catch_stmt:
            try:
                self.visit(node.catch_stmt)(try_result['data'])
            except ThrowSignal as e:
                if node.finally_stmt:
                    self.visit(node.finally_stmt)()
                raise e
        else:
            if node.finally_stmt:
                self.visit(node.finally_stmt)()
            raise ThrowSignal(try_result['data']['message'])

    def visit_TryStmt(self, node: TryStmt):
        def app():
            try:
                self.visit(node.body)
                return {'success': True, 'data': {}}
            except ThrowSignal as e:
                return {'success': False, 'data': {'message': e.message}}
        return app

    def visit_CatchStmt(self, node: CatchStmt):
        def app(data):
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
            try:
                self.current_scope.declare(node.name, data['message'], BasicType('teks'), hex(id(data['message'])), False)
                self.visit(node.body)
            finally:
                self.current_scope = old_scope
        return app

    def visit_FinallyStmt(self, node: FinallyStmt):
        def app():
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
            try:
                self.visit(node.body)
            finally:
                self.current_scope = old_scope
        return app

    def visit_SwitchStmt(self, node: SwitchStmt):
        expr = self.visit(node.expr)
        cases = [self.visit(stmt) for stmt in node.body if stmt]
        self._isloop = True
        try:
            for case in cases:
                try:
                    if case(expr):
                        break
                except (BreakSignal, ContinueSignal):
                    break
                except (ReturnSignal, ThrowSignal) as e:
                    raise e
        finally:
            self._isloop = False

    def visit_CaseStmt(self, node: CaseStmt):
        if len(node.expr) == 1 and node.expr[0] == '_':
            def wrapper(expr):
                for stmt in node.body:
                    self.visit(stmt)
                return True
            return wrapper
        exprs = [self.visit(e) for e in node.expr if e is not None]
        def wrapper(expr):
            if expr in exprs:
                for stmt in node.body:
                    self.visit(stmt)
                return True
            return False
        return wrapper

    def visit_Block(self, node: Block):
        old_scope = self.current_scope
        self.current_scope = Scope(parent=old_scope)
        for stmt in node.statements:
            self.visit(stmt)
        self.current_scope = old_scope

    # --- Module ---
    def visit_Export(self, node: Export):
        for arg in node.exports:
            self._module['ekspor'].update(self.visit(arg))

    def visit_ExportArgument(self, node: ExportArgument):
        obj = self.current_scope.get(node.name)
        name = node.alias or node.name
        return {name: obj}

    def visit_Import(self, node: Import):
        path_str = self.visit(node.from_path)
        module_interp, exports = self._load_module(path_str)
        for imp in node.imports:
            name = imp.name
            alias = imp.alias or name
            if name not in exports:
                raise ImporGalat(f"'{name}' tidak ditemukan di modul {path_str}", node)
            obj = exports[name]
            self.current_scope.declare(alias, obj['value'], obj['type'], obj['address'], obj['constant'])

    def visit_ImportArgument(self, node: ImportArgument):
        return node

    def visit_PathID(self, node: PathID):
        parts = [self.visit(p) for p in node.path]
        return str(Path(*parts))

    def visit_PathArg(self, node: PathArg):
        return node.arg

    # --- Expressions ---
    def visit_BinaryOp(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        try:
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '%': return left % right
            if op == '**': return left ** right
            if op == '//': return left // right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '>=': return left >= right
            if op == '>': return left > right
            if op == '<=': return left <= right
            if op == '<': return left < right
            if op == 'dan': return left and right
            if op == 'atau': return left or right
            if op == 'dalam': return left in right
            if op == 'tidak dalam': return left not in right
            raise IsiGalat(f"Operator {op} tidak dikenal", node)
        except Exception as e:
            raise TipeGalat(str(e), node)

    def visit_UnaryOp(self, node: UnaryOp):
        val = self.visit(node.expr)
        if node.op == 'tidak':
            return not val
        raise IsiGalat(f"Unary operator {node.op} tidak dikenal", node)

    def visit_Literal(self, node: Literal):
        val = node.value
        if isinstance(val, Node):
            return self.visit(val)
        return val

    def visit_Character(self, node: Character):
        char = Karakter(node.char)
        if char.__id__ != node.id:
            raise IsiGalat('Tipe Karakter tidak sesuai dengan kode id', node)
        return char

    def visit_Array(self, node: Array):
        result = []
        for val in node.values:
            if isinstance(val, Unpacking):
                result.extend(self.visit(val.value))
            else:
                result.append(self.visit(val))
        return result

    def visit_Dictionary(self, node: Dictionary):
        obj = {}
        for k, v in zip(node.keys, node.values):
            if isinstance(v, Node) and k is None:
                obj.update(self.visit(v))
            elif isinstance(v, Node) and k:
                obj[k] = self.visit(v)
            else:
                key = self.visit(k) if isinstance(k, Node) else k
                value = self.visit(v) if isinstance(v, Node) else v
                obj[key] = value
        return obj

    def visit_Variable(self, node: Variable):
        if not self.current_scope.has(node.name) and node.value:
            return node.value
        try:
            return self.current_scope.get(node.name)['value']
        except NameError as e:
            raise VariabelGalat(str(e), node)
        except TypeError as e:
            raise TipeGalat(str(e), node)

    def visit_GetObj(self, node: GetObj):
        obj = self.visit(node.obj)
        target = self.visit(node.target) if isinstance(node.target, Node) else node.target
        try:
            return obj[target]
        except (KeyError, IndexError, TypeError):
            try:
                return getattr(obj, target)
            except AttributeError:
                return None

    def visit_Crement(self, node: Crement):
        if not isinstance(node.obj, Variable):
            raise VariabelGalat("Peningkatan hanya untuk variabel", node)
        obj_name = node.obj.name
        obj = self.current_scope.get(obj_name)
        if not isinstance(obj['value'], int):
            raise TipeGalat("Peningkatan hanya untuk angka", node)
        if node.negated:
            obj['value'] -= 1
        else:
            obj['value'] += 1
        self.current_scope.set(obj_name, obj['value'], obj['type'], hex(id(obj['value'])), obj['constant'])

    def visit_CallFunc(self, node: CallFunc):
        func = self.visit(node.func)
        args = []
        kwargs = {}
        if node.params:
            params = self.visit(node.params)
            args = params.get('args', [])
            kwargs = params.get('kwargs', {})
        try:
            if args or kwargs:
                return func(*args, **kwargs)
            return func()
        except TypeError as e:
            if "missing" in str(e):
                raise TipeGalat(f"Parameter fungsi tidak lengkap: {e}", node)
            raise

    def visit_CallParameter(self, node: CallParameter):
        if not node.args:
            return {'args': [], 'kwargs': {}}
        args = [self.visit(a) for a in node.args]
        positional = []
        keyword = {}
        seen_keyword = False
        for arg in args:
            if arg['name']:
                seen_keyword = True
                keyword[arg['name']] = arg['value']
            else:
                if seen_keyword:
                    raise TipeGalat("Argumen posisi setelah keyword tidak diperbolehkan", node)
                positional.append(arg['value'])
        return {'args': positional, 'kwargs': keyword}

    def visit_CallArgument(self, node: CallArgument):
        return {'name': node.name, 'value': self.visit(node.value)}

    def visit_LambdaFunc(self, node: LambdaFunc):
        params_func = None
        if node.params and node.params.args:
            params_func = self.visit(node.params)
        expr = node.expr
        def lambda_wrapper(*args, **kwargs):
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
            try:
                if params_func:
                    param_defs = params_func(*args, **kwargs)
                    for pdef in param_defs:
                        self.current_scope.declare(pdef['name'], pdef['value'], pdef['type'], pdef['address'], False)
                return self.visit(expr)
            finally:
                self.current_scope = old_scope
        func_def = Lambda(lambda_wrapper)
        func_def.__name__ = '<lambda>'
        func_def.__dict__ = {'nama': '<lambda>', 'isi': func_def, 'tipe': {'kembalikan': 'apapun'}, 'lokasi': hex(id(func_def))}
        func_def.__id__ = id(func_def)
        func_def.__hex__ = hex(id(func_def))
        return func_def

    def visit_TypeOf(self, node: TypeOf):
        obj = self.current_scope.get(node.var.name)
        if isinstance(obj['type'], BasicType):
            return obj['type'].name
        return str(obj['type'])

    def visit_GetAddr(self, node: GetAddr):
        if node.negated:
            addr = self.current_scope.get(node.var)['value']
            return self.current_scope.get(addr, 'address')
        return self.current_scope.get(node.var)['address']

    def visit_IsStmt(self, node: IsStmt):
        left = self.current_scope.get(node.left)
        right = self.current_scope.get(node.right)
        same = (left is right) or (left['value'] == right['value'] and left['type'] == right['type'] and left['address'] == right['address'])
        return not same if node.negated else same

    def visit_Looping(self, node: Looping):
        if not self._isloop:
            raise PenulisanGalat(f"'lanjutkan' atau 'berhentikan' di luar perulangan", node)
        if node.is_continue:
            raise ContinueSignal()
        raise BreakSignal()

    def visit_Parameter(self, node: Parameter):
        if not node.args:
            def empty(*a, **kw):
                return []
            empty.signature = {}
            return empty
        arg_funcs = [self.visit(a) for a in node.args]
        sig = {af.name: af.signature for af in arg_funcs}
        def app(*args, **kwargs):
            result = [None] * len(arg_funcs)
            for i, af in enumerate(arg_funcs):
                if i < len(args):
                    result[i] = af(args[i])
                else:
                    result[i] = None
            for i, af in enumerate(arg_funcs):
                if result[i] is None:
                    if af.name in kwargs:
                        result[i] = af(kwargs[af.name])
                    else:
                        try:
                            result[i] = af()
                        except IsiGalat:
                            raise IsiGalat(f"Argumen '{af.name}' wajib diisi", node)
            return result
        app.signature = sig
        return app

    def visit_Argument(self, node: Argument):
        default = self.visit(node.value) if node.value else None
        def app(val=None):
            if val is None:
                if default is not None:
                    val = default
                else:
                    raise IsiGalat(f"Argumen '{node.name}' wajib diisi", node)
            self._check_type(val, node.type_ann)
            return {'name': node.name, 'type': node.type_ann, 'value': val, 'address': hex(id(val)), 'constant': False}
        app.name = node.name
        app.type = node.type_ann
        app.value = default
        app.signature = I.Parameter(name=node.name, default=default or I._empty, annotation=node.type_ann, kind=I._ParameterKind(1))
        return app

    # --- Type visitors ---
    def visit_BasicType(self, node: BasicType):
        obj = self.current_scope.get(node.name)['value']
        return {'type': 'basic', 'data_type': {'name': node.name, 'value': obj}}
    def visit_DictType(self, node: DictType):
        return {'type': 'dict', 'data_type': {'length': int(node.length), 'key': node.key_type, 'value': node.value_type, 'origin': dict}}
    def visit_ArrayType(self, node: ArrayType):
        return {'type': 'array', 'data_type': {'length': int(node.length), 'value': node.value_type, 'origin': list}}
    def visit_FunctionType(self, node: FunctionType):
        return {'type': 'function', 'data_type': {'arguments': node.args_type or [], 'return_type': node.return_type, 'origin': T1.FunctionType}}
    def visit_UnionType(self, node: UnionType):
        return {'type': 'union', 'data_type': {'types': node.types, 'origin': T1.UnionType}}
    def visit_LiteralType(self, node: LiteralType):
        return {'type': 'literal', 'data_type': {'literal': node.literal, 'origin': T2.Literal}}
    def visit_OptionalType(self, node: OptionalType):
        return {'type': 'optional', 'data_type': {'type': node.type_ann, 'origin': T2.Optional}}

    # --- Helpers ---
    def _check_type(self, value, type_ann):
        if not self._check_instance(value, type_ann):
            raise TipeGalat(f"Tipe tidak sesuai: {type_ann.name!r} != {value!r}", node)

    def _check_instance(self, value, type_ann):
        if isinstance(type_ann, BasicType):
            if type_ann.name == 'apapun':
                return True
            if type_ann.name == 'kekosongan':
                return value is None
            expected = TYPES.get(type_ann.name, object)
            return isinstance(value, expected)
        # untuk tipe kompleks, kita sederhanakan
        return isinstance(value, object)  # fallback

    def _default_value(self, type_ann):
        if isinstance(type_ann, BasicType):
            name = type_ann.name
            if name in ('apapun', 'kekosongan'):
                return None
            if name == 'angka':
                return 0
            if name == 'desimal':
                return 0.0
            if name == 'teks':
                return ""
            if name == 'boolean':
                return False
            if name == 'daftar':
                return []
            if name == 'kamus':
                return {}
        return None

    def _convert(self, s, type_ann):
        if isinstance(type_ann, BasicType):
            if type_ann.name == 'teks':
                return s
            if type_ann.name == 'angka':
                return int(s)
            if type_ann.name == 'desimal':
                return float(s)
            if type_ann.name == 'boolean':
                return s.lower() == 'benar'
        return s

    def _load_module(self, path_str):
        from .compile import Compile
        path = Path(self._filename).parent / path_str
        key = str(path)
        if key in self._module['impor']:
            return self._module['impor'][key]
        if not path.exists():
            raise JalurGalat(f"Jalur modul '{path_str}' tidak ditemukan", node)
        if path.is_dir():
            if str(path) == 'builtins':
                path = Path(__file__).parent / 'Builtins' / 'Built-ins'
            init_file = path / 'inisiasi.is'
            if not init_file.exists():
                raise PaketGalat(f"Paket '{path.name}' tidak memiliki inisiasi.is", node)
            path = init_file
        if path.suffix == '.py':
            from importlib.util import spec_from_file_location
            spec = spec_from_file_location(path.stem, str(path))
            module = spec.loader.load_module()
            for attr in dir(module):
                val = getattr(module, attr)
                if hasattr(val, '_get_interp'):
                    interp = val._get_interp()
                    cache = (interp, interp._module['ekspor'])
                    self._module['impor'][key] = cache
                    return cache
            return (None, None)
        code = path.read_text(encoding='utf-8')
        module_interp = Compile(filename=str(path), code=code, ismodule=True)
        module_interp()
        interp = module_interp.get_interp()
        cache = (interp, interp._module['ekspor'])
        self._module['impor'][key] = cache
        return cache

    def _get_current_scope(self):
        return self.current_scope

    def _get_global_scope(self):
        return self.global_scope