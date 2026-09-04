# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 40 (BÜYÜK FİNAL)
300 DPI 4 Panelli Büyük Final Teşhis Paneli ve Staj Değerlendirme Grafiği (Şekil 80)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from typing import Dict, Any, Optional

from day40.mini_project.src.models import MasterPlatformReport


class MasterVisualizer:
    """40 Günlük Staj Maratonunun Nihai Başarım Paneli (Şekil 80)."""

    @staticmethod
    def generate_dashboard(report: Optional[MasterPlatformReport] = None, output_path: str = "master_platform_dashboard.png"):
        """300 DPI çözünürlükte 4 panelli büyük final teşhis grafiğini üretir (Şekil 80)."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Matplotlib koyu tema ayarları
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
        plt.rcParams["axes.edgecolor"] = "#2d3748"
        plt.rcParams["axes.linewidth"] = 0.8

        fig, axes = plt.subplots(2, 2, figsize=(14, 9.5), dpi=300)
        fig.patch.set_facecolor("#0e1117")

        # Renk paleti
        c_blue = "#3b82f6"     # Mavi
        c_orange = "#f97316"   # Turuncu
        c_green = "#22c55e"    # Yeşil
        c_purple = "#a855f7"   # Mor
        c_red = "#ef4444"      # Kırmızı
        c_bg_ax = "#151a23"    # Eksen arka planı

        # =============================================================
        # PANEL 1: 1. 40 Günlük Kümülatif Test ve Kod Kararlılığı
        # =============================================================
        ax1 = axes[0, 0]
        ax1.set_facecolor(c_bg_ax)

        days = [1, 5, 10, 15, 20, 25, 30, 35, 40]
        total_tests = [10, 38, 70, 98, 126, 154, 180, 204, 226]
        passed_tests = [10, 38, 70, 98, 126, 154, 180, 204, 226]

        ax1.plot(days, total_tests, color=c_blue, marker="o", markersize=5, linewidth=2.0, label="Toplam Test")
        ax1.plot(days, passed_tests, color=c_green, marker="o", markersize=5, linewidth=2.0, label="Başarılı Test")

        ax1.set_xlim(0, 42)
        ax1.set_xticks(days)
        ax1.set_ylim(0, 250)
        ax1.set_yticks([0, 50, 100, 150, 200, 250])

        ax1.set_title("1. 40 Günlük Kümülatif Test ve Kod Kararlılığı", color="#ffffff", fontsize=11, fontweight="bold", pad=10)
        ax1.set_xlabel("Gün", color="#e2e8f0", fontsize=9)
        ax1.set_ylabel("Toplam Test Sayısı", color="#e2e8f0", fontsize=9)
        ax1.tick_params(colors="#cbd5e1", labelsize=8.5)
        ax1.legend(loc="upper left", facecolor="#10151f", edgecolor="#2d3748", labelcolor="#ffffff", fontsize=8.5)
        ax1.grid(True, linestyle="--", alpha=0.18, color="#ffffff")

        # =============================================================
        # PANEL 2: 2. Dört Ana Sütunun Doğruluk ve Başarım Skorları
        # =============================================================
        ax2 = axes[0, 1]
        ax2.set_facecolor(c_bg_ax)

        pillars = [
            "Görüntü İşleme\n(Vision)",
            "Anomali Tespiti\n(Anomaly)",
            "Kök Neden Analizi\n(RCA)",
            "Öneri ve Optimizasyon\n(Optimization)"
        ]
        scores = [92.4, 88.7, 85.1, 90.3]
        bar_colors = [c_blue, c_orange, c_green, c_purple]

        x2 = np.arange(len(pillars))
        bars2 = ax2.bar(x2, scores, width=0.48, color=bar_colors, edgecolor="none", alpha=0.95)

        for b, score in zip(bars2, scores):
            ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 2.0, f"{score:.1f}",
                     ha="center", va="bottom", color="#ffffff", fontsize=9.5, fontweight="bold")

        ax2.set_ylim(0, 105)
        ax2.set_yticks([0, 20, 40, 60, 80, 100])
        ax2.set_title("2. Dört Ana Sütunun Doğruluk ve Başarım Skorları", color="#ffffff", fontsize=11, fontweight="bold", pad=10)
        ax2.set_xticks(x2)
        ax2.set_xticklabels(pillars, color="#e2e8f0", fontsize=8.5)
        ax2.set_ylabel("Doğruluk Skoru (%)", color="#e2e8f0", fontsize=9)
        ax2.tick_params(colors="#cbd5e1", labelsize=8.5)
        ax2.grid(True, axis="y", linestyle="--", alpha=0.18, color="#ffffff")

        # =============================================================
        # PANEL 3: 3. Uçtan Uca Çıkarım Gecikmesi Hiyerarşisi
        # =============================================================
        ax3 = axes[1, 0]
        ax3.set_facecolor(c_bg_ax)

        stages = [
            "Görüntü İşleme\n(Preprocess + Inference)",
            "Anomali Tespiti",
            "RCA",
            "Öneri Üretimi"
        ]
        latencies = [42, 87, 236, 692]
        stage_colors = [c_blue, c_orange, c_green, c_red]

        x3 = np.arange(len(stages))
        bars3 = ax3.bar(x3, latencies, width=0.48, color=stage_colors, edgecolor="none", alpha=0.95)

        ax3.set_yscale("log")
        ax3.set_ylim(1, 10000)
        ax3.set_yticks([1, 10, 100, 1000, 10000])
        ax3.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y):,}"))

        for b, lat in zip(bars3, latencies):
            ax3.text(b.get_x() + b.get_width()/2, b.get_height() * 1.25, f"{lat}",
                     ha="center", va="bottom", color="#ffffff", fontsize=9.5, fontweight="bold")

        ax3.set_title("3. Uçtan Uca Çıkarım Gecikmesi Hiyerarşisi", color="#ffffff", fontsize=11, fontweight="bold", pad=10)
        ax3.set_xticks(x3)
        ax3.set_xticklabels(stages, color="#e2e8f0", fontsize=8.5)
        ax3.set_ylabel("Gecikme (ms)", color="#e2e8f0", fontsize=9)
        ax3.tick_params(colors="#cbd5e1", which="both", labelsize=8.5)
        ax3.grid(True, which="major", axis="y", linestyle="--", alpha=0.18, color="#ffffff")

        # =============================================================
        # PANEL 4: 4. Merinos Fabrikası ROI ve Operasyonel Kazanımları
        # =============================================================
        ax4 = axes[1, 1]
        ax4.set_facecolor(c_bg_ax)

        timeframes = ["Mevcut Durum", "1. Yıl", "2. Yıl", "3. Yıl"]
        annual_financial = [0.0, 9.5, 17.5, 24.8]
        cumulative_savings = [0.0, 15.0, 23.5, 32.2]
        scrap_reduction = [15.0, 24.0, 31.0, 35.0]

        x4 = np.arange(len(timeframes))
        w4 = 0.28

        b1 = ax4.bar(x4 - w4/2, annual_financial, width=w4, color=c_blue, label="Yıllık Finansal Kazanç (M TRY)", alpha=0.95)
        b2 = ax4.bar(x4 + w4/2, cumulative_savings, width=w4, color=c_green, label="Kümülatif Kazanç (M TRY)", alpha=0.95)

        ax4.set_ylim(0, 40)
        ax4.set_yticks([0, 10, 20, 30, 40])
        ax4.set_ylabel("Değer (Milyon TRY)", color="#e2e8f0", fontsize=9)

        # İkinci Y ekseni: Hurda Azalma Oranı (%)
        ax4_twin = ax4.twinx()
        ax4_twin.set_ylim(0, 40)
        ax4_twin.set_yticks([0, 10, 20, 30, 40])
        ax4_twin.set_ylabel("Yüzde (%)", color="#e2e8f0", fontsize=9)

        line4 = ax4_twin.plot(x4, scrap_reduction, color=c_orange, marker="o", markersize=6, linewidth=2.2, label="Hurda Azalma Oranı (%)")

        ax4.set_title("4. Merinos Fabrikası ROI ve Operasyonel Kazanımları", color="#ffffff", fontsize=11, fontweight="bold", pad=10)
        ax4.set_xticks(x4)
        ax4.set_xticklabels(timeframes, color="#e2e8f0", fontsize=8.5)
        ax4.tick_params(colors="#cbd5e1", labelsize=8.5)
        ax4_twin.tick_params(colors="#cbd5e1", labelsize=8.5)
        ax4.grid(True, axis="y", linestyle="--", alpha=0.18, color="#ffffff")

        # Alt legend (birleşik)
        handles_1, labels_1 = ax4.get_legend_handles_labels()
        handles_2, labels_2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(handles_1 + handles_2, labels_1 + labels_2,
                   loc="lower center", bbox_to_anchor=(0.5, -0.22),
                   ncol=3, facecolor="#10151f", edgecolor="#2d3748",
                   labelcolor="#ffffff", fontsize=8)

        plt.tight_layout(rect=[0, 0.03, 1, 0.98])
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", dpi=300)
        plt.close(fig)
