# main.py - Auto Interpreter untuk Indonesian Script
from lark import Lark, UnexpectedCharacters, UnexpectedToken
from pathlib import Path
import sys

# Import dari submodule
from .Interpreter.transformer import ASTBuilder
from .Interpreter.interpreter import Interpreter
from .Interpreter.Exceptions.exceptions import *

class IndonesianScriptInterpreter:
    """
    Auto Interpreter untuk Indonesian Script
    Bisa digunakan secara langsung atau di-import
    """
    
    def __init__(self, filename=None, code=None, ismodule=False):
        self.filename = Path(filename) if filename else None
        self.code = code
        self.result = None
        self.error = None
        self.ismodule = ismodule
        
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
    
    def run(self, console=False, get_interpreter=False):
        """
        Jalankan interpreter
        console: jika True, tampilkan output lengkap
        """
        if not self.code:
            raise IsiGalat("Tidak ada kode untuk dijalankan")
        
        # Buat parser
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
            tree = self._exc_check(parser, self.code)
            
            # Transform ke AST
            builder = ASTBuilder()
            ast = builder.transform(tree)
            
            # Interpretasi
            interpreter = Interpreter(filename=str(self.filename))
            
            self.result = interpreter.load(ast)
            
            if console:
                self._console_output(interpreter)
            
            if get_interpreter:
                return self.result, interpreter
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
    
    def _get_exc_text(self, exception, code):
        """Buat teks exception"""
        lines = []
        lines.append(f"Pada: {self.filename or '<string>'}")
        
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

# Alias untuk kemudahan
isi = IndonesianScriptInterpreter