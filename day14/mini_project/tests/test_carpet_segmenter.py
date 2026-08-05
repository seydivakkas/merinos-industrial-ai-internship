"""Unit tests for Day 14 Carpet Segmenter."""

import cv2
import numpy as np
import pytest
from day14.mini_project.src.carpet_segmenter import CarpetSegmenter


def test_otsu_and_region_extraction():
    # Synthetic image with two bright motifs on noisy background
    np.random.seed(42)
    img = np.random.randint(10, 40, (100, 100), dtype=np.uint8)
    cv2.circle(img, (30, 30), 15, 200, -1)   # Circular motif
    cv2.rectangle(img, (60, 60), (90, 90), 220, -1)  # Square motif

    mask, thresh_val = CarpetSegmenter.segment_otsu(img)
    assert 35.0 <= thresh_val <= 200.0
    assert mask.sum() > 0

    regions = CarpetSegmenter.extract_regions(mask, min_area=20.0)
    assert len(regions) >= 2

    # Circularity of circle is close to 1.0 (approx > 0.8)
    circle_reg = min(regions, key=lambda r: abs(1.0 - r.circularity))
    assert circle_reg.circularity > 0.75
