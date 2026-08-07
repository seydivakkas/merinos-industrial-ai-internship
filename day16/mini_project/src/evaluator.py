"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
İkili Sınıflandırma Metrikleri, ROC-AUC, PR-AUC ve Eşik Optimizasyon Motoru

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

from .models import (
    BinaryClassificationReport,
    ConfusionMatrixMetrics,
    FeatureWeight,
    ModelEvaluationSummary,
    ROCAUCMetrics,
    ThresholdEvaluation,
)


class ClassificationEvaluator:
    """Karar matrisi, eğri altı alanları ve endüstriyel eşik optimizasyon motoru."""

    def __init__(self, cost_fn: float = 10.0, cost_fp: float = 1.0):
        self.cost_fn = cost_fn
        self.cost_fp = cost_fp

    def compute_confusion_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Tuple[ConfusionMatrixMetrics, float]:
        """
        Verilen gerçek ve tahmin dizilerinden karar matrisi bileşenlerini ve türetilmiş metrikleri hesaplar.
        """
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        total = len(y_true)
        accuracy = float((tp + tn) / total) if total > 0 else 0.0
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

        if precision + recall > 0:
            f1 = float(2 * precision * recall / (precision + recall))
            f2 = float(5 * precision * recall / (4 * precision + recall))
        else:
            f1 = 0.0
            f2 = 0.0

        cost = float(self.cost_fn * fn + self.cost_fp * fp)

        metrics = ConfusionMatrixMetrics(
            tp=int(tp),
            fp=int(fp),
            tn=int(tn),
            fn=int(fn),
            accuracy=round(accuracy, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            specificity=round(specificity, 4),
            f1_score=round(f1, 4),
            f2_score=round(f2, 4),
        )
        return metrics, cost

    def sweep_thresholds(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        num_points: int = 99,
    ) -> Tuple[List[ThresholdEvaluation], float, float, float]:
        """
        [0.01, 0.99] aralığında karar eşiklerini tarayarak Youden's J, F2 ve Maliyet optimizasyonunu yapar.
        
        Returns:
            evaluations, opt_thresh_youden, opt_thresh_f2, opt_thresh_cost
        """
        thresholds = np.linspace(0.01, 0.99, num_points)
        evaluations: List[ThresholdEvaluation] = []

        best_j = -1.0
        opt_thresh_youden = 0.50

        best_f2 = -1.0
        opt_thresh_f2 = 0.50

        min_cost = float("inf")
        opt_thresh_cost = 0.50

        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)
            metrics, cost = self.compute_confusion_metrics(y_true, y_pred)

            fpr = round(1.0 - metrics.specificity, 4)
            tpr = metrics.recall

            # Youden's J = TPR - FPR
            youden_j = tpr - fpr
            if youden_j > best_j:
                best_j = youden_j
                opt_thresh_youden = float(t)

            # F2 Score
            if metrics.f2_score > best_f2:
                best_f2 = metrics.f2_score
                opt_thresh_f2 = float(t)

            # Cost
            if cost < min_cost:
                min_cost = cost
                opt_thresh_cost = float(t)

            evaluations.append(
                ThresholdEvaluation(
                    threshold=round(float(t), 4),
                    precision=metrics.precision,
                    recall=metrics.recall,
                    specificity=metrics.specificity,
                    f1_score=metrics.f1_score,
                    f2_score=metrics.f2_score,
                    fpr=fpr,
                    tpr=tpr,
                    cost=round(cost, 2),
                )
            )

        return evaluations, round(opt_thresh_youden, 4), round(opt_thresh_f2, 4), round(opt_thresh_cost, 4)

    def evaluate_probabilities(
        self, y_true: np.ndarray, y_prob: np.ndarray
    ) -> Tuple[ROCAUCMetrics, List[ThresholdEvaluation], Dict[str, np.ndarray]]:
        """
        Kusurlu sınıf olasılıkları (P(Y=1|x)) üzerinden ROC, PR ve kalibrasyon analizini yapar.
        """
        roc_auc = float(roc_auc_score(y_true, y_prob))
        pr_auc = float(average_precision_score(y_true, y_prob))
        brier = float(brier_score_loss(y_true, y_prob))

        evals, opt_youden, opt_f2, opt_cost = self.sweep_thresholds(y_true, y_prob)

        roc_metrics = ROCAUCMetrics(
            roc_auc=round(roc_auc, 4),
            pr_auc=round(pr_auc, 4),
            brier_score=round(brier, 4),
            optimal_threshold_youden=opt_youden,
            optimal_threshold_f2=opt_f2,
            optimal_threshold_cost=opt_cost,
        )

        # Eğri koordinatları
        fpr_arr, tpr_arr, roc_thresh = roc_curve(y_true, y_prob)
        prec_arr, rec_arr, pr_thresh = precision_recall_curve(y_true, y_prob)

        curve_data = {
            "fpr": fpr_arr,
            "tpr": tpr_arr,
            "roc_thresholds": roc_thresh,
            "precision": prec_arr,
            "recall": rec_arr,
            "pr_thresholds": pr_thresh,
        }

        return roc_metrics, evals, curve_data

    def generate_master_report(
        self,
        y_true: np.ndarray,
        baseline_probs: np.ndarray,
        balanced_probs: np.ndarray,
        feature_weights: List[FeatureWeight],
    ) -> BinaryClassificationReport:
        """
        Tüm model varyantlarını (Temel, Dengeli, Optimal Eşikli) karşılaştıran master raporu üretir.
        """
        total_samples = len(y_true)
        defect_count = int(np.sum(y_true))
        defect_ratio = round(defect_count / total_samples, 4)

        roc_metrics, _, _ = self.evaluate_probabilities(y_true, baseline_probs)

        # 1. Baseline Model (tau = 0.50)
        base_pred = (baseline_probs >= 0.50).astype(int)
        base_metrics, base_cost = self.compute_confusion_metrics(y_true, base_pred)
        baseline_summary = ModelEvaluationSummary(
            model_type="Baseline (Standard Weights, tau=0.50)",
            threshold=0.50,
            metrics=base_metrics,
            cost=round(base_cost, 2),
        )

        # 2. Balanced Model (tau = 0.50)
        bal_pred = (balanced_probs >= 0.50).astype(int)
        bal_metrics, bal_cost = self.compute_confusion_metrics(y_true, bal_pred)
        balanced_summary = ModelEvaluationSummary(
            model_type="Balanced Class Weights (class_weight='balanced', tau=0.50)",
            threshold=0.50,
            metrics=bal_metrics,
            cost=round(bal_cost, 2),
        )

        # 3. Tuned Threshold Model (Maliyet Optimizasyonu Eşiği)
        opt_thresh = roc_metrics.optimal_threshold_cost
        tuned_pred = (baseline_probs >= opt_thresh).astype(int)
        tuned_metrics, tuned_cost = self.compute_confusion_metrics(y_true, tuned_pred)
        tuned_summary = ModelEvaluationSummary(
            model_type=f"Cost-Sensitive Tuned Threshold (tau={opt_thresh:.2f})",
            threshold=opt_thresh,
            metrics=tuned_metrics,
            cost=round(tuned_cost, 2),
        )

        return BinaryClassificationReport(
            dataset_samples=total_samples,
            defect_count=defect_count,
            defect_ratio=defect_ratio,
            roc_auc_metrics=roc_metrics,
            baseline_model=baseline_summary,
            balanced_model=balanced_summary,
            tuned_threshold_model=tuned_summary,
            feature_weights=feature_weights,
        )
