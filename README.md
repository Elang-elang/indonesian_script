# Indonesian Script

Bahasa pemrograman dalam Bahasa Indonesia - Programming language in Indonesian

## Instalasi

### Yang dibutuhkan

```txt
python>=3.12
```

### Dan jalankan

```bash
git clone https://github.com/Elang-elang/is.git
cd is
./instalasi
```

## Penggunaan CLI

### Menjalankan file

```bash
is run program.is
```

### Melihat AST (Abstract Syntax Tree)

```bash
is ast program.is
```

### Mode REPL interaktif

```bash
is repl
```

### Melihat versi

```bash
is version
```

### Contoh Kode

```is
// hello.is
tuliskan "Halo, Dunia!"; // untuk primitif node
tampilkan("Halo, Dunia!"); // untuk modern node

teks nama = "Budi";
angka umur = 25;

jika (umur >= 18) maka {
    tuliskan(nama + " sudah dewasa");
} namun tidak {
    tuliskan(nama + " masih anak-anak");
}

angka faktorial(angka n) {
    jika (n <= 1) maka {
        kembalikan 1;
    }
    kembalikan n * faktorial(n - 1);
}

tampilkan("Faktorial 5 = " + faktorial(5));
```

## Fitur

· ✅ Variabel (var_decl, final_decl, def_decl)
· ✅ Tipe data: teks, angka, desimal, boolean, daftar, kamus
· ✅ Operator aritmatika dan logika
· ✅ Control flow: jika, selama, untuk
· ✅ Function dengan return dan throw
· ✅ Lambda expression
· ✅ Array dan Dictionary
· ✅ Pointer (& dan *)
· ✅ Try-catch-finally
· ✅ Input/Output (tuliskan, bacalah)
· ✅ REPL interaktif

## Lisensi

[MIT](./indonesian_script/License)

```