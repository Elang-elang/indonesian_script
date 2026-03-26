# Indonesian Script

Bahasa pemrograman dalam Bahasa Indonesia - Programming language in Indonesian

## Instalasi

### Yang dibutuhkan

* Python (Utama) >= 3.12
* lark-parser (Utama) >= 0.12.0
* regex (Utama) >= 2026.1.15
* colorama (Opsional) >= 0.4.6

```txt
lark-parser>=0.12.0,
regex>=2026.1.15,
colorama>=0.4.6,
```

### Dan jalankan

```bash
git clone https://github.com/Elang-elang/indonesian_script.git
cd is
pip install -e . # atau pip install -r requirements.txt
```

## Penggunaan CLI

### Menjalankan file

```bash
is run program.is
```

### Kompil kode (Python3, C, C++) 
```bash
is compile {Python3|C|C++} program.is
```
>komen ini sedang tahap perkembangan


### Mode REPL interaktif

```bash
is repl
```

### Melihat versi

```bash
is version
```

### Contoh Kode

```indonesian_script
// hello.is
tuliskan "Halo, Dunia!"; // untuk primitif node
tampilkan("Halo, Dunia!"); // untuk modern node

var[teks] nama = "Budi";
var[angka] umur = 25;

jika (umur >= 18) maka {
    tuliskan(nama + " sudah dewasa");
} namun tidak {
    tuliskan(nama + " masih anak-anak");
}

fungsi[angka] faktorial(angka n) {
    jika (n <= 1) maka {
        kembalikan 1;
    }
    kembalikan{n * faktorial(n - 1)};
}

tampilkan("Faktorial 5 = " + faktorial(5));
```

## Tentang
**indonesian_script** atau disingkat ***is*** adalah sebuah bahasa pemrograman yang terkompilasi serta membawa bahasa lokal, yakni bahasa Indonesia. Sintaks yang ada di bawakan untuk mempermudah, mempersingkat, dan memperdetail untuk dibaca. Bahasa pemrograman ini dikompilasi dengan bahasa Python versi 3 (**Python3**) yang membawa perpustakaan **lark-parser** sebagai pe-parse (penguraian bahasa) dan grammarnya sebagai lexer (leksikal).

## Keuntungan & Kekurangan
Adapun keuntungan dan kekurangan dari menjalankan bahasa ini, yakni:

### Keuntungan
* Bahasa mudah dibaca
* Dapat diinterpreterasikan & dikompilasikan
* Sintaks sangat mudah dipahami, detail, dan berbahasa lokal
* Kode-nya terbuka sumbernya

### Kekurangan
* Sangat lambat dari Python
* Mungking ada yang sebagian dari sintaksnya yang mungkin tidak dikenali
* Belum adanya dokumentasi yang lengkap

## Bantuan / Dokumentasi untuk 

[**Daftar bantuan**](./indonesian_script/Interpreter/ListHelpper.md)

> sedang dikembangkan

## Lisensi
[MIT](indonesian_script/License)