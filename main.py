"""
Skrip Eksekusi Utama (Main Runner)
Pengujian Komparasi Algoritma CLALHE pada Domain Warna YCbCr

CATATAN:
OpenCV (cv2) hanya digunakan untuk disk I/O (cv2.imread & cv2.imwrite).
Seluruh algoritma pengolahan citra diimplementasikan dalam modul 'src'
berbasis NumPy murni sesuai formulasi analitis matematika.
"""

import os
import time
import argparse
from datetime import datetime
import cv2
import numpy as np

from src.color_space import bgr_to_rgb, rgb_to_bgr, gray_to_rgb, rgb_to_gray
from src.enhancement import AVAILABLE_METHODS
from src.metrics import (
    compute_psnr,
    compute_ssim,
    compute_ambe,
    compute_entropy,
    delta_e_76
)


def process_image(path: str, output_dir: str = "hasil", methods: dict = None) -> list:
    """Memproses satu citra uji dengan seluruh metode yang terdaftar."""
    if methods is None:
        methods = AVAILABLE_METHODS

    name = os.path.splitext(os.path.basename(path))[0]
    img_bgr = cv2.imread(path)

    if img_bgr is None:
        print(f"  [SKIP] Berkas tidak dapat dibaca: {path}")
        return []

    # Normalisasi format ke RGB 3-kanal
    if len(img_bgr.shape) == 2:
        img_rgb = gray_to_rgb(img_bgr)
    else:
        img_rgb = bgr_to_rgb(img_bgr)

    rows = []
    for method_name, fn in methods.items():
        t0 = time.time()
        result_rgb = fn(img_rgb)
        elapsed = time.time() - t0

        rows.append({
            "image": name,
            "method": method_name,
            "psnr": compute_psnr(img_rgb, result_rgb),
            "ssim": compute_ssim(img_rgb, result_rgb),
            "delta_e": delta_e_76(img_rgb, result_rgb),
            "entropy": compute_entropy(rgb_to_gray(result_rgb)),
            "ambe": compute_ambe(img_rgb, result_rgb),
            "time": elapsed,
        })

        # Simpan hasil visual ke disk (konversi RGB kembali ke BGR untuk cv2.imwrite)
        out_path = os.path.join(output_dir, f"{name}_{method_name}.png")
        cv2.imwrite(out_path, rgb_to_bgr(result_rgb))

    return rows


def run_experiment(dataset_dir: str = "dataset", output_dir: str = "hasil"):
    """Menjalankan eksperimen pada seluruh citra di direktori dataset."""
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(dataset_dir):
        print(f"[ERROR] Direktori dataset '{dataset_dir}' tidak ditemukan.")
        return

    valid_exts = ('.tiff', '.tif', '.ppm', '.png', '.jpg', '.jpeg')
    files = sorted([f for f in os.listdir(dataset_dir) if f.lower().endswith(valid_exts)])

    if not files:
        print(f"[PERINGATAN] Tidak ditemukan berkas citra di '{dataset_dir}/'.")
        return

    all_rows = []
    print(f"\nMemproses {len(files)} citra uji dari direktori '{dataset_dir}'...\n")

    for f in files:
        print(f"[{f}] sedang diproses...")
        rows = process_image(os.path.join(dataset_dir, f), output_dir=output_dir)
        all_rows.extend(rows)

    # Tampilkan tabel evaluasi di konsol
    print("\n" + "=" * 102)
    print(f"{'Image':<12} {'Method':<22} {'PSNR':>7} {'SSIM':>7} {'DeltaE':>8} {'Entropy':>8} {'AMBE':>7} {'Time(s)':>8}")
    print("=" * 102)
    for r in all_rows:
        print(f"{r['image']:<12} {r['method']:<22} {r['psnr']:>7.2f} {r['ssim']:>7.4f} "
              f"{r['delta_e']:>8.2f} {r['entropy']:>8.3f} {r['ambe']:>7.2f} {r['time']:>8.2f}")

    # Simpan rekap metrik ke file CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    csv_path = os.path.join(output_dir, f"hasil_evaluasi_{timestamp}.csv")
    with open(csv_path, "w") as f:
        f.write("image,method,psnr,ssim,delta_e,entropy,ambe,time\n")
        for r in all_rows:
            f.write(f"{r['image']},{r['method']},{r['psnr']:.4f},{r['ssim']:.4f},"
                    f"{r['delta_e']:.4f},{r['entropy']:.4f},{r['ambe']:.4f},{r['time']:.4f}\n")

    print(f"\n[SELESAI] Rekap CSV tersimpan di: {csv_path}")
    print(f"[SELESAI] Citra visual tersimpan di: {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Eksperimen Komparasi CLALHE Domain Warna YCbCr (Pure Math)")
    parser.add_argument("--dataset", type=str, default="dataset", help="Direktori dataset citra masukan")
    parser.add_argument("--output", type=str, default="hasil", help="Direktori penyimpanan hasil pengujian")
    args = parser.parse_args()

    run_experiment(dataset_dir=args.dataset, output_dir=args.output)


if __name__ == "__main__":
    main()
