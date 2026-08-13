"""Preprocessor for unsupervised learning and feature normalization using StandardScaler."""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class UnsupervisedPreprocessor:
    """Normalizes industrial telemetry via z-score standardization for distance-based ML algorithms."""

    FEATURE_COLS = [
        "yarn_tensile_strength",
        "yarn_elongation_at_break",
        "yarn_hairiness_index",
        "twist_per_meter",
        "yarn_linear_density_dtex",
        "loom_rpm",
        "loom_tension_variation",
        "ambient_relative_humidity",
        "ambient_temperature_c",
        "weft_insertion_rate"
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Fits StandardScaler on feature matrix and returns scaled X, true labels, and anomaly mask.

        Returns:
            X_scaled, y_labels, is_anomaly_mask
        """
        X = df[self.FEATURE_COLS].values
        y = df["defect_class"].values
        is_anom = df["is_anomaly"].values.astype(bool)

        X_scaled = self.scaler.fit_transform(X)
        self.is_fitted = True

        return X_scaled, y, is_anom

    def transform_sample(self, raw_sample: np.ndarray) -> np.ndarray:
        """Scales a single sample or batch for live anomaly detection."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transforming samples.")
        if raw_sample.ndim == 1:
            raw_sample = raw_sample.reshape(1, -1)
        return self.scaler.transform(raw_sample)

    def get_feature_names(self) -> List[str]:
        """Returns the list of 10 feature names."""
        return list(self.FEATURE_COLS)
