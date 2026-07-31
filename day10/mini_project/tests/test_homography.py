"""
test_homography.py - Unit tests for 3x3 homography projection and point warping.
"""

import numpy as np
from day10.mini_project.src.homography import compute_homography, transform_points


def test_homography_identity():
    """Identical source and destination coordinates must yield identity projection matrix."""
    pts = np.array([
        [50.0, 50.0],
        [450.0, 50.0],
        [450.0, 550.0],
        [50.0, 550.0],
    ], dtype=np.float32)

    H, res = compute_homography(pts, pts)

    np.testing.assert_allclose(H, np.eye(3), atol=1e-5)
    assert abs(res.determinant - 1.0) < 1e-3
    assert abs(res.condition_number - 1.0) < 1e-3
    assert res.inverse_frobenius_error < 1e-5


def test_homography_point_warping():
    """Source points projected through calculated H matrix must map exactly to destination points."""
    src = np.array([
        [150.0, 80.0],
        [520.0, 100.0],
        [580.0, 620.0],
        [90.0,  590.0],
    ], dtype=np.float32)
    dst = np.array([
        [0.0, 0.0],
        [500.0, 0.0],
        [500.0, 700.0],
        [0.0, 700.0],
    ], dtype=np.float32)

    H, _ = compute_homography(src, dst)
    projected = transform_points(src, H)

    np.testing.assert_allclose(projected, dst, atol=0.1)
