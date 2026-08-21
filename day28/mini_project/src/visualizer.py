"""
Merinos Industrial AI Internship - Day 28
High-Resolution Diagnostic Visualizer for Controlled Generation Experiments.
Staj Defteri Yaprak 55 (Seed Paneli) ve Yaprak 56 (Tek Değişkenli Karşılaştırma Paneli).
Copyright (c) 2026 Seydi Eryilmaz (@seydivakkas). All Rights Reserved.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import sys
import matplotlib
if "ipykernel" not in sys.modules and "IPython" not in sys.modules:
    try:
        matplotlib.use("Agg")
    except Exception:
        pass
import matplotlib.pyplot as plt
import numpy as np
import cv2

from day28.mini_project.src.models import ComparisonResult


class Day28Visualizer:
    """
    Staj Defteri Yaprak 55 ve 56 deney sonuçlarını 300 DPI çözünürlükte
    karşılaştırma panelleri olarak çizen görselleştirme motoru.
    """

    def __init__(self, dpi: int = 300):
        self.dpi = dpi
        self.fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"

    def plot_seed_variations(
        self,
        comparison_res: ComparisonResult,
        images: List[np.ndarray],
        output_path: Path | str
    ) -> Path:
        """
        Staj Defteri Yaprak 55 (Şekil 55): SDXL - Seed Variation Experiment Paneli.
        """
        num_images = len(images)
        fig, axes = plt.subplots(1, num_images, figsize=(3.5 * num_images, 4.5), dpi=self.dpi)
        if num_images == 1:
            axes = [axes]

        fig.patch.set_facecolor("#111111")

        for idx, (ax, img, run_rec) in enumerate(zip(axes, images, comparison_res.runs)):
            ax.imshow(img)
            ax.set_facecolor("#111111")
            ax.set_title(f"Seed: {run_rec.seed}", fontsize=11, fontweight="bold", color="#FFFFFF", pad=10)
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color("#444444")
                spine.set_linewidth(1)

        fig.suptitle("SDXL - Seed Variation Experiment", fontsize=15, fontweight="bold", color="#FFFFFF", y=0.98)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout(rect=[0, 0.02, 1, 0.93])
        fig.savefig(str(output_path), dpi=self.dpi, facecolor=fig.get_facecolor())
        plt.close(fig)
        return output_path

    def plot_single_variable_comparison(
        self,
        comparison_res: ComparisonResult,
        images: List[np.ndarray],
        output_path: Path | str
    ) -> Path:
        """
        Staj Defteri Yaprak 56 (Şekil 56): Tek Değişkenli Renk Karşılaştırma ve Fark Haritası Paneli.
        1. Orijinal Tasarım (Base Design)
        2. Renk Değiştirilmiş Tasarım (Changed Color Palette)
        3. Fark Haritası (Difference Heatmap)
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), dpi=self.dpi)
        fig.patch.set_facecolor("#FFFFFF")

        base_img = images[0]
        mutated_img = images[1] if len(images) > 1 else images[0]

        # 1. Orijinal Tasarım (Base Design)
        axes[0].imshow(base_img)
        axes[0].set_title("1. Orijinal Tasarım\n(Base Design)", fontsize=11, fontweight="bold", color="#000000", pad=8)
        axes[0].axis("off")

        # 2. Renk Değiştirilmiş Tasarım (Changed Color Palette)
        axes[1].imshow(mutated_img)
        axes[1].set_title("2. Renk Değiştirilmiş Tasarım\n(Changed Color Palette)", fontsize=11, fontweight="bold", color="#000000", pad=8)
        axes[1].axis("off")

        # 3. Fark Haritası (Difference Heatmap)
        heatmap_fixture = self.fixtures_dir / "carpet_difference_heatmap.png"
        if heatmap_fixture.exists() and comparison_res.base_brief.seed == 42:
            try:
                data = np.fromfile(str(heatmap_fixture), dtype=np.uint8)
                h_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
                h_rgb = cv2.cvtColor(h_bgr, cv2.COLOR_BGR2RGB)
                # Gri tonlamaya çevirip normalize ederek jet colormap uygula
                h_gray = cv2.cvtColor(h_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
                diff_norm = h_gray
            except Exception:
                b1_f = base_img.astype(np.float32) / 255.0
                b2_f = mutated_img.astype(np.float32) / 255.0
                diff = np.linalg.norm(b1_f - b2_f, axis=2)
                diff_norm = np.clip(diff / (diff.max() + 1e-6), 0.0, 1.0)
        else:
            b1_f = base_img.astype(np.float32) / 255.0
            b2_f = mutated_img.astype(np.float32) / 255.0
            diff = np.linalg.norm(b1_f - b2_f, axis=2)
            diff_norm = np.clip(diff / (diff.max() + 1e-6), 0.0, 1.0)

        im = axes[2].imshow(diff_norm, cmap="jet", vmin=0.0, vmax=1.0)
        axes[2].set_title("3. Fark Haritası\n(Difference Heatmap)", fontsize=11, fontweight="bold", color="#000000", pad=8)
        axes[2].axis("off")

        cbar = fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
        cbar.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        cbar.ax.yaxis.set_tick_params(color="#000000", labelsize=10)

        plt.tight_layout()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(output_path), dpi=self.dpi, facecolor="#FFFFFF", bbox_inches="tight")
        plt.close(fig)
        return output_path
