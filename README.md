# Tucil 1 IF2211 – Colored Queens

Repositori ini berisi implementasi penyelesaian masalah *Colored Queens* untuk mata kuliah IF2211 Strategi Algoritma.

## Deskripsi Singkat

Diberikan sebuah papan berukuran $N \times N$ yang setiap selnya berisi sebuah huruf (warna). Tujuannya adalah menempatkan tepat satu ratu untuk setiap warna sehingga:

- Tidak ada dua ratu pada baris yang sama.
- Tidak ada dua ratu pada kolom yang sama.
- Tidak ada dua ratu yang saling menyerang secara diagonal bersebelahan.
- Setiap warna hanya boleh memiliki **paling banyak satu** ratu.

Papan dibaca dari file teks, dan solusi (jika ada) dituliskan kembali ke file test `*_solution.txt` di folder yang sama dengan file input, serta pengguna bisa menyimpan output yang berupa image pada folder output.

## Struktur Folder

- `src/`
  - [`src/main.py`](src/main.py): entry point program (menjalankan GUI).
  - [`src/gui.py`](src/gui.py): implementasi antarmuka grafis dengan Tkinter.
  - [`src/Board.py`](src/Board.py): representasi papan, pembacaan file, serta algoritma pencarian.
  - [`src/QueenManager.py`](src/QueenManager.py): pengelolaan posisi ratu.
- `test/`: berisi contoh kasus uji dalam format `.txt` dan file solusi `*_solution.txt`.
- `output/`: folder tujuan penyimpanan gambar solusi (`solution.png`) dari GUI.
- `bin/`: (opsional) skrip untuk menjalankan program dengan satu perintah.
- `README.md`: dokumentasi proyek.

## Ketergantungan

- Python 3.x
- Tkinter (biasanya sudah ter-install bersama Python)
- (Opsional) Pillow (`PIL`) untuk menyimpan gambar solusi ke `.png`:
  
  ```bash
  pip install pillow
  ```

## Cara Menjalankan

### 1. Menjalankan GUI

Dari root proyek:

```bash
python src/main.py
```

Atau, menggunakan skrip di `bin/`

- Windows:

  ```bash
  bin\run.bat
  ```

- Linux/macOS:

  ```bash
  chmod +x bin/run.sh
  ./bin/run.sh
  ```

### 2. Penggunaan GUI

1. Tekan tombol **Browse…** untuk memilih file papan (`.txt`) di folder `test/` atau lokasi lain.
2. Tekan:
   - **Solve Exhaustive** untuk menjalankan pencarian *exhaustive search*.
   - **Solve Backtrack** untuk menjalankan pencarian *backtracking*.
3. Jika solusi ditemukan:
   - Papan dan posisi ratu akan ditampilkan.
   - File solusi akan disimpan otomatis di file `*_solution.txt` pada folder yang sama dengan input.
4. Tombol lain:
   - **Clear Board**: menghapus ratu dan mengembalikan papan ke kondisi awal.
   - **Save Image**: menyimpan gambar papan+solusi ke `output/solution.png` (atau `solution.ps` jika Pillow tidak terpasang).

## Format File Masukan

- Berkas teks berisi tepat $N$ baris.
- Tiap baris berisi tepat $N$ karakter (tanpa spasi).
- Setiap karakter melambangkan sebuah warna (misal `A`, `B`, `C`, …).
- Jumlah warna unik harus sama dengan $N$.

Contoh (`test/test.txt`):

```txt
AAABBCCCD
ABBBBCECD
ABBBDCECD
AAABDCCCD
BBBBDDDDD
FGGGDDHDD
FGIGDDHDD
FGIGDDHDD
FGGGDDHHH
```

## Algoritma

Implementasi tersedia di [`src/Board.py`](src/Board.py):

- **Exhaustive Search**
  - Mencoba semua kombinasi kemungkinan posisi ratu untuk setiap warna.
  - Menggunakan fungsi `exhaustiveSearch` dan `moveQueen` untuk enumerasi kombinasi.
- **Backtracking**
  - Membangun solusi baris demi baris, mundur (*backtrack*) jika terjadi konflik.
  - Menggunakan fungsi `backtrack` untuk rekursi penempatan ratu.

Keduanya menggunakan:

- `checkDiagonal` untuk memastikan tidak ada dua ratu yang saling menyerang secara diagonal.
- `validChecker` untuk memeriksa keabsahan susunan ratu pada papan.

## Penulisan Solusi

Jika solusi ditemukan, fungsi `writeSolutionToFile` di [`src/Board.py`](src/Board.py) akan menulis:

- Metode yang digunakan (`exhaustive` atau `backtrack`).
- Waktu pencarian dalam milidetik.
- Representasi papan dengan `#` sebagai posisi ratu.

Contoh (`test/test_solution.txt`):

```txt
Metode: exhaustive
Waktu pencarian: 212585.8319 ms
AAABBCC#D
ABBB#CECD
...
```

## Lisensi

Tidak ada lisensi khusus; digunakan untuk keperluan akademik mata kuliah IF2211.
