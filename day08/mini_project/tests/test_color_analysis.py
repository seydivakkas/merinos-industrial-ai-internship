"""Unit and Integration Tests for Day 08 Perceptual Color Space Analysis."""

import json
from pathlib import Path
import tempfile
import cv2
import numpy as np
import pytest

from day08.mini_project.src.analyzer import CarpetColorAnalyzer
from day08.mini_project.src.cli import run_full_benchmark
from day08.mini_project.src.color_models import QAGrade, YarnColor
from day08.mini_project.src.conversions import ColorConverter
from day08.mini_project.src.delta_e import DeltaECalculator
from day08.mini_project.src.generator import SyntheticCarpetPaletteGenerator
from day08.mini_project.src.thresholding import (
    HSVColorThresholder,
    MaskMorphologyCleaner,
    PerceptualDeltaEThresholder,
)


@pytest.fixture(scope="module")
def fixture_carpets():
    """Generates fixture carpets for testing."""
    generator = SyntheticCarpetPaletteGenerator(height=180, width=240, seed=42)
    master = generator.generate_carpet()
    drift_pass = generator.generate_carpet(
        bgr_navy=(77, 44, 28),
        bgr_cream=(234, 241, 244),
        bgr_gold=(57, 177, 214),
        bgr_red=(2, 4, 142),
    )
    drift_warn = generator.generate_carpet(
        bgr_navy=(82, 48, 32),
        bgr_cream=(225, 236, 240),
        bgr_gold=(65, 185, 225),
        bgr_red=(6, 9, 150),
    )
    drift_reject = generator.generate_carpet(
        bgr_navy=(95, 60, 45),
        bgr_cream=(210, 225, 230),
        bgr_gold=(80, 195, 240),
        bgr_red=(30, 45, 190),
    )
    return {
        "master": master,
        "drift_pass": drift_pass,
        "drift_warn": drift_warn,
        "drift_reject": drift_reject,
    }


def test_color_conversions_accuracy():
    """Verifies color conversions for standard reference colors against CIE D65 standards."""
    # Pure White
    white_rgb = ColorConverter.hex_to_rgb("#FFFFFF")
    assert white_rgb == (255, 255, 255)
    white_lab = ColorConverter.rgb_to_cielab_exact(white_rgb)
    assert white_lab[0] == pytest.approx(100.0, abs=0.5)

    # Pure Black
    black_rgb = ColorConverter.hex_to_rgb("#000000")
    assert black_rgb == (0, 0, 0)
    black_lab = ColorConverter.rgb_to_cielab_exact(black_rgb)
    assert black_lab[0] == pytest.approx(0.0, abs=0.1)

    # RGB to Hex round-trip
    assert ColorConverter.rgb_to_hex((26, 43, 76)) == "#1A2B4C"


def test_delta_e_cie76_identical_and_known():
    """Verifies Delta E CIE76 properties: identity, symmetry, and triangle inequality."""
    lab_a = (50.0, 20.0, -10.0)
    lab_b = (55.0, 15.0, -5.0)
    lab_c = (70.0, -5.0, 25.0)

    # 1. Identity
    res_ident = DeltaECalculator.calculate_delta_e_cie76(lab_a, lab_a)
    assert res_ident.delta_e == 0.0
    assert res_ident.grade == QAGrade.PASS

    # 2. Symmetry
    res_ab = DeltaECalculator.calculate_delta_e_cie76(lab_a, lab_b)
    res_ba = DeltaECalculator.calculate_delta_e_cie76(lab_b, lab_a)
    assert res_ab.delta_e == pytest.approx(res_ba.delta_e, abs=1e-4)

    # 3. Triangle Inequality
    res_ac = DeltaECalculator.calculate_delta_e_cie76(lab_a, lab_c)
    res_bc = DeltaECalculator.calculate_delta_e_cie76(lab_b, lab_c)
    assert res_ac.delta_e <= (res_ab.delta_e + res_bc.delta_e) + 1e-4


def test_delta_e_tolerance_grading():
    """Verifies industrial QA classification: PASS (< 2.0), WARNING ([2.0, 5.0)), REJECT (>= 5.0)."""
    ref = (50.0, 0.0, 0.0)

    # Very small shift: Delta E = 1.0
    sample_pass = (51.0, 0.0, 0.0)
    res_pass = DeltaECalculator.calculate_delta_e_cie76(ref, sample_pass)
    assert res_pass.grade == QAGrade.PASS
    assert res_pass.delta_e == pytest.approx(1.0, abs=0.01)

    # Noticeable shift: Delta E = 3.0
    sample_warn = (53.0, 0.0, 0.0)
    res_warn = DeltaECalculator.calculate_delta_e_cie76(ref, sample_warn)
    assert res_warn.grade == QAGrade.WARNING

    # Unacceptable shift: Delta E = 7.0
    sample_reject = (57.0, 0.0, 0.0)
    res_reject = DeltaECalculator.calculate_delta_e_cie76(ref, sample_reject)
    assert res_reject.grade == QAGrade.REJECT


def test_hsv_thresholding_hue_wraparound():
    """Verifies that Imperial Red wrap-around (H: 0-10 and 170-180) captures both ends of hue circle."""
    # Create synthetic 2-pixel image: Pixel 1 has Hue=3, Pixel 2 has Hue=176
    img_hsv = np.zeros((1, 2, 3), dtype=np.uint8)
    img_hsv[0, 0] = [3, 200, 150]    # Low red
    img_hsv[0, 1] = [176, 200, 150]  # High red

    img_bgr = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)

    # Mask without wrap-around (only lower range 0-10)
    mask_single = HSVColorThresholder.create_mask(
        img_bgr, lower=(0, 100, 50), upper=(10, 255, 255)
    )
    assert mask_single[0, 0] == 255
    assert mask_single[0, 1] == 0  # Missed high red!

    # Mask with wrap-around (0-10 AND 170-180)
    mask_wrap = HSVColorThresholder.create_mask(
        img_bgr,
        lower=(0, 100, 50),
        upper=(10, 255, 255),
        lower2=(170, 100, 50),
        upper2=(180, 255, 255),
    )
    assert mask_wrap[0, 0] == 255
    assert mask_wrap[0, 1] == 255  # Both ends captured!

    # Yaprak 15 uyumlu örnek (instance) ve doğrudan hsv_image çağrı testi
    thresholder = HSVColorThresholder()
    mask_inst = thresholder.create_mask(
        img_hsv,
        lower1=(0, 100, 50),
        upper1=(10, 255, 255),
        lower2=(170, 100, 50),
        upper2=(180, 255, 255),
    )
    assert mask_inst[0, 0] == 255
    assert mask_inst[0, 1] == 255


def test_hsv_illumination_invariance():
    """Verifies that HSV thresholding isolates hue regardless of lighting / shadow variations."""
    # Two pixels: same Gold hue (H=26, S=180), but different brightness (V=230 vs V=90 shadow)
    img_hsv = np.zeros((1, 2, 3), dtype=np.uint8)
    img_hsv[0, 0] = [26, 180, 230]  # Bright gold
    img_hsv[0, 1] = [26, 180, 90]   # Shadowed gold

    img_bgr = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)

    # If threshold permits broad V [50, 255], both should be masked
    mask = HSVColorThresholder.create_mask(img_bgr, lower=(20, 140, 50), upper=(35, 255, 255))
    assert mask[0, 0] == 255
    assert mask[0, 1] == 255


def test_cielab_delta_e_thresholding_mask():
    """Verifies spherical Delta E masking around a target CIELAB color."""
    # Target color: Royal Navy LAB [18.2, 3.4, -22.1]
    target_lab = (18.2, 3.4, -22.1)

    # Create image with near pixel and far pixel
    navy_bgr = np.uint8([[[76, 43, 26]]])  # Target BGR
    gold_bgr = np.uint8([[[55, 175, 212]]]) # Distinct gold BGR

    test_img = np.hstack([navy_bgr, gold_bgr])
    mask, delta_map = PerceptualDeltaEThresholder.create_mask(test_img, target_lab, tolerance_delta_e=12.0)

    assert mask[0, 0] == 255  # Navy is within tolerance
    assert mask[0, 1] == 0    # Gold is far beyond tolerance
    assert delta_map[0, 0] < 5.0
    assert delta_map[0, 1] > 40.0


def test_mask_morphological_cleanup():
    """Verifies morphological cleaning removes isolated noise spikes and closes internal holes."""
    # 20x20 binary mask with a 10x10 square
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[5:15, 5:15] = 255

    # Introduce isolated single-pixel salt noise outside
    mask[1, 1] = 255
    # Introduce 1-pixel hole inside
    mask[10, 10] = 0

    cleaned = MaskMorphologyCleaner.clean(mask, open_ksize=(3, 3), close_ksize=(3, 3))

    # Isolated noise at (1, 1) should be eliminated
    assert cleaned[1, 1] == 0
    # Hole at (10, 10) should be filled
    assert cleaned[10, 10] == 255


def test_carpet_color_composition_sum(fixture_carpets):
    """Verifies that all 4 reference yarns are segmented and area percentages are positive."""
    master = fixture_carpets["master"]
    analyzer = CarpetColorAnalyzer()

    report, masks = analyzer.analyze_carpet(master, "Master_Test", method="hsv")

    assert len(masks) == 4
    total_area_pct = sum(item.area_percentage for item in report.yarn_findings)

    # All 4 reference yarns must be present
    for item in report.yarn_findings:
        assert item.area_percentage > 1.0  # Every yarn has substantial presence

    # Sum of yarn areas + unclassified background should approximately equal 100%
    assert 95.0 <= (total_area_pct + report.unclassified_percentage) <= 100.5


def test_dye_lot_drift_detection(fixture_carpets):
    """Verifies automated QA lot grading on master, drift_pass, drift_warn, and drift_reject."""
    analyzer = CarpetColorAnalyzer()

    rep_master, _ = analyzer.analyze_carpet(fixture_carpets["master"], "Master")
    rep_pass, _ = analyzer.analyze_carpet(fixture_carpets["drift_pass"], "Drift_Pass")
    rep_warn, _ = analyzer.analyze_carpet(fixture_carpets["drift_warn"], "Drift_Warn")
    rep_reject, _ = analyzer.analyze_carpet(fixture_carpets["drift_reject"], "Drift_Reject")

    assert rep_master.overall_status == QAGrade.PASS
    assert rep_pass.overall_status == QAGrade.PASS
    assert rep_warn.overall_status == QAGrade.WARNING
    assert rep_reject.overall_status == QAGrade.REJECT

    # Max Delta E should increase strictly monotonically
    assert rep_master.max_delta_e <= rep_pass.max_delta_e
    assert rep_pass.max_delta_e < rep_warn.max_delta_e
    assert rep_warn.max_delta_e < rep_reject.max_delta_e


def test_cli_color_analysis_pipeline_and_artifacts():
    """Verifies that CLI benchmark execution produces valid JSON reports and Markdown summary."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "outputs"
        res = run_full_benchmark(out_dir)

        assert Path(res["inspection_report"]).exists()
        assert Path(res["benchmark_report"]).exists()
        assert Path(res["summary_markdown"]).exists()

        # Validate JSON content
        with open(res["inspection_report"], "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "master" in data
            assert "drift_reject" in data
            assert data["drift_reject"]["overall_status"] == "REJECT"

        with open(res["benchmark_report"], "r", encoding="utf-8") as f:
            bench = json.load(f)
            assert len(bench) >= 4
            for op in bench:
                assert op["avg_latency_ms"] > 0.0
                assert op["throughput_fps"] > 0.0
