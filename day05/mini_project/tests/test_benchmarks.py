"""
Merinos Industrial AI Internship - Day 05
test_benchmarks.py: Comprehensive Test Suite for Vectorized Operations & Memory Analyzer
"""

from pathlib import Path
import json
import numpy as np
import pytest

from day05.mini_project.src.generator import CarpetPatternGenerator
from day05.mini_project.src.memory_analyzer import MemoryLayoutAnalyzer
from day05.mini_project.src.benchmark import BenchmarkEngine
from day05.mini_project.src import operations as ops

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"


@pytest.fixture
def sample_pattern() -> np.ndarray:
    return CarpetPatternGenerator.generate_rgb_pattern(64, 64, seed=42)


@pytest.fixture
def sample_gray() -> np.ndarray:
    return CarpetPatternGenerator.generate_knot_grid(64, 64, seed=42)


@pytest.fixture
def sample_features() -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.standard_normal((8, 64 * 64)).astype(np.float32)


def test_generator_shapes_and_dtypes():
    pattern = CarpetPatternGenerator.generate_rgb_pattern(128, 128)
    assert pattern.shape == (128, 128, 3)
    assert pattern.dtype == np.float32
    assert pattern.min() >= 0.0
    assert pattern.max() <= 1.0

    knots = CarpetPatternGenerator.generate_knot_grid(64, 64, knot_range=(400.0, 800.0))
    assert knots.shape == (64, 64)
    assert knots.dtype == np.float32
    assert knots.min() >= 400.0
    assert knots.max() <= 800.0


def test_vectorized_vs_naive_luma_numerical_equivalence(sample_pattern):
    luma_n = ops.luma_naive(sample_pattern)
    luma_v = ops.luma_vectorized(sample_pattern)
    luma_e = ops.luma_einsum(sample_pattern)

    assert luma_n.shape == (64, 64)
    assert luma_v.shape == (64, 64)
    assert luma_e.shape == (64, 64)

    assert np.allclose(luma_n, luma_v, atol=1e-5, rtol=1e-5)
    assert np.allclose(luma_v, luma_e, atol=1e-5, rtol=1e-5)


def test_vectorized_vs_naive_min_max_numerical_equivalence(sample_gray):
    norm_n = ops.min_max_naive(sample_gray)
    norm_v = ops.min_max_vectorized(sample_gray)

    assert norm_n.shape == sample_gray.shape
    assert norm_v.shape == sample_gray.shape
    assert np.allclose(norm_n, norm_v, atol=1e-5, rtol=1e-5)
    assert norm_v.min() == pytest.approx(0.0, abs=1e-5)
    assert norm_v.max() == pytest.approx(1.0, abs=1e-5)


def test_vectorized_vs_naive_z_score_numerical_equivalence(sample_gray):
    z_n = ops.z_score_naive(sample_gray)
    z_v = ops.z_score_vectorized(sample_gray)

    assert z_n.shape == sample_gray.shape
    assert z_v.shape == sample_gray.shape
    assert np.allclose(z_n, z_v, atol=1e-4, rtol=1e-4)
    assert float(np.mean(z_v)) == pytest.approx(0.0, abs=1e-4)
    assert float(np.std(z_v)) == pytest.approx(1.0, abs=1e-4)


def test_vectorized_vs_naive_gram_matrix_equivalence(sample_features):
    gram_n = ops.gram_matrix_naive(sample_features)
    gram_v = ops.gram_matrix_vectorized(sample_features)
    gram_e = ops.gram_matrix_einsum(sample_features)

    assert gram_n.shape == (8, 8)
    assert gram_v.shape == (8, 8)
    assert gram_e.shape == (8, 8)

    assert np.allclose(gram_n, gram_v, atol=1e-4, rtol=1e-4)
    assert np.allclose(gram_v, gram_e, atol=1e-4, rtol=1e-4)


def test_vectorized_vs_naive_spatial_filter_equivalence(sample_gray):
    # Test with 32x32 crop for fast test execution
    crop = sample_gray[:32, :32]
    filtered_n = ops.spatial_box_filter_naive(crop, kernel_size=3)
    filtered_v = ops.spatial_box_filter_vectorized(crop, kernel_size=3)

    assert filtered_n.shape == (30, 30)
    assert filtered_v.shape == (30, 30)
    assert np.allclose(filtered_n, filtered_v, atol=1e-5, rtol=1e-5)


def test_vectorized_speedup_factor(sample_pattern):
    # Vectorized luma should be at least 5x faster than naive loop even on 64x64
    m_naive = BenchmarkEngine.measure_function(ops.luma_naive, sample_pattern, warmup=1, repeats=3, number=1)
    m_vec = BenchmarkEngine.measure_function(ops.luma_vectorized, sample_pattern, warmup=1, repeats=3, number=1)

    speedup = m_naive["mean_ms"] / max(m_vec["mean_ms"], 1e-6)
    assert speedup > 3.0, f"Expected speedup > 3.0x, observed {speedup:.1f}x"


def test_memory_analyzer_contiguity_and_strides():
    arr_c = np.zeros((100, 100), dtype=np.float32)
    info_c = MemoryLayoutAnalyzer.inspect_array(arr_c)
    assert info_c["c_contiguous"] is True
    assert info_c["f_contiguous"] is False
    assert info_c["nbytes"] == 100 * 100 * 4
    assert info_c["strides"] == [400, 4]

    arr_f = np.asfortranarray(arr_c)
    info_f = MemoryLayoutAnalyzer.inspect_array(arr_f)
    assert info_f["c_contiguous"] is False
    assert info_f["f_contiguous"] is True
    assert info_f["strides"] == [4, 400]

    # Non-contiguous slice
    slice_non_contig = arr_c[::2, ::2]
    info_slice = MemoryLayoutAnalyzer.inspect_array(slice_non_contig)
    assert info_slice["c_contiguous"] is False
    assert info_slice["owndata"] is False


def test_cache_locality_impact_row_vs_col_major():
    res = MemoryLayoutAnalyzer.benchmark_cache_locality(size=256, repeats=3)
    assert "c_contiguous_order" in res
    assert "f_contiguous_order" in res
    assert res["c_contiguous_order"]["row_sum_time_ms"] > 0
    assert res["c_contiguous_order"]["col_sum_time_ms"] > 0


def test_benchmark_engine_run_and_artifacts(tmp_path):
    config_path = CONFIGS_DIR / "benchmark_config.json"
    engine = BenchmarkEngine(config_path=config_path, output_dir=tmp_path)
    res = engine.execute_and_export()

    assert "benchmark_results" in res
    assert "cache_results" in res

    bench_json = Path(res["benchmark_json_path"])
    cache_json = Path(res["cache_json_path"])
    summary_md = Path(res["summary_md_path"])

    assert bench_json.exists()
    assert cache_json.exists()
    assert summary_md.exists()

    with open(bench_json, "r", encoding="utf-8") as f:
        bench_data = json.load(f)
    assert "luma_conversion" in bench_data
    assert bench_data["luma_conversion"]["speedup_factor"] > 1.0

    with open(summary_md, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "Merinos Industrial AI" in md_text
    assert "Speedup" in md_text
