"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
GrabCut Enerji Minimizasyonlu Grafik Kesme Motoru (GrabCutSegmenter)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, Optional, Tuple
import cv2
import numpy as np


class GrabCutSegmenter:
    """GMM ve Min-Cut/Max-Flow grafik kesme tabanlı GrabCut segmentasyon motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        gc_cfg = self.config.get("grabcut", {})
        self.iterations = int(gc_cfg.get("iterations", 5))
        self.margin_fraction = float(gc_cfg.get("margin_fraction", 0.08))

    def segment_with_rect(
        self,
        image: np.ndarray,
        rect: Optional[Tuple[int, int, int, int]] = None,
        iterations: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sınırlayıcı kutu (bounding box) ile GrabCut segmentasyonu gerçekleştirir.

        Döndürür:
            - binary_mask: 0 veya 255 uint8 ikili maske
            - gc_mask: GrabCut 4 sınıflı ham maskesi (0: BGD, 1: FGD, 2: PR_BGD, 3: PR_FGD)
        """
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            bgr = image.copy()

        h, w = bgr.shape[:2]
        iters = iterations if iterations is not None else self.iterations

        # Dikdörtgen belirtilmediyse kenar marjini ile otomatik merkez pencere kur
        if rect is None:
            mx = int(round(w * self.margin_fraction))
            my = int(round(h * self.margin_fraction))
            rect = (mx, my, w - 2 * mx, h - 2 * my)

        mask = np.zeros((h, w), dtype=np.uint8)
        bgd_model = np.zeros((1, 65), dtype=np.float64)
        fgd_model = np.zeros((1, 65), dtype=np.float64)

        cv2.grabCut(
            bgr,
            mask,
            rect,
            bgd_model,
            fgd_model,
            iters,
            mode=cv2.GC_INIT_WITH_RECT,
        )

        # Ön plan pikselleri (Kesin Ön Plan: 1 veya Olası Ön Plan: 3)
        binary_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

        return binary_mask, mask

    def segment_with_mask(
        self,
        image: np.ndarray,
        initial_mask: np.ndarray,
        iterations: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Ön segmentasyon maskesi (tohum) kullanarak GrabCut segmentasyonunu rafine eder."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            bgr = image.copy()

        h, w = bgr.shape[:2]
        iters = iterations if iterations is not None else self.iterations

        # GrabCut başlangıç maskesi (0: Kesin Arka Plan, 3: Olası Ön Plan)
        gc_mask = np.zeros((h, w), dtype=np.uint8)
        gc_mask[initial_mask > 0] = cv2.GC_PR_FGD
        gc_mask[initial_mask == 0] = cv2.GC_BGD

        bgd_model = np.zeros((1, 65), dtype=np.float64)
        fgd_model = np.zeros((1, 65), dtype=np.float64)

        cv2.grabCut(
            bgr,
            gc_mask,
            None,
            bgd_model,
            fgd_model,
            iters,
            mode=cv2.GC_INIT_WITH_MASK,
        )

        binary_mask = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

        return binary_mask, gc_mask
