"""Day 12 - Perspective Rectification and Homography for Textile Inspection.

Detects and orders 4 quad corner points, computes the 3x3 projective homography matrix,
and warps perspective-distorted carpet camera images into top-down metric views.
"""

from typing import Tuple
import cv2
import numpy as np


def order_four_points(pts: np.ndarray) -> np.ndarray:
    """Orders 4 coordinates as: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left has min sum (x+y)
    rect[2] = pts[np.argmax(s)]  # Bottom-right has max sum (x+y)

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right has min diff (y-x)
    rect[3] = pts[np.argmax(diff)]  # Bottom-left has max diff (y-x)
    return rect


class HomographyRectifier:
    """Warps an oblique camera perspective of a carpet into an orthorectified view."""

    def __init__(self, output_width: int = 500, output_height: int = 700) -> None:
        self.output_width = output_width
        self.output_height = output_height

    def rectify(self, image: np.ndarray, quad_corners: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates homography and returns warped top-down image and 3x3 transform matrix."""
        rect = order_four_points(quad_corners)

        dst = np.array([
            [0, 0],
            [self.output_width - 1, 0],
            [self.output_width - 1, self.output_height - 1],
            [0, self.output_height - 1]
        ], dtype=np.float32)

        H = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, H, (self.output_width, self.output_height))
        return warped, H
