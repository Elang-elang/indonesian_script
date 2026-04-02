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
    file: str = typer.Argument(..., help='Masukan berkas untuk dijalankan')
):
    "Untuk menjalankan berkas"
    with open(file, 'r') as f:
        interp = Compile(f, None, False)
        interp()

@app.command()
def repl(
    debug_err: bool = typer.Option(
        False, '--debug', '-d',
        help='Untuk mendebug kegalatan'
    )
): 
    "Mode interaktif REPL"
    repl = ISRepl(debug_err)
    repl.main()

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
    from .. import __version__, __status__
    
    if version or not status:
        typer.secho(f'Version: {__version__}', fg='green', bold=True)
    if status or not version:
        typer.secho(f'State: {__status__}', fg='yellow')

@app.command()
def init(
    path: Path = typer.Argument(
        '.', help='Jalur untuk inisiasi paket'
    )
):
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
    except Exception as e:
        typer.secho(f'Kesalahan saat membuat paket: {str(e)!r}', fg='red')

if __name__ == '__main__':
    app()