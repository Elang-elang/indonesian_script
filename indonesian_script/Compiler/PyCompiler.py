# PyCompiler.py
"""
Compiler Indonesian Script → Python
Mengubah AST Indonesian Script menjadi kode Python yang valid
Mengimplementasikan StructCompiler dengan manajemen scope dan pengumpulan kode.
"""

from .structure import StructCompiler, Utils
from ..Interpreter.Exceptions.exceptions import PenulisanGalat, TipeGalat
from ..Interpreter.Builtins.builtins import TYPES
import textwrap
import types
import typing as T
import inspect

class Scope:
    """
    Manajemen scope untuk kompilasi.
    Menyimpan informasi variabel: nama, tipe, nilai (jika konstanta), dan kode deklarasi.
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}  # name -> {'type': type_obj, 'constant': bool, 'code': str, 'value': any}
    
    def declare(self, name, value, type_ann, code, constant=False):
        if name in self.vars:
            raise PenulisanGalat(f"Variabel '{name}' sudah dideklarasikan di scope ini")
        
        # Validasi tipe (jika value diberikan)
        if value is not None and not Utils.check_type(value, type_ann):
            raise TipeGalat(f"Variabel '{name}' tidak sesuai tipe {type_ann.name if hasattr(type_ann, 'name') else type_ann}")
        
        self.vars[name] = {
            'type': type_ann,
            'value': value,
            'code': code,
            'constant': constant
        }
    
    def set(self, name, value, code):
        # Cari di scope ini atau parent
        if name in self.vars:
            if self.vars[name]['constant']:
                raise PenulisanGalat(f"Variabel '{name}' bersifat final, tidak dapat diubah")
            # Validasi tipe
            if not Utils.check_type(value, self.vars[name]['type']):
                raise TipeGalat(f"Variabel '{name}' tidak sesuai tipe")
            self.vars[name]['value'] = value
            self.vars[name]['code'] = code  # simpan kode assignment terbaru (opsional)
            return
        elif self.parent:
            self.parent.set(name, value, code)
            return
        else:
            raise PenulisanGalat(f"Variabel '{name}' belum dideklarasikan")
    
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise PenulisanGalat(f"Variabel '{name}' belum dideklarasikan")
    
    def has(self, name):
        return name in self.vars or (self.parent and self.parent.has(name))


class Compiler(StructCompiler):
    """
    Compiler Indonesian Script → Python.
    Mengumpulkan kode Python dalam `current_lines` dan menggunakan `current_scope` untuk manajemen variabel.
    """
    
    def __init__(self, filename='<stdout>'):
        self.filename = filename
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_lines = []          # Baris kode Python yang dihasilkan
        self.indent_level = 0            # Level indentasi saat ini
        self.imports = set()              # Kumpulan import yang diperlukan
        self.functions = []                # Kode fungsi yang sudah jadi (untuk diletakkan di global)
        self.classes = []                  # Kode class (jika ada)
        self._infunction = False
        self._build_init_()
    
    def _build_init_(self):
        self.imports.add("import typing as T")
        self.imports.add("import types as t")
        
        code = [
            "def tampilkan(*args, **kwargs) -> None:",
            "    print(*args, **kwargs)",
            "    return None"
        ]
        
        code_txt = '\n'.join(code)
        self.current_scope.declare(
            "tampilkan",
            exec(code_txt),
            T.Callable[
                [
                    T.Tuple[T.Any],
                    T.Dict[str, T.Any]
                ],
                types.NoneType
            ],
            code_txt,
            True
        )
        
        code = [
            "def format(text: str, /, **kwargs) -> str:",
            "    return text.format(**kwargs)",
        ]
        code_txt = '\n'.join(code)
        self.current_scope.declare(
            "format",
            exec(code_txt),
            T.Callable[
                [
                    str,
                    T.Dict[str, T.Any]
                ],
                str
            ],
            code_txt,
            True
        )
        
    
    def _indent(self):
        """Mengembalikan string indentasi sesuai level"""
        return "    " * self.indent_level
    
    def _add_line(self, line):
        """Menambahkan baris kode dengan indentasi yang sesuai"""
        if line.strip():  # hanya tambahkan jika tidak kosong
            self.current_lines.append(self._indent() + line)
    
    def _add_to_global(self, code):
        """Menambahkan kode ke bagian global (seperti deklarasi variabel global)"""
        # Untuk saat ini, kita simpan di current_lines dengan asumsi sudah di global scope
        # Tapi nanti bisa dipisah jika perlu
        self.current_lines.append(code)
    
    # ==================== PROGRAM & BLOCKS ====================
    
    def compile_Program(self, node: Utils.ASTNodes.Program):
        """Program utama: kompilasi semua statement"""
        if node.statements:
            for stmt in node.statements:
                self.compile(stmt)
        # Kumpulkan semua kode
        return "\n".join([line for line in self.current_lines if line is not None])
    
    def compile_Block(self, node: Utils.ASTNodes.Block):
        """Blok kode: masuk scope baru, kompilasi statement, keluar scope"""
        # Buat scope baru
        old_scope = self.current_scope
        old_lines = current_lines
        self.current_scope = Scope(parent=old_scope)
        self.current_lines = []
        self.indent_level += 1
        
        for stmt in node.statements or []:
            self.compile(stmt)
        
        self.indent_level -= 1
        self.current_scope = old_scope
        self.current_lines = old_lines
    
    # ==================== STATEMENTS ====================
    
    # --- Variable Declarations ---
    def compile_VarDecl(self, node: Utils.ASTNodes.VarDecl):
        """teks nama = nilai → nama: tipe = nilai"""
        name = node.name
        value = self.compile(node.value) if node.value else None
        type_ann = node.type_ann
        py_type = Utils.get_py_type(type_ann)  # Misal: str, int, dll.
        
        # Nilai default jika tidak ada
        if value is None:
            value = self._default_value(py_type)
        
        # Format kode Python
        if py_type is not None:
            code = f"{name}: {py_type.__name__} = {value}"
        else:
            code = f"{name} = {value}"
        
        self._add_line(code)
        self.current_scope.declare(name, value, type_ann, code, constant=False)
    
    def compile_FinalDecl(self, node: Utils.ASTNodes.FinalDecl):
        """final teks nama = nilai → nama: tipe = nilai (tidak ada konstanta khusus di Python, bisa gunakan UPPER_CASE)"""
        name = node.name.upper()  # konvensi konstanta
        value = self.compile(node.value)
        type_ann = node.type_ann
        py_type = Utils.get_py_type(type_ann)
        
        if py_type is not None:
            code = f"{name}: {py_type.__name__} = {value}"
        else:
            code = f"{name} = {value}"
        
        self._add_line(code)
        self.current_scope.declare(name, value, type_ann, code, constant=True)
    
    def compile_DefDecl(self, node: Utils.ASTNodes.DefDecl):
        """teks nama → nama: tipe = default_value"""
        name = node.name
        type_ann = node.type_ann
        py_type = Utils.get_py_type(type_ann)
        default = self._default_value(py_type)
        
        if py_type is not None:
            code = f"{name}: {py_type.__name__} = {default}"
        else:
            code = f"{name} = {default}"
        
        self._add_line(code)
        self.current_scope.declare(name, default, type_ann, code, constant=False)
    
    def compile_AliasDecl(self, node: Utils.ASTNodes.AliasDecl):
        """alias nama2 = nama → nama2 = nama"""
        # Cari variabel target
        target_info = self.current_scope.get(node.target)
        code = f"{node.alias} = {node.target}"
        self._add_line(code)
        # Alias hanya referensi, tidak perlu validasi tipe ulang? Kita copy saja.
        self.current_scope.declare(node.alias, target_info['value'], target_info['type'], code, constant=target_info['constant'])
    
    def compile_Redecl(self, node: Utils.ASTNodes.Redecl):
        """nama = nilai → assignment"""
        name = node.name
        value = self.compile(node.value)
        var_info = self.current_scope.get(name)
        py_type = Utils.get_py_type(var_info['type'])
        
        # Validasi tipe (opsional, bisa dilakukan di scope.set)
        code = f"{name} = {repr(value)}"
        self._add_line(code)
        self.current_scope.set(name, value, code)
    
    # --- Pointer ---
    
    # --- CLI I/O ---
    def compile_WriteStmt(self, node: Utils.ASTNodes.WriteStmt):
        """tuliskan expr → print(expr, end='')"""
        expr = self.compile(node.target)
        self._add_line(f"print({expr}, end='')")
    
    def compile_ReadStmt(self, node: Utils.ASTNodes.ReadStmt):
        """bacalah nama → nama = input()"""
        if isinstance(node.expr, Utils.ASTNodes.Variable):
            var_name = node.expr.name
            self._add_line(f"{var_name} = input()")
            # Nilai input adalah string, perlu konversi? Biarkan pengguna yang handle.
        else:
            raise PenulisanGalat("bacalah hanya bisa diikuti variabel")
    
    # ==================== CONTROL FLOW ====================
    
    # --- If ---
    def compile_IfCtrl(self, node: Utils.ASTNodes.IfCtrl):
        """if ... elif ... else ..."""
        self.compile(node.if_stmt)
        for elif_stmt in node.elif_stmt or []:
            self.compile(elif_stmt)
        if node.else_stmt:
            self.compile(node.else_stmt)
    
    def compile_IfStmt(self, node: Utils.ASTNodes.IfStmt):
        cond = self.compile(node.condition)
        self._add_line(f"if {cond}:")
        self.compile(node.body)
    
    def compile_ElifStmt(self, node: Utils.ASTNodes.ElifStmt):
        cond = self.compile(node.condition)
        self._add_line(f"elif {cond}:")
        self.compile(node.body)
    
    def compile_ElseStmt(self, node: Utils.ASTNodes.ElseStmt):
        self._add_line(f"else:")
        self.compile(node.body)
    
    # --- While ---
    def compile_WhileStmt(self, node: Utils.ASTNodes.WhileStmt):
        cond = self.compile(node.condition)
        self._add_line(f"while {cond}:")
        self.compile(node.body)
    
    # --- For ---
    def compile_ForStmt(self, node: Utils.ASTNodes.ForStmt):
        # Untuk sementara, kita asumsikan ForExpr berisi nama dan target list
        # Nanti bisa dikembangkan untuk range
        expr = node.expr
        target = self.compile(expr.target)
        self._add_line(f"for {expr.name} in {target}:")
        self.compile(node.body)
    
    def compile_ForExpr(self, node: Utils.ASTNodes.ForExpr):
        # Ekspresi for itu sendiri tidak menghasilkan kode, hanya digunakan oleh ForStmt
        # Kita kembalikan representasi target
        # Tapi method ini dipanggil oleh compile(node.expr) di ForStmt, jadi harus mengembalikan string
        return self.compile(node.target)  # target adalah List[Any] (sudah dikompilasi jadi list literal)
    
    # --- Try ---
    def compile_TryCtrl(self, node: Utils.ASTNodes.TryCtrl):
        self.compile(node.try_stmt)
        self.compile(node.catch_stmt)
        if node.finally_stmt:
            self.compile(node.finally_stmt)
    
    def compile_TryStmt(self, node: Utils.ASTNodes.TryStmt):
        self._add_line(f"try:")
        self.compile(node.body)
    
    def compile_CatchStmt(self, node: Utils.ASTNodes.CatchStmt):
        self._add_line(f"except Exception as {node.name}:")
        self.compile(node.body)
    
    def compile_FinallyStmt(self, node: Utils.ASTNodes.FinallyStmt):
        self._add_line(f"finally:")
        self.compile(node.body)
    
    # ==================== EXPRESSIONS ====================
    
    def compile_BinaryOp(self, node: Utils.ASTNodes.BinaryOp):
        print(node)
        left = self.compile(node.left)
        right = self.compile(node.right)
        op = self._py_operator(node.op)
        return f"({left} {op} {right})"
    
    def compile_UnaryOp(self, node: Utils.ASTNodes.UnaryOp):
        expr = self.compile(node.expr)
        if node.op == 'tidak':
            return f"(not {expr})"
        return f"({node.op}{expr})"
    
    def compile_Literal(self, node: Utils.ASTNodes.Literal):
        # Untuk list/dict, sudah direpresentasikan sebagai Literal dengan value list/dict
        return repr(node.value)
    
    def compile_Variable(self, node: Utils.ASTNodes.Variable):
        # Variabel bisa punya default value jika tidak ada di scope? Di interpreter ada fitur itu, tapi di kompilasi kita anggap sudah dideklarasikan.
        print(node)
        if self.current_scope.has(node.name):
            obj = self.current_scope.get(node.name)
            if obj['type'] is types.FunctionType:
                return obj['name']
            return obj['value']
        else:
            return node.name
    
    def compile_GetObj(self, node: Utils.ASTNodes.GetObj):
        obj = self.compile(node.obj)
        if isinstance(obj, dict):
            return f"{obj}[{self.compile(node.target)}]"
        return f"{obj}.{node.target}"
    
    def compile_CallFunc(self, node: Utils.ASTNodes.CallFunc):
        func = self.compile(node.func)
        params = self.compile(node.params)  # params sudah berupa string argumen
        return f"{func}{params}"
    
    def compile_CallParameter(self, node: Utils.ASTNodes.CallParameter):
        # node.args adalah list of CallArgument
        args = []
        for arg in node.args or []:
            arg_str = self.compile(arg)
            args.append(arg_str)
        return f"({', '.join(args)})"
    
    def compile_CallArgument(self, node: Utils.ASTNodes.CallArgument):
        # Bisa positional (name None) atau keyword (name string)
        value = self.compile(node.value)
        if node.name:
            return f"{node.name}={value}"
        else:
            return value
    
    def compile_LambdaFunc(self, node: Utils.ASTNodes.LambdaFunc):
        params = self.compile(node.params)  # misal: "x, y"
        expr = self.compile(node.expr)
        return f"lambda {params}: {expr}"
    
    def compile_TypeOf(self, node: Utils.ASTNodes.TypeOf):
        return f"type({node.var.name}).__name__"
    
    def compile_IsStmt(self, node: Utils.ASTNodes.IsStmt):
        left = node.left
        right = node.right
        if node.negated:
            return f"({left} is not {right})"
        else:
            return f"({left} is {right})"
    
    # ==================== FUNCTIONS ====================
    
    def compile_Function(self, node: Utils.ASTNodes.Function):
        """Deklarasi fungsi"""
        # Simpan state saat ini
        old_lines = self.current_lines
        old_scope = self.current_scope
        old_indent = self.indent_level
        
        # Buat scope baru untuk fungsi
        self.current_scope = Scope(parent=self.global_scope)  # fungsi bisa akses global
        self.indent_level = 0
        self.current_lines = []  # kumpulkan kode fungsi di sini
        # Parameter
        params_str = self.compile(node.params) if node.params else ""
        return_type = Utils.get_py_type(node.type_ann)
        return_annotation = f" -> {return_type.__name__}" if return_type and return_type is not None else ""
        
        # Header fungsi
        self._add_line(f"def {node.name}({params_str}){return_annotation}:")
        self.indent_level += 1
        
        # Body
        for stmt in node.inner or []:
            self.compile(stmt)
        
        # Kumpulkan kode fungsi
        func_code = self.current_lines.copy()
        
        # Kembalikan state
        self.current_lines = old_lines
        self.current_scope = old_scope
        self.indent_level = old_indent
        
        self.current_lines.extend([self._add_line(code) for code in func_code])
        
        # Simpan fungsi ke daftar (nanti ditaruh di global)
        # Untuk sementara, kita tambahkan ke current_lines dengan indentasi 0
        func_code_txt = '\n'.join(func_code)
        exec(func_code_txt)
        print(kali)
        func = eval(node.name)
        print(func_code)
        print(func_code_txt)
        print(func)
        func_type = inspect.signature(func)
        params_type = []
        
        for param in func_type.parameters.values():
            if param.annotation is inspect._empty:
                params_type.append(T.Any)
            
            params_type.append(param.annotation)
        
        func_code_txt = '\n'.join(func_code)
        return_type = func_type.return_annotation if func_type.return_annotation is not inspect._empty else T.Any
        
        print(T.Callable[func_params_type, return_type])
        
        self.current_scope.declare(
            node.name,
            func,
            T.Callable[func_params_type, return_type],
            func_code_txt,
            True
        )
    
    def compile_Parameter(self, node: Utils.ASTNodes.Parameter):
        """Parameter fungsi: kumpulan Argument"""
        arg_func = node.args
        params = []
        for arg in arg_func.code or []:
            params.append(self.compile(arg))
        code = ", ".join(params)
        
        def wrapper_parans(*args, **kwargs):
            pass
        
        return code
    
    def compile_Argument(self, node: Utils.ASTNodes.Argument):
        """Argumen formal: nama: tipe = default"""
        name = node.name
        type_ann = node.type_ann
        py_type = Utils.get_py_type(type_ann)
        type_hint = f": {py_type.__name__}" if py_type else ""
        code = None
        if node.value:
            default = self.compile(node.value)
            code = f"{name}{type_hint}={default}"
        else:
            default = None
            code = f"{name}{type_hint}"
            py_type = T.Optional[py_type]
        
        def wrapper_arg(value: py_type = default) -> py_type:
            if value:
                if Utils.check_type(value, py_type):
                    self.current_scope.declare(
                        name,
                        value,
                        py_type,
                        code,
                        False
                    )
                    return value
            raise TypeError(f"Isi dari argumen {name!r} tidak sesuai dengan tipenya")
        
        wrapper_arg.__name__ = name
        wrapper_arg.code = code
        
        return wrapper_arg
    
    def compile_Return(self, node: Utils.ASTNodes.Return):
        expr = self.compile(node.expr)
        self._add_line(f"return {expr}")
    
    def compile_Throw(self, node: Utils.ASTNodes.Throw):
        expr = self.compile(node.expr)
        self._add_line(f"raise Exception({expr})  # {node.name}")
    
    # ==================== MODULE ====================
    
    def compile_Export(self, node: Utils.ASTNodes.Export):
        """Ekspor: di Python bisa menggunakan __all__"""
        exports = []
        for exp in node.exports or []:
            result = self.compile(exp)
            if result:
                exports.append(result)
        if exports:
            self._add_line(f"__all__ = {exports}")
    
    def compile_ExportArgument(self, node: Utils.ASTNodes.ExportArgument):
        name = node.name.name
        alias = node.alias or name
        return alias
    
    def compile_Import(self, node: Utils.ASTNodes.Import):
        """impor { x as y } dari .:modul → from modul import x as y"""
        imports = []
        for imp in node.imports or []:
            imp_str = self.compile(imp)
            if imp_str:
                imports.append(imp_str)
        
        path = self.compile(node.from_path)
        # Ubah path IS ke Python import path
        py_path = self._is_path_to_py_path(path)
        
        if imports:
            imports_str = ", ".join(imports)
            self.imports.add(f"from {py_path} import {imports_str}")
    
    def compile_ImportArgument(self, node: Utils.ASTNodes.ImportArgument):
        if node.alias:
            return f"{node.name} as {node.alias}"
        return node.name
    
    def compile_PathID(self, node: Utils.ASTNodes.PathID):
        parts = []
        for arg in node.path or []:
            part = self.compile(arg)
            if part:
                parts.append(part)
        return "/".join(parts)
    
    def compile_PathArg(self, node: Utils.ASTNodes.PathArg):
        return node.arg
    
    # ==================== TYPES ====================
    
    def compile_BasicType(self, node: Utils.ASTNodes.BasicType):
        # BasicType hanya digunakan sebagai informasi tipe, tidak menghasilkan kode
        return node.name
    
    def compile_ArrayType(self, node: Utils.ASTNodes.ArrayType):
        # ArrayType juga hanya informasi
        return f"list[{self.compile(node.element_type)}]"
    
    # ==================== HELPERS ====================
    
    def _py_operator(self, op):
        """Mengubah operator Indonesian Script ke operator Python"""
        mapping = {
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '**': '**',
            '//': '//',
            '==': '==',
            '!=': '!=',
            '>=': '>=',
            '>': '>',
            '<=': '<=',
            '<': '<',
            'dan': 'and',
            'atau': 'or',
            'dalam': 'in',
            'tidak dalam': 'not in'
        }
        return mapping.get(op, op)
    
    def _default_value(self, py_type):
        """Nilai default untuk tipe Python"""
        if py_type is str:
            return ""
        elif py_type is int:
            return 0
        elif py_type is float:
            return 0.0
        elif py_type is bool:
            return False
        elif py_type is list:
            return []
        elif py_type is dict:
            return {}
        elif py_type is None or py_type is type(None):
            return None
        else:
            return None
    
    def _is_path_to_py_path(self, path: str) -> str:
        """Mengubah path Indonesian Script ke Python import path"""
        # Contoh: .:modul:file → modul.file
        path = path.replace(':', '.')
        if path.startswith('.'):
            path = path[1:]
        if path.endswith('.is'):
            path = path[:-3]
        return path
    
    def result(self):
        """Mengembalikan kode Python lengkap dengan import dan main guard"""
        lines = []
        
        # Imports
        if self.imports:
            lines.extend(sorted(self.imports))
            lines.append("")
        
        # Kode utama (global statements)
        lines.extend(self.current_lines)
        
        # Main guard
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")  # TODO: jika ada fungsi main? Atau jalankan langsung?
        
        return "\n".join(lines)