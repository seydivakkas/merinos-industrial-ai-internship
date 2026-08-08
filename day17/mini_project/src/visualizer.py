"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Model Teşhis ve Değerlendirme Paneli Görselleştiricisi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .models import MulticlassEvaluationReport


class MulticlassVisualizer:
    """Endüstriyel 2x2 çok sınıflı model teşhis ve kıyaslama paneli oluşturucu."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid"):
        try:
            plt.style.use(style)
        except Exception:
            plt.style.use("default")

    def plot_diagnostic_panel(
        self,
        report: MulticlassEvaluationReport,
        cm: np.ndarray,
        roc_curves: Dict[str, Dict[str, np.ndarray]],
        output_path: str,
    ) -> str:
        """
        2x2 düzeninde kurumsal çok sınıflı model teşhis panelini oluşturur ve kaydeder.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(15, 10), dpi=150)
        fig.suptitle(
            "Merinos Halı & İplik Kalite Kontrolü - Çok Sınıflı Kusur Sınıflandırma Teşhis Paneli",
            fontsize=13,
            fontweight="bold",
            y=0.98,
        )

        class_names = [p.class_name for p in report.multinomial_model.per_class]
        short_names = ["İPLİK KOP.", "YAĞ LEKESİ", "JAKAR KAY.", "DİKİŞ HAT."]
        full_names = ["İplik Kopması", "Yağ Lekesi", "Jakar Desen Kayması", "Kenar Dikiş Hatası"]

        # -------------------------------------------------------------
        # Panel 1: 4x4 Karar Matrisi (Confusion Matrix) Isı Haritası
        # -------------------------------------------------------------
        ax1 = axes[0, 0]
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        cm_norm = np.nan_to_num(cm_norm)

        annot_matrix = np.empty_like(cm, dtype=object)
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                annot_matrix[i, j] = f"{cm[i, j]}\n(%{cm_norm[i, j]*100:.1f})"

        sns.heatmap(
            cm,
            annot=annot_matrix,
            fmt="",
            cmap="Blues",
            cbar=True,
            ax=ax1,
            xticklabels=short_names,
            yticklabels=short_names,
            annot_kws={"size": 8.5},
        )
        ax1.set_title("1. Karar Matrisi (4x4)", fontsize=11, fontweight="bold")
        ax1.set_xlabel("Tahmin Edilen Sınıf", fontsize=9)
        ax1.set_ylabel("Gerçek Kusur Sınıfı", fontsize=9)

        # -------------------------------------------------------------
        # Panel 2: Sınıf Bazlı Precision, Recall ve F1 Skorları
        # -------------------------------------------------------------
        ax2 = axes[0, 1]
        per_class = report.multinomial_model.per_class
        x = np.arange(len(class_names))
        width = 0.22

        precisions = [p.precision for p in per_class]
        recalls = [p.recall for p in per_class]
        f1s = [p.f1_score for p in per_class]

        b1 = ax2.bar(x - width, precisions, width, label="Precision", color="#1f77b4")
        b2 = ax2.bar(x, recalls, width, label="Recall", color="#2ca02c")
        b3 = ax2.bar(x + width, f1s, width, label="F1-Skoru", color="#ff7f0e")

        # Metin etiketleri
        for bars in [b1, b2, b3]:
            for bar in bars:
                height = bar.get_height()
                ax2.annotate(
                    f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                )

        ax2.set_xticks(x)
        ax2.set_xticklabels(short_names, fontsize=8.5)
        ax2.set_ylim([0.0, 1.15])
        ax2.set_title("2. Sınıf Bazlı Başarım Metrikleri (Softmax)", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Skor", fontsize=9)
        ax2.legend(loc="upper right", fontsize=8, ncol=3)
        ax2.grid(True, alpha=0.3)

        # -------------------------------------------------------------
        # Panel 3: 4 Sınıflı One-vs-Rest ROC Eğrileri
        # -------------------------------------------------------------
        ax3 = axes[1, 0]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        for idx, (cname, data) in enumerate(roc_curves.items()):
            label_text = f"{full_names[idx % len(full_names)]} (AUC = {data['auc']:.4f})"
            ax3.plot(data["fpr"], data["tpr"], lw=1.8, color=colors[idx % len(colors)], label=label_text)

        ax3.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1.2, label="Rastgele Tahmin (AUC = 0.5000)")
        macro_auc = report.multinomial_model.metrics.roc_auc_ovr_macro
        ax3.set_title(f"3. Çok Sınıflı OvR ROC Eğrileri (Makro AUC = {macro_auc:.4f})", fontsize=11, fontweight="bold")
        ax3.set_xlabel("False Positive Rate", fontsize=9)
        ax3.set_ylabel("True Positive Rate", fontsize=9)
        ax3.set_xlim([-0.02, 1.02])
        ax3.set_ylim([-0.02, 1.05])
        ax3.legend(loc="lower right", fontsize=8)
        ax3.grid(True, alpha=0.3)

        # -------------------------------------------------------------
        # Panel 4: Mimari Kıyaslama (Multinomial vs OvR) Tablosu
        # -------------------------------------------------------------
        ax4 = axes[1, 1]
        ax4.axis("off")
        ax4.set_title("4. Mimari Kıyaslama: Softmax vs One-vs-Rest", fontsize=11, fontweight="bold")

        m_multi = report.multinomial_model
        m_ovr = report.ovr_model

        table_data = [
            ["Accuracy", f"%{m_multi.metrics.accuracy*100:.1f}", f"%{m_ovr.metrics.accuracy*100:.1f}"],
            ["Macro F1", f"{m_multi.metrics.macro_f1:.4f}", f"{m_ovr.metrics.macro_f1:.4f}"],
            ["Weighted F1", f"{m_multi.metrics.weighted_f1:.4f}", f"{m_ovr.metrics.weighted_f1:.4f}"],
            ["Cohen's Kappa", f"{m_multi.metrics.cohen_kappa:.4f}", f"{m_ovr.metrics.cohen_kappa:.4f}"],
            ["Log-Loss", f"{m_multi.metrics.log_loss:.4f}", f"{m_ovr.metrics.log_loss:.4f}"],
            ["Eğitim Süresi", f"{m_multi.training_time_ms:.2f} ms", f"{m_ovr.training_time_ms:.2f} ms"],
            ["Tahmin Süresi (1 örnek)", f"{m_multi.inference_latency_ms:.4f} ms", f"{m_ovr.inference_latency_ms:.4f} ms"],
        ]
        col_labels = ["Metrik", "Softmax\n(Multinomial)", "One-vs-Rest\n(OvR)"]

        tbl = ax4.table(
            cellText=table_data,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9.0)
        tbl.scale(1.0, 1.5)

        # Tablo başlık stili
        for col_idx in range(len(col_labels)):
            cell = tbl[(0, col_idx)]
            cell.set_facecolor("#e9ecef")
            cell.set_text_props(weight="bold")

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(out_p, format="png", bbox_inches="tight")
        plt.close(fig)

        return str(out_p)
