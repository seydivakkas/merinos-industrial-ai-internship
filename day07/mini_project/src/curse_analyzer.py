"""
Merinos Industrial AI Internship - Day 06
curse_analyzer.py: Curse of Dimensionality and Distance Concentration Analyzer
"""

from typing import Any, Dict, List, Optional
import numpy as np

from day07.mini_project.src.metrics import pairwise_euclidean, pairwise_manhattan, pairwise_cosine_distance


class CurseOfDimensionalityAnalyzer:
    """Analyzes distance concentration and contrast decay in high-dimensional vector spaces."""

    @staticmethod
    def evaluate_dimension(
        dim: int,
        n_samples: int = 500,
        metric: str = "euclidean",
        seed: int = 42,
    ) -> Dict[str, Any]:
        rng = np.random.default_rng(seed)
        # Uniform random points in [-1, 1]^D
        X = rng.uniform(-1.0, 1.0, size=(n_samples, dim)).astype(np.float32)

        if metric == "euclidean":
            dists = pairwise_euclidean(X)
        elif metric == "manhattan":
            dists = pairwise_manhattan(X)
        elif metric == "cosine":
            dists = pairwise_cosine_distance(X)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        # Mask out diagonal (self-distances = 0)
        np.fill_diagonal(dists, np.nan)
        flat_dists = dists[~np.isnan(dists)]

        d_min = float(np.min(flat_dists))
        d_max = float(np.max(flat_dists))
        d_mean = float(np.mean(flat_dists))
        d_std = float(np.std(flat_dists))

        # Relative contrast: (D_max - D_min) / D_min
        contrast = float((d_max - d_min) / max(d_min, 1e-9))
        # Variance to mean ratio: Var / Mean
        var_to_mean = float((d_std ** 2) / max(d_mean, 1e-9))

        return {
            "dimension": int(dim),
            "n_samples": int(n_samples),
            "metric": metric,
            "min_distance": round(d_min, 4),
            "max_distance": round(d_max, 4),
            "mean_distance": round(d_mean, 4),
            "std_distance": round(d_std, 4),
            "relative_contrast": round(contrast, 4),
            "var_to_mean_ratio": round(var_to_mean, 4),
        }

    @classmethod
    def run_multi_dimensional_analysis(
        cls,
        dimensions: Optional[List[int]] = None,
        n_samples: int = 500,
        metric: str = "euclidean",
        seed: int = 42,
    ) -> Dict[str, Any]:
        dims = dimensions or [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        reports = []

        for d in dims:
            rep = cls.evaluate_dimension(d, n_samples=n_samples, metric=metric, seed=seed)
            reports.append(rep)

        first_contrast = reports[0]["relative_contrast"]
        last_contrast = reports[-1]["relative_contrast"]
        decay_ratio = round(first_contrast / max(last_contrast, 1e-6), 2)

        return {
            "metric": metric,
            "dimensions_tested": dims,
            "sample_size": n_samples,
            "contrast_decay_ratio": decay_ratio,
            "results": reports,
            "theoretical_insight": (
                f"As dimension D increases from {dims[0]} to {dims[-1]}, relative contrast (D_max - D_min)/D_min "
                f"decreases by {decay_ratio}x. In high-dimensional spaces, points become nearly equidistant, "
                "making metric selection (e.g. Cosine on normalized manifolds) and dimensionality reduction essential."
            )
        }
