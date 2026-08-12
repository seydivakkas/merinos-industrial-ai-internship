"""Pydantic v2 data models for Merinos SVM Defect Classification."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DefectClass(str, Enum):
    """Primary carpet quality and defect categories observed in jacquard looms."""
    NORMAL = "NORMAL"
    YARN_BREAKAGE = "YARN_BREAKAGE"
    OIL_STAIN = "OIL_STAIN"
    JACQUARD_PATTERN_SHIFT = "JACQUARD_PATTERN_SHIFT"
    BORDER_SEWING_DEFECT = "BORDER_SEWING_DEFECT"


class SupportVectorMetrics(BaseModel):
    """Metrics regarding support vector geometry and margin allocation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_support_vectors: int = Field(..., description="Total count of support vectors across all classes")
    support_vectors_per_class: Dict[str, int] = Field(..., description="Support vector counts per defect class")
    support_vector_ratio_pct: float = Field(..., description="Percentage of training samples serving as SVs")
    dual_coef_norm: float = Field(..., description="L2 norm of dual coefficients (alpha)")


class SVMKernelMetrics(BaseModel):
    """Performance and complexity metrics for a specific SVM kernel."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kernel_name: str = Field(..., description="Kernel type: linear, poly, or rbf")
    train_accuracy: float = Field(..., ge=0.0, le=1.0)
    test_accuracy: float = Field(..., ge=0.0, le=1.0)
    macro_f1: float = Field(..., ge=0.0, le=1.0)
    weighted_f1: float = Field(..., ge=0.0, le=1.0)
    cohen_kappa: float = Field(..., ge=-1.0, le=1.0)
    support_vectors: SupportVectorMetrics = Field(..., description="Support vector details")
    training_time_ms: float = Field(..., ge=0.0, description="Model training time in milliseconds")
    single_sample_latency_ms: float = Field(..., ge=0.0, description="Single sample prediction latency")
    throughput_fps: float = Field(..., ge=0.0, description="Inference throughput in predictions per second")


class SVMGridSearchRecord(BaseModel):
    """Single cell result from C and gamma hyperparameter sweep."""
    C: float
    gamma: float
    mean_cv_accuracy: float
    test_accuracy: float
    n_support_vectors: int


class SVMGridSearchResult(BaseModel):
    """Overall hyperparameter grid optimization result."""
    best_C: float
    best_gamma: float
    best_score: float
    grid_records: List[SVMGridSearchRecord]


class SVMComparisonReport(BaseModel):
    """Comprehensive benchmark comparison report across all SVM kernels."""
    dataset_name: str = "Merinos Carpet Weaving Sensor Telemetry"
    total_samples: int
    train_samples: int
    test_samples: int
    features_count: int
    linear_metrics: SVMKernelMetrics
    polynomial_metrics: SVMKernelMetrics
    rbf_metrics: SVMKernelMetrics
    winner_model: str
    speedup_summary: str
    grid_search_result: Optional[SVMGridSearchResult] = None


class SVMPredictionResult(BaseModel):
    """Real-time defect prediction inference payload."""
    predicted_class: str
    predicted_class_tr: str
    confidence_score: float
    class_probabilities: Dict[str, float]
    support_vector_distance: Optional[float] = None
