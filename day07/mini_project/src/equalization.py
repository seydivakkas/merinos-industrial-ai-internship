"""Histogram Equalization and Contrast Enhancement Module.

Provides Global Histogram Equalization (GHE) and Contrast Limited Adaptive
Histogram Equalization (CLAHE) on both grayscale and perceptual color spaces
(CIELAB L* and YCrCb Y), preventing hue/chroma distortion in textile imagery.
"""

from typing import Literal
import cv2
import numpy as np


class HistogramEqualizer:
    """Industrial contrast enhancer with perceptual color-channel isolation."""

    @staticmethod
    def global_equalize_grayscale(img: np.ndarray) -> np.ndarray:
        """Applies global histogram equalization to a 1-channel grayscale image."""
        if img.ndim != 2 and not (img.ndim == 3 and img.shape[2] == 1):
            raise ValueError(f"Expected single-channel grayscale image, got shape {img.shape}")
        gray = img if img.ndim == 2 else img[:, :, 0]
        return cv2.equalizeHist(gray)

    @staticmethod
    def clahe_grayscale(
        img: np.ndarray,
        clip_limit: float = 2.5,
        tile_grid_size: tuple[int, int] = (8, 8),
    ) -> np.ndarray:
        """Applies CLAHE to a single-channel grayscale image."""
        if img.ndim != 2 and not (img.ndim == 3 and img.shape[2] == 1):
            raise ValueError(f"Expected single-channel grayscale image, got shape {img.shape}")
        gray = img if img.ndim == 2 else img[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(gray)

    @classmethod
    def enhance_color_perceptual(
        cls,
        img_bgr: np.ndarray,
        method: Literal["clahe", "global"] = "clahe",
        space: Literal["lab", "ycrcb"] = "lab",
        clip_limit: float = 2.5,
        tile_grid_size: tuple[int, int] = (8, 8),
    ) -> np.ndarray:
        """Enhances color contrast by equalizing ONLY the luminance/lightness channel.

        Prevents chromatic shift and false color tinting by leaving color-opponent
        chrominance channels completely untouched.
        """
        if img_bgr.ndim != 3 or img_bgr.shape[2] != 3:
            raise ValueError(f"Expected 3-channel BGR image, got shape {img_bgr.shape}")

        if space.lower() == "lab":
            lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab)
            l_channel, a_channel, b_channel = cv2.split(lab)

            if method.lower() == "clahe":
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
                l_eq = clahe.apply(l_channel)
            else:
                l_eq = cv2.equalizeHist(l_channel)

            merged_lab = cv2.merge([l_eq, a_channel, b_channel])
            return cv2.cvtColor(merged_lab, cv2.COLOR_Lab2BGR)

        if space.lower() == "ycrcb":
            ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
            y_channel, cr_channel, cb_channel = cv2.split(ycrcb)

            if method.lower() == "clahe":
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
                y_eq = clahe.apply(y_channel)
            else:
                y_eq = cv2.equalizeHist(y_channel)

            merged_ycrcb = cv2.merge([y_eq, cr_channel, cb_channel])
            return cv2.cvtColor(merged_ycrcb, cv2.COLOR_YCrCb2BGR)

        raise ValueError(f"Unsupported perceptual color space: {space}. Use 'lab' or 'ycrcb'.")

    @staticmethod
    def naive_rgb_equalize(img_bgr: np.ndarray) -> np.ndarray:
        """Demonstrates naive independent channel equalization (anti-pattern).

        Included as a baseline to demonstrate chromatic distortion in reports.
        """
        b, g, r = cv2.split(img_bgr)
        return cv2.merge([cv2.equalizeHist(b), cv2.equalizeHist(g), cv2.equalizeHist(r)])
