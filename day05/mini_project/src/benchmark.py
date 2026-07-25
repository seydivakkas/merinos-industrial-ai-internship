"""
Merinos Industrial AI Internship - Day 05
benchmark.py: Comprehensive Performance Benchmarking Engine
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import json
import time
import tracemalloc
import numpy as np

from day05.mini_project.src.generator import CarpetPatternGenerator
from day05.mini_project.src.memory_analyzer import MemoryLayoutAnalyzer
from day05.mini_project.src import operations as ops


class BenchmarkEngine:
    """Conducts rigorous statistical benchmarks comparing naive vs vectorized implementations."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = config_path or base_dir / "configs" / "benchmark_config.json"
        self.output_dir = output_dir or base_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    @staticmethod
    def measure_function(
        func: Callable[..., Any],
        *args: Any,
        warmup: int = 2,
        repeats: int = 5,
        number: int = 3,
        **kwargs: Any,
    ) -> Dict[str, float]:
        """Runs warmup and timed repetitions, collecting latency statistics in milliseconds."""
        # 1. Warmup runs
        for _ in range(warmup):
            _ = func(*args, **kwargs)

        # 2. Timing measurements
        iteration_times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            for _ in range(number):
                _ = func(*args, **kwargs)
            t1 = time.perf_counter()
            iteration_times.append((t1 - t0) / float(number))

        times_ms = np.array(iteration_times) * 1000.0

        # 3. Peak memory measurement
        tracemalloc.start()
        _ = func(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            "mean_ms": round(float(np.mean(times_ms)), 4),
            "std_ms": round(float(np.std(times_ms)), 4),
            "min_ms": round(float(np.min(times_ms)), 4),
            "max_ms": round(float(np.max(times_ms)), 4),
            "p95_ms": round(float(np.percentile(times_ms, 95)), 4),
            "peak_memory_kb": round(peak / 1024.0, 2),
        }

    def run_all_benchmarks(self, max_dim: int = 128) -> Dict[str, Any]:
        """
        Executes benchmarks across all registered operations.
        max_dim limits naive nested loop matrix size to keep testing fast and deterministic.
        """
        params = self.config.get("benchmark_parameters", {})
        warmup = 1
        repeats = 3
        number = 1

        # Generate test inputs
        img_rgb = CarpetPatternGenerator.generate_rgb_pattern(max_dim, max_dim, seed=42)
        gray_mat = CarpetPatternGenerator.generate_knot_grid(max_dim, max_dim, seed=42)
        # For Gram matrix: features of shape (C, N) where C=8, N = max_dim * max_dim
        feature_mat = np.random.default_rng(42).standard_normal((8, max_dim * max_dim)).astype(np.float32)

        results: Dict[str, Any] = {}

        # 1. Luma Channel Weighting
        naive_luma = self.measure_function(ops.luma_naive, img_rgb, warmup=warmup, repeats=repeats, number=number)
        vec_luma = self.measure_function(ops.luma_vectorized, img_rgb, warmup=warmup, repeats=repeats, number=number)
        einsum_luma = self.measure_function(ops.luma_einsum, img_rgb, warmup=warmup, repeats=repeats, number=number)
        speedup_luma = round(naive_luma["mean_ms"] / max(vec_luma["mean_ms"], 1e-6), 1)

        results["luma_conversion"] = {
            "dimension": f"{max_dim}x{max_dim}x3",
            "naive": naive_luma,
            "vectorized": vec_luma,
            "einsum": einsum_luma,
            "speedup_factor": speedup_luma,
            "throughput_mpx_sec": round((max_dim * max_dim / 1e6) / (vec_luma["mean_ms"] / 1000.0), 2),
        }

        # 2. Min-Max Normalization
        naive_norm = self.measure_function(ops.min_max_naive, gray_mat, warmup=warmup, repeats=repeats, number=number)
        vec_norm = self.measure_function(ops.min_max_vectorized, gray_mat, warmup=warmup, repeats=repeats, number=number)
        speedup_norm = round(naive_norm["mean_ms"] / max(vec_norm["mean_ms"], 1e-6), 1)

        results["min_max_normalization"] = {
            "dimension": f"{max_dim}x{max_dim}",
            "naive": naive_norm,
            "vectorized": vec_norm,
            "speedup_factor": speedup_norm,
            "throughput_mpx_sec": round((max_dim * max_dim / 1e6) / (vec_norm["mean_ms"] / 1000.0), 2),
        }

        # 3. Z-Score Standardization
        naive_z = self.measure_function(ops.z_score_naive, gray_mat, warmup=warmup, repeats=repeats, number=number)
        vec_z = self.measure_function(ops.z_score_vectorized, gray_mat, warmup=warmup, repeats=repeats, number=number)
        speedup_z = round(naive_z["mean_ms"] / max(vec_z["mean_ms"], 1e-6), 1)

        results["z_score_standardization"] = {
            "dimension": f"{max_dim}x{max_dim}",
            "naive": naive_z,
            "vectorized": vec_z,
            "speedup_factor": speedup_z,
            "throughput_mpx_sec": round((max_dim * max_dim / 1e6) / (vec_z["mean_ms"] / 1000.0), 2),
        }

        # 4. Gram Matrix Computation
        naive_gram = self.measure_function(ops.gram_matrix_naive, feature_mat, warmup=warmup, repeats=repeats, number=number)
        vec_gram = self.measure_function(ops.gram_matrix_vectorized, feature_mat, warmup=warmup, repeats=repeats, number=number)
        einsum_gram = self.measure_function(ops.gram_matrix_einsum, feature_mat, warmup=warmup, repeats=repeats, number=number)
        speedup_gram = round(naive_gram["mean_ms"] / max(vec_gram["mean_ms"], 1e-6), 1)

        results["gram_matrix_computation"] = {
            "dimension": f"16x{max_dim * max_dim}",
            "naive": naive_gram,
            "vectorized": vec_gram,
            "einsum": einsum_gram,
            "speedup_factor": speedup_gram,
            "throughput_mpx_sec": round((max_dim * max_dim / 1e6) / (vec_gram["mean_ms"] / 1000.0), 2),
        }

        # 5. Spatial Box Filter (3x3)
        # Use smaller dim for naive 4-nested loops
        filter_dim = min(max_dim, 64)
        small_gray = CarpetPatternGenerator.generate_knot_grid(filter_dim, filter_dim, seed=42)
        naive_filter = self.measure_function(ops.spatial_box_filter_naive, small_gray, 3, warmup=1, repeats=3, number=1)
        vec_filter = self.measure_function(ops.spatial_box_filter_vectorized, small_gray, 3, warmup=1, repeats=3, number=1)
        speedup_filter = round(naive_filter["mean_ms"] / max(vec_filter["mean_ms"], 1e-6), 1)

        results["spatial_box_filtering"] = {
            "dimension": f"{filter_dim}x{filter_dim} (Kernel: 3x3)",
            "naive": naive_filter,
            "vectorized": vec_filter,
            "speedup_factor": speedup_filter,
            "throughput_mpx_sec": round((filter_dim * filter_dim / 1e6) / (vec_filter["mean_ms"] / 1000.0), 2),
        }

        return results

    def generate_summary_markdown(self, benchmark_data: Dict[str, Any], cache_data: Dict[str, Any]) -> str:
        """Generates an enterprise-grade Markdown performance table."""
        lines = [
            "# Merinos Industrial AI — Day 05: NumPy Vektörizasyon Benchmark Raporu",
            "",
            "> **Donanım & Çevre:** Python 3.14+ | NumPy 2.x (SIMD / BLAS)  ",
            f"> **Tarih:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
            "",
            "## 1. Vektörizasyon ve SIMD Hızlanma Özeti",
            "",
            "| Operasyon | Matris Boyutu | Saf Python (ms) | NumPy Vectorized (ms) | Hızlanma Katsayısı (Speedup) | Throughput (MPx/s) |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for op_name, data in benchmark_data.items():
            dim = data.get("dimension", "-")
            naive_t = data.get("naive", {}).get("mean_ms", 0.0)
            vec_t = data.get("vectorized", {}).get("mean_ms", 0.0)
            speedup = data.get("speedup_factor", 1.0)
            throughput = data.get("throughput_mpx_sec", 0.0)
            lines.append(f"| **{op_name}** | `{dim}` | `{naive_t:.2f} ms` | **`{vec_t:.3f} ms`** | **`{speedup}x`** | `{throughput} MPx/s` |")

        lines.extend([
            "",
            "## 2. Bellek Düzeni ve CPU Cache Yerelliği Analizi",
            "",
            f"- **Test Matrisi:** `{cache_data.get('matrix_dimension')}` ({cache_data.get('memory_size_mb')} MB)",
            f"- **C-Contiguous (Row-Major) Satır Taraması:** `{cache_data.get('c_contiguous_order', {}).get('row_sum_time_ms')} ms`",
            f"- **C-Contiguous (Row-Major) Sütun Taraması (Strided):** `{cache_data.get('c_contiguous_order', {}).get('col_sum_time_ms')} ms` (Cache Miss Farkı: **`{cache_data.get('c_contiguous_order', {}).get('speed_difference_ratio')}x`**)",
            f"- **Fortran-Contiguous (Col-Major) Sütun Taraması:** `{cache_data.get('f_contiguous_order', {}).get('col_sum_time_ms')} ms`",
            "",
            "## 3. Mühendislik Çıkarımları",
            "1. **SIMD & Vektörizasyon Kazancı:** Saf Python döngülerinin C seviyesinde vektörize edilmesi, halı piksel manipülasyonlarında **10x - 100x+** hız artışı sağlar.",
            "2. **Cache Locality Önemi:** C-Contiguous bir halı desen matrisinde satır bazlı bellek erişimi, önbellek atlamalarını (cache thrashing) önleyerek bellek bant genişliğini maksimize eder.",
            "3. **Einstein Summation (`np.einsum`):** Yüksek boyutlu tensör daralmalarında ve Gram matrisinde standart matris çarpımı (`matmul`) seviyesinde verimlilik sunar.",
        ])

        return "\n".join(lines)

    def execute_and_export(self) -> Dict[str, Any]:
        """Runs benchmarks and saves all JSON and Markdown output artifacts."""
        # 1. Run benchmarks
        bench_results = self.run_all_benchmarks(max_dim=128)

        # 2. Run memory layout and cache locality analysis
        cache_results = MemoryLayoutAnalyzer.benchmark_cache_locality(size=512, repeats=3)

        # 3. Export JSON artifacts
        bench_json_path = self.output_dir / "benchmark_results.json"
        with open(bench_json_path, "w", encoding="utf-8") as f:
            json.dump(bench_results, f, indent=2, ensure_ascii=False)

        cache_json_path = self.output_dir / "memory_layout_report.json"
        with open(cache_json_path, "w", encoding="utf-8") as f:
            json.dump(cache_results, f, indent=2, ensure_ascii=False)

        # 4. Export Markdown summary
        md_content = self.generate_summary_markdown(bench_results, cache_results)
        summary_md_path = self.output_dir / "performance_summary.md"
        with open(summary_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return {
            "benchmark_results": bench_results,
            "cache_results": cache_results,
            "benchmark_json_path": str(bench_json_path),
            "cache_json_path": str(cache_json_path),
            "summary_md_path": str(summary_md_path),
        }


if __name__ == "__main__":
    engine = BenchmarkEngine()
    print("=" * 60)
    print("Running Day 05 NumPy Vectorization Benchmarks...")
    outputs = engine.execute_and_export()
    print("Benchmarks complete!")
    print(f"Results saved to: {outputs['benchmark_json_path']}")
    print(f"Summary saved to: {outputs['summary_md_path']}")
    print("=" * 60)
