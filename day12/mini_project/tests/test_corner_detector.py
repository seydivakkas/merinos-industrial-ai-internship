"""
test_corner_detector.py - Unit and integration tests for carpet quadrilateral corner detection.
"""

from pathlib import Path
import numpy as np
import cv2
from day12.mini_project.src.corner_detector import CornerDetector


def test_detect_corners_on_synthetic():
    """Verify that CornerDetector detects the 4 carpet corners on a synthetic perspective image."""
    fixture_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    img_path = fixture_dir / "carpet_skewed_oblique_25deg.png"
    assert img_path.exists(), f"Fixture missing: {img_path}"

    raw_bytes = np.fromfile(str(img_path), dtype=np.uint8)
    img_bgr = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
    assert img_bgr is not None

    detector = CornerDetector()
    corners = detector.detect_corners(img_bgr)

    assert corners is not None
    assert corners.shape == (4, 2)
    # Expected corners: [[150, 100], [550, 120], [590, 620], [90, 590]]
    expected = np.array([[150.0, 100.0], [550.0, 120.0], [590.0, 620.0], [90.0, 590.0]], dtype=np.float32)
    diffs = np.linalg.norm(corners - expected, axis=1)
    assert np.all(diffs < 15.0), f"Corners deviated beyond tolerance: {diffs}"


def test_corner_detector_returns_four_points():
    """Verify that CornerDetector returns exactly 4 points forming a valid convex quadrilateral."""
    detector = CornerDetector()
    fixture_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    img_path = fixture_dir / "carpet_skewed_conveyor_35deg.png"

    raw_bytes = np.fromfile(str(img_path), dtype=np.uint8)
    img_bgr = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)

    corners = detector.detect_corners(img_bgr)
    assert corners is not None
    assert len(corners) == 4
    assert corners.dtype == np.float32 or corners.dtype == np.float64

    # Quadrilateral area must be substantial (> 20% of canvas)
    h, w = img_bgr.shape[:2]
    area = cv2.contourArea(corners.astype(np.float32))
    assert area > 0.20 * (h * w)
