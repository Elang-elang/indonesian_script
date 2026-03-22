# interpreter.py
from .Exceptions.exceptions import *
from .AST_node.ast_nodes import *
from .transformer import *
from .Builtins.builtins import BUILTINS, TYPES, BUILTINS_FUNCTIONS, Fungsi, Lambda
from pathlib import Path

class Scope:
    def __init__(self, parent=None):
        self.vars = {}  # name -> {'type': ..., 'value': ..., 'constant': bool}
        self.parent = parent
    
    def get(self, attr, getindex: ['name', 'address'] = 'name'):
        # __import__('pprint').pprint(self.vars)
        if getindex == 'name':
            if attr in self.vars:
                return self.vars[attr]
            if self.parent:
                return self.parent.get(attr, 'name')
            raise VariabelGalat(f"Variabel '{attr}' tidak ditemukan")
        elif getindex == 'address':
            for var in self.vars:
                if self.vars[var]['address'] == attr:
                    return self.vars[var]
            if self.parent:
                return self.parent.get(attr, 'address')
            raise AlamatMemoriGalat(f"Memory '{attr}' tidak ditemukan")
        else:
            raise AtributGalat(f"Tidak ada getindex dengan '{getindex}' hanya ada dengan 'name' atau 'address' saja")
    
    def set(self, name, value, type_ann, address, constant=False):
        # Cek apakah sudah ada di scope ini atau parent (untuk reassign)
        if name in self.vars:
            if self.vars[name]['constant']:
                raise FinalGalat(f"Variabel '{name}' adalah final, tidak bisa diubah")
            self.vars[name]['value'] = value
            return
        # Cek di parent untuk reassign? Biasanya assignment mencari di scope terdekat
        if self.parent and self.parent.has(name):
            self.parent.set(name, value, type_ann, address, constant)
            return
        # Jika tidak ada, buat baru di scope lokal
        self.vars[name] = {
            'type': type_ann,
            'value': value,
            'address': address,
            'constant': constant
        }
    
    def declare(self, name, value, type_ann, address, constant=False):
        if name in self.vars:
            raise VariabelGalat(f"Variabel '{name}' sudah dideklarasikan di scope ini")
        self.vars[name] = {
            'type': type_ann,
            'value': value,
            'address': address,
            'constant': constant
        }
    
    def has(self, name):
        return name in self.vars

class Interpreter:
    def __init__(self, filename='<utama>', ismodule=False):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self._init_builtins()
        
        self._output = []
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
            'modul',
            self._module['berkas'],
            BasicType('teks'),
            hex(id(self._module['berkas'])),
            False
        )
    
    def _init_builtins(self):
        # Masukkan tipe bawaan dan konstanta
        for name, value in BUILTINS.items():
            if callable(value):
                # fungsi built-in
                value = Fungsi(value)
                value.__name__ = name
                self.global_scope.declare(name, value, BasicType('fungsi'), hex(id(value)), constant=True)
            else:
                # konstanta seperti benar, salah, kosong
                type_name = type(value).__name__
                self.global_scope.declare(name, value, BasicType(type_name), hex(id(value)), constant=True)
        
        # khusus untuk BUILTINS_FUNCTIONS yang membutuhkan 'self'
        for name, func_builtins in BUILTINS_FUNCTIONS.items():
            func = Fungsi(lambda *args, **kwargs: func_builtins(self, *args, **kwargs))
            func.__name__ = name
            func.__dict__.update({
                'nama': name,
                'isi': func,
                'tipe': 'fungsi',
                'lokasi': hex(id(func))
            })
            func.__id__ = id(func)
            func.__hex__ = hex(id(func))
            
            self.current_scope.declare(
                name,
                func,
                BasicType('fungsi'),
                func.__hex__,
                True
            )
        
    def load(self, node: Node):
        """Method utama untuk mengeksekusi AST. Mengembalikan hasil akhir (misal output)."""
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)
        else:
            self.visit(node)
        # Kembalikan sesuatu? Mungkin output yang dikumpulkan
        return self._output  # kita perlu koleksi output
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        #print(node)
        return visitor(node)
    
    def generic_visit(self, node):
        raise NotImplementedError(f'Tidak ada visitor untuk {type(node).__name__}')
    
    # --- Statements ---
    def visit_VarDecl(self, node: VarDecl):
        value = self.visit(node.value) if node.value else None
        # Jika value None, gunakan default sesuai tipe
        if value is None:
            value = self._default_value(node.type_ann)
        # Cek tipe
        self._check_type(value, node.type_ann)
        self.current_scope.declare(node.name, value, node.type_ann, hex(id(value)), constant=False)
        
        #print(self.current_scope.get(node.name))
    
    def visit_FinalDecl(self, node: FinalDecl):
        value = self.visit(node.value)
        self._check_type(value, node.type_ann)
        self.current_scope.declare(node.name, value, node.type_ann, hex(id(value)), constant=True)
    
    def visit_DefDecl(self, node: DefDecl):
        #__import__('pprint').pprint(self.current_scope.vars, width=50, indent=2)
        
        value = self._default_value(node.type_ann)
        self.current_scope.declare(node.name, value, node.type_ann, hex(id(value)), constant=False)
    
    def visit_AliasDecl(self, node: AliasDecl):
        # Alias mengacu ke variabel lain
        target = self.current_scope.get(node.target)
        # Alias tidak membuat variabel baru, tapi referensi? Atau copy?
        # Di sini kita buat variabel baru dengan nilai yang sama
        self.current_scope.declare(node.alias, target['value'], target['type'], target['address'], constant=False)
    
    def visit_Redecl(self, node: Redecl):
        value = self.visit(node.value)
        var_info = self.current_scope.get(node.name)
        self._check_type(value, var_info['type'])
        self.current_scope.set(node.name, value, var_info['type'], hex(id(value)), constant=var_info['constant'])
    
    def visit_SetObj(self, node: SetObj):
        obj = node.obj
        value = self.visit(node.value)
        
        target_arr = []
        while True:
            if isinstance(obj, GetObj):
                target_arr.append(obj.target)
                obj = obj.obj
            else:
                target_arr.append(obj)
                break
        
        base_name = target_arr[-1]
        target_arr = target_arr[:-1][::-1]
        
        base = self.current_scope.get(base_name)
        base_val = base['value']
        obj = None
        for i, target in enumerate(target_arr):
            if isinstance(target, Node):
                target = self.visit(target)
            
            if i != len(target_arr)-1:
                try:
                    if isinstance(base_val, dict):
                        base_val = base_val[target]
                    else:
                        try:
                            base_val = getattr(base_val, target)
                        except:
                            return None
                except (KeyError, IndexError):
                    base_val = getattr(base_val, target)
                except:
                    return None
                
            else:
                try:
                    if isinstance(base_val, dict):
                        base_val[target] = value
                    else:
                        try:
                            setattr(base_val, target, value)
                        except:
                            return None
                except (KeyError, IndexError):
                    setattr(base_val, target, value)
                except:
                    return None
        
        self.current_scope.vars[base_name] = base
    
    def visit_Function(self, node: Function):
        type_ann = node.type_ann
        name = node.name
        params_func = None
        if node.params and node.params.args:
            params_func = self.visit(node.params)  # Fungsi untuk proses parameter
        
        inner_stmts = node.inner if node.inner else []  # List of statements

        def func_wrapper(*args, **kwargs):
            # Buat scope baru
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
            self._infunction = True
            try:
                # 1. Proses parameter jika ada
                if params_func:
                    param_defs = params_func(*args, **kwargs)
                
                    # 2. Deklarasikan parameter di scope
                    for param_def in param_defs:
                        self.current_scope.declare(
                            param_def['name'],
                            param_def['value'],
                            param_def['type'],
                            param_def['address'],
                            constant=False
                        )
                
                # 3. Eksekusi body function
                result = None
                try:
                    for stmt in inner_stmts:
                        try:
                            self.visit(stmt)
                        except ReturnSignal as e:
                            raise ReturnSignal(e.value)  # Propagate return signal
                        except ThrowSignal as e:
                            raise  # Propagate throw signal
                        except Exception as e:
                            raise ThrowSignal(str(e))
                except ReturnSignal as ret:
                    # Tangkap sinyal return
                    result = ret.value
                    
                except ThrowSignal as thr:
                    # Tangkap sinyal throw, tapi lempar lagi ke atas
                    raise  # Lempar lagi
            
                # 4. Validasi tipe return
                if result is not None:
                    self._check_type(result, type_ann)
                elif type_ann.name != 'kekosongan' and inner_stmts:
                    # Function harus return sesuatu jika ada isi dan bukan void
                    raise TipeGalat(f"Function {name} harus mengembalikan nilai tipe {type_ann.name}")
            
                return result
            
            finally:
                # Kembalikan scope lama
                self.current_scope = old_scope
                self._infunction = False
        
        func_def = Fungsi(func_wrapper)
        func_def.__name__ = name
        
        func_def.__dict__ = {
            'nama': name,
            'isi': func_def,
            'tipe': {
                'kembalikan': type_ann.name
            },
            'lokasi': hex(id(func_def))
        }
        
        func_def.__id__ = id(func_def)
        func_def.__hex__ = hex(id(func_def))
        # Daftarkan function
        self.current_scope.declare(
            func_def.__dict__['nama'], 
            func_def.__dict__['isi'],
            type_ann,
            func_def.__dict__['lokasi'],
            constant=True
        )
        
        return func_def
    
    def visit_Return(self, node: Return):
        """Return statement - mengirim sinyal return"""
        if not self._infunction:
            raise PenulisanGalat(f'Ekspresi \'kembalikan\' berada diluar fungsi. Ekspresi ini harus didalam fungsi')
        value = self.visit(node.expr)
        raise ReturnSignal(value)

    def visit_Throw(self, node: Throw):
        """Throw statement - mengirim sinyal throw"""
        message = self.visit(node.expr)
        classThrow = get_exc(node.name, message)
        raise classThrow
    
    def visit_Decoreted(self, node: Decoreted):
        func_call = node.func_call
        target = node.func_target
        
        self.visit(target)
        func_def = self.current_scope.get(target.name)['value']
        
        func_call.params.args.append(
            CallArgument(
                name=None,
                value=Literal(value=func_def.__dict__)
            )
        )
        
        result_called = self.visit(func_call)
        self.current_scope.vars[target.name]['value'] = result_called
    
    def visit_WriteStmt(self, node: WriteStmt):
        # print(self.current_scope.vars)
        info = self.visit(node.target)
        # Simpan ke output? Atau langsung print?
        # Di sini kita kumpulkan output ke list
        print(str(info), end="")
    
    def visit_ReadStmt(self, node: ReadStmt):
        # Membaca input dari pengguna dan menyimpan ke ekspresi? Ekspresi harus berupa variable?
        # Di grammar, read_stmt: "bacalah" expression -> expression bisa apa saja?
        # Biasanya read digunakan untuk assignment. Mungkin kita perlu menangani kasus tertentu.
        # Sementara kita asumsikan expression adalah variable.
        if isinstance(node.expr, Variable):
            var_name = node.expr.name
            # Baca input
            val = input()
            # Konversi sesuai tipe variabel
            var_info = self.current_scope.get(var_name)
            # Coba konversi
            try:
                converted = self._convert(val, var_info['type'])
            except:
                raise TypeError(f"Input tidak sesuai tipe {var_info['type']}")
            self.current_scope.set(var_name, converted, var_info['type'], hex(id(str(converted))), constant=var_info['constant'])
        else:
            raise PenulisanGalat("bacalah hanya bisa diikuti variabel")
    
    def visit_IfCtrl(self, node: IfCtrl):
        if_stmt = node.if_stmt
        elif_stmt = node.elif_stmt or []
        else_stmt = node.else_stmt
    
        # Cek if
        if self.visit(if_stmt):
            return
        
        # Cek elif
        for stmt in elif_stmt:
            if self.visit(stmt):
                return
            
        # Cek else
        if else_stmt:
            self.visit(else_stmt)
    
    def visit_IfStmt(self, node: IfStmt):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.body)
            
        return True if cond else False
        
    def visit_ElifStmt(self, node: ElifStmt):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.body)
        return cond
        
    def visit_ElseStmt(self, node: ElseStmt):
        self.visit(node.body)
    
    def visit_WhileStmt(self, node: WhileStmt):
        self._isloop = True
        
        while self.visit(node.condition):
            try:
                self.visit(node.body)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
            except (ReturnSignal, ThrowSignal) as e:
                # Propagate return/throw dari dalam loop
                raise e
            finally:
                self._isloop = False
    
    def visit_ForStmt(self, node: ForStmt):
        self._isloop = True
        expr = self.visit(node.expr)  # expr adalah instance IterHelper
        body = node.body
    
        # Validasi
        if not hasattr(expr, 'name') or not hasattr(expr, 'get'):
            raise EkspresiGalat("Ekspresi for tidak valid")
    
        # Eksekusi loop
        while expr.index < expr.max:
            value = expr.get()
            if value is None:
                break
            
            # Update variabel loop
            self.current_scope.set(
                expr.name,
                value,
                BasicType('apapun'),
                hex(id(value)),
                constant=False
            )
            
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
            raise TipeGalat(f'Tipe {type(target).__name__!r} tidak mendukung operasi iterasi')
    
        # Buat instance, bukan class
        class IterHelper:
            def __init__(self, name, target):
                self.name = name
                self.target = [self._visit_item(tg) for tg in target]  # Perlu method visit
                self.index = 0
                self.max = len(target)
        
            def _visit_item(self, item):
                # Jika item adalah AST node, visit dulu
                if hasattr(item, '__dict__') and hasattr(self, 'interpreter'):
                    return self.interpreter.visit(item)
                return item
        
            def get(self):
                if self.index < self.max:
                    result = self.target[self.index]
                    self.index += 1
                    return result
                return None
    
        # Buat instance dengan interpreter reference
        helper = IterHelper(name, target)
        helper.interpreter = self  # Beri akses ke interpreter untuk visit
        return helper
    
    def visit_TryCtrl(self, node: TryCtrl):
        try_stmt = node.try_stmt
        catch_stmt = node.catch_stmt
        finally_stmt = node.finally_stmt  # Perhatikan nama attribute
    
        # Eksekusi try block
        try_result = self.visit(try_stmt)()  # Panggil function
    
        # Jika try sukses
        if try_result['success']:
            # Langsung ke finally jika ada
            if finally_stmt:
                self.visit(finally_stmt)()
            return
    
        # Jika try gagal (throw)
        if not try_result['success']:
            # Eksekusi catch block
            if catch_stmt:
                # Catch block mungkin melempar lagi
                try:
                    self.visit(catch_stmt)(try_result['data'])
                except ThrowSignal as e:
                    # Catch melempar, lanjutkan ke finally lalu lempar lagi
                    if finally_stmt:
                        self.visit(finally_stmt)()
                    raise e
            else:
                # Tidak ada catch, lempar lagi
                if finally_stmt:
                    self.visit(finally_stmt)()
                # Buat ThrowSignal dari data
                data = try_result['data']
                raise ThrowSignal(data['name'], data['message'])
    
    # Finally selalu dijalankan (sudah di handle di atas)
    
    def visit_TryStmt(self, node: TryStmt):
        body = node.body
        
        def app():
            try:
                self.visit(body)
                return {
                    'success': True,
                    'data': {}
                }
            except ThrowSignal as e:
                return {
                    'success': False,
                    'data': {
                        'message': e.message
                    }
                }
        
        return app
    
    def visit_CatchStmt(self, node: CatchStmt):
        name = node.name
        body = node.body
    
        def app(data: dict):
            # Buat scope baru untuk catch block
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
        
            try:
                # Deklarasi variabel exception
                self.current_scope.declare(
                    name,
                    data['message'],
                    BasicType('teks'),
                    hex(id(data['message'])),
                    constant=False
                )
            
                # Eksekusi body catch
                self.visit(body)
            
            except ReturnSignal as ret:
                # Return dalam catch, propagasi
                raise ret
            
            except ThrowSignal as thr:
                # Throw dalam catch, propagasi
                raise thr
            
            finally:
                # Kembalikan scope
                self.current_scope = old_scope
    
        return app
        
    def visit_FinallyStmt(self, node: FinallyStmt):  # Konsisten nama
        body = node.body
    
        def app():
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
        
            try:
                self.visit(body)
            finally:
                self.current_scope = old_scope
    
        return app
    
    def visit_SwitchStmt(self, node: SwitchStmt):
        expr = self.visit(node.expr)
        case_func = [self.visit(stmt) for stmt in node.body if stmt is not None]
        
        self._isloop = True
        for func in case_func:
            try:
                func(expr)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
            except (ReturnSignal, ThrowSignal) as e:
                raise e
            finally:
                self._isloop = False
        
    def visit_CaseStmt(self, node: CaseStmt):
        if len(node.expr) == 1 and node.expr[0] == '_':
            def wrapper(expr):
                for stmt in node.body:
                    try:
                        self.visit(stmt)
                    except (ReturnSignal, ThrowSignal, BreakSignal, ContinueSignal) as e:
                        raise e
                return True
            
            return wrapper
            
        exprs = [self.visit(expr) for expr in node.expr if expr is not None]
        
        def wrapper(expr):
            if expr in exprs:
                for stmt in node.body:
                    try:
                        self.visit(stmt)
                    except (ReturnSignal, ThrowSignal, BreakSignal, ContinueSignal) as e:
                        raise e
                    
                return True
                
            return False
        
        return wrapper
    
    def visit_Block(self, node: Block):
        # Masuk scope baru
        old_scope = self.current_scope
        self.current_scope = Scope(parent=old_scope)
        for stmt in node.statements:
            self.visit(stmt)
        self.current_scope = old_scope
    
    # --- Module ---
    def visit_Export(self, node: Export):
        exports = [self.visit(arg) for arg in node.exports if arg is not None]
        
        for i, export in enumerate(exports):
            self._module['ekspor'].update(export)
    
    def visit_ExportArgument(self, node: ExportArgument):
        name = node.name
        alias = node.alias
        
        obj = None
        try:
            obj = self.current_scope.get(name)
        except VariabelGalat as e:
            raise EksporGalat(e.message)
        
        if alias:
            name = alias
        
        return {name: obj}
    
    def visit_Import(self, node: Import):
        imports = node.imports  # List of ImportArgument
        path_str = self.visit(node.from_path)  # String path
    
        # Load module
        module_interp, module_exports = self._load_module(path_str)
    
        # Proses setiap import
        for imp in imports:
            name = imp.name
            alias = imp.alias or name
        
            if name not in module_exports:
                raise ImporGalat(f"'{name}' tidak ditemukan di module {path_str}")
        
            obj = module_exports[name]
        
            # Deklarasikan di scope saat ini
            self.current_scope.declare(
                alias,
                obj['value'],
                obj['type'],
                obj['address'],
                obj['constant']
            )
    
    def visit_ImportArgument(self, node: ImportArgument):
        return [node.name, node.alias]
    
    def visit_PathID(self, node: PathID):
        args = [self.visit(arg) for arg in node.path if arg is not None]
        
        path = Path()
        for arg in args:
            path /= arg
        
        return str(path)
    
    def visit_PathArg(self, node: PathArg):
        return Path(node.arg)
    
    # --- Expressions ---
    def visit_BinaryOp(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        
        # Operasi aritmatika
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '%':
            return left % right
        elif op == '**':
            return left ** right
        elif op == '//':
            return left // right
        # Perbandingan
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '>=':
            return left >= right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '<':
            return left < right
        elif op == 'dan':
            return left and right
        elif op == 'atau':
            return left or right
        elif op == 'dalam':
            return left in right
        elif op == 'tidak dalam':
            return left not in right
        else:
            raise IsiGalat(f"Operator {op} tidak dikenal")
    
    def visit_UnaryOp(self, node: UnaryOp):
        val = self.visit(node.expr)
        if node.op == 'tidak':
            return not val
        else:
            raise IsiGalat(f"Unary operator {node.op} tidak dikenal")
    
    def visit_Literal(self, node: Literal):
        value = node.value
        if isinstance(value, Node):
            value = self.visit(value)
        
        return value
    
    def visit_Array(self, node: Array):
        values = node.values
        
        arr = []
        for val in values:
            if isinstance(val, Unpacking):
                arr.extend(self.visit(val.value))
            elif isinstance(val, Node):
                arr.append(self.visit(val))
            else:
                arr.append(val)
        
        return arr
    
    def visit_Dictionary(self, node: Dictionary):
        keys = node.keys
        values = node.values
        
        if len(keys) != len(values):
            raise AtributGalat(f"Mengapa panjang dari kunci dan isi tidak sama?")
        
        idx = 0
        obj = {}
        while len(keys) == len(values) and idx < len(keys):
            key = keys[idx]
            val = values[idx]
            idx += 1
            
            if isinstance(val, Node) and key is None:
                sbj = self.visit(val)
                obj.update(sbj)
                continue
            
            if isinstance(val, Node) and key:
                sbj = self.visit(val)
                obj[key] = sbj
                continue
            
            if isinstance(key, Node):
                key = self.visit(key)
            
            if isinstance(val, Node):
                val = self.visit(val)
            
            if (not isinstance(key, Node) and key) and (not isinstance(val, Node) and val):
                obj[key] = val
            
        return obj
    
    def visit_Variable(self, node: Variable):
        name = node.name
        default_value = node.value
        
        if not self.current_scope.has(name) and default_value:
            return default_value
        
        var_info = self.current_scope.get(node.name)
        return var_info['value']
    
    def visit_GetObj(self, node: GetObj):
        obj = self.visit(node.obj)
        target = node.target
        
        if isinstance(target, Node):
            target = self.visit(target)
        
        try:
            return obj[target]
        except (KeyError, IndexError):
            return getattr(obj, node.target)
            # raise IndeksGalat(f'Tidak ada indeks {str(idx)!r} pada {str(obj)!r}')
        except:
            return None
            # raise AtributGalat(f'Tidak ada atribut {str(node.attr)!r} pada {str(obj)!r}')
    
    def visit_Crement(self, node: Crement):
        if not isinstance(node.obj, Variable):
            raise VariabelGalat('Peningkatan harus berupa variabel, bukan non-variabel')
        
        obj_name = node.obj.name
        obj = self.current_scope.get(obj_name)
        
        if (not isinstance(obj['value'], int)) or obj['type'].name != 'angka':
            raise TipeGalat('Peningkatan pada isi dari variabel harus berupa angka')
        
        if node.negated:
            obj['value'] -= 1
        else:
            obj['value'] += 1
            
        self.current_scope.set(
            obj_name,
            obj['value'],
            obj['type'],
            hex(id(obj['value'])),
            obj['constant']
        )
    
    def visit_CallFunc(self, node: CallFunc):
        func = self.visit(node.func)
        
        # Handle params
        args = []
        kwargs = {}
        
        if node.params:
            params_result = self.visit(node.params)
            if params_result:
                args = params_result.get('args', [])
                kwargs = params_result.get('kwargs', {})
        
        # Debugging
        # print(f"Memanggil {func} dengan args={args}, kwargs={kwargs}")

        try:
            # Panggil fungsi dengan args dan kwargs
            if args or kwargs:
                result = func(*args, **kwargs)
            else:
                # Fungsi tanpa argumen
                result = func()
            return result
        except TypeError as e:
            # Beri pesan error yang lebih jelas
            if "missing" in str(e):
                raise TipeGalat(f"Parameter fungsi tidak lengkap: {str(e)}")
            if "takes 0 positional arguments" in str(e):
                # Fungsi tidak menerima argumen tapi diberikan argumen
                if args or kwargs:
                    raise TipeGalat(f"Fungsi tidak menerima argumen")
            raise
        
    def visit_CallParameter(self, node: CallParameter):
        if not node.args:
            return {
                'args': [],
                'kwargs': {}
            }
        
        args = [self.visit(arg) for arg in node.args]
        bef1, bef2 = 'args', 'args'

        Args = []
        Kwargs = {}

        for i, arg in enumerate(args):
            if arg['name']:
                if bef2 == 'args': 
                    bef1, bef2 = bef2, 'keyword'
                Kwargs[arg['name']] = arg['value']
            else:
                if bef2 == 'keyword':
                    raise TypeError("Positional argument setelah keyword argument tidak diperbolehkan")
                Args.append(arg['value'])

        return {
            'args': Args,
            'kwargs': Kwargs
        }
        
    def visit_CallArgument(self, node: CallArgument):
        name = node.name
        value = self.visit(node.value)
        
        if name:
            name = str(name)
        
        return {
            'name': name,
            'value': value,
        }
    
    def visit_LambdaFunc(self, node: LambdaFunc):
        # Dapatkan function pembuat parameter
        param_func = self.visit(node.params)  # returns app(params) function
        expr = node.expr
    
        def lambda_wrapper(*args, **kwargs):
            """Wrapper yang akan dipanggil saat lambda dieksekusi"""
            # Buat scope baru
            old_scope = self.current_scope
            self.current_scope = Scope(parent=old_scope)
        
            try:
                # Buat parameter definitions
                param_defs = param_func(*args, **kwargs)  # panggil dengan args
            
                # Deklarasikan parameter di scope baru
                for param_def in param_defs:
                    self.current_scope.declare(
                        param_def['name'],
                        param_def['value'],
                        param_def['type'],
                        param_def['address'],
                        constant=param_def.get('constant', False)
                    )
            
                # Eksekusi body lambda
                result = self.visit(expr)
            
                return result
            
            finally:
                # Kembalikan scope lama
                self.current_scope = old_scope
        
        func_def = Lambda(lambda_wrapper)
        
        return func_def
    
    # Perbaiki visit_TypeOf
    def visit_TypeOf(self, node: TypeOf):
        var_name = node.var.name
        obj = self.current_scope.get(var_name)
        
        # Kembalikan nama tipe sebagai string
        if isinstance(obj['type'], BasicType):
            return obj['type'].name
        else:
            return str(obj['type'])
    
    def visit_GetAddr(self, node: GetAddr):
        var = node.var
        negated = node.negated
        if negated:
            addr = self.current_scope.get(var)['value']
            return self.current_scope.get(addr, 'address')
        else:
            return self.current_scope.get(var)['address']
    
    def visit_IsStmt(self, node: IsStmt):
        left_info = self.current_scope.get(node.left)
        right_info = self.current_scope.get(node.right)
        # Bandingkan berdasarkan identitas? Atau nilai dan tipe?
        # Di sini kita bandingkan objeknya (memory) dan nilai
        same = (left_info is right_info) or (left_info['value'] == right_info['value'] and left_info['type'] == right_info['type'] and left_info['address'] == right_info['address'])
        if node.negated:
            return not same
        return same
    
    def visit_Looping(self, node: Looping):
        if not self._isloop:
            raise PenulisanGalat(f'Ekspresi {'lanjutkan' if node.is_continue else 'berhentikan'} harus berada pada perulangan')
            
        if node.is_continue:
            raise ContinueSignal()
        raise BreakSignal()
    
    def visit_Parameter(self, node: Parameter):
        if not node.args:
            # Fungsi tanpa parameter
            def app(*args, **kwargs):
                return []
            return app
        
        arg_functions = [self.visit(arg) for arg in node.args]

        def app(*args, **kwargs):
            # Map positional args ke parameter
            result_def = []

            # 1. Proses positional args
            for i, arg_func in enumerate(arg_functions):
                if i < len(args):
                    # Pakai positional arg
                    result_def.append(arg_func(args[i]))
                else:
                    # Belum diisi, cek kwargs nanti
                    result_def.append(None)

            # 2. Proses keyword args
            for i, arg_def in enumerate(result_def):
                if arg_def is None:
                    # Cari di kwargs berdasarkan nama parameter
                    param_name = arg_functions[i].param_name
                    if param_name in kwargs:
                        # Pakai dari kwargs
                        val = kwargs[param_name]
                        result_def[i] = arg_functions[i](val)
                    else:
                        # Pakai default value jika ada
                        try:
                            result_def[i] = arg_functions[i]()  # Akan raise error jika tidak ada default
                        except IsiGalat:
                            # Beri pesan error yang jelas
                            raise IsiGalat(f'Argumen {param_name!r} wajib diisi (tidak memiliki nilai default)')

            return result_def

        return app

    def visit_Argument(self, node: Argument):
        type_ann = node.type_ann
        name = node.name
        default_value = self.visit(node.value) if node.value else None

        def app(val=None):
            if val is None:
                if default_value is not None:
                    val = default_value
                else:
                    # Beri pesan error yang jelas
                    raise IsiGalat(f'Argumen {name!r} wajib diisi (tidak memiliki nilai default)')
    
            # Validasi tipe (opsional, bisa diaktifkan nanti)
            # self._check_type(val, type_ann)
    
            return {
                'name': name,
                'type': type_ann,
                'value': val,
                'address': hex(id(val)),
                'constant': False
            }

        # Simpan nama parameter untuk referensi di visit_Parameter
        app.param_name = name

        return app
    
    def visit_BasicType(self, node: BasicType):
        return node.name
    
    # --- Helpers ---
    def _check_type(self, value, type_ann):
        if isinstance(type_ann, BasicType):
            expected = TYPES.get(type_ann.name)
            if expected == callable:
                if not callable(value):
                    raise TipeGalat(f"Nilai {value} tidak sesuai tipe {type_ann.name}")
            else:
                if expected and not isinstance(value, expected):
                    raise TipeGalat(f"Nilai {value} tidak sesuai tipe {type_ann.name}")
        # Untuk array type dll, perlu penanganan lebih lanjut
        # ...
    
    def _default_value(self, type_ann):
        if isinstance(type_ann, BasicType):
            if type_ann.name == 'teks':
                return ""
            elif type_ann.name == 'angka':
                return 0
            elif type_ann.name == 'desimal':
                return 0.0
            elif type_ann.name == 'boolean':
                return False
            elif type_ann.name == 'kekosongan':
                return None
            elif type_ann.name == 'daftar':
                return []
            elif type_ann.name == 'kamus':
                return {}
            elif type_ann.name == 'panggilan':
                return lambda: None
        return None
    
    def _convert(self, s, type_ann):
        if isinstance(type_ann, BasicType):
            if type_ann.name == 'teks':
                return s
            elif type_ann.name == 'angka':
                return int(s)
            elif type_ann.name == 'desimal':
                return float(s)
            elif type_ann.name == 'boolean':
                return s.lower() == 'benar'
        return s
    
    def _load_module(self, path_str: str) -> tuple:
        """
        Memuat module dari path string
        Returns: (interpreter, exports)
        - interpreter: instance Interpreter dari module
        - exports: dictionary exports dari module
        """
        from ..main import IndonesianScriptInterpreter  # Import di dalam fungsi untuk hindari circular

        # 1. Parse path string
        path = Path(self._filename).parent / path_str

        # 2. Cek apakah sudah pernah di-load (cache)
        path_key = str(path)
        if path_key in self._module['impor']:
            return self._module['impor'][path_key]

        # 3. Validasi path
        if not path.exists():
            raise JalurGalat(f"Jalur modul '{path_str}' tidak ditemukan")

        # 4. Jika direktori, cari file inisiasi.is
        if path.is_dir():
            if str(path) == 'builtins':
                path = Path(__file__).parent / 'Builtins' / 'Built-ins'
            init_file = path / 'inisiasi.is'
            if not init_file.exists():
                raise PaketGalat(f"Paket '{path.name}' tidak memiliki file inisiasi.is")
            path = init_file
    
        # 5. Jika file .py, load sebagai modul Python
        if path.is_file() and path.suffix == '.py':
            from importlib.util import spec_from_file_location
            import sys
        
            try:
                # Load module Python
                module_name = path.stem
                spec = spec_from_file_location(module_name, str(path))
                module = spec.loader.load_module()
            
                # Cari decorator Modul di module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # Cek apakah ini instance dari class Modul
                    if hasattr(attr, '_get_interp'):
                        interp = attr._get_interp()
                        cache_entry = (interp, interp._module['ekspor'])
                        self._module['impor'][path_key] = cache_entry
                        return cache_entry
                
                return (None, None)
                
            except Exception as e:
                raise ImporGalat(f"Gagal memuat modul Python: {str(e)}")

        # 6. Baca dan load file .is
        try:
            code = path.read_text(encoding='utf-8')
    
            # Buat interpreter untuk module
            module_interp = IndonesianScriptInterpreter(
                filename=str(path),
                code=code,
                ismodule=True
            )
    
            # Jalankan module (tanpa console output)
            result, interpreter = module_interp.run(
                console=False,
                get_interpreter=True
            )
    
            # Simpan ke cache
            cache_entry = (interpreter, interpreter._module['ekspor'])
            self._module['impor'][path_key] = cache_entry
    
            return cache_entry
    
        except (VariabelGalat, FinalGalat) as e:
            raise ImporGalat(e.message)
        except Exception as e:
            raise ImporGalat(f"Gagal memuat modul: {str(e)}")