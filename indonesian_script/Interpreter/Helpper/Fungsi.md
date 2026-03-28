## Fungsi
Saat anda ingin membuat kode, pasti ingin menyimpan dan tidak membuat ulang lagi kodenya. Fungsi merupakan blok kode yang dapat dipanggil ulang berkali-kali tanpa membuat ulang. Fungsi terdiri dari beberapa bagian yaitu: parameter, nilai kembali dan blok fungsi. dengan contoh kode sebagai berikut:

```indonesian_script
fungsi[tipe_nilai_kembali] nama_fungsi(argumen){
    pernyataan
}
```

* **tipe_nilai_kembali** adalah tipe dari nilai kembali.
* **nama_fungsi** adalah nama fungsnya.
* **parameter** adalah parameternya.
* **pernyataan** adalah pernyataan-pernyataannya.
* **fungsi[** ... **]** ...**(** ... **){** ... **}** adalah format pernyataan

### Parameter
Mungkin fungsi memerlukan masukan untuk membuat pernyataan lebih fleksibel. Parameter terdiri dari beberapa argumen dengan menyatakan sebagai berikut:

```indonesian_script
(argumen1, argumen2, ...)
```

* **(** ... **)** adalah tempat mendeklarasikan parameternya.
* **argumen1**, **argumen2** adalah dari argumennya.
* ... dan seterusnya

Adapun cara mendeklarasikan argumen-argumennya, dengan cara:
```indonesian_script
tipe argumen
// atau
tipe argumen = isian_bawaan
```

* **tipe**: adalah tipe dari argumennya dan bersifat wajib.
* **argumen** adalah nama dari argumennya.
* **isian_bawaan** adalah isian bawaan dari argumennya jika argumen tersebut tidak di isikan. Serta bersifat opsional.
* **tipe[** ... **]** ... **=** ... adalah format untuk mendeklarasikan

### Nilai Kembali
Nilai kembali adalah nilai yang di kembalikan dengan pernyataan **kembalikan{ ekspresi };** jika tidak sesuai dengan tipe kembali maka akan galat. bawaannya adalah *kosong*.

## Dekorator
Ada kalanya sebuah fungsi memerlukan masukan fungsi yang benar-benae fungsi. Dekorator adalah sebuah pernyataan untuk membuat memasukan masukan fungsi agar lebih mudah saat diperlukan. contoh penerapannya:

```indonesian_script
#[nama_fungsi_yang_dipanggil(parameter)];
fungsi[...] ...(...){...}
```

* **nama_fungsi_yang_dipanggil** adalah nama fungsi yang memerlukan masukan serta yang diinginkan.
* **parameter** adalah parameter untuk mengisi parameter lainnya (opsional). jika tidak ada, maka bawaannya adalah fungsi yang meminta masukan akan langsung dimasukan
* **#[** ... **]** adalah format dari pernyataan.

```indonesian_script
// kasus 1
#[pemanggil];
fungsi[kekosongan] dipanggil(){} 

// seperti
fungsi[kekosongan] dipanggil(){}
pemanggil(dipanggil);



// kasus 2
#[pemanggil(parameter)];
fungsi[kekosongan] dipanggil(){}

// seperti
fungsi[kekosongan] dipanggil(){}
pemanggil(parameter, dipanggil);
```