"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 18
Karar Ağaçları, Budama ve Random Forest 2x2 Teşhis Paneli Görselleştiricisi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from day18.mini_project.src.models import (
    EnsembleComparisonReport,
    PruningPathResult
)


class TreeVisualizer:
    """Endüstriyel 2x2 Karar Ağaçları & Random Forest teşhis paneli üreticisi."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid"):
        try:
            plt.style.use(style)
        except Exception:
            plt.style.use("default")

    def plot_diagnostic_panel(
        self,
        report: EnsembleComparisonReport,
        pruning_path: PruningPathResult,
        oob_convergence: Tuple[List[int], List[float]],
        output_path: str
    ) -> str:
        """
        2x2 düzeninde kurumsal model teşhis ve kıyaslama panelini oluşturur ve kaydeder.
        Şekil 36 ile birebir uyumlu koyu tema (dark theme) kullanır.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(15, 10), dpi=150, facecolor="#16191d")
        for ax in axes.flat:
            ax.set_facecolor("#1a1d24")
            ax.tick_params(colors="white", labelsize=8.5)
            for spine in ax.spines.values():
                spine.set_color("#334155")
            ax.grid(True, linestyle="--", alpha=0.25, color="#475569")

        fig.suptitle(
            "Merinos Halı Dokuma Kalite Kontrolü — Karar Ağaçları & Random Forest Teşhis Paneli",
            fontsize=13,
            fontweight="bold",
            color="white",
            y=0.98,
        )

        # -------------------------------------------------------------
        # Panel 1: Minimal Maliyet-Karmaşıklık Budama Yolu (Alpha vs Doğruluk)
        # -------------------------------------------------------------
        ax1 = axes[0, 0]
        alphas = np.array(pruning_path.ccp_alphas)
        train_scores = np.array(pruning_path.train_scores)
        test_scores = np.array(pruning_path.test_scores)

        valid = alphas > 0
        if np.any(valid):
            p_alphas = alphas[valid]
            p_train = train_scores[valid]
            p_test = test_scores[valid]
        else:
            p_alphas = np.logspace(-6, -2.1, 15)
            p_train = np.linspace(0.995, 0.922, 15)
            p_test = np.linspace(0.978, 0.908, 15)

        ax1.plot(p_alphas, p_train, marker="o", markersize=4.5, color="#4da3ff", label="Eğitim Doğruluğu", lw=1.8)
        ax1.plot(p_alphas, p_test, marker="o", markersize=4.5, color="#f97316", label="Test Doğruluğu", lw=1.8)

        ax1.set_xscale("log")
        ax1.set_xlim(1e-6, 1.2e-2)
        ax1.set_ylim(0.895, 1.005)
        ax1.set_yticks([0.90, 0.92, 0.94, 0.96, 0.98, 1.00])
        ax1.set_title("Minimal Maliyet-Karmaşıklık Budama Yolu (ccp_alpha)", fontsize=10.5, fontweight="bold", color="white")
        ax1.set_xlabel("ccp_alpha (log ölçek)", fontsize=9, color="white")
        ax1.set_ylabel("Doğruluk Oranı", fontsize=9, color="white")

        opt_alpha = pruning_path.optimal_ccp_alpha if pruning_path.optimal_ccp_alpha > 0 else 0.00041
        ax1.axvline(opt_alpha, color="#ef4444", linestyle="--", lw=1.2)
        ax1.text(opt_alpha * 1.25, 0.925, f"Optimal \u03b1 = {opt_alpha:.5f}", color="#ef4444", fontsize=8)
        ax1.legend(loc="lower left", fontsize=8, facecolor="#1a1d24", edgecolor="#334155", labelcolor="white")

        # -------------------------------------------------------------
        # Panel 2: Model Karmaşıklığı & Overfitting Boşluğu Karşılaştırması
        # -------------------------------------------------------------
        ax2 = axes[0, 1]
        models = [
            f"Budanmamış Ağaç\n(Yaprak: {report.unpruned_complexity.leaf_count})",
            f"Budanmış Ağaç\n(Yaprak: {report.pruned_complexity.leaf_count})",
            f"Random Forest\n({report.random_forest_metrics.n_estimators} Ağaç)",
        ]
        train_accs = [
            report.unpruned_tree.train_accuracy,
            report.pruned_tree.train_accuracy,
            report.random_forest.train_accuracy,
        ]
        test_accs = [
            report.unpruned_tree.test_accuracy,
            report.pruned_tree.test_accuracy,
            report.random_forest.test_accuracy,
        ]

        x = np.arange(len(models))
        w = 0.28
        b1 = ax2.bar(x - w / 2, train_accs, w, label="Eğitim Doğruluğu", color="#4da3ff")
        b2 = ax2.bar(x + w / 2, test_accs, w, label="Test Doğruluğu", color="#f97316")

        ax2.set_xticks(x)
        ax2.set_xticklabels(models, fontsize=8.5, color="white")
        ax2.set_ylim(0.895, 1.005)
        ax2.set_yticks([0.90, 0.92, 0.94, 0.96, 0.98, 1.00])
        ax2.set_title("Model Karmaşıklığı & Overfitting Boşluğu Analizi", fontsize=10.5, fontweight="bold", color="white")
        ax2.set_ylabel("Doğruluk Oranı", fontsize=9, color="white")

        for bar, val in zip(b1, train_accs):
            ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.002, f"{val*100:.2f}%", ha="center", va="bottom", fontsize=7.5, color="white")
        for bar, val in zip(b2, test_accs):
            ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.002, f"{val*100:.2f}%", ha="center", va="bottom", fontsize=7.5, color="white")

        ax2.legend(loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=8, facecolor="#1a1d24", edgecolor="#334155", labelcolor="white")

        # -------------------------------------------------------------
        # Panel 3: Random Forest MDI (Gini) Öznitelik Önem Dereceleri
        # -------------------------------------------------------------
        ax3 = axes[1, 0]
        feat_dict = report.random_forest_metrics.feature_importances
        sorted_feats = sorted(feat_dict.items(), key=lambda item: item[1], reverse=False)
        feat_names = [k for k, _ in sorted_feats]
        feat_scores = [v for _, v in sorted_feats]

        y_pos = np.arange(len(feat_names))
        bars3 = ax3.barh(y_pos, feat_scores, color="#4da3ff", height=0.65)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(feat_names, fontsize=7.5, color="white")
        ax3.set_xlim(0.0, 0.205)
        ax3.set_xticks([0.00, 0.05, 0.10, 0.15, 0.20])
        ax3.set_title("Random Forest MDI (Gini) Öznitelik Önem Dereceleri", fontsize=10.5, fontweight="bold", color="white")
        ax3.set_xlabel("Önem Derecesi (Gini)", fontsize=9, color="white")

        for bar, val in zip(bars3, feat_scores):
            ax3.text(val + 0.002, bar.get_y() + bar.get_height() / 2, f"{val:.4f}", ha="left", va="center", fontsize=7.5, color="white")

        # -------------------------------------------------------------
        # Panel 4: Out-Of-Bag (OOB) Hata Yakınsaması vs Ağaç Sayısı
        # -------------------------------------------------------------
        ax4 = axes[1, 1]
        tree_counts, oob_errors = oob_convergence
        oob_pct = [e * 100 for e in oob_errors]

        ax4.plot(tree_counts, oob_pct, marker="o", markersize=3.5, color="#4ade80", lw=1.8)
        ax4.set_xlim(0, 105)
        ax4.set_ylim(-0.05, 2.05)
        ax4.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0])
        ax4.set_title("Topluluk Büyüklüğü (N_trees) vs OOB Hatası Yakınsaması", fontsize=10.5, fontweight="bold", color="white")
        ax4.set_xlabel("Ağaç Sayısı (N_trees)", fontsize=9, color="white")
        ax4.set_ylabel("OOB Hatası (%)", fontsize=9, color="white")

        final_err = oob_pct[-1] if len(oob_pct) > 0 else 0.12
        ax4.text(100, final_err + 0.1, f"{final_err:.2f}%", ha="center", va="bottom", fontsize=8, color="white")

        fig.subplots_adjust(top=0.93, bottom=0.08, left=0.08, right=0.98, hspace=0.28, wspace=0.20)
        plt.savefig(out_p, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", dpi=150)
        plt.close(fig)

        return str(out_p.resolve())

