"""Day 08 - Exploratory Data Analysis (EDA) Toolkit for Industrial Data.

Computes descriptive statistics, IQR/Z-score outlier detection,
correlation matrices, and distributions for textile manufacturing parameters.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class ColumnSummary(BaseModel):
    """Statistical summary for a single numeric feature."""
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    outlier_count_iqr: int


class EDAReport(BaseModel):
    """Full exploratory data analysis report."""
    row_count: int
    column_count: int
    columns: Dict[str, ColumnSummary]
    top_correlated_pairs: List[Tuple[str, str, float]]


class EDAToolkit:
    """Automates exploratory data analysis on manufacturing datasets."""

    def __init__(self, iqr_multiplier: float = 1.5) -> None:
        self.iqr_multiplier = iqr_multiplier

    def analyze(self, df: pd.DataFrame) -> EDAReport:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            raise ValueError("DataFrame contains no numerical columns for EDA.")

        cols_summary: Dict[str, ColumnSummary] = {}
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            iqr = q75 - q25
            lower_bound = q25 - (self.iqr_multiplier * iqr)
            upper_bound = q75 + (self.iqr_multiplier * iqr)

            outlier_count = int(((series < lower_bound) | (series > upper_bound)).sum())

            cols_summary[col] = ColumnSummary(
                mean=round(float(series.mean()), 4),
                std=round(float(series.std()), 4),
                min=round(float(series.min()), 4),
                q25=round(q25, 4),
                median=round(float(series.median()), 4),
                q75=round(q75, 4),
                max=round(float(series.max()), 4),
                outlier_count_iqr=outlier_count,
            )

        # Correlation analysis
        corr_matrix = numeric_df.corr().abs()
        correlated_pairs: List[Tuple[str, str, float]] = []
        cols = list(numeric_df.columns)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = float(corr_matrix.iloc[i, j])
                if not np.isnan(val):
                    correlated_pairs.append((cols[i], cols[j], round(val, 4)))

        correlated_pairs.sort(key=lambda x: x[2], reverse=True)

        return EDAReport(
            row_count=len(df),
            column_count=len(df.columns),
            columns=cols_summary,
            top_correlated_pairs=correlated_pairs[:5],
        )
