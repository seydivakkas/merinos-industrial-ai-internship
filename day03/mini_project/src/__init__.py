"""
day03.mini_project.src
Problem tanımlama, başarı ölçütü sözleşmesi, baseline değerlendirici ve veri hattı modülü.
"""

from day03.mini_project.src.normalizer import DataNormalizer
from day03.mini_project.src.parsers import CsvDataSourceParser, JsonDataSourceParser
from day03.mini_project.src.pipeline import DataIngestionPipeline
from day03.mini_project.src.problem_spec import (
    BaselineEvaluator,
    EvaluationComparison,
    ProblemSpecification,
)

__all__ = [
    "ProblemSpecification",
    "EvaluationComparison",
    "BaselineEvaluator",
    "DataIngestionPipeline",
    "DataNormalizer",
    "CsvDataSourceParser",
    "JsonDataSourceParser",
]
