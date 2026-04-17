import sys
import time
from pathlib import Path
import os
import typer
from ..Interpreter.compile import Compile
from ._repl import ISRepl

app = typer.Typer(
    help='CS (dan kawan-kawan) merupakan perintah baris antarmuka yang friendly untuk menemani setiap perjalanan Anda',
    add_completion=False
)

@app.command()
def run(
    filename: str = typer.Argument(..., help='Masukan berkas untuk dijalankan')
) -> int:
    "Untuk menjalankan berkas"
    try:
        with open(filename, 'r') as _f:
            interp = Compile(filename, _f.read(), False)
            interp()
        return 0
    except Exception as e:
        raise e
        typer.secho(e, fg='cyan')
        typer.secho(f'Kesalahan {str(type(e))!r} saat menerjemahkan dan menjalankan berkas:', fg='red')
        return 1

@app.command()
def repl(
    debug_err: bool = typer.Option(
        False, '--debug', '-d',
        help='Untuk mendebug kegalatan'
    )
) -> int:
    "Mode interaktif REPL"
    try:
        repl = ISRepl(debug_err)
        repl.main()
        return 0
        
    except Exception as e:
        typer.secho(e, fg='cyan')
        typer.secho(f'Kesalahan {str(type(e))!r} saat menerjemahkan dan menjalankan antarmuka perintah:', fg='red')
        return 1

@app.command()
def self(
    version: bool = typer.Option(
        False, '--version', '-v',
        help='Untuk melihat versi cs & is'
    ),
    status: bool = typer.Option(
        False, '--state', '-s',
        help='Untuk melihat status cs & is'
    )
):
    "Untuk melihat cs & is"
    try:
        from .. import __version__, __status__
    
        if version or not status:
            typer.secho(f'Version: {__version__}', fg='green', bold=True)
        if status or not version:
            typer.secho(f'State: {__status__}', fg='yellow')
        
        return 0
        
    except Exception as e:
        typer.secho(e, fg='cyan')
        typer.secho(f'Kesalahan {str(type(e))!r} saat menjalankan perintah:', fg='red')
        return 1

@app.command()
def init(
    path: Path = typer.Argument(
        '.', help='Jalur untuk inisiasi paket'
    )
) -> int:
    try:
        
        with typer.progressbar(
            length=100,
            label='Proses pembuatan ...',
        ) as p:
            path = Path('.').absolute() / Path(path)
            p.update(10)
            time.sleep(0.01)
            
            src = path / 'src'
            p.update(10)
            time.sleep(0.01)
            
            file = src / 'utama.is'
            p.update(15)
            time.sleep(0.015)
            
            if not src.exists():
                src.mkdir()
                
            p.update(15)
            time.sleep(0.015)
            
            file.touch()
            p.update(20)
            time.sleep(0.02)
            
            file.write_text(
'''
fungsi[kekosongan] utama(){
    tuliskan "Halo Dunia" + enter;
}

jika (modul["berkas"] == "utama") {
    utama()
}
''')
            p.update(30)
            time.sleep(0.3)
        time.sleep(0.5)
        typer.secho(f'Sukses untuk membuat paket, cek berkas utama pada jalur {str(file)!r}', fg='green')
        return 0
        
    except Exception as e:
        typer.secho(e, fg='cyan')
        typer.secho(f'Kesalahan {str(type(e))!r} saat membuat paket:', fg='red')
        return 1

if __name__ == '__main__':
    sys.exit(app())