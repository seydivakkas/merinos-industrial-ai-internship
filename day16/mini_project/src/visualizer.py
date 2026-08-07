"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
İkili Sınıflandırma Görselleştirme ve Teşhis Paneli Motoru

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .models import BinaryClassificationReport, ThresholdEvaluation


class ClassificationVisualizer:
    """Endüstriyel 2x2 model teşhis ve değerlendirme paneli oluşturucu."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid"):
        try:
            plt.style.use(style)
        except Exception:
            plt.style.use("default")

    def plot_diagnostic_panel(
        self,
        report: BinaryClassificationReport,
        curve_data: Dict[str, np.ndarray],
        evaluations: List[ThresholdEvaluation],
        output_path: str,
    ) -> str:
        """
        2x2 düzeninde kapsamlı endüstriyel teşhis paneli oluşturur ve kaydeder.

        Paneller:
            1. ROC Eğrisi (ROC Curve)
            2. Precision-Recall Eğrisi (PR Curve)
            3. Karar Matrisi Isı Haritası (Confusion Matrix at Threshold = 0.5)
            4. Eşik Değişimi Metrik Karşılaştırması (Threshold Sweep: Precision, Recall, F1-score, Youden J)
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=150)
        fig.suptitle(
            "Logistic Regression - Classification Diagnostic Panel (Day 16)",
            fontsize=13,
            fontweight="bold",
            y=0.98,
        )

        # -------------------------------------------------------------
        # Panel 1: ROC Curve
        # -------------------------------------------------------------
        ax1 = axes[0, 0]
        fpr = curve_data["fpr"]
        tpr = curve_data["tpr"]
        roc_auc = report.roc_auc_metrics.roc_auc

        ax1.plot(fpr, tpr, color="#1f77b4", lw=2.0, label=f"ROC curve (AUC = {roc_auc:.4f})")
        ax1.plot([0, 1], [0, 1], color="gray", lw=1.2, linestyle="--")

        ax1.set_title(f"ROC Curve (AUC = {roc_auc:.4f})", fontsize=11, fontweight="bold")
        ax1.set_xlabel("False Positive Rate", fontsize=9)
        ax1.set_ylabel("True Positive Rate", fontsize=9)
        ax1.set_xlim([-0.02, 1.02])
        ax1.set_ylim([-0.02, 1.02])
        ax1.legend(loc="lower right", fontsize=8)
        ax1.grid(True, alpha=0.3)

        # -------------------------------------------------------------
        # Panel 2: Precision-Recall Curve
        # -------------------------------------------------------------
        ax2 = axes[0, 1]
        prec = curve_data["precision"]
        rec = curve_data["recall"]
        pr_auc = report.roc_auc_metrics.pr_auc

        ax2.plot(rec, prec, color="#2ca02c", lw=2.0, label=f"PR curve (AUC = {pr_auc:.4f})")

        ax2.set_title(f"Precision-Recall Curve (AUC = {pr_auc:.4f})", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Recall", fontsize=9)
        ax2.set_ylabel("Precision", fontsize=9)
        ax2.set_xlim([-0.02, 1.02])
        ax2.set_ylim([-0.02, 1.05])
        ax2.legend(loc="lower right", fontsize=8)
        ax2.grid(True, alpha=0.3)

        # -------------------------------------------------------------
        # Panel 3: Confusion Matrix Heatmap
        # -------------------------------------------------------------
        ax3 = axes[1, 0]
        base_m = report.baseline_model.metrics
        cm = np.array([[base_m.tn, base_m.fp], [base_m.fn, base_m.tp]])

        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=True,
            ax=ax3,
            annot_kws={"size": 11, "weight": "bold"},
        )
        ax3.set_title(f"Confusion Matrix (Threshold = {report.baseline_model.threshold:.1f})", fontsize=11, fontweight="bold")
        ax3.set_xlabel("Predicted Label", fontsize=9)
        ax3.set_ylabel("True Label", fontsize=9)
        ax3.set_xticklabels([0, 1])
        ax3.set_yticklabels([0, 1])

        # -------------------------------------------------------------
        # Panel 4: Threshold Sweep - Metrics Comparison
        # -------------------------------------------------------------
        ax4 = axes[1, 1]
        t_vals = [e.threshold for e in evaluations]
        p_vals = [e.precision for e in evaluations]
        r_vals = [e.recall for e in evaluations]
        f1_vals = [e.f1_score for e in evaluations]
        yj_vals = [e.tpr - e.fpr for e in evaluations]

        ax4.plot(t_vals, p_vals, color="#ff7f0e", lw=1.8, linestyle=":", label="Precision")
        ax4.plot(t_vals, r_vals, color="#2ca02c", lw=1.8, label="Recall")
        ax4.plot(t_vals, f1_vals, color="#1f77b4", lw=1.8, linestyle="--", label="F1-score")
        ax4.plot(t_vals, yj_vals, color="#d62728", lw=1.8, linestyle="-.", label="Youden J")

        ax4.axvline(x=0.50, color="gray", linestyle="--", lw=1.0)
        ax4.set_title("Threshold Sweep - Metrics Comparison", fontsize=11, fontweight="bold")
        ax4.set_xlabel("Threshold", fontsize=9)
        ax4.set_ylabel("Score", fontsize=9)
        ax4.set_xlim([0.0, 1.0])
        ax4.set_ylim([-0.02, 1.05])
        ax4.legend(loc="center right", fontsize=8)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(out_p, format="png", bbox_inches="tight")
        plt.close(fig)

        return str(out_p)
