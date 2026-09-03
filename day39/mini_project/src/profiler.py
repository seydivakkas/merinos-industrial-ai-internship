# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Performans Profilleme Motoru: Gecikme (P50/P95/P99), QPS, Bellek ve Hassasiyet Analizi
"""

import os
import time
import psutil
import datetime
import numpy as np
import torch
from typing import List, Dict, Any, Tuple, Optional

from day39.mini_project.src.models import (
    LatencyDistribution,
    ModelSizeReport,
    AccuracyPreservation,
    HardwareProfiling,
    EngineBenchmarkItem,
    ThreadScalingItem,
    EdgeBenchmarkReport
)
from day39.mini_project.src.edge_engine import EdgeInferenceEngine


class PerformanceProfiler:
    """Endüstriyel Edge PC için Kapsamlı Çıkarım ve Donanım Profilleyicisi."""

    def __init__(self, warmup_iters: int = 10, benchmark_iters: int = 100):
        self.warmup_iters = warmup_iters
        self.benchmark_iters = benchmark_iters

    def compute_latency_distribution(self, latencies_ms: List[float]) -> LatencyDistribution:
        """Gecikme listesinden persentil (P50, P95, P99) ve istatistikleri üretir."""
        arr = np.array(latencies_ms, dtype=np.float64)
        return LatencyDistribution(
            p50_ms=round(float(np.percentile(arr, 50)), 3),
            p95_ms=round(float(np.percentile(arr, 95)), 3),
            p99_ms=round(float(np.percentile(arr, 99)), 3),
            mean_ms=round(float(np.mean(arr)), 3),
            std_ms=round(float(np.std(arr)), 3),
            min_ms=round(float(np.min(arr)), 3),
            max_ms=round(float(np.max(arr)), 3)
        )

    def measure_accuracy_preservation(
        self,
        fp32_output: np.ndarray,
        int8_output: np.ndarray,
        min_cosine_threshold: float = 0.985,
        max_mae_threshold: float = 0.025
    ) -> AccuracyPreservation:
        """FP32 referans çıktısı ile INT8 çıktısı arasındaki sapmayı ölçer."""
        y_fp = fp32_output.flatten().astype(np.float64)
        y_int = int8_output.flatten().astype(np.float64)

        # Kosinüs Benzerliği
        norm_fp = np.linalg.norm(y_fp)
        norm_int = np.linalg.norm(y_int)
        if norm_fp > 1e-12 and norm_int > 1e-12:
            cos_sim = float(np.dot(y_fp, y_int) / (norm_fp * norm_int))
        else:
            cos_sim = 1.0

        # Mutlak Hatalar
        diff = np.abs(y_fp - y_int)
        mae = float(np.mean(diff))
        max_ae = float(np.max(diff))

        is_tolerable = (cos_sim >= min_cosine_threshold) and (mae <= max_mae_threshold)

        return AccuracyPreservation(
            cosine_similarity=round(cos_sim, 5),
            mean_absolute_error=round(mae, 5),
            max_absolute_error=round(max_ae, 5),
            is_tolerable=is_tolerable
        )

    def profile_onnx_engine(
        self,
        engine: EdgeInferenceEngine,
        model_name: str,
        engine_type: str,
        input_data: np.ndarray,
        fp32_baseline_output: Optional[np.ndarray] = None
    ) -> EngineBenchmarkItem:
        """Tek bir ONNX motorunun gecikme, bellek ve verimini profiller."""
        engine.warmup(self.warmup_iters)

        latencies = []
        feed_key = engine.input_names[0]
        feed = {feed_key: input_data}

        t_start_total = time.perf_counter()
        latest_output = None
        for _ in range(self.benchmark_iters):
            t0 = time.perf_counter()
            out = engine.run(feed)
            latencies.append((time.perf_counter() - t0) * 1000.0)
            latest_output = out[0]
        total_time_sec = time.perf_counter() - t_start_total

        latency_dist = self.compute_latency_distribution(latencies)
        qps = round(self.benchmark_iters / max(total_time_sec, 1e-6), 1)

        # Bellek Kullanımı (RSS MB)
        process = psutil.Process(os.getpid())
        mem_rss_mb = round(process.memory_info().rss / (1024 * 1024), 2)

        hardware = HardwareProfiling(
            thread_count=engine.num_threads,
            cpu_architecture="x86_64",
            memory_rss_mb=mem_rss_mb,
            throughput_qps=qps
        )

        accuracy = None
        if fp32_baseline_output is not None and latest_output is not None:
            accuracy = self.measure_accuracy_preservation(fp32_baseline_output, latest_output)

        return EngineBenchmarkItem(
            model_name=model_name,
            engine_type=engine_type,
            latency=latency_dist,
            accuracy=accuracy,
            hardware=hardware
        )

    def profile_pytorch_module(
        self,
        module: torch.nn.Module,
        model_name: str,
        input_data: np.ndarray
    ) -> Tuple[EngineBenchmarkItem, np.ndarray]:
        """PyTorch modelinin ham CPU çıkarım gecikmesini profiller."""
        module.eval()
        tensor_in = torch.from_numpy(input_data)

        # Isınma
        with torch.no_grad():
            for _ in range(self.warmup_iters):
                _ = module(tensor_in)

        latencies = []
        latest_out = None
        t_start_total = time.perf_counter()
        with torch.no_grad():
            for _ in range(self.benchmark_iters):
                t0 = time.perf_counter()
                out = module(tensor_in)
                latencies.append((time.perf_counter() - t0) * 1000.0)
                latest_out = out.numpy()
        total_time_sec = time.perf_counter() - t_start_total

        latency_dist = self.compute_latency_distribution(latencies)
        qps = round(self.benchmark_iters / max(total_time_sec, 1e-6), 1)

        process = psutil.Process(os.getpid())
        mem_rss_mb = round(process.memory_info().rss / (1024 * 1024), 2)

        item = EngineBenchmarkItem(
            model_name=model_name,
            engine_type="PyTorch_FP32",
            latency=latency_dist,
            accuracy=None,
            hardware=HardwareProfiling(
                thread_count=torch.get_num_threads(),
                cpu_architecture="x86_64",
                memory_rss_mb=mem_rss_mb,
                throughput_qps=qps
            )
        )
        return item, latest_out

    def profile_thread_scaling(
        self,
        model_path: str,
        input_data: np.ndarray,
        thread_counts: List[int] = [1, 2, 4]
    ) -> List[ThreadScalingItem]:
        """Farklı CPU thread sayıları (1, 2, 4) için gecikme ve verim ölçeklemesini test eder."""
        results = []

        for threads in thread_counts:
            engine = EdgeInferenceEngine(model_path=model_path, num_threads=threads)
            engine.warmup(self.warmup_iters)
            feed_key = engine.input_names[0]
            feed = {feed_key: input_data}

            latencies = []
            t_start = time.perf_counter()
            for _ in range(self.benchmark_iters):
                t0 = time.perf_counter()
                _ = engine.run(feed)
                latencies.append((time.perf_counter() - t0) * 1000.0)
            total_sec = time.perf_counter() - t_start

            mean_lat = round(float(np.mean(latencies)), 3)
            qps = round(self.benchmark_iters / max(total_sec, 1e-6), 1)

            results.append(ThreadScalingItem(
                thread_count=threads,
                mean_latency_ms=mean_lat,
                throughput_qps=qps
            ))

        return results
