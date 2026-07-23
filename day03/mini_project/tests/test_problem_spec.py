"""Unit tests for Day 03 Problem Specification and Baseline Evaluator."""

import pytest
from day03.mini_project.src.problem_spec import BaselineEvaluator, ProblemSpecification


@pytest.fixture
def sample_spec() -> ProblemSpecification:
    return ProblemSpecification(
        problem_id="PROB-DEFECT-01",
        name="Loom Weft Defect Detection",
        input_contract={"sensor_reading": "float", "camera_frame": "ndarray"},
        output_contract={"has_defect": "bool", "confidence": "float"},
        target_metric="Accuracy",
        baseline_threshold=0.70,
        latency_sla_ms=10.0,
    )


def test_baseline_evaluator_candidate_wins(sample_spec: ProblemSpecification):
    evaluator = BaselineEvaluator(sample_spec)
    ground_truth = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0]
    baseline_preds = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Constant majority guess (5/10 = 50%)
    candidate_preds = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]  # 9/10 = 90%

    comp = evaluator.evaluate(
        ground_truth=ground_truth,
        baseline_preds=baseline_preds,
        candidate_preds=candidate_preds,
        baseline_lat_ms=0.01,
        candidate_lat_ms=1.25,
    )

    assert comp.baseline_metric == 0.50
    assert comp.candidate_metric == 0.90
    assert comp.relative_improvement_pct == 80.0
    assert comp.is_candidate_superior is True


def test_baseline_evaluator_validation_error_on_mismatched_lengths(sample_spec: ProblemSpecification):
    evaluator = BaselineEvaluator(sample_spec)
    with pytest.raises(ValueError):
        evaluator.evaluate(
            ground_truth=[1, 0],
            baseline_preds=[1],
            candidate_preds=[1, 0],
            baseline_lat_ms=0.1,
            candidate_lat_ms=0.2,
        )
