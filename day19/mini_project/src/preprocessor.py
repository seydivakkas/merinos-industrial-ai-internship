"""
Merinos Industrial AI Internship - Day 19
3-Way Stratified Data Preprocessing (Train / Validation / Test)
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class BoostingDataPreprocessor:
    """Prepares and partitions telemetry data into 3 stratified subsets for boosting."""

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_state: int = 42,
        target_column: str = "defect_class",
        feature_names: Optional[List[str]] = None,
        **kwargs
    ):
        if "val_size" in kwargs:
            val_ratio = kwargs["val_size"]
        if "test_size" in kwargs:
            test_ratio = kwargs["test_size"]
        if "train_size" in kwargs:
            train_ratio = kwargs["train_size"]
        elif "val_size" in kwargs or "test_size" in kwargs:
            train_ratio = round(1.0 - (val_ratio + test_ratio), 4)

        if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
            raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.0")

        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
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

    def split_3way(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Performs 3-way stratified partition:
        Returns: (X_train, y_train, X_val, y_val, X_test, y_test)
        """
        missing_cols = [col for col in self.feature_names if col not in df.columns]
        if missing_cols:
            raise ValueError(f"DataFrame is missing features: {missing_cols}")

        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found.")

        X = df[self.feature_names].to_numpy(dtype=np.float64)
        y = df[self.target_column].to_numpy(dtype=np.int64)

        # First split: separate test set (15%)
        temp_ratio = self.val_ratio + self.test_ratio
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=temp_ratio,
            random_state=self.random_state,
            stratify=y,
            shuffle=True
        )

        # Second split: separate val and test (50% each of the 30% temp set = 15% and 15% overall)
        val_share = self.val_ratio / temp_ratio
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=(1.0 - val_share),
            random_state=self.random_state,
            stratify=y_temp,
            shuffle=True
        )

        return X_train, y_train, X_val, y_val, X_test, y_test

    def split(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Partition returns: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        X_train, y_train, X_val, y_val, X_test, y_test = self.split_3way(df)
        return X_train, X_val, X_test, y_train, y_val, y_test

    def get_feature_names(self) -> List[str]:
        """Returns the list of feature names."""
        return list(self.feature_names)
