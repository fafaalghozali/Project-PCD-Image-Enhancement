"""
Modul Pipeline Peningkatan Kontras Citra (Metode Pembanding & Usulan)
Mencakup:
- CLAHE_RGB (Pembanding 1)
- CLAHE_YCbCr (Pembanding 2)
- CLALHE_gray_recolor (Pembanding 3)
- CLALHE_YCbCr (Metode Usulan)
"""

import numpy as np
from .color_space import rgb_to_ycbcr, ycbcr_to_rgb, rgb_to_gray, gray_to_rgb
from .clahe_math import pure_clahe_math
from .clalhe import clalhe_gray


def clahe_rgb(img_rgb: np.ndarray) -> np.ndarray:
    """Metode Pembanding 1: CLAHE konvensional pada kanal R, G, B secara independen."""
    r = pure_clahe_math(img_rgb[:, :, 0], clip_limit=2.0, grid_size=(8, 8))
    g = pure_clahe_math(img_rgb[:, :, 1], clip_limit=2.0, grid_size=(8, 8))
    b = pure_clahe_math(img_rgb[:, :, 2], clip_limit=2.0, grid_size=(8, 8))
    return np.stack([r, g, b], axis=-1)


def clahe_ycbcr(img_rgb: np.ndarray) -> np.ndarray:
    """Metode Pembanding 2: CLAHE konvensional hanya pada kanal Luminansi Y."""
    ycbcr = rgb_to_ycbcr(img_rgb)
    y_channel = np.clip(np.round(ycbcr[:, :, 0]), 0, 255).astype(np.uint8)
    y_enh = pure_clahe_math(y_channel, clip_limit=2.0, grid_size=(8, 8))
    ycbcr[:, :, 0] = y_enh.astype(np.float64)
    return ycbcr_to_rgb(ycbcr)


def clalhe_gray_recolor(img_rgb: np.ndarray) -> np.ndarray:
    """Metode Pembanding 3: CLALHE grayscale yang diduplikasi ke kanal warna."""
    gray = rgb_to_gray(img_rgb)
    gray_enh = clalhe_gray(gray)
    return gray_to_rgb(gray_enh)


def clalhe_ycbcr(img_rgb: np.ndarray) -> np.ndarray:
    """
    METODE USULAN:
    1. Dekomposisi R'G'B' -> Y'CbCr
    2. Peningkatan kontras adaptif CLALHE HANYA pada kanal Luminansi Y
    3. Preservasi mutlak kanal Krominans (Cb, Cr) untuk mempertahankan rona warna
    4. Rekonstruksi kembali ke domain R'G'B'
    """
    ycbcr = rgb_to_ycbcr(img_rgb)
    y_channel = np.clip(np.round(ycbcr[:, :, 0]), 0, 255).astype(np.uint8)
    y_enh = clalhe_gray(y_channel)
    ycbcr[:, :, 0] = y_enh.astype(np.float64)
    return ycbcr_to_rgb(ycbcr)


AVAILABLE_METHODS = {
    "CLAHE_RGB": clahe_rgb,
    "CLAHE_YCbCr": clahe_ycbcr,
    "CLALHE_gray_recolor": clalhe_gray_recolor,
    "CLALHE_YCbCr": clalhe_ycbcr,
}
