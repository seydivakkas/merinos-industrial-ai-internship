"""Day 13 - Morphological Operations, Edge and Line Detection.

Implements mathematical morphology (erosion, dilation, opening, closing),
Canny edge detection, and Probabilistic Hough Transform for textile yarn/border alignment.
"""

from typing import List, Tuple
import cv2
import numpy as np


class MorphologyEdgeEngine:
    """Processes binary and grayscale textile images for structural edge and line analysis."""

    @staticmethod
    def apply_morphology(image: np.ndarray, operation: str = "opening", kernel_size: int = 3) -> np.ndarray:
        """Applies mathematical morphology using a rectangular structuring element."""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        op_map = {
            "erosion": cv2.MORPH_ERODE,
            "dilation": cv2.MORPH_DILATE,
            "opening": cv2.MORPH_OPEN,
            "closing": cv2.MORPH_CLOSE,
        }
        if operation not in op_map:
            raise ValueError(f"Unsupported morphology operation: {operation}")
        return cv2.morphologyEx(image, op_map[operation], kernel)

    @staticmethod
    def detect_canny_edges(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """Applies hysteresis double-thresholding Canny edge detection."""
        gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, low_threshold, high_threshold)

    @staticmethod
    def detect_lines_hough(
        edges: np.ndarray,
        threshold: int = 50,
        min_line_length: int = 30,
        max_line_gap: int = 10
    ) -> List[Tuple[int, int, int, int]]:
        """Detects linear segments (e.g. yarn paths or carpet border edges)."""
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=threshold,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap
        )
        if lines is None:
            return []
        return [tuple(line[0]) for line in lines]
