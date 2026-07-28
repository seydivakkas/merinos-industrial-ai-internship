"""Unit tests for Day 07 Distance and Similarity Metrics."""

import numpy as np
import pytest
from day07.mini_project.src.distance_similarity import (
    KNNPatternMatcher,
    compute_pairwise_distances,
    cosine_similarity,
    euclidean_distance,
    manhattan_distance,
    minkowski_distance,
)


def test_distance_metrics():
    u = np.array([1.0, 2.0, 3.0])
    v = np.array([4.0, 6.0, 3.0])

    # Euclidean: sqrt(3^2 + 4^2 + 0) = 5.0
    assert euclidean_distance(u, v) == 5.0

    # Manhattan: 3 + 4 + 0 = 7.0
    assert manhattan_distance(u, v) == 7.0

    # Cosine identical vectors
    assert cosine_similarity(u, u) == pytest.approx(1.0)

    # Minkowski p=2 should equal Euclidean
    assert minkowski_distance(u, v, p=2.0) == pytest.approx(5.0)


def test_knn_pattern_matcher():
    matcher = KNNPatternMatcher(metric="euclidean")
    ids = ["carpet_red", "carpet_blue", "carpet_green"]
    features = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ])
    matcher.fit(ids, features)

    # Query close to red
    query = np.array([0.9, 0.1, 0.0])
    results = matcher.query(query, k=2)

    assert results[0][0] == "carpet_red"
    assert len(results) == 2


def test_pairwise_distance_matrix():
    X = np.array([
        [0.0, 0.0],
        [3.0, 0.0],
        [0.0, 4.0],
    ])
    D = compute_pairwise_distances(X, metric="euclidean")
    assert D.shape == (3, 3)
    assert D[0, 1] == 3.0
    assert D[0, 2] == 4.0
    assert D[1, 2] == 5.0
    assert D[0, 0] == 0.0
