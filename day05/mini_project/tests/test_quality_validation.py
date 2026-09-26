"""
Merinos Industrial AI Internship - Day 04
test_quality_validation.py: Automated Test Suite for Data Quality & Expectations Engine
"""

from pathlib import Path
import json
import pandas as pd
import pytest

from day05.mini_project.src.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnMeanToBeBetween,
    ExpectTableRowCountToBeBetween,
)
from day05.mini_project.src.suite import ExpectationSuite, SuiteValidator
from day05.mini_project.src.profiler import AutomatedDataProfiler
from day05.mini_project.src.quality_pipeline import DataQualityPipeline

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.read_csv(FIXTURES_DIR / "clean_production_data.csv")


@pytest.fixture
def dirty_df() -> pd.DataFrame:
    return pd.read_csv(FIXTURES_DIR / "dirty_production_data.csv")


@pytest.fixture
def drifted_df() -> pd.DataFrame:
    return pd.read_csv(FIXTURES_DIR / "drifted_production_data.csv")


@pytest.fixture
def suite_config_path() -> Path:
    return CONFIGS_DIR / "expectation_suite_config.json"


def test_expect_column_values_to_not_be_null(clean_df, dirty_df):
    exp = ExpectColumnValuesToNotBeNull(column="product_id", mostly=1.0)
    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert res_clean.result["unexpected_count"] == 0

    res_dirty = exp.validate(dirty_df)
    assert res_dirty.success is False
    assert res_dirty.result["unexpected_count"] > 0


def test_expect_column_values_to_be_unique(clean_df, dirty_df):
    exp = ExpectColumnValuesToBeUnique(column="product_id")
    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert res_clean.result["unexpected_count"] == 0

    res_dirty = exp.validate(dirty_df)
    assert res_dirty.success is False
    assert res_dirty.result["unexpected_count"] >= 2  # MRP-1001 duplicate


def test_expect_column_values_to_be_between(clean_df, dirty_df):
    exp = ExpectColumnValuesToBeBetween(column="width_cm", min_value=60.0, max_value=350.0)
    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert res_clean.result["unexpected_count"] == 0

    res_dirty = exp.validate(dirty_df)
    assert res_dirty.success is False
    assert res_dirty.result["unexpected_count"] >= 2  # 450.0 and -20.0


def test_expect_column_values_to_be_in_set(clean_df, dirty_df):
    allowed_materials = ["wool", "acrylic", "viscose", "bamboo", "polyester", "cotton"]
    exp = ExpectColumnValuesToBeInSet(column="material", allowed_set=allowed_materials)

    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert res_clean.result["unexpected_count"] == 0

    res_dirty = exp.validate(dirty_df)
    assert res_dirty.success is False
    assert "plastic" in res_dirty.result["partial_unexpected_list"] or "nylon_synthetic" in res_dirty.result["partial_unexpected_list"]


def test_expect_column_values_to_match_regex(clean_df, dirty_df):
    exp = ExpectColumnValuesToMatchRegex(column="product_id", regex=r"^MRP-[0-9]{4}$")
    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert res_clean.result["unexpected_count"] == 0

    res_dirty = exp.validate(dirty_df)
    assert res_dirty.success is False
    assert res_dirty.result["unexpected_count"] > 0


def test_expect_column_mean_to_be_between_and_drift_detection(clean_df, drifted_df):
    exp = ExpectColumnMeanToBeBetween(column="pile_height_mm", min_value=8.0, max_value=15.0)

    # Clean dataset mean should be ~11.5mm (within 8.0 - 15.0)
    res_clean = exp.validate(clean_df)
    assert res_clean.success is True
    assert 8.0 <= res_clean.result["observed_value"] <= 15.0

    # Drifted dataset mean is elevated (~18.5mm), detecting loom tension drift
    res_drifted = exp.validate(drifted_df)
    assert res_drifted.success is False
    assert res_drifted.result["observed_value"] > 15.0


def test_expect_table_row_count_to_be_between(clean_df):
    exp_pass = ExpectTableRowCountToBeBetween(min_value=10, max_value=100)
    assert exp_pass.validate(clean_df).success is True

    exp_fail_min = ExpectTableRowCountToBeBetween(min_value=50, max_value=100)
    assert exp_fail_min.validate(clean_df).success is False


def test_expectation_suite_from_json_and_validate_clean(suite_config_path, clean_df):
    suite = ExpectationSuite.from_json(suite_config_path)
    assert len(suite.expectations) == 15

    val_result = SuiteValidator.validate(clean_df, suite)
    assert val_result.success is True
    assert val_result.statistics["success_percent"] == 100.0
    assert val_result.statistics["unsuccessful_expectations"] == 0


def test_expectation_suite_detects_dirty_anomalies(suite_config_path, dirty_df):
    suite = ExpectationSuite.from_json(suite_config_path)
    val_result = SuiteValidator.validate(dirty_df, suite)

    assert val_result.success is False
    assert val_result.statistics["unsuccessful_expectations"] > 0
    assert val_result.statistics["success_percent"] < 100.0


def test_data_profiler_and_pipeline_artifacts(tmp_path, suite_config_path):
    pipeline = DataQualityPipeline(config_path=suite_config_path, output_dir=tmp_path)
    clean_csv = FIXTURES_DIR / "clean_production_data.csv"
    res = pipeline.run(clean_csv)

    assert res["summary"]["total_records"] == 20
    assert res["summary"]["anomalous_records_count"] == 0
    assert res["summary"]["composite_quality_score"] == 100.0
    assert res["summary"]["validation_success"] is True

    # Check files exist
    assert Path(res["validation_report_path"]).exists()
    assert Path(res["data_profile_path"]).exists()
    assert Path(res["dashboard_html_path"]).exists()
    assert Path(res["anomalous_records_path"]).exists()

    # Check dashboard contains HTML structure
    with open(res["dashboard_html_path"], "r", encoding="utf-8") as f:
        html_text = f.read()
    assert "<!DOCTYPE html>" in html_text
    assert "Merinos Endüstriyel Veri Kalitesi" in html_text
    assert "MRP-1001" in html_text or "expect_table_row_count_to_be_between" in html_text
