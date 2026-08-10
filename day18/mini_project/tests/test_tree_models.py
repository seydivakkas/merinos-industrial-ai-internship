"""
Merinos Industrial AI Internship - Day 18
Unit and Integration Test Suite for Decision Tree & Random Forest Pipeline
"""

import os
from pathlib import Path
import tempfile
import numpy as np
import pytest

from day18.mini_project.src.models import (
    DefectClass,
    EnsembleComparisonReport,
    PruningPathResult
)
from day18.mini_project.src.data_generator import TreeQualityDataGenerator
from day18.mini_project.src.preprocessor import TreeDataPreprocessor
from day18.mini_project.src.tree_models import (
    MerinosDecisionTreeClassifier,
    MerinosRandomForestClassifier
)
from day18.mini_project.src.evaluator import TreeEnsembleEvaluator
from day18.mini_project.src.visualizer import TreeVisualizer


@pytest.fixture
def dataset():
    """Provides consistent synthetic telemetry dataset for tests."""
    gen = TreeQualityDataGenerator(n_samples=600, random_state=42)
    return gen.generate()


@pytest.fixture
def split_data(dataset):
    """Provides partitioned train/test matrices."""
    preprocessor = TreeDataPreprocessor(test_size=0.25, random_state=42)
    return preprocessor.split(dataset)


def test_data_generator_non_linear_partition(dataset):
    """1. Tests synthetic dataset shape, feature count, and multiclass distribution."""
    assert len(dataset) == 600
    assert "defect_class" in dataset.columns
    assert "defect_name" in dataset.columns

    unique_classes = set(dataset["defect_class"].unique())
    assert unique_classes == {0, 1, 2, 3}

    # Verify physical non-negative bounds
    assert (dataset["yarn_tensile_strength"] >= 10.0).all()
    assert (dataset["ambient_relative_humidity"] >= 30.0).all()


def test_preprocessor_stratified_integrity(split_data):
    """2. Tests stratified partitioning proportions and non-null array shapes."""
    X_train, X_test, y_train, y_test = split_data

    assert len(X_train) == 450
    assert len(X_test) == 150
    assert X_train.shape[1] == 10
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_test).any()

    # Stratified balance check: all classes present in both splits
    assert len(np.unique(y_train)) == 4
    assert len(np.unique(y_test)) == 4


def test_unpruned_decision_tree_overfitting_behavior(split_data):
    """3. Tests that unpruned tree exhibits high train accuracy and non-trivial complexity."""
    X_train, X_test, y_train, y_test = split_data
    dt = MerinosDecisionTreeClassifier(criterion="gini", random_state=42)
    dt.fit(X_train, y_train)

    comp = dt.get_complexity()
    assert comp.depth >= 3
    assert comp.leaf_count >= 5
    assert comp.node_count > comp.leaf_count

    eval_res = TreeEnsembleEvaluator.evaluate_model(dt, X_train, y_train, X_test, y_test)
    assert eval_res.train_accuracy >= eval_res.test_accuracy
    assert eval_res.train_accuracy >= 0.90
    assert eval_res.test_accuracy >= 0.75


def test_cost_complexity_pruning_path_computation(split_data):
    """4. Tests ccp_alpha extraction, monotonicity, and optimal alpha identification."""
    X_train, X_test, y_train, y_test = split_data
    dt = MerinosDecisionTreeClassifier(criterion="gini", random_state=42)
    path_res = dt.compute_pruning_path(X_train, y_train, X_test, y_test, max_alpha_points=15)

    assert isinstance(path_res, PruningPathResult)
    assert len(path_res.ccp_alphas) > 0
    assert path_res.optimal_ccp_alpha >= 0.0
    assert path_res.optimal_leaf_count >= 1
    assert len(path_res.train_scores) == len(path_res.ccp_alphas)


def test_pruned_tree_complexity_reduction(split_data):
    """5. Tests that pruned tree reduces leaf count while maintaining high accuracy."""
    X_train, X_test, y_train, y_test = split_data
    unpruned = MerinosDecisionTreeClassifier(random_state=42).fit(X_train, y_train)
    path_res = unpruned.compute_pruning_path(X_train, y_train, X_test, y_test)

    pruned = MerinosDecisionTreeClassifier(
        ccp_alpha=path_res.optimal_ccp_alpha,
        random_state=42
    ).fit(X_train, y_train)

    unpruned_comp = unpruned.get_complexity()
    pruned_comp = pruned.get_complexity()

    assert pruned_comp.leaf_count <= unpruned_comp.leaf_count
    assert pruned_comp.depth <= unpruned_comp.depth


def test_random_forest_training_and_oob_metrics(split_data):
    """6. Tests Random Forest ensemble fitting, OOB score, and test accuracy."""
    X_train, X_test, y_train, y_test = split_data
    rf = MerinosRandomForestClassifier(
        n_estimators=30,
        oob_score=True,
        random_state=42
    ).fit(X_train, y_train)

    oob_score, oob_error = rf.get_oob_metrics()
    assert 0.0 < oob_score <= 1.0
    assert abs((oob_score + oob_error) - 1.0) < 1e-5

    eval_res = TreeEnsembleEvaluator.evaluate_model(rf, X_train, y_train, X_test, y_test)
    assert eval_res.test_accuracy >= 0.85
    assert eval_res.macro_f1 >= 0.80


def test_random_forest_oob_convergence(split_data):
    """7. Tests Out-Of-Bag error curve generation across tree counts."""
    X_train, _, y_train, _ = split_data
    rf = MerinosRandomForestClassifier(n_estimators=20, random_state=42)
    tree_counts, oob_errors = rf.compute_oob_convergence(
        X_train, y_train, min_trees=5, max_trees=25, step=10
    )

    assert len(tree_counts) == 3
    assert tree_counts == [5, 15, 25]
    assert all(0.0 <= err <= 1.0 for err in oob_errors)


def test_gini_vs_entropy_criteria_comparison(split_data):
    """8. Tests comparative evaluation between Gini Impurity and Shannon Entropy."""
    X_train, X_test, y_train, y_test = split_data
    criteria_res = TreeEnsembleEvaluator.compare_criteria(
        X_train, y_train, X_test, y_test, random_state=42
    )

    assert "gini" in criteria_res
    assert "entropy" in criteria_res
    assert criteria_res["gini"]["test_accuracy"] >= 0.75
    assert criteria_res["entropy"]["test_accuracy"] >= 0.75


def test_feature_importance_sum_to_one(split_data):
    """9. Tests that Random Forest MDI feature importances are non-negative and sum to 1.0."""
    X_train, _, y_train, _ = split_data
    feature_names = [f"feat_{i}" for i in range(10)]
    rf = MerinosRandomForestClassifier(n_estimators=20, random_state=42).fit(X_train, y_train)
    importances = rf.get_feature_importances(feature_names)

    assert len(importances) == 10
    total_imp = sum(importances.values())
    assert abs(total_imp - 1.0) < 0.02
    assert all(v >= 0.0 for v in importances.values())


def test_cli_lifecycle_and_json_report_generation(split_data):
    """10. Tests full evaluation report generation, JSON serialization, and panel plotting."""
    X_train, X_test, y_train, y_test = split_data
    feature_names = [f"f_{i}" for i in range(10)]

    unpruned = MerinosDecisionTreeClassifier(random_state=42).fit(X_train, y_train)
    path_res = unpruned.compute_pruning_path(X_train, y_train, X_test, y_test)
    pruned = MerinosDecisionTreeClassifier(ccp_alpha=path_res.optimal_ccp_alpha, random_state=42).fit(X_train, y_train)
    rf = MerinosRandomForestClassifier(n_estimators=20, random_state=42).fit(X_train, y_train)

    report = TreeEnsembleEvaluator.generate_report(
        unpruned_tree=unpruned,
        pruned_tree=pruned,
        random_forest=rf,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    assert isinstance(report, EnsembleComparisonReport)
    assert report.best_model_name in ["Random Forest Ensemble", "Cost-Complexity Pruned Decision Tree"]

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "report.json")
        saved_json = TreeEnsembleEvaluator.save_report_to_json(report, json_path)
        assert os.path.exists(saved_json)

        png_path = os.path.join(tmpdir, "panel.png")
        viz = TreeVisualizer()
        saved_png = viz.plot_diagnostic_panel(report, path_res, ([5, 10], [0.15, 0.10]), png_path)
        assert os.path.exists(saved_png)
        assert os.path.getsize(saved_png) > 30000
