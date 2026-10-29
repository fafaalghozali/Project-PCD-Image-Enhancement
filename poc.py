"""
================================================================================
PROOF OF CONCEPT (PoC) TUGAS AKHIR:
Ekstensi Matematis CLALHE (Mohammed & Isa, 2025) ke Domain Citra Berwarna
melalui Dekomposisi Ruang Warna Ortogonal YCbCr (ITU-R BT.601)

ARSITEKTUR MODULAR:
Kode telah dipisah ke dalam paket 'src/' untuk mempermudah pemeliharaan:
- src/color_space.py : Transformasi matriks R'G'B' <-> Y'CbCr dan Grayscale (ITU-R BT.601).
- src/clahe_math.py  : Engine CLAHE analitis murni (partisi, clipping, CDF, interpolasi bilinear).
- src/clalhe.py      : Algoritma CLALHE adaptif (deteksi peaks/valleys & optimasi CIQI).
- src/enhancement.py : Pipeline metode pembanding & metode usulan.
- src/metrics.py     : Metrik evaluasi kualitas citra (PSNR, SSIM, AMBE, Entropy, Delta E 76).
- main.py            : Skrip eksekusi eksperimen utama dengan dukungan CLI.
================================================================================
"""

from main import main, run_experiment, process_image
from src import (
    bgr_to_rgb,
    rgb_to_bgr,
    rgb_to_ycbcr,
    ycbcr_to_rgb,
    rgb_to_gray,
    gray_to_rgb,
    pure_clahe_math,
    clalhe_gray,
    detect_peaks_valleys,
    clahe_rgb,
    clahe_ycbcr,
    clalhe_gray_recolor,
    clalhe_ycbcr,
    AVAILABLE_METHODS,
    compute_psnr,
    compute_ssim,
    compute_ambe,
    compute_entropy,
    delta_e_76,
)

if __name__ == "__main__":
    main()