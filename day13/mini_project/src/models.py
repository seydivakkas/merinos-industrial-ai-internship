"""
models.py - Pydantic models for Day 13: Border Analysis & Morphological Defect Detection.

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from .border_models import (
    EdgeOperatorType,
    BorderSide,
    QualityDecision,
    LineSegment,
    BorderEdge,
    ParallelismMetric,
    BorderParallelismReport,
)
from .defect_models import (
    DefectType,
    DefectSeverity,
    RollDecision,
    DefectBoundingBox,
    DetectedDefect,
    MorphologyInspectionReport,
)

__all__ = [
    "EdgeOperatorType",
    "BorderSide",
    "QualityDecision",
    "LineSegment",
    "BorderEdge",
    "ParallelismMetric",
    "BorderParallelismReport",
    "DefectType",
    "DefectSeverity",
    "RollDecision",
    "DefectBoundingBox",
    "DetectedDefect",
    "MorphologyInspectionReport",
]
