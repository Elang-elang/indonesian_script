# CONTEXT.md – Panduan untuk AI Agent

## Tujuan Utama
Kamu adalah AI agent yang bertanggung jawab untuk menjalankan perintah terminal secara aman, mendeteksi error, dan memperbaiki kode yang rusak. Fokus utama saat ini adalah pada perintah `is` atau `cs` serta file `interpreter.py` dan `transformer.py`.

## Aturan Dasar Eksekusi Perintah

1. **Jalankan perintah** `is` atau `cs` di terminal.
   - Jika kedua perintah tersedia, prioritaskan `is`.
   - Jika hanya satu yang tersedia, gunakan yang itu.
   - Jika tidak ada, laporkan dan tanyakan alternatif.

2. **Setelah menjalankan**, periksa output:
   - **Tidak ada error** (exit code 0) → lanjut ke langkah 3.
   - **Ada error** (exit code non-zero) → catat pesan error, lalu langsung menuju **Proses Perbaikan** (lihat bagian bawah).

3. **Jika tidak ada error**, jalankan perintah beserta subcommand (jika ada).
   - Contoh: `is --list` atau `cs status`.
   - Cek ulang apakah subcommand menghasilkan error.

4. **Setiap kali error muncul** (baik dari perintah utama maupun subcommand), kamu WAJIB:
   - Menampilkan pesan error secara jelas.
   - Menjelaskan penyebab error (analisis sementara).
   - Memperbaiki file yang berkaitan: **`interpreter.py`**, **`transformer.py`**, dan file lain yang disebutkan dalam error atau yang relevan.
   - Setelah perbaikan, ulangi langkah 1–3 hingga tidak ada error.

## File yang Sudah Diketahui Benar
Beberapa file dalam proyek ini sudah dalam kondisi benar dan TIDAK perlu diubah kecuali ada error yang secara langsung mengarah ke file tersebut. Jika error tidak menyebutkan file lain, fokus perbaikan hanya pada:
- `interpreter.py`
- `transformer.py`
- File lain yang disebutkan dalam pesan error (misalnya `parser.py`, `lexer.py`, dll.)

## Prosedur Perbaikan (Wajib Diikuti)

Saat menemukan error:

1. **Baca dan pahami error** – identifikasi baris, tipe error (SyntaxError, AttributeError, ImportError, dll.), dan file penyebab.
2. **Jelaskan mengapa error itu terjadi** dalam bahasa yang lugas, misal:
   - "Error NameError: name 'x' not defined terjadi karena variabel x belum didefinisikan di fungsi parse() di interpreter.py baris 42."
3. **Perbaiki file** dengan mengedit konten yang sesuai. Gunakan tool edit file yang tersedia (write, replace, patch).
4. **Simpan perubahan** dan **jalankan ulang** perintah `is` atau `cs` beserta subcommand-nya.
5. **Konfirmasi** bahwa error sudah hilang. Jika masih ada error lain, ulangi siklus ini.

## Contoh Skenario yang Mungkin Terjadi

- **Error SyntaxError di `interpreter.py`** → perbaiki tanda kurung, indentasi, atau sintaks lain.
- **Error ModuleNotFoundError** → cek apakah ada impor modul yang salah atau kurang, perbaiki dengan impor yang benar.
- **Error terkait logika transformasi di `transformer.py`** → perbaiki fungsi transformasi, pastikan input/output sesuai tipe data yang diharapkan.

## Larangan
- Jangan mengubah file yang sudah benar tanpa alasan yang jelas dari error.
- Jangan menebak-nebak perbaikan tanpa membaca pesan error terlebih dahulu.
- Jangan mengabaikan error dengan sekadar melewatkan langkah pengecekan.

## Tujuan Akhir
Setelah semua error diperbaiki, perintah `is` atau `cs` beserta subcommand-nya harus berjalan tanpa error. Kamu akan melaporkan **"Semua perintah berhasil dijalankan tanpa error. File interpreter.py, transformer.py, dan file terkait telah diperbaiki."**

--- 
Mulai sekarang, jalankan langkah-langkah di atas secara otomatis setiap kali kamu diminta menjalankan perintah kompleks dalam proyek ini.
