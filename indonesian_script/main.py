# main.py - Auto Interpreter untuk Indonesian Script
from lark import Lark, UnexpectedCharacters, UnexpectedToken
from pathlib import Path
import sys

# Import dari submodule
from .Interpreter.transformer import ASTBuilder
from .Interpreter.interpreter import Interpreter
from .Interpreter.Exceptions.exceptions import *
from . import Compiler

# var
grammar_path = Path(__file__).parent / 'grammar.txt'
if not grammar_path.exists():
    raise JalurGalat(f"File grammar tidak ditemukan di {grammar_path}")

with open(grammar_path, 'r', encoding='utf-8') as f:
    grammar = f.read()

class IndonesianScriptInterpreter:
    """
    Auto Interpreter untuk Indonesian Script
    Bisa digunakan secara langsung atau di-import
    """
    
    parser = Lark(
        grammar,
        parser='earley',
        lexer='dynamic',
        start='program',
        regex=True,
        ambiguity='resolve'
    )
    
    def __init__(self, filename=None, code=None, ismodule=False):
        self.filename = Path(filename) if filename else None
        self.code = code
        self.result = None
        self.error = None
        self.ismodule = ismodule
        self.interpreter = Interpreter(filename=str(self.filename))
        self.builder = ASTBuilder()
        
        # Load grammar
        grammar_path = Path(__file__).parent / 'grammar.txt'
        if not grammar_path.exists():
            raise JalurGalat(f"File grammar tidak ditemukan di {grammar_path}")
        
        with open(grammar_path, 'r', encoding='utf-8') as f:
            self.grammar = f.read()
    
    def load_file(self, filename):
        """Load kode dari file"""
        self.filename = Path(filename)
        if not self.filename.exists():
            raise JalurGalat(f"File '{filename}' tidak ditemukan")
        
        with open(self.filename, 'r', encoding='utf-8') as f:
            self.code = f.read()
        
        return self
    
    def load_code(self, code):
        """Load kode dari string"""
        self.code = code
        return self
    
    def load_interp(self, interp):
        self.interpreter.load_interp(interp)
        return self
    
    def get_ast(self, code=None):
        if code:
            self.code = code
        
        tree = self._exc_check(self.parser, self.code)
        return self.builder.transform(tree)
    
    def run(self, console=False, get_interpreter=False):
        """
        Jalankan interpreter
        console: jika True, tampilkan output lengkap
        """
        if not self.code:
            raise IsiGalat("Tidak ada kode untuk dijalankan")
        
        try:
            # Parse kode
            tree = self._exc_check(self.parser, self.code)
            
            # Transform ke AST
            ast = self.builder.transform(tree)
            
            self.result = self.interpreter.load(ast)
            
            if console:
                self._console_output(self.interpreter)
            
            if get_interpreter:
                return self.result, self.interpreter
            return self.result
            
        except Exception as e:
            self.error = e
            if console:
                print(f"\n❌ Error: {e}", file=sys.stderr)
            raise
    
    def _exc_check(self, parser, code):
        """Cek exception saat parsing"""
        try:
            return parser.parse(code)
        except UnexpectedCharacters as e:
            raise KarakterGalat(self._get_exc_text(e, code))
        except UnexpectedToken as e:
            if hasattr(e, 'expected') and 'SEMICOLON' in str(e.expected):
                raise TitikKomaGalat(self._get_exc_text(e, code))
            raise PenulisanGalat(self._get_exc_text(e, code))
        except Exception as e:
            raise PenulisanGalat(f"Error parsing: {str(e)}")
    
    def _get_exc_text(self, exception, filename='<string>'):
        """Buat teks exception"""
        if hasattr(self, 'filename'):
            filename = self.filename
        lines = []
        lines.append(f"Pada: {filename}")
        
        # Dapatkan context
        if hasattr(exception, 'get_context'):
            context = exception.get_context(code)
            if context:
                lines.append(context)
        
        # Dapatkan line dan column
        if hasattr(exception, 'line') and hasattr(exception, 'column'):
            line = getattr(exception, 'line', 0)
            column = getattr(exception, 'column', 0)
            if line > 0 and column > 0:
                lines.append(f"Baris: {line}, Kolom: {column}")
        
        return '\n'.join(lines)
    
    def _console_output(self, interpreter):
        """Tampilkan output console"""
        print("\n" + "="*50)
        print(" HASIL EKSEKUSI ")
        print("="*50)
        
        # Output sudah dicetak oleh interpreter.visit_WriteStmt
        # Tapi kita bisa tambahkan info scope jika perlu
        
        if hasattr(interpreter, 'current_scope'):
            print("\n" + "="*50)
            print(" VARIABEL GLOBAL ")
            print("="*50)
            for name, info in interpreter.global_scope.vars.items():
                if not name.startswith('_'):  # Skip internal
                    print(f"  {name}: {info['value']} ({info['type'].name})")

class IndonesianScriptCompiler:
    """
    Compiler untuk Indonesian Script ke berbagai target
    """
    
    _list_compiler = {
        'Python3': getattr(Compiler, 'PyCompiler')
    }
    
    _extend_list = {
        'Python3': '.py'
    }
    
    def __init__(self, filename='<stdin>', code='', compiler='Python3'):
        self.filename = filename
        self.code = code
        self.compiler = compiler
        self.grammar_path = Path(__file__).parent / 'grammar.txt'
        
        # Load grammar
        if not self.grammar_path.exists():
            raise JalurGalat(f"File grammar tidak ditemukan di {self.grammar_path}")
        
        with open(self.grammar_path, 'r', encoding='utf-8') as f:
            self.grammar = f.read()
        
        # Validasi compiler
        if self.compiler not in self._list_compiler:
            raise KeyError(f"Compiler '{self.compiler}' tidak tersedia. Pilihan: {list(self._list_compiler.keys())}")
    
    def load_filename(self, filename: str):
        """Load kode dari file"""
        filepath = Path(filename)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File '{filename}' tidak ditemukan")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.code = f.read()
        
        self.filename = str(filepath)
        return self
    
    def load_code(self, code: str):
        """Load kode dari string"""
        if not code:
            raise ValueError("Kode tidak boleh kosong")
        
        self.code = code
        return self
    
    def compile(self):
        """Melakukan kompilasi dan mengembalikan hasil sebagai string"""
        if not self.code:
            raise ValueError("Tidak ada kode untuk dikompilasi")
        
        parser = Lark(
            self.grammar,
            parser='earley',
            lexer='dynamic',
            start='program',
            regex=True,
            ambiguity='resolve'
        )
        
        try:
            # Parse kode
            tree = parser.parse(self.code)
            
            builder = ASTBuilder()
            ast = builder.transform(tree)
            
            # Pilih compiler berdasarkan target
            compiler_obj = self._list_compiler[self.compiler].Compiler(self.filename)
            compiler_obj.compile(ast)
            result = compiler_obj.result()
            return result
            
        except KeyError as e:
            raise ValueError(f"Compiler {self.compiler} belum diimplementasi")
        except Exception as e:
            # Tangkap error parsing
            if hasattr(e, 'line') and hasattr(e, 'column'):
                line_info = f" pada baris {e.line}, kolom {e.column}"
            else:
                line_info = ""
            raise RuntimeError(f"Error kompilasi{line_info}: {e}")
    
    def output_file(self, filename: str = None):
        """Simpan hasil kompilasi ke file"""
        if not filename:
            # Buat nama file default
            base = Path(self.filename).stem if self.filename != '<stdin>' else 'output'
            ext = self._extend_list.get(self.compiler, '.txt')
            filename = base + ext
        
        # Lakukan kompilasi
        result = self.compile()
        
        # Simpan ke file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return filename
        
# Alias untuk kemudahan
isi = IndonesianScriptInterpreter
isc = IndonesianScriptCompiler