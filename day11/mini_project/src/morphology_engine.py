import cv2
import numpy as np
from typing import Tuple, List, Union, Optional

class MorphologyEngine:
    """Temel morfolojik görüntü işleme işlemleri için yardımcı sınıf."""
    def __init__(self, kernel_size: int = 3):
        self.kernel_size = kernel_size
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (kernel_size, kernel_size)
        )

    def erode(self, image: np.ndarray = None, iterations: int = 1) -> np.ndarray:
        """Aşındırma (erosion) işlemi."""
        if not isinstance(self, MorphologyEngine):
            return cv2.erode(self, image, iterations=iterations)
        return cv2.erode(image, self.kernel, iterations=iterations)

    def dilate(self, image: np.ndarray = None, iterations: int = 1) -> np.ndarray:
        """Genişletme (dilation) işlemi."""
        if not isinstance(self, MorphologyEngine):
            return cv2.dilate(self, image, iterations=iterations)
        return cv2.dilate(image, self.kernel, iterations=iterations)

    def opening(self, image: np.ndarray = None, iterations: int = 1) -> np.ndarray:
        """Opening = erosion + dilation."""
        if not isinstance(self, MorphologyEngine):
            return cv2.morphologyEx(self, cv2.MORPH_OPEN, image, iterations=iterations)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, self.kernel, iterations=iterations)

    def closing(self, image: np.ndarray = None, iterations: int = 1) -> np.ndarray:
        """Closing = dilation + erosion."""
        if not isinstance(self, MorphologyEngine):
            return cv2.morphologyEx(self, cv2.MORPH_CLOSE, image, iterations=iterations)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, self.kernel, iterations=iterations)

    def white_tophat(self, image: np.ndarray = None) -> np.ndarray:
        """Beyaz tepe şapkası (white top-hat) işlemi."""
        if not isinstance(self, MorphologyEngine):
            return cv2.morphologyEx(self, cv2.MORPH_TOPHAT, image)
        return cv2.morphologyEx(image, cv2.MORPH_TOPHAT, self.kernel)

    def black_tophat(self, image: np.ndarray = None) -> np.ndarray:
        """Siyah tepe şapkası (black top-hat) işlemi."""
        if not isinstance(self, MorphologyEngine):
            return cv2.morphologyEx(self, cv2.MORPH_BLACKHAT, image)
        return cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, self.kernel)

    def gradient(self, image: np.ndarray = None) -> np.ndarray:
        """Morfolojik gradyan (dilation - erosion) işlemi."""
        if not isinstance(self, MorphologyEngine):
            return cv2.morphologyEx(self, cv2.MORPH_GRADIENT, image)
        return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, self.kernel)

    @staticmethod
    def get_kernel(
        shape: int = cv2.MORPH_RECT,
        ksize: Tuple[int, int] = (5, 5),
    ) -> np.ndarray:
        """Create structuring element of given shape and size."""
        return cv2.getStructuringElement(shape, ksize)

    @staticmethod
    def get_directional_kernel(
        direction: str = "horizontal",
        length: int = 15,
        thickness: int = 1,
    ) -> np.ndarray:
        """Create directional linear structuring element (e.g. for warp or weft analysis)."""
        kernel = np.zeros((length, length), dtype=np.uint8)
        mid = length // 2

        if direction == "horizontal":
            y_start = max(0, mid - thickness // 2)
            y_end = min(length, y_start + thickness)
            kernel[y_start:y_end, :] = 1
        elif direction == "vertical":
            x_start = max(0, mid - thickness // 2)
            x_end = min(length, x_start + thickness)
            kernel[:, x_start:x_end] = 1
        elif direction == "diagonal_45":
            for i in range(length):
                for t in range(-thickness // 2, thickness // 2 + 1):
                    y = length - 1 - i + t
                    if 0 <= y < length:
                        kernel[y, i] = 1
        elif direction == "diagonal_135":
            for i in range(length):
                for t in range(-thickness // 2, thickness // 2 + 1):
                    y = i + t
                    if 0 <= y < length:
                        kernel[y, i] = 1
        else:
            raise ValueError(f"Unknown direction: {direction}")

        return kernel

    @classmethod
    def multi_scale_tophat(
        cls,
        img: np.ndarray,
        kernel_sizes: List[int],
    ) -> np.ndarray:
        """Accumulate White Top-Hat responses across multiple kernel scales."""
        accum = np.zeros_like(img, dtype=np.float32)
        for ks in kernel_sizes:
            engine = cls(kernel_size=ks)
            th = engine.white_tophat(img)
            accum += th.astype(np.float32)
        accum /= len(kernel_sizes)
        return np.clip(accum, 0, 255).astype(np.uint8)

    @classmethod
    def multi_scale_blackhat(
        cls,
        img: np.ndarray,
        kernel_sizes: List[int],
    ) -> np.ndarray:
        """Accumulate Black Top-Hat responses across multiple kernel scales."""
        accum = np.zeros_like(img, dtype=np.float32)
        for ks in kernel_sizes:
            engine = cls(kernel_size=ks)
            bh = engine.black_tophat(img)
            accum += bh.astype(np.float32)
        accum /= len(kernel_sizes)
        return np.clip(accum, 0, 255).astype(np.uint8)
