"""
test_morphology_defects.py - Unit & Integration Tests for Day 11.
"""

from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
import cv2

from day11.mini_project.src.morphology_engine import MorphologyEngine
from day11.mini_project.src.defect_detector import CarpetDefectDetector
from day11.mini_project.src.generator import (
    create_woven_fabric_texture,
    inject_hole,
    inject_yarn_break,
    inject_slub_knot,
    inject_oil_stain,
    generate_all_synthetic_defect_fixtures,
)


def test_erode_basic():
    """Verify basic erosion operation shrinks foreground object."""
    engine = MorphologyEngine(kernel_size=3)
    img = np.zeros((30, 30), dtype=np.uint8)
    img[10:20, 10:20] = 255

    eroded = engine.erode(img)
    assert eroded.shape == img.shape
    assert np.sum(eroded) < np.sum(img)
    # 10x10 square eroded with 3x3 kernel becomes 8x8
    assert np.sum(eroded > 0) == 64


def test_dilate_basic():
    """Verify basic dilation operation expands foreground object."""
    engine = MorphologyEngine(kernel_size=3)
    img = np.zeros((30, 30), dtype=np.uint8)
    img[12:18, 12:18] = 255

    dilated = engine.dilate(img)
    assert dilated.shape == img.shape
    assert np.sum(dilated) > np.sum(img)
    # 6x6 square dilated with 3x3 kernel becomes 8x8
    assert np.sum(dilated > 0) == 64


def test_opening_basic():
    """Verify morphological opening removes small noise while preserving large objects."""
    engine = MorphologyEngine(kernel_size=3)
    img = np.zeros((30, 30), dtype=np.uint8)
    img[10:20, 10:20] = 255
    img[3, 3] = 255  # 1-px isolated salt noise

    opened = engine.opening(img)
    assert opened[3, 3] == 0  # isolated noise eliminated
    assert opened[15, 15] == 255  # object preserved


def test_closing_basic():
    """Verify morphological closing fills small holes inside solid objects."""
    engine = MorphologyEngine(kernel_size=3)
    img = np.full((30, 30), 255, dtype=np.uint8)
    img[15, 15] = 0  # 1-px pepper hole

    closed = engine.closing(img)
    assert closed[15, 15] == 255  # hole bridged and filled


def test_white_tophat_basic():
    """Verify White Top-Hat isolates bright elements smaller than kernel."""
    engine = MorphologyEngine(kernel_size=5)
    img = np.full((30, 30), 100, dtype=np.uint8)
    img[15, 15] = 255  # bright knot defect

    wth = engine.white_tophat(img)
    assert wth[15, 15] > 100
    assert wth[5, 5] == 0


def test_black_tophat_basic():
    """Verify Black Top-Hat isolates dark elements smaller than kernel."""
    engine = MorphologyEngine(kernel_size=5)
    img = np.full((30, 30), 150, dtype=np.uint8)
    img[15, 15] = 10  # dark puncture defect

    bth = engine.black_tophat(img)
    assert bth[15, 15] > 100
    assert bth[5, 5] == 0


def test_generator_output():
    """Verify synthetic carpet fabric texture and defect injection generators."""
    fabric = create_woven_fabric_texture(224, 224)
    assert fabric.shape == (224, 224, 3)
    assert fabric.dtype == np.uint8

    hole_img = inject_hole(fabric, cx=100, cy=100, radius=8)
    assert not np.array_equal(fabric, hole_img)

    yarn_img = inject_yarn_break(fabric, x=50, y=50, length=40)
    assert not np.array_equal(fabric, yarn_img)


def test_detector_pipeline():
    """Verify end-to-end defect inspection pipeline and reporting."""
    fabric = create_woven_fabric_texture(224, 224)
    hole_img = inject_hole(fabric, cx=112, cy=112, radius=11)

    detector = CarpetDefectDetector()
    report, masks = detector.inspect(hole_img)

    assert report.total_defects >= 1
    assert "white_tophat" in masks
    assert "black_tophat" in masks
    assert report.resolution == (224, 224)


def test_cli_help():
    """Verify CLI interface executes cleanly and provides help documentation."""
    res = subprocess.run(
        [sys.executable, "-m", "day11.mini_project.src.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "Merinos Carpet Morphological Defect Detection CLI" in res.stdout or "usage" in res.stdout.lower()


def test_synthetic_fixtures(tmp_path):
    """Verify synthetic fixtures generator creates all reference and defect files."""
    fixtures = generate_all_synthetic_defect_fixtures(tmp_path)
    assert Path(fixtures["clean_reference"]).exists()
    assert Path(fixtures["yarn_break"]).exists()
    assert Path(fixtures["hole_puncture"]).exists()
    assert Path(fixtures["oil_slub"]).exists()
