"""Data preprocessor for SVM defect classification featuring StandardScaler."""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class SVMDataPreprocessor:
    """Preprocesses carpet telemetry by applying stratified splitting and z-score standard scaling."""

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

    def __init__(self, test_size: float = 0.20, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.is_fitted = False

    def split_and_scale(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Performs stratified train/test split followed by strictly leak-free StandardScaler transformation.

        Returns:
            X_train_scaled, X_test_scaled, y_train, y_test
        """
        X = df[self.FEATURE_COLS].values
        y = df["defect_class"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.is_fitted = True

        return X_train_scaled, X_test_scaled, y_train, y_test

    def transform_sample(self, raw_sample: np.ndarray) -> np.ndarray:
        """Scales a single sample or batch for live real-time inference."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transforming samples.")
        if raw_sample.ndim == 1:
            raw_sample = raw_sample.reshape(1, -1)
        return self.scaler.transform(raw_sample)

    def get_feature_names(self) -> List[str]:
        """Returns the list of input telemetry feature names."""
        return list(self.FEATURE_COLS)
