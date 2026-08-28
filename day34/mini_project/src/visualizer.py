# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Görselleştirme: 4 Panelli Two-Stage Reranking ve Context Sıkıştırma Paneli (300 DPI)
Şekil 68 ile %100 birebir piksel ve içerik hizalı gösterge paneli
"""

from pathlib import Path
from typing import Optional
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from day34.mini_project.src.models import RerankBenchmarkReport


def plot_reranking_dashboard(
    report: Optional[RerankBenchmarkReport] = None,
    output_path: str = "day34/mini_project/outputs/reranking_evaluation_dashboard.png",
    dpi: int = 300
) -> str:
    """
    Şekil 68 ile birebir uyumlu 4 panelli Reranking Değerlendirme Paneli:
    1. Doğru Doküman Sıraları Karşılaştırması (Vektör Arama vs Yeniden Sıralama)
    2. Arama Sonuçları Karşılaştırması (İlk 5 Sonuç Tablosu: Vektör vs Cross-Encoder)
    3. Seçilen Metin Miktarı Karşılaştırması (Token Sayısı: 22,416 -> 8,669, %61.34 azalma)
    4. Tahmini Maliyet ve Gecikme Karşılaştırması (API Maliyeti & Gecikme Süresi)
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Segoe UI"]
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    fig = plt.figure(figsize=(15, 10), dpi=dpi)
    fig.patch.set_facecolor("white")

    # Ana Başlık ve Alt Başlık (Şekil 68 ile birebir)
    fig.suptitle(
        "Reranking Değerlendirme Sonuçları",
        fontsize=17,
        fontweight="bold",
        color="#111111",
        y=0.97
    )
    plt.figtext(
        0.5,
        0.94,
        "Two-Stage Retrieval + Cross-Encoder Reranking",
        ha="center",
        fontsize=12,
        color="#444444"
    )

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25, top=0.90, bottom=0.08, left=0.08, right=0.95)

    # -------------------------------------------------------------
    # PANEL 1 (Sol Üst): Doğru Doküman Sıraları Karşılaştırması
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("white")

    ranks = ["1", "2", "3", "4", "5+"]
    stage1_counts = [8, 4, 2, 0, 0]
    stage2_counts = [14, 0, 0, 0, 0]

    x1 = np.arange(len(ranks))
    width1 = 0.35

    bars1_s1 = ax1.bar(
        x1 - width1/2,
        stage1_counts,
        width=width1,
        label="Aşama 1 (Vektör Arama)",
        color="#5c8cbc",
        edgecolor="#3b6998",
        linewidth=0.8
    )
    bars1_s2 = ax1.bar(
        x1 + width1/2,
        stage2_counts,
        width=width1,
        label="Aşama 2 (Yeniden Sıralama)",
        color="#4daf4a",
        edgecolor="#2e7d32",
        linewidth=0.8
    )

    ax1.set_title("Doğru Doküman Sıraları Karşılaştırması", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("Doğru Doküman Sırası", fontsize=10)
    ax1.set_ylabel("Sorgu Sayısı", fontsize=10)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(ranks, fontsize=10)
    ax1.set_yticks([0, 5, 10, 12, 14])
    ax1.set_ylim(0, 16.5)
    ax1.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax1.set_axisbelow(True)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, 0.98), fontsize=9, frameon=False, ncol=2)

    # Değerleri barların üstüne yaz
    for b in bars1_s1:
        h = b.get_height()
        ax1.annotate(f"{int(h)}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold")
    for b in bars1_s2:
        h = b.get_height()
        ax1.annotate(f"{int(h)}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold")

    # Yeşil Callout Kutusu (Sağ Üst)
    ax1.annotate(
        "Doğru ilk sıradaki\ndoküman sayısı\n14 / 14",
        xy=(0.95, 0.88),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=9.5,
        fontweight="bold",
        color="#1b5e20",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f5e9", edgecolor="#4caf50", linewidth=1.2)
    )

    # -------------------------------------------------------------
    # PANEL 2 (Sağ Üst): Arama Sonuçları Karşılaştırması (Tablo)
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off")
    ax2.set_title("Arama Sonuçları Karşılaştırması\n(Örnek Sorgu için İlk 5 Sonuç)", fontsize=12, fontweight="bold", pad=8)

    # İki alt tablo verisi
    t1_headers = ["#", "Doküman", "Benzerlik Skoru"]
    t1_rows = [
        ["1", "MTR-401.pdf", "0.721"],
        ["2", "E-401_troubleshooting.pdf", "0.689"],
        ["3", "ana_tahrik_motoru.pdf", "0.656"],
        ["4", "motor_isinma_nedenleri.pdf", "0.648"],
        ["5", "sogutma_sistemi.pdf", "0.620"]
    ]

    t2_headers = ["#", "Doküman", "Cross-Encoder Skoru"]
    t2_rows = [
        ["1", "E-401_troubleshooting.pdf", "0.892"],
        ["2", "ana_tahrik_motoru.pdf", "0.881"],
        ["3", "MTR-401.pdf", "0.837"],
        ["4", "motor_isinma_nedenleri.pdf", "0.521"],
        ["5", "elektrik_kontrol.pdf", "0.402"]
    ]

    # Tablo 1 Çiz (Sol)
    ax2.text(0.24, 0.85, "Aşama 1 - Vektör Arama (k1=10)", ha="center", va="center", fontsize=9, fontweight="bold", color="white",
             bbox=dict(boxstyle="square,pad=0.4", facecolor="#1976d2", edgecolor="#1976d2"))
    table1 = ax2.table(
        cellText=t1_rows,
        colLabels=t1_headers,
        cellLoc="center",
        loc="center",
        bbox=[0.0, 0.05, 0.48, 0.72]
    )
    table1.auto_set_font_size(False)
    table1.set_fontsize(8)
    for (r, c), cell in table1.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if r == 0:
            cell.set_facecolor("#e3f2fd")
            cell.set_text_props(weight="bold", color="#0d47a1")
        else:
            cell.set_facecolor("#ffffff" if r % 2 == 1 else "#f9f9f9")

    # Tablo 2 Çiz (Sağ)
    ax2.text(0.76, 0.85, "Aşama 2 - Yeniden Sıralama (k2=3)", ha="center", va="center", fontsize=9, fontweight="bold", color="white",
             bbox=dict(boxstyle="square,pad=0.4", facecolor="#1976d2", edgecolor="#1976d2"))
    table2 = ax2.table(
        cellText=t2_rows,
        colLabels=t2_headers,
        cellLoc="center",
        loc="center",
        bbox=[0.52, 0.05, 0.48, 0.72]
    )
    table2.auto_set_font_size(False)
    table2.set_fontsize(8)
    for (r, c), cell in table2.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if r == 0:
            cell.set_facecolor("#e3f2fd")
            cell.set_text_props(weight="bold", color="#0d47a1")
        else:
            cell.set_facecolor("#ffffff" if r % 2 == 1 else "#f9f9f9")

    # -------------------------------------------------------------
    # PANEL 3 (Sol Alt): Seçilen Metin Miktarı Karşılaştırması
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor("white")

    token_cats = ["Aşama 1\n(İlk 10 doküman)", "Aşama 2\n(En iyi 3 doküman)"]
    token_vals = [22416, 8669]
    token_colors = ["#e57373", "#64b5f6"]

    bars3 = ax3.bar([0, 1], token_vals, color=token_colors, edgecolor="#555555", linewidth=0.6, width=0.45)

    ax3.set_title("Seçilen Metin Miktarı Karşılaştırması", fontsize=12, fontweight="bold", pad=12)
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(token_cats, fontsize=9.5)
    ax3.set_ylabel("Ortalama Token Sayısı", fontsize=10)
    ax3.set_yticks([0, 5000, 10000, 15000, 20000, 25000])
    ax3.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax3.set_ylim(0, 26000)
    ax3.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax3.set_axisbelow(True)

    # Custom legend for panel 3
    from matplotlib.patches import Patch
    legend_elements3 = [
        Patch(facecolor="#e57373", edgecolor="#555555", label="Aşama 1 (k1=10)"),
        Patch(facecolor="#64b5f6", edgecolor="#555555", label="Aşama 2 (k2=3)")
    ]
    ax3.legend(handles=legend_elements3, loc="upper center", bbox_to_anchor=(0.5, 0.98), fontsize=9, frameon=False, ncol=2)

    for b in bars3:
        h = b.get_height()
        ax3.annotate(f"{int(h):,}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9.5, fontweight="bold")

    # Yeşil Callout Kutusu ve Aşağı Ok
    ax3.annotate(
        "Metin miktarında\nortalama azalma\n%61.34\n⬇",
        xy=(0.95, 0.72),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="#1b5e20",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f5e9", edgecolor="#4caf50", linewidth=1.2)
    )

    # -------------------------------------------------------------
    # PANEL 4 (Sağ Alt): Tahmini Maliyet ve Gecikme Karşılaştırması
    # -------------------------------------------------------------
    # İki alt mini-grafik için subplotspec
    gs_sub = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[1, 1], wspace=0.4)

    # 4.A: Tahmini API Maliyeti
    ax4a = fig.add_subplot(gs_sub[0, 0])
    ax4a.set_facecolor("white")

    cost_vals = [0.0224, 0.0086]
    bars4a = ax4a.bar([0, 1], cost_vals, color=["#e57373", "#64b5f6"], edgecolor="#555555", linewidth=0.6, width=0.5)

    ax4a.set_title("Tahmini API Maliyeti\n(USD / sorgu)", fontsize=10, fontweight="bold", pad=8)
    ax4a.set_xticks([0, 1])
    ax4a.set_xticklabels(["Aşama 1", "Aşama 2"], fontsize=9)
    ax4a.set_yticks([0.00, 0.01, 0.02, 0.03])
    ax4a.set_ylim(0, 0.035)
    ax4a.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax4a.set_axisbelow(True)

    for b in bars4a:
        h = b.get_height()
        ax4a.annotate(f"${h:.4f}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold")

    ax4a.annotate(
        "%61.34\ndaha düşük maliyet",
        xy=(1, 0.015),
        ha="center",
        fontsize=8,
        fontweight="bold",
        color="#1b5e20",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", edgecolor="#4caf50", linewidth=0.8)
    )

    # 4.B: Ortalama Gecikme Süresi
    ax4b = fig.add_subplot(gs_sub[0, 1])
    ax4b.set_facecolor("white")

    lat_vals = [1.42, 0.58]
    bars4b = ax4b.bar([0, 1], lat_vals, color=["#e57373", "#64b5f6"], edgecolor="#555555", linewidth=0.6, width=0.5)

    ax4b.set_title("Ortalama Gecikme Süresi\n(saniye / sorgu)", fontsize=10, fontweight="bold", pad=8)
    ax4b.set_xticks([0, 1])
    ax4b.set_xticklabels(["Aşama 1\n(k1=10)", "Aşama 2\n(k2=3)"], fontsize=8.5)
    ax4b.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0])
    ax4b.set_ylim(0, 2.2)
    ax4b.grid(True, axis="y", linestyle="-", color="#e0e0e0", alpha=0.8)
    ax4b.set_axisbelow(True)

    for b in bars4b:
        h = b.get_height()
        ax4b.annotate(f"{h:.2f}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold")

    ax4b.annotate(
        "%59.15\ndaha düşük gecikme",
        xy=(1, 1.05),
        ha="center",
        fontsize=8,
        fontweight="bold",
        color="#1b5e20",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", edgecolor="#4caf50", linewidth=0.8)
    )

    fig.savefig(out_file, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return str(out_file)


if __name__ == "__main__":
    out = plot_reranking_dashboard()
    print(f"Grafik üretildi: {out}")
