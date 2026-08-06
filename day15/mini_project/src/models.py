"""Pydantic data models for Merinos Industrial Vision CLI Toolkit (Day 15).

Defines structured schema for pipeline stages, inspection reports, verdicts,
and Phase 2 master benchmark release manifests.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QualityVerdict(str, Enum):
    """Overall carpet manufacturing quality verdict."""

    ACCEPT = "ACCEPT"
    WARNING = "WARNING"
    REJECT = "REJECT"


class StageStatus(str, Enum):
    """Status of an individual inspection pipeline stage."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


class StageResult(BaseModel):
    """Result of a single inspection pipeline stage."""

    stage_name: str = Field(..., description="Unique name of the pipeline stage")
    status: StageStatus = Field(default=StageStatus.PASS, description="Pass/Warn/Fail status")
    execution_time_ms: float = Field(default=0.0, description="Stage latency in milliseconds")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Stage-specific scalar metrics")
    notes: Optional[str] = Field(default=None, description="Diagnostic notes or failure reasons")


class MasterInspectionReport(BaseModel):
    """End-to-end carpet quality inspection final report."""

    carpet_id: str = Field(..., description="Unique identifier for inspected carpet sample")
    timestamp: str = Field(..., description="ISO-formatted inspection timestamp")
    overall_verdict: QualityVerdict = Field(..., description="Final quality decision: ACCEPT/WARNING/REJECT")
    total_execution_time_ms: float = Field(..., description="Total pipeline latency across all stages")
    stage_results: Dict[str, StageResult] = Field(
        default_factory=dict, description="Detailed stage-by-stage results"
    )
    defect_count: int = Field(default=0, description="Total morphological defect count")
    border_skew_deg: float = Field(default=0.0, description="Maximum border skew angle in degrees")
    mean_delta_e: float = Field(default=0.0, description="Mean CIEDE2000 color difference")
    motif_coverage_pct: float = Field(default=0.0, description="Motif segmentation coverage percentage")
    predicted_pattern: str = Field(default="unknown", description="Identified jacquard pattern category")
    confidence: float = Field(default=0.0, description="Pattern classification confidence score")
    summary_recommendation: str = Field(..., description="Actionable manufacturing recommendation")


class Phase2ModuleBenchmark(BaseModel):
    """Performance and latency benchmark record for a Phase 2 module."""

    module_id: str = Field(..., description="Unique ID (e.g., day07_io_and_filtering)")
    module_name: str = Field(..., description="Descriptive human-readable module title")
    day_number: int = Field(..., description="Curriculum day number (7 to 14)")
    fps: float = Field(..., description="Throughput in frames per second")
    mean_latency_ms: float = Field(..., description="Mean execution latency in milliseconds")
    std_latency_ms: float = Field(..., description="Latency standard deviation in milliseconds")
    status: str = Field(default="OPERATIONAL", description="Health status (OPERATIONAL/DEGRADED)")
    memory_mb: float = Field(default=0.0, description="Estimated process memory footprint in MB")


class ReleaseManifest(BaseModel):
    """Complete Phase 2 release manifest and system readiness record."""

    app_name: str = Field(..., description="Toolkit application name")
    version: str = Field(..., description="Toolkit semantic version")
    phase: str = Field(..., description="Curriculum phase name")
    facility: str = Field(..., description="Industrial plant location")
    modules: List[Phase2ModuleBenchmark] = Field(
        default_factory=list, description="Benchmarks for all integrated modules"
    )
    overall_health: str = Field(default="HEALTHY", description="Overall system health status")
    total_integrated_days: int = Field(default=8, description="Number of integrated Phase 2 days (7-14)")
    release_notes: str = Field(..., description="Summary of features and production readiness")
