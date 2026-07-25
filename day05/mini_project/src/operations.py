"""
Merinos Industrial AI Internship - Day 05
operations.py: Comparative Numerical Implementations (Naive Loop vs Vectorized NumPy vs Einsum)
"""

from typing import Tuple
import numpy as np


# ---------------------------------------------------------------------------
# 1. Luma Channel Weighting (RGB to Luminance)
# Formula: Y = 0.299 * R + 0.587 * G + 0.114 * B
# ---------------------------------------------------------------------------
LUMA_WEIGHTS = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def luma_naive(img: np.ndarray) -> np.ndarray:
    """Computes grayscale luminance using nested pure Python for loops."""
    h, w, c = img.shape
    out = np.zeros((h, w), dtype=np.float32)
    w_r, w_g, w_b = float(LUMA_WEIGHTS[0]), float(LUMA_WEIGHTS[1]), float(LUMA_WEIGHTS[2])

    for i in range(h):
        for j in range(w):
            val = (
                float(img[i, j, 0]) * w_r +
                float(img[i, j, 1]) * w_g +
                float(img[i, j, 2]) * w_b
            )
            out[i, j] = val
    return out


def luma_vectorized(img: np.ndarray) -> np.ndarray:
    """Computes grayscale luminance using NumPy broadcasting and vector dot product."""
    return np.sum(img * LUMA_WEIGHTS, axis=-1, dtype=np.float32)


def luma_einsum(img: np.ndarray) -> np.ndarray:
    """Computes grayscale luminance using Einstein summation notation."""
    return np.einsum("hwc,c->hw", img, LUMA_WEIGHTS, dtype=np.float32)


# ---------------------------------------------------------------------------
# 2. Min-Max Normalization
# Formula: X_norm = (X - X_min) / (X_max - X_min)
# ---------------------------------------------------------------------------
def min_max_naive(matrix: np.ndarray) -> np.ndarray:
    """Min-Max normalization using Python loops for extremum search and array scaling."""
    shape = matrix.shape
    flat = matrix.flatten()
    n = len(flat)

    min_val = float(flat[0])
    max_val = float(flat[0])
    for i in range(1, n):
        v = float(flat[i])
        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v

    diff = max_val - min_val
    if diff == 0.0:
        diff = 1e-8

    out = np.zeros(n, dtype=np.float32)
    for i in range(n):
        out[i] = (float(flat[i]) - min_val) / diff

    return out.reshape(shape)


def min_max_vectorized(matrix: np.ndarray) -> np.ndarray:
    """Min-Max normalization using vectorized NumPy SIMD operations."""
    min_val = matrix.min()
    max_val = matrix.max()
    diff = max_val - min_val
    if diff == 0:
        diff = 1e-8
    return ((matrix - min_val) / diff).astype(np.float32)


# ---------------------------------------------------------------------------
# 3. Z-Score Standardization
# Formula: X_std = (X - mu) / sigma
# ---------------------------------------------------------------------------
def z_score_naive(matrix: np.ndarray) -> np.ndarray:
    """Z-Score standardization using Python loops for mean and variance estimation."""
    shape = matrix.shape
    flat = matrix.flatten()
    n = len(flat)

    # 1. Compute Mean
    total = 0.0
    for i in range(n):
        total += float(flat[i])
    mean = total / n

    # 2. Compute Variance
    var_sum = 0.0
    for i in range(n):
        diff = float(flat[i]) - mean
        var_sum += diff * diff
    std = (var_sum / n) ** 0.5
    if std == 0.0:
        std = 1e-8

    # 3. Standardize
    out = np.zeros(n, dtype=np.float32)
    for i in range(n):
        out[i] = (float(flat[i]) - mean) / std

    return out.reshape(shape)


def z_score_vectorized(matrix: np.ndarray) -> np.ndarray:
    """Z-Score standardization using vectorized NumPy operations."""
    mean = np.mean(matrix)
    std = np.std(matrix)
    if std == 0:
        std = 1e-8
    return ((matrix - mean) / std).astype(np.float32)


# ---------------------------------------------------------------------------
# 4. Gram Matrix (Feature Correlation for Texture & Style Representation)
# Given F of shape (C, N) where N = H * W:
# G[i, j] = sum_k F[i, k] * F[j, k]
# ---------------------------------------------------------------------------
def gram_matrix_naive(features: np.ndarray) -> np.ndarray:
    """Computes Gram matrix of shape (C, C) using 3 nested Python loops."""
    c, n = features.shape
    out = np.zeros((c, c), dtype=np.float32)

    for i in range(c):
        for j in range(c):
            acc = 0.0
            for k in range(n):
                acc += float(features[i, k]) * float(features[j, k])
            out[i, j] = acc
    return out


def gram_matrix_vectorized(features: np.ndarray) -> np.ndarray:
    """Computes Gram matrix of shape (C, C) using NumPy matrix multiplication (BLAS)."""
    return np.matmul(features, features.T, dtype=np.float32)


def gram_matrix_einsum(features: np.ndarray) -> np.ndarray:
    """Computes Gram matrix using Einstein summation index contraction."""
    return np.einsum("ik,jk->ij", features, features, dtype=np.float32)


# ---------------------------------------------------------------------------
# 5. Spatial Box Filter (2D Convolution on Carpet Surface)
# ---------------------------------------------------------------------------
def spatial_box_filter_naive(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Applies a (K, K) uniform box blur filter using nested Python coordinate loops."""
    h, w = image.shape
    k = kernel_size
    out_h = h - k + 1
    out_w = w - k + 1
    out = np.zeros((out_h, out_w), dtype=np.float32)
    inv_k2 = 1.0 / float(k * k)

    for i in range(out_h):
        for j in range(out_w):
            window_sum = 0.0
            for ki in range(k):
                for kj in range(k):
                    window_sum += float(image[i + ki, j + kj])
            out[i, j] = window_sum * inv_k2

    return out


def spatial_box_filter_vectorized(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Applies a (K, K) uniform box blur using NumPy sliding_window_view with vectorized mean reduction.
    """
    windows = np.lib.stride_tricks.sliding_window_view(image, (kernel_size, kernel_size))
    # windows shape: (out_h, out_w, k, k)
    return np.mean(windows, axis=(-2, -1), dtype=np.float32)
