"""Unit tests for Day 12 Homography Rectifier."""

import numpy as np
import pytest
from day12.mini_project.src.homography_rectifier import HomographyRectifier, order_four_points


def test_order_four_points():
    unordered = np.array([
        [200, 300],  # bottom-right
        [10, 20],    # top-left
        [210, 15],   # top-right
        [15, 310],   # bottom-left
    ], dtype=np.float32)

    ordered = order_four_points(unordered)
    # ordered: [TL, TR, BR, BL]
    assert np.allclose(ordered[0], [10, 20])
    assert np.allclose(ordered[1], [210, 15])
    assert np.allclose(ordered[2], [200, 300])
    assert np.allclose(ordered[3], [15, 310])


def test_homography_rectification_shape():
    rectifier = HomographyRectifier(output_width=300, output_height=400)
    dummy_img = np.zeros((500, 500, 3), dtype=np.uint8)
    quad = np.array([[50, 50], [450, 60], [420, 460], [60, 440]], dtype=np.float32)

    warped, H = rectifier.rectify(dummy_img, quad)
    assert warped.shape == (400, 300, 3)
    assert H.shape == (3, 3)
