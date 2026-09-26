"""Statistical Image Profiling and Quality Analytics Engine.

Calculates Shannon entropy, RMS contrast, dynamic range, channel histograms,
and comparative enhancement metrics for textile quality assessment.
"""

from dataclasses import asdict, dataclass
from typing import Any
import cv2
import numpy as np


@dataclass
class ImageProfile:
    """Statistical summary profile of an image."""

    mean_intensity: float
    std_intensity: float
    rms_contrast: float
    shannon_entropy: float
    dynamic_range: int
    min_val: int
    max_val: int
    p10_intensity: float
    median_intensity: float
    p90_intensity: float
    sharpness_laplacian: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ImageAnalyticsEngine:
    """Comprehensive image statistics and quality comparison analyzer."""

    @staticmethod
    def calculate_entropy(img: np.ndarray, base: float = 2.0) -> float:
        """Calculates Shannon entropy of image intensity distribution."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        hist, _ = np.histogram(gray.ravel(), bins=256, range=(0, 256), density=True)
        # Filter out zero probabilities to avoid log(0)
        prob = hist[hist > 0]
        if base == 2.0:
            entropy = -np.sum(prob * np.log2(prob))
        else:
            entropy = -np.sum(prob * (np.log(prob) / np.log(base)))
        return round(float(entropy), 4)

    @staticmethod
    def calculate_rms_contrast(img: np.ndarray) -> float:
        """Calculates Root-Mean-Square (RMS) contrast: standard deviation of pixel intensities."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        return round(float(np.std(gray)), 4)

    @staticmethod
    def calculate_histogram(img: np.ndarray, bins: int = 256) -> dict[str, list[int]]:
        """Calculates 1D intensity histograms for each channel."""
        if img.ndim == 2:
            hist = cv2.calcHist([img], [0], None, [bins], [0, 256])
            return {"gray": [int(x[0]) for x in hist]}

        b_hist = cv2.calcHist([img], [0], None, [bins], [0, 256])
        g_hist = cv2.calcHist([img], [1], None, [bins], [0, 256])
        r_hist = cv2.calcHist([img], [2], None, [bins], [0, 256])

        return {
            "blue": [int(x[0]) for x in b_hist],
            "green": [int(x[0]) for x in g_hist],
            "red": [int(x[0]) for x in r_hist],
        }

    @classmethod
    def profile_image(cls, img: np.ndarray) -> ImageProfile:
        """Generates a full statistical profile of an image array."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

        min_val, max_val = int(np.min(gray)), int(np.max(gray))
        dynamic_range = max_val - min_val

        p10, median, p90 = np.percentile(gray, [10, 50, 90])

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var())

        return ImageProfile(
            mean_intensity=round(float(np.mean(gray)), 2),
            std_intensity=round(float(np.std(gray)), 2),
            rms_contrast=cls.calculate_rms_contrast(gray),
            shannon_entropy=cls.calculate_entropy(gray),
            dynamic_range=dynamic_range,
            min_val=min_val,
            max_val=max_val,
            p10_intensity=round(float(p10), 2),
            median_intensity=round(float(median), 2),
            p90_intensity=round(float(p90), 2),
            sharpness_laplacian=round(sharpness, 2),
        )

    @classmethod
    def compare_enhancement(cls, before_img: np.ndarray, after_img: np.ndarray) -> dict[str, Any]:
        """Compares two images (e.g. before and after filtering/equalization)."""
        p_before = cls.profile_image(before_img)
        p_after = cls.profile_image(after_img)

        contrast_gain = round(p_after.rms_contrast - p_before.rms_contrast, 4)
        entropy_gain = round(p_after.shannon_entropy - p_before.shannon_entropy, 4)
        sharpness_gain = round(p_after.sharpness_laplacian - p_before.sharpness_laplacian, 2)

        return {
            "before": p_before.to_dict(),
            "after": p_after.to_dict(),
            "deltas": {
                "contrast_gain": contrast_gain,
                "entropy_gain": entropy_gain,
                "sharpness_gain": sharpness_gain,
            },
        }
