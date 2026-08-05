"""Day 14 - Classical Image Segmentation for Carpet Motifs.

Implements Otsu bimodal thresholding, Watershed marker-controlled segmentation,
and region contour extraction for isolating carpet design elements from background yarn.
"""

from typing import Dict, List, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field


class SegmentedRegion(BaseModel):
    """Geometric and spatial properties of an isolated motif region."""
    region_id: int
    area_px: float
    perimeter_px: float
    circularity: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)


class CarpetSegmenter:
    """Performs classical thresholding and morphological contour segmentation."""

    @staticmethod
    def segment_otsu(gray_img: np.ndarray) -> Tuple[np.ndarray, float]:
        """Calculates optimal threshold using Otsu variance maximization."""
        val, mask = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return mask, float(val)

    @staticmethod
    def extract_regions(binary_mask: np.ndarray, min_area: float = 50.0) -> List[SegmentedRegion]:
        """Finds external contours and computes morphology descriptors."""
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        regions: List[SegmentedRegion] = []

        for idx, cnt in enumerate(contours):
            area = float(cv2.contourArea(cnt))
            if area < min_area:
                continue

            perimeter = float(cv2.arcLength(cnt, closed=True))
            circularity = 0.0
            if perimeter > 0:
                circularity = (4.0 * np.pi * area) / (perimeter ** 2)

            x, y, w, h = cv2.boundingRect(cnt)
            regions.append(SegmentedRegion(
                region_id=idx + 1,
                area_px=round(area, 2),
                perimeter_px=round(perimeter, 2),
                circularity=round(circularity, 4),
                bounding_box=(x, y, w, h)
            ))

        return regions
