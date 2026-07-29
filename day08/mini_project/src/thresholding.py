"""Color Thresholding and Morphological Mask Cleanup Module.

Provides Hue-wrap-around aware HSV segmentation, perceptual CIELAB Delta-E
distance thresholding, and morphological cleanup for textile yarn inspection.
"""

from typing import Sequence
import cv2
import numpy as np

from day08.mini_project.src.conversions import ColorConverter
from day08.mini_project.src.delta_e import DeltaECalculator


class HSVColorThresholder:
    """HSV renk uzayında eşikleme yapan sınıf.
    Özellikle kırmızı gibi dairesel renkler için çift aralık desteği sağlar."""

    def __init__(self):
        """Renk eşikleme için yardımcı sınıf."""
        pass

    @classmethod
    def create_mask(
        cls,
        hsv_image: np.ndarray,
        lower1: Sequence[int] | None = None,
        upper1: Sequence[int] | None = None,
        lower2: Sequence[int] | None = None,
        upper2: Sequence[int] | None = None,
        *,
        lower: Sequence[int] | None = None,
        upper: Sequence[int] | None = None,
        is_bgr: bool | None = None,
    ) -> np.ndarray:
        """Verilen HSV aralıklarına göre ikili maske oluşturur.
        Kırmızı renk gibi 0/180 etrafında tanımlanan renkler için iki aralık birleştirilebilir.

        Args:
            hsv_image (np.ndarray): HSV formatında görüntü
            lower1, upper1 (tuple): İlk HSV aralığı (np.array veya tuple)
            lower2, upper2 (tuple, optional): İkinci HSV aralığı (kırmızı için)
            lower, upper (tuple, optional): Geriye dönük uyumluluk için ilk aralık
            is_bgr (bool, optional): Görüntünün BGR formatında olduğunu zorla belirtir
        """
        l1 = lower1 if lower1 is not None else lower
        u1 = upper1 if upper1 is not None else upper
        l2 = lower2
        u2 = upper2

        if l1 is None or u1 is None:
            raise ValueError("lower1 ve upper1 (veya lower ve upper) aralıkları belirtilmelidir.")

        # Görüntü BGR ise veya legacy çağrılarda otomatik tespit/dönüşüm
        if is_bgr is True or (is_bgr is None and (lower is not None or upper is not None)):
            working_image = ColorConverter.bgr_image_to_hsv(hsv_image)
        else:
            working_image = hsv_image

        # İlk aralık için maske
        mask1 = cv2.inRange(working_image, np.array(l1, dtype=np.uint8), np.array(u1, dtype=np.uint8))

        # İkinci aralık varsa (örneğin kırmızı renk için)
        if l2 is not None and u2 is not None:
            mask2 = cv2.inRange(working_image, np.array(l2, dtype=np.uint8), np.array(u2, dtype=np.uint8))
            # İki maskeyi birleştir
            return cv2.bitwise_or(mask1, mask2)

        return mask1


class PerceptualDeltaEThresholder:
    """CIELAB Delta E spherical color segmentation engine."""

    @classmethod
    def create_mask(
        cls,
        img_bgr: np.ndarray,
        target_lab: Sequence[float],
        tolerance_delta_e: float = 12.0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Creates a binary mask for pixels whose Delta E distance from target_lab is <= tolerance.

        Returns:
            (mask, delta_e_map): binary mask (0 or 255) and raw continuous float32 Delta E map.
        """
        lab_img = ColorConverter.bgr_image_to_cielab_float(img_bgr)
        delta_e_map = DeltaECalculator.pairwise_delta_e_image(lab_img, target_lab)
        mask = (delta_e_map <= tolerance_delta_e).astype(np.uint8) * 255
        return mask, delta_e_map


class MaskMorphologyCleaner:
    """Removes salt-and-pepper fiber noise and closes microscopic weave gaps."""

    @staticmethod
    def clean(
        mask: np.ndarray,
        open_ksize: tuple[int, int] = (3, 3),
        close_ksize: tuple[int, int] | None = None,
    ) -> np.ndarray:
        """Applies morphological Opening (noise removal) and optional Closing (hole filling)."""
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, open_ksize)
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
        if close_ksize is not None:
            kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, close_ksize)
            return cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_close)
        return opened
