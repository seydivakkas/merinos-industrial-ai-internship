"""
Merinos Industrial AI Internship - Day 19
Unit and Integration Test Suite for Gradient Boosting (XGBoost & LightGBM)
"""

import os
import tempfile
import numpy as np
import pytest

from day19.mini_project.src.models import (
    DefectClass,
    EarlyStoppingResult,
    BoostingComparisonReport,
    HyperparameterTuningResult
)
from day19.mini_project.src.data_generator import BoostingQualityDataGenerator
from day19.mini_project.src.preprocessor import BoostingDataPreprocessor
from day19.mini_project.src.boosting_models import (
    MerinosXGBoostClassifier,
    MerinosLightGBMClassifier
)
from day19.mini_project.src.evaluator import BoostingEvaluator
from day19.mini_project.src.visualizer import BoostingVisualizer


@pytest.fixture
def dataset():
    """Provides consistent synthetic telemetry dataset for tests."""
    gen = BoostingQualityDataGenerator(n_samples=600, random_state=42)
    return gen.generate()


@pytest.fixture
def split_data(dataset):
    """Provides 3-way partitioned matrices (Train, Val, Test)."""
    preprocessor = BoostingDataPreprocessor(
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        random_state=42
    )
    return preprocessor.split_3way(dataset)


def test_data_generator_boosting_distribution(dataset):
    """1. Tests dataset shape, feature completeness, and class distribution."""
    assert len(dataset) == 600
    assert "defect_class" in dataset.columns
    assert "defect_name" in dataset.columns

    unique_classes = set(dataset["defect_class"].unique())
    assert unique_classes == {0, 1, 2, 3}

    assert (dataset["yarn_tensile_strength"] >= 10.0).all()
    assert (dataset["ambient_relative_humidity"] >= 30.0).all()


def test_preprocessor_3way_stratified_split(split_data):
    """2. Tests 3-way stratified partition proportions and non-null arrays."""
    X_train, y_train, X_val, y_val, X_test, y_test = split_data

    assert len(X_train) == 420  # 70%
    assert len(X_val) == 90     # 15%
    assert len(X_test) == 90    # 15%

    assert X_train.shape[1] == 10
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_val).any()
    assert not np.isnan(X_test).any()

    # Stratified balance across all 3 partitions
    assert len(np.unique(y_train)) == 4
    assert len(np.unique(y_val)) == 4
    assert len(np.unique(y_test)) == 4


def test_xgboost_training_and_early_stopping(split_data):
    """3. Tests XGBoost model fitting and early stopping loss tracking."""
    X_train, y_train, X_val, y_val, _, _ = split_data
    xgb_model = MerinosXGBoostClassifier(
        n_estimators=30,
        learning_rate=0.1,
        early_stopping_rounds=5,
        random_state=42
    )
    xgb_model.fit(X_train, y_train, X_val, y_val)

    es_res = xgb_model.get_early_stopping_result()
    assert isinstance(es_res, EarlyStoppingResult)
    assert es_res.best_iteration >= 1
    assert es_res.stopping_iteration >= es_res.best_iteration
    assert len(es_res.train_loss_history) > 0
    assert len(es_res.val_loss_history) > 0
    assert es_res.best_val_loss >= 0.0


def test_lightgbm_training_and_early_stopping(split_data):
    """4. Tests LightGBM model fitting and callback-based early stopping."""
    X_train, y_train, X_val, y_val, _, _ = split_data
    lgb_model = MerinosLightGBMClassifier(
        n_estimators=30,
        learning_rate=0.1,
        early_stopping_rounds=5,
        random_state=42
    )
    lgb_model.fit(X_train, y_train, X_val, y_val)

    es_res = lgb_model.get_early_stopping_result()
    assert isinstance(es_res, EarlyStoppingResult)
    assert es_res.best_iteration >= 1
    assert len(es_res.train_loss_history) > 0
    assert len(es_res.val_loss_history) > 0


def test_xgboost_accuracy_and_metrics(split_data):
    """5. Tests XGBoost test set generalization and multiclass metrics."""
    X_train, y_train, X_val, y_val, X_test, y_test = split_data
    xgb_model = MerinosXGBoostClassifier(
        n_estimators=30,
        learning_rate=0.1,
        early_stopping_rounds=5,
        random_state=42
    ).fit(X_train, y_train, X_val, y_val)

    metrics = BoostingEvaluator.evaluate_model(
        xgb_model, X_train, y_train, X_val, y_val, X_test, y_test
    )

    assert metrics.accuracy >= 0.85
    assert metrics.macro_f1 >= 0.80
    assert metrics.cohen_kappa >= 0.80
    assert metrics.val_loss >= 0.0


def test_lightgbm_accuracy_and_metrics(split_data):
    """6. Tests LightGBM test set generalization and multiclass metrics."""
    X_train, y_train, X_val, y_val, X_test, y_test = split_data
    lgb_model = MerinosLightGBMClassifier(
        n_estimators=30,
        learning_rate=0.1,
        early_stopping_rounds=5,
        random_state=42
    ).fit(X_train, y_train, X_val, y_val)

    metrics = BoostingEvaluator.evaluate_model(
        lgb_model, X_train, y_train, X_val, y_val, X_test, y_test
    )

    assert metrics.accuracy >= 0.85
    assert metrics.macro_f1 >= 0.80
    assert metrics.cohen_kappa >= 0.80


def test_feature_importances_sum_to_one(split_data):
    """7. Tests that Gain and Split feature importances normalize to sum to 1.0."""
    X_train, y_train, X_val, y_val, _, _ = split_data
    feature_names = [f"f_{i}" for i in range(10)]

    xgb_model = MerinosXGBoostClassifier(n_estimators=20, random_state=42).fit(X_train, y_train, X_val, y_val)
    lgb_model = MerinosLightGBMClassifier(n_estimators=20, random_state=42).fit(X_train, y_train, X_val, y_val)

    imp_xgb = xgb_model.get_feature_importances(feature_names)
    imp_lgb = lgb_model.get_feature_importances(feature_names)

    assert len(imp_xgb) == 10
    assert len(imp_lgb) == 10
    assert abs(sum(imp_xgb.values()) - 1.0) < 0.02
    assert abs(sum(imp_lgb.values()) - 1.0) < 0.02


def test_hyperparameter_tuning_sweep(split_data):
    """8. Tests grid tuning search over learning rates and depths."""
    X_train, y_train, X_val, y_val, X_test, y_test = split_data

    res = BoostingEvaluator.tune_hyperparameters(
        X_train, y_train, X_val, y_val, X_test, y_test,
        learning_rates=[0.05, 0.15],
        max_depths=[3, 4],
        model_type="xgboost"
    )

    assert isinstance(res, HyperparameterTuningResult)
    assert len(res.records) == 4
    assert res.best_learning_rate in [0.05, 0.15]
    assert res.best_max_depth in [3, 4]
    assert res.best_accuracy >= 0.80


def test_latency_and_throughput_benchmarks(split_data):
    """9. Tests single-sample latency profiling and throughput calculation."""
    X_train, y_train, X_val, y_val, X_test, _ = split_data
    lgb_model = MerinosLightGBMClassifier(n_estimators=20, random_state=42).fit(X_train, y_train, X_val, y_val)

    lat_ms, fps = lgb_model.benchmark_latency(X_test, n_runs=50)
    assert lat_ms >= 0.0
    assert fps > 0.0


def test_cli_lifecycle_and_json_report_generation(split_data):
    """10. Tests full report generation, JSON serialization, and 2x2 panel plotting."""
    X_train, y_train, X_val, y_val, X_test, y_test = split_data
    feature_names = [f"f_{i}" for i in range(10)]

    xgb_model = MerinosXGBoostClassifier(n_estimators=20, random_state=42).fit(X_train, y_train, X_val, y_val)
    lgb_model = MerinosLightGBMClassifier(n_estimators=20, random_state=42).fit(X_train, y_train, X_val, y_val)

    report = BoostingEvaluator.generate_report(
        xgb_model=xgb_model,
        lgb_model=lgb_model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    assert isinstance(report, BoostingComparisonReport)
    assert report.champion_model in ["XGBoost Classifier", "LightGBM Classifier"]

    xgb_es = xgb_model.get_early_stopping_result()
    lgb_es = lgb_model.get_early_stopping_result()
    tuning_res = BoostingEvaluator.tune_hyperparameters(
        X_train, y_train, X_val, y_val, X_test, y_test,
        learning_rates=[0.1],
        max_depths=[3],
        model_type="xgboost"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "report.json")
        saved_json = BoostingEvaluator.save_report_to_json(report, json_path)
        assert os.path.exists(saved_json)

        png_path = os.path.join(tmpdir, "panel.png")
        viz = BoostingVisualizer()
        saved_png = viz.plot_diagnostic_panel(report, xgb_es, lgb_es, tuning_res, png_path)
        assert os.path.exists(saved_png)
        assert os.path.getsize(saved_png) > 30000
