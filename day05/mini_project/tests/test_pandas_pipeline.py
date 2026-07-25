"""Unit tests for Day 05 Pandas Data Pipeline and Data Quality."""

import numpy as np
import pandas as pd
import pytest
from day05.mini_project.src.pandas_pipeline import PandasDataPipeline


@pytest.fixture
def sample_telemetry_df() -> pd.DataFrame:
    return pd.DataFrame({
        "loom_id": ["L1", "L2", "L3", "L4", "L5"],
        "temp_c": [75.0, 82.0, np.nan, 130.0, 80.0],  # 130.0 is out of valid range (10-120)
        "pressure_bar": [14.0, 15.5, 13.8, 14.2, np.nan],
        "rpm": [800, 820, 810, 850, 790]
    })


def test_pandas_pipeline_cleaning_and_quarantine(sample_telemetry_df: pd.DataFrame):
    pipeline = PandasDataPipeline()
    valid_df, quarantine_df, report = pipeline.clean_and_profile(
        df=sample_telemetry_df,
        required_columns=["loom_id", "rpm"],
        valid_ranges={"temp_c": (10.0, 120.0), "pressure_bar": (5.0, 25.0)}
    )

    # L4 has temp=130 (out of bounds) -> quarantined
    # L3 has temp=NaN, pressure=13.8 -> quarantined because of valid_ranges check
    # L5 has pressure=NaN -> quarantined
    # L1, L2 valid
    assert len(valid_df) == 2
    assert len(quarantine_df) == 3
    assert report.total_rows == 5
    assert report.completeness_score_pct < 100.0
