"""
Merinos Industrial AI Internship - Day 04
expectations.py: Declarative Data Quality Expectations Engine
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
import numpy as np
import pandas as pd


@dataclass
class ExpectationResult:
    """Represents the outcome of validating a single expectation against a dataset."""
    expectation_type: str
    success: bool
    kwargs: Dict[str, Any]
    result: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expectation_type": self.expectation_type,
            "success": self.success,
            "kwargs": self.kwargs,
            "result": self.result,
        }


class BaseExpectation(ABC):
    """Abstract base class for all declarative data expectations."""

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        """Validate the expectation against the given pandas DataFrame."""
        pass

    @property
    def expectation_type(self) -> str:
        return self.__class__.__name__


class ExpectTableRowCountToBeBetween(BaseExpectation):
    """Expect total number of rows in the table to fall between min_value and max_value."""

    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        observed_rows = len(df)
        success = True

        if self.min_value is not None and observed_rows < self.min_value:
            success = False
        if self.max_value is not None and observed_rows > self.max_value:
            success = False

        return ExpectationResult(
            expectation_type="expect_table_row_count_to_be_between",
            success=success,
            kwargs={"min_value": self.min_value, "max_value": self.max_value},
            result={
                "observed_value": observed_rows,
                "element_count": observed_rows,
                "message": f"Observed {observed_rows} rows (Expected: [{self.min_value}, {self.max_value}])"
            }
        )


class ExpectColumnValuesToNotBeNull(BaseExpectation):
    """Expect column values to not be null, optionally satisfying a threshold ratio (mostly)."""

    def __init__(self, column: str, mostly: float = 1.0):
        self.column = column
        self.mostly = float(mostly)

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_values_to_not_be_null",
                success=False,
                kwargs={"column": self.column, "mostly": self.mostly},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        series = df[self.column]
        element_count = len(series)
        # Treat empty string as null if string type
        null_mask = series.isna() | (series.astype(str).str.strip() == "")
        missing_count = int(null_mask.sum())
        non_null_count = element_count - missing_count
        non_null_percent = (non_null_count / element_count) if element_count > 0 else 0.0

        unexpected_indices = df.index[null_mask].tolist()
        success = non_null_percent >= self.mostly

        return ExpectationResult(
            expectation_type="expect_column_values_to_not_be_null",
            success=success,
            kwargs={"column": self.column, "mostly": self.mostly},
            result={
                "element_count": element_count,
                "unexpected_count": missing_count,
                "unexpected_percent": round((missing_count / element_count) * 100, 2) if element_count > 0 else 0.0,
                "unexpected_index_list": unexpected_indices[:20],
                "partial_unexpected_list": [None] * min(missing_count, 5),
                "message": f"{non_null_count}/{element_count} ({non_null_percent * 100:.1f}%) non-null (threshold: {self.mostly * 100:.1f}%)"
            }
        )


class ExpectColumnValuesToBeUnique(BaseExpectation):
    """Expect all values in a column to be unique."""

    def __init__(self, column: str):
        self.column = column

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_values_to_be_unique",
                success=False,
                kwargs={"column": self.column},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        series = df[self.column].dropna()
        element_count = len(series)
        duplicate_mask = series.duplicated(keep=False)
        duplicate_count = int(duplicate_mask.sum())
        unexpected_indices = series.index[duplicate_mask].tolist()
        duplicates_sample = series[duplicate_mask].head(10).tolist()

        success = duplicate_count == 0

        return ExpectationResult(
            expectation_type="expect_column_values_to_be_unique",
            success=success,
            kwargs={"column": self.column},
            result={
                "element_count": element_count,
                "unexpected_count": duplicate_count,
                "unexpected_percent": round((duplicate_count / element_count) * 100, 2) if element_count > 0 else 0.0,
                "unexpected_index_list": unexpected_indices[:20],
                "partial_unexpected_list": duplicates_sample,
                "message": f"Found {duplicate_count} duplicate values in '{self.column}'."
            }
        )


class ExpectColumnValuesToBeBetween(BaseExpectation):
    """Expect numeric values in a column to fall within [min_value, max_value]."""

    def __init__(self, column: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.column = column
        self.min_value = float(min_value) if min_value is not None else None
        self.max_value = float(max_value) if max_value is not None else None

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_values_to_be_between",
                success=False,
                kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        # Convert to numeric safely
        numeric_series = pd.to_numeric(df[self.column], errors="coerce")
        valid_mask = ~numeric_series.isna()
        element_count = int(valid_mask.sum())

        if element_count == 0:
            return ExpectationResult(
                expectation_type="expect_column_values_to_be_between",
                success=False,
                kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
                result={"message": f"No valid numeric data in column '{self.column}'."}
            )

        out_of_bounds_mask = pd.Series(False, index=df.index)
        if self.min_value is not None:
            out_of_bounds_mask |= (numeric_series < self.min_value)
        if self.max_value is not None:
            out_of_bounds_mask |= (numeric_series > self.max_value)

        # Only consider valid numeric records for boundary check
        unexpected_mask = out_of_bounds_mask & valid_mask
        unexpected_count = int(unexpected_mask.sum())
        unexpected_indices = df.index[unexpected_mask].tolist()
        unexpected_sample = numeric_series[unexpected_mask].head(10).tolist()

        success = unexpected_count == 0

        return ExpectationResult(
            expectation_type="expect_column_values_to_be_between",
            success=success,
            kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
            result={
                "element_count": element_count,
                "unexpected_count": unexpected_count,
                "unexpected_percent": round((unexpected_count / element_count) * 100, 2) if element_count > 0 else 0.0,
                "unexpected_index_list": unexpected_indices[:20],
                "partial_unexpected_list": unexpected_sample,
                "observed_min": float(numeric_series.min()) if element_count > 0 else None,
                "observed_max": float(numeric_series.max()) if element_count > 0 else None,
                "message": f"{unexpected_count} out-of-spec values found outside [{self.min_value}, {self.max_value}]."
            }
        )


class ExpectColumnValuesToBeInSet(BaseExpectation):
    """Expect column values to belong to an explicitly permitted set."""

    def __init__(self, column: str, allowed_set: List[Any]):
        self.column = column
        self.allowed_set = list(allowed_set)

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_values_to_be_in_set",
                success=False,
                kwargs={"column": self.column, "allowed_set": self.allowed_set},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        series = df[self.column].dropna()
        element_count = len(series)
        unexpected_mask = ~series.isin(self.allowed_set)
        unexpected_count = int(unexpected_mask.sum())
        unexpected_indices = series.index[unexpected_mask].tolist()
        unexpected_sample = series[unexpected_mask].head(10).tolist()

        success = unexpected_count == 0

        return ExpectationResult(
            expectation_type="expect_column_values_to_be_in_set",
            success=success,
            kwargs={"column": self.column, "allowed_set": self.allowed_set},
            result={
                "element_count": element_count,
                "unexpected_count": unexpected_count,
                "unexpected_percent": round((unexpected_count / element_count) * 100, 2) if element_count > 0 else 0.0,
                "unexpected_index_list": unexpected_indices[:20],
                "partial_unexpected_list": unexpected_sample,
                "message": f"{unexpected_count} invalid categorical values found not in allowed set."
            }
        )


class ExpectColumnValuesToMatchRegex(BaseExpectation):
    """Expect string values in a column to match a specified regular expression."""

    def __init__(self, column: str, regex: str):
        self.column = column
        self.regex = regex
        self._compiled_regex = re.compile(regex)

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_values_to_match_regex",
                success=False,
                kwargs={"column": self.column, "regex": self.regex},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        series = df[self.column].dropna().astype(str)
        element_count = len(series)
        
        matches = series.apply(lambda val: bool(self._compiled_regex.match(str(val))))
        unexpected_mask = ~matches
        unexpected_count = int(unexpected_mask.sum())
        unexpected_indices = series.index[unexpected_mask].tolist()
        unexpected_sample = series[unexpected_mask].head(10).tolist()

        success = unexpected_count == 0

        return ExpectationResult(
            expectation_type="expect_column_values_to_match_regex",
            success=success,
            kwargs={"column": self.column, "regex": self.regex},
            result={
                "element_count": element_count,
                "unexpected_count": unexpected_count,
                "unexpected_percent": round((unexpected_count / element_count) * 100, 2) if element_count > 0 else 0.0,
                "unexpected_index_list": unexpected_indices[:20],
                "partial_unexpected_list": unexpected_sample,
                "message": f"{unexpected_count} string values do not conform to regex pattern '{self.regex}'."
            }
        )


class ExpectColumnMeanToBeBetween(BaseExpectation):
    """Expect column arithmetic mean to fall within [min_value, max_value] (Statistical Drift)."""

    def __init__(self, column: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.column = column
        self.min_value = float(min_value) if min_value is not None else None
        self.max_value = float(max_value) if max_value is not None else None

    def validate(self, df: pd.DataFrame) -> ExpectationResult:
        if self.column not in df.columns:
            return ExpectationResult(
                expectation_type="expect_column_mean_to_be_between",
                success=False,
                kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
                result={"message": f"Column '{self.column}' does not exist in DataFrame."}
            )

        numeric_series = pd.to_numeric(df[self.column], errors="coerce").dropna()
        if len(numeric_series) == 0:
            return ExpectationResult(
                expectation_type="expect_column_mean_to_be_between",
                success=False,
                kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
                result={"message": f"No valid numeric data in column '{self.column}' to compute mean."}
            )

        observed_mean = float(numeric_series.mean())
        success = True
        if self.min_value is not None and observed_mean < self.min_value:
            success = False
        if self.max_value is not None and observed_mean > self.max_value:
            success = False

        return ExpectationResult(
            expectation_type="expect_column_mean_to_be_between",
            success=success,
            kwargs={"column": self.column, "min_value": self.min_value, "max_value": self.max_value},
            result={
                "observed_value": round(observed_mean, 3),
                "element_count": len(numeric_series),
                "message": f"Observed mean={observed_mean:.3f} (Expected range: [{self.min_value}, {self.max_value}])"
            }
        )


EXPECTATION_REGISTRY = {
    "expect_table_row_count_to_be_between": ExpectTableRowCountToBeBetween,
    "expect_column_values_to_not_be_null": ExpectColumnValuesToNotBeNull,
    "expect_column_values_to_be_unique": ExpectColumnValuesToBeUnique,
    "expect_column_values_to_be_between": ExpectColumnValuesToBeBetween,
    "expect_column_values_to_be_in_set": ExpectColumnValuesToBeInSet,
    "expect_column_values_to_match_regex": ExpectColumnValuesToMatchRegex,
    "expect_column_mean_to_be_between": ExpectColumnMeanToBeBetween,
}


def create_expectation(expectation_type: str, kwargs: Dict[str, Any]) -> BaseExpectation:
    """Factory method to instantiate an expectation from its type and keyword arguments."""
    if expectation_type not in EXPECTATION_REGISTRY:
        raise ValueError(f"Unknown expectation type: '{expectation_type}'. Available: {list(EXPECTATION_REGISTRY.keys())}")
    cls = EXPECTATION_REGISTRY[expectation_type]
    return cls(**kwargs)
