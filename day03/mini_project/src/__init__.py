"""Day 03 - Mini Project: Problem Specification, Baselines, and Success Metrics.

Defines formal problem contracts, baseline heuristics (majority class, thresholding),
and empirical evaluation utilities.
"""

from day03.mini_project.src.baseline import (
    MajorityClassBaseline,
    MeanThresholdBaseline,
)
from day03.mini_project.src.problem_spec import (
    BaselineEvaluator,
    EvaluationComparison,
    ProblemSpecification,
)

__all__ = [
    "ProblemSpecification",
    "EvaluationComparison",
    "BaselineEvaluator",
    "MajorityClassBaseline",
    "MeanThresholdBaseline",
]
