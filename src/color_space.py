"""
Modul Transformasi Ruang Warna Analitis Murni (ITU-R BT.601)
Dibuat dengan NumPy murni tanpa ketergantungan pada cv2.cvtColor.
"""

import numpy as np

# Matriks Transformasi Maju: R'G'B' -> Y'CbCr (ITU-R BT.601)
MAT_RGB2YCBCR = np.array([
    [ 0.299000,  0.587000,  0.114000],
    [-0.168736, -0.331264,  0.500000],
    [ 0.500000, -0.418688, -0.081312]
], dtype=np.float64)

# Matriks Transformasi Balik: Y'CbCr -> R'G'B'
MAT_YCBCR2RGB = np.array([
    [1.000000,  0.000000,  1.402000],
    [1.000000, -0.344136, -0.714136],
    [1.000000,  1.772000,  0.000000]
], dtype=np.float64)


def bgr_to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    """Konversi urutan kanal memori BGR ke RGB standar analitis."""
    return img_bgr[:, :, ::-1].copy()


def rgb_to_bgr(img_rgb: np.ndarray) -> np.ndarray:
    """Konversi urutan kanal RGB ke BGR untuk penyimpanan disk."""
    return img_rgb[:, :, ::-1].copy()


def rgb_to_ycbcr(img_rgb: np.ndarray) -> np.ndarray:
    """
    Transformasi afina R'G'B' -> Y'CbCr sesuai persamaan matematika:
    [Y, Cb, Cr]^T = MAT_RGB2YCBCR * [R, G, B]^T + [0, 128, 128]^T
    """
    ycbcr = np.dot(img_rgb.astype(np.float64), MAT_RGB2YCBCR.T)
    ycbcr[:, :, [1, 2]] += 128.0
    return ycbcr


def ycbcr_to_rgb(ycbcr: np.ndarray) -> np.ndarray:
    """
    Transformasi balik Y'CbCr -> R'G'B' dengan pembatasan domain (clamping) [0, 255]:
    [R, G, B]^T = MAT_YCBCR2RGB * [Y, Cb - 128, Cr - 128]^T
    """
    shifted = ycbcr.astype(np.float64).copy()
    shifted[:, :, [1, 2]] -= 128.0
    rgb = np.dot(shifted, MAT_YCBCR2RGB.T)
    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)


def rgb_to_gray(img_rgb: np.ndarray) -> np.ndarray:
    """Proyeksi intensitas skala abu-abu analitis: Y = 0.299R + 0.587G + 0.114B."""
    gray = (0.299 * img_rgb[:, :, 0] +
            0.587 * img_rgb[:, :, 1] +
            0.114 * img_rgb[:, :, 2])
    return np.clip(np.round(gray), 0, 255).astype(np.uint8)


def gray_to_rgb(gray: np.ndarray) -> np.ndarray:
    """Menduplikasi kanal skala abu-abu menjadi representasi 3 kanal RGB."""
    return np.stack([gray, gray, gray], axis=-1)
