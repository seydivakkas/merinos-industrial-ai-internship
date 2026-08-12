"""Evaluator and hyperparameter optimization engine for SVM defect classification."""

import numpy as np
from typing import List, Optional
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.svm import SVC

from day20.mini_project.src.models import (
    SVMKernelMetrics,
    SVMGridSearchRecord,
    SVMGridSearchResult,
    SVMComparisonReport
)
from day20.mini_project.src.svm_models import MerinosSVMClassifier


class SVMEvaluator:
    """Evaluates SVM kernel variants and optimizes C / gamma regularization parameters."""

    @staticmethod
    def evaluate_model(
        model: MerinosSVMClassifier,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> SVMKernelMetrics:
        """Evaluates an SVM classifier computing accuracy, F1, Kappa, latency, and SV metrics."""
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_acc = float(accuracy_score(y_train, y_train_pred))
        test_acc = float(accuracy_score(y_test, y_test_pred))
        macro_f1 = float(f1_score(y_test, y_test_pred, average="macro"))
        weighted_f1 = float(f1_score(y_test, y_test_pred, average="weighted"))
        kappa = float(cohen_kappa_score(y_test, y_test_pred))

        sv_metrics = model.get_support_vector_metrics()
        latency_ms, throughput_fps = model.benchmark_latency(X_test, n_runs=200)

        return SVMKernelMetrics(
            kernel_name=model.kernel,
            train_accuracy=round(train_acc, 4),
            test_accuracy=round(test_acc, 4),
            macro_f1=round(macro_f1, 4),
            weighted_f1=round(weighted_f1, 4),
            cohen_kappa=round(kappa, 4),
            support_vectors=sv_metrics,
            training_time_ms=round(model.training_time_ms, 2),
            single_sample_latency_ms=round(latency_ms, 4),
            throughput_fps=round(throughput_fps, 1)
        )

    @staticmethod
    def tune_hyperparameters(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        C_values: Optional[List[float]] = None,
        gamma_values: Optional[List[float]] = None,
        cv_folds: int = 3
    ) -> SVMGridSearchResult:
        """Performs grid search across C and gamma hyperparameters for RBF kernel."""
        if C_values is None:
            C_values = [0.1, 1.0, 10.0, 100.0]
        if gamma_values is None:
            gamma_values = [0.001, 0.01, 0.1, 1.0]

        records: List[SVMGridSearchRecord] = []
        best_score = -1.0
        best_C = C_values[0]
        best_gamma = gamma_values[0]

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)

        for c in C_values:
            for g in gamma_values:
                svc = SVC(kernel="rbf", C=c, gamma=g, random_state=42)
                cv_scores = cross_val_score(svc, X_train, y_train, cv=cv, scoring="accuracy")
                mean_cv = float(np.mean(cv_scores))

                # Test değerlendirmesi
                svc.fit(X_train, y_train)
                test_acc = float(svc.score(X_test, y_test))
                n_sv = int(np.sum(svc.n_support_))

                records.append(
                    SVMGridSearchRecord(
                        C=c,
                        gamma=g,
                        mean_cv_accuracy=round(mean_cv, 4),
                        test_accuracy=round(test_acc, 4),
                        n_support_vectors=n_sv
                    )
                )

                if mean_cv > best_score:
                    best_score = mean_cv
                    best_C = c
                    best_gamma = g

        return SVMGridSearchResult(
            best_C=best_C,
            best_gamma=best_gamma,
            best_score=round(best_score, 4),
            grid_records=records
        )

    @staticmethod
    def generate_comparison_report(
        linear_model: MerinosSVMClassifier,
        poly_model: MerinosSVMClassifier,
        rbf_model: MerinosSVMClassifier,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        grid_result: Optional[SVMGridSearchResult] = None
    ) -> SVMComparisonReport:
        """Generates comprehensive comparative report across Linear, Polynomial, and RBF kernels."""
        lin_metrics = SVMEvaluator.evaluate_model(linear_model, X_train, y_train, X_test, y_test)
        poly_metrics = SVMEvaluator.evaluate_model(poly_model, X_train, y_train, X_test, y_test)
        rbf_metrics = SVMEvaluator.evaluate_model(rbf_model, X_train, y_train, X_test, y_test)

        # Winner selection
        models_map = {
            "Linear SVM": lin_metrics,
            "Polynomial SVM": poly_metrics,
            "RBF (Gaussian) SVM": rbf_metrics
        }
        winner = max(models_map.keys(), key=lambda k: (models_map[k].test_accuracy, models_map[k].macro_f1))

        # Speed comparison
        fastest_train = min(models_map.keys(), key=lambda k: models_map[k].training_time_ms)
        speedup_text = (
            f"{fastest_train} en hızlı eğitilen model oldu ({models_map[fastest_train].training_time_ms} ms). "
            f"RBF SVM çıkarım gecikmesi {rbf_metrics.single_sample_latency_ms} ms ({rbf_metrics.throughput_fps} FPS)."
        )

        return SVMComparisonReport(
            total_samples=len(X_train) + len(X_test),
            train_samples=len(X_train),
            test_samples=len(X_test),
            features_count=X_train.shape[1],
            linear_metrics=lin_metrics,
            polynomial_metrics=poly_metrics,
            rbf_metrics=rbf_metrics,
            winner_model=winner,
            speedup_summary=speedup_text,
            grid_search_result=grid_result
        )
