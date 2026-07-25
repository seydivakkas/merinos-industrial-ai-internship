"""
Merinos Industrial AI Internship - Day 05
memory_analyzer.py: Memory Layout, Strides, and CPU Cache Locality Analyzer
"""

from typing import Any, Dict
import time
import numpy as np


class MemoryLayoutAnalyzer:
    """Analyzes ndarray memory layout, byte strides, contiguity, and cache locality performance."""

    @staticmethod
    def inspect_array(arr: np.ndarray) -> Dict[str, Any]:
        """Inspects array flags, strides, and memory footprint."""
        flags = arr.flags
        nbytes = int(arr.nbytes)

        return {
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "itemsize": int(arr.itemsize),
            "nbytes": nbytes,
            "nbytes_kb": round(nbytes / 1024, 2),
            "nbytes_mb": round(nbytes / (1024 * 1024), 3),
            "strides": list(arr.strides),
            "c_contiguous": bool(flags["C_CONTIGUOUS"]),
            "f_contiguous": bool(flags["F_CONTIGUOUS"]),
            "owndata": bool(flags["OWNDATA"]),
            "writeable": bool(flags["WRITEABLE"]),
            "base_is_none": arr.base is None,
        }

    @staticmethod
    def benchmark_cache_locality(
        size: int = 2048,
        repeats: int = 5,
    ) -> Dict[str, Any]:
        """
        Benchmarks cache locality impact by comparing row-major (contiguous) vs column-major (strided)
        access on C-contiguous vs Fortran-contiguous carpet matrices.
        """
        # Create C-contiguous array (Row-Major)
        arr_c = np.ones((size, size), dtype=np.float32)
        # Create F-contiguous array (Column-Major)
        arr_f = np.asfortranarray(arr_c)

        def measure_row_traversal(matrix: np.ndarray) -> float:
            times = []
            for _ in range(repeats):
                t0 = time.perf_counter()
                _ = matrix.sum(axis=1)  # Sums elements along each row
                t1 = time.perf_counter()
                times.append(t1 - t0)
            return float(np.median(times))

        def measure_col_traversal(matrix: np.ndarray) -> float:
            times = []
            for _ in range(repeats):
                t0 = time.perf_counter()
                _ = matrix.sum(axis=0)  # Sums elements along each column
                t1 = time.perf_counter()
                times.append(t1 - t0)
            return float(np.median(times))

        # C-contiguous tests:
        # On C-order: row traversal is sequential along cache lines; col traversal jumps strides of 'size * 4' bytes
        time_c_row = measure_row_traversal(arr_c)
        time_c_col = measure_col_traversal(arr_c)

        # F-contiguous tests:
        # On F-order: col traversal is sequential; row traversal jumps strides
        time_f_row = measure_row_traversal(arr_f)
        time_f_col = measure_col_traversal(arr_f)

        return {
            "matrix_dimension": f"{size}x{size}",
            "element_count": size * size,
            "memory_size_mb": round((size * size * 4) / (1024 * 1024), 2),
            "c_contiguous_order": {
                "row_sum_time_ms": round(time_c_row * 1000, 3),
                "col_sum_time_ms": round(time_c_col * 1000, 3),
                "speed_difference_ratio": round(time_c_col / max(time_c_row, 1e-9), 2),
            },
            "f_contiguous_order": {
                "row_sum_time_ms": round(time_f_row * 1000, 3),
                "col_sum_time_ms": round(time_f_col * 1000, 3),
                "speed_difference_ratio": round(time_f_row / max(time_f_col, 1e-9), 2),
            },
            "engineering_insight": (
                "Row-major sequential scanning utilizes CPU cache lines (L1/L2) efficiently without cache thrashing. "
                "Non-contiguous strided scanning causes cache misses and degrades memory bandwidth throughput."
            ),
        }
