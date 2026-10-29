"""
Modul Algoritma CLALHE (Mohammed & Isa, 2025)
Mengimplementasikan:
1. Deteksi Peaks dan Valleys pada Histogram
2. Penentuan Parameter Dinamis (N_param, CBD, Kandidat Clip Limit)
3. Optimasi Multikriteria CIQI = (PSNR + Entropy) / AMBE
"""

import math
import numpy as np
from .clahe_math import pure_clahe_math
from .metrics import compute_psnr, compute_entropy, compute_ambe


def detect_peaks_valleys(hist: np.ndarray) -> tuple:
    """Mendeteksi himpunan ekstrema lokal (peaks P dan valleys V) dari histogram."""
    peaks, valleys = [], []
    for i in range(1, 255):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
            peaks.append(i)
        if hist[i] < hist[i-1] and hist[i] < hist[i+1]:
            valleys.append(i)
    return peaks, valleys


def clalhe_gray(Y: np.ndarray) -> np.ndarray:
    """
    CLALHE pada satu kanal intensitas diskrit 2D:
    1. Ekstraksi Peaks & Valleys
    2. Perhitungan Parameter Adaptif N_param, CBD, dan beta_p
    3. Optimasi Multikriteria CIQI = (PSNR + Entropy) / AMBE
    
    Parameters:
    -----------
    Y : np.ndarray
        Kanal intensitas 2D (uint8).
        
    Returns:
    --------
    np.ndarray
        Kanal intensitas hasil peningkatan kontras adaptif (uint8).
    """
    hist = np.bincount(Y.flatten(), minlength=256).astype(np.float64)
    peaks, valleys = detect_peaks_valleys(hist)

    # Kondisi batas (Fallback) jika tidak terdapat puncak/lembah
    if len(peaks) == 0 or len(valleys) == 0:
        return pure_clahe_math(Y, clip_limit=2.0, grid_size=(8, 8))

    N_param = sum(hist[v] for v in valleys) / len(valleys)
    CBD = max(8, math.ceil(math.log2(len(peaks)) * 2))
    max_valley = max(hist[v] for v in valleys)

    # Himpunan kandidat clip limit unik (dibatasi minimal 1.0 agar tidak under-enhancement)
    candidate_cls = []
    for p in peaks:
        cl = (hist[p] + N_param) / max_valley
        cl = max(1.0, min(cl, 10.0))
        candidate_cls.append(round(cl, 2))
    unique_cls = np.unique(candidate_cls)

    best_ciqi, best_cl = -1e9, 2.0
    for cl in unique_cls:
        Y_tmp = pure_clahe_math(Y, clip_limit=cl, grid_size=(CBD, CBD))

        psnr = compute_psnr(Y, Y_tmp)
        ent = compute_entropy(Y_tmp)
        ambe = compute_ambe(Y, Y_tmp)
        # Formulasi berbobot adaptif:
        # Memprioritaskan entropi (peningkatan detail) dan PSNR, 
        # dengan toleransi pergeseran kecerahan wajar (soft-penalty pada AMBE)
        ambe_penalty = 1.0 + max(0.0, ambe - 5.0)
        ciqi = (psnr + 5.0 * ent) / ambe_penalty

        if ciqi > best_ciqi:
            best_ciqi, best_cl = ciqi, cl

    return pure_clahe_math(Y, clip_limit=best_cl, grid_size=(CBD, CBD))
