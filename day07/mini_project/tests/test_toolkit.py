"""Unit and Integration Tests for Day 07 OpenCV Image Analytics Toolkit."""

import json
from pathlib import Path
import tempfile
import cv2
import numpy as np
import pytest

from day07.mini_project.src.analytics import ImageAnalyticsEngine
from day07.mini_project.src.cli import run_full_benchmark
from day07.mini_project.src.color_spaces import ColorSpaceConverter, ColorSpaceError
from day07.mini_project.src.equalization import HistogramEqualizer
from day07.mini_project.src.filters import IndustrialFilterPipeline
from day07.mini_project.src.generator import SyntheticCarpetGenerator
from day07.mini_project.src.io_validator import (
    ImageIOError,
    ImageIOValidator,
    ImageValidationError,
)
from day07.mini_project.src.resizer import AspectPreservingResizer


@pytest.fixture(scope="module")
def sample_carpets():
    """Provides synthetic carpet fixture arrays for testing."""
    generator = SyntheticCarpetGenerator(height=180, width=240, seed=42)
    base = generator.generate_base_carpet()
    low_con = generator.generate_low_contrast(base)
    noisy = generator.generate_noisy_carpet(base)
    return {
        "base": base,
        "low_contrast": low_con,
        "noisy": noisy,
    }


def test_image_io_unicode_safe_read_write(sample_carpets):
    """Verifies that ImageIOValidator works safely with Unicode / Turkish folder paths."""
    base_img = sample_carpets["base"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create folder with Turkish characters: 'Merinos_Halı_Örnekleri_Şti'
        turkish_dir = Path(tmp_dir) / "Merinos_Halı_Örnekleri_Şti"
        target_file = turkish_dir / "desen_test_ğüşıöç.png"

        saved_path = ImageIOValidator.write_image(base_img, target_file)
        assert saved_path.exists()

        # Read back
        loaded = ImageIOValidator.read_image(saved_path)
        assert loaded is not None
        assert loaded.shape == base_img.shape
        assert loaded.dtype == base_img.dtype
        assert np.array_equal(loaded, base_img)


def test_image_io_metadata_extraction(sample_carpets):
    """Verifies correct calculation of image metadata attributes."""
    base_img = sample_carpets["base"]
    meta = ImageIOValidator.extract_metadata(base_img, "test_carpet.png")

    assert meta.height == 180
    assert meta.width == 240
    assert meta.channels == 3
    assert meta.dtype == "uint8"
    assert meta.aspect_ratio == round(240 / 180, 4)
    assert meta.is_c_contiguous is True
    assert 0 <= meta.min_intensity <= meta.max_intensity <= 255


def test_color_space_conversions(sample_carpets):
    """Verifies conversions across BGR, RGB, HSV, LAB, and YCrCb."""
    bgr = sample_carpets["base"]

    # RGB
    rgb = ColorSpaceConverter.convert(bgr, "BGR", "RGB")
    assert rgb.shape == bgr.shape
    assert np.array_equal(rgb[:, :, 0], bgr[:, :, 2])  # R == B in reversed channels

    # HSV (H: 0-180 in 8-bit cv2)
    hsv = ColorSpaceConverter.convert(bgr, "BGR", "HSV")
    assert hsv.shape == bgr.shape
    assert np.max(hsv[:, :, 0]) <= 180

    # LAB (L, A, B)
    lab = ColorSpaceConverter.convert(bgr, "BGR", "LAB")
    assert lab.shape == bgr.shape

    # Channel stats
    stats = ColorSpaceConverter.channel_statistics(hsv, "HSV")
    assert "H" in stats and "S" in stats and "V" in stats
    assert stats["H"]["max"] <= 180

    # Error handling on invalid space
    with pytest.raises(ColorSpaceError):
        ColorSpaceConverter.convert(bgr, "BGR", "INVALID_SPACE")


def test_aspect_preserving_resizer_letterbox(sample_carpets):
    """Verifies aspect-ratio preserving letterbox resizing with symmetric padding."""
    base_img = sample_carpets["base"]  # 180 x 240 (4:3 aspect ratio)
    target_size = (256, 256)

    res = AspectPreservingResizer.letterbox(base_img, target_size=target_size, pad_color=(128, 128, 128))

    assert res.image.shape == (256, 256, 3)
    assert res.scale == pytest.approx(256 / 240, rel=1e-2)
    assert res.pad_left + res.pad_right + int(round(240 * res.scale)) == 256
    assert res.pad_top + res.pad_bottom + int(round(180 * res.scale)) == 256
    # Padding borders should match pad_color
    assert np.all(res.image[0, 0] == [128, 128, 128])


def test_median_filter_salt_pepper_removal(sample_carpets):
    """Verifies that median filter effectively removes impulse noise (salt and pepper)."""
    noisy_img = sample_carpets["noisy"]

    # Count extreme impulse pixels before filtering
    salt_before = np.sum(noisy_img == 255)
    pepper_before = np.sum(noisy_img == 0)

    filtered = IndustrialFilterPipeline.median_filter(noisy_img, ksize=5)

    salt_after = np.sum(filtered == 255)
    pepper_after = np.sum(filtered == 0)

    # Extreme noise pixels should be dramatically reduced (> 60% reduction)
    assert (salt_after + pepper_after) < (salt_before + pepper_before) * 0.4


def test_bilateral_filter_edge_preservation(sample_carpets):
    """Verifies bilateral filter smooths repetitive texture while preserving high-contrast edges."""
    base_img = sample_carpets["base"]

    bilateral = IndustrialFilterPipeline.bilateral_filter(base_img, d=9, sigma_color=75, sigma_space=75)
    gaussian = IndustrialFilterPipeline.gaussian_filter(base_img, ksize=(9, 9), sigma_x=2.0)

    # Edge sharpness via Laplacian variance: Bilateral must preserve higher sharpness than equal-sized Gaussian
    sharpness_orig = IndustrialFilterPipeline.calculate_sharpness(base_img)
    sharpness_bilateral = IndustrialFilterPipeline.calculate_sharpness(bilateral)
    sharpness_gaussian = IndustrialFilterPipeline.calculate_sharpness(gaussian)

    assert sharpness_bilateral > sharpness_gaussian


def test_unsharp_masking_laplacian_variance(sample_carpets):
    """Verifies that unsharp masking enhances high-frequency detail and increases sharpness."""
    base_img = sample_carpets["base"]

    sharp_img = IndustrialFilterPipeline.unsharp_mask(base_img, strength=1.5)
    sharpness_before = IndustrialFilterPipeline.calculate_sharpness(base_img)
    sharpness_after = IndustrialFilterPipeline.calculate_sharpness(sharp_img)

    assert sharpness_after > sharpness_before
    assert sharp_img.shape == base_img.shape
    assert sharp_img.dtype == np.uint8


def test_clahe_vs_global_equalization_luminance(sample_carpets):
    """Verifies CLAHE in CIELAB space modifies L* without altering chrominance channels a* and b*."""
    low_con = sample_carpets["low_contrast"]

    # Convert to LAB to inspect original a* and b*
    orig_lab = cv2.cvtColor(low_con, cv2.COLOR_BGR2Lab)
    orig_l, orig_a, orig_b = cv2.split(orig_lab)

    # Equalize perceptual
    clahe_enhanced = HistogramEqualizer.enhance_color_perceptual(low_con, method="clahe", space="lab")
    enh_lab = cv2.cvtColor(clahe_enhanced, cv2.COLOR_BGR2Lab)
    enh_l, enh_a, enh_b = cv2.split(enh_lab)

    # Chrominance channels must remain essentially identical (allowing 1-unit rounding in 8-bit roundtrip)
    assert np.max(np.abs(orig_a.astype(int) - enh_a.astype(int))) <= 1
    assert np.max(np.abs(orig_b.astype(int) - enh_b.astype(int))) <= 1

    # Luminance L* must be modified and have higher dynamic range / standard deviation
    assert not np.array_equal(orig_l, enh_l)
    assert np.std(enh_l) > np.std(orig_l)


def test_image_analytics_entropy_and_contrast(sample_carpets):
    """Verifies statistical profiling: low-contrast image has lower RMS contrast than normal carpet."""
    base_img = sample_carpets["base"]
    low_con = sample_carpets["low_contrast"]

    prof_normal = ImageAnalyticsEngine.profile_image(base_img)
    prof_low = ImageAnalyticsEngine.profile_image(low_con)

    assert prof_normal.rms_contrast > prof_low.rms_contrast
    assert prof_normal.dynamic_range > prof_low.dynamic_range
    assert prof_normal.shannon_entropy > 0.0

    comp = ImageAnalyticsEngine.compare_enhancement(low_con, base_img)
    assert comp["deltas"]["contrast_gain"] > 0


def test_cli_pipeline_execution_and_reports():
    """Verifies full benchmark pipeline execution and valid JSON/Markdown artifact creation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "outputs"
        summary = run_full_benchmark(out_dir)

        assert Path(summary["sample_report"]).exists()
        assert Path(summary["benchmark_report"]).exists()
        assert Path(summary["summary_markdown"]).exists()

        # Check JSON integrity
        with open(summary["sample_report"], "r", encoding="utf-8") as f:
            sample_data = json.load(f)
            assert "normal" in sample_data
            assert "metadata" in sample_data["normal"]

        with open(summary["benchmark_report"], "r", encoding="utf-8") as f:
            bench_data = json.load(f)
            assert len(bench_data) >= 7
            for item in bench_data:
                assert "operation" in item
                assert "avg_latency_ms" in item
                assert "throughput_fps" in item
