"""Unit and integration test suite for Merinos SVM Defect Classification."""

import json
from pathlib import Path
import numpy as np
import pytest

from day20.mini_project.src.data_generator import SVMQualityDataGenerator
from day20.mini_project.src.preprocessor import SVMDataPreprocessor
from day20.mini_project.src.svm_models import MerinosSVMClassifier
from day20.mini_project.src.evaluator import SVMEvaluator
from day20.mini_project.src.visualizer import SVMVisualizer
from day20.mini_project.src.models import SVMComparisonReport


@pytest.fixture(scope="module")
def sample_dataset():
    """Generates a small synthetic dataset for fast, deterministic testing."""
    gen = SVMQualityDataGenerator(n_samples=400, random_state=42)
    return gen.generate()


@pytest.fixture(scope="module")
def prepared_data(sample_dataset):
    """Splits and standardizes the synthetic dataset."""
    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(sample_dataset)
    return X_train, X_test, y_train, y_test, preprocessor


def test_data_generator_svm_distribution():
    """Tests data generation integrity, column count, balance, and physical constraints."""
    gen = SVMQualityDataGenerator(n_samples=600, random_state=42)
    df = gen.generate()

    assert len(df) == 600
    assert "defect_class" in df.columns
    assert "defect_name" in df.columns
    assert df["defect_class"].nunique() in [4, 5]

    # Check balanced class distribution
    class_counts = df["defect_class"].value_counts()
    for count in class_counts:
        assert count in [120, 150]

    # Check physical boundaries
    assert df["yarn_tensile_strength"].between(10.0, 40.0).all()
    assert df["yarn_elongation_at_break"].between(6.0, 28.0).all()
    assert df["loom_tension_variation"].between(5.0, 60.0).all()


def test_preprocessor_scaling_and_split(sample_dataset):
    """Tests stratified 80/20 train/test split and z-score standard scaling."""
    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(sample_dataset)

    assert len(X_train) == 320
    assert len(X_test) == 80
    assert X_train.shape[1] == 10
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_test).any()

    # Verify z-score standardization properties on training set (mean ~ 0, std ~ 1)
    np.testing.assert_allclose(X_train.mean(axis=0), 0.0, atol=1e-2)
    np.testing.assert_allclose(X_train.std(axis=0), 1.0, atol=1e-2)


def test_linear_svm_training_and_metrics(prepared_data):
    """Verifies training, convergence, and metrics for Linear SVM."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42)
    clf.fit(X_train, y_train)

    metrics = SVMEvaluator.evaluate_model(clf, X_train, y_train, X_test, y_test)
    assert metrics.train_accuracy >= 0.85
    assert metrics.test_accuracy >= 0.85
    assert metrics.macro_f1 >= 0.85
    assert metrics.training_time_ms > 0.0


def test_polynomial_svm_training_and_metrics(prepared_data):
    """Verifies Polynomial SVM (cubic degree=3) fitting and generalization."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    clf = MerinosSVMClassifier(kernel="poly", degree=3, coef0=1.0, C=1.0, random_state=42)
    clf.fit(X_train, y_train)

    metrics = SVMEvaluator.evaluate_model(clf, X_train, y_train, X_test, y_test)
    assert metrics.test_accuracy >= 0.85
    assert metrics.cohen_kappa >= 0.80
    assert metrics.support_vectors.total_support_vectors > 0


def test_rbf_svm_training_and_metrics(prepared_data):
    """Verifies RBF (Gaussian) SVM high accuracy, Platt probabilities, and latency."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42)
    clf.fit(X_train, y_train)

    metrics = SVMEvaluator.evaluate_model(clf, X_train, y_train, X_test, y_test)
    assert metrics.test_accuracy >= 0.95
    assert metrics.macro_f1 >= 0.95

    # Check Platt probabilities sum to 1.0
    probs = clf.predict_proba(X_test[:5])
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, atol=1e-5)


def test_rbf_svm_outperforms_or_matches_linear(prepared_data):
    """Verifies RBF SVM non-linear capability equals or exceeds Linear SVM."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    lin_clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42).fit(X_train, y_train)
    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    lin_m = SVMEvaluator.evaluate_model(lin_clf, X_train, y_train, X_test, y_test)
    rbf_m = SVMEvaluator.evaluate_model(rbf_clf, X_train, y_train, X_test, y_test)

    assert rbf_m.test_accuracy >= lin_m.test_accuracy
    assert rbf_m.macro_f1 >= lin_m.macro_f1


def test_support_vectors_integrity_and_ratios(prepared_data):
    """Verifies support vector extraction, class breakdown, and dual coefficients."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    sv_info = clf.get_support_vector_metrics()
    assert sv_info.total_support_vectors > 0
    assert 0.0 < sv_info.support_vector_ratio_pct <= 100.0
    assert len(sv_info.support_vectors_per_class) in [4, 5]
    assert sum(sv_info.support_vectors_per_class.values()) == sv_info.total_support_vectors
    assert sv_info.dual_coef_norm > 0.0


def test_hyperparameter_grid_tuning(prepared_data):
    """Tests grid search over C and gamma values and validates optimal selection."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    grid_res = SVMEvaluator.tune_hyperparameters(
        X_train, y_train, X_test, y_test,
        C_values=[1.0, 10.0],
        gamma_values=[0.01, 0.1],
        cv_folds=3
    )

    assert len(grid_res.grid_records) == 4
    assert grid_res.best_C in [1.0, 10.0]
    assert grid_res.best_gamma in [0.01, 0.1]
    assert grid_res.best_score >= 0.85


def test_latency_and_throughput_benchmarks(prepared_data):
    """Verifies single-sample inference latency benchmark and throughput calculation."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    latency_ms, fps = clf.benchmark_latency(X_test, n_runs=50)
    assert 0.0 < latency_ms < 50.0
    assert fps > 20.0


def test_cli_lifecycle_and_json_report(prepared_data, tmp_path):
    """Tests report generation, JSON serializability, and visualizer panel generation."""
    X_train, X_test, y_train, y_test, _ = prepared_data
    lin_clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42).fit(X_train, y_train)
    poly_clf = MerinosSVMClassifier(kernel="poly", degree=3, coef0=1.0, C=1.0, random_state=42).fit(X_train, y_train)
    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    report = SVMEvaluator.generate_comparison_report(lin_clf, poly_clf, rbf_clf, X_train, y_train, X_test, y_test)
    assert isinstance(report, SVMComparisonReport)
    assert report.winner_model in ["Linear SVM", "Polynomial SVM", "RBF (Gaussian) SVM"]

    json_path = tmp_path / "test_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f)
    assert json_path.exists()

    viz = SVMVisualizer()
    png_path = tmp_path / "test_panel.png"
    out_fig = viz.plot_diagnostic_panel(report, None, X_train, y_train, str(png_path))
    assert Path(out_fig).exists()
