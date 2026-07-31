"""Day 10 - Color Spaces and Perceptual Color Difference (Delta E).

Provides conversion between BGR, HSV, and CIE L*a*b* color spaces,
along with Delta E (CIE76) metric calculation for textile dye-lot quality grading.
"""

from typing import Tuple
import cv2
import numpy as np


def bgr_to_cielab(bgr_pixel: np.ndarray) -> np.ndarray:
    """Converts a BGR uint8 pixel array to CIE L*a*b* space."""
    pixel_1x1 = np.uint8([[bgr_pixel]])
    lab_1x1 = cv2.cvtColor(pixel_1x1, cv2.COLOR_BGR2Lab)
    return lab_1x1[0, 0].astype(np.float64)


def bgr_to_hsv(bgr_pixel: np.ndarray) -> np.ndarray:
    """Converts a BGR uint8 pixel array to HSV space."""
    pixel_1x1 = np.uint8([[bgr_pixel]])
    hsv_1x1 = cv2.cvtColor(pixel_1x1, cv2.COLOR_BGR2HSV)
    return hsv_1x1[0, 0].astype(np.float64)


def delta_e_cie76(lab1: np.ndarray, lab2: np.ndarray) -> float:
    """Computes CIE76 Euclidean color distance in L*a*b* space."""
    return float(np.linalg.norm(lab1 - lab2))


class ColorDifferenceAnalyzer:
    """Evaluates color tolerance between a reference standard and dyed yarn sample."""

    def __init__(self, tolerance_threshold: float = 2.5) -> None:
        self.tolerance_threshold = tolerance_threshold

    def grade_color_match(self, ref_bgr: np.ndarray, sample_bgr: np.ndarray) -> Tuple[float, str, bool]:
        """Calculates Delta E and provides industrial tolerance grading."""
        lab_ref = bgr_to_cielab(ref_bgr)
        lab_sample = bgr_to_cielab(sample_bgr)
        d_e = delta_e_cie76(lab_ref, lab_sample)

        if d_e < 1.0:
            grade = "EXCELLENT (Fark insan gözüyle ayırt edilemez)"
            is_acceptable = True
        elif d_e <= self.tolerance_threshold:
            grade = "ACCEPTABLE (Ticari dokuma toleransında)"
            is_acceptable = True
        elif d_e <= 5.0:
            grade = "MARGINAL (Gözle fark edilir ton sapması)"
            is_acceptable = False
        else:
            grade = "REJECTED (Kritik boya partisi hatası)"
            is_acceptable = False

        return round(d_e, 3), grade, is_acceptable
