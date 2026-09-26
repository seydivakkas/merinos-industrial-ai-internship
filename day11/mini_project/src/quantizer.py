"""
quantizer.py - Carpet Color Quantization, Indexed Weaving Map & Distortion Analysis.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2

from .color_models import CatalogYarn, ExtractedColor, QuantizationReport
from .ciede2000 import bgr_to_cielab_float, ciede2000_vectorized, ciede2000_error_map


class CarpetQuantizer:
    """Quantizes continuous carpet images to discrete factory yarn bobbins or palette clusters."""

    def __init__(self, chunk_size: int = 32768):
        self.chunk_size = chunk_size

    def quantize_to_catalog(
        self,
        image_bgr: np.ndarray,
        catalog_yarns: List[CatalogYarn],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, QuantizationReport]:
        """Quantize carpet image to nearest Merinos factory yarn bobbins using CIEDE2000.

        Args:
            image_bgr: uint8 BGR input image of shape (H, W, 3).
            catalog_yarns: List of candidate CatalogYarn bobbins.

        Returns:
            Tuple of:
            - indexed_map: (H, W) uint8 array of bobbin index [0, num_yarns - 1].
            - quantized_bgr: (H, W, 3) uint8 BGR reconstructed image.
            - error_map: (H, W) float32 CIEDE2000 distortion heatmap.
            - report: QuantizationReport metadata object.
        """
        h, w, _ = image_bgr.shape
        total_pixels = h * w
        num_yarns = len(catalog_yarns)

        lab_img = bgr_to_cielab_float(image_bgr)
        flat_lab = lab_img.reshape(-1, 3).astype(np.float64)

        catalog_labs = np.array([y.cielab for y in catalog_yarns], dtype=np.float64)
        catalog_bgrs = np.array(
            [[y.rgb[2], y.rgb[1], y.rgb[0]] for y in catalog_yarns],
            dtype=np.uint8
        )

        indexed_flat = np.zeros(total_pixels, dtype=np.int32)
        min_errors_flat = np.zeros(total_pixels, dtype=np.float32)

        # Process in chunks to maintain optimal L2/L3 cache utilization
        for start_idx in range(0, total_pixels, self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, total_pixels)
            chunk_pixels = flat_lab[start_idx:end_idx]  # (B, 3)
            b_size = chunk_pixels.shape[0]

            # Broadcast chunk (B, 1, 3) against catalog (1, M, 3)
            chunk_expanded = np.expand_dims(chunk_pixels, axis=1)  # (B, 1, 3)
            # Repeat to (B, M, 3)
            tile_chunk = np.broadcast_to(chunk_expanded, (b_size, num_yarns, 3)).reshape(-1, 3)
            tile_catalog = np.tile(catalog_labs, (b_size, 1))

            dist_flat = ciede2000_vectorized(tile_chunk, tile_catalog)
            dist_matrix = dist_flat.reshape(b_size, num_yarns)

            best_idx = np.argmin(dist_matrix, axis=1)
            best_dist = np.min(dist_matrix, axis=1)

            indexed_flat[start_idx:end_idx] = best_idx
            min_errors_flat[start_idx:end_idx] = best_dist

        indexed_map = indexed_flat.reshape(h, w).astype(np.uint8)
        error_map = min_errors_flat.reshape(h, w).astype(np.float32)

        # Reconstruct BGR image from indexed map
        quantized_bgr = catalog_bgrs[indexed_flat].reshape(h, w, 3)

        # Compute coverage percentages
        counts = np.bincount(indexed_flat, minlength=num_yarns)
        coverage = {
            catalog_yarns[i].yarn_id: round(float(counts[i] / total_pixels) * 100.0, 2)
            for i in range(num_yarns)
            if counts[i] > 0
        }

        report = QuantizationReport(
            image_shape=[h, w, 3],
            num_colors_used=len(coverage),
            mean_delta_e_00=round(float(np.mean(error_map)), 3),
            max_delta_e_00=round(float(np.max(error_map)), 3),
            coverage_percentages=coverage,
        )

        return indexed_map, quantized_bgr, error_map, report

    def quantize_to_palette(
        self,
        image_bgr: np.ndarray,
        palette: List[ExtractedColor],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, QuantizationReport]:
        """Quantize carpet image directly to the K extracted dominant palette colors."""
        h, w, _ = image_bgr.shape
        total_pixels = h * w
        num_colors = len(palette)

        lab_img = bgr_to_cielab_float(image_bgr)
        flat_lab = lab_img.reshape(-1, 3).astype(np.float64)

        palette_labs = np.array([c.cielab for c in palette], dtype=np.float64)
        palette_bgrs = np.array(
            [[c.rgb[2], c.rgb[1], c.rgb[0]] for c in palette],
            dtype=np.uint8
        )

        indexed_flat = np.zeros(total_pixels, dtype=np.int32)
        min_errors_flat = np.zeros(total_pixels, dtype=np.float32)

        for start_idx in range(0, total_pixels, self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, total_pixels)
            chunk_pixels = flat_lab[start_idx:end_idx]
            b_size = chunk_pixels.shape[0]

            chunk_expanded = np.expand_dims(chunk_pixels, axis=1)
            tile_chunk = np.broadcast_to(chunk_expanded, (b_size, num_colors, 3)).reshape(-1, 3)
            tile_palette = np.tile(palette_labs, (b_size, 1))

            dist_flat = ciede2000_vectorized(tile_chunk, tile_palette)
            dist_matrix = dist_flat.reshape(b_size, num_colors)

            indexed_flat[start_idx:end_idx] = np.argmin(dist_matrix, axis=1)
            min_errors_flat[start_idx:end_idx] = np.min(dist_matrix, axis=1)

        indexed_map = indexed_flat.reshape(h, w).astype(np.uint8)
        error_map = min_errors_flat.reshape(h, w).astype(np.float32)
        quantized_bgr = palette_bgrs[indexed_flat].reshape(h, w, 3)

        counts = np.bincount(indexed_flat, minlength=num_colors)
        coverage = {
            f"Cluster_{i}": round(float(counts[i] / total_pixels) * 100.0, 2)
            for i in range(num_colors)
            if counts[i] > 0
        }

        report = QuantizationReport(
            image_shape=[h, w, 3],
            num_colors_used=len(coverage),
            mean_delta_e_00=round(float(np.mean(error_map)), 3),
            max_delta_e_00=round(float(np.max(error_map)), 3),
            coverage_percentages=coverage,
        )

        return indexed_map, quantized_bgr, error_map, report


def process_image(image_path: str, n_colors: int = 8) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Görüntüden K-Means ile baskın renk paleti çıkarır, nicemleme yapar ve 4'lü hata analiz panelini gösterir.

    Args:
        image_path: Halı görseli dosya yolu (str veya Path)
        n_colors: Küme sayısı (varsayılan: 8)

    Returns:
        pal: (n_colors, 3) uint8 RGB palet renkleri
        labels: Kümeleme piksel etiketleri
        q_img: Nicemlenmiş RGB görüntü
        error_map: Hata haritası (0-100 ölçekli)
    """
    from PIL import Image
    import matplotlib.pyplot as plt
    from .kmeans_palette import KMeansPaletteExtractor

    img_pil = Image.open(str(image_path)).convert("RGB")
    img_np = np.array(img_pil)
    h, w, _ = img_np.shape

    extractor = KMeansPaletteExtractor(n_colors=n_colors, random_state=42)
    pal, labels = extractor.extract_palette(img_pil)

    # 3. Nicemleme (Reconstruction)
    q_img = pal[labels].reshape(h, w, 3)

    # 4. Hata Haritası (Error Map)
    diff = img_np.astype(np.float32) - q_img.astype(np.float32)
    error_map = np.sqrt(np.sum(diff ** 2, axis=2))
    max_err = error_map.max()
    error_map_scaled = (error_map / max_err * 100.0) if max_err > 0 else error_map

    # Kümeleme oranlarını hesapla (baskınlığa göre azalan sırada)
    counts = np.bincount(labels, minlength=n_colors)
    total_px = len(labels)
    sorted_order = np.argsort(-counts)

    # 4'lü Panel Görselleştirme (Şekil 18 standardı)
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))

    # 1. Orijinal Sentetik Halı Görüntüsü
    axes[0].imshow(img_np)
    axes[0].set_title("1. Orijinal Sentetik Halı Görüntüsü", fontsize=11, fontweight="medium")
    axes[0].axis("off")

    # 2. K-Means Baskın Renk Paleti (k=8)
    axes[1].set_title(f"2. K-Means Baskın Renk Paleti (k={n_colors})", fontsize=11, fontweight="medium")
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(-0.5, n_colors - 0.5)
    axes[1].axis("off")

    for rank, idx in enumerate(sorted_order):
        y_pos = n_colors - 1 - rank
        color_rgb = pal[idx] / 255.0
        hex_code = f"#{pal[idx][0]:02X}{pal[idx][1]:02X}{pal[idx][2]:02X}"
        pct = (counts[idx] / total_px) * 100.0

        # Renk kutusu
        rect = plt.Rectangle((0.05, y_pos - 0.35), 0.25, 0.7, facecolor=color_rgb, edgecolor="#444444", linewidth=0.8)
        axes[1].add_patch(rect)

        # HEX kodu
        axes[1].text(0.35, y_pos, hex_code, va="center", ha="left", fontsize=10, family="monospace", fontweight="bold")
        # Yüzdelik pay
        axes[1].text(0.95, y_pos, f"{pct:.1f}%", va="center", ha="right", fontsize=10, fontweight="medium")

    # 3. Nicemlenmiş (Sınırlı Renkli) Görüntü
    axes[2].imshow(q_img)
    axes[2].set_title("3. Nicemlenmiş (Sınırlı Renkli) Görüntü", fontsize=11, fontweight="medium")
    axes[2].axis("off")

    # 4. Bozulma (Hata) Isı Haritası
    im_err = axes[3].imshow(error_map_scaled, cmap="magma", vmin=0, vmax=100)
    axes[3].set_title("4. Bozulma (Hata) Isı Haritası", fontsize=11, fontweight="medium")
    axes[3].axis("off")
    cbar = fig.colorbar(im_err, ax=axes[3], fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.show()

    return pal, labels, q_img, error_map_scaled
