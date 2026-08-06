"""Comprehensive Unit & Integration Test Suite for Merinos Vision CLI Toolkit (Day 15).

Validates:
1. Safe I/O handling on Windows filesystems
2. Synthetic fixture generation (4 scenarios)
3. Filtering and resizing operations (Day 07)
4. Color extraction and CIEDE2000 calculations (Day 08/09)
5. Morphological defect detection (Day 11)
6. Border edge parallelism analysis (Day 12)
7. Classical motif segmentation (Day 13)
8. Multimodal feature extraction and fusion (Day 14)
9. End-to-end 6-stage inspection pipeline verdicts & HUD overlay
10. Phase 2 master benchmark suite and manifest compiler
"""

import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from day15.mini_project.src.benchmark_suite import Phase2BenchmarkSuite
from day15.mini_project.src.generator import VisionToolkitFixtureGenerator
from day15.mini_project.src.inspect_pipeline import CarpetInspectionPipeline
from day15.mini_project.src.models import (
    MasterInspectionReport,
    QualityVerdict,
    ReleaseManifest,
    StageStatus,
)
from day15.mini_project.src.toolkit import (
    MerinosIndustrialVisionToolkit,
    safe_read_image,
    safe_write_image,
)


@pytest.fixture
def sample_canvas() -> np.ndarray:
    """Fixture returning a standard 600x600 synthetic carpet image."""
    gen = VisionToolkitFixtureGenerator(size=(600, 600))
    return gen.create_perfect_carpet()


@pytest.fixture
def defective_canvas() -> np.ndarray:
    """Fixture returning a carpet with injected holes and yarn defects."""
    gen = VisionToolkitFixtureGenerator(size=(600, 600))
    return gen.create_defective_carpet()


def test_01_safe_image_io(sample_canvas: np.ndarray):
    """Test safe image writing and reading with Unicode/Turkish characters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "merinos_halı_şablon_test.png"
        write_ok = safe_write_image(test_path, sample_canvas)
        assert write_ok is True
        assert test_path.exists()

        read_img = safe_read_image(test_path)
        assert read_img is not None
        assert read_img.shape == sample_canvas.shape
        assert read_img.dtype == np.uint8
        assert np.array_equal(read_img, sample_canvas)


def test_02_fixture_generator_scenarios():
    """Test generating all 4 synthetic fixture scenarios."""
    gen = VisionToolkitFixtureGenerator(size=(400, 400))
    fixtures = gen.generate_all_fixtures()

    assert len(fixtures) == 4
    for key in ["perfect_carpet", "defective_carpet", "skewed_carpet", "faded_carpet"]:
        assert key in fixtures
        img = fixtures[key]
        assert isinstance(img, np.ndarray)
        assert img.shape == (400, 400, 3)
        assert img.dtype == np.uint8


def test_03_toolkit_filtering_and_resizing(sample_canvas: np.ndarray):
    """Test image filtering (bilateral, gaussian, median) and resizing."""
    toolkit = MerinosIndustrialVisionToolkit()

    filtered_bi = toolkit.filter_image(sample_canvas, filter_type="bilateral", kernel_size=5)
    assert filtered_bi.shape == sample_canvas.shape

    filtered_gauss = toolkit.filter_image(sample_canvas, filter_type="gaussian", kernel_size=5)
    assert filtered_gauss.shape == sample_canvas.shape

    resized = toolkit.resize_image(sample_canvas, 300, 300)
    assert resized.shape == (300, 300, 3)


def test_04_toolkit_dominant_colors_and_delta_e(sample_canvas: np.ndarray):
    """Test dominant color palette extraction and CIEDE2000 difference."""
    toolkit = MerinosIndustrialVisionToolkit()

    centers, weights = toolkit.extract_dominant_colors(sample_canvas, n_colors=4)
    assert centers.shape[0] == 4
    assert centers.shape[1] == 3
    assert len(weights) == 4
    assert np.isclose(np.sum(weights), 1.0, atol=0.05)

    # Identical colors should yield Delta-E == 0
    lab1 = np.array([50.0, 10.0, -20.0])
    de_same = toolkit.calculate_delta_e(lab1, lab1)
    assert de_same == pytest.approx(0.0, abs=1e-3)

    # Distinct colors should have Delta-E > 0
    lab2 = np.array([70.0, -15.0, 30.0])
    de_diff = toolkit.calculate_delta_e(lab1, lab2)
    assert de_diff > 10.0


def test_05_toolkit_morphological_defects(defective_canvas: np.ndarray, sample_canvas: np.ndarray):
    """Test morphological defect detection on clean vs defective carpets."""
    toolkit = MerinosIndustrialVisionToolkit()

    defects_clean, _ = toolkit.detect_defects(sample_canvas, min_area=25)
    defects_dirty, mask = toolkit.detect_defects(defective_canvas, min_area=25)

    assert len(defects_dirty) > len(defects_clean)
    assert len(defects_dirty) >= 2
    assert mask.shape == defective_canvas.shape[:2]


def test_06_toolkit_border_parallelism(sample_canvas: np.ndarray):
    """Test border edge detection and parallelism metrics."""
    toolkit = MerinosIndustrialVisionToolkit()
    metrics = toolkit.analyze_borders(sample_canvas)

    assert "max_skew_deg" in metrics
    assert "orthogonality_error_deg" in metrics
    assert "is_parallel" in metrics
    assert metrics["max_skew_deg"] >= 0.0


def test_07_toolkit_segmentation_and_coverage(sample_canvas: np.ndarray):
    """Test jacquard motif segmentation (watershed & otsu) and coverage calculation."""
    toolkit = MerinosIndustrialVisionToolkit()

    mask_ws, cov_ws = toolkit.segment_motif(sample_canvas, method="watershed")
    assert mask_ws.shape == sample_canvas.shape[:2]
    assert 5.0 <= cov_ws <= 95.0

    mask_otsu, cov_otsu = toolkit.segment_motif(sample_canvas, method="otsu")
    assert mask_otsu.shape == sample_canvas.shape[:2]
    assert 5.0 <= cov_otsu <= 95.0


def test_08_toolkit_multimodal_features(sample_canvas: np.ndarray):
    """Test multimodal feature extraction (ORB, GLCM, color histogram fusion)."""
    toolkit = MerinosIndustrialVisionToolkit()
    feats = toolkit.extract_multimodal_features(sample_canvas, n_keypoints=300)

    assert "keypoint_count" in feats
    assert feats["keypoint_count"] > 0
    assert "glcm_contrast" in feats
    assert "glcm_homogeneity" in feats
    assert "glcm_energy" in feats
    assert feats["fused_vector_dim"] > 0
    assert feats["fused_vector"].ndim == 1


def test_09_inspection_pipeline_verdict_and_hud(
    sample_canvas: np.ndarray, defective_canvas: np.ndarray
):
    """Test full 6-stage inspection pipeline decisions and HUD rendering."""
    pipeline = CarpetInspectionPipeline()

    # 1. Clean sample test
    rep_clean, hud_clean = pipeline.inspect(sample_canvas, carpet_id="CLEAN-01", render_hud=True)
    assert isinstance(rep_clean, MasterInspectionReport)
    assert rep_clean.overall_verdict in [QualityVerdict.ACCEPT, QualityVerdict.WARNING]
    assert hud_clean is not None
    assert hud_clean.shape == sample_canvas.shape
    assert len(rep_clean.stage_results) == 6

    # 2. Defective sample test (must REJECT due to multiple defects)
    rep_dirty, hud_dirty = pipeline.inspect(defective_canvas, carpet_id="DIRTY-01", render_hud=True)
    assert rep_dirty.overall_verdict == QualityVerdict.REJECT
    assert rep_dirty.defect_count >= 2
    assert hud_dirty is not None


def test_10_benchmark_suite_manifest(sample_canvas: np.ndarray):
    """Test Phase 2 benchmark suite profiling across all 8 modules."""
    suite = Phase2BenchmarkSuite(iterations=3)
    manifest = suite.run_all_benchmarks(sample_image=sample_canvas)

    assert isinstance(manifest, ReleaseManifest)
    assert manifest.version == "2.0.0"
    assert manifest.total_integrated_days == 8
    assert len(manifest.modules) == 8

    table_md = suite.format_markdown_table(manifest)
    assert "| Gün | Modül Adı |" in table_md
    assert "Day 07" in table_md
    assert "Day 14" in table_md

    for mod in manifest.modules:
        assert mod.fps > 0.0
        assert mod.mean_latency_ms >= 0.0
        assert mod.status == "OPERATIONAL"
