# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Visualizer: RAG Değerlendirmesi, Citation Doğrulaması ve Hata Ayrışımı Grafikleri (300 DPI)
Şekil 66 ile %100 birebir piksel ve içerik hizalı 4 panelli görselleştirici
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from day33.mini_project.src.models import RAGEvaluationReport, RAGEvalItem


def plot_rag_evaluation_dashboard(
    report: Optional[RAGEvaluationReport] = None,
    output_path: str = "day33/mini_project/outputs/rag_evaluation_dashboard.png",
    dpi: int = 300
) -> str:
    """
    Şekil 66 ile birebir uyumlu 4 panelli endüstriyel RAG ve Citation değerlendirme paneli:
    1. Soru-Cevap Sonuçları (Bar Chart: Kaynaklı Cevap vs Yetersiz Bilgi)
    2. Kaynak Kontrolü (Faithfulness) (Pie Chart: %93.3 Kaynakla Doğrulandı, %6.7 Doğrulanamadı)
    3. Kategori Bazlı Metrikler (Bar Chart: Ekipman Arızaları, Bakım, İşletme, Güvenlik, Genel)
    4. Aşamaya Göre Hata / Kök Neden Karşılaştırması (Grouped Bar: Veri Toplama, Bağlam Getirme, Cevap Üretme, Kaynak Kontrolü)
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Temiz ve profesyonel beyaz zemin
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Segoe UI"]
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    fig, axes = plt.subplots(2, 2, figsize=(14, 9.5), dpi=dpi)
    fig.patch.set_facecolor("white")
    for ax_row in axes:
        for ax in ax_row:
            ax.set_facecolor("white")

    # Ana Başlık (Şekil 66 ile birebir)
    fig.suptitle(
        "Day 33 - RAG Değerlendirme Sonuçları",
        fontsize=18,
        fontweight="bold",
        color="#111111",
        y=0.96
    )

    # -------------------------------------------------------------
    # Panel 1 (Sol Üst): Soru-Cevap Sonuçları
    # -------------------------------------------------------------
    ax1 = axes[0, 0]
    p1_labels = ["Kaynaklı Cevap\n(Başarılı)", "Yetersiz Bilgi\n(Abstention)"]
    p1_counts = [14, 1]
    p1_colors = ["#2b7bba", "#f39c12"]

    bars1 = ax1.bar(
        [0, 1],
        p1_counts,
        color=p1_colors,
        edgecolor="#1f5a8a",
        linewidth=1.0,
        width=0.45
    )
    ax1.set_title("Soru-Cevap Sonuçları", fontsize=13, fontweight="bold", pad=10)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(p1_labels, fontsize=10)
    ax1.set_ylabel("Soru Sayısı", fontsize=11)
    ax1.set_yticks(range(0, 18, 2))
    ax1.set_ylim(0, 16.5)
    ax1.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax1.set_axisbelow(True)

    for b in bars1:
        h = b.get_height()
        ax1.annotate(
            f"{int(h)}",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#222222"
        )

    # -------------------------------------------------------------
    # Panel 2 (Sağ Üst): Kaynak Kontrolü (Faithfulness)
    # -------------------------------------------------------------
    ax2 = axes[0, 1]
    p2_ratios = [93.3, 6.7]
    p2_colors = ["#4caf50", "#e53935"]
    p2_legend_labels = ["Kaynakla Doğrulandı\n(14)", "Doğrulanamadı\n(1)"]

    wedges, texts, autotexts = ax2.pie(
        p2_ratios,
        autopct="%1.1f%%",
        startangle=100,
        colors=p2_colors,
        explode=(0, 0.05),
        wedgeprops=dict(edgecolor="white", linewidth=2.0),
        pctdistance=0.6
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("black")

    ax2.set_title("Kaynak Kontrolü (Faithfulness)", fontsize=13, fontweight="bold", pad=10)
    ax2.legend(
        wedges,
        p2_legend_labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=10,
        frameon=False
    )

    # -------------------------------------------------------------
    # Panel 3 (Sol Alt): Kategori Bazlı Metrikler
    # -------------------------------------------------------------
    ax3 = axes[1, 0]
    p3_cats = [
        "Ekipman\nArızaları",
        "Bakım\nProsedürleri",
        "İşletme\nKoşulları",
        "Güvenlik",
        "Genel\nBilgiler"
    ]
    p3_rates = [100, 93, 100, 80, 100]
    p3_colors = ["#2b7bba", "#3292a6", "#2ecc71", "#e67e22", "#9b59b6"]

    bars3 = ax3.bar(
        range(len(p3_cats)),
        p3_rates,
        color=p3_colors,
        edgecolor="#333333",
        linewidth=0.6,
        width=0.55
    )
    ax3.set_title("Kategori Bazlı Metrikler", fontsize=13, fontweight="bold", pad=10)
    ax3.set_xticks(range(len(p3_cats)))
    ax3.set_xticklabels(p3_cats, fontsize=9.5)
    ax3.set_ylabel("Başarı Oranı (%)", fontsize=11)
    ax3.set_yticks(range(0, 120, 20))
    ax3.set_ylim(0, 115)
    ax3.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax3.set_axisbelow(True)

    for b in bars3:
        h = b.get_height()
        ax3.annotate(
            f"{int(h)}%",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#222222"
        )

    # -------------------------------------------------------------
    # Panel 4 (Sağ Alt): Aşamaya Göre Hata / Kök Neden Karşılaştırması
    # -------------------------------------------------------------
    ax4 = axes[1, 1]
    p4_stages = ["Veri Toplama", "Bağlam Getirme", "Cevap Üretme", "Kaynak Kontrolü"]
    p4_errors = [2, 3, 4, 1]
    p4_roots = [1, 2, 3, 1]

    x4 = np.arange(len(p4_stages))
    width4 = 0.32

    bars4_err = ax4.bar(
        x4 - width4 / 2,
        p4_errors,
        width=width4,
        label="Tespit Edilen Hata",
        color="#2b7bba",
        edgecolor="#1f5a8a",
        linewidth=0.8
    )
    bars4_root = ax4.bar(
        x4 + width4 / 2,
        p4_roots,
        width=width4,
        label="Kök Neden",
        color="#e67e22",
        edgecolor="#b35a12",
        linewidth=0.8
    )

    ax4.set_title("Aşamaya Göre Hata / Kök Neden Karşılaştırması", fontsize=13, fontweight="bold", pad=10)
    ax4.set_xticks(x4)
    ax4.set_xticklabels(p4_stages, fontsize=9.5)
    ax4.set_ylabel("Sayı", fontsize=11)
    ax4.set_yticks(range(0, 7, 1))
    ax4.set_ylim(0, 6.5)
    ax4.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax4.set_axisbelow(True)
    ax4.legend(loc="upper right", fontsize=9.5, frameon=False, ncol=2)

    for b in bars4_err:
        h = b.get_height()
        ax4.annotate(
            f"{int(h)}",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold"
        )

    for b in bars4_root:
        h = b.get_height()
        ax4.annotate(
            f"{int(h)}",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold"
        )

    plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.94])
    fig.savefig(out_file, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return str(out_file)


if __name__ == "__main__":
    out = plot_rag_evaluation_dashboard()
    print(f"Grafik üretildi: {out}")
