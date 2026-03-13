from indonesian_script import ModuleBridge as Mb

@Mb.Fungsi
def tambah(a: int, b: int) -> int:
    """Menambahkan dua angka"""
    raise Mb.Kembalikan(a + b)

@Mb.Fungsi
def kali(a: int, b: int) -> int:
    """Mengalikan dua angka"""
    return Mb.Kembalikan(a * b)

@Mb.Fungsi
def bagi(a: int, b: int) -> int:
    """Membagi dua angka"""
    if b == 0:
        raise Mb.Kegalatan("Tidak bisa membagi dengan nol")
    return (a // b)

@Mb.Fungsi
def check_time(angka: int) -> None:
    for i in range(angka):
        pass

@Mb.Modul
def matematika(p):
    """Modul matematika"""
    p.atur(tambah).atur(kali).atur(bagi).atur(check_time)
    p.ok()
    return p