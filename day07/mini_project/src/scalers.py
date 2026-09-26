"""
Merinos Industrial AI Internship - Day 06
scalers.py: Feature Scalers and Normalization Transformers
"""

from typing import Optional
import numpy as np


class StandardScaler:
    """Standardizes features by removing the mean and scaling to unit variance (Z-score)."""

    def __init__(self, eps: float = 1e-8):
        self.eps = eps
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "StandardScaler":
        self.mean_ = np.mean(X, axis=0, keepdims=True)
        self.std_ = np.std(X, axis=0, keepdims=True)
        self.std_ = np.where(self.std_ == 0.0, self.eps, self.std_)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("StandardScaler must be fitted before transforming.")
        return ((X - self.mean_) / self.std_).astype(np.float32)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class MinMaxScaler:
    """Transforms features by scaling each feature to a given range [feature_range[0], feature_range[1]]."""

    def __init__(self, feature_range: tuple = (0.0, 1.0), eps: float = 1e-8):
        self.feature_range = feature_range
        self.eps = eps
        self.data_min_: Optional[np.ndarray] = None
        self.data_max_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "MinMaxScaler":
        self.data_min_ = np.min(X, axis=0, keepdims=True)
        self.data_max_ = np.max(X, axis=0, keepdims=True)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.data_min_ is None or self.data_max_ is None:
            raise RuntimeError("MinMaxScaler must be fitted before transforming.")
        diff = self.data_max_ - self.data_min_
        diff = np.where(diff == 0.0, self.eps, diff)
        scale = self.feature_range[1] - self.feature_range[0]
        norm = (X - self.data_min_) / diff
        return (norm * scale + self.feature_range[0]).astype(np.float32)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class L2Normalizer:
    """Scales individual samples to have unit L2 norm (||x||_2 = 1.0)."""

    @staticmethod
    def transform(X: np.ndarray, eps: float = 1e-9) -> np.ndarray:
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms = np.where(norms == 0.0, eps, norms)
        return (X / norms).astype(np.float32)

    @classmethod
    def fit_transform(cls, X: np.ndarray) -> np.ndarray:
        return cls.transform(X)
