"""Unit tests for Day 13 Morphology and Edge/Line Engine."""

import numpy as np
import pytest
from day13.mini_project.src.morphology_lines import MorphologyEdgeEngine


def test_morphology_operations():
    img = np.zeros((50, 50), dtype=np.uint8)
    img[20:30, 20:30] = 255  # 10x10 white square

    eroded = MorphologyEdgeEngine.apply_morphology(img, "erosion", kernel_size=3)
    dilated = MorphologyEdgeEngine.apply_morphology(img, "dilation", kernel_size=3)

    assert eroded.sum() < img.sum()
    assert dilated.sum() > img.sum()


def test_canny_and_hough_lines():
    img = np.zeros((100, 100), dtype=np.uint8)
    # Draw a vertical white line
    img[10:90, 50] = 255

    edges = MorphologyEdgeEngine.detect_canny_edges(img, low_threshold=50, high_threshold=150)
    assert edges.sum() > 0

    lines = MorphologyEdgeEngine.detect_lines_hough(edges, threshold=20, min_line_length=20, max_line_gap=5)
    assert len(lines) >= 1
    # Check that detected line is roughly vertical (x1 close to x2)
    x1, y1, x2, y2 = lines[0]
    assert abs(x1 - x2) <= 2
