"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Klasik Segmentasyon Kıyaslaması Paketi (Otsu, Watershed, GrabCut)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from .benchmark import SegmentationBenchmarkEngine
from .evaluator import SegmentationEvaluator
from .generator import CarpetSegmentationFixtureGenerator, _safe_imread, _safe_imwrite
from .grabcut_segmenter import GrabCutSegmenter
from .models import (
    AlgorithmBenchmarkResult,
    CarpetSegmentationReport,
    EvaluationMetrics,
    SegmentationClass,
    SegmentationMethod,
)
from .otsu_segmenter import OtsuSegmenter
from .watershed_segmenter import WatershedSegmenter

__all__ = [
    "OtsuSegmenter",
    "WatershedSegmenter",
    "GrabCutSegmenter",
    "SegmentationEvaluator",
    "SegmentationBenchmarkEngine",
    "CarpetSegmentationFixtureGenerator",
    "_safe_imread",
    "_safe_imwrite",
    "SegmentationMethod",
    "SegmentationClass",
    "EvaluationMetrics",
    "AlgorithmBenchmarkResult",
    "CarpetSegmentationReport",
]
