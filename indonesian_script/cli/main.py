import sys
from pathlib import Path
from ._argparse import ArgumentParser, Colors, f, s

# Import dari parent directory
from ..main import IndonesianScriptInterpreter, IndonesianScriptCompiler

class ISArgument:
    def __init__(self):
        self.parse, self.parser = self.__parse__()
    
    def __parse__(self):
        args = ArgumentParser(
            'cs',
            description='CS (dan kawan-kawan) merupakan perintah baris antarmuka yang friendly untuk menemani setiap perjalanan Anda'
        )
        
        arg_run = args.add_command('run', aliases=['r'], help='Untuk menjalankan berkas')
        arg_run.add_argument('file', help='Berkas yang ingin dijalankan')
        
        arg_compile = args.add_command('compile', aliases=['c'], help='Kompilasi berkas Indonesian Script')
        arg_compile.add_argument('--compiler', '-c',
            choices=list(IndonesianScriptCompiler._list_compiler.keys()),
            help='Target Kompilasi'
        )
        arg_compile.add_argument('--input', '-i', help='Berkas yang ingin dijalankan')
        arg_compile.add_argument('--output', '-o', nargs='?', help='Untuk keluaran berkas')
        
        arg_repl = args.add_command('repl', help='Mode interaktif REPL')
        arg_repl.add_argument('--debug', '-d', action='store_true', help='Untuk mendebugging error')
        
        args.add_argument('--version', '-v', action='store_true', help='Menampilkan versi')
        
        return args, args.parse_args()
    
    def main(self):
        args = self.parser
        print(args)
        if getattr(args, 'version', False):
            from .. import __version__, __status__
            print(
                f'{s.BRIGHT}{f.RED}i{f.WHITE}s{s.RESET_ALL} {Colors.bright_cyan(__version__)} {f.CYAN}{Colors.dim(__status__)}'
            )
            return 0
        
        elif args.command == 'repl':
            from . import ISRepl
            try:
                repr = ISRepl(getattr(args, 'debug', False))
                repr.main()
            except:
                raise
            finally:
                return 1
        
        elif args.command in ['r', 'run']:
            file = args.file
            if not file.endswith('.is'):
                raise NameError(f'Berkas harus berakhiran .is')
            
            with open(file, 'r') as file:
                try:
                    interp = IndonesianScriptInterpreter(file, file.read(), False)
                    interp.run()
                    return 0
                except:
                    raise
                finally:
                    return 1
            return 0
        
        elif args.command in ['c', 'compile']:
            print(f'{f.YELLOW}{s.BRIGHT}Komen ini sedang di kembangkan!{s.RESET_ALL}', end='\n\n')
            return 0
        else:
            args.help()
            return 0

def main():
    args: ISArgument = ISArgument()
    args.main()