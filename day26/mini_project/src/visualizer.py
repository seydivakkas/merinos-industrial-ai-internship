"""
Merinos Industrial AI Internship - Day 26
Vector Indexing & Quantization Master Diagnostic Panel (2x2)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from day26.mini_project.src.models import VectorIndexReport


def plot_vector_index_diagnostic_panel(
    report: VectorIndexReport,
    output_path: str | Path,
    title_suffix: str = ""
) -> Path:
    """
    Flat, IVF, HNSW ve Kuantize HNSW indekslerinin gecikme, bellek tüketimi,
    QPS işlem hızı ve payload filtreleme başarımını Şekil 52'deki 2x2 Master Tanı Paneli
    olarak birebir görselleştirir.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Matplotlib stil ayarları (Koyu/Endüstriyel Kurumsal Tema)
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    fig.patch.set_facecolor("#121820")

    # Renk ve etiket tanımları (Şekil 52 ile birebir uyumlu)
    colors = {
        "exact_flat": "#3498db",        # Mavi (Exact Flat Baseline)
        "ivf": "#e67e22",               # Turuncu (IVF Centroid Voronoi)
        "hnsw": "#2ecc71",              # Yeşil (HNSW Graf)
        "quantized_hnsw": "#e74c3c"     # Kırmızı/Mercan (Quantized HNSW SQ8)
    }
    labels = {
        "exact_flat": "Exact Flat (Baseline)",
        "ivf": "IVF (Centroid Voronoi)",
        "hnsw": "HNSW (Graf)",
        "quantized_hnsw": "Quantized HNSW (SQ8)"
    }
    short_labels = {
        "exact_flat": "Exact Flat\n(Baseline)",
        "ivf": "IVF\n(Centroid Voronoi)",
        "hnsw": "HNSW\n(Graf)",
        "quantized_hnsw": "Quantized HNSW\n(SQ8)"
    }

    # -------------------------------------------------------------
    # Panel 1: Gecikme vs. Arama Doğruluğu (Pareto Eğrisi)
    # -------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor("#18202c")
    ax1.grid(True, linestyle="-", alpha=0.25, color="#4a5568")

    # Log scale x ekseni
    ax1.set_xscale("log")
    ax1.set_xlim([0.008, 3.0])
    ax1.set_ylim([55, 105])
    ax1.set_yticks([60, 70, 80, 90, 100])

    # Özel x-ticks: 0.01, 0.1, 1
    ax1.set_xticks([0.01, 0.1, 1.0])
    ax1.get_xaxis().set_major_formatter(ticker.ScalarFormatter())

    order_p1 = ["exact_flat", "ivf", "hnsw", "quantized_hnsw"]
    for k in order_p1:
        if k in report.indices:
            m = report.indices[k]
            x_val = m.query_latency_ms
            y_val = m.recall_at_5 * 100
            ax1.scatter(
                x_val,
                y_val,
                s=120,
                color=colors[k],
                edgecolor="#ffffff",
                linewidth=1.2,
                zorder=5,
                label=labels[k]
            )

    # Annotations matching Şekil 52
    if "exact_flat" in report.indices:
        m = report.indices["exact_flat"]
        ax1.annotate(
            f"Exact Flat (Baseline)\n%{m.recall_at_5*100:.1f}, {m.query_latency_ms:.2f} ms",
            xy=(m.query_latency_ms, m.recall_at_5 * 100),
            xytext=(-15, 10),
            textcoords="offset points",
            fontsize=8.5,
            color="#f1f5f9",
            ha="right"
        )

    if "ivf" in report.indices:
        m = report.indices["ivf"]
        ax1.annotate(
            f"IVF (Centroid Voronoi)\n%{m.recall_at_5*100:.1f}, {m.query_latency_ms:.2f} ms",
            xy=(m.query_latency_ms, m.recall_at_5 * 100),
            xytext=(10, -5),
            textcoords="offset points",
            fontsize=8.5,
            color="#f1f5f9",
            ha="left"
        )

    if "hnsw" in report.indices:
        m = report.indices["hnsw"]
        ax1.annotate(
            f"HNSW (Graf)\n%{m.recall_at_5*100:.1f}, {m.query_latency_ms:.2f} ms",
            xy=(m.query_latency_ms, m.recall_at_5 * 100),
            xytext=(-10, -25),
            textcoords="offset points",
            fontsize=8.5,
            color="#f1f5f9",
            ha="right"
        )

    if "quantized_hnsw" in report.indices:
        m = report.indices["quantized_hnsw"]
        ax1.annotate(
            f"Quantized HNSW (SQ8)\n%{m.recall_at_5*100:.1f}, {m.query_latency_ms:.2f} ms",
            xy=(m.query_latency_ms, m.recall_at_5 * 100),
            xytext=(10, 8),
            textcoords="offset points",
            fontsize=8.5,
            color="#f1f5f9",
            ha="left"
        )

    ax1.set_xlabel("Gecikme (ms, log ölçek)", fontsize=10, fontweight="bold", color="#cbd5e1")
    ax1.set_ylabel("Arama Doğruluğu (Recall @ 5, %)", fontsize=10, fontweight="bold", color="#cbd5e1")
    ax1.set_title("1. Gecikme vs. Arama Doğruluğu (Pareto Eğrisi)", fontsize=12, fontweight="bold", color="#f8fafc", pad=10)
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.3, edgecolor="#475569")

    # -------------------------------------------------------------
    # Panel 2: İndeks Bellek Ayak İzi & Kuantizasyon Kazancı
    # -------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor("#18202c")
    ax2.grid(True, linestyle="-", alpha=0.25, color="#4a5568", axis="y")

    order_p2 = ["exact_flat", "ivf", "hnsw", "quantized_hnsw"]
    x_pos2 = np.arange(len(order_p2))
    mem_vals = [report.indices[k].memory_kb if k in report.indices else 0.0 for k in order_p2]

    bars2 = ax2.bar(
        x_pos2,
        mem_vals,
        width=0.45,
        color=[colors[k] for k in order_p2],
        edgecolor="#ffffff",
        linewidth=0.8,
        zorder=3
    )

    for bar, val in zip(bars2, mem_vals):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 3.0,
            f"{val:.1f} KB",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#ffffff"
        )

    ax2.set_xticks(x_pos2)
    ax2.set_xticklabels([short_labels[k] for k in order_p2], fontsize=9, color="#cbd5e1")
    ax2.set_ylabel("İndeks Boyutu (KB)", fontsize=10, fontweight="bold", color="#cbd5e1")
    ax2.set_ylim([0, 140])
    ax2.set_yticks([0, 20, 40, 60, 80, 100, 120, 140])
    ax2.set_title("2. İndeks Bellek Ayak İzi & Kuantizasyon Kazancı", fontsize=12, fontweight="bold", color="#f8fafc", pad=10)

    # -------------------------------------------------------------
    # Panel 3: Arama Hızı ve Üretim İşlem Kapasitesi (QPS)
    # -------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor("#18202c")
    ax3.grid(True, linestyle="-", alpha=0.25, color="#4a5568", axis="y")

    # X eksenindeki sıralama Şekil 52'de:
    # 1. Quantized HNSW (SQ8)
    # 2. HNSW (Graf)
    # 3. IVF (Centroid Voronoi)
    # 4. Exact Flat (Baseline)
    order_p3 = ["quantized_hnsw", "hnsw", "ivf", "exact_flat"]
    x_pos3 = np.arange(len(order_p3))
    qps_vals = [report.indices[k].qps if k in report.indices else 0.0 for k in order_p3]

    bars3 = ax3.bar(
        x_pos3,
        qps_vals,
        width=0.45,
        color=[colors[k] for k in order_p3],
        edgecolor="#ffffff",
        linewidth=0.8,
        zorder=3
    )

    for bar, val in zip(bars3, qps_vals):
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 450,
            f"{val:,.0f} QPS",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#ffffff"
        )

    ax3.set_xticks(x_pos3)
    ax3.set_xticklabels([short_labels[k] for k in order_p3], fontsize=9, color="#cbd5e1")
    ax3.set_ylabel("Sorgu/Saniye (QPS)", fontsize=10, fontweight="bold", color="#cbd5e1")
    ax3.set_ylim([0, 22000])
    ax3.set_yticks([0, 5000, 10000, 15000, 20000])
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax3.set_title("3. Arama Hızı ve Üretim İşlem Kapasitesi (QPS)", fontsize=12, fontweight="bold", color="#f8fafc", pad=10)

    # -------------------------------------------------------------
    # Panel 4: Payload Filtrelemenin Arama Doğruluğuna Etkisi
    # -------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor("#18202c")
    ax4.grid(True, linestyle="-", alpha=0.25, color="#4a5568", axis="y")

    order_p4 = ["exact_flat", "ivf", "hnsw", "quantized_hnsw"]
    x_pos4 = np.arange(len(order_p4))
    width4 = 0.28

    unfiltered_vals = [report.indices[k].recall_at_5 * 100 if k in report.indices else 0.0 for k in order_p4]
    filtered_vals = [report.indices[k].filtered_recall_at_5 * 100 if k in report.indices else 0.0 for k in order_p4]

    rects1 = ax4.bar(
        x_pos4 - width4 / 2,
        unfiltered_vals,
        width4,
        label="Filtresiz Recall@5",
        color="#3498db",
        edgecolor="#ffffff",
        linewidth=0.6,
        zorder=3
    )
    rects2 = ax4.bar(
        x_pos4 + width4 / 2,
        filtered_vals,
        width4,
        label="Payload filtreli Recall@5",
        color="#e67e22",
        edgecolor="#ffffff",
        linewidth=0.6,
        zorder=3
    )

    for r in rects1:
        h = r.get_height()
        ax4.annotate(
            f"{h:.1f}",
            (r.get_x() + r.get_width() / 2, h + 2),
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#ffffff"
        )
    for r in rects2:
        h = r.get_height()
        ax4.annotate(
            f"{h:.1f}",
            (r.get_x() + r.get_width() / 2, h + 2),
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#ffffff"
        )

    ax4.set_xticks(x_pos4)
    ax4.set_xticklabels([short_labels[k] for k in order_p4], fontsize=9, color="#cbd5e1")
    ax4.set_ylabel("Recall @5 (%)", fontsize=10, fontweight="bold", color="#cbd5e1")
    ax4.set_ylim([0, 120])
    ax4.set_yticks([0, 20, 40, 60, 80, 100, 120])
    ax4.set_title("4. Payload Filtrelemenin Arama Doğruluğuna Etkisi", fontsize=12, fontweight="bold", color="#f8fafc", pad=10)
    ax4.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=8.5, framealpha=0.3, edgecolor="#475569")

    # Ana Başlık ve Alt Başlık (Şekil 52 ile birebir aynı)
    fig.suptitle(
        f"MERİNOS HALI SANAYİ A.Ş. — VEKTÖR VERİTABANI & İNDEKS OPTİMİZASYONU TANI PANELİ {title_suffix}\n"
        f"Faz 4: Retrieval & Hibrit Arama (Day 26) | HNSW vs IVF, Skaler Kuantizasyon (SQ8) ve Payload Filtreleme",
        fontsize=14,
        fontweight="bold",
        color="#ffffff",
        y=0.98
    )

    plt.subplots_adjust(left=0.07, right=0.95, top=0.91, bottom=0.10, hspace=0.30, wspace=0.18)
    plt.savefig(out_file, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    return out_file
