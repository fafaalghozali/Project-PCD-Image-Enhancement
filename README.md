# CLALHE-YCbCr: Peningkatan Kontras Citra Berwarna Berbasis CLALHE pada Domain YCbCr

> Ekstensi Matematis Algoritma CLALHE (Mohammed & Isa, 2025) ke Domain Citra Berwarna
> melalui Dekomposisi Ruang Warna Ortogonal YCbCr (ITU-R BT.601)

---

## Deskripsi Singkat

Proyek ini mengimplementasikan dan membandingkan empat metode peningkatan kontras citra (*contrast enhancement*) menggunakan **NumPy murni** (tanpa ketergantungan pada fungsi pengolahan citra OpenCV). Metode utama yang diusulkan adalah **CLALHE-YCbCr**, yang mengekstensi algoritma CLALHE grayscale ke domain citra berwarna melalui dekomposisi ruang warna YCbCr, dengan reformulasi fungsi seleksi parameter untuk mengatasi fenomena *under-enhancement*.

**Catatan:** OpenCV (`cv2`) hanya digunakan untuk membaca dan menulis file gambar ke disk (`cv2.imread` / `cv2.imwrite`). Seluruh komputasi pengolahan citra (transformasi warna, histogram, clipping, CDF, interpolasi bilinear, metrik evaluasi) diimplementasikan secara analitis murni menggunakan NumPy.

---

## Metode yang Dibandingkan

| No. | Metode | Deskripsi |
| :---: | :--- | :--- |
| 1 | **CLAHE RGB** | CLAHE konvensional diterapkan secara independen pada kanal R, G, B |
| 2 | **CLAHE YCbCr** | CLAHE konvensional hanya pada kanal Luminansi Y (Cb, Cr utuh) |
| 3 | **CLALHE Gray Recolor** | CLALHE adaptif pada grayscale, diduplikasi ke 3 kanal |
| 4 | **CLALHE YCbCr** *(Usulan)* | CLALHE adaptif pada kanal Y di domain YCbCr, Cb & Cr diproteksi utuh |

---

## Struktur Proyek

```
ProjectPCD/
├── poc.py                          # Entry-point kompatibel (memanggil main.py)
├── main.py                         # Runner eksperimen utama + CLI
├── src/
│   ├── __init__.py                 # Facade paket (ekspor semua fungsi publik)
│   ├── color_space.py              # Transformasi warna: RGB ↔ YCbCr, RGB ↔ Gray (ITU-R BT.601)
│   ├── clahe_math.py               # Engine inti CLAHE (partisi, clipping, CDF, interpolasi bilinear)
│   ├── clalhe.py                   # Algoritma CLALHE adaptif (peaks/valleys, CIQI, optimasi parameter)
│   ├── enhancement.py              # Pipeline 4 metode pembanding
│   └── metrics.py                  # Metrik evaluasi: PSNR, SSIM, AMBE, Entropy, Delta E 76
├── dataset/                        # Folder citra masukan (USC-SIPI + custom)
├── hasil/                          # Folder output: citra hasil + CSV rekap metrik
├── DOKUMENTASI_IMPROVISASI_CLALHE.md   # Dokumentasi teknis perbandingan CLAHE vs CLALHE vs Usulan
└── penjelasan_arsitektur.md            # Diagram arsitektur & alur eksekusi program
```

---

## Persyaratan Sistem

- **Python** 3.10+
- **NumPy**
- **OpenCV** (`opencv-python`) — hanya untuk disk I/O

### Instalasi Dependensi

```bash
pip install numpy opencv-python
```

---

## Cara Menjalankan

### Eksperimen Lengkap (Seluruh Dataset)

```bash
python main.py
```

Secara default, program akan:
1. Membaca semua citra dari folder `dataset/`
2. Memproses setiap citra dengan 4 metode enhancement
3. Menghitung 5 metrik evaluasi per metode
4. Menyimpan citra hasil ke folder `hasil/`
5. Menyimpan rekap metrik ke file CSV di `hasil/`

### Menentukan Folder Dataset & Output Kustom

```bash
python main.py --dataset path/ke/folder/citra --output path/ke/folder/hasil
```

### Via poc.py (Kompatibilitas)

```bash
python poc.py
```

---

## Metrik Evaluasi

Program menghitung 5 metrik kualitas citra objektif:

| Metrik | Mengukur | Terbaik Bila |
| :--- | :--- | :--- |
| **PSNR** (dB) | Distorsi piksel terhadap citra asli | Tinggi (↑) |
| **SSIM** | Kemiripan struktural (luminansi, kontras, tekstur) | Mendekati 1 (↑) |
| **Delta E** (ΔE₇₆) | Perbedaan warna perseptual di ruang CIELAB | Rendah (↓) |
| **Entropy** (bit) | Kekayaan informasi / detail citra hasil | Tinggi (↑) |
| **AMBE** | Pergeseran kecerahan rata-rata | Mendekati 0 (↓) |

---

## Contoh Output

### Tabel Evaluasi (Konsol)

```
======================================================================================================
Image        Method                    PSNR    SSIM   DeltaE  Entropy    AMBE  Time(s)
======================================================================================================
im0005       CLAHE_RGB                25.97  0.9902     9.01    7.118    5.32     0.01
im0005       CLAHE_YCbCr              27.70  0.9854     3.48    7.184    4.77     0.01
im0005       CLALHE_gray_recolor      15.16  0.9908    33.20    7.114    7.93     0.13
im0005       CLALHE_YCbCr             29.73  0.9909     2.80    7.110    3.89     0.17
```

### File Output

- Citra visual: `hasil/{nama_citra}_{nama_metode}.png`
- Rekap CSV: `hasil/hasil_evaluasi_{timestamp}.csv`

---

## Keunggulan Metode Usulan (CLALHE YCbCr)

Dibandingkan metode pembanding, CLALHE YCbCr secara konsisten menunjukkan:

1. **Preservasi warna terbaik** — Nilai ΔE₇₆ sangat rendah (< 5.0) karena kanal krominans (Cb, Cr) tidak dimodifikasi
2. **Pergeseran kecerahan minimal** — AMBE terjaga rendah tanpa mengorbankan peningkatan detail
3. **Struktur visual utuh** — SSIM sangat tinggi (> 0.98) karena enhancement bersifat natural
4. **Penentuan parameter otomatis** — Clip limit dan ukuran grid ditentukan secara adaptif berdasarkan analisis histogram

---

## Dokumentasi Teknis

Untuk penjelasan lengkap mengenai formulasi matematis, perbandingan CLAHE vs CLALHE vs CLALHE Usulan, serta rincian improvisasi yang diterapkan, lihat:

- **[DOKUMENTASI_IMPROVISASI_CLALHE.md](DOKUMENTASI_IMPROVISASI_CLALHE.md)** — Tinjauan komparatif lengkap ketiga algoritma
- **[penjelasan_arsitektur.md](penjelasan_arsitektur.md)** — Arsitektur modular & diagram alur eksekusi

---

## Dataset

Proyek ini menggunakan citra uji dari **USC-SIPI Image Database** (University of Southern California, Signal and Image Processing Institute) serta citra custom tambahan. Citra uji ditempatkan di folder `dataset/` dengan format yang didukung: `.tiff`, `.tif`, `.ppm`, `.png`, `.jpg`, `.jpeg`.

---

## Referensi

1. Mohammed, I. M., & Isa, N. A. M. (2025). *Contrast Limited Adaptive Local Histogram Equalization (CLALHE)*. — Algoritma dasar yang diekstensikan dalam proyek ini.
2. Zuiderveld, K. (1994). *Contrast Limited Adaptive Histogram Equalization*. Graphics Gems IV, Academic Press. — Algoritma CLAHE asli.
3. ITU-R BT.601. *Studio Encoding Parameters of Digital Television for Standard 4:3 and Wide-Screen 16:9 Aspect Ratios*. — Standar transformasi ruang warna YCbCr.

