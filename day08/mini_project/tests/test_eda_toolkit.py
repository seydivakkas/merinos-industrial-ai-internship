"""Unit tests for Day 08 EDA Toolkit (Outliers, Correlation, Histograms, Boxplots)."""

import numpy as np
import pandas as pd
import pytest
from day08.mini_project.src.eda_toolkit import EDAToolkit


@pytest.fixture
def sample_telemetry_df():
    # 20 samples with 1 strong outlier in temperature
    rng = np.random.default_rng(42)
    temps = rng.normal(70.0, 2.0, size=20).tolist()
    temps[5] = 135.0  # Obvious extreme outlier
    pressures = rng.normal(15.0, 0.5, size=20).tolist()
    rpms = [t * 10 + rng.normal(0, 1) for t in temps]  # Strongly correlated with temp

    return pd.DataFrame({
        "temperature": temps,
        "pressure": pressures,
        "rpm": rpms,
    })


def test_eda_toolkit_analysis(sample_telemetry_df):
    toolkit = EDAToolkit(iqr_multiplier=1.5, zscore_threshold=3.0)
    report = toolkit.analyze(sample_telemetry_df)

    assert report.row_count == 20
    assert report.column_count == 3
    assert "temperature" in report.columns
    assert report.columns["temperature"].outlier_count_iqr >= 1
    assert report.columns["temperature"].outlier_count_zscore >= 1

    # Check correlation: temperature and rpm must be top correlated
    assert len(report.top_correlated_pairs) > 0
    top_pair = report.top_correlated_pairs[0]
    assert "temperature" in (top_pair[0], top_pair[1])
    assert "rpm" in (top_pair[0], top_pair[1])
    assert top_pair[2] > 0.85  # Strong correlation


def test_eda_histogram_computation(sample_telemetry_df):
    toolkit = EDAToolkit()
    hist = toolkit.compute_histogram(sample_telemetry_df["pressure"], bins=5)
    assert len(hist["bin_counts"]) == 5
    assert len(hist["bin_edges"]) == 6
    assert sum(hist["bin_counts"]) == 20


def test_eda_boxplot_stats(sample_telemetry_df):
    toolkit = EDAToolkit()
    bp = toolkit.compute_boxplot_stats(sample_telemetry_df["temperature"])
    assert bp.q25 < bp.median < bp.q75
    assert bp.iqr > 0.0
    assert bp.lower_whisker <= bp.q25
    assert bp.upper_whisker >= bp.q75
    assert bp.outlier_count >= 1


def test_eda_toolkit_error_on_non_numeric():
    toolkit = EDAToolkit()
    df = pd.DataFrame({"text_only": ["warp", "weft", "pile"]})
    with pytest.raises(ValueError, match="no numerical columns"):
        toolkit.analyze(df)
