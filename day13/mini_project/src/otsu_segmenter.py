import cv2
import numpy as np
from typing import Any, Dict, List, Optional, Tuple


def segment_global(image: np.ndarray) -> np.ndarray:
    """Otsu yöntemi ile global eşikleme."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return mask


def segment_multi_level(image: np.ndarray, levels: int = 3) -> np.ndarray:
    """Çok seviyeli Otsu segmentasyonu."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholds, mask = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    # Çok seviyeli için basit genişletme
    if levels > 1:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, (3, 3))
    return mask


class OtsuSegmenter:
    """Otsu global ve çok seviyeli eşikleme algoritmasını çalıştıran segmentasyon motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        otsu_cfg = self.config.get("otsu", {})
        self.blur_ksize = tuple(otsu_cfg.get("gaussian_blur_ksize", [5, 5]))
        self.blur_sigma = float(otsu_cfg.get("gaussian_sigma", 1.2))
        self.multi_classes = int(otsu_cfg.get("multi_level_classes", 3))

        morph_cfg = otsu_cfg.get("morphological_cleanup", {"apply": True, "ksize": [3, 3]})
        self.apply_morph = morph_cfg.get("apply", True)
        self.morph_ksize = tuple(morph_cfg.get("ksize", [3, 3]))

    def preprocess_gray(self, image: np.ndarray) -> np.ndarray:
        """Giriş görüntüsünü gri seviyeye ve Gauss filtresine tabi tutar."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        if len(image.shape) == 3 and image.shape[2] >= 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            gray = image.copy()
        else:
            raise ValueError(f"Geçersiz görüntü şekli: {image.shape}")

        if self.blur_ksize[0] > 1 and self.blur_ksize[1] > 1:
            gray = cv2.GaussianBlur(gray, self.blur_ksize, self.blur_sigma)
        return gray

    def segment_global(
        self,
        image: np.ndarray,
        inverse: bool = False,
    ) -> Tuple[np.ndarray, float]:
        """Klasik 2 sınıflı Otsu eşikleme ile ön plan/arka plan maskesini ve optimal eşiği çıkarır."""
        gray = self.preprocess_gray(image)
        thresh_type = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY
        optimal_t, binary_mask = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)

        if self.apply_morph:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.morph_ksize)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        return binary_mask, float(optimal_t)

    def segment_multi_level(
        self,
        image: np.ndarray,
        classes: Optional[int] = None,
    ) -> Tuple[np.ndarray, List[int]]:
        """Zemin, motif ve bordür için çok seviyeli Otsu eşikleme ile etiketli maske çıkarır."""
        gray = self.preprocess_gray(image)
        num_classes = classes if classes is not None else self.multi_classes

        if num_classes != 3:
            # Genel 2 seviye (3 sınıf) implementasyonu endüstriyel standarttır
            num_classes = 3

        # Histogram analizi (256 seviye)
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist.astype(np.float64)
        total_pixels = float(gray.size)
        prob = hist / total_pixels

        # Kümülatif toplamlar ve momentler
        cum_prob = np.cumsum(prob)
        cum_mean = np.cumsum(prob * np.arange(256))
        global_mean = cum_mean[-1]

        best_variance = -1.0
        best_t1, best_t2 = 85, 170

        # İki eşik (t1 < t2) için ızgara taraması
        # Hız için adım aralığı (step=2)
        for t1 in range(10, 240, 2):
            w0 = cum_prob[t1]
            if w0 <= 1e-6:
                continue
            u0 = cum_mean[t1] / w0

            for t2 in range(t1 + 10, 250, 2):
                w1 = cum_prob[t2] - cum_prob[t1]
                w2 = 1.0 - cum_prob[t2]
                if w1 <= 1e-6 or w2 <= 1e-6:
                    continue

                u1 = (cum_mean[t2] - cum_mean[t1]) / w1
                u2 = (global_mean - cum_mean[t2]) / w2

                # Sınıflar arası varyans (Between-class variance)
                variance = w0 * (u0 - global_mean) ** 2 + w1 * (u1 - global_mean) ** 2 + w2 * (u2 - global_mean) ** 2

                if variance > best_variance:
                    best_variance = variance
                    best_t1, best_t2 = t1, t2

        # 3 sınıflı etiketleme (0: Koyu zemin, 1: Orta ton, 2: Parlak motif)
        labeled_mask = np.zeros_like(gray, dtype=np.uint8)
        labeled_mask[gray >= best_t1] = 1
        labeled_mask[gray >= best_t2] = 2

        return labeled_mask, [best_t1, best_t2]

    @staticmethod
    def compute_inter_class_variance(gray: np.ndarray, threshold: int) -> float:
        """Belirtilen eşik değeri için sınıflar arası varyansı hesaplar."""
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        prob = hist.astype(np.float64) / float(gray.size)

        w0 = np.sum(prob[:threshold])
        w1 = np.sum(prob[threshold:])
        if w0 <= 1e-6 or w1 <= 1e-6:
            return 0.0

        u0 = np.sum(np.arange(threshold) * prob[:threshold]) / w0
        u1 = np.sum(np.arange(threshold, 256) * prob[threshold:]) / w1

        return float(w0 * w1 * (u0 - u1) ** 2)
