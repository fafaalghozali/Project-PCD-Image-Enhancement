"""
Modul Engine Inti CLAHE Matematika Murni (Pure NumPy)
Mengimplementasikan:
1. Partisi Spasial Kisi (Grid Partitioning)
2. Pemotongan Histogram Lokal & Redistribusi Seragam (Clipping & Redistribution)
3. Fungsi Distribusi Kumulatif (CDF Mapping Function)
4. Interpolasi Spasial Bilinear Antar-Pusat Blok (Bilinear Spatial Interpolation)
"""

import numpy as np


def pure_clahe_math(channel: np.ndarray, clip_limit: float = 2.0, grid_size: tuple = (8, 8)) -> np.ndarray:
    """
    Implementasi murni CLAHE sesuai formulasi analitis matematika.
    
    Parameters:
    -----------
    channel : np.ndarray
        Array 2D skalar intensitas (uint8) dengan dimensi (H, W).
    clip_limit : float
        Faktor ambang pemotongan histogram.
    grid_size : tuple (gy, gx)
        Jumlah pembagian grid spasial kontekstual.
        
    Returns:
    --------
    np.ndarray
        Array 2D hasil ekualisasi kontras adaptif berukuran (H, W) tipe uint8.
    """
    H, W = channel.shape
    gy, gx = grid_size
    step_y = H / gy
    step_x = W / gx

    # Tahap 1, 2, & 3: Hitung Fungsi Pemetaan T_{(i,j)}(k) untuk setiap blok
    mappings = np.zeros((gy, gx, 256), dtype=np.float64)

    for i in range(gy):
        for j in range(gx):
            y1, y2 = int(round(i * step_y)), int(round((i + 1) * step_y))
            x1, x2 = int(round(j * step_x)), int(round((j + 1) * step_x))
            tile = channel[y1:y2, x1:x2]

            # Histogram lokal blok
            hist = np.bincount(tile.flatten(), minlength=256).astype(np.float64)
            tile_pixels = tile.size

            # Ambang batas kliping proporsional terhadap ukuran blok
            actual_clip = max(1.0, clip_limit * (tile_pixels / 256.0))

            # Pemotongan puncak dan redistribusi kelebihan
            excess = np.sum(np.maximum(hist - actual_clip, 0.0))
            clipped_hist = np.minimum(hist, actual_clip) + (excess / 256.0)

            # Cumulative Distribution Function (CDF) dinormalisasi ke domain [0, 255]
            cdf = np.cumsum(clipped_hist)
            mappings[i, j, :] = np.round((cdf / cdf[-1]) * 255.0)

    # Tahap 4: Interpolasi Bilinear Spasial
    center_y = (np.arange(gy) + 0.5) * step_y
    center_x = (np.arange(gx) + 0.5) * step_x

    y_coords, x_coords = np.indices((H, W))

    i_float = (y_coords - center_y[0]) / step_y
    j_float = (x_coords - center_x[0]) / step_x

    # Indeks 4 pusat blok terdekat
    i1 = np.clip(np.floor(i_float).astype(int), 0, gy - 2)
    i2 = i1 + 1
    j1 = np.clip(np.floor(j_float).astype(int), 0, gx - 2)
    j2 = j1 + 1

    # Bobot interpolasi bilinear (s, t)
    t = np.clip(i_float - i1, 0.0, 1.0)
    s = np.clip(j_float - j1, 0.0, 1.0)

    val = channel[y_coords, x_coords]

    T11 = mappings[i1, j1, val]
    T12 = mappings[i1, j2, val]
    T21 = mappings[i2, j1, val]
    T22 = mappings[i2, j2, val]

    # Rumus interpolasi bilinear analitis:
    interpolated = ((1.0 - s) * (1.0 - t) * T11 +
                    s * (1.0 - t) * T12 +
                    (1.0 - s) * t * T21 +
                    s * t * T22)

    return np.clip(np.round(interpolated), 0, 255).astype(np.uint8)
