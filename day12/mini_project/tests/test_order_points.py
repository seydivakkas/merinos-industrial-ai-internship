"""
test_order_points.py - Unit tests for deterministic 4-corner quadrilateral ordering.
"""

import numpy as np
from day12.mini_project.src.corner_detector import order_points


def test_order_points_basic():
    """Verify that 4 unordered rectangle corners are sorted strictly into [TL, TR, BR, BL] format."""
    expected_tl = [100.0, 100.0]
    expected_tr = [500.0, 100.0]
    expected_br = [500.0, 600.0]
    expected_bl = [100.0, 600.0]
    ground_truth = np.array([expected_tl, expected_tr, expected_br, expected_bl], dtype=np.float32)

    # Test arbitrary scrambled permutations
    shuffled = np.array([expected_br, expected_tl, expected_bl, expected_tr], dtype=np.float32)
    ordered = order_points(shuffled)

    assert ordered.shape == (4, 2)
    np.testing.assert_allclose(ordered[0], expected_tl, atol=1e-3)
    np.testing.assert_allclose(ordered[1], expected_tr, atol=1e-3)
    np.testing.assert_allclose(ordered[2], expected_br, atol=1e-3)
    np.testing.assert_allclose(ordered[3], expected_bl, atol=1e-3)


def test_order_points_rotated():
    """Verify that rotated/skewed quad corners are properly ordered and preserved."""
    pts = np.array([
        [150.0, 100.0],  # TL
        [550.0, 120.0],  # TR
        [590.0, 620.0],  # BR
        [90.0,  590.0],  # BL
    ], dtype=np.float32)

    shuffled = pts[[2, 0, 3, 1]]
    ordered = order_points(shuffled)

    assert ordered.shape == (4, 2)
    np.testing.assert_allclose(ordered, pts, atol=1e-3)
