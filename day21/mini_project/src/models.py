"""Pydantic v2 data models for Merinos Unsupervised Learning and Phase 3 Master Benchmark."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DefectClass(str, Enum):
    """Primary defect categories and novel anomaly tag."""
    YARN_BREAKAGE = "YARN_BREAKAGE"
    OIL_STAIN = "OIL_STAIN"
    JACQUARD_PATTERN_SHIFT = "JACQUARD_PATTERN_SHIFT"
    BORDER_SEWING_DEFECT = "BORDER_SEWING_DEFECT"
    ANOMALOUS_NOISE = "ANOMALOUS_NOISE"


class PCAMetrics(BaseModel):
    """Metrics regarding principal component decomposition and variance retention."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    explained_variance_ratio: List[float] = Field(..., description="Variance ratio per principal component")
    cumulative_variance_ratio: List[float] = Field(..., description="Running cumulative variance sum")
    components_for_95_variance: int = Field(..., description="Number of PCs needed to retain 95% total variance")
    total_variance_explained: float = Field(..., description="Total variance captured by selected components")


class ClusteringMetrics(BaseModel):
    """Unsupervised cluster quality metrics and ground truth alignment."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    silhouette_score: float = Field(..., ge=-1.0, le=1.0, description="Silhouette coefficient (-1 to +1)")
    davies_bouldin_index: float = Field(..., ge=0.0, description="Davies-Bouldin index (lower is better)")
    calinski_harabasz_index: float = Field(..., ge=0.0, description="Calinski-Harabasz variance ratio (higher is better)")
    adjusted_rand_index: float = Field(..., ge=-1.0, le=1.0, description="ARI vs true defect labels")


class DBSCANAnomalyMetrics(BaseModel):
    """Metrics for density-based spatial clustering and novel anomaly discovery."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    n_clusters_found: int = Field(..., description="Number of dense clusters discovered (excluding noise)")
    n_anomalies_detected: int = Field(..., description="Number of points assigned to noise label -1")
    anomaly_ratio_pct: float = Field(..., description="Percentage of dataset flagged as novel anomalies")


class Phase3ModelEntry(BaseModel):
    """Standardized performance benchmark entry for a Phase 3 supervised or unsupervised model."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_name: str
    day_tag: str
    paradigm: str
    test_accuracy: float = Field(..., ge=0.0, le=1.0)
    macro_f1: float = Field(..., ge=0.0, le=1.0)
    training_time_ms: float = Field(..., ge=0.0)
    single_sample_latency_ms: float = Field(..., ge=0.0)
    throughput_fps: float = Field(..., ge=0.0)
    memory_footprint_rank: str
    industrial_deployment_tier: str


class Phase3MasterReport(BaseModel):
    """Phase 3 Master Consolidated Benchmark Report spanning Day 16 to Day 21."""
    title: str = "Merinos Industrial AI Phase 3 Master Benchmark Release"
    phase: str = "Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma"
    total_models_evaluated: int
    dataset_samples: int
    pca_metrics: PCAMetrics
    clustering_metrics: ClusteringMetrics
    dbscan_metrics: DBSCANAnomalyMetrics
    models: List[Phase3ModelEntry]
    champion_high_speed_edge: str
    champion_high_accuracy_server: str
    phase_conclusion_summary: str


class AnomalyDetectionResult(BaseModel):
    """Real-time payload for unsupervised anomaly triage."""
    is_anomaly: bool
    anomaly_score: float
    nearest_cluster_id: int
    distance_to_centroid: float
