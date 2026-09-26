"""
Merinos Industrial AI Internship - Day 06
metrics.py: High-Performance Vectorized Vector Similarity & Distance Metrics
"""

from typing import Optional
import numpy as np


# ---------------------------------------------------------------------------
# 1. Single Vector Pair Metrics
# ---------------------------------------------------------------------------
def euclidean_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Calculates Euclidean (L2) distance between vectors u and v."""
    diff = u - v
    return float(np.sqrt(np.dot(diff, diff)))


def manhattan_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Calculates Manhattan (L1 / Taxicab) distance between vectors u and v."""
    return float(np.sum(np.abs(u - v)))


def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    """
    Calculates Cosine similarity between vectors u and v: S_C = (u . v) / (||u|| * ||v||).
    Range: [-1.0, 1.0].
    """
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    if norm_u == 0.0 or norm_v == 0.0:
        return 0.0
    cos_sim = float(np.dot(u, v) / (norm_u * norm_v))
    # Clip to prevent floating point inaccuracies beyond [-1.0, 1.0]
    return float(np.clip(cos_sim, -1.0, 1.0))


def cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Calculates Cosine distance: d_C = 1.0 - S_C. Range: [0.0, 2.0]."""
    return 1.0 - cosine_similarity(u, v)


def mahalanobis_distance(u: np.ndarray, v: np.ndarray, cov_inv: np.ndarray) -> float:
    """
    Calculates Mahalanobis distance accounting for feature correlation:
    d_M = sqrt((u - v)^T * Sigma^{-1} * (u - v)).
    """
    diff = u - v
    dist_sq = float(np.dot(diff, np.dot(cov_inv, diff)))
    # Numerical guard against tiny negative values due to float inaccuracies
    return float(np.sqrt(max(0.0, dist_sq)))


def minkowski_distance(u: np.ndarray, v: np.ndarray, p: float = 3.0) -> float:
    """Calculates generalized Minkowski (L_p) distance: d_p = (sum |u_i - v_i|^p)^(1/p)."""
    if p <= 0:
        raise ValueError(f"Minkowski parameter p must be > 0, got {p}")
    return float(np.sum(np.abs(u - v) ** p) ** (1.0 / p))


# ---------------------------------------------------------------------------
# 2. Pairwise Matrix Metrics (Vectorized Batch Computations)
# ---------------------------------------------------------------------------
def pairwise_euclidean(X: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes pairwise Euclidean distances between rows of X (N, D) and Y (M, D).
    If Y is None, computes pairwise distances within X (N, N).
    Formula: ||x - y||^2 = ||x||^2 + ||y||^2 - 2 * x . y^T
    """
    if Y is None:
        Y = X

    x_sq = np.sum(X ** 2, axis=1, keepdims=True)  # (N, 1)
    y_sq = np.sum(Y ** 2, axis=1, keepdims=True).T  # (1, M)
    dot_prod = np.matmul(X, Y.T)  # (N, M)

    dist_sq = x_sq + y_sq - 2.0 * dot_prod
    dist_sq = np.maximum(dist_sq, 0.0)  # Numerical safety against negative values
    return np.sqrt(dist_sq).astype(np.float32)


def pairwise_manhattan(X: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes pairwise Manhattan (L1) distances between rows of X (N, D) and Y (M, D).
    Uses broadcasting: |X[:, None, :] - Y[None, :, :]|.sum(axis=-1).
    """
    if Y is None:
        Y = X
    return np.sum(np.abs(X[:, None, :] - Y[None, :, :]), axis=-1, dtype=np.float32)


def pairwise_cosine_similarity(X: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes pairwise Cosine similarity between rows of X (N, D) and Y (M, D).
    S_C = (X_norm . Y_norm^T).
    """
    if Y is None:
        Y = X

    norm_x = np.linalg.norm(X, axis=1, keepdims=True)
    norm_y = np.linalg.norm(Y, axis=1, keepdims=True)

    norm_x = np.where(norm_x == 0, 1e-9, norm_x)
    norm_y = np.where(norm_y == 0, 1e-9, norm_y)

    x_unit = X / norm_x
    y_unit = Y / norm_y

    sim = np.matmul(x_unit, y_unit.T)
    return np.clip(sim, -1.0, 1.0).astype(np.float32)


def pairwise_cosine_distance(X: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
    """Computes pairwise Cosine distances: 1.0 - S_C."""
    return (1.0 - pairwise_cosine_similarity(X, Y)).astype(np.float32)


def pairwise_mahalanobis(
    X: np.ndarray,
    Y: Optional[np.ndarray] = None,
    cov_inv: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Computes pairwise Mahalanobis distances between rows of X (N, D) and Y (M, D).
    If cov_inv is None, empirical covariance inverse of X is estimated.
    """
    if Y is None:
        Y = X

    if cov_inv is None:
        cov = np.cov(X, rowvar=False)
        # Add regularization to avoid singular covariance matrix
        reg = np.eye(cov.shape[0]) * 1e-6
        cov_inv = np.linalg.pinv(cov + reg)

    # Transform coordinates: X_prime = X . L where cov_inv = L . L^T
    # Or pairwise difference matrix
    n, d = X.shape
    m, _ = Y.shape
    out = np.zeros((n, m), dtype=np.float32)

    for i in range(n):
        diff = Y - X[i]  # (M, D)
        # (M, D) * (D, D) -> (M, D)
        m_dist_sq = np.sum(np.matmul(diff, cov_inv) * diff, axis=1)
        out[i] = np.sqrt(np.maximum(m_dist_sq, 0.0))

    return out
