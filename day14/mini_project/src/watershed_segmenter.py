import cv2
import numpy as np
from typing import Any, Dict, Optional, Tuple


def segment(image: np.ndarray) -> np.ndarray:
    """Watershed yöntemi ile segmentasyon."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    # Gürültü azaltma
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # İkili eşikleme (Otsu)
    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    # Morfolojik işlemler
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    # Sure foreground alanı
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(
        dist_transform, 0.5 * dist_transform.max(), 255, 0
    )
    sure_fg = np.uint8(sure_fg)
    # Bilinmeyen bölge
    unknown = cv2.subtract(sure_bg, sure_fg)
    # Marker etiketleme
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
    markers = cv2.watershed(bgr, markers)
    mask = np.zeros_like(gray, dtype=np.uint8)
    mask[markers > 1] = 255
    return mask


class WatershedSegmenter:
    """Mesafe dönüşümü ve morfolojik tohum işaretçileriyle havza (Watershed) segmentasyonu motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        ws_cfg = self.config.get("watershed", {})
        self.thresh_ratio = float(ws_cfg.get("distance_transform_threshold_ratio", 0.45))
        self.bg_dilation_ksize = tuple(ws_cfg.get("background_dilation_ksize", [3, 3]))
        self.bg_dilation_iters = int(ws_cfg.get("background_dilation_iterations", 3))
        self.morph_ksize = tuple(ws_cfg.get("morphological_kernel_size", [3, 3]))

    def segment(
        self,
        image: np.ndarray,
        binary_prior: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Görüntü üzerinde işaretçi kontrollü Watershed algoritmasını çalıştırır.

        Döndürür:
            - binary_mask: İkili ön plan motif maskesi (0 veya 255 uint8)
            - markers: Havza etiket haritası (sınırlar -1)
            - dist_transform: Normalleştirilmiş mesafe haritası
        """
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        # Watershed 3 kanallı 8-bit BGR görüntü gerektirir
        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            gray = image.copy()
        elif len(image.shape) == 3 and image.shape[2] >= 3:
            bgr = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError(f"Geçersiz görüntü boyutu: {image.shape}")

        # 1. Ön İşleme ve İkili Eşikleme (Öncelik verilmediyse Otsu)
        if binary_prior is None:
            blurred = cv2.GaussianBlur(gray, (5, 5), 1.2)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            thresh = binary_prior.copy()

        # 2. Gürültü Giderme (Açma Operasyonu)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.morph_ksize)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # 3. Kesin Arka Plan Bölgesi (Genişletme)
        bg_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.bg_dilation_ksize)
        sure_bg = cv2.dilate(opening, bg_kernel, iterations=self.bg_dilation_iters)

        # 4. Kesin Ön Plan Bölgesi (Öklid Mesafe Dönüşümü)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        max_dist = dist_transform.max()
        if max_dist > 1e-4:
            _, sure_fg = cv2.threshold(dist_transform, self.thresh_ratio * max_dist, 255, 0)
        else:
            sure_fg = np.zeros_like(opening)
        sure_fg = np.uint8(sure_fg)

        # 5. Belirsiz Sınır Bölgesi (Unknown)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # 6. Bağlantılı Bileşenler ile İşaretçi (Marker) Etiketleme
        _, markers = cv2.connectedComponents(sure_fg)

        # Arka plan 0 olmasın diye tüm etiketlere 1 ekle (arka plan 1 olur)
        markers = markers + 1
        # Belirsiz pikseller 0 olarak işaretlenir (Watershed buraları doldurur)
        markers[unknown == 255] = 0

        # 7. Havza Algoritmasını Çalıştır
        markers = cv2.watershed(bgr, markers)

        # 8. İkili Ön Plan Maskesi Çıkarımı (Sınırlar -1 ve zemin 1 dışındakiler ön plandır)
        binary_mask = np.zeros(gray.shape, dtype=np.uint8)
        binary_mask[markers > 1] = 255

        # Normalleştirilmiş mesafe görseli
        norm_dist = np.zeros_like(gray, dtype=np.uint8)
        if max_dist > 1e-4:
            norm_dist = np.clip((dist_transform / max_dist) * 255.0, 0, 255).astype(np.uint8)

        return binary_mask, markers, norm_dist
