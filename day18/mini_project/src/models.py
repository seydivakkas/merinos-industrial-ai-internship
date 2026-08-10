"""
Merinos Industrial AI Internship - Day 18
Pydantic Data Models and Schemas for Decision Tree and Random Forest Ensemble
"""

from enum import IntEnum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DefectClass(IntEnum):
    """Merinos carpet and yarn 4-class industrial defect taxonomy."""
    YARN_BREAKAGE = 0
    OIL_STAIN = 1
    JACQUARD_PATTERN_SHIFT = 2
    BORDER_SEWING_DEFECT = 3


class TreeComplexityMetrics(BaseModel):
    """Structural complexity metrics of a decision tree."""
    depth: int = Field(..., description="Maximum depth of the tree")
    node_count: int = Field(..., description="Total number of nodes (split + leaves)")
    leaf_count: int = Field(..., description="Number of terminal leaves")
    ccp_alpha: float = Field(0.0, description="Cost-complexity pruning parameter alpha")


class ModelEvaluationMetrics(BaseModel):
    """Performance and generalization metrics for a classifier."""
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Test accuracy score")
    macro_f1: float = Field(..., ge=0.0, le=1.0, description="Macro-averaged F1 score")
    weighted_f1: float = Field(..., ge=0.0, le=1.0, description="Weighted-averaged F1 score")
    cohen_kappa: float = Field(..., ge=-1.0, le=1.0, description="Cohen's kappa coefficient")
    train_accuracy: float = Field(..., ge=0.0, le=1.0, description="Training set accuracy")
    test_accuracy: float = Field(..., ge=0.0, le=1.0, description="Testing set accuracy")
    overfitting_gap: float = Field(..., description="Train accuracy minus test accuracy")
    latency_ms: float = Field(..., ge=0.0, description="Single sample inference latency in ms")
    throughput_fps: float = Field(..., ge=0.0, description="Inference throughput in frames/samples per second")


class PruningPathResult(BaseModel):
    """Cost-complexity pruning path evaluation and optimal alpha selection."""
    ccp_alphas: List[float] = Field(..., description="Array of effective pruning alphas")
    impurities: List[float] = Field(..., description="Subtree total impurities at each step")
    train_scores: List[float] = Field(..., description="Train accuracy along the alpha path")
    test_scores: List[float] = Field(..., description="Test accuracy along the alpha path")
    optimal_ccp_alpha: float = Field(..., ge=0.0, description="Selected optimal alpha minimizing test error")
    optimal_leaf_count: int = Field(..., ge=1, description="Leaf count of pruned tree at optimal alpha")
    unpruned_leaf_count: int = Field(..., ge=1, description="Leaf count of unpruned baseline tree")
    leaf_reduction_pct: float = Field(..., description="Percentage reduction in leaf count")


class RandomForestMetrics(BaseModel):
    """Random Forest ensemble specific evaluation and diagnostics."""
    oob_score: float = Field(..., ge=0.0, le=1.0, description="Out-Of-Bag accuracy score")
    oob_error: float = Field(..., ge=0.0, le=1.0, description="Out-Of-Bag error (1 - oob_score)")
    n_estimators: int = Field(..., ge=1, description="Number of trees in ensemble")
    max_features: str = Field("sqrt", description="Feature sampling rule per split")
    feature_importances: Dict[str, float] = Field(..., description="MDI / Gini feature importances")


class EnsembleComparisonReport(BaseModel):
    """Master benchmark report comparing Unpruned Tree, Pruned Tree, and Random Forest."""
    timestamp: str = Field(..., description="ISO 8601 generation timestamp")
    n_samples: int = Field(..., ge=1, description="Total dataset size")
    test_samples: int = Field(..., ge=1, description="Test partition sample count")
    unpruned_tree: ModelEvaluationMetrics = Field(..., description="Unpruned decision tree metrics")
    unpruned_complexity: TreeComplexityMetrics = Field(..., description="Unpruned tree complexity")
    pruned_tree: ModelEvaluationMetrics = Field(..., description="Pruned decision tree metrics")
    pruned_complexity: TreeComplexityMetrics = Field(..., description="Pruned tree complexity")
    random_forest: ModelEvaluationMetrics = Field(..., description="Random Forest ensemble metrics")
    random_forest_metrics: RandomForestMetrics = Field(..., description="Random Forest OOB and MDI metrics")
    criterion_comparison: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Performance metrics comparing Gini Impurity vs Shannon Entropy"
    )
    best_model_name: str = Field(..., description="Name of the champion model for deployment")
    recommendations: List[str] = Field(default_factory=list, description="Production engineering action items")


class TreePredictionResult(BaseModel):
    """Single-sample real-time inference prediction payload."""
    predicted_class_id: int = Field(..., description="Predicted defect class integer (0..3)")
    predicted_class_name: str = Field(..., description="Human-readable defect class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Posterior probability/vote fraction")
    class_probabilities: Dict[str, float] = Field(..., description="Predicted class probability distribution")
    dominant_features: List[str] = Field(default_factory=list, description="Key features influencing decision")
