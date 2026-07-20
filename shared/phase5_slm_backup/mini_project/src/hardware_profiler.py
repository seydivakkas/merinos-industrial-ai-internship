"""
Merinos Industrial AI Internship - Day 29
Hardware Profiler, VRAM / KV-Cache Estimator & Roofline Bottleneck Analyzer.

Provides:
1. Analytical VRAM footprint calculation across precisions (FP32, FP16/BF16, INT8, INT4/NF4).
2. KV Cache memory scaling for Multi-Head Attention (MHA) vs. Grouped-Query Attention (GQA).
3. Roofline Model analyzer (Arithmetic Intensity vs. Peak FLOPs & Bandwidth).
4. Token throughput & latency simulator (TTFT vs. TPOT).
5. Comprehensive SLM candidate benchmark evaluation.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from day29.mini_project.src.models import (
    HardwareTarget,
    ModelCandidateSpec,
    QuantizationDetail,
    RooflinePoint,
)

# Precision bytes specification
BYTES_PER_PARAM: Dict[str, float] = {
    "FP32": 4.0,
    "FP16": 2.0,
    "BF16": 2.0,
    "INT8": 1.0,
    "INT4": 0.5,
    "NF4": 0.5,
}

BITS_PER_PARAM: Dict[str, int] = {
    "FP32": 32,
    "FP16": 16,
    "BF16": 16,
    "INT8": 8,
    "INT4": 4,
    "NF4": 4,
}


class HardwareProfiler:
    """
    Industrial hardware profiling engine for edge and on-premise SLM deployment.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        specs_path: Optional[Path] = None
    ):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = config_path or base_dir / "configs" / "llm_config.json"
        self.specs_path = specs_path or base_dir / "fixtures" / "slm_benchmark_specs.json"

        self.hardware_targets: Dict[str, HardwareTarget] = {}
        self.candidate_models: List[ModelCandidateSpec] = []
        self._load_data()

    def _load_data(self) -> None:
        """Loads hardware profiles and candidate specifications from disk."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                hw_list = cfg.get("hardware_targets", [])
                for item in hw_list:
                    target = HardwareTarget(**item)
                    # Index by multiple common aliases
                    name_lower = target.name.lower()
                    if "4060" in name_lower:
                        self.hardware_targets["rtx_4060_8gb"] = target
                        self.hardware_targets["rtx_4060"] = target
                    elif "3060" in name_lower:
                        self.hardware_targets["rtx_3060_12gb"] = target
                        self.hardware_targets["rtx_3060"] = target
                    elif "a10g" in name_lower:
                        self.hardware_targets["a10g_24gb"] = target
                        self.hardware_targets["a10g"] = target
                    self.hardware_targets[target.name] = target

        if self.specs_path.exists():
            with open(self.specs_path, "r", encoding="utf-8") as f:
                specs_list = json.load(f)
                self.candidate_models = [ModelCandidateSpec(**item) for item in specs_list]

    def get_hardware(self, key: str) -> HardwareTarget:
        """Finds hardware target by key or alias."""
        if key in self.hardware_targets:
            return self.hardware_targets[key]
        for k, v in self.hardware_targets.items():
            if key.lower() in k.lower() or key.lower() in v.name.lower():
                return v
        raise ValueError(f"Hardware target '{key}' not found. Available: {list(self.hardware_targets.keys())}")

    @staticmethod
    def calculate_weights_memory_gb(params_billion: float, precision: str) -> float:
        """Calculates raw model weights memory footprint in gigabytes."""
        bytes_per = BYTES_PER_PARAM.get(precision.upper(), 2.0)
        total_bytes = (params_billion * 1e9) * bytes_per
        return total_bytes / (1024 ** 3)

    @staticmethod
    def calculate_kv_cache_memory_mb(
        n_layers: int,
        n_kv_heads: int,
        d_model: int,
        n_heads: int,
        seq_len: int = 1000,
        batch_size: int = 1,
        precision: str = "FP16"
    ) -> float:
        """
        Computes KV cache memory in Megabytes:
        KV Memory = 2 (Key + Value) * n_layers * n_kv_heads * (d_model // n_heads) * seq_len * batch_size * bytes_per_elem
        """
        head_dim = d_model // n_heads
        bytes_per = 2.0 if precision.upper() in ["FP16", "BF16", "FP32"] else 1.0
        kv_elements = 2 * n_layers * n_kv_heads * head_dim * seq_len * batch_size
        total_bytes = kv_elements * bytes_per
        return total_bytes / (1024 ** 2)

    def profile_model_quantization(
        self,
        model_spec: ModelCandidateSpec,
        hardware_id: str = "rtx_4060_8gb"
    ) -> List[QuantizationDetail]:
        """
        Calculates quantization detail records across FP32, FP16, INT8, and INT4.
        """
        hw = self.get_hardware(hardware_id)
        precisions = ["FP32", "FP16", "INT8", "INT4"]
        results: List[QuantizationDetail] = []

        fp32_size = self.calculate_weights_memory_gb(model_spec.params_billion, "FP32")

        for prec in precisions:
            weights_gb = self.calculate_weights_memory_gb(model_spec.params_billion, prec)
            kv_mb = self.calculate_kv_cache_memory_mb(
                n_layers=model_spec.n_layers,
                n_kv_heads=model_spec.n_kv_heads,
                d_model=model_spec.d_model,
                n_heads=model_spec.n_heads,
                seq_len=1000,
                batch_size=1,
                precision=prec
            )
            compression_ratio = fp32_size / max(weights_gb, 1e-4)
            # Memory-bound speedup factor relative to FP32 bandwidth bottleneck
            estimated_speedup = min(compression_ratio * 0.9, 7.5)

            results.append(
                QuantizationDetail(
                    precision_type=prec,
                    bits_per_param=BITS_PER_PARAM[prec],
                    bytes_per_param=BYTES_PER_PARAM[prec],
                    model_size_gb=round(weights_gb, 3),
                    kv_cache_per_1k_tokens_mb=round(kv_mb, 2),
                    compression_ratio=round(compression_ratio, 2),
                    estimated_speedup=round(estimated_speedup, 2)
                )
            )

        return results

    def analyze_roofline(
        self,
        hardware_id: str,
        operational_intensity: float
    ) -> RooflinePoint:
        """
        Evaluates operational intensity (FLOPs / Byte) against hardware peak compute and memory bandwidth.
        Knee point = Peak TFLOPS / Bandwidth (GB/s).
        """
        hw = self.get_hardware(hardware_id)
        peak_tflops = hw.fp16_tflops
        bw_gbs = hw.memory_bandwidth_gbs

        # Knee intensity in FLOP/Byte
        knee_intensity = (peak_tflops * 1000.0) / bw_gbs

        # Attainable performance
        memory_bound_limit = (operational_intensity * bw_gbs) / 1000.0
        achievable_tflops = min(peak_tflops, memory_bound_limit)

        regime = "memory_bound" if operational_intensity < knee_intensity else "compute_bound"
        efficiency_pct = (achievable_tflops / peak_tflops) * 100.0

        return RooflinePoint(
            hardware_name=hw.name,
            arithmetic_intensity=round(operational_intensity, 2),
            achievable_tflops=round(achievable_tflops, 2),
            operational_regime=regime,
            efficiency_pct=round(efficiency_pct, 2)
        )

    def benchmark_all_candidates(
        self,
        hardware_id: str = "rtx_4060_8gb",
        preferred_precision: str = "INT4"
    ) -> Dict[str, Any]:
        """
        Benchmarks all candidate SLMs against a selected factory deployment target.
        """
        hw = self.get_hardware(hardware_id)
        benchmark_table: List[Dict[str, Any]] = []

        for candidate in self.candidate_models:
            profiles = self.profile_model_quantization(candidate, hardware_id=hardware_id)
            sel_profile = next((p for p in profiles if p.precision_type == preferred_precision), profiles[1])

            # Total VRAM footprint = Weights + 2K KV cache + 0.5 GB runtime context
            kv_2k_gb = (sel_profile.kv_cache_per_1k_tokens_mb * 2.0) / 1024.0
            total_vram_gb = sel_profile.model_size_gb + kv_2k_gb + 0.5
            fits_in_vram = total_vram_gb <= hw.vram_gb

            # Estimated token generation throughput (tokens/sec)
            # TPS ~ Memory Bandwidth / Weights Size
            est_tps = min((hw.memory_bandwidth_gbs * 0.65) / max(sel_profile.model_size_gb, 0.05), 260.0)

            # Scoring: balances MMLU capability, memory headroom, throughput
            vram_headroom = max(0.0, hw.vram_gb - total_vram_gb)
            score = (
                (candidate.mmlu_score / 100.0) * 4.0 +
                (min(est_tps, 200.0) / 200.0) * 3.5 +
                (vram_headroom / hw.vram_gb) * 2.5
            )
            if not fits_in_vram:
                score *= 0.1  # Heavy penalty if OOM

            benchmark_table.append({
                "model_id": candidate.model_id,
                "model_name": candidate.model_name,
                "params_billion": candidate.params_billion,
                "precision": sel_profile.precision_type,
                "model_size_gb": sel_profile.model_size_gb,
                "total_vram_gb": round(total_vram_gb, 2),
                "fits_in_vram": fits_in_vram,
                "estimated_tps": round(est_tps, 1),
                "mmlu_score": candidate.mmlu_score,
                "suitability_score": round(score, 2),
                "recommended_for": candidate.recommended_for
            })

        benchmark_table.sort(key=lambda x: x["suitability_score"], reverse=True)

        return {
            "hardware_target": hw.model_dump(),
            "preferred_precision": preferred_precision,
            "candidates_ranked": benchmark_table,
            "selected_slm": benchmark_table[0]["model_id"] if benchmark_table else None
        }
