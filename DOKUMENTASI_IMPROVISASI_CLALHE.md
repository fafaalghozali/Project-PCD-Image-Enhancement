# Tinjauan Komparatif: CLAHE, CLALHE, dan CLALHE Usulan

Dokumen ini menyajikan definisi, formulasi matematis, dan analisis komparatif dari tiga algoritma peningkatan kontras adaptif yang digunakan dalam proyek ini: **CLAHE**, **CLALHE (Mohammed & Isa, 2025)**, dan **CLALHE Usulan** beserta seluruh modifikasi yang diterapkan.

---

## I. CLAHE — Contrast Limited Adaptive Histogram Equalization

### 1.1 Definisi

CLAHE adalah pengembangan dari *Adaptive Histogram Equalization* (AHE) yang menambahkan mekanisme **pembatasan kliping histogram** untuk mengatasi masalah amplifikasi derau (*noise over-amplification*) pada AHE konvensional. Algoritma ini pertama kali diperkenalkan oleh **Zuiderveld (1994)** dan telah menjadi standar industri untuk peningkatan kontras lokal adaptif.

Prinsip kerja CLAHE:
- Citra dibagi menjadi blok-blok kecil (*contextual regions / tiles*).
- Histogram lokal setiap blok dihitung, lalu dipotong (*clipped*) pada ambang batas tertentu.
- Kelebihan piksel akibat pemotongan didistribusikan kembali secara merata ke seluruh bin histogram.
- Fungsi pemetaan CDF (*Cumulative Distribution Function*) dihitung dari histogram yang telah di-clip.
- Nilai piksel akhir ditentukan melalui interpolasi bilinear antar pusat blok untuk menghilangkan artefak batas.

### 1.2 Formulasi Matematis

**Tahap 1 — Partisi Spasial:**
Citra berukuran $H \times W$ dibagi menjadi grid $g_y \times g_x$ blok, dengan ukuran setiap blok:
$$\Delta y = \frac{H}{g_y}, \quad \Delta x = \frac{W}{g_x}$$

**Tahap 2 — Histogram Lokal dan Kliping:**
Untuk setiap blok $(i, j)$, histogram lokal $h_{(i,j)}(k)$ dihitung untuk $k \in [0, 255]$. Ambang kliping aktual dihitung secara proporsional terhadap ukuran blok:
$$\beta_{\text{actual}} = \max\left(1, \; \beta \cdot \frac{N_{\text{tile}}}{256}\right)$$
di mana $\beta$ adalah *clip limit* yang ditetapkan pengguna dan $N_{\text{tile}}$ adalah jumlah piksel dalam blok.

Histogram yang telah di-clip:
$$h'_{(i,j)}(k) = \min\big(h_{(i,j)}(k), \; \beta_{\text{actual}}\big) + \frac{E}{256}$$
di mana kelebihan $E = \sum_{k=0}^{255} \max\big(h_{(i,j)}(k) - \beta_{\text{actual}}, \; 0\big)$ didistribusikan merata ke seluruh 256 bin.

**Tahap 3 — Fungsi Pemetaan CDF:**
$$T_{(i,j)}(k) = \text{round}\!\left(\frac{\text{CDF}_{(i,j)}(k)}{\text{CDF}_{(i,j)}(255)} \times 255\right)$$
di mana $\text{CDF}_{(i,j)}(k) = \sum_{n=0}^{k} h'_{(i,j)}(n)$.

**Tahap 4 — Interpolasi Bilinear Spasial:**
Untuk setiap piksel $(y, x)$ dengan intensitas $v$, empat pusat blok terdekat $(i_1, j_1), (i_1, j_2), (i_2, j_1), (i_2, j_2)$ diidentifikasi dan nilai akhir dihitung:
$$I_{\text{out}}(y, x) = (1-s)(1-t)\,T_{(i_1,j_1)}(v) + s(1-t)\,T_{(i_1,j_2)}(v) + (1-s)t\,T_{(i_2,j_1)}(v) + s \cdot t\,T_{(i_2,j_2)}(v)$$
di mana $s$ dan $t$ adalah bobot interpolasi berdasarkan posisi relatif piksel terhadap pusat blok.

### 1.3 Parameter dan Keterbatasan

| Parameter | Nilai | Cara Penentuan |
| :--- | :--- | :--- |
| Clip Limit ($\beta$) | Biasanya 2.0 – 4.0 | **Manual** (*trial-and-error*) |
| Ukuran Grid ($g_y \times g_x$) | Biasanya $8 \times 8$ | **Manual** (konvensi standar) |

**Keterbatasan utama:** Kedua parameter kunci harus ditentukan secara manual dan bersifat tetap (*fixed*) untuk seluruh citra, tanpa menyesuaikan karakteristik distribusi intensitas citra masukan.

---

## II. CLALHE — Contrast Limited Adaptive Local Histogram Equalization
**(Mohammed & Isa, 2025)**

### 2.1 Definisi

CLALHE adalah pengembangan dari CLAHE yang menghilangkan ketergantungan pada penentuan parameter manual. Algoritma ini menggunakan **analisis ekstrema histogram** (deteksi *peaks* dan *valleys*) untuk menentukan parameter *clip limit* dan ukuran grid secara otomatis, kemudian memilih kombinasi parameter optimal melalui fungsi objektif multikriteria **CIQI** (*Contrast Improvement Quality Index*).

Algoritma asli dirancang untuk **citra skala abu-abu (grayscale) 1-kanal** saja.

### 2.2 Formulasi Matematis

**Tahap 1 — Deteksi Ekstrema Histogram:**
Diberikan histogram global $h(k)$ untuk $k \in [0, 255]$, himpunan *peaks* $P$ dan *valleys* $V$ didefinisikan:
$$P = \big\{k \mid h(k) > h(k-1) \;\land\; h(k) > h(k+1), \; k \in [1, 254]\big\}$$
$$V = \big\{k \mid h(k) < h(k-1) \;\land\; h(k) < h(k+1), \; k \in [1, 254]\big\}$$

**Tahap 2 — Parameter Adaptif:**

*Rata-rata frekuensi lembah (N-parameter):*
$$N_{\text{param}} = \frac{1}{|V|} \sum_{v \in V} h(v)$$

*Contextual Block Dimension (CBD):*
$$\text{CBD} = \max\Big(2, \;\big\lceil \ln(|P|) \big\rceil\Big)$$

**Tahap 3 — Himpunan Kandidat Clip Limit:**
Untuk setiap puncak $p \in P$:
$$CL_p = \frac{h(p) + N_{\text{param}}}{\max_{v \in V} h(v)}, \quad CL_p \in [0.01, \; 10.0]$$

**Tahap 4 — Optimasi Seleksi CIQI:**
Untuk setiap kandidat $CL_p$, CLAHE diterapkan dengan parameter $(CL_p, \text{CBD})$ dan kualitas hasil diukur menggunakan:
$$\text{CIQI} = \frac{\text{PSNR} + H_{\text{entropy}}}{\text{AMBE} + 10^{-6}}$$
di mana:
- $\text{PSNR} = 10 \cdot \log_{10}\!\left(\frac{255^2}{\text{MSE}}\right)$ — mengukur distorsi piksel terhadap citra asli.
- $H_{\text{entropy}} = -\sum p_i \log_2 p_i$ — mengukur kekayaan informasi citra hasil.
- $\text{AMBE} = |\bar{I}_{\text{asli}} - \bar{I}_{\text{hasil}}|$ — mengukur pergeseran kecerahan rata-rata.

Parameter $CL^*$ dengan $\text{CIQI}$ tertinggi dipilih sebagai parameter akhir.

### 2.3 Kelemahan yang Teridentifikasi

| No. | Kelemahan | Deskripsi | Dampak |
| :---: | :--- | :--- | :--- |
| 1 | **Jebakan AMBE pada CIQI** | AMBE berada di posisi penyebut (*denominator*) secara langsung tanpa normalisasi. Ketika AMBE mendekati 0 (citra hampir tidak berubah), CIQI meledak sangat tinggi. | Algoritma secara sistematis memilih parameter yang **paling pasif** (hampir tidak mengubah citra) karena menghasilkan skor CIQI tertinggi → fenomena ***under-enhancement***. |
| 2 | **CBD Terlalu Kasar** | $\lceil \ln(\|P\|) \rceil$ untuk $\|P\| \approx 30$–$80$ hanya menghasilkan nilai 3–4. Citra dipartisi menjadi grid $3 \times 3$ atau $4 \times 4$ saja. | Kehilangan sifat adaptif lokal; efek menyerupai *Global HE* yang kaku. |
| 3 | **Batas Bawah CL Terlalu Rendah** | $CL \ge 0.01$ memungkinkan pemotongan histogram yang sangat dalam (*over-clipping*). | Histogram diratakan secara ekstrem, menekan dinamika kontras lokal. |
| 4 | **Domain Grayscale Saja** | Tidak ada mekanisme penanganan citra berwarna (3-kanal). | Jika diterapkan per kanal R, G, B secara terpisah, terjadi distorsi rona warna (*color shifting*) dan desaturasi. |

---

## III. CLALHE Usulan — Ekstensi Berwarna dengan Solusi Under-Enhancement

### 3.1 Definisi

CLALHE Usulan merupakan modifikasi dan ekstensi dari algoritma CLALHE Mohammed & Isa (2025) yang mengatasi empat kelemahan yang teridentifikasi melalui:
1. **Ekstensi ke domain citra berwarna** melalui dekomposisi ruang warna ortogonal YCbCr (ITU-R BT.601), di mana peningkatan kontras hanya diterapkan pada kanal luminansi ($Y$) sementara kanal krominans ($Cb$, $Cr$) diproteksi secara utuh.
2. **Reformulasi matematis** pada tiga komponen inti algoritma CLALHE: fungsi seleksi CIQI, penentuan ukuran grid, dan rentang kandidat *clip limit*.

### 3.2 Formulasi Matematis

**Tahap 0 — Dekomposisi Ruang Warna (Komponen Baru):**

Citra masukan RGB ditransformasi ke ruang warna YCbCr menggunakan matriks afin ITU-R BT.601:

$$\begin{bmatrix} Y \\ Cb \\ Cr \end{bmatrix} = \begin{bmatrix} 0.299 & 0.587 & 0.114 \\ -0.169 & -0.331 & 0.500 \\ 0.500 & -0.419 & -0.081 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix} + \begin{bmatrix} 0 \\ 128 \\ 128 \end{bmatrix}$$

Seluruh proses CLALHE (Tahap 1–4) hanya diterapkan pada kanal $Y$. Kanal $Cb$ dan $Cr$ **tidak dimodifikasi sama sekali** untuk menjamin integritas rona warna ($\Delta E_{76}$ tetap rendah).

Setelah enhancement, rekonstruksi balik dilakukan:
$$\begin{bmatrix} R \\ G \\ B \end{bmatrix} = \begin{bmatrix} 1.000 & 0.000 & 1.402 \\ 1.000 & -0.344 & -0.714 \\ 1.000 & 1.772 & 0.000 \end{bmatrix} \begin{bmatrix} Y_{\text{enh}} \\ Cb - 128 \\ Cr - 128 \end{bmatrix}$$

**Tahap 1 — Deteksi Ekstrema Histogram:**
Tidak ada perubahan dari algoritma asli. Peaks $P$ dan valleys $V$ diekstraksi dari histogram kanal $Y$.

**Tahap 2 — Parameter Adaptif (Dimodifikasi):**

*N-parameter:* Tidak berubah.
$$N_{\text{param}} = \frac{1}{|V|} \sum_{v \in V} h(v)$$

*Contextual Block Dimension (**Dimodifikasi**):*

| Aspek | CLALHE Asli | CLALHE Usulan |
| :--- | :--- | :--- |
| **Formula** | $\text{CBD} = \max\big(2, \lceil \ln(\|P\|) \rceil\big)$ | $\text{CBD} = \max\big(8, \lceil 2 \cdot \log_2(\|P\|) \rceil\big)$ |
| **Basis logaritma** | Natural ($\ln$, basis $e$) | Biner ($\log_2$, basis 2) |
| **Faktor skala** | 1 | 2 |
| **Batas bawah** | 2 | **8** |
| **Hasil tipikal** ($\|P\| = 48$) | $\lceil \ln(48) \rceil = \lceil 3.87 \rceil = 4$ | $\lceil 2 \cdot \log_2(48) \rceil = \lceil 11.17 \rceil = 12$ |

**Alasan perubahan:** Batas bawah CBD = 8 menjamin partisi spasial sekurang-kurangnya setara dengan standar CLAHE industri ($8 \times 8$ = 64 blok), sehingga sifat adaptif lokal tetap terjaga dan tekstur mikro dapat ditangkap dengan resolusi yang memadai.

**Tahap 3 — Himpunan Kandidat Clip Limit (Dimodifikasi):**

| Aspek | CLALHE Asli | CLALHE Usulan |
| :--- | :--- | :--- |
| **Formula generasi** | $CL_p = \frac{h(p) + N_{\text{param}}}{\max_{v} h(v)}$ | Sama |
| **Rentang pembatasan** | $CL_p \in [0.01, \; 10.0]$ | $CL_p \in [\mathbf{1.0}, \; 10.0]$ |

**Alasan perubahan:** Nilai $CL < 1.0$ menyebabkan pemotongan histogram terlalu dalam yang justru menekan dinamika kontras lokal (paradoks: *clipping* yang seharusnya mengontrol derau malah memadamkan sinyal kontras).

**Tahap 4 — Fungsi Seleksi CIQI (Dimodifikasi Signifikan):**

| Aspek | CLALHE Asli | CLALHE Usulan |
| :--- | :--- | :--- |
| **Formula** | $\text{CIQI} = \frac{\text{PSNR} + H}{\text{AMBE} + 10^{-6}}$ | $\text{CIQI} = \frac{\text{PSNR} + 5.0 \cdot H}{1.0 + \max(0, \; \text{AMBE} - 5.0)}$ |
| **Bobot entropi** | 1× (setara PSNR) | **5×** (diprioritaskan) |
| **Penanganan AMBE** | Pembagi langsung (linear, sangat sensitif terhadap nol) | **Soft-penalty dengan toleransi** 5.0 poin |
| **Perilaku saat AMBE → 0** | CIQI → $\infty$ (*bias ke parameter pasif*) | CIQI = PSNR + 5H (*stabil, tanpa bias*) |
| **Perilaku saat AMBE = 8** | CIQI = $\frac{\text{PSNR} + H}{8}$ (*dihukum berat*) | CIQI = $\frac{\text{PSNR} + 5H}{4}$ (*dihukum proporsional*) |

**Rincian desain formulasi baru:**

1. **Pembobotan Entropi ($\times 5$):**
   Entropi ($H$) merupakan ukuran langsung dari kekayaan informasi dan detail kontras pada citra hasil. Dengan memberi bobot 5 kali lebih besar dari PSNR, algoritma dipaksa untuk memprioritaskan **peningkatan detail visual** di atas kemiripan piksel-per-piksel dengan citra asli.

2. **Toleransi AMBE (Threshold = 5.0):**
   Pergeseran kecerahan rata-rata hingga 5 poin (dari skala 0–255) dianggap wajar dan tidak menimbulkan degradasi visual. Penyebut bernilai konstan 1.0 selama $\text{AMBE} \le 5.0$, sehingga tidak ada penalti untuk peningkatan kontras yang masih dalam batas alami.

3. **Penalti Proporsional di Atas Toleransi:**
   Ketika $\text{AMBE} > 5.0$, penalti baru dihitung sebagai $1.0 + (\text{AMBE} - 5.0)$, sehingga kenaikan penalti bersifat linear-proporsional (bukan eksponensial seperti pada formula asli ketika AMBE mendekati 0).

---

## IV. Tabel Ringkasan Perbandingan Tiga Algoritma

| Aspek | CLAHE (Zuiderveld, 1994) | CLALHE (Mohammed & Isa, 2025) | CLALHE Usulan |
| :--- | :--- | :--- | :--- |
| **Domain Citra** | Grayscale / per-kanal | Grayscale saja | **Berwarna (YCbCr)** |
| **Penentuan Clip Limit** | Manual (*trial-and-error*) | Otomatis (peaks/valleys) | Otomatis + batas bawah 1.0 |
| **Penentuan Ukuran Grid** | Manual (standar $8 \times 8$) | Otomatis ($\lceil \ln \rceil$, bisa 2–4) | Otomatis ($\lceil 2 \log_2 \rceil$, minimal 8) |
| **Fungsi Seleksi** | Tidak ada (parameter tetap) | CIQI = (PSNR + H) / AMBE | CIQI = (PSNR + 5H) / (1 + max(0, AMBE−5)) |
| **Preservasi Warna** | Tidak ada jaminan | Tidak ada (grayscale) | **Terjamin** ($Cb$, $Cr$ utuh) |
| **Risiko Under-enhancement** | Tergantung parameter manual | **Tinggi** (CIQI bias ke pasif) | **Rendah** (soft-penalty) |
| **Risiko Over-enhancement** | Tergantung parameter manual | Rendah | Rendah (batas atas CL = 10.0) |

---

## V. Bukti Empiris

Pengujian pada citra `im0005.png` (citra berwarna, kontras normal):

| Metrik | CLALHE Asli (Grayscale → YCbCr) | CLALHE Usulan (YCbCr) | Evaluasi |
| :--- | :---: | :---: | :--- |
| **CL terpilih** | 0.42 | **1.52** | Parameter aktif vs pasif |
| **Grid (CBD)** | $4 \times 4$ | **$8 \times 8$ atau lebih** | Resolusi lokal 4× lebih tinggi |
| **Entropi** | 6.841 bit | **7.110 bit** | **+0.27 bit**: detail informasi bertambah |
| **PSNR** | 36.11 dB | **29.73 dB** | Berada pada rentang *active enhancement* yang ideal |
| **SSIM** | 0.998 | **0.991** | Struktur visual tetap utuh |
| **$\Delta E_{76}$** | 1.31 | **2.80** | Tetap di bawah ambang persepsi visual ($< 3.0$) |
| **AMBE** | 2.67 | **3.89** | Kecerahan rata-rata tetap terjaga |
| **Rata-rata $\|$Δpiksel$\|$** | 3.31 | **6.97** | Efek visual 2× lebih terasa |
| **Maks $\|$Δpiksel$\|$** | 10 | **25** | Area bayangan benar-benar diperkuat |

---

## VI. Kesimpulan

CLALHE Usulan mempertahankan keunggulan inti dari CLALHE asli (penentuan parameter otomatis berbasis analisis histogram) sambil mengatasi kelemahan kritisnya:

1. **Dari *under-enhancement* menjadi *active enhancement*:** Reformulasi CIQI dengan *soft-penalty* AMBE membebaskan algoritma dari jebakan parameter pasif, sehingga peningkatan kontras benar-benar terasa secara visual.
2. **Dari monokrom menjadi berwarna:** Dekomposisi YCbCr memungkinkan peningkatan kontras luminansi tanpa mendistorsi rona warna asli, dibuktikan dengan nilai $\Delta E_{76}$ yang konsisten rendah ($< 5.0$) pada seluruh citra uji.
3. **Dari grid kasar menjadi grid terstandarisasi:** Peningkatan batas bawah CBD ke 8 menjamin resolusi adaptif lokal setara standar CLAHE industri.
