"""Day 06 - NumPy Vectorized Array Operations.

Provides high-performance vectorized operations on textile weave matrices,
sensor telemetry arrays, and multi-dimensional carpet tensors.
"""

from __future__ import annotations

from typing import Any, Dict
import numpy as np


class ArrayOperations:
    """Vectorized array operations using pure NumPy SIMD routines."""

    @staticmethod
    def normalize_min_max(arr: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        """Min-Max normalization of an array to [0, 1] range."""
        arr_min = np.min(arr)
        arr_max = np.max(arr)
        if (arr_max - arr_min) < eps:
            return np.zeros_like(arr, dtype=np.float32)
        return (arr - arr_min) / (arr_max - arr_min + eps)

    @staticmethod
    def standardize_z_score(arr: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        """Standardizes array to zero mean and unit variance."""
        mean = np.mean(arr)
        std = np.std(arr)
        if std < eps:
            return np.zeros_like(arr, dtype=np.float32)
        return (arr - mean) / (std + eps)

    @staticmethod
    def compute_matrix_statistics(matrix: np.ndarray) -> Dict[str, float]:
        """Calculates comprehensive summary statistics across array axes."""
        return {
            "mean": float(np.mean(matrix)),
            "std": float(np.std(matrix)),
            "min": float(np.min(matrix)),
            "max": float(np.max(matrix)),
            "sum": float(np.sum(matrix)),
            "frobenius_norm": float(np.linalg.norm(matrix, "fro")),
        }

    @staticmethod
    def broadcast_color_bias(image_matrix: np.ndarray, rgb_bias: np.ndarray) -> np.ndarray:
        """Applies RGB channel bias via NumPy broadcasting without explicit loops."""
        if image_matrix.ndim != 3 or image_matrix.shape[2] != 3:
            raise ValueError("image_matrix must have shape (H, W, 3).")
        if rgb_bias.shape != (3,):
            raise ValueError("rgb_bias must have shape (3,).")
        # Broadcasting: (H, W, 3) + (3,)
        return np.clip(image_matrix.astype(np.float32) + rgb_bias, 0.0, 255.0).astype(image_matrix.dtype)

    @staticmethod
    def threshold_matrix(matrix: np.ndarray, threshold: float) -> np.ndarray:
        """Vectorized boolean mask thresholding."""
        return (matrix >= threshold).astype(np.uint8)
