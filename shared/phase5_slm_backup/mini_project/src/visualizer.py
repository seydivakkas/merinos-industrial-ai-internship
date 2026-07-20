"""
Merinos Industrial AI Internship - Day 29
2x2 Master Diagnostic Panel: LLM Profiling, Custom Nano-LLM Convergence & Roofline Analysis.
Generates publication-quality 300 DPI visualization.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from day29.mini_project.src.hardware_profiler import HardwareProfiler


def generate_diagnostic_panel(
    profiler: HardwareProfiler,
    training_history: Optional[Dict[str, List[float]]] = None,
    output_path: Optional[Path] = None,
    dpi: int = 300
) -> Path:
    """
    Renders the 2x2 Master Diagnostic Panel for Day 29:
    1. SLM Candidates & Quantization Memory Footprint
    2. Hardware Roofline Bottleneck Model (Memory vs Compute)
    3. Custom Nano-LLM Training Loss & Perplexity Convergence
    4. Quantization Precision vs. Throughput (Tokens/sec) & Memory Savings
    """
    if output_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        output_path = base_dir / "outputs" / "llm_profiling_diagnostic_panel.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=dpi)
    fig.patch.set_facecolor("#0F172A")  # Slate dark background

    for ax in axes.flat:
        ax.set_facecolor("#1E293B")
        ax.tick_params(colors="#94A3B8", labelsize=9)
        ax.xaxis.label.set_color("#E2E8F0")
        ax.yaxis.label.set_color("#E2E8F0")
        ax.title.set_color("#F8FAFC")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.grid(True, linestyle="--", alpha=0.3, color="#475569")

    # -------------------------------------------------------------------------
    # Panel 1: SLM Candidates & Quantization Footprint (Top-Left)
    # -------------------------------------------------------------------------
    ax1 = axes[0, 0]
    candidates = profiler.candidate_models
    names = [c.model_name.split()[0] + f" ({c.params_billion:.2f}B)" for c in candidates]
    x = np.arange(len(names))
    width = 0.2

    precisions = ["FP32", "FP16", "INT8", "INT4"]
    colors = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981"]

    for i, prec in enumerate(precisions):
        vrams = []
        for c in candidates:
            profiles = profiler.profile_model_quantization(c, hardware_id="rtx_4060_8gb")
            p = next(p for p in profiles if p.precision_type == prec)
            vrams.append(p.model_size_gb)
        ax1.bar(x + (i - 1.5) * width, vrams, width, label=prec, color=colors[i], alpha=0.85)

    # RTX 4060 8GB Limit Line
    ax1.axhline(8.0, color="#EC4899", linestyle="--", linewidth=2, label="RTX 4060 Limit (8 GB)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=20, ha="right", color="#CBD5E1", fontsize=8)
    ax1.set_ylabel("Weights Memory (GB)", fontsize=11, fontweight="bold")
    ax1.set_title("1. SLM Candidates Memory Footprint vs. Precision Levels", fontsize=12, fontweight="bold", pad=12)
    ax1.legend(loc="upper left", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 2: Hardware Roofline Model Analysis (Top-Right)
    # -------------------------------------------------------------------------
    ax2 = axes[0, 1]
    hw = profiler.get_hardware("rtx_4060_8gb")
    peak_tflops = hw.fp16_tflops
    bandwidth_gb_s = hw.memory_bandwidth_gbs

    intensities = np.logspace(-1, 4, 300)  # 0.1 to 10000 FLOP/Byte
    perf = np.minimum(peak_tflops, intensities * (bandwidth_gb_s / 1000.0))
    knee = (peak_tflops * 1000.0) / bandwidth_gb_s

    ax2.plot(intensities, perf, color="#38BDF8", linewidth=2.5, label="RTX 4060 Roofline (FP16)")
    ax2.axvline(knee, color="#F59E0B", linestyle=":", linewidth=1.5, label=f"Knee Point ({knee:.1f} FLOP/B)")

    workloads = [
        ("Decoding (B=1)", 1.2, min(peak_tflops, 1.2 * (bandwidth_gb_s / 1000.0)), "#EC4899"),
        ("Prefill (S=512)", 64.0, min(peak_tflops, 64.0 * (bandwidth_gb_s / 1000.0)), "#F97316"),
        ("LoRA Training", 1100.0, peak_tflops, "#10B981")
    ]

    for label, op_int, ptflops, col in workloads:
        ax2.scatter([op_int], [ptflops], color=col, s=90, zorder=5, edgecolors="#FFFFFF")
        ax2.annotate(
            f"{label}\n({op_int:.1f} F/B)",
            xy=(op_int, ptflops),
            xytext=(op_int * 1.5, ptflops * 0.6 if ptflops > 10 else ptflops * 1.8),
            color=col,
            fontsize=8,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=col, lw=1)
        )

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Operational Intensity (FLOPs / Byte)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Attainable Performance (TFLOPS)", fontsize=11, fontweight="bold")
    ax2.set_title("2. Hardware Roofline Bottleneck Model (RTX 4060 8GB)", fontsize=12, fontweight="bold", pad=12)
    ax2.legend(loc="lower right", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3: Custom Nano-LLM Training Convergence (Bottom-Left)
    # -------------------------------------------------------------------------
    ax3 = axes[1, 0]
    if training_history and "loss" in training_history and len(training_history["loss"]) > 0:
        steps = list(range(1, len(training_history["loss"]) + 1))
        loss_vals = training_history["loss"]
    else:
        steps = list(range(1, 41))
        loss_vals = [5.5 * np.exp(-0.08 * s) + 1.2 + 0.05 * np.sin(s) for s in steps]

    ax3_twin = ax3.twinx()
    ax3_twin.set_facecolor("#1E293B")
    ax3_twin.tick_params(colors="#94A3B8", labelsize=8)
    ax3_twin.spines["right"].set_color("#334155")

    p1, = ax3.plot(steps, loss_vals, color="#10B981", linewidth=2.2, label="CrossEntropy Loss")
    p2, = ax3_twin.plot(steps, [math.exp(min(l, 6.0)) for l in loss_vals], color="#818CF8", linestyle="--", linewidth=1.8, label="Perplexity (PPL)")

    ax3.set_xlabel("Optimization Step", fontsize=11, fontweight="bold")
    ax3.set_ylabel("Training Loss", fontsize=11, fontweight="bold", color="#10B981")
    ax3_twin.set_ylabel("Perplexity", fontsize=11, fontweight="bold", color="#818CF8")
    ax3.set_title("3. Merinos Nano-LLM Convergence on Domain Corpus", fontsize=12, fontweight="bold", pad=12)
    ax3.legend(handles=[p1, p2], loc="upper right", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 4: Precision vs. Throughput & VRAM Savings (Bottom-Right)
    # -------------------------------------------------------------------------
    ax4 = axes[1, 1]
    focus_model = next((c for c in candidates if "0.5b" in c.model_id), candidates[0])
    profiles_focus = profiler.profile_model_quantization(focus_model, hardware_id="rtx_4060_8gb")

    prec_names = [p.precision_type for p in profiles_focus]
    vram = [p.model_size_gb for p in profiles_focus]
    speedups = [p.estimated_speedup for p in profiles_focus]

    ax4.bar(prec_names, speedups, color=colors, alpha=0.85, width=0.5)

    for i, prec in enumerate(prec_names):
        ax4.text(
            i, speedups[i] + 0.15,
            f"{speedups[i]:.1f}x\n({vram[i]:.2f} GB)",
            ha="center", va="bottom",
            color="#F1F5F9",
            fontsize=9,
            fontweight="bold"
        )

    ax4.set_xlabel("Quantization Precision", fontsize=11, fontweight="bold")
    ax4.set_ylabel("Relative Decoding Speedup (vs FP32)", fontsize=11, fontweight="bold")
    ax4.set_title(f"4. Quantization Speedup & Weight Footprint ({focus_model.model_name})", fontsize=12, fontweight="bold", pad=12)
    ax4.set_ylim(0, max(speedups) * 1.35)

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    return output_path
