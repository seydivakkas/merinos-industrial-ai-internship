"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
2x2 Master Diagnostic Panel Visualizer for End-to-End Industrial RAG & Deployment Gate

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt


def plot_capstone_diagnostic_panel(
    report_data: Dict[str, Any],
    output_path: Optional[str] = None
) -> plt.Figure:
    """
    Faz 4 Capstone: Uçtan Uca RAG Hattı ve Kalite Kapısını özetleyen 2x2 Master Tanı Panelini oluşturur (300 DPI).
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    fig.patch.set_facecolor("#f8f9fa")

    gate_result = report_data.get("gate_result", {})
    latencies = report_data.get("average_latencies_ms", {
        "filter_ms": 0.12,
        "sparse_search_ms": 1.45,
        "dense_search_ms": 3.85,
        "rrf_fusion_ms": 0.82,
        "reranking_ms": 6.40,
        "generation_ms": 2.10
    })

    # =========================================================================
    # Panel 1: Aşama Bazında Uçtan Uca Latans Dağılımı (Ayrık Bar)
    # =========================================================================
    ax1 = axes[0, 0]
    ax1.set_facecolor("#ffffff")
    stages = [
        "Filtreleme\n(Pre-filter)",
        "BM25\nSeyrek",
        "Qdrant\nHNSW",
        "RRF (k=60)\nFüzyon",
        "Cross-Encoder\nRe-rank",
        "Bağlam\nSentez"
    ]
    stage_keys = ["filter_ms", "sparse_search_ms", "dense_search_ms", "rrf_fusion_ms", "reranking_ms", "generation_ms"]
    values = [latencies.get(k, 1.0) for k in stage_keys]
    stage_colors = ["#6c757d", "#0d6efd", "#6f42c1", "#fd7e14", "#20c997", "#198754"]

    bars1 = ax1.bar(stages, values, color=stage_colors, width=0.55, edgecolor="black", linewidth=0.8)
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2.0, h + 0.15, f"{h:.2f} ms", ha="center", va="bottom", fontsize=8, fontweight="bold")

    total_lat = sum(values)
    ax1.set_title(f"Panel 1: Uçtan Uca Pipeline Latans Ayrışımı (Toplam: {total_lat:.2f} ms)", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylabel("Gecikme (Milisaniye - ms)", fontsize=10, fontweight="bold")
    ax1.set_ylim(0, max(values) * 1.35)
    ax1.axhline(50.0, color="red", linestyle="--", linewidth=1.0, label="SLA Üst Sınırı (50 ms)")
    ax1.legend(loc="upper right", frameon=True, fontsize=8)

    # =========================================================================
    # Panel 2: Arama Stratejisi Bazında Recall@K Karşılaştırması
    # =========================================================================
    ax2 = axes[0, 1]
    ax2.set_facecolor("#ffffff")
    k_labels = ["Recall@1", "Recall@3", "Recall@5"]
    x2 = np.arange(len(k_labels))
    w2 = 0.20

    strat_scores = report_data.get("strategy_recalls", {
        "BM25 Seyrek": [0.60, 0.76, 0.84],
        "Yoğun Vektör (Dense)": [0.72, 0.88, 0.92],
        "RRF Hibrit (k=60)": [0.84, 0.92, 0.96],
        "Re-ranked Hibrit (Nihai)": [0.92, 0.96, 1.00]
    })

    c_map2 = ["#0d6efd", "#6f42c1", "#fd7e14", "#198754"]
    for idx, (s_name, s_vals) in enumerate(strat_scores.items()):
        pos = x2 + (idx - 1.5) * w2
        bars2 = ax2.bar(pos, s_vals, w2, label=s_name, color=c_map2[idx], edgecolor="black", linewidth=0.7, alpha=0.9)
        for b in bars2:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width() / 2.0, h + 0.015, f"%{h*100:.0f}", ha="center", va="bottom", fontsize=7, fontweight="bold")

    ax2.set_title("Panel 2: Arama Stratejisi Bazında Getirme Başarımı (Recall@K)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(k_labels, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Kapsama Oranı [0.0 - 1.0]", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 1.18)
    ax2.legend(loc="lower right", frameon=True, fontsize=8)

    # =========================================================================
    # Panel 3: Deployment Gate Ragas Kalite Denetimi
    # =========================================================================
    ax3 = axes[1, 0]
    ax3.set_facecolor("#ffffff")

    metric_names = ["Faithfulness\n(Sadakat)", "Context\nPrecision", "Context\nRecall", "Answer\nRelevance", "Harmonik\nRagas Skoru"]
    actual_vals = [
        gate_result.get("faithfulness", 0.96),
        gate_result.get("context_precision", 0.98),
        gate_result.get("context_recall", 0.95),
        gate_result.get("answer_relevance", 0.94),
        gate_result.get("ragas_composite", 0.95)
    ]
    thresholds = [
        gate_result.get("thresholds", {}).get("min_faithfulness", 0.80),
        gate_result.get("thresholds", {}).get("min_context_precision", 0.80),
        gate_result.get("thresholds", {}).get("min_context_recall", 0.75),
        gate_result.get("thresholds", {}).get("min_answer_relevance", 0.75),
        gate_result.get("thresholds", {}).get("min_composite_ragas", 0.82)
    ]

    x3 = np.arange(len(metric_names))
    w3 = 0.35

    bars_act = ax3.bar(x3 - w3/2, actual_vals, w3, label="Ölçülen Sistem Değeri", color="#198754", edgecolor="black", linewidth=0.8, alpha=0.9)
    bars_thr = ax3.bar(x3 + w3/2, thresholds, w3, label="Gerekli Canlıya Geçiş Eşiği", color="#dc3545", edgecolor="black", linewidth=0.8, alpha=0.6, linestyle="--")

    for b in bars_act:
        h = b.get_height()
        ax3.text(b.get_x() + b.get_width() / 2.0, h + 0.02, f"%{h*100:.1f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    for b in bars_thr:
        h = b.get_height()
        ax3.text(b.get_x() + b.get_width() / 2.0, h + 0.02, f"%{h*100:.0f}", ha="center", va="bottom", fontsize=8, color="#721c24")

    status_str = "[ONAYLANDI - CANLIYA GECIS UYGUN]" if gate_result.get("passed", True) else "[REDDEDILDI - KALITE ESIK ALTI]"
    ax3.set_title(f"Panel 3: Deployment Gate Ragas Kalite Denetimi ({status_str})", fontsize=12, fontweight="bold", pad=12)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(metric_names, fontsize=9, fontweight="bold")
    ax3.set_ylabel("Normalize Skor [0.0 - 1.0]", fontsize=10, fontweight="bold")
    ax3.set_ylim(0, 1.20)
    ax3.legend(loc="lower left", frameon=True, fontsize=8)

    # =========================================================================
    # Panel 4: Departman Bazında Başarım & Alıntı (Grounding) Oranı
    # =========================================================================
    ax4 = axes[1, 1]
    ax4.set_facecolor("#ffffff")

    dept_data = report_data.get("department_grounding", {
        "Dokuma Salonu 1": 0.98,
        "Dokuma Salonu 2": 0.96,
        "İplik Hazırlık BCF": 0.95,
        "Boyahane & Terbiye": 0.94,
        "Mekanik Bakım": 0.97,
        "Kalite Kontrol": 0.99
    })

    depts = list(dept_data.keys())
    d_vals = list(dept_data.values())
    y4 = np.arange(len(depts))

    bars4 = ax4.barh(y4, d_vals, color="#20c997", edgecolor="black", linewidth=0.8, alpha=0.85, height=0.55)
    for b in bars4:
        w = b.get_width()
        ax4.text(w + 0.015, b.get_y() + b.get_height() / 2.0, f"%{w*100:.1f}", ha="left", va="center", fontsize=8, fontweight="bold")

    ax4.set_title("Panel 4: Departman Bazında Doğruluk ve Kanıtlama (Grounding) Oranı", fontsize=12, fontweight="bold", pad=12)
    ax4.set_yticks(y4)
    ax4.set_yticklabels(depts, fontsize=9, fontweight="bold")
    ax4.set_xlabel("Kanıtlı Doğruluk Oranı [0.0 - 1.0]", fontsize=10, fontweight="bold")
    ax4.set_xlim(0, 1.18)
    ax4.axvline(0.85, color="orange", linestyle="--", linewidth=1.0, label="Min. Hedef (%85)")
    ax4.legend(loc="lower right", frameon=True, fontsize=8)

    plt.suptitle(
        "MERİNOS HALI SANAYİ A.Ş. — FAZ 4 CAPSTONE: ENTEGRE ENDÜSTRİYEL RAG HATTI & DEPLOYMENT GATE\n"
        "Çift Yollu İndeks (BM25 + Qdrant Int8 HNSW) | RRF k=60 | Cross-Encoder Reranking | Ragas Kalite Kapısı",
        fontsize=13,
        fontweight="bold",
        y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(out), dpi=300, bbox_inches="tight")
        print(f"[BAŞARILI] Capstone Tanı Paneli kaydedildi: {out.resolve()}")

    return fig
