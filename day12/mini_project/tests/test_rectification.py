"""
test_rectification.py - Integration tests for perspective distortion rectification pipeline.
"""

from pathlib import Path
import numpy as np
import cv2
from day12.mini_project.src.rectifier import CarpetPerspectiveRectifier
from day12.mini_project.src.models import QAGrade, StandardCarpetRatio
from day12.mini_project.src.generator import create_flat_carpet_patch, apply_synthetic_homography


def test_rectify_preserves_content():
    """Verify that perspective rectification preserves pattern content and achieves orthogonal angles."""
    carpet = create_flat_carpet_patch(300, 450)
    h_c, w_c = carpet.shape[:2]
    src_quad = np.array([[0, 0], [w_c - 1, 0], [w_c - 1, h_c - 1], [0, h_c - 1]], dtype=np.float32)

    skewed_dst = np.array([
        [140.0, 90.0],
        [460.0, 110.0],
        [530.0, 540.0],
        [70.0,  510.0],
    ], dtype=np.float32)

    composite, _ = apply_synthetic_homography(carpet, (600, 600), src_quad, skewed_dst)

    rectifier = CarpetPerspectiveRectifier()
    rectified, report = rectifier.rectify(composite, corners=skewed_dst, mode="adaptive")

    assert report.qa_grade == QAGrade.PASS
    assert report.max_angle_deviation < 1.0
    assert rectified.mean() > 10.0  # Image contains valid carpet pixel content


def test_rectify_output_size():
    """Verify that rectified output matches specified dimensions or standard physical ratio."""
    carpet = create_flat_carpet_patch(300, 450)
    h_c, w_c = carpet.shape[:2]
    src_quad = np.array([[0, 0], [w_c - 1, 0], [w_c - 1, h_c - 1], [0, h_c - 1]], dtype=np.float32)

    skewed_dst = np.array([
        [150.0, 100.0],
        [480.0, 120.0],
        [520.0, 560.0],
        [80.0,  540.0],
    ], dtype=np.float32)

    composite, _ = apply_synthetic_homography(carpet, (600, 600), src_quad, skewed_dst)

    rectifier = CarpetPerspectiveRectifier()
    rectified, report = rectifier.rectify(
        composite,
        corners=skewed_dst,
        mode="standard",
        standard_ratio=StandardCarpetRatio.STANDARD_160_230,
    )

    expected_ratio = 160.0 / 230.0
    assert abs(report.aspect_ratio - expected_ratio) < 0.02
    assert rectified.shape[0] == report.target_dimensions[1]
    assert rectified.shape[1] == report.target_dimensions[0]


def test_rectify_on_realistic_synthetic():
    """End-to-end rectification on realistic synthetic fixture."""
    fixture_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    img_path = fixture_dir / "carpet_skewed_conveyor_35deg.png"

    raw_bytes = np.fromfile(str(img_path), dtype=np.uint8)
    img_bgr = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)

    rectifier = CarpetPerspectiveRectifier()
    rectified, report = rectifier.rectify(img_bgr, mode="adaptive")

    assert rectified is not None
    assert report.qa_grade in (QAGrade.PASS, QAGrade.WARNING)
    assert report.target_dimensions[0] > 100
    assert report.target_dimensions[1] > 100
