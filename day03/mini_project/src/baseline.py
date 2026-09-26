"""Day 03 - Baseline Heuristics and Empirical Evaluators.

Provides simple, rule-based baseline implementations (majority class,
mean numerical threshold, random choice) to establish minimum performance
baselines before applying complex ML or CV models.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, List, Sequence
import numpy as np


class MajorityClassBaseline:
    """A baseline classifier that always predicts the most frequent training class."""

    def __init__(self) -> None:
        self.majority_class: Any = None

    def fit(self, y: Sequence[Any]) -> MajorityClassBaseline:
        """Fit by determining the mode of the training targets."""
        if len(y) == 0:
            raise ValueError("Training targets cannot be empty.")
        counts = Counter(y)
        self.majority_class = counts.most_common(1)[0][0]
        return self

    def predict(self, n_samples: int) -> List[Any]:
        """Predict the majority class for n_samples."""
        if self.majority_class is None:
            raise RuntimeError("Baseline has not been fitted yet.")
        return [self.majority_class] * n_samples


class MeanThresholdBaseline:
    """A baseline classifier for binary detection based on mean numerical threshold."""

    def __init__(self, threshold_margin: float = 1.0) -> None:
        self.threshold_margin = threshold_margin
        self.mean_value: float = 0.0

    def fit(self, values: Sequence[float]) -> MeanThresholdBaseline:
        """Calculate mean threshold from normal telemetry values."""
        if len(values) == 0:
            raise ValueError("Values cannot be empty.")
        self.mean_value = float(np.mean(values))
        return self

    def predict(self, values: Sequence[float]) -> List[int]:
        """Predict 1 (anomaly) if value deviates from mean by margin, else 0."""
        cutoff = self.mean_value * self.threshold_margin
        return [1 if v > cutoff else 0 for v in values]
