"""Unit tests for Day 06 NumPy Vectorized Operations and Matrix Toolkits."""

import numpy as np
import pytest

from day06.mini_project.src.array_ops import ArrayOperations
from day06.mini_project.src.image_matrix import ImageMatrixToolkit
from day06.mini_project.src.vectorization_benchmark import VectorizationBenchmark


def test_normalize_min_max():
    arr = np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32)
    norm = ArrayOperations.normalize_min_max(arr)
    assert np.isclose(norm[0], 0.0)
    assert np.isclose(norm[-1], 1.0)
    assert np.all(norm >= 0.0) and np.all(norm <= 1.0)


def test_standardize_z_score():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    std_arr = ArrayOperations.standardize_z_score(arr)
    assert np.isclose(np.mean(std_arr), 0.0, atol=1e-6)
    assert np.isclose(np.std(std_arr), 1.0, atol=1e-5)


def test_matrix_statistics():
    mat = np.ones((10, 10), dtype=np.float32) * 5.0
    stats = ArrayOperations.compute_matrix_statistics(mat)
    assert stats["mean"] == 5.0
    assert stats["min"] == 5.0
    assert stats["max"] == 5.0
    assert stats["sum"] == 500.0


def test_broadcast_color_bias():
    img = np.zeros((4, 4, 3), dtype=np.uint8)
    bias = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    biased = ArrayOperations.broadcast_color_bias(img, bias)
    assert biased.shape == (4, 4, 3)
    assert np.all(biased[:, :, 0] == 10)
    assert np.all(biased[:, :, 1] == 20)
    assert np.all(biased[:, :, 2] == 30)


def test_threshold_matrix():
    mat = np.array([[10, 50], [60, 100]], dtype=np.float32)
    mask = ArrayOperations.threshold_matrix(mat, threshold=55.0)
    assert np.array_equal(mask, np.array([[0, 0], [1, 1]], dtype=np.uint8))


def test_vectorization_benchmark():
    res = VectorizationBenchmark.benchmark_addition(size=10_000, n_repeats=2)
    assert "speedup_factor" in res
    assert res["is_vectorized_faster"] is True
    assert res["size"] == 10_000


def test_image_matrix_toolkit():
    patch = ImageMatrixToolkit.generate_synthetic_carpet_patch(64, 64)
    assert patch.shape == (64, 64)
    assert patch.dtype == np.uint8

    subpatches = ImageMatrixToolkit.slice_patches(patch, patch_size=32)
    assert len(subpatches) == 4
    for sp in subpatches:
        assert sp.shape == (32, 32)

    energy = ImageMatrixToolkit.compute_patch_energy(patch)
    assert energy > 0.0
