"""Industrial Spatial Filtering and Noise Reduction Module.

Applies Gaussian, Median, Bilateral, and Unsharp Masking filters to carpet imagery,
preserving pattern boundary contrast while suppressing optical dust and loom vibration artifacts.
"""

from typing import Any
import cv2
import numpy as np


class IndustrialFilterPipeline:
    """Industrial image filtering and edge-preserving noise suppression pipeline."""

    @staticmethod
    def gaussian_filter(
        img: np.ndarray,
        ksize: tuple[int, int] = (5, 5),
        sigma_x: float = 1.5,
        sigma_y: float = 0.0,
    ) -> np.ndarray:
        """Applies Gaussian smoothing to suppress high-frequency optical sensor noise."""
        if ksize[0] % 2 == 0 or ksize[1] % 2 == 0:
            raise ValueError(f"Kernel size dimensions must be odd numbers: {ksize}")
        return cv2.GaussianBlur(img, ksize, sigmaX=sigma_x, sigmaY=sigma_y)

    @staticmethod
    def median_filter(img: np.ndarray, ksize: int = 5) -> np.ndarray:
        """Applies non-linear median filtering to remove salt-and-pepper noise and lint particles."""
        if ksize % 2 == 0 or ksize <= 1:
            raise ValueError(f"Median filter kernel size must be an odd integer > 1, got {ksize}")
        return cv2.medianBlur(img, ksize)

    @staticmethod
    def bilateral_filter(
        img: np.ndarray,
        d: int = 9,
        sigma_color: float = 75.0,
        sigma_space: float = 75.0,
    ) -> np.ndarray:
        """Edge-preserving smoothing filter.

        Smooths repetitive yarn texture within uniform color regions while
        maintaining crisp, sharp transitions across pattern borders.
        """
        return cv2.bilateralFilter(img, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)

    @staticmethod
    def unsharp_mask(
        img: np.ndarray,
        ksize: tuple[int, int] = (5, 5),
        sigma: float = 1.0,
        strength: float = 1.5,
    ) -> np.ndarray:
        """High-frequency enhancement via unsharp masking: I_sharp = I + strength * (I - I_blurred)."""
        blurred = cv2.GaussianBlur(img, ksize, sigmaX=sigma)
        # Compute difference in float32 to prevent underflow/overflow
        diff = img.astype(np.float32) - blurred.astype(np.float32)
        sharpened = img.astype(np.float32) + strength * diff
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @staticmethod
    def calculate_sharpness(img: np.ndarray) -> float:
        """Calculates image sharpness using the variance of the Laplacian operator."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(laplacian.var())
        return round(variance, 2)
