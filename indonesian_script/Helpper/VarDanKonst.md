## Variabel & Konstanta
Dalam ada variabel untuk menyimpan data atau isian agar lebih mudah dikelola, begitu juga di indonesian_script. indonesian_script ada pernyataan untuk mendeklarasikan variabel dan konstanta (variabel yang bernilai tetap) dengan cara dan penggunaannya masing-masing. Ada beberapa pernyataan pada indonesian_script untuk menyatakan variabel yaitu sebagai berikut:

### Variabel Umun
Variabel umum adalah variabel yang umum ditemukan serta sering digunakan, penggunaannya sangat fleksibel dan mudah dikelola. Contoh penerapannya:

```indonesian_script
var[tipe] nama = isi;
```

* **var* adalah kata kuncinya.
* **var[** ... **]** ... **=** ... **;** format untuk mendeklarasikannya.
* **tipe**: adalah tipe dari variabel itu.
* **nama**: adalah nama variabel.
* **isi**: adalah isi dari variabel tersebut.

saat membuat variabel, mungkin ada yang tidak ingin diisi dahulu isiannya atau memang tidak diisikan dulu. dengan cara sebagai berikut:

```indonesian_script
def[tipe] nama;
```
Maka akan membuat **nama** memuat isian bawaannya sesuai tipe-nya

* **def* adalah kata kuncinya.
* **def[** ... **]** ... **;** format untuk mendeklarasikannya.
* **tipe**: adalah tipe dari variabel itu.
* **nama**: adalah nama variabel.

Adapun saat kalian ingin pengisian ulang variabel-nya dengan cara:
```indonesian_script
nama = isi;
```
* ... **=** ... **;** format untuk mendeklarasikannya.
* **nama**: adalah nama variabel.
* **isi**: adalah isi dari variabel tersebut.

> catatan: *harus sesuai isian harus sesuai tipe, jikalau tidak maka akan galat*

### Konstanta Final
Umumnya variabel mudah dikelola namun jika salah sedikit saja saat pengelolaannya akan ada kesalahan yang fatal, disinilah konstanta final diciptakan. variabel konstanta final akan mengunci isiannya agar suatu saat nanti jika ada kesalahan saat pengelolaannya isian akan memunculkan kegalatan yang jelas dan mudah untuk diketahui. adapun cara penerapannya sebagai berikut:

```indonesian_script
final[tipe] nama = isi;
```

* **final** adalah kata kuncinya.
* **final[** ... **]** ... **=** ... **;** format untuk mendeklarasikannya.
* **tipe**: adalah tipe dari variabel itu.
* **nama**: adalah nama variabel.
* **isi**: adalah isi dari variabel tersebut.

### Variabel Alias
Variabel alias adalah bagian variabel yang memuat alias. Saat anda mendeklarasikan dengan alias ini, maka **HANYA** nama saja yang berbeda. Mengapa demikian? Karena sejatinya mendeklarasikan ulang atau mengaliaskan variabel dengan menggunakan cara-cara sebelumnya, lokasi dari alamat penyimpanan itu akan berubah sesuai dengan isi dan tipe isiannya. Ini adalah cara yang baik untuk mengaliaskan variabel, berikut caranya:

```indonesian_script
alias[nama_sebelumnya] sebagai nama_sesudahnya;
```

* **alias* dan **sebagai** adalah kata kuncinya.
* **alias[** ... **] sebagai** ... **;** format untuk mendeklarasikannya.
* **nama_sebelumnya**: adalah nama variabel dari nama variabel yang ingin di aliaskan.
* **nama_sesudahnya**: adalah nama untuk mengaliaskannya.

> catatan: *alias akan benar-benae mengaliaskan variabel dengan mengubah namanya menjadi yang diinginkan, tidak termasuk dengan lokasi penyimpanannya*