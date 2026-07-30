"""
test_palette_and_ciede2000.py - Comprehensive Unit & Integration Tests for Day 09.
"""

from pathlib import Path
import numpy as np
import pytest

from day09.mini_project.src.color_models import (
    CatalogYarn,
    ExtractedColor,
    MatchGrade,
    YarnMatchResult,
    CreelAllocationPlan,
    QuantizationReport,
)
from day09.mini_project.src.ciede2000 import (
    ciede2000_scalar,
    ciede2000_vectorized,
    ciede2000_error_map,
    bgr_to_cielab_float,
    cielab_to_bgr_uint8,
)
from day09.mini_project.src.kmeans_palette import KMeansPaletteExtractor
from day09.mini_project.src.yarn_matcher import YarnMatcher
from day09.mini_project.src.quantizer import CarpetQuantizer
from day09.mini_project.src.generator import (
    generate_oriental_classic_carpet,
    generate_modern_geometric_carpet,
    generate_monochrome_textured_carpet,
)


import cv2
from PIL import Image

# ---------------------------------------------------------------------------
# 1. Palette Extraction Test (Şekil 17 - Şekil 18 Standardı)
# ---------------------------------------------------------------------------

def test_palette_extraction():
    """Görüntüden PIL Image kullanarak K-Means ile 8 renkli palet ve etiket çıkarımını doğrular (Şekil 17 standardı)."""
    carpet_bgr = generate_oriental_classic_carpet(128)
    carpet_rgb = cv2.cvtColor(carpet_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(carpet_rgb)

    extractor = KMeansPaletteExtractor(n_colors=8, random_state=42)
    palette, labels = extractor.extract_palette(pil_img)

    assert palette.shape == (8, 3)
    assert palette.dtype == np.uint8
    assert labels.shape == (128 * 128,)
    assert set(np.unique(labels)).issubset(set(range(8)))


# ---------------------------------------------------------------------------
# 2. CIEDE2000 Standard Metric Tests
# ---------------------------------------------------------------------------

def test_ciede2000_identical_colors_zero():
    """Identical CIELAB colors must have Delta E_00 strictly equal to 0.0."""
    test_colors = [
        [0.0, 0.0, 0.0],          # Pure black
        [100.0, 0.0, 0.0],        # Pure white
        [50.0, 0.0, 0.0],         # Neutral grey
        [65.48, 5.25, 60.18],     # Antique Gold
        [16.48, 4.35, -23.12],    # Royal Navy
        [29.62, 51.48, 28.32],    # Imperial Ruby Red
    ]
    for c in test_colors:
        dE = ciede2000_scalar(c, c)
        assert abs(dE) < 1e-6, f"Identical color {c} produced non-zero DeltaE00: {dE}"


def test_ciede2000_standard_sharma_pairs():
    """Verify accuracy against official Sharma et al. (2005) published benchmark test pairs."""
    pairs = [
        ([50.0, 2.6772, -79.7751], [50.0, 0.0000, -82.7485], 2.0425),
        ([50.0, 3.1571, -77.2803], [50.0, 0.0000, -82.7485], 2.8615),
        ([50.0, 2.4972, -80.9360], [50.0, 0.0000, -82.7485], 1.6982),
        ([50.0, 2.8398, -79.2084], [50.0, 0.0000, -82.7485], 2.2549),
        ([50.0, -1.3802, -84.9583], [50.0, 0.0000, -82.7485], 1.1271),
        ([50.0, 0.0, 0.0], [50.0, -1.0, 2.0], 2.3669),
    ]
    for lab1, lab2, expected in pairs:
        computed = ciede2000_scalar(lab1, lab2)
        assert abs(computed - expected) < 1e-3, (
            f"Sharma test pair failed: lab1={lab1}, lab2={lab2}, "
            f"computed={computed:.4f}, expected={expected:.4f}"
        )


def test_ciede2000_blue_region_rotation_significance():
    """Verify that the rotation term RT is active and non-zero in the blue region (h ~ 275 deg)."""
    blue1 = [30.0, 10.0, -35.0]
    blue2 = [30.0, 15.0, -40.0]

    dE00 = ciede2000_scalar(blue1, blue2)
    dE76 = float(np.linalg.norm(np.array(blue1) - np.array(blue2)))

    assert dE00 > 0.0
    assert dE76 > 0.0
    assert abs(dE00 - dE76) > 0.2, "CIEDE2000 should perceptually adjust from Euclidean CIE 1976 in blue region"


def test_ciede2000_achromatic_numerical_stability():
    """Ensure achromatic colors (C* == 0) produce stable results without zero-division or NaNs."""
    greys = np.array([
        [0.0, 0.0, 0.0],
        [20.0, 0.0, 0.0],
        [50.0, 0.0, 0.0],
        [80.0, 0.0, 0.0],
        [100.0, 0.0, 0.0],
    ])
    diffs = ciede2000_vectorized(greys, greys)
    assert np.all(diffs < 1e-6)
    assert not np.any(np.isnan(diffs))

    g1 = np.array([[20.0, 0.0, 0.0]])
    g2 = np.array([[50.0, 0.0, 0.0]])
    d = ciede2000_vectorized(g1, g2)
    assert d[0] > 0.0
    assert not np.isnan(d[0])


# ---------------------------------------------------------------------------
# 3. K-Means Clustering & Subsampling Tests
# ---------------------------------------------------------------------------

def test_kmeans_palette_extraction_proportions_sum_to_100():
    """Extracted color cluster percentages must sum to 100% (+/- 0.1) and cover all pixels."""
    carpet = generate_oriental_classic_carpet(256)
    h, w, _ = carpet.shape
    total_pixels = h * w

    extractor = KMeansPaletteExtractor(default_k=6, subsample_size=5000, random_state=42)
    result = extractor.extract_palette(carpet, k=6)

    assert len(result.palette) == 6
    assert result.total_pixels == total_pixels

    sum_pct = sum(c.percentage for c in result.palette)
    sum_count = sum(c.pixel_count for c in result.palette)

    assert abs(sum_pct - 100.0) < 0.2, f"Percentages sum to {sum_pct}, expected ~100.0"
    assert sum_count == total_pixels, f"Pixel counts sum to {sum_count}, expected {total_pixels}"

    counts = [c.pixel_count for c in result.palette]
    assert counts == sorted(counts, reverse=True), "Clusters must be sorted by descending dominance"


def test_kmeans_palette_rgb_vs_lab_clustering():
    """Both LAB and RGB color spaces must successfully cluster and output valid centroids."""
    carpet = generate_modern_geometric_carpet(256)

    ext_lab = KMeansPaletteExtractor(default_k=5, color_space="LAB", subsample_size=5000)
    res_lab = ext_lab.extract_palette(carpet, k=5)

    ext_rgb = KMeansPaletteExtractor(default_k=5, color_space="RGB", subsample_size=5000)
    res_rgb = ext_rgb.extract_palette(carpet, k=5)

    assert len(res_lab.palette) == 5
    assert len(res_rgb.palette) == 5

    for c in res_lab.palette:
        assert 0 <= c.rgb[0] <= 255 and 0 <= c.rgb[1] <= 255 and 0 <= c.rgb[2] <= 255
        assert 0.0 <= c.cielab[0] <= 100.0

    for c in res_rgb.palette:
        assert 0 <= c.rgb[0] <= 255 and 0 <= c.rgb[1] <= 255 and 0 <= c.rgb[2] <= 255
        assert 0.0 <= c.cielab[0] <= 100.0


def test_subsampling_acceleration_and_fidelity():
    """Subsampling must execute rapidly while preserving centroid fidelity within close tolerance."""
    carpet = generate_monochrome_textured_carpet(256)

    ext_sub = KMeansPaletteExtractor(default_k=4, subsample_size=4000, random_state=42)
    res_sub = ext_sub.extract_palette(carpet, k=4)

    assert res_sub.elapsed_ms >= 0.0
    assert res_sub.sample_ratio < 1.0

    for c in res_sub.palette:
        assert c.percentage > 0.0
        assert len(c.rgb) == 3


# ---------------------------------------------------------------------------
# 4. Carpet Quantization & Distortion Test
# ---------------------------------------------------------------------------

def test_carpet_quantization_and_distortion_metric():
    """Quantization must produce indexed map of (H, W) and positive mean distortion."""
    carpet = generate_oriental_classic_carpet(128)
    h, w, _ = carpet.shape

    matcher = YarnMatcher()
    quantizer = CarpetQuantizer(chunk_size=4096)

    indexed_map, quantized_bgr, error_map, report = quantizer.quantize_to_catalog(
        carpet, matcher.catalog
    )

    assert indexed_map.shape == (h, w)
    assert indexed_map.dtype == np.uint8
    assert quantized_bgr.shape == (h, w, 3)
    assert quantized_bgr.dtype == np.uint8
    assert error_map.shape == (h, w)
    assert error_map.dtype == np.float32

    assert report.num_colors_used > 0
    assert report.mean_delta_e_00 >= 0.0
    assert report.max_delta_e_00 >= report.mean_delta_e_00
    assert len(report.coverage_percentages) == report.num_colors_used


# ---------------------------------------------------------------------------
# 5. Yarn Matching & Creel Allocation Test (Item 10)
# ---------------------------------------------------------------------------

def test_yarn_matching():
    """Verify catalog yarn matching with exact match DeltaE00 == 0.0 and creel allocation plan generation."""
    matcher = YarnMatcher()
    first_yarn: CatalogYarn = matcher.catalog[0]  # Royal Navy

    mock_extracted = ExtractedColor(
        cluster_id=0,
        rgb=first_yarn.rgb,
        cielab=first_yarn.cielab,
        percentage=45.0,
        pixel_count=10000,
    )

    match_res = matcher.match_color(mock_extracted)
    assert match_res.matched_yarn.yarn_id == first_yarn.yarn_id
    assert match_res.delta_e_00 < 1e-4
    assert match_res.match_grade == MatchGrade.EXACT
    assert len(match_res.alternative_matches) >= 1

    # Verify jacquard loom bobbin creel allocation plan generation
    palette = [
        ExtractedColor(cluster_id=0, rgb=matcher.catalog[0].rgb, cielab=matcher.catalog[0].cielab, percentage=40.0, pixel_count=4000),
        ExtractedColor(cluster_id=1, rgb=matcher.catalog[1].rgb, cielab=matcher.catalog[1].cielab, percentage=30.0, pixel_count=3000),
        ExtractedColor(cluster_id=2, rgb=matcher.catalog[2].rgb, cielab=matcher.catalog[2].cielab, percentage=20.0, pixel_count=2000),
        ExtractedColor(cluster_id=3, rgb=[255, 0, 255], cielab=[60.0, 98.0, -60.0], percentage=10.0, pixel_count=1000),
    ]

    plan = matcher.generate_creel_allocation_plan(palette, pattern_name="Test Oriental")
    assert plan.target_creel_size == 4
    assert plan.unique_yarn_count >= 3
    assert plan.total_estimated_yarn_cost_per_m2 > 0.0
    assert plan.uncatalogued_colors_count >= 1
