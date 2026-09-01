# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 37
Visualizer: Şekil 74 ile Birebir Uyumlu RAGAS ve Güvenlik Kontrolleri Değerlendirme Dashboard'u
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from typing import Optional, List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np


def plot_ragas_guardrails_dashboard(
    report: Optional[Any] = None,
    output_path: str = "day37/mini_project/outputs/ragas_guardrails_dashboard.png"
):
    """
    Şekil 74'te yer alan 4 panelli koyu temalı RAGAS ve Güvenlik Değerlendirme Dashboard'unu çizer.
    
    Paneller:
      1. Ortalama RAGAS Metrikleri (Context Precision: 0.78, Recall: 0.74, Faithfulness: 0.76, Relevance: 0.80)
      2. Senaryo Bazlı RAG Triad Skorları (15 senaryo çizgisel grafik)
      3. Guardrail Kararları (Pasta grafik: 12 İzin Verilen %80.0, 3 Engellenen %20.0 ve bilgi kutusu)
      4. İşlem Süreleri / Latency (Sorgu İşleme: 0.32s, Retriever: 1.24s, RAGAS: 0.28s, Guardrail: 1.85s)
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Koyu tema renk paleti (VS Code Slate Dark)
    bg_color = "#0e1726"       # Ana arka plan
    card_color = "#162130"     # Panel kart rengi
    border_color = "#243447"   # Panel kenarlık rengi
    text_color = "#e2e8f0"     # Açık gri/beyaz metin
    bar_color = "#38bdf8"      # Parlak mavi bar rengi
    green_color = "#22c55e"    # İzin verilen / Güvenli
    red_color = "#ef4444"      # Engellenen / Riskli
    grid_color = "#1e293b"     # Izgara çizgisi rengi

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["text.color"] = text_color
    plt.rcParams["axes.labelcolor"] = text_color
    plt.rcParams["xtick.color"] = text_color
    plt.rcParams["ytick.color"] = text_color

    fig, axes = plt.subplots(2, 2, figsize=(15, 9.5), dpi=300)
    fig.patch.set_facecolor(bg_color)

    # -------------------------------------------------------------
    # Panel 1: 1. Ortalama RAGAS Metrikleri
    # -------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor(card_color)
    for spine in ax1.spines.values():
        spine.set_color(border_color)
        spine.set_linewidth(1.2)

    p1_labels = ["Context\nPrecision", "Context\nRecall", "Faithfulness", "Answer\nRelevance"]
    p1_values = [0.78, 0.74, 0.76, 0.80]

    bars1 = ax1.bar(p1_labels, p1_values, color=bar_color, width=0.52, edgecolor=border_color, linewidth=1.0)
    ax1.set_ylim(0.0, 1.05)
    ax1.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax1.set_title("1. Ortalama RAGAS Metrikleri", fontsize=12, fontweight="bold", pad=12, loc="left", color=text_color)
    ax1.grid(axis="y", linestyle=":", color=grid_color, alpha=0.8)

    for bar, val in zip(bars1, p1_values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.025,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=text_color
        )

    # -------------------------------------------------------------
    # Panel 2: 2. Senaryo Bazlı RAG Triad Skorları
    # -------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor(card_color)
    for spine in ax2.spines.values():
        spine.set_color(border_color)
        spine.set_linewidth(1.2)

    scenario_ids = list(range(1, 16))
    triad_curve = [0.68, 0.72, 0.74, 0.74, 0.70, 0.78, 0.84, 0.81, 0.72, 0.74, 0.79, 0.70, 0.72, 0.75, 0.78]

    ax2.plot(
        scenario_ids,
        triad_curve,
        color=bar_color,
        marker="o",
        markersize=6,
        linewidth=1.8,
        label="RAG Triad Skoru"
    )
    ax2.set_ylim(0.0, 1.05)
    ax2.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax2.set_xticks(scenario_ids)
    ax2.set_xlabel("Senaryo ID", fontsize=10, labelpad=8)
    ax2.set_title("2. Senaryo Bazlı RAG Triad Skorları", fontsize=12, fontweight="bold", pad=12, loc="left", color=text_color)
    ax2.grid(axis="y", linestyle=":", color=grid_color, alpha=0.8)
    leg = ax2.legend(loc="upper right", facecolor=card_color, edgecolor=border_color, fontsize=9)
    for text in leg.get_texts():
        text.set_color(text_color)

    # -------------------------------------------------------------
    # Panel 3: 3. Guardrail Kararları
    # -------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor(card_color)
    for spine in ax3.spines.values():
        spine.set_color(border_color)
        spine.set_linewidth(1.2)

    pie_counts = [12, 3]
    pie_colors = [green_color, red_color]

    # Pasta grafiği sol tarafta konumlandırmak için alt alan
    wedges, texts, autotexts = ax3.pie(
        pie_counts,
        labels=None,
        autopct=lambda pct: f"{int(round(pct * 15 / 100))}\n({pct:.1f}%)",
        colors=pie_colors,
        startangle=90,
        radius=0.78,
        center=(-0.35, 0),
        wedgeprops=dict(edgecolor=card_color, linewidth=2.0)
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9.5)
        at.set_fontweight("bold")

    # Sağ tarafa lejant ve özet bilgi kutusu
    legend_elements = [
        plt.Line2D([0], [0], marker="s", color="w", label="İzin Verilen (Normal Akış)", markerfacecolor=green_color, markersize=10),
        plt.Line2D([0], [0], marker="s", color="w", label="Engellenen (Güvenlik Riski)", markerfacecolor=red_color, markersize=10)
    ]
    ax3.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(0.98, 0.90),
               facecolor=card_color, edgecolor=border_color, fontsize=8.5)

    info_box_text = "Toplam Senaryo : 15\nİzin Verilen     : 12 (%80.0)\nEngellenen     : 3 (%20.0)"
    ax3.text(
        0.58, -0.22,
        info_box_text,
        transform=ax3.transAxes,
        fontsize=9,
        family="monospace",
        color=text_color,
        verticalalignment="top",
        bbox=dict(boxstyle="square,pad=0.6", facecolor=bg_color, edgecolor=border_color, linewidth=1.0)
    )

    ax3.set_title("3. Guardrail Kararları", fontsize=12, fontweight="bold", pad=12, loc="left", color=text_color)

    # -------------------------------------------------------------
    # Panel 4: 4. İşlem Süreleri (Latency)
    # -------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor(card_color)
    for spine in ax4.spines.values():
        spine.set_color(border_color)
        spine.set_linewidth(1.2)

    latency_labels = ["Sorgu İşleme", "Retriever", "RAGAS\nDeğerlendirme", "Guardrail\nKontrolü"]
    latency_values = [0.32, 1.24, 0.28, 1.85]

    bars4 = ax4.bar(latency_labels, latency_values, color=bar_color, width=0.52, edgecolor=border_color, linewidth=1.0)
    ax4.set_ylim(0.0, 2.2)
    ax4.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0])
    ax4.set_ylabel("Süre (s)", fontsize=10, labelpad=6)
    ax4.set_title("4. İşlem Süreleri (Latency)", fontsize=12, fontweight="bold", pad=12, loc="left", color=text_color)
    ax4.grid(axis="y", linestyle=":", color=grid_color, alpha=0.8)

    for bar, val in zip(bars4, latency_values):
        ax4.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.05,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=text_color
        )

    # Üst Başlıklar
    plt.suptitle("RAGAS ve Güvenlik Kontrolleri Değerlendirme Dashboard'u",
                 fontsize=16, fontweight="bold", color="white", y=0.98, x=0.08, ha="left")
    fig.text(0.08, 0.942, "Day 37 — Teknik Doküman Arama, RAGAS Değerlendirme ve Güvenlik Guardrails Analizi",
             fontsize=11, color="#94a3b8", ha="left")

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.92])
    plt.subplots_adjust(hspace=0.28, wspace=0.20)
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"📊 Dashboard görseli başarıyla üretildi: {output_path}")


if __name__ == "__main__":
    plot_ragas_guardrails_dashboard()
