"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Model Değerlendirme, Karar Matrisi ve ROC-AUC Analiz Motoru

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from .models import (
    DefectClass,
    ModelComparisonSummary,
    MulticlassEvaluationReport,
    MulticlassMetrics,
    PerClassMetrics,
)
from .multiclass_classifier import MerinosMulticlassClassifier


class MulticlassEvaluator:
    """Çok sınıflı sınıflandırma metrikleri ve mimari kıyaslama motoru."""

    def __init__(self, class_names: Optional[List[str]] = None):
        self.class_names = class_names or [e.name for e in DefectClass]
        self.n_classes = len(self.class_names)

    def compute_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """4x4 Karar Matrisini (Confusion Matrix) hesaplar."""
        return confusion_matrix(y_true, y_pred, labels=list(range(self.n_classes)))

    def compute_per_class_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> List[PerClassMetrics]:
        """Her 4 kusur sınıfı için TP, FP, FN, Precision, Recall ve F1-Skorunu hesaplar."""
        cm = self.compute_confusion_matrix(y_true, y_pred)
        results: List[PerClassMetrics] = []

        for k in range(self.n_classes):
            tp = int(cm[k, k])
            fp = int(np.sum(cm[:, k]) - tp)
            fn = int(np.sum(cm[k, :]) - tp)
            support = int(np.sum(cm[k, :]))

            prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

            results.append(
                PerClassMetrics(
                    class_id=k,
                    class_name=self.class_names[k],
                    tp=tp,
                    fp=fp,
                    fn=fn,
                    precision=round(prec, 4),
                    recall=round(rec, 4),
                    f1_score=round(f1, 4),
                    support=support,
                )
            )

        return results

    def compute_global_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray, y_probs: np.ndarray
    ) -> MulticlassMetrics:
        """Makro, Mikro, Ağırlıklı F1, Kappa ve OvR ROC-AUC metriklerini hesaplar."""
        acc = float(accuracy_score(y_true, y_pred))
        macro_p = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
        macro_r = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
        macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        micro_f1 = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
        weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
        kappa = float(cohen_kappa_score(y_true, y_pred))
        ce_loss = float(log_loss(y_true, y_probs, labels=list(range(self.n_classes))))

        try:
            roc_auc_ovr = float(
                roc_auc_score(
                    y_true,
                    y_probs,
                    multi_class="ovr",
                    average="macro",
                    labels=list(range(self.n_classes)),
                )
            )
        except Exception:
            roc_auc_ovr = 1.0

        return MulticlassMetrics(
            accuracy=round(acc, 4),
            macro_precision=round(macro_p, 4),
            macro_recall=round(macro_r, 4),
            macro_f1=round(macro_f1, 4),
            micro_f1=round(micro_f1, 4),
            weighted_f1=round(weighted_f1, 4),
            cohen_kappa=round(kappa, 4),
            log_loss=round(ce_loss, 4),
            roc_auc_ovr_macro=round(roc_auc_ovr, 4),
        )

    def evaluate_model(
        self, clf: MerinosMulticlassClassifier, X_test: np.ndarray, y_test: np.ndarray
    ) -> ModelComparisonSummary:
        """Belirtilen modeli test verisi üzerinde tam kapsamlı değerlendirir ve hız profilini çıkarır."""
        y_pred = clf.predict(X_test)
        y_probs = clf.predict_proba(X_test)

        per_class = self.compute_per_class_metrics(y_test, y_pred)
        metrics = self.compute_global_metrics(y_test, y_pred, y_probs)
        latency_ms, throughput_fps = clf.measure_inference_speed(X_test)

        strategy_label = (
            "Softmax Multinomial Lojistik Regresyon"
            if clf.strategy == "multinomial"
            else "One-vs-Rest (OvR) Lojistik Regresyon"
        )

        return ModelComparisonSummary(
            strategy_name=strategy_label,
            training_time_ms=clf.training_time_ms,
            inference_latency_ms=latency_ms,
            throughput_fps=throughput_fps,
            metrics=metrics,
            per_class=per_class,
        )

    def get_ovr_roc_curves(
        self, y_true: np.ndarray, y_probs: np.ndarray
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """Her sınıf için bağımsız One-vs-Rest ROC eğrisi koordinatlarını ve AUC değerlerini üretir."""
        curves = {}
        for k in range(self.n_classes):
            y_binary = (y_true == k).astype(int)
            prob_k = y_probs[:, k]
            fpr, tpr, thresholds = roc_curve(y_binary, prob_k)
            try:
                auc_val = float(roc_auc_score(y_binary, prob_k))
            except Exception:
                auc_val = 1.0

            curves[self.class_names[k]] = {
                "fpr": fpr,
                "tpr": tpr,
                "auc": round(auc_val, 4),
            }
        return curves

    def generate_master_report(
        self,
        multinomial_summary: ModelComparisonSummary,
        ovr_summary: ModelComparisonSummary,
        y_test: np.ndarray,
        feature_names: List[str],
        clf_multinomial: MerinosMulticlassClassifier,
    ) -> MulticlassEvaluationReport:
        """Her iki mimariyi kıyaslayan kurumsal master raporunu üretir."""
        unique_cls, counts = np.unique(y_test, return_counts=True)
        dist = {self.class_names[c]: int(cnt) for c, cnt in zip(unique_cls, counts)}

        feature_importance = clf_multinomial.get_feature_importance(feature_names)

        return MulticlassEvaluationReport(
            dataset_samples=len(y_test),
            class_distribution=dist,
            multinomial_model=multinomial_summary,
            ovr_model=ovr_summary,
            feature_importance=feature_importance,
        )
