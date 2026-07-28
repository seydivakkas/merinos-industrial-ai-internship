"""Day 07 - Distance and Similarity Methods for Industrial Pattern Matching.

Implements Euclidean (L2), Manhattan (L1), Cosine, and Minkowski distance metrics,
pairwise distance matrix computation, and K-Nearest Neighbors search.
"""

from typing import List, Tuple
import numpy as np


def euclidean_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Computes Euclidean (L2) distance between two vectors."""
    diff = u - v
    return float(np.sqrt(np.dot(diff, diff)))


def manhattan_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Computes Manhattan (L1) distance between two vectors."""
    return float(np.sum(np.abs(u - v)))


def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    """Computes Cosine similarity between two vectors."""
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    if norm_u == 0.0 or norm_v == 0.0:
        return 0.0
    return float(np.dot(u, v) / (norm_u * norm_v))


def minkowski_distance(u: np.ndarray, v: np.ndarray, p: float = 3.0) -> float:
    """Computes Minkowski (L_p) distance."""
    if p < 1.0:
        raise ValueError("Minkowski parameter p must be >= 1.0.")
    return float(np.sum(np.abs(u - v) ** p) ** (1.0 / p))


def compute_pairwise_distances(X: np.ndarray, metric: str = "euclidean") -> np.ndarray:
    """Computes symmetric pairwise distance matrix for an N x D dataset."""
    N = X.shape[0]
    D = np.zeros((N, N), dtype=np.float64)

    for i in range(N):
        for j in range(i, N):
            if metric == "euclidean":
                dist = euclidean_distance(X[i], X[j])
            elif metric == "manhattan":
                dist = manhattan_distance(X[i], X[j])
            elif metric == "cosine":
                dist = 1.0 - cosine_similarity(X[i], X[j])
            else:
                raise ValueError(f"Unsupported metric: {metric}")
            D[i, j] = dist
            D[j, i] = dist
    return D


class KNNPatternMatcher:
    """Simple K-Nearest Neighbors retrieval engine using pairwise metrics."""

    def __init__(self, metric: str = "euclidean") -> None:
        self.metric = metric
        self.database: np.ndarray = np.empty((0, 0))
        self.item_ids: List[str] = []

    def fit(self, item_ids: List[str], features: np.ndarray) -> None:
        self.item_ids = item_ids
        self.database = features

    def query(self, query_vec: np.ndarray, k: int = 3) -> List[Tuple[str, float]]:
        """Returns top-k closest items with their distance scores."""
        if len(self.item_ids) == 0:
            raise ValueError("Matcher database is empty. Call fit() first.")

        distances: List[Tuple[str, float]] = []
        for item_id, feat in zip(self.item_ids, self.database):
            if self.metric == "euclidean":
                d = euclidean_distance(query_vec, feat)
            elif self.metric == "manhattan":
                d = manhattan_distance(query_vec, feat)
            elif self.metric == "cosine":
                d = 1.0 - cosine_similarity(query_vec, feat)
            else:
                d = euclidean_distance(query_vec, feat)
            distances.append((item_id, round(d, 4)))

        distances.sort(key=lambda x: x[1])
        return distances[:k]
