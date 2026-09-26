"""
Day 11 - K-Means ile Baskın Renk ve Palet Çıkarımı Paketi.
"""

from day11.mini_project.src.generator import (
    create_woven_fabric_texture,
    generate_all_synthetic_defect_fixtures,
)
from day11.mini_project.src.kmeans_palette_engine import (
    ColorCluster,
    DominantPaletteResult,
    KMeansPaletteExtractor,
)
from day11.mini_project.src.models import (
    DefectBoundingBox,
    DefectSeverity,
    DefectType,
    DetectedDefect,
    MorphologyInspectionReport,
    RollDecision,
)
from day11.mini_project.src.morphology_engine import MorphologyEngine
from day11.mini_project.src.defect_detector import CarpetDefectDetector

__all__ = [
    "ColorCluster",
    "DominantPaletteResult",
    "KMeansPaletteExtractor",
    "DefectType",
    "DefectSeverity",
    "RollDecision",
    "DefectBoundingBox",
    "DetectedDefect",
    "MorphologyInspectionReport",
    "MorphologyEngine",
    "CarpetDefectDetector",
    "create_woven_fabric_texture",
    "generate_all_synthetic_defect_fixtures",
]
