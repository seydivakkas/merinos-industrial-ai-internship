"""Day 08 - Exploratory Data Analysis (EDA) Toolkit for Industrial Data.

Computes descriptive statistics, IQR/Z-score outlier detection,
correlation matrices, histograms, and boxplot metrics for textile
manufacturing parameters.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class BoxplotSummary(BaseModel):
    """Five-number summary and IQR whisker bounds for boxplot analysis."""
    min_val: float
    q25: float
    median: float
    q75: float
    max_val: float
    iqr: float
    lower_whisker: float
    upper_whisker: float
    outlier_count: int


class ColumnSummary(BaseModel):
    """Statistical summary for a single numeric feature."""
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    skewness: float
    kurtosis: float
    outlier_count_iqr: int
    outlier_count_zscore: int


class EDAReport(BaseModel):
    """Full exploratory data analysis report."""
    row_count: int
    column_count: int
    columns: Dict[str, ColumnSummary]
    top_correlated_pairs: List[Tuple[str, str, float]]


class EDAToolkit:
    """Automates exploratory data analysis on manufacturing datasets."""

    def __init__(self, iqr_multiplier: float = 1.5, zscore_threshold: float = 3.0) -> None:
        self.iqr_multiplier = iqr_multiplier
        self.zscore_threshold = zscore_threshold

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
            outlier_count_iqr = int(((series < lower_bound) | (series > upper_bound)).sum())

            # Z-Score Outliers
            mean = float(series.mean())
            std = float(series.std()) if float(series.std()) > 1e-8 else 1.0
            zscores = np.abs((series - mean) / std)
            outlier_count_zscore = int((zscores > self.zscore_threshold).sum())

            skew = float(series.skew()) if len(series) > 2 else 0.0
            kurt = float(series.kurtosis()) if len(series) > 3 else 0.0

            cols_summary[col] = ColumnSummary(
                mean=round(mean, 4),
                std=round(std, 4),
                min=round(float(series.min()), 4),
                q25=round(q25, 4),
                median=round(float(series.median()), 4),
                q75=round(q75, 4),
                max=round(float(series.max()), 4),
                skewness=round(skew, 4),
                kurtosis=round(kurt, 4),
                outlier_count_iqr=outlier_count_iqr,
                outlier_count_zscore=outlier_count_zscore,
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
            top_correlated_pairs=correlated_pairs,
        )

    def compute_histogram(self, series: pd.Series, bins: int = 10) -> Dict[str, Any]:
        """Computes histogram bins and frequency counts."""
        cleaned = series.dropna().to_numpy()
        counts, bin_edges = np.histogram(cleaned, bins=bins)
        return {
            "bin_counts": counts.tolist(),
            "bin_edges": [round(float(b), 4) for b in bin_edges],
            "total_samples": len(cleaned),
        }

    def compute_boxplot_stats(self, series: pd.Series) -> BoxplotSummary:
        """Computes five-number summary and Tukey's whisker boundaries."""
        cleaned = series.dropna().to_numpy()
        q25, median, q75 = np.percentile(cleaned, [25, 50, 75])
        iqr = q75 - q25
        lower_whisker = float(np.min(cleaned[cleaned >= q25 - (self.iqr_multiplier * iqr)]))
        upper_whisker = float(np.max(cleaned[cleaned <= q75 + (self.iqr_multiplier * iqr)]))
        outliers = cleaned[(cleaned < lower_whisker) | (cleaned > upper_whisker)]

        return BoxplotSummary(
            min_val=round(float(np.min(cleaned)), 4),
            q25=round(float(q25), 4),
            median=round(float(median), 4),
            q75=round(float(q75), 4),
            max_val=round(float(np.max(cleaned)), 4),
            iqr=round(float(iqr), 4),
            lower_whisker=round(lower_whisker, 4),
            upper_whisker=round(upper_whisker, 4),
            outlier_count=len(outliers),
        )
