# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
300 DPI 4-Panel Master Diagnostic Panel Generator.
Day 28 Üretim + Day 29 Görsel Analiz Tümleşik Raporlayıcısı (Yaprak 59-60).
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Union
import sys
import matplotlib
if "ipykernel" not in sys.modules:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cv2

from day30.mini_project.src.models import IntegratedPipelineOutput


class CarpetPipelineVisualizer:
    """
    300 DPI 4-Panelli Tümleşik Teşhis ve Raporlama Görselleştiricisi (Staj Defteri Yaprak 59-60).
    
    Paneller:
    1. Üretilen Halı Deseni ve Yapılandırılmış İstem Parametreleri (Day 28)
    2. K-Means Baskın Renk Ayrıştırması ve CIEDE2000 Merinos İplik Bobini Uyumu (Day 29)
    3. Yatay/Dikey Simetri Skoru ve Sonsuz Rulo Dikiş Sürekliliği (Day 29)
    4. CNN Embedding ile Bulunan Top-K Benzer Referans Halılar (Day 29)
    """

    def __init__(self, dpi: int = 300):
        self.dpi = dpi

    def create_master_diagnostic_panel(
        self,
        output_data: IntegratedPipelineOutput,
        image_rgb: Optional[np.ndarray] = None,
        save_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        4 panelli yüksek çözünürlüklü grafik panelini oluşturur ve kaydeder.
        """
        if save_path is None:
            save_path = Path(output_data.generated_image_path).parent / f"{output_data.brief.brief_id}_diagnostic_panel.png"
        else:
            save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Görsel yükleme
        if image_rgb is None:
            if output_data.generated_image_path and Path(output_data.generated_image_path).exists():
                bgr = cv2.imread(output_data.generated_image_path)
                if bgr is not None:
                    image_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = np.full((256, 256, 3), 240, dtype=np.uint8)
            else:
                image_rgb = np.full((256, 256, 3), 240, dtype=np.uint8)

        fig, axes = plt.subplots(2, 2, figsize=(18, 14), dpi=self.dpi)
        plt.subplots_adjust(hspace=0.28, wspace=0.22)

        # Başlık Bilgisi
        fig.suptitle(
            f"MERİNOS HALI SANAYİ A.Ş. — TÜMLEŞİK DESEN ÜRETİM VE GÖRSEL ANALİZ BORU HATTI\n"
            f"Brif: {output_data.brief.brief_id} | Stil: {output_data.brief.style} | "
            f"Toplam Süre: {output_data.total_latency_ms:.1f} ms | Durum: {'BAŞARILI' if output_data.success else 'HATA'}",
            fontsize=15,
            fontweight="bold",
            color="#1B243B",
            y=0.98
        )

        # ----------------------------------------------------------------------
        # PANEL 1: Üretilen Halı Deseni ve Bilgi Kartı (Day 28)
        # ----------------------------------------------------------------------
        ax1 = axes[0, 0]
        ax1.imshow(image_rgb)
        ax1.set_title("1. Üretilen Halı Deseni & İstem Parametreleri (Day 28 SDXL)", fontsize=12, fontweight="bold", color="#8C1D2F")
        ax1.axis("off")

        prompt_snippet = output_data.prompt_result.assembled_prompt
        if len(prompt_snippet) > 100:
            prompt_snippet = prompt_snippet[:97] + "..."

        info_box = (
            f"Brif: {output_data.brief.brief_id}\n"
            f"Stil: {output_data.brief.style}\n"
            f"Motif: {output_data.brief.motif}\n"
            f"Renk: {output_data.brief.primary_color}"
            + (f" & {output_data.brief.secondary_color}" if output_data.brief.secondary_color else "")
            + f"\nSimetri: {output_data.brief.symmetry_mode.value}\n"
            f"Tohum (Seed): {output_data.brief.seed}\n"
            f"Prompt: {prompt_snippet}"
        )
        ax1.text(
            15, image_rgb.shape[0] - 25,
            info_box,
            fontsize=9,
            color="white",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1B243B", alpha=0.85, edgecolor="#C9A050", lw=1.5)
        )

        # ----------------------------------------------------------------------
        # PANEL 2: K-Means Baskın Renkler ve CIEDE2000 İplik Eşleşmesi (Day 29)
        # ----------------------------------------------------------------------
        ax2 = axes[0, 1]
        ax2.set_title("2. K-Means Baskın Renkler & CIEDE2000 İplik Uyumu (Day 29)", fontsize=12, fontweight="bold", color="#1B243B")

        dominant_colors = output_data.color_analysis.get("dominant_colors", [])
        if dominant_colors:
            names = [f"{c['nearest_yarn'][:16]}\n(ΔE={c['delta_e']:.2f})" for c in dominant_colors]
            percentages = [c["percentage"] for c in dominant_colors]
            hex_colors = [c["hex"] for c in dominant_colors]

            y_pos = np.arange(len(dominant_colors))
            bars = ax2.barh(y_pos, percentages, color=hex_colors, edgecolor="#2F3136", lw=1.2, height=0.6)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(names, fontsize=9)
            ax2.invert_yaxis()
            ax2.set_xlabel("Yüzdesel Alan Kapsamı (%)", fontsize=10)
            ax2.set_xlim(0, max(percentages) + 14 if percentages else 100)

            for bar, pct in zip(bars, percentages):
                ax2.text(bar.get_width() + 1.0, bar.get_y() + bar.get_height() / 2.0, f"%{pct:.1f}", va="center", fontsize=9, fontweight="bold")

            mean_dE = output_data.color_analysis.get("mean_delta_e", 0.0)
            status_color = "#2E7D32" if mean_dE <= 5.0 else "#D32F2F"
            status_text = "UYGUN (ΔE ≤ 5.0)" if mean_dE <= 5.0 else "UYARI (ΔE > 5.0)"
            ax2.text(
                0.97, 0.05,
                f"Ortalama ΔE*: {mean_dE:.2f} — {status_text}",
                transform=ax2.transAxes,
                ha="right",
                fontsize=10,
                fontweight="bold",
                color=status_color,
                bbox=dict(boxstyle="square,pad=0.4", facecolor="#F5F2EB", edgecolor=status_color, lw=1.2)
            )
        else:
            ax2.text(0.5, 0.5, "Renk analiz verisi bulunamadı.", ha="center", va="center")

        # ----------------------------------------------------------------------
        # PANEL 3: Simetri ve Kenar/Dikiş Süreklilik Grafiği (Day 29)
        # ----------------------------------------------------------------------
        ax3 = axes[1, 0]
        ax3.set_title("3. Geometrik Simetri ve Dikiş Sürekliliği (Day 29)", fontsize=12, fontweight="bold", color="#1B243B")

        sym = output_data.symmetry_analysis
        seam = output_data.seam_analysis
        metrics = ["Yatay Simetri", "Dikey Simetri", "Dörtlü Çeyrek", "Otokorelasyon"]
        scores = [
            sym.get("horizontal_score", 0.0),
            sym.get("vertical_score", 0.0),
            sym.get("quadrant_score", 0.0),
            sym.get("repeat_autocorr", 0.0),
        ]
        colors_bar = ["#587C52", "#1B243B", "#C9A050", "#8C1D2F"]

        bars3 = ax3.bar(metrics, scores, color=colors_bar, width=0.45, edgecolor="#2F3136", lw=1.2)
        ax3.set_ylim(0, 1.15)
        ax3.set_ylabel("Simetri Skoru (0.0 - 1.0)", fontsize=10)
        ax3.axhline(0.70, color="orange", linestyle="--", alpha=0.7, label="Kabul Eşiği (0.70)")
        ax3.axhline(0.90, color="green", linestyle=":", alpha=0.7, label="Mükemmel Eşiği (0.90)")

        for bar, val in zip(bars3, scores):
            ax3.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 0.02, f"{val:.3f}", ha="center", fontsize=9, fontweight="bold")

        ax3.legend(loc="upper left", fontsize=8)

        # Dikiş atlama bilgisi kutusu
        is_tileable = seam.get("is_tileable", False)
        sobel_jump = seam.get("sobel_jump", 0.0)
        seam_color = "#2E7D32" if is_tileable else "#D32F2F"
        seam_badge = "Dikiş Uygun (Tekrarlanabilir)" if is_tileable else "Dikiş Uyumsuz"
        ax3.text(
            0.97, 0.85,
            f"Dikiş Atlama: {sobel_jump:.2f} px\n({seam_badge})",
            transform=ax3.transAxes,
            ha="right",
            fontsize=9,
            fontweight="bold",
            color=seam_color,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor=seam_color, lw=1.2)
        )

        # ----------------------------------------------------------------------
        # PANEL 4: CNN Embedding ile Top-K Benzer Referans Halılar (Day 29)
        # ----------------------------------------------------------------------
        ax4 = axes[1, 1]
        ax4.set_title("4. CNN Embedding ile En Yakın Referans Halılar (Day 29)", fontsize=12, fontweight="bold", color="#1B243B")

        sims = output_data.similar_carpets
        if sims and any(s.get("similarity_score", 0.0) > 0 for s in sims):
            labels = [f"#{i+1} {s.get('name', 'Halı')[:16]}\n({s.get('carpet_id', '')})" for i, s in enumerate(sims)]
            scores_sim = [s.get("similarity_score", 0.0) for s in sims]

            y_pos4 = np.arange(len(sims))
            bars4 = ax4.barh(y_pos4, scores_sim, color="#C9A050", edgecolor="#1B243B", lw=1.2, height=0.55)
            ax4.set_yticks(y_pos4)
            ax4.set_yticklabels(labels, fontsize=9)
            ax4.invert_yaxis()
            ax4.set_xlabel("Kosinüs Benzerlik Skoru (Cosine Similarity)", fontsize=10)
            ax4.set_xlim(0, 1.1)

            for bar, score in zip(bars4, scores_sim):
                ax4.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2.0, f"{score:.3f}", va="center", fontsize=9, fontweight="bold")
        else:
            # Hata / Fallback durumu (Yaprak 60)
            ax4.text(
                0.5, 0.5,
                "UYARI (Yaprak 60):\nReferans görsel koleksiyonu boş veya katalog bulunamadı.\nBenzerlik araması güvenli biçimde atlandı.",
                ha="center", va="center", fontsize=10, color="#D32F2F", fontweight="bold"
            )

        # Alt Bilgi Notu (Yaprak 60 Sınır Beyanı)
        disclaimer = (
            "MÜHENDİSLİK SINIRLARI BEYANI (Staj Defteri Yaprak 60): "
            "Yukarıdaki analizler yalnızca sayısal ön inceleme niteliğinde olup; "
            "jakar tezgahında mutlak dokunabilirlik garantisi, estetik kesinlik veya telif tescili sağlamaz."
        )
        fig.text(0.5, 0.02, disclaimer, ha="center", fontsize=8.5, color="#555555", style="italic")

        plt.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        return save_path


# Şekil 59 İsim Uyumluluğu
CarpetVisualizer = CarpetPipelineVisualizer
