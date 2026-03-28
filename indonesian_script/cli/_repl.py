# repr.py
from colorama import init, Fore, Style
import os
import sys
from pathlib import Path
import readline  # Untuk history
import atexit

# Inisialisasi colorama
init()

class ISRepl:
    """
    REPL (Read-Eval-Print-Loop) untuk Indonesian Script
    Fitur:
    - Deteksi blok otomatis (if, fungsi, loop, dll)
    - History penyimpanan di ~/.is_history
    - State interpreter yang bertahan
    - Auto-completion sederhana
    """
    
    # Kata kunci yang memulai blok
    _BLOCK_STARTERS = {
        'jika', 'selama', 'untuk', 'coba', 'kelas', 'fungsi',
        'jika', 'namun', 'dengan', 'pakai'
    }
    
    # Kata kunci yang menandakan akhir blok (opsional, untuk deteksi)
    _BLOCK_ENDERS = {'akhiri', 'selesai'}
    
    # Karakter yang menandakan akhir statement
    _STATEMENT_END = ';'
    
    def __init__(self, debug_err=False):
        self._interp = None           # Interpreter yang menyimpan state
        self._debug_err = debug_err   # Mode debug untuk melihat error detail
        self._current_block = []      # Kumpulan baris dalam blok saat ini
        self._in_block = False        # Apakah sedang dalam mode blok
        self._history_file = Path.home() / '.is_history'  # Lokasi file history
        
        # Setup history
        self._setup_history()
        
        # Setup auto-completion
        self._setup_completer()
    
    def _setup_history(self):
        """Mengatur history penyimpanan dari file"""
        try:
            # Load history jika ada
            if self._history_file.exists():
                readline.read_history_file(str(self._history_file))
            
            # Set history length
            readline.set_history_length(1000)
            
            # Simpan history saat keluar
            atexit.register(self._save_history)
        except Exception as e:
            # Jika gagal, lanjutkan tanpa history
            if self._debug_err:
                print(f"Warning: Could not setup history: {e}")
    
    def _save_history(self):
        """Menyimpan history ke file"""
        try:
            readline.write_history_file(str(self._history_file))
        except Exception as e:
            if self._debug_err:
                print(f"Warning: Could not save history: {e}")
    
    def _setup_completer(self):
        """Mengatur auto-completion sederhana"""
        try:
            readline.set_completer(self._completer)
            readline.parse_and_bind("tab: complete")
        except Exception:
            pass  # Completer tidak wajib
    
    def _completer(self, text, state):
        """Auto-completion untuk kata kunci"""
        # Daftar kata kunci untuk auto-completion
        keywords = [
            'jika', 'namun', 'selama', 'untuk', 'coba', 'tangkap', 'akhiri',
            'fungsi', 'kelas', 'kembalikan', 'kegalatan', 'tuliskan', 'bacalah',
            'alias', 'final', 'teks', 'angka', 'desimal', 'boolean', 'daftar', 'kamus',
            'benar', 'salah', 'kosong', 'enter', 'tab', 'lambda', 'tipe_dari',
            'adalah', 'bukanlah', 'dalam', 'tidak', 'dan', 'atau',
            'impor', 'ekspor', 'dari', 'sebagai'
        ]
        
        # Filter keyword yang dimulai dengan text
        matches = [k for k in keywords if k.startswith(text)]
        
        if state < len(matches):
            return matches[state]
        return None
    
    def _get_prompt(self):
        """Mendapatkan prompt berdasarkan mode (blok atau tidak)"""
        if self._in_block:
            return f'{Fore.MAGENTA}{Style.BRIGHT}...{Style.RESET_ALL} '
        return f'{Fore.MAGENTA}{Style.BRIGHT}>>>{Style.RESET_ALL} '
    
    def _is_block_start(self, line: str) -> bool:
        """
        Mengecek apakah baris memulai sebuah blok.
        Deteksi berdasarkan:
        - Kata kunci di awal (jika, selama, untuk, fungsi, kelas, coba)
        - Adanya '{' atau 'maka' di akhir
        """
        stripped = line.strip()
        
        # Cek jika baris kosong
        if not stripped:
            return False
        
        # Cek jika baris diakhiri dengan '{' atau 'maka' (indikasi blok)
        if stripped.endswith('{') or stripped.endswith('maka') or stripped.endswith('lakukan'):
            return True
        
        # Cek kata kunci di awal
        first_word = stripped.split()[0] if stripped.split() else ''
        if first_word in self._BLOCK_STARTERS:
            # Jika ada '{' atau 'maka' di baris ini juga, bisa jadi satu baris
            if '{' in stripped or 'maka' in stripped:
                # Cek apakah blok sudah selesai dalam satu baris
                if stripped.count('{') == stripped.count('}') and stripped.endswith('}'):
                    return False
            return True
        
        return False
    
    def _is_block_end(self, line: str) -> bool:
        """
        Mengecek apakah baris mengakhiri blok.
        Blok selesai ketika jumlah '{' dan '}' seimbang, atau ada '}'
        """
        stripped = line.strip()
        
        # Hitung kurung kurawal
        open_braces = stripped.count('{')
        close_braces = stripped.count('}')
        
        # Jika tidak ada kurung kurawal, blok mungkin selesai dengan kata kunci 'akhiri'
        if open_braces == 0 and close_braces == 0:
            # Cek kata kunci penutup
            first_word = stripped.split()[0] if stripped.split() else ''
            if first_word in self._BLOCK_ENDERS:
                return True
        
        # Blok selesai jika jumlah buka dan tutup sama
        return open_braces == close_braces and close_braces > 0
    
    def _needs_continuation(self, code: str) -> bool:
        """
        Mengecek apakah kode masih membutuhkan lanjutan.
        Tidak hanya blok, tapi juga struktur yang belum selesai.
        """
        if not code.strip():
            return False
        
        # Hitung kurung
        parentheses = code.count('(') - code.count(')')
        brackets = code.count('[') - code.count(']')
        braces = code.count('{') - code.count('}')
        
        # Cek jika ada kurung yang belum ditutup
        if parentheses > 0 or brackets > 0 or braces > 0:
            return True
        
        # Cek jika ada operator yang menggantung (+, -, dll di akhir)
        stripped = code.strip()
        if stripped and stripped[-1] in '+-*/%=&|<>':
            return True
        
        # Cek jika ada kata kunci yang belum selesai
        last_line = code.strip().split('\n')[-1] if '\n' in code else code.strip()
        if last_line and last_line.split() and last_line.split()[0] in self._BLOCK_STARTERS:
            # Cek apakah sudah ada 'maka' atau '{'
            if 'maka' not in last_line and '{' not in last_line:
                return True
        
        return False
    
    def _collect_block(self, first_line: str) -> str:
        """
        Mengumpulkan baris-baris hingga blok selesai.
        """
        lines = [first_line]
        self._in_block = True
        
        while True:
            try:
                prompt = self._get_prompt()
                line = input(prompt).strip()
                
                if not line and not lines:
                    continue
                
                lines.append(line)
                
                # Gabungkan kode yang sudah dikumpulkan
                full_code = '\n'.join(lines)
                
                # Cek apakah sudah selesai (tidak perlu lanjutan)
                if not self._needs_continuation(full_code):
                    self._in_block = False
                    return full_code
                
            except (KeyboardInterrupt, EOFError):
                print()  # New line
                self._in_block = False
                return None
        
        return None
    
    def run_prompt(self, prompt: str):
        """
        Menjalankan satu prompt dan menampilkan hasilnya.
        """
        from .. import IndonesianScriptInterpreter
        
        if not prompt.strip():
            return
        
        try:
            # Cek apakah ini memulai blok
            if self._is_block_start(prompt):
                full_code = self._collect_block(prompt)
                if full_code is None:
                    return
            else:
                full_code = prompt
            
            # Pastikan ada titik koma di akhir jika tidak ada
            if not full_code.strip().endswith(';') and not full_code.strip().endswith('}'):
                full_code = full_code.rstrip() + ';'
            
            # Buat interpreter baru atau gunakan yang sudah ada
            interp = IndonesianScriptInterpreter(
                filename='<repl>',
                code=full_code,
                ismodule=False
            )
            
            ast = interp.get_ast()
            
            # Load interpreter dengan state sebelumnya
            if self._interp:
                # Gunakan interpreter yang sudah ada
                result = self._interp.load(ast)
            else:
                # Buat interpreter baru
                result, self._interp = interp.run(False, True)
            
            # Tampilkan hasil jika ada (bukan None)
            if result is not None:
                print(f"{Fore.GREEN}{Style.BRIGHT}{result}{Style.RESET_ALL}")
            
        except Exception as e:
            # Tampilkan error dengan warna
            print(f"{Fore.RED}{Style.BRIGHT}Galat:{Style.RESET_ALL} {Fore.MAGENTA}{str(e)}{Style.RESET_ALL}")
            
            # Jika mode debug, tampilkan traceback
            if self._debug_err:
                import traceback
                traceback.print_exc()
            
            # Reset block state
            self._in_block = False
            self._current_block = []
    
    def main(self):
        """
        Loop utama REPL.
        """
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("=" * 50)
        print("  Indonesian Script REPL v1.0")
        print("  Ketik '.exit;' untuk keluar")
        print("  Ketik '.clear;' untuk bersihkan layar")
        print("  Ketik '.help;' untuk bantuan")
        print("=" * 50)
        print(f"{Style.RESET_ALL}")
        
        _isrun = True
        _cexit = 0
        
        while _isrun:
            try:
                prompt_text = self._get_prompt()
                prompt = input(prompt_text).strip()
                
                # Skip empty
                if not prompt:
                    continue
                
                # Perintah khusus
                if prompt == '.exit;' or prompt == '.exit':
                    _isrun = False
                    break
                
                elif prompt == '.clear;' or prompt == '.clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                elif prompt == '.help;' or prompt == '.help':
                    self._show_help()
                    continue
                
                elif prompt == '.vars;' or prompt == '.vars':
                    self._show_vars()
                    continue
                
                # Jalankan prompt
                self.run_prompt(prompt)
                
            except KeyboardInterrupt:
                print()  # New line
                continue
            
            except EOFError:
                print()
                break
            
            except Exception as e:
                print(f"{Fore.RED}{Style.BRIGHT}Error:{Style.RESET_ALL} {Fore.MAGENTA}{str(e)}{Style.RESET_ALL}")
                if self._debug_err:
                    import traceback
                    traceback.print_exc()
                continue
        
        print(f"\n\n{Fore.GREEN}{Style.BRIGHT}Terima kasih telah menggunakan Indonesian Script!{Style.RESET_ALL}\n")
        return _cexit
    
    def _show_help(self):
        """Menampilkan bantuan"""
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("Perintah REPL Indonesian Script:")
        print("  .exit;        - Keluar dari REPL")
        print("  .clear;       - Bersihkan layar")
        print("  .help;        - Tampilkan bantuan ini")
        print("  .vars;        - Tampilkan variabel yang tersedia")
        print()
        print("Fitur:")
        print("  - Auto-completion (tekan Tab)")
        print("  - History perintah (tersimpan di ~/.is_history)")
        print("  - Deteksi blok otomatis (if, loop, fungsi, dll)")
        print("  - State interpreter bertahan antar perintah")
        print(f"{Style.RESET_ALL}")
    
    def _show_vars(self):
        """Menampilkan variabel yang tersedia di interpreter"""
        if self._interp and hasattr(self._interp, 'global_scope'):
            vars_dict = self._interp.global_scope.vars
            if vars_dict:
                print(f"{Fore.GREEN}{Style.BRIGHT}Variabel yang tersedia:{Style.RESET_ALL}")
                for name, info in vars_dict.items():
                    if not name.startswith('_'):
                        val = info['value']
                        tipe = info['type'].name if hasattr(info['type'], 'name') else str(info['type'])
                        print(f"  {Fore.CYAN}{name}{Style.RESET_ALL}: {Fore.YELLOW}{val}{Style.RESET_ALL} ({tipe})")
            else:
                print(f"{Fore.YELLOW}Tidak ada variabel yang tersedia{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Belum ada interpreter yang dijalankan{Style.RESET_ALL}")