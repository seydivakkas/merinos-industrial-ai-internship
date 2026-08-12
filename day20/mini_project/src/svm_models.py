import numpy as np
from sklearn.svm import SVC
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import classification_report
from typing import Dict, Any, Tuple, Optional, List
import time

from day20.mini_project.src.models import DefectClass, SupportVectorMetrics


class MerinosSVMClassifier(BaseEstimator, ClassifierMixin):
    """Merinos halı kalite kontrolü için SVM sınıflandırıcı."""

    def __init__(self, kernel: str = 'rbf', C: float = 1.0,
                 gamma: str = 'scale', degree: int = 3,
                 probability: bool = True, random_state: int = 42,
                 coef0: float = 1.0, **kwargs):
        self.kernel = kernel
        self.C = C
        self.gamma = gamma
        self.degree = degree
        self.probability = probability
        self.random_state = random_state
        self.coef0 = coef0
        self.kwargs = kwargs
        self.model = SVC(
            kernel=self.kernel,
            C=self.C,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0,
            probability=self.probability,
            random_state=self.random_state,
            **kwargs
        )
        self.is_fitted = False
        self.training_time_ms = 0.0
        self.n_train_samples = 0

    def fit(self, X, y):
        """Modeli eğitir."""
        self.n_train_samples = len(X)
        t0 = time.perf_counter()
        self.model.fit(X, y)
        t1 = time.perf_counter()
        self.training_time_ms = (t1 - t0) * 1000.0
        self.is_fitted = True
        return self

    def predict(self, X):
        """Sınıf tahminleri."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predicts calibrated class probabilities via Platt scaling."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting probabilities.")
        return self.model.predict_proba(X)

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Computes distance to separating hyperplanes."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before computing decision function.")
        return self.model.decision_function(X)

    @property
    def support_vectors_(self):
        return self.model.support_vectors_

    @property
    def n_support_(self):
        return self.model.n_support_

    @property
    def dual_coef_(self):
        return self.model.dual_coef_

    @property
    def classes_(self):
        return self.model.classes_

    def get_support_vector_metrics(self) -> SupportVectorMetrics:
        """Extracts support vector statistics, class distribution, and dual coefficient norm."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted to inspect support vectors.")

        n_sv = self.model.n_support_
        total_sv = int(np.sum(n_sv))
        sv_ratio_pct = round((total_sv / self.n_train_samples) * 100.0, 2) if self.n_train_samples > 0 else 0.0

        if len(n_sv) == 5:
            class_names = [
                DefectClass.NORMAL.value,
                DefectClass.YARN_BREAKAGE.value,
                DefectClass.OIL_STAIN.value,
                DefectClass.JACQUARD_PATTERN_SHIFT.value,
                DefectClass.BORDER_SEWING_DEFECT.value
            ]
        else:
            class_names = [
                DefectClass.YARN_BREAKAGE.value,
                DefectClass.OIL_STAIN.value,
                DefectClass.JACQUARD_PATTERN_SHIFT.value,
                DefectClass.BORDER_SEWING_DEFECT.value
            ]

        sv_per_class = {
            class_names[i]: int(n_sv[i]) for i in range(min(len(class_names), len(n_sv)))
        }

        dual_norm = float(np.linalg.norm(self.model.dual_coef_))

        return SupportVectorMetrics(
            total_support_vectors=total_sv,
            support_vectors_per_class=sv_per_class,
            support_vector_ratio_pct=sv_ratio_pct,
            dual_coef_norm=round(dual_norm, 4)
        )

    def benchmark_latency(self, X: np.ndarray, n_runs: int = 200) -> Tuple[float, float]:
        """Measures single-sample inference latency in ms and throughput in predictions per second."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted for benchmarking.")

        sample = X[:1]
        for _ in range(20):
            self.model.predict(sample)

        t0 = time.perf_counter()
        for _ in range(n_runs):
            self.model.predict(sample)
        t1 = time.perf_counter()

        latency_ms = ((t1 - t0) / n_runs) * 1000.0
        throughput_fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0

        return latency_ms, throughput_fps
