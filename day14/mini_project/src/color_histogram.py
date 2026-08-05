"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Çok Kanallı Renk Histogramı ve Karşılaştırma Motoru (ColorHistogramEngine)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from .models import ColorHistogramFeatures


class ColorHistogramEngine:
    """3D HSV / LAB renk histogramı çıkarıcı ve benzerlik karşılaştırıcısı."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        ch_cfg = self.config.get("color_histogram", {})
        
        self.color_space = ch_cfg.get("color_space", "HSV")
        self.bins = list(ch_cfg.get("bins", [16, 8, 8]))
        self.normalize = bool(ch_cfg.get("normalize", True))

    def compute_histogram(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, ColorHistogramFeatures]:
        """Görüntüden 3D normalize HSV histogramı çıkarır."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        if len(image.shape) != 3 or image.shape[2] < 3:
            raise ValueError("Renk histogramı için 3 kanallı BGR görüntü gereklidir.")

        # Renk uzayı dönüşümü
        if self.color_space == "HSV":
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            ranges = [0, 180, 0, 256, 0, 256]
        elif self.color_space == "LAB":
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            ranges = [0, 256, 0, 256, 0, 256]
        else:
            converted = image.copy()
            ranges = [0, 256, 0, 256, 0, 256]

        # 3D Histogram hesapla
        hist = cv2.calcHist(
            [converted],
            channels=[0, 1, 2],
            mask=mask,
            histSize=self.bins,
            ranges=ranges,
        )

        # L1 Normalizasyonu (toplam = 1.0)
        total = hist.sum()
        if total > 0 and self.normalize:
            hist = hist / total

        flat_hist = hist.flatten().astype(np.float32)
        total_dim = int(flat_hist.size)

        # En baskın ilk 5 bin
        sorted_indices = np.argsort(flat_hist)[::-1][:5]
        top_bins = [(int(idx), round(float(flat_hist[idx]), 4)) for idx in sorted_indices]

        # Shannon Renk Entropisi
        eps = 1e-12
        p_nz = flat_hist[flat_hist > eps]
        entropy = float(-np.sum(p_nz * np.log2(p_nz))) if len(p_nz) > 0 else 0.0
        peak_val = float(flat_hist.max())

        features = ColorHistogramFeatures(
            dimension=total_dim,
            top_bins=top_bins,
            entropy=round(entropy, 4),
            peak_bin_value=round(peak_val, 4),
        )

        return flat_hist, features

    @staticmethod
    def compare_histograms(
        hist1: np.ndarray,
        hist2: np.ndarray,
        method: str = "bhattacharyya",
    ) -> float:
        """İki normalize histogram arasındaki benzerlik veya mesafeyi hesaplar."""
        h1 = hist1.astype(np.float32)
        h2 = hist2.astype(np.float32)

        method_map = {
            "correlation": cv2.HISTCMP_CORREL,
            "chi_square": cv2.HISTCMP_CHISQR,
            "intersection": cv2.HISTCMP_INTERSECT,
            "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA,
        }
        cv_method = method_map.get(method.lower(), cv2.HISTCMP_BHATTACHARYYA)
        dist = cv2.compareHist(h1, h2, cv_method)
        return float(dist)
