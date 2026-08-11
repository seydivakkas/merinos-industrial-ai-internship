"""
Merinos Industrial AI Internship - Day 19
Pydantic Data Models and Schemas for Gradient Boosting (XGBoost & LightGBM)
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


class EarlyStoppingResult(BaseModel):
    """Early stopping tracking diagnostics across boosting iterations."""
    train_loss_history: List[float] = Field(..., description="Training loss progression per iteration")
    val_loss_history: List[float] = Field(..., description="Validation loss progression per iteration")
    best_iteration: int = Field(..., ge=1, description="Iteration yielding minimum validation loss")
    stopping_iteration: int = Field(..., ge=1, description="Iteration where early stopping triggered")
    best_val_loss: float = Field(..., ge=0.0, description="Minimum validation loss achieved")

    @property
    def best_score(self) -> float:
        return self.best_val_loss


class BoostingModelMetrics(BaseModel):
    """Performance, loss convergence and profiling metrics for gradient boosted models."""
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Test accuracy score")
    macro_f1: float = Field(..., ge=0.0, le=1.0, description="Macro-averaged F1 score")
    weighted_f1: float = Field(..., ge=0.0, le=1.0, description="Weighted-averaged F1 score")
    cohen_kappa: float = Field(..., ge=-1.0, le=1.0, description="Cohen's kappa coefficient")
    train_loss: float = Field(..., ge=0.0, description="Final training multi-logloss")
    val_loss: float = Field(..., ge=0.0, description="Final validation multi-logloss")
    best_iteration: int = Field(..., ge=1, description="Optimal boosting tree iteration selected by early stopping")
    total_iterations: int = Field(..., ge=1, description="Total number of boosting iterations evaluated")
    latency_ms: float = Field(..., ge=0.0, description="Single-sample inference latency in milliseconds")
    throughput_fps: float = Field(..., ge=0.0, description="Inference throughput in samples/second")
    training_time_ms: float = Field(..., ge=0.0, description="Total model fitting time in milliseconds")
    early_stopping: Optional[EarlyStoppingResult] = Field(None, description="Early stopping results payload")

    @property
    def test_accuracy(self) -> float:
        return self.accuracy

    @property
    def single_sample_latency_ms(self) -> float:
        return self.latency_ms


class HyperparameterTuningRecord(BaseModel):
    """Single trial record in hyperparameter grid evaluation."""
    learning_rate: float = Field(..., description="Shrinkage factor eta")
    max_depth: int = Field(..., description="Maximum tree depth")
    val_accuracy: float = Field(..., description="Validation accuracy score")
    test_accuracy: float = Field(..., description="Test accuracy score")
    best_iteration: int = Field(..., description="Early stopping optimal iteration")
    train_time_ms: float = Field(default=0.0, description="Trial training duration in ms")


class HyperparameterTuningResult(BaseModel):
    """Overall hyperparameter grid search results."""
    best_learning_rate: float = Field(..., description="Selected optimal learning rate")
    best_max_depth: int = Field(..., description="Selected optimal tree depth")
    best_accuracy: float = Field(..., description="Top validation accuracy achieved")
    records: List[HyperparameterTuningRecord] = Field(..., description="All evaluated configurations")

    @property
    def best_score(self) -> float:
        return self.best_accuracy

    @property
    def grid_records(self) -> List[HyperparameterTuningRecord]:
        return self.records


class BoostingComparisonReport(BaseModel):
    """Master benchmark report comparing XGBoost and LightGBM models."""
    timestamp: str = Field(..., description="ISO 8601 generation timestamp")
    n_train: int = Field(..., ge=1, description="Number of training samples (70%)")
    n_val: int = Field(..., ge=1, description="Number of validation samples (15%)")
    n_test: int = Field(..., ge=1, description="Number of testing samples (15%)")
    xgboost: BoostingModelMetrics = Field(..., description="XGBoost performance metrics")
    lightgbm: BoostingModelMetrics = Field(..., description="LightGBM performance metrics")
    baseline_rf_accuracy: float = Field(..., description="Day 18 Random Forest baseline test accuracy")
    feature_importances_xgb: Dict[str, float] = Field(..., description="XGBoost Gain feature importances")
    feature_importances_lgb: Dict[str, float] = Field(..., description="LightGBM Split feature importances")
    champion_model: str = Field(..., description="Best performing gradient boosting model")
    speedup_factor: float = Field(..., description="Training speedup ratio of LightGBM over XGBoost")
    recommendations: List[str] = Field(default_factory=list, description="Production deployment guidelines")

    @property
    def winner_model(self) -> str:
        return self.champion_model

    @property
    def speedup_summary(self) -> str:
        return f"LightGBM, XGBoost modeline göre {self.speedup_factor:.1f}x kat daha hızlı eğitildi."

    @property
    def xgboost_metrics(self) -> BoostingModelMetrics:
        return self.xgboost

    @property
    def lightgbm_metrics(self) -> BoostingModelMetrics:
        return self.lightgbm


class BoostingPredictionResult(BaseModel):
    """Single-sample real-time inference prediction payload."""
    predicted_class_id: int = Field(..., description="Predicted defect class integer (0..3)")
    predicted_class_name: str = Field(..., description="Human-readable defect class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Posterior probability score")
    class_probabilities: Dict[str, float] = Field(..., description="Probability distribution across classes")
    top_contributing_feature: str = Field(..., description="Feature with highest attribution for this sample")
