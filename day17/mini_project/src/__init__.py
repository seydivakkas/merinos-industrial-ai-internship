"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Kusur Sınıflandırma Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import inspect
from sklearn.linear_model import LogisticRegression

# Scikit-learn >= 1.5 multi_class uyumluluk yaması (şablon ve test kararlılığı için)
_orig_lr_init = LogisticRegression.__init__
_sig = inspect.signature(_orig_lr_init)
if "multi_class" not in _sig.parameters:
    def _compat_lr_init(self, *args, **kwargs):
        kwargs.pop("multi_class", None)
        return _orig_lr_init(self, *args, **kwargs)
    _compat_lr_init.__signature__ = _sig
    LogisticRegression.__init__ = _compat_lr_init

from .data_generator import MulticlassQualityDataGenerator
from .evaluator import MulticlassEvaluator
from .models import (
    ClassTopFeatures,
    DefectClass,
    ModelComparisonSummary,
    MulticlassEvaluationReport,
    MulticlassMetrics,
    MulticlassPredictionResult,
    PerClassMetrics,
)
from .multiclass_classifier import MerinosMulticlassClassifier
from .preprocessor import MulticlassDataPreprocessor
from .visualizer import MulticlassVisualizer

__all__ = [
    "DefectClass",
    "PerClassMetrics",
    "MulticlassMetrics",
    "ModelComparisonSummary",
    "ClassTopFeatures",
    "MulticlassEvaluationReport",
    "MulticlassPredictionResult",
    "MulticlassQualityDataGenerator",
    "MulticlassDataPreprocessor",
    "MerinosMulticlassClassifier",
    "MulticlassEvaluator",
    "MulticlassVisualizer",
]
