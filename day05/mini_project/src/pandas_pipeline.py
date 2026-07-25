"""Day 05 - Pandas Data Pipeline and Data Quality Framework.

Provides automated cleaning, imputation, transformation, and quality metric
computation (completeness, validity, consistency) for industrial manufacturing datasets.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class DataQualityReport(BaseModel):
    """Summarizes completeness, validity, and consistency of an industrial dataset."""
    total_rows: int
    total_columns: int
    completeness_score_pct: float
    validity_score_pct: float
    quarantine_row_count: int
    missing_values_by_column: Dict[str, int]
    quality_verdict: str


class PandasDataPipeline:
    """End-to-end Pandas data processing and quality enforcement pipeline."""

    def __init__(self, numeric_fill_strategy: str = "median") -> None:
        self.numeric_fill_strategy = numeric_fill_strategy

    def clean_and_profile(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        valid_ranges: Dict[str, Tuple[float, float]],
    ) -> Tuple[pd.DataFrame, pd.DataFrame, DataQualityReport]:
        """Cleans input dataframe, separates quarantine records, and computes quality scores."""
        total_rows = len(df)
        if total_rows == 0:
            raise ValueError("Input DataFrame cannot be empty.")

        # 1. Missing values check
        missing_counts = df.isnull().sum().to_dict()
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness = round(((total_cells - missing_cells) / total_cells) * 100.0, 2)

        # 2. Validity check against bounds
        validity_mask = pd.Series(True, index=df.index)
        for col in required_columns:
            if col in df.columns:
                validity_mask &= df[col].notnull()
            else:
                validity_mask &= False

        for col, (min_v, max_v) in valid_ranges.items():
            if col in df.columns:
                validity_mask &= (df[col] >= min_v) & (df[col] <= max_v)

        valid_df = df[validity_mask].copy()
        quarantine_df = df[~validity_mask].copy()

        validity_score = round((len(valid_df) / total_rows) * 100.0, 2)

        # 3. Imputation for clean records with minor missing fields
        for col in valid_df.select_dtypes(include=[np.number]).columns:
            if valid_df[col].isnull().any():
                if self.numeric_fill_strategy == "median":
                    fill_val = valid_df[col].median()
                else:
                    fill_val = valid_df[col].mean()
                valid_df[col] = valid_df[col].fillna(fill_val)

        verdict = "PASSED" if validity_score >= 80.0 and completeness >= 90.0 else "WARNING"

        report = DataQualityReport(
            total_rows=total_rows,
            total_columns=len(df.columns),
            completeness_score_pct=completeness,
            validity_score_pct=validity_score,
            quarantine_row_count=len(quarantine_df),
            missing_values_by_column={k: int(v) for k, v in missing_counts.items()},
            quality_verdict=verdict,
        )
        return valid_df, quarantine_df, report
