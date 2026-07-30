"""Day 09 - OpenCV Image Preprocessing Toolkit.

Implements grayscale conversion, Gaussian blurring, contrast adjustment,
and CLAHE histogram equalization for industrial textile images.
"""

from typing import Tuple
import cv2
import numpy as np


class ImagePreprocessor:
    """Preprocesses camera captures for downstream industrial inspection."""

    def __init__(self, target_size: Tuple[int, int] = (512, 512)) -> None:
        self.target_size = target_size

    def resize_image(self, img: np.ndarray) -> np.ndarray:
        """Resizes image to canonical processing resolution."""
        return cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Converts BGR image to grayscale."""
        if len(img.shape) == 2:
            return img
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def apply_gaussian_blur(self, img: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """Suppresses high-frequency sensor noise while preserving structural edges."""
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    def apply_clahe(self, gray_img: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """Applies Contrast Limited Adaptive Histogram Equalization (CLAHE)."""
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        return clahe.apply(gray_img)

    def preprocess_pipeline(self, img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Runs full sequence: Resize -> Blur -> Grayscale -> CLAHE."""
        resized = self.resize_image(img)
        gray = self.to_grayscale(resized)
        blurred = self.apply_gaussian_blur(gray, kernel_size=5)
        enhanced = self.apply_clahe(blurred)
        return resized, enhanced
