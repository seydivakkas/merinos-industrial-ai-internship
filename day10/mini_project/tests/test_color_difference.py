"""Unit tests for Day 10 Color Spaces and Delta E."""

import numpy as np
import pytest
from day10.mini_project.src.color_difference import (
    ColorDifferenceAnalyzer,
    bgr_to_cielab,
    bgr_to_hsv,
    delta_e_cie76,
)


def test_color_space_conversions():
    pure_blue_bgr = np.array([255, 0, 0], dtype=np.uint8)
    lab = bgr_to_cielab(pure_blue_bgr)
    hsv = bgr_to_hsv(pure_blue_bgr)

    assert len(lab) == 3
    assert len(hsv) == 3
    assert hsv[0] >= 110.0  # Blue hue in OpenCV HSV [0-180] is ~120


def test_delta_e_identical():
    c1 = np.array([50.0, 20.0, -10.0])
    assert delta_e_cie76(c1, c1) == 0.0


def test_color_difference_grading():
    analyzer = ColorDifferenceAnalyzer(tolerance_threshold=3.0)
    ref = np.array([200, 100, 50], dtype=np.uint8)
    sample_close = np.array([202, 101, 51], dtype=np.uint8)
    sample_far = np.array([50, 200, 200], dtype=np.uint8)

    d_e1, grade1, ok1 = analyzer.grade_color_match(ref, sample_close)
    d_e2, grade2, ok2 = analyzer.grade_color_match(ref, sample_far)

    assert d_e1 < 3.0
    assert ok1 is True
    assert d_e2 > 10.0
    assert ok2 is False
