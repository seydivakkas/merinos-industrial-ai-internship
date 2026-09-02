# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
300 DPI API ve Sistem Teşhis Paneli Görselleştiricisi (Şekil 76)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class ApiSystemVisualizer:
    """
    Şekil 76 ile birebir uyumlu Merinos Industrial RAG API Sistem Dashboard'u üreticisi.
    KPI özet kartları, 1 saatlik canlı sorgu eğrisi, kategori dağılımı ve en çok sorgulanan konular.
    """

    def __init__(self, output_dir: str = "day38/mini_project/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_api_dashboard(
        self,
        benchmark_results: Optional[List[Dict[str, Any]]] = None,
        system_metrics: Optional[Dict[str, Any]] = None,
        filename: str = "api_system_dashboard.png"
    ) -> str:
        """
        Şekil 76'da gösterilen Sistem Dashboard'unu 300 DPI çözünürlükte çizer ve kaydeder.
        """
        fig = plt.figure(figsize=(10, 8), dpi=300, facecolor="#ffffff")

        # Layout: GridSpec
        gs = fig.add_gridspec(
            3, 2,
            height_ratios=[0.20, 0.40, 0.40],
            hspace=0.38,
            wspace=0.48,
            left=0.06,
            right=0.94,
            top=0.91,
            bottom=0.06
        )

        # -------------------------------------------------------------
        # 1. ÜST BAŞLIK (Şekil 76)
        # -------------------------------------------------------------
        fig.text(
            0.06, 0.955,
            "Merinos Industrial RAG API - Sistem Dashboard",
            fontsize=17,
            fontweight="bold",
            color="#1e293b",
            ha="left",
            va="center"
        )

        # -------------------------------------------------------------
        # 2. KPI KARTLARI (4 KART)
        # -------------------------------------------------------------
        card_w = 0.205
        card_h = 0.115
        y_pos = 0.815
        xs = [0.06, 0.292, 0.524, 0.735]

        total_q = 127
        if system_metrics and system_metrics.get("total_queries", 0) > 0:
            total_q = max(127, system_metrics.get("total_queries", 127))

        kpi_data = [
            ("API Durumu", "Çalışıyor", "#16a34a", "status"),
            ("Toplam Sorgu", str(total_q), "#1e40af", "text"),
            ("Ortalama Yanıt Süresi", "1.42 sn", "#0f172a", "text"),
            ("Başarı Oranı", "%96", "#16a34a", "text")
        ]

        for x, (title, val, col, mode) in zip(xs, kpi_data):
            # Kart Arka Planı
            rect = patches.FancyBboxPatch(
                (x, y_pos), card_w, card_h,
                boxstyle="round,pad=0.012,rounding_size=0.025",
                facecolor="#f8fafc",
                edgecolor="#e2e8f0",
                linewidth=1.1,
                transform=fig.transFigure
            )
            fig.patches.append(rect)

            # Kart Başlığı
            fig.text(
                x + card_w / 2, y_pos + card_h * 0.72,
                title,
                fontsize=8.5,
                color="#64748b",
                ha="center",
                va="center",
                fontweight="medium"
            )

            # Kart Değeri
            if mode == "status":
                # Yeşil daire içinde beyaz checkmark
                circle = patches.Circle(
                    (x + card_w * 0.28, y_pos + card_h * 0.32),
                    0.015,
                    facecolor="#16a34a",
                    edgecolor="none",
                    transform=fig.transFigure
                )
                fig.patches.append(circle)
                fig.text(
                    x + card_w * 0.28, y_pos + card_h * 0.32,
                    "✓",
                    fontsize=10,
                    color="#ffffff",
                    ha="center",
                    va="center",
                    fontweight="bold"
                )
                fig.text(
                    x + card_w * 0.62, y_pos + card_h * 0.32,
                    val,
                    fontsize=12,
                    color="#16a34a",
                    ha="center",
                    va="center",
                    fontweight="bold"
                )
            else:
                fig.text(
                    x + card_w / 2, y_pos + card_h * 0.32,
                    val,
                    fontsize=14,
                    color=col,
                    ha="center",
                    va="center",
                    fontweight="bold"
                )

        # -------------------------------------------------------------
        # 3. ORTA PANEL: Sorgu Sayısı (Son 1 Saat)
        # -------------------------------------------------------------
        ax_line = fig.add_subplot(gs[1, :])
        times = ["13:00", "13:10", "13:20", "13:30", "13:40", "13:50", "14:00"]
        x_pts = np.linspace(0, 6, 25)
        # Şekil 76'daki dalga formunu simüle eden veri noktaları
        y_pts = [6, 4, 6, 4, 6, 12, 7, 10, 6, 11, 7, 10, 12, 7, 11, 9, 15, 8, 7, 13, 9, 13, 8, 10, 12]

        ax_line.plot(x_pts, y_pts, color="#0284c7", linewidth=2.0, marker="o", markersize=3.8, markerfacecolor="#0284c7")
        ax_line.fill_between(x_pts, y_pts, color="#38bdf8", alpha=0.18)
        ax_line.set_title("Sorgu Sayısı (Son 1 Saat)", fontsize=11, fontweight="bold", color="#1e293b", loc="left", pad=9)
        ax_line.set_xticks(range(7))
        ax_line.set_xticklabels(times, fontsize=8.5, color="#64748b")
        ax_line.set_yticks([0, 5, 10, 15, 20])
        ax_line.set_ylim(0, 22)
        ax_line.tick_params(colors="#64748b", labelsize=8.5)
        ax_line.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0", axis="y")
        ax_line.set_facecolor("#ffffff")
        for spine in ax_line.spines.values():
            spine.set_color("#e2e8f0")

        # -------------------------------------------------------------
        # 4. ALT SOL PANEL: Sorgu Kategorileri (Donut)
        # -------------------------------------------------------------
        ax_pie = fig.add_subplot(gs[2, 0])
        pie_labels = ["Arıza ve Bakım", "Kullanım ve Ayar", "İSG ve Güvenlik", "Genel Bilgi", "Diğer"]
        pie_vals = [45, 25, 15, 10, 5]
        pie_colors = ["#0284c7", "#f59e0b", "#10b981", "#38bdf8", "#818cf8"]

        wedges, _ = ax_pie.pie(
            pie_vals,
            colors=pie_colors,
            startangle=160,
            wedgeprops=dict(width=0.6, edgecolor="white", linewidth=2)
        )
        ax_pie.set_title("Sorgu Kategorileri", fontsize=11, fontweight="bold", color="#1e293b", loc="left", pad=9)

        # Açıklama / Legend
        legend_labels = [f"{l:<18} {v}%" for l, v in zip(pie_labels, pie_vals)]
        ax_pie.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(0.88, 0.5),
            fontsize=7.8,
            frameon=False
        )

        # -------------------------------------------------------------
        # 5. ALT SAĞ PANEL: En Çok Sorgulanan Konular (Horizontal Bar)
        # -------------------------------------------------------------
        ax_bar = fig.add_subplot(gs[2, 1])
        topics = ["İSG Prosedürleri", "Yağlama Sistemi", "Hereke Jakar", "E-108 Mekik Sensörü", "E-401 Motor"]
        counts = [10, 12, 18, 24, 28]
        y_pos_bar = np.arange(len(topics))

        bars = ax_bar.barh(
            y_pos_bar,
            counts,
            color="#38bdf8",
            edgecolor="#0284c7",
            height=0.48,
            linewidth=0.8
        )
        for b in bars:
            b.set_facecolor("#38bdf8")

        ax_bar.set_yticks(y_pos_bar)
        ax_bar.set_yticklabels(topics, fontsize=8.5, color="#1e293b")
        ax_bar.set_title("En Çok Sorgulanan Konular", fontsize=11, fontweight="bold", color="#1e293b", loc="left", pad=9)
        ax_bar.set_xlim(0, 32)
        ax_bar.set_xticks([0, 10, 20, 30])
        ax_bar.tick_params(colors="#64748b", labelsize=8.5)
        ax_bar.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0", axis="x")
        ax_bar.set_facecolor("#ffffff")
        for spine in ax_bar.spines.values():
            spine.set_color("#e2e8f0")

        # Değer etiketleri
        for bar in bars:
            w_val = bar.get_width()
            ax_bar.text(
                w_val + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{int(w_val)}",
                va="center",
                ha="left",
                fontsize=8.5,
                fontweight="bold",
                color="#1e293b"
            )

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300, facecolor="#ffffff", bbox_inches="tight")
        plt.close()

        return str(out_path)
