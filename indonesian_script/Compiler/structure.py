# structure.py
from abc import ABC, abstractmethod
from ..Interpreter.AST_node.ast_nodes import *
from ..Interpreter.AST_node import ast_nodes
from ..Interpreter.Builtins.builtins import TYPES
from ..Interpreter.Builtins.checking_type import check_type

class StructCompiler(ABC):
    """
    Kelas abstrak untuk kompilasi dari Indonesian Script ke berbagai bahasa target.
    Turunan kelas harus mengimplementasikan semua method compile_... yang sesuai dengan node AST.
    """
    
    def compile(self, node: Node):
        """
        Mendispatch kompilasi berdasarkan tipe node.
        """
        method_name = f"compile_{type(node).__name__}"
        compiler = getattr(self, method_name, self.generic_compile)
        return compiler(node)
    
    def generic_compile(self, node: Node):
        """
        Fallback jika tidak ada method khusus untuk tipe node.
        """
        raise NotImplementedError(f"Tidak ada compiler untuk node {type(node).__name__}")
    
    @abstractmethod
    def result(self):
        """
        Untuk mengambil Return dan diolah menjadi Result
        """
        pass
    
    # ==================== PROGRAM & BLOCKS ====================
    
    @abstractmethod
    def compile_Program(self, node: Program):
        """Program utama (kumpulan statement)"""
        pass
    
    @abstractmethod
    def compile_Block(self, node: Block):
        """Blok kode (kurung kurawal)"""
        pass
    
    # ==================== STATEMENTS ====================
    
    # --- Variable Declarations ---
    @abstractmethod
    def compile_VarDecl(self, node: VarDecl):
        """Deklarasi variabel dengan inisialisasi"""
        pass
    
    @abstractmethod
    def compile_FinalDecl(self, node: FinalDecl):
        """Deklarasi variabel final (konstan)"""
        pass
    
    @abstractmethod
    def compile_DefDecl(self, node: DefDecl):
        """Deklarasi variabel tanpa inisialisasi (default)"""
        pass
    
    @abstractmethod
    def compile_AliasDecl(self, node: AliasDecl):
        """Alias/deklarasi ulang dengan nama lain"""
        pass
    
    @abstractmethod
    def compile_Redecl(self, node: Redecl):
        """Reassign nilai variabel yang sudah ada"""
        pass
    
    # --- CLI I/O ---
    @abstractmethod
    def compile_WriteStmt(self, node: WriteStmt):
        """Statement tulis (output)"""
        pass
    
    @abstractmethod
    def compile_ReadStmt(self, node: ReadStmt):
        """Statement baca (input)"""
        pass
    
    # ==================== CONTROL FLOW ====================
    
    # --- If ---
    @abstractmethod
    def compile_IfCtrl(self, node: IfCtrl):
        """Kontrol if dengan elif dan else"""
        pass
    
    @abstractmethod
    def compile_IfStmt(self, node: IfStmt):
        """Statement if tunggal"""
        pass
    
    @abstractmethod
    def compile_ElifStmt(self, node: ElifStmt):
        """Statement elif"""
        pass
    
    @abstractmethod
    def compile_ElseStmt(self, node: ElseStmt):
        """Statement else"""
        pass
    
    # --- While ---
    @abstractmethod
    def compile_WhileStmt(self, node: WhileStmt):
        """Loop while"""
        pass
    
    # --- For ---
    @abstractmethod
    def compile_ForStmt(self, node: ForStmt):
        """Loop for each"""
        pass
    
    @abstractmethod
    def compile_ForExpr(self, node: ForExpr):
        """Ekspresi for (range/iterable)"""
        pass
    
    # --- Try ---
    @abstractmethod
    def compile_TryCtrl(self, node: TryCtrl):
        """Kontrol try-catch-finally"""
        pass
    
    @abstractmethod
    def compile_TryStmt(self, node: TryStmt):
        """Blok try"""
        pass
    
    @abstractmethod
    def compile_CatchStmt(self, node: CatchStmt):
        """Blok catch"""
        pass
    
    @abstractmethod
    def compile_FinallyStmt(self, node: FinallyStmt):
        """Blok finally"""
        pass
    
    # ==================== EXPRESSIONS ====================
    
    @abstractmethod
    def compile_BinaryOp(self, node: BinaryOp):
        """Operator biner (+, -, *, /, %, **, //, ==, !=, >=, >, <=, <, dan, atau, dalam, tidak dalam)"""
        pass
    
    @abstractmethod
    def compile_UnaryOp(self, node: UnaryOp):
        """Operator unary ('tidak')"""
        pass
    
    @abstractmethod
    def compile_Literal(self, node: Literal):
        """Literal (string, angka, boolean, array, dictionary)"""
        pass
    
    @abstractmethod
    def compile_Variable(self, node: Variable):
        """Variabel (identifier)"""
        pass
    
    @abstractmethod
    def compile_GetObj(self, node: GetObj):
        """Akses atribut atau indeks"""
        pass
    
    @abstractmethod
    def compile_CallFunc(self, node: CallFunc):
        """Panggilan fungsi"""
        pass
    
    @abstractmethod
    def compile_CallParameter(self, node: CallParameter):
        """Parameter pemanggilan fungsi (kumpulan argumen)"""
        pass
    
    @abstractmethod
    def compile_CallArgument(self, node: CallArgument):
        """Argumen pemanggilan (bisa positional atau keyword)"""
        pass
    
    @abstractmethod
    def compile_LambdaFunc(self, node: LambdaFunc):
        """Fungsi lambda"""
        pass
    
    @abstractmethod
    def compile_TypeOf(self, node: TypeOf):
        """Operator tipe_dari (type of)"""
        pass
    
    @abstractmethod
    def compile_IsStmt(self, node: IsStmt):
        """Pernyataan is (adalah / bukanlah)"""
        pass
    
    # ==================== FUNCTIONS ====================
    
    @abstractmethod
    def compile_Function(self, node: Function):
        """Deklarasi fungsi"""
        pass
    
    @abstractmethod
    def compile_Parameter(self, node: Parameter):
        """Parameter fungsi (kumpulan argumen formal)"""
        pass
    
    @abstractmethod
    def compile_Argument(self, node: Argument):
        """Argumen formal fungsi (dengan tipe dan default)"""
        pass
    
    @abstractmethod
    def compile_Return(self, node: Return):
        """Statement return"""
        pass
    
    @abstractmethod
    def compile_Throw(self, node: Throw):
        """Statement throw (kegalatan)"""
        pass
    
    # ==================== MODULE ====================
    
    @abstractmethod
    def compile_Export(self, node: Export):
        """Ekspor modul"""
        pass
    
    @abstractmethod
    def compile_ExportArgument(self, node: ExportArgument):
        """Argumen ekspor (nama dengan alias opsional)"""
        pass
    
    @abstractmethod
    def compile_Import(self, node: Import):
        """Impor modul"""
        pass
    
    @abstractmethod
    def compile_ImportArgument(self, node: ImportArgument):
        """Argumen impor (nama dengan alias opsional)"""
        pass
    
    @abstractmethod
    def compile_PathID(self, node: PathID):
        """Path identifier (kumpulan segmen path)"""
        pass
    
    @abstractmethod
    def compile_PathArg(self, node: PathArg):
        """Segmen path"""
        pass
    
    # ==================== TYPES ====================
    
    @abstractmethod
    def compile_BasicType(self, node: BasicType):
        """Tipe dasar (teks, angka, dll)"""
        pass
    
    @abstractmethod
    def compile_ArrayType(self, node: ArrayType):
        """Tipe array (daftar dengan panjang dan tipe elemen)"""
        pass


class Utils:
    ASTNodes = ast_nodes
    
    @classmethod
    def check_type(cls, value, type):
        return check_type(value, type)
    
    @classmethod
    def get_py_type(cls, node: BasicType):
        return TYPES.get(node.name, node.name)