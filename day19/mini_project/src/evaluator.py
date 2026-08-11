"""
Merinos Industrial AI Internship - Day 19
Evaluation, Benchmark & Hyperparameter Tuning Engine for Gradient Boosting
"""

from datetime import datetime, timezone
import json
import os
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, log_loss

from day19.mini_project.src.models import (
    BoostingModelMetrics,
    HyperparameterTuningRecord,
    HyperparameterTuningResult,
    BoostingComparisonReport
)
from day19.mini_project.src.boosting_models import (
    MerinosXGBoostClassifier,
    MerinosLightGBMClassifier
)


class BoostingEvaluator:
    """Computes comprehensive classification metrics, early stopping analysis, and tuning."""

    @staticmethod
    def evaluate_model(
        model: Any,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> BoostingModelMetrics:
        """Evaluates model performance across train, validation and unseen test sets."""
        y_pred_test = model.predict(X_test)
        probs_test = model.predict_proba(X_test)
        probs_train = model.predict_proba(X_train)
        probs_val = model.predict_proba(X_val)

        acc = float(accuracy_score(y_test, y_pred_test))
        macro_f1 = float(f1_score(y_test, y_pred_test, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_test, y_pred_test, average="weighted", zero_division=0))
        kappa = float(cohen_kappa_score(y_test, y_pred_test))

        train_loss = float(log_loss(y_train, probs_train))
        val_loss = float(log_loss(y_val, probs_val))

        es_res = model.get_early_stopping_result()
        latency_ms, throughput_fps = model.benchmark_latency(X_test)

        return BoostingModelMetrics(
            accuracy=round(acc, 4),
            macro_f1=round(macro_f1, 4),
            weighted_f1=round(weighted_f1, 4),
            cohen_kappa=round(kappa, 4),
            train_loss=round(train_loss, 4),
            val_loss=round(val_loss, 4),
            best_iteration=es_res.best_iteration,
            total_iterations=es_res.stopping_iteration,
            latency_ms=round(latency_ms, 4),
            throughput_fps=round(throughput_fps, 1),
            training_time_ms=round(model.training_time_ms, 2),
            early_stopping=es_res
        )

    @staticmethod
    def tune_hyperparameters(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        learning_rates: Optional[List[float]] = None,
        max_depths: Optional[List[int]] = None,
        model_type: str = "xgboost"
    ) -> HyperparameterTuningResult:
        """Performs grid evaluation over shrinkage (learning rate) and tree depth."""
        lrs = learning_rates or [0.03, 0.08, 0.15]
        depths = max_depths or [3, 4, 6]

        records: List[HyperparameterTuningRecord] = []
        best_val_acc = -1.0
        best_lr = lrs[0]
        best_depth = depths[0]

        for lr in lrs:
            for depth in depths:
                if model_type == "xgboost":
                    model = MerinosXGBoostClassifier(
                        learning_rate=lr,
                        max_depth=depth,
                        n_estimators=100,
                        early_stopping_rounds=10
                    )
                else:
                    model = MerinosLightGBMClassifier(
                        learning_rate=lr,
                        max_depth=depth,
                        n_estimators=100,
                        early_stopping_rounds=10
                    )

                model.fit(X_train, y_train, X_val, y_val)
                val_acc = float(accuracy_score(y_val, model.predict(X_val)))
                test_acc = float(accuracy_score(y_test, model.predict(X_test)))
                es = model.get_early_stopping_result()

                rec = HyperparameterTuningRecord(
                    learning_rate=lr,
                    max_depth=depth,
                    val_accuracy=round(val_acc, 4),
                    test_accuracy=round(test_acc, 4),
                    best_iteration=es.best_iteration,
                    train_time_ms=round(model.training_time_ms, 2)
                )
                records.append(rec)

                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_lr = lr
                    best_depth = depth

        return HyperparameterTuningResult(
            best_learning_rate=best_lr,
            best_max_depth=best_depth,
            best_accuracy=round(best_val_acc, 4),
            records=records
        )

    @staticmethod
    def generate_report(
        xgb_model: MerinosXGBoostClassifier,
        lgb_model: MerinosLightGBMClassifier,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str],
        baseline_rf_accuracy: float = 0.9967
    ) -> BoostingComparisonReport:
        """Generates comprehensive Master Benchmark Report."""
        xgb_metrics = BoostingEvaluator.evaluate_model(
            xgb_model, X_train, y_train, X_val, y_val, X_test, y_test
        )
        lgb_metrics = BoostingEvaluator.evaluate_model(
            lgb_model, X_train, y_train, X_val, y_val, X_test, y_test
        )

        importances_xgb = xgb_model.get_feature_importances(feature_names)
        importances_lgb = lgb_model.get_feature_importances(feature_names)

        # Calculate LightGBM speedup over XGBoost
        speedup = (
            round(xgb_metrics.training_time_ms / lgb_metrics.training_time_ms, 2)
            if lgb_metrics.training_time_ms > 0 else 1.0
        )

        # Select champion model
        if lgb_metrics.accuracy > xgb_metrics.accuracy:
            champion = "LightGBM Classifier"
        elif xgb_metrics.accuracy > lgb_metrics.accuracy:
            champion = "XGBoost Classifier"
        else:
            # Tie breaker: lowest validation loss or highest throughput
            champion = "LightGBM Classifier" if lgb_metrics.throughput_fps > xgb_metrics.throughput_fps else "XGBoost Classifier"

        recommendations = [
            f"Champion Model: {champion} reached top test accuracy of {max(xgb_metrics.accuracy, lgb_metrics.accuracy)*100:.2f}%.",
            f"Early Stopping Benefit: Prevented overfitting by halting at iteration {xgb_metrics.best_iteration} (XGBoost) and {lgb_metrics.best_iteration} (LightGBM).",
            f"Throughput Comparison: LightGBM delivered {lgb_metrics.throughput_fps:,.0f} FPS ({lgb_metrics.latency_ms:.4f} ms) vs XGBoost {xgb_metrics.throughput_fps:,.0f} FPS ({xgb_metrics.latency_ms:.4f} ms).",
            f"Training Speedup: LightGBM completed fitting {speedup}x faster than XGBoost on industrial telemetry.",
            f"Top Telemetry Driver: '{max(importances_xgb, key=importances_xgb.get)}' holds highest Gain in XGBoost ({max(importances_xgb.values()):.4f})."
        ]

        return BoostingComparisonReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            n_train=len(X_train),
            n_val=len(X_val),
            n_test=len(X_test),
            xgboost=xgb_metrics,
            lightgbm=lgb_metrics,
            baseline_rf_accuracy=baseline_rf_accuracy,
            feature_importances_xgb=importances_xgb,
            feature_importances_lgb=importances_lgb,
            champion_model=champion,
            speedup_factor=speedup,
            recommendations=recommendations
        )

    @staticmethod
    def save_report_to_json(report: BoostingComparisonReport, filepath: str) -> str:
        """Serializes and saves report as JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
        return filepath


BoostingEvaluator.generate_comparison_report = BoostingEvaluator.generate_report
BoostingModelEvaluator = BoostingEvaluator
