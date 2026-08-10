"""
Merinos Industrial AI Internship - Day 18
Evaluation Engine for Decision Tree, Cost-Complexity Pruning & Random Forest
"""

from datetime import datetime, timezone
import json
import os
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

from day18.mini_project.src.models import (
    ModelEvaluationMetrics,
    TreeComplexityMetrics,
    PruningPathResult,
    RandomForestMetrics,
    EnsembleComparisonReport
)
from day18.mini_project.src.tree_models import (
    MerinosDecisionTreeClassifier,
    MerinosRandomForestClassifier
)


class TreeEnsembleEvaluator:
    """Computes comprehensive classification, overfitting, and complexity diagnostics."""

    @staticmethod
    def evaluate_model(
        model: Any,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> ModelEvaluationMetrics:
        """Evaluates model performance and measures the train-test generalization gap."""
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        train_acc = float(accuracy_score(y_train, y_pred_train))
        test_acc = float(accuracy_score(y_test, y_pred_test))
        overfitting_gap = float(train_acc - test_acc)

        macro_f1 = float(f1_score(y_test, y_pred_test, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_test, y_pred_test, average="weighted", zero_division=0))
        kappa = float(cohen_kappa_score(y_test, y_pred_test))

        latency_ms, throughput_fps = model.benchmark_latency(X_test)

        return ModelEvaluationMetrics(
            accuracy=round(test_acc, 4),
            macro_f1=round(macro_f1, 4),
            weighted_f1=round(weighted_f1, 4),
            cohen_kappa=round(kappa, 4),
            train_accuracy=round(train_acc, 4),
            test_accuracy=round(test_acc, 4),
            overfitting_gap=round(overfitting_gap, 4),
            latency_ms=round(latency_ms, 4),
            throughput_fps=round(throughput_fps, 1)
        )

    @staticmethod
    def compare_criteria(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        random_state: int = 42
    ) -> Dict[str, Dict[str, float]]:
        """Compares tree performance between Gini Impurity and Shannon Entropy."""
        results = {}
        for criterion in ["gini", "entropy"]:
            tree = DecisionTreeClassifier(criterion=criterion, random_state=random_state)
            tree.fit(X_train, y_train)

            train_acc = float(accuracy_score(y_train, tree.predict(X_train)))
            test_acc = float(accuracy_score(y_test, tree.predict(X_test)))
            leaves = int(tree.get_n_leaves())
            depth = int(tree.get_depth())

            results[criterion] = {
                "train_accuracy": round(train_acc, 4),
                "test_accuracy": round(test_acc, 4),
                "overfitting_gap": round(train_acc - test_acc, 4),
                "leaf_count": float(leaves),
                "depth": float(depth)
            }
        return results

    @staticmethod
    def generate_report(
        unpruned_tree: MerinosDecisionTreeClassifier,
        pruned_tree: MerinosDecisionTreeClassifier,
        random_forest: MerinosRandomForestClassifier,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str]
    ) -> EnsembleComparisonReport:
        """Generates the master benchmark comparison report."""
        unpruned_metrics = TreeEnsembleEvaluator.evaluate_model(
            unpruned_tree, X_train, y_train, X_test, y_test
        )
        unpruned_complexity = unpruned_tree.get_complexity()

        pruned_metrics = TreeEnsembleEvaluator.evaluate_model(
            pruned_tree, X_train, y_train, X_test, y_test
        )
        pruned_complexity = pruned_tree.get_complexity()

        rf_metrics = TreeEnsembleEvaluator.evaluate_model(
            random_forest, X_train, y_train, X_test, y_test
        )
        oob_score, oob_error = random_forest.get_oob_metrics()
        importances = random_forest.get_feature_importances(feature_names)

        rf_ensemble_metrics = RandomForestMetrics(
            oob_score=round(oob_score, 4),
            oob_error=round(oob_error, 4),
            n_estimators=random_forest.n_estimators,
            max_features=random_forest.max_features,
            feature_importances=importances
        )

        criteria_comp = TreeEnsembleEvaluator.compare_criteria(
            X_train, y_train, X_test, y_test
        )

        # Champion model selection
        best_model = "Random Forest Ensemble"
        if rf_metrics.test_accuracy >= pruned_metrics.test_accuracy:
            best_model = "Random Forest Ensemble"
        else:
            best_model = "Cost-Complexity Pruned Decision Tree"

        recommendations = [
            f"Model Champion: {best_model} achieved highest generalization with test accuracy {rf_metrics.test_accuracy * 100:.2f}%.",
            f"Overfitting Mitigation: Pruning reduced leaf count from {unpruned_complexity.leaf_count} to {pruned_complexity.leaf_count} ({((unpruned_complexity.leaf_count - pruned_complexity.leaf_count) / unpruned_complexity.leaf_count) * 100:.1f}% reduction).",
            f"Top Telemetry Driver: '{max(importances, key=importances.get)}' holds highest MDI importance ({max(importances.values()):.4f}).",
            f"Ensemble Stability: 100 trees achieved OOB score of {oob_score * 100:.2f}% without separate validation set."
        ]

        return EnsembleComparisonReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            n_samples=len(X_train) + len(X_test),
            test_samples=len(X_test),
            unpruned_tree=unpruned_metrics,
            unpruned_complexity=unpruned_complexity,
            pruned_tree=pruned_metrics,
            pruned_complexity=pruned_complexity,
            random_forest=rf_metrics,
            random_forest_metrics=rf_ensemble_metrics,
            criterion_comparison=criteria_comp,
            best_model_name=best_model,
            recommendations=recommendations
        )

    @staticmethod
    def save_report_to_json(report: EnsembleComparisonReport, filepath: str) -> str:
        """Persists the master comparison report as a formatted JSON document."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
        return filepath
