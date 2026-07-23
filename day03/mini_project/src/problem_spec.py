"""Day 03 - Problem Specification, Baseline Evaluation, and Success Metrics.

Defines schemas and evaluators for formulating industrial computer engineering
problems, setting baseline thresholds, and measuring empirical gain over baselines.
"""

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class ProblemSpecification(BaseModel):
    """Formal specification of a computer engineering problem in manufacturing."""
    problem_id: str = Field(..., description="Unique problem identifier (e.g. PROB-SIM-01)")
    name: str = Field(..., description="Problem title (e.g. Carpet Visual Similarity)")
    input_contract: Dict[str, str] = Field(..., description="Expected inputs and their data types")
    output_contract: Dict[str, str] = Field(..., description="Expected outputs and their data types")
    target_metric: str = Field(..., description="Primary optimization metric (e.g. Accuracy, Top-1 Precision)")
    baseline_threshold: float = Field(..., description="Minimum baseline performance to beat")
    latency_sla_ms: float = Field(default=50.0, description="Maximum acceptable latency SLA in ms")


class EvaluationComparison(BaseModel):
    """Results comparing a simple baseline against an advanced candidate method."""
    problem_id: str
    baseline_metric: float
    candidate_metric: float
    relative_improvement_pct: float
    baseline_latency_ms: float
    candidate_latency_ms: float
    is_candidate_superior: bool
    summary: str


class BaselineEvaluator:
    """Evaluates candidate models against simple baseline heuristics."""

    def __init__(self, spec: ProblemSpecification) -> None:
        self.spec = spec

    def evaluate(
        self,
        ground_truth: List[Any],
        baseline_preds: List[Any],
        candidate_preds: List[Any],
        baseline_lat_ms: float,
        candidate_lat_ms: float,
    ) -> EvaluationComparison:
        """Computes matching accuracy and compares baseline against candidate method."""
        if not (len(ground_truth) == len(baseline_preds) == len(candidate_preds)):
            raise ValueError("All prediction lists must have the same length as ground truth.")

        total = len(ground_truth)
        if total == 0:
            raise ValueError("Evaluation set cannot be empty.")

        baseline_correct = sum(1 for gt, p in zip(ground_truth, baseline_preds) if gt == p)
        candidate_correct = sum(1 for gt, p in zip(ground_truth, candidate_preds) if gt == p)

        baseline_acc = baseline_correct / total
        candidate_acc = candidate_correct / total

        improvement = 0.0
        if baseline_acc > 0:
            improvement = ((candidate_acc - baseline_acc) / baseline_acc) * 100.0

        is_superior = (candidate_acc > baseline_acc) and (candidate_acc >= self.spec.baseline_threshold)

        summary = (
            f"Candidate achieved {candidate_acc:.2%} vs Baseline {baseline_acc:.2%} "
            f"(+{improvement:.1f}% relative gain). Latency: {candidate_lat_ms:.2f}ms vs {baseline_lat_ms:.2f}ms."
        )

        return EvaluationComparison(
            problem_id=self.spec.problem_id,
            baseline_metric=round(baseline_acc, 4),
            candidate_metric=round(candidate_acc, 4),
            relative_improvement_pct=round(improvement, 2),
            baseline_latency_ms=baseline_lat_ms,
            candidate_latency_ms=candidate_lat_ms,
            is_candidate_superior=is_superior,
            summary=summary,
        )
