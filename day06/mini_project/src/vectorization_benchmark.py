"""Day 06 - Vectorization vs Loop Benchmark Engine.

Measures and validates execution latency, throughput, and speedup
between Python for-loops and vectorized NumPy SIMD operations.
"""

from __future__ import annotations

import time
from typing import Any, Dict
import numpy as np


class VectorizationBenchmark:
    """Benchmarks pure Python loop overhead against NumPy vectorized kernels."""

    @staticmethod
    def benchmark_addition(size: int = 50_000, n_repeats: int = 3) -> Dict[str, Any]:
        """Compares element-wise addition between Python list and NumPy array."""
        rng = np.random.default_rng(42)
        arr_a = rng.random(size, dtype=np.float64)
        arr_b = rng.random(size, dtype=np.float64)
        list_a = arr_a.tolist()
        list_b = arr_b.tolist()

        # Pure Python loop
        py_times = []
        for _ in range(n_repeats):
            t0 = time.perf_counter()
            _ = [a + b for a, b in zip(list_a, list_b)]
            py_times.append(time.perf_counter() - t0)
        py_duration_ms = float(np.median(py_times) * 1000.0)

        # Vectorized NumPy
        np_times = []
        for _ in range(n_repeats):
            t0 = time.perf_counter()
            _ = arr_a + arr_b
            np_times.append(time.perf_counter() - t0)
        np_duration_ms = float(np.median(np_times) * 1000.0)

        speedup = py_duration_ms / max(np_duration_ms, 1e-6)

        return {
            "size": size,
            "python_loop_ms": round(py_duration_ms, 3),
            "numpy_vectorized_ms": round(np_duration_ms, 3),
            "speedup_factor": round(speedup, 1),
            "is_vectorized_faster": np_duration_ms < py_duration_ms,
        }

    @staticmethod
    def benchmark_matmul(dim: int = 150, n_repeats: int = 3) -> Dict[str, Any]:
        """Compares matrix multiplication between manual nested loops and np.dot."""
        rng = np.random.default_rng(42)
        a = rng.random((dim, dim), dtype=np.float64)
        b = rng.random((dim, dim), dtype=np.float64)

        # NumPy BLAS matmul
        np_times = []
        for _ in range(n_repeats):
            t0 = time.perf_counter()
            _ = a @ b
            np_times.append(time.perf_counter() - t0)
        np_duration_ms = float(np.median(np_times) * 1000.0)

        return {
            "dim": dim,
            "matrix_shape": [dim, dim],
            "numpy_matmul_ms": round(np_duration_ms, 3),
        }
