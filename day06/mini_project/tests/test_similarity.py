"""
Merinos Industrial AI Internship - Day 06
test_similarity.py: Comprehensive Test Suite for Vector Similarity Metrics & Search Engine
"""

from pathlib import Path
import json
import numpy as np
import pytest

from day06.mini_project.src import metrics
from day06.mini_project.src.scalers import StandardScaler, MinMaxScaler, L2Normalizer
from day06.mini_project.src.curse_analyzer import CurseOfDimensionalityAnalyzer
from day06.mini_project.src.search import VectorSimilaritySearchEngine, run_benchmark_and_generate_artifacts

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def sample_vectors():
    u = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    v = np.array([4.0, 5.0, 6.0], dtype=np.float32)
    w = np.array([2.0, 0.0, -1.0], dtype=np.float32)
    return u, v, w


def test_euclidean_distance_numerical_properties(sample_vectors):
    u, v, w = sample_vectors

    # 1. Identity of indiscernibles: d(u, u) == 0
    assert metrics.euclidean_distance(u, u) == pytest.approx(0.0, abs=1e-6)

    # 2. Positivity: d(u, v) >= 0
    d_uv = metrics.euclidean_distance(u, v)
    assert d_uv > 0.0

    # 3. Symmetry: d(u, v) == d(v, u)
    assert metrics.euclidean_distance(v, u) == pytest.approx(d_uv, abs=1e-6)

    # 4. Triangle inequality: d(u, w) <= d(u, v) + d(v, w)
    d_uw = metrics.euclidean_distance(u, w)
    d_vw = metrics.euclidean_distance(v, w)
    assert d_uw <= d_uv + d_vw + 1e-6


def test_manhattan_distance_numerical_properties(sample_vectors):
    u, v, _ = sample_vectors
    d_l1 = metrics.manhattan_distance(u, v)

    # |1-4| + |2-5| + |3-6| = 3 + 3 + 3 = 9.0
    assert d_l1 == pytest.approx(9.0, abs=1e-6)
    assert metrics.manhattan_distance(v, u) == pytest.approx(d_l1, abs=1e-6)


def test_cosine_similarity_properties():
    u = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    w = np.array([2.0, 0.0, 0.0], dtype=np.float32)
    neg_u = np.array([-1.0, 0.0, 0.0], dtype=np.float32)

    # Orthogonal vectors: similarity == 0.0
    assert metrics.cosine_similarity(u, v) == pytest.approx(0.0, abs=1e-6)

    # Collinear vectors (independent of scale): similarity == 1.0
    assert metrics.cosine_similarity(u, w) == pytest.approx(1.0, abs=1e-6)

    # Opposite vectors: similarity == -1.0
    assert metrics.cosine_similarity(u, neg_u) == pytest.approx(-1.0, abs=1e-6)


def test_l2_normalized_cosine_euclidean_relationship():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((10, 16)).astype(np.float32)
    X_unit = L2Normalizer.transform(X)

    for i in range(len(X_unit)):
        for j in range(i + 1, len(X_unit)):
            u = X_unit[i]
            v = X_unit[j]

            d_e = metrics.euclidean_distance(u, v)
            d_c = metrics.cosine_distance(u, v)

            # Mathematical identity on unit vectors: d_E^2 == 2 * d_C
            assert (d_e ** 2) == pytest.approx(2.0 * d_c, abs=1e-4)


def test_mahalanobis_distance_identity_covariance(sample_vectors):
    u, v, _ = sample_vectors
    dim = len(u)
    cov_eye = np.eye(dim, dtype=np.float32)

    # When Sigma == Identity, Mahalanobis == Euclidean
    d_m = metrics.mahalanobis_distance(u, v, cov_eye)
    d_e = metrics.euclidean_distance(u, v)
    assert d_m == pytest.approx(d_e, abs=1e-5)


def test_minkowski_distance_cases(sample_vectors):
    u, v, _ = sample_vectors
    # p=1 -> Manhattan
    assert metrics.minkowski_distance(u, v, p=1.0) == pytest.approx(metrics.manhattan_distance(u, v), abs=1e-5)
    # p=2 -> Euclidean
    assert metrics.minkowski_distance(u, v, p=2.0) == pytest.approx(metrics.euclidean_distance(u, v), abs=1e-5)


def test_pairwise_metric_matrices_shapes_and_values():
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=np.float32)
    Y = np.array([[1.0, 2.0], [0.0, 0.0]], dtype=np.float32)

    # Shapes
    p_euc = metrics.pairwise_euclidean(X, Y)
    assert p_euc.shape == (3, 2)
    assert p_euc[0, 0] == pytest.approx(0.0, abs=1e-5)

    p_man = metrics.pairwise_manhattan(X, Y)
    assert p_man.shape == (3, 2)

    p_cos = metrics.pairwise_cosine_similarity(X, Y)
    assert p_cos.shape == (3, 2)
    assert p_cos[0, 0] == pytest.approx(1.0, abs=1e-5)


def test_scalers_transformation_properties():
    rng = np.random.default_rng(42)
    X = rng.uniform(10.0, 100.0, size=(50, 5)).astype(np.float32)

    # StandardScaler
    scaler_std = StandardScaler().fit(X)
    X_std = scaler_std.transform(X)
    assert np.allclose(np.mean(X_std, axis=0), 0.0, atol=1e-5)
    assert np.allclose(np.std(X_std, axis=0), 1.0, atol=1e-5)

    # MinMaxScaler
    scaler_mm = MinMaxScaler(feature_range=(0.0, 1.0)).fit(X)
    X_mm = scaler_mm.transform(X)
    assert X_mm.min() == pytest.approx(0.0, abs=1e-5)
    assert X_mm.max() == pytest.approx(1.0, abs=1e-5)

    # L2Normalizer
    X_l2 = L2Normalizer.transform(X)
    norms = np.linalg.norm(X_l2, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_curse_of_dimensionality_concentration():
    # Compare relative contrast at D=2 vs D=128
    rep_2d = CurseOfDimensionalityAnalyzer.evaluate_dimension(dim=2, n_samples=300, seed=42)
    rep_128d = CurseOfDimensionalityAnalyzer.evaluate_dimension(dim=128, n_samples=300, seed=42)

    # Relative contrast must decrease significantly as dimension increases
    assert rep_2d["relative_contrast"] > rep_128d["relative_contrast"]
    assert rep_128d["relative_contrast"] > 0.0


def test_vector_similarity_search_and_artifacts(tmp_path):
    fixture_file = FIXTURES_DIR / "carpet_feature_embeddings.npz"
    res = run_benchmark_and_generate_artifacts(fixture_file, tmp_path)

    assert "benchmarks" in res
    assert "curse_report" in res
    assert "search_sample" in res

    # Verify exported files exist
    assert Path(res["benchmark_file"]).exists()
    assert Path(res["curse_file"]).exists()
    assert Path(res["search_file"]).exists()
    assert Path(res["summary_file"]).exists()

    # Verify search content
    search_sample = res["search_sample"]
    assert len(search_sample["comparisons"]["cosine"]) == 5
    # Nearest neighbor should have lowest distance
    dists = [item["distance"] for item in search_sample["comparisons"]["cosine"]]
    assert dists == sorted(dists)
