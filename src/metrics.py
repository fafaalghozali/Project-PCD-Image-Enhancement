"""
Modul Metrik Evaluasi Kualitas Citra Analitis
Mengimplementasikan metrik kualitas objektif:
- Peak Signal-to-Noise Ratio (PSNR)
- Entropi Informasi Shannon
- Absolute Mean Brightness Error (AMBE)
- Structural Similarity Index (SSIM)
- Selisih Warna Delta E (CIE 1976)
"""

import math
import numpy as np
from .color_space import rgb_to_gray


def compute_entropy(img: np.ndarray) -> float:
    """Entropi Informasi Shannon H = - sum(p_i * log2(p_i)) secara vektorisasi."""
    hist = np.bincount(img.flatten(), minlength=256).astype(np.float64)
    total = hist.sum()
    if total == 0:
        return 0.0
    p = hist / total
    nz = p[p > 0]
    return -float(np.sum(nz * np.log2(nz)))


def compute_psnr(a: np.ndarray, b: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio (PSNR) berbasis Mean Squared Error (MSE)."""
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64))**2)
    return 10.0 * math.log10(255.0**2 / mse) if mse > 0 else 100.0


def compute_ambe(a: np.ndarray, b: np.ndarray) -> float:
    """Absolute Mean Brightness Error: |mu_a - mu_b|."""
    return float(abs(np.mean(a.astype(np.float64)) - np.mean(b.astype(np.float64))))


def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """Structural Similarity Index (SSIM) analitis pada intensitas luminansi."""
    if len(img1.shape) == 3:
        a = rgb_to_gray(img1).astype(np.float64)
    else:
        a = img1.astype(np.float64)

    if len(img2.shape) == 3:
        b = rgb_to_gray(img2).astype(np.float64)
    else:
        b = img2.astype(np.float64)

    mu_a, mu_b = a.mean(), b.mean()
    var_a, var_b = a.var(), b.var()
    cov = ((a - mu_a) * (b - mu_b)).mean()

    C1, C2 = (0.01 * 255.0)**2, (0.03 * 255.0)**2
    return float(((2.0 * mu_a * mu_b + C1) * (2.0 * cov + C2)) /
                 ((mu_a**2 + mu_b**2 + C1) * (var_a + var_b + C2)))


def delta_e_76(img1_rgb: np.ndarray, img2_rgb: np.ndarray) -> float:
    """
    Perhitungan matematis selisih warna Delta E (CIE 1976):
    RGB -> CIEXYZ -> CIELAB -> Euclidean Distance.
    """
    def rgb_to_lab(img):
        img_norm = img.astype(np.float64) / 255.0
        R, G, B = img_norm[:, :, 0], img_norm[:, :, 1], img_norm[:, :, 2]

        def f_gamma(t):
            return np.where(t > 0.04045, ((t + 0.055) / 1.055)**2.4, t / 12.92)

        R, G, B = f_gamma(R), f_gamma(G), f_gamma(B)
        X = 0.4124564 * R + 0.3575761 * G + 0.1804375 * B
        Y = 0.2126729 * R + 0.7151522 * G + 0.0721750 * B
        Z = 0.0193339 * R + 0.1191920 * G + 0.9503041 * B

        Xn, Yn, Zn = 0.95047, 1.00000, 1.08883

        def f_cielab(t):
            return np.where(t > 0.008856, t**(1.0 / 3.0), 7.787 * t + 16.0 / 116.0)

        fx, fy, fz = f_cielab(X / Xn), f_cielab(Y / Yn), f_cielab(Z / Zn)
        L = 116.0 * fy - 16.0
        a = 500.0 * (fx - fy)
        b = 200.0 * (fy - fz)
        return L, a, b

    L1, a1, b1 = rgb_to_lab(img1_rgb)
    L2, a2, b2 = rgb_to_lab(img2_rgb)
    return float(np.mean(np.sqrt((L1 - L2)**2 + (a1 - a2)**2 + (b1 - b2)**2)))
