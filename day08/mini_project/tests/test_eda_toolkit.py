"""Unit tests for Day 08 EDA Toolkit."""

import numpy as np
import pandas as pd
import pytest
from day08.mini_project.src.eda_toolkit import EDAToolkit


def test_eda_toolkit_analysis():
    toolkit = EDAToolkit()
    df = pd.DataFrame({
        "temperature": [70, 72, 71, 73, 72, 70, 150],  # 150 is an extreme outlier
        "pressure": [14.0, 14.2, 14.1, 14.3, 14.2, 14.1, 14.2],
        "rpm": [800, 810, 805, 815, 808, 802, 804],
    })

    report = toolkit.analyze(df)
    assert report.row_count == 7
    assert report.column_count == 3
    assert report.columns["temperature"].outlier_count_iqr >= 1
    assert len(report.top_correlated_pairs) > 0


def test_eda_toolkit_error_on_non_numeric():
    toolkit = EDAToolkit()
    df = pd.DataFrame({"text_only": ["a", "b", "c"]})
    with pytest.raises(ValueError):
        toolkit.analyze(df)
