## Tipe pada **indonesian_script**
Tipe bersifat **WAJIB** pada indonesian_script. dikarenakan sistem butuh namanya patokan untuk tipe dari isian yang diisikan atau nilai yang dikembalikan.

Adapun dalam **indonesian_script** (is) tipe dibagi menjadi 2, yaitu:

### BasicType (Tipe Umum)
BasicType atau dalam bahasa indonesia nya adalah tipe umum merupakan tipe yang sering kali ditemukan dan juga ***TIDAK MEMERLUKAN PERINTAH YANG SPESIFIK*** untuk penguraian (parsering). inilah tipe-tipe umum yang ada pada indonesian_script:

* **teks** (string): adalah tipe yang bersifat apapun selagi dibuka dengan " dan ditutup dengan ", contoh: "hello world".
* **angka** (integer): adalah tipe yang bersifat bilangan bulat.
* **desimal** (decimal): adalah tipe yang bersifat bilangan non-bulat/pecahan dan pasti ada "." sebagai penanda ",".
* **boolean** (boolean): bersifat biner (1 dan 0) dalam bentuk kata, yakni: *benar* (1) dan *salah* (0).
* **kekosongan** (void): adalah tipe dari isi kosong (null).
* **apapun** (any): adalah tipe yang memperesentasikan semua tipe

**contoh penggunaan**:
```indonesian_script
var[teks] nama_aku = "user123";
var[angka] umur = 10;
var[desimal] tiggi_badan = 0.9;
var[boolean] apakah_aku_anak = benar;
var[kekosongan] isi_dompetku = kosong;
var[apapun] isi_barang_temanku = kosong; // bisa apap saja
```

### ObjectType (Tipe Objek)
ObjectType atau Tipe Objek adalah tipe yang ***MEMERLUKAN PERINTAH YANG SPESIFIK*** seperti perintah untuk masukan panjang literal-nya, tipe isi pada setiap blok literal-nya, dan lain-lain sebagainya. Adapun daftar dari tipe-tipe objek yang telah di sediakan. yaitu:

#### **Daftar**
Daftar (Array/List) adalah tipe yang memuat lebih dari 1 literal disimpan pada daftar yang dapat diakses dengan indeks yang bermula dari indeks ke 0, yang pasti diawali dengan [ dan di tutup dengan ]; Tipe dari literal itu harus dideklarasikan dan panjang dari isi daftar itu harus di ketahui, contoh perintah:

```indonesian_script
daftar< panjang >[ tipe ];
```

* **daftar**: adalah nama tipe-nya.
* **panjang**: berupa angka.
* **tipe**: adalah tipe dari literal yang akan diisi oleh literalnya itu sendiri.
* **<** ... **>** **[** ... **]** adalah tempat pendefinisiannya

> catatan: kalau tidak ada isi-nya (tipe maupun panjangnya) kosongkan saja

#### **Kamus**
Kamus (dictionary) adalah tipe yang memuat lebih dari 1 literal yang terdiri dari literal untuk kunci dan literal isi dari kunci tersebut yang juga dimana setiap literal pasti lebiu dari 1 literal, kunci sebagai "dimana" isi itu disimpan. kamus itu pasti diawali dan berisi serta diakhiri dengan { kunci: isi, ...dan_seterusnya }; Tipe dari literal itu harus dideklarasikan dan panjang dari isi kamus itu harus diketahui, contoh perintah: 

```indonesian_script
kamus< panjang >{ tipe_kunci: tipe_isi };
```

* **kamus**: adalah nama dari tipe-nya.
* **panjang**: berupa angka.
* **tipe_kunci**: adalah tipe dari literal yang akan menjadi kunci / petunjuk dari letak dimana isi-nya akan disimpan.
* **tipe_isi**: adalah tipe dari literal yang akan menjadi isi dari kunci / petunjuk yang telah ditetapkan.
* **<** ... **>** **{** ... **}** adalah tempat pendefinisiannya

> catatan: kalau tidak ada isi-nya (tipe maupun panjangnya) kosongkan saja

#### Fungsi
Fungsi Tipe (FunctionType) adalah tipe untuk memperesentasikan isi tipe dari argumen, parameter, dan nilai kembali dengan diperesentasikan dengan sebagai berikut:

```indonesian_script
fungsi< tipe_dari_nilai_kembali >{ tipe_dari_argumen1, ... };
```
* **fungsi**: adalah nama tipe.
* **tipe_dari_nilai_kembali**: adalah tipe dari nilai kembali.
* **tipe_dari_argumen1**: adalah tipe dari argumen ke 1.
* **...** : dan seterusnya.
* **<** ... **>** **{** ... **}** adalah tempat pendefinisiannya

> catatan: kalau tidak ada isi-nya (tipe maupun panjangnya) kosongkan saja

#### Serikatan
Serikatan Tipe (UnionType) adalah tipe yang menyimpan berbagai tipe. pasti ada waktunya kita tidak ingin menggunakan tipe **apapun** namun ingin menggunakan tipe lebih dari satu, serikatan/Gabungan-Gabungan dari tipe akan taruh disini sebagai patokan agar interpreter tidak mendefinisikan tipe yang lebih baik dan mudah dilihat. contoh perintah untuk mendefinisikan tipe serikatan:

```indonesian_script
[tipe1, tipe2, ...];
```
* **[** ... **]** adalah blok untuk mendefinisikannya.
* **tipe1**, **tipe2** adalah tipe ke 1, ke 2, dan seterusnya.

#### Literal
Literal Tipe (LiteralType) adalah tipe yang menyimpan berbagai literal. saat kalian ingin memastikan literal yang harus sesuai dengan yang diinginkan, pasti memiliki pemilahan yang panjang dan sulit. namun dengan Literal Tipe ini anda dapat mepilahnya dengan lebih mudah. Dengan cara ini kalian dapat menjalankan perintah dan mendefinisikan:

```indonesian_script
[literal1, literal2, ...];
```

* **[** ... **]** adalah blok untuk mendefinisikannya.
* **literal1**, **literal2** adalah literal ke 1, ke 2, dan seterusnya.

#### Opsi / Opsional
Opsional Tipe (OptionalType) adalah tipe yang memuat kekosongan tipe. Agar apa? Agar memberi opsi masukan, mengembalikan kosong atau berisi dengan tipe yang ada. cara mendefinisikannya adalah:

```indonesian_script
? tipe;
```

* **? ...** adalah blok untuk mendefinisikannya.
* **tipe** adalah tipe yang telah didefinisikan