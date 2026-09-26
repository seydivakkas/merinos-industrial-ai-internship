"""
Merinos Industrial AI Internship - Day 04
suite.py: ExpectationSuite and SuiteValidator Engine
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import pandas as pd

from day05.mini_project.src.expectations import (
    BaseExpectation,
    ExpectationResult,
    create_expectation,
)


@dataclass
class ValidationResult:
    """Comprehensive validation result encompassing all executed expectations in a suite."""
    suite_name: str
    success: bool
    statistics: Dict[str, Any]
    results: List[ExpectationResult]
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "success": self.success,
            "statistics": self.statistics,
            "results": [r.to_dict() for r in self.results],
            "meta": self.meta,
        }


class ExpectationSuite:
    """A declarative collection of expectations that define data quality contracts."""

    def __init__(
        self,
        suite_name: str = "default_suite",
        expectations: Optional[List[BaseExpectation]] = None,
        description: str = "",
        version: str = "1.0.0"
    ):
        self.suite_name = suite_name
        self.expectations = expectations or []
        self.description = description
        self.version = version

    def add_expectation(self, expectation: BaseExpectation) -> "ExpectationSuite":
        self.expectations.append(expectation)
        return self

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpectationSuite":
        suite_name = data.get("suite_name", "unnamed_suite")
        description = data.get("description", "")
        version = data.get("version", "1.0.0")

        suite = cls(suite_name=suite_name, description=description, version=version)
        for exp_dict in data.get("expectations", []):
            exp_type = exp_dict.get("expectation_type")
            kwargs = exp_dict.get("kwargs", {})
            expectation = create_expectation(exp_type, kwargs)
            suite.add_expectation(expectation)

        return suite

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> "ExpectationSuite":
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "version": self.version,
            "description": self.description,
            "expectations": [
                {
                    "expectation_type": exp.expectation_type,
                    "kwargs": getattr(exp, "__dict__", {})
                }
                for exp in self.expectations
            ]
        }


class SuiteValidator:
    """Executes an ExpectationSuite on target pandas DataFrames."""

    @staticmethod
    def validate(df: pd.DataFrame, suite: ExpectationSuite) -> ValidationResult:
        results: List[ExpectationResult] = []
        successful_count = 0

        for expectation in suite.expectations:
            res = expectation.validate(df)
            results.append(res)
            if res.success:
                successful_count += 1

        total_evaluated = len(results)
        unsuccessful_count = total_evaluated - successful_count
        success_percent = (successful_count / total_evaluated * 100.0) if total_evaluated > 0 else 100.0
        overall_success = unsuccessful_count == 0

        statistics = {
            "evaluated_expectations": total_evaluated,
            "successful_expectations": successful_count,
            "unsuccessful_expectations": unsuccessful_count,
            "success_percent": round(success_percent, 2),
        }

        return ValidationResult(
            suite_name=suite.suite_name,
            success=overall_success,
            statistics=statistics,
            results=results,
            meta={"dataset_rows": len(df), "dataset_columns": len(df.columns)}
        )
