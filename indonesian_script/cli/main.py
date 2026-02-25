#!/usr/bin/env python3
"""
Command Line Interface untuk Indonesian Script
"""

import argparse
import sys
from pathlib import Path

# Import dari parent directory
# sys.path.insert(0, str(Path(__file__).parent.parent))
from ..main import IndonesianScriptInterpreter
from ..Interpreter.Exceptions.Exceptions import *

# Warna untuk output (opsional)
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''

def print_color(text, color=Fore.CYAN, **kwargs):
    """Print dengan warna"""
    print(f"{color}{text}{Style.RESET_ALL}", **kwargs)

def run_file(filename, show_ast=False):
    """Jalankan file .is"""
    if not filename.endswith('.is'):
        print_color(f"Error: File harus berekstensi .is", Fore.RED)
        print_color(f"Tip: Gunakan 'is run namafile.is'", Fore.YELLOW)
        return 1
    
    filepath = Path(filename)
    if not filepath.exists():
        print_color(f"Error: File '{filename}' tidak ditemukan", Fore.RED)
        return 1
    
    try:
        print_color(f"\n📖 Membaca file: {filename}", Fore.CYAN)
        
        # Buat interpreter
        interpreter = IndonesianScriptInterpreter(filename)
        interpreter.load_file(filename)
        
        if show_ast:
            # Tampilkan AST
            print_color("\n🌳 Abstract Syntax Tree (AST):", Fore.MAGENTA + Style.BRIGHT)
            print_color("="*50, Fore.MAGENTA)
            
            # Parse untuk AST
            from lark import Lark
            with open(Path(__file__).parent.parent / 'grammar.txt', 'r') as f:
                grammar = f.read()
            
            parser = Lark(grammar, parser='earley', lexer='dynamic', start='program', regex=True)
            tree = parser.parse(interpreter.code)
            print(tree.pretty())
            print_color("="*50, Fore.MAGENTA)
        else:
            # Jalankan program
            print_color("\n🚀 Menjalankan program...", Fore.CYAN)
            print_color("="*50, Fore.WHITE + Style.BRIGHT)
            
            # Redirect output untuk capture jika perlu
            interpreter.run()
            
            print_color("="*50, Fore.WHITE + Style.BRIGHT)
        
        return 0
        
    except Galat as e:
        print_color(f"\n❌ {e.__class__.__name__}: {e}", Fore.RED)
        return 1
    except Exception as e:
        print_color(f"\n❌ Error: {e}", Fore.RED)
        import traceback
        traceback.print_exc()
        return 1

def repl_mode():
    """REPL Interactive Mode"""
    print_color("="*50, Fore.MAGENTA + Style.BRIGHT)
    print_color("  Indonesian Script REPL v0.1.0", Fore.MAGENTA + Style.BRIGHT)
    print_color("  Ketik 'exit()' untuk keluar", Fore.CYAN)
    print_color("  Ketik 'help()' untuk bantuan", Fore.CYAN)
    print_color("="*50, Fore.MAGENTA + Style.BRIGHT)
    
    interpreter = IndonesianScriptInterpreter()
    
    while True:
        try:
            # Input multi-line
            lines = []
            while True:
                prompt = "... " if lines else ">>> "
                try:
                    line = input(prompt)
                except EOFError:
                    print()
                    return 0
                
                if line.strip() == 'exit()':
                    print_color("Bye!", Fore.GREEN)
                    return 0
                
                if line.strip() == 'help()':
                    print_color("\nPerintah REPL:", Fore.MAGENTA)
                    print_color("  exit() - Keluar dari REPL", Fore.CYAN)
                    print_color("  help() - Tampilkan bantuan ini", Fore.CYAN)
                    print_color("  clear() - Bersihkan layar", Fore.CYAN)
                    print()
                    break
                
                if line.strip() == 'clear()':
                    import os
                    os.system('clear' if os.name == 'posix' else 'cls')
                    break
                
                lines.append(line)
                
                # Cek apakah sudah complete (ada titik koma di akhir baris terakhir)
                if line.rstrip().endswith(';'):
                    break
                # Atau jika baris kosong setelah beberapa baris
                if not line and lines:
                    break
            else:
                continue
            
            code = '\n'.join(lines)
            if not code.strip():
                continue
            
            # Jalankan kode
            try:
                interpreter.load_code(code).run()
            except Galat as e:
                print_color(f"Error: {e}", Fore.RED)
            except Exception as e:
                print_color(f"Error: {e}", Fore.RED)
                
        except KeyboardInterrupt:
            print("\nBye!")
            return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Indonesian Script - Bahasa pemrograman dalam Bahasa Indonesia',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['run', 'ast', 'repl', 'version', 'help'],
        default='help',
        help='Perintah yang akan dijalankan'
    )
    
    parser.add_argument(
        'filename',
        nargs='?',
        help='File .is yang akan diproses'
    )
    
    args = parser.parse_args()
    
    if args.command == 'version':
        from .. import __version__
        print_color(f"Indonesian Script v{__version__}", Fore.MAGENTA + Style.BRIGHT)
        print_color("Bahasa pemrograman dalam Bahasa Indonesia", Fore.CYAN)
        return 0
    
    elif args.command == 'repl':
        return repl_mode()
    
    elif args.command in ['run', 'ast']:
        if not args.filename:
            print_color(f"Error: Perlu menyertakan nama file", Fore.RED)
            print_color(f"Usage: is {args.command} <filename.is>", Fore.YELLOW)
            return 1
        
        return run_file(args.filename, show_ast=(args.command == 'ast'))
    
    else:  # help
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())