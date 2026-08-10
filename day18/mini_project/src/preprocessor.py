"""
Merinos Industrial AI Internship - Day 18
Data Preprocessing and Stratified Partitioning for Tree and Ensemble Models
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class TreeDataPreprocessor:
    """Prepares and partitions industrial telemetry datasets for tree-based estimators."""

    def __init__(
        self,
        test_size: float = 0.20,
        random_state: int = 42,
        target_column: str = "defect_class",
        feature_names: Optional[List[str]] = None
    ):
        self.test_size = test_size
        self.random_state = random_state
        self.target_column = target_column
        self.feature_names = feature_names or [
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

    def split(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Executes stratified train/test partitioning preserving multiclass defect proportions.
        Returns: (X_train, X_test, y_train, y_test)
        """
        missing_cols = [col for col in self.feature_names if col not in df.columns]
        if missing_cols:
            raise ValueError(f"DataFrame is missing required features: {missing_cols}")

        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in DataFrame.")

        X = df[self.feature_names].to_numpy(dtype=np.float64)
        y = df[self.target_column].to_numpy(dtype=np.int64)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y,
            shuffle=True
        )

        return X_train, X_test, y_train, y_test

    def get_feature_names(self) -> List[str]:
        """Returns the list of engineered feature names."""
        return list(self.feature_names)
