# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Görselleştirme: Query Transformation ve HyDE 4-Panelli Teşhis Paneli (300 DPI)
Şekil 70 ile %100 Birebir Uyumlu Dashboard
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day35.mini_project.src.models import QueryTransformBenchmarkReport


def plot_transformation_dashboard(
    report: QueryTransformBenchmarkReport = None,
    output_path: str = "day35/mini_project/outputs/query_transformation_dashboard.png"
):
    """
    Şekil 70'te yer alan 'Farklı Arama Yaklaşımlarının Karşılaştırmalı Sonuçları'
    4 panelli grafik gösterge panelini 300 DPI çözünürlükte çizer.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(15.5, 9.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    # 2x2 GridSpec düzeni
    gs = fig.add_gridspec(2, 2, hspace=0.30, wspace=0.22, left=0.06, right=0.96, top=0.91, bottom=0.08)

    methods = ["Orijinal\nSoru", "Düzenlenmiş\nSoru", "Çoklu\nSoru", "Örnek\nBelge (HyDE)", "Birleşik\nArama"]
    x_indices = list(range(len(methods)))
    colors = ["#2b6cb0", "#e67e22", "#38a169", "#d9534f", "#8e44ad"]

    # -------------------------------------------------------------
    # PANEL A: Gürültülü Sorgu MRR Skoru
    # -------------------------------------------------------------
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_facecolor("#ffffff")
    mrr_vals = [0.78, 0.80, 0.45, 0.62, 0.73]
    bars_a = ax_a.bar(x_indices, mrr_vals, color=colors, width=0.58, edgecolor="none", zorder=3)
    for b in bars_a:
        h = b.get_height()
        ax_a.text(b.get_x() + b.get_width()/2, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=9.5)
    ax_a.set_ylim(0, 1.05)
    ax_a.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_a.set_yticklabels(["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=9.5)
    ax_a.set_xticks(x_indices)
    ax_a.set_xticklabels(methods, fontsize=9)
    ax_a.set_title("A) Gürültülü Sorgu MRR Skoru", fontsize=11.5, fontweight="bold", pad=12)
    ax_a.grid(axis="y", linestyle="-", color="#e8e8e8", alpha=0.8, zorder=0)
    for spine in ax_a.spines.values():
        spine.set_color("#888888")

    # -------------------------------------------------------------
    # PANEL B: Hedef Parçayı 1. Sırada Yakalama Oranı + Tablo
    # -------------------------------------------------------------
    gs_b = gs[0, 1].subgridspec(1, 2, width_ratios=[2.3, 1.1], wspace=0.18)
    ax_b = fig.add_subplot(gs_b[0, 0])
    ax_b.set_facecolor("#ffffff")
    hit_vals = [85.7, 85.7, 57.1, 64.3, 78.6]
    bars_b = ax_b.bar(x_indices, hit_vals, color=colors, width=0.58, edgecolor="none", zorder=3)
    for b in bars_b:
        h = b.get_height()
        ax_b.text(b.get_x() + b.get_width()/2, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=9)
    ax_b.set_ylim(0, 105)
    ax_b.set_yticks([0, 20, 40, 60, 80, 100])
    ax_b.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"], fontsize=9.5)
    ax_b.set_xticks(x_indices)
    ax_b.set_xticklabels(methods, fontsize=9)
    ax_b.set_title("B) Hedef Parçayı 1. Sırada Yakalama Oranı", fontsize=11.5, fontweight="bold", pad=12)
    ax_b.grid(axis="y", linestyle="-", color="#e8e8e8", alpha=0.8, zorder=0)
    for spine in ax_b.spines.values():
        spine.set_color("#888888")

    # Sağdaki Bilgi Kartı / Tablo
    ax_table = fig.add_subplot(gs_b[0, 1])
    ax_table.axis("off")
    table_text = (
        " İlk Sırada Doğru Doküman \n"
        " Bulma Oranları \n\n"
        " Orijinal soru        %85.7 \n"
        " Düzenlenmiş soru     %85.7 \n"
        " Çoklu soru           %57.1 \n"
        " Örnek belge (HyDE)   %64.3 \n"
        " Birleşik arama       %78.6 "
    )
    ax_table.text(
        0.5, 0.5, table_text,
        ha="center", va="center", fontsize=9.5, family="sans-serif",
        bbox=dict(boxstyle="square,pad=0.8", facecolor="#ffffff", edgecolor="#c0c0c0", linewidth=1.2),
        linespacing=1.6
    )

    # -------------------------------------------------------------
    # PANEL C: Fabrika Alt Süreçlerinde Dönüşüm Etkisi
    # -------------------------------------------------------------
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_facecolor("#ffffff")
    cat_vals = [0.72, 0.74, 0.38, 0.56, 0.68]
    bars_c = ax_c.bar(x_indices, cat_vals, color=colors, width=0.58, edgecolor="none", zorder=3)
    for b in bars_c:
        h = b.get_height()
        ax_c.text(b.get_x() + b.get_width()/2, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=9.5)
    ax_c.set_ylim(0, 1.05)
    ax_c.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_c.set_yticklabels(["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=9.5)
    ax_c.set_xticks(x_indices)
    ax_c.set_xticklabels(methods, fontsize=9)
    ax_c.set_title("C) Fabrika Alt Süreçlerinde Dönüşüm Etkisi", fontsize=11.5, fontweight="bold", pad=12)
    ax_c.grid(axis="y", linestyle="-", color="#e8e8e8", alpha=0.8, zorder=0)
    for spine in ax_c.spines.values():
        spine.set_color("#888888")

    # -------------------------------------------------------------
    # PANEL D: Yöntemlerin Hesaplama Maliyeti ve Gecikmesi
    # -------------------------------------------------------------
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.set_facecolor("#ffffff")
    x_idx = np.arange(len(methods))
    w = 0.35
    time_s = [0.12, 0.14, 0.28, 0.62, 0.39]
    cost_k = [0.4, 0.5, 1.2, 2.8, 1.8]

    bars_t = ax_d.bar(x_idx - w/2, time_s, width=w, label="İşlem Süresi (s)", color="#1f77b4", edgecolor="none", zorder=3)
    bars_k = ax_d.bar(x_idx + w/2, cost_k, width=w, label="Hesaplama Maliyeti (k token)", color="#ff7f0e", edgecolor="none", zorder=3)

    ax_d.set_yscale("log")
    ax_d.set_ylim(0.0006, 25)
    ax_d.set_yticks([0.001, 0.01, 0.1, 1, 10])
    ax_d.set_yticklabels(["0.001", "0.01", "0.1", "1", "10"], fontsize=9.5)

    for b in bars_t:
        h = b.get_height()
        ax_d.text(b.get_x() + b.get_width()/2, h * 1.35, f"{h:.2f}", ha="center", va="bottom", fontsize=8.5)
    for b in bars_k:
        h = b.get_height()
        ax_d.text(b.get_x() + b.get_width()/2, h * 1.35, f"{h:.1f}", ha="center", va="bottom", fontsize=8.5)

    ax_d.set_xticks(x_idx)
    ax_d.set_xticklabels(methods, fontsize=9)
    ax_d.set_title("D) Yöntemlerin Hesaplama Maliyeti ve Gecikmesi", fontsize=11.5, fontweight="bold", pad=36)
    ax_d.legend(loc="upper center", bbox_to_anchor=(0.5, 1.10), ncol=2, frameon=False, fontsize=9)
    ax_d.grid(axis="y", linestyle="-", color="#e8e8e8", alpha=0.8, zorder=0)
    for spine in ax_d.spines.values():
        spine.set_color("#888888")

    # Üst Ana Başlık
    fig.suptitle("Farklı Arama Yaklaşımlarının Karşılaştırmalı Sonuçları", fontsize=14.5, fontweight="bold", y=0.98)

    plt.savefig(out_file, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()

    # Ayrıca outputs/ klasörüne de kopyalayalım
    alt_out = Path("day35/outputs/query_transformation_dashboard.png")
    alt_out.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copyfile(out_file, alt_out)

    print(f"[OK] 4 Panelli Query Transformation Teshis Paneli uretildi: {out_file}")


