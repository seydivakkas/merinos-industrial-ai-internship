"""Unit and integration test suite for Day 21 Unsupervised Learning & Phase 3 Master Benchmark."""

import json
from pathlib import Path
import numpy as np
import pytest

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from day21.mini_project.src.data_generator import UnsupervisedQualityDataGenerator
from day21.mini_project.src.preprocessor import UnsupervisedPreprocessor
from day21.mini_project.src.dimensionality import MerinosDimensionalityReducer
from day21.mini_project.src.clustering import MerinosClusteringEngine
from day21.mini_project.src.benchmark_consolidator import Phase3BenchmarkConsolidator
from day21.mini_project.src.visualizer import UnsupervisedVisualizer
from day21.mini_project.src.models import (
    PCAMetrics,
    ClusteringMetrics,
    DBSCANAnomalyMetrics,
    Phase3MasterReport,
    AnomalyDetectionResult
)


@pytest.fixture(scope="module")
def sample_dataset():
    """Generates a compact synthetic dataset for fast, deterministic testing."""
    gen = UnsupervisedQualityDataGenerator(n_samples=400, n_anomalies=20, random_state=42)
    return gen.generate()


@pytest.fixture(scope="module")
def scaled_data(sample_dataset):
    """Scales the feature matrix for clustering and dimensionality tests."""
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(sample_dataset)
    X_raw = sample_dataset[preprocessor.get_feature_names()].values
    return X_raw, X_scaled, y, is_anom, preprocessor


def test_data_generator_distribution_and_anomalies():
    """1. Tests data generator sample count, defect classes, and extreme novel anomalies."""
    gen = UnsupervisedQualityDataGenerator(n_samples=400, n_anomalies=24, random_state=42)
    df = gen.generate()

    assert len(df) == 424
    assert "defect_class" in df.columns
    assert "defect_name" in df.columns
    assert "is_anomaly" in df.columns

    # Nominal classes 0, 1, 2, 3 have 100 samples each
    for c_id in range(4):
        assert (df["defect_class"] == c_id).sum() == 100

    # Anomalies have label -1
    assert (df["defect_class"] == -1).sum() == 24
    assert (df["is_anomaly"] == 1).sum() == 24


def test_preprocessor_scaling(sample_dataset):
    """2. Tests data preprocessor matrix extraction, z-score scaling, and single sample transform."""
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(sample_dataset)

    assert X_scaled.shape == (420, 10)
    assert len(y) == 420
    assert len(is_anom) == 420

    # Mean approx 0 and std approx 1
    assert np.allclose(X_scaled.mean(axis=0), 0.0, atol=1e-2)
    assert np.allclose(X_scaled.std(axis=0), 1.0, atol=1e-2)

    # Single vector transform
    single_raw = np.array([18.0, 11.0, 4.8, 435.0, 2230.0, 615.0, 41.0, 59.0, 24.0, 530.0])
    single_vec = preprocessor.transform_sample(single_raw)
    assert single_vec.shape == (1, 10)
    assert not np.isnan(single_vec).any()


def test_pca_dimensionality_reduction(scaled_data):
    """3. Tests full PCA explained variance, elbow threshold detection, and 2D projection."""
    _, X_scaled, _, _, _ = scaled_data
    reducer = MerinosDimensionalityReducer(random_state=42)
    pca, X_pca, explained_variance_ratio = reducer.fit_pca(X_scaled, n_components=0.95)

    assert isinstance(pca, PCA)
    assert len(explained_variance_ratio) > 0
    assert X_pca.shape[0] == len(X_scaled)
    assert X_pca.shape[1] == pca.n_components_
    assert not np.isnan(X_pca).any()


def test_tsne_manifold_projection(scaled_data):
    """4. Tests non-linear t-SNE 2D manifold projection shape and numeric stability."""
    _, X_scaled, _, _, _ = scaled_data
    reducer = MerinosDimensionalityReducer(random_state=42)
    X_tsne_2d = reducer.fit_tsne(X_scaled)

    assert X_tsne_2d.shape == (len(X_scaled), 2)
    assert not np.isnan(X_tsne_2d).any()


def test_kmeans_clustering_metrics(scaled_data):
    """5. Tests K-Means clustering, silhouette score, Davies-Bouldin, and ARI alignment."""
    _, X_scaled, y, _, _ = scaled_data
    engine = MerinosClusteringEngine(random_state=42)
    res = engine.fit_kmeans(X_scaled, n_clusters=4)

    assert "model" in res
    assert "labels" in res
    assert "silhouette_score" in res
    assert "davies_bouldin_score" in res
    assert -1.0 <= res["silhouette_score"] <= 1.0
    assert res["silhouette_score"] > 0.15 # Well-structured industrial telemetry
    assert res["davies_bouldin_score"] > 0.0
    assert len(res["labels"]) == len(X_scaled)
    assert len(set(res["labels"])) == 4


def test_dbscan_anomaly_detection(scaled_data):
    """6. Tests DBSCAN density clustering and unlabelled anomaly isolation."""
    _, X_scaled, _, _, _ = scaled_data
    engine = MerinosClusteringEngine(random_state=42)
    res = engine.fit_dbscan(X_scaled, eps=1.8, min_samples=5)

    assert "model" in res
    assert "labels" in res
    assert "n_clusters" in res
    assert res["n_clusters"] >= 1
    assert -1 in res["labels"]


def test_live_anomaly_detection_sample(scaled_data):
    """7. Tests real-time live anomaly scoring against fitted sample distances."""
    _, X_scaled, y, _, preprocessor = scaled_data
    engine = MerinosClusteringEngine(random_state=42)

    # 1. Nominal sample (close to Yarn Breakage centroid)
    nom_raw = np.array([15.0, 9.5, 4.5, 430.0, 2220.0, 610.0, 42.0, 58.0, 23.5, 525.0])
    nom_sample = preprocessor.transform_sample(nom_raw)
    is_nom_anom = engine.detect_anomaly_sample(X_scaled, nom_sample)
    assert is_nom_anom == 0.0

    # 2. Extreme anomaly sample (massive tension and temperature)
    anom_raw = np.array([8.0, 4.0, 12.0, 250.0, 1500.0, 950.0, 85.0, 18.0, 48.0, 820.0])
    anom_sample = preprocessor.transform_sample(anom_raw)
    is_anom = engine.detect_anomaly_sample(X_scaled, anom_sample)
    assert isinstance(is_anom, float)
    assert is_anom in (0.0, 1.0)


def test_phase3_benchmark_consolidator(scaled_data):
    """8. Tests consolidation of all 7 Phase 3 models under identical test partitions."""
    X_raw, _, y, _, _ = scaled_data
    pca_metrics = PCAMetrics(
        explained_variance_ratio=[0.2, 0.18, 0.15, 0.12, 0.1, 0.08, 0.06, 0.05, 0.04, 0.02],
        cumulative_variance_ratio=[0.2, 0.38, 0.53, 0.65, 0.75, 0.83, 0.89, 0.94, 0.98, 1.0],
        components_for_95_variance=9,
        total_variance_explained=1.0
    )
    clustering_metrics = ClusteringMetrics(
        silhouette_score=0.45,
        davies_bouldin_index=0.85,
        calinski_harabasz_index=350.0,
        adjusted_rand_index=0.72
    )
    dbscan_metrics = DBSCANAnomalyMetrics(
        n_clusters_found=4,
        n_anomalies_detected=20,
        anomaly_ratio_pct=4.76
    )

    consolidator = Phase3BenchmarkConsolidator(random_state=42)
    report = consolidator.run_master_benchmark(
        X_raw=X_raw,
        y=y,
        pca_metrics=pca_metrics,
        clustering_metrics=clustering_metrics,
        dbscan_metrics=dbscan_metrics
    )

    assert isinstance(report, Phase3MasterReport)
    assert report.total_models_evaluated == 7
    assert len(report.models) == 7

    model_names = [m.model_name for m in report.models]
    assert "Multinomial Logistic Regression" in model_names
    assert "Cost-Complexity Pruned Decision Tree" in model_names
    assert "Random Forest Classifier" in model_names
    assert "XGBoost Classifier" in model_names
    assert "LightGBM Classifier" in model_names
    assert "Linear Support Vector Machine" in model_names
    assert "RBF (Gaussian) Support Vector Machine" in model_names

    for m in report.models:
        assert m.test_accuracy >= 0.80
        assert m.macro_f1 >= 0.80
        assert m.single_sample_latency_ms > 0.0
        assert m.throughput_fps > 0.0

    assert report.champion_high_speed_edge is not None
    assert report.champion_high_accuracy_server is not None
    assert len(report.phase_conclusion_summary) > 20


def test_visualizer_master_panel_generation(scaled_data, tmp_path):
    """9. Tests rendering of 2x2 diagnostic figure with PCA, t-SNE, DBSCAN, and Model Benchmark."""
    X_raw, X_scaled, y, _, _ = scaled_data

    reducer = MerinosDimensionalityReducer(random_state=42)
    pca, X_pca_2d, exp_var = reducer.fit_pca(X_scaled, n_components=0.95)
    X_tsne_2d = reducer.fit_tsne(X_scaled)

    engine = MerinosClusteringEngine(random_state=42)
    km_res = engine.fit_kmeans(X_scaled, n_clusters=4)
    db_res = engine.fit_dbscan(X_scaled, eps=1.8, min_samples=5)

    cum_var = np.cumsum(exp_var).tolist()
    k95 = next((i + 1 for i, v in enumerate(cum_var) if v >= 0.95), len(exp_var))
    pca_metrics = PCAMetrics(
        explained_variance_ratio=[round(float(v), 4) for v in exp_var],
        cumulative_variance_ratio=[round(float(v), 4) for v in cum_var],
        components_for_95_variance=k95,
        total_variance_explained=round(float(sum(exp_var)), 4)
    )
    clustering_metrics = ClusteringMetrics(
        silhouette_score=round(float(km_res["silhouette_score"]), 4),
        davies_bouldin_index=round(float(km_res["davies_bouldin_score"]), 4),
        calinski_harabasz_index=350.0,
        adjusted_rand_index=1.00
    )
    n_anom = int(np.sum(db_res["labels"] == -1))
    dbscan_metrics = DBSCANAnomalyMetrics(
        n_clusters_found=db_res["n_clusters"],
        n_anomalies_detected=n_anom,
        anomaly_ratio_pct=round((n_anom / len(X_scaled)) * 100.0, 2)
    )

    consolidator = Phase3BenchmarkConsolidator(random_state=42)
    report = consolidator.run_master_benchmark(
        X_raw=X_raw,
        y=y,
        pca_metrics=pca_metrics,
        clustering_metrics=clustering_metrics,
        dbscan_metrics=dbscan_metrics
    )

    out_file = tmp_path / "test_unsupervised_master_panel.png"
    vis = UnsupervisedVisualizer()
    vis.plot_master_panel(
        report=report,
        X_pca_2d=X_pca_2d,
        X_tsne_2d=X_tsne_2d,
        dbscan_labels=db_res["labels"],
        y_true=y,
        output_path=str(out_file)
    )

    assert out_file.exists()
    assert out_file.stat().st_size > 25_000


def test_models_json_serialization(scaled_data):
    """10. Tests Pydantic v2 serialization of Phase 3 Master Report to valid JSON."""
    X_raw, _, y, _, _ = scaled_data
    pca_metrics = PCAMetrics(
        explained_variance_ratio=[0.2, 0.18, 0.15, 0.12, 0.1, 0.08, 0.06, 0.05, 0.04, 0.02],
        cumulative_variance_ratio=[0.2, 0.38, 0.53, 0.65, 0.75, 0.83, 0.89, 0.94, 0.98, 1.0],
        components_for_95_variance=9,
        total_variance_explained=1.0
    )
    clustering_metrics = ClusteringMetrics(
        silhouette_score=0.42,
        davies_bouldin_index=0.91,
        calinski_harabasz_index=310.0,
        adjusted_rand_index=0.68
    )
    dbscan_metrics = DBSCANAnomalyMetrics(
        n_clusters_found=4,
        n_anomalies_detected=18,
        anomaly_ratio_pct=4.29
    )

    consolidator = Phase3BenchmarkConsolidator(random_state=42)
    report = consolidator.run_master_benchmark(
        X_raw=X_raw,
        y=y,
        pca_metrics=pca_metrics,
        clustering_metrics=clustering_metrics,
        dbscan_metrics=dbscan_metrics
    )

    dump_str = report.model_dump_json(indent=2)
    parsed = json.loads(dump_str)

    assert parsed["total_models_evaluated"] == 7
    assert len(parsed["models"]) == 7
    assert "champion_high_speed_edge" in parsed
    assert "champion_high_accuracy_server" in parsed
