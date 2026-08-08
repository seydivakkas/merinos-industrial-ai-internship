from typing import Literal, Optional, Dict, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

class MerinosMulticlassClassifier:
    """Merinos halı & iplik kalite kontrolü için
    çok sınıflı lojistik regresyon sınıflandırıcısı.
    Softmax (multinomial) ve One-vs-Rest (OvR) yaklaşımlarını destekler."""
    def __init__(
        self,
        strategy: Literal["multinomial", "ovr"] = "multinomial",
        class_weight: Optional[str] = "balanced",
        random_state: int = 42
    ):
        self.strategy = strategy
        self.class_weight = class_weight
        self.random_state = random_state
        self.model = self._create_model()

    def _create_model(self):
        if self.strategy == "multinomial":
            # Softmax - çok sınıflı lojistik regresyon
            return Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(
                    multi_class="multinomial",
                    solver="lbfgs",
                    class_weight=self.class_weight,
                    max_iter=1000,
                    random_state=self.random_state
                ))
            ])
        else:
            return Pipeline([
                ("scaler", StandardScaler()),
                ("clf", OneVsRestClassifier(
                    LogisticRegression(
                        solver="liblinear",
                        class_weight=self.class_weight,
                        max_iter=1000,
                        random_state=self.random_state
                    )
                ))
            ])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MerinosMulticlassClassifier":
        """Modeli verilen eğitim tensörleri üzerinde eğitir ve eğitim süresini ölçer."""
        t0 = time.perf_counter()
        self.model.fit(X, y)
        self.training_time_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        self.is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """En yüksek olasılıklı sınıf tahminlerini döndürür."""
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Her sınıf için öngörülen olasılık dağılımını (N, 4) döndürür."""
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")
        probs = self.model.predict_proba(X)
        row_sums = probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return probs / row_sums

    def measure_inference_speed(
        self, X: np.ndarray, n_iterations: int = 50
    ) -> Tuple[float, float]:
        """
        Çıkarım gecikmesini (ms) ve saniyedeki örneklem kapasitesini (FPS) ölçer.
        """
        if not self.is_trained:
            raise RuntimeError("Model eğitilmemiş!")

        _ = self.model.predict(X[:min(len(X), 10)])

        t0 = time.perf_counter()
        for _ in range(n_iterations):
            _ = self.model.predict(X)
        elapsed = time.perf_counter() - t0

        total_samples = len(X) * n_iterations
        throughput_fps = round(total_samples / elapsed, 1)
        latency_per_sample_ms = round((elapsed / total_samples) * 1000.0, 4)

        return latency_per_sample_ms, throughput_fps

    def get_feature_importance(self, feature_names: List[str]) -> List[ClassTopFeatures]:
        """
        Her sınıf için en ayırt edici pozitif ve negatif katsayıları çıkarır.
        """
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")

        clf_step = self.model.named_steps["clf"]
        if self.strategy == "multinomial":
            coef_matrix = clf_step.coef_
        else:
            coef_matrix = np.array([est.coef_[0] for est in clf_step.estimators_])

        results: List[ClassTopFeatures] = []
        class_names = [e.name for e in DefectClass]

        for k, cname in enumerate(class_names):
            weights = coef_matrix[k]
            paired = [(fname, float(w)) for fname, w in zip(feature_names, weights)]

            pos_sorted = sorted([p for p in paired if p[1] > 0], key=lambda x: x[1], reverse=True)
            neg_sorted = sorted([p for p in paired if p[1] < 0], key=lambda x: x[1])

            results.append(
                ClassTopFeatures(
                    class_name=cname,
                    top_positive_features=[{item[0]: round(item[1], 4)} for item in pos_sorted[:3]],
                    top_negative_features=[{item[0]: round(item[1], 4)} for item in neg_sorted[:3]],
                )
            )

        return results

    @property
    def coef_(self):
        clf_step = self.model.named_steps["clf"]
        if self.strategy == "multinomial":
            return clf_step.coef_
        else:
            return np.array([est.coef_[0] for est in clf_step.estimators_])

    @property
    def intercept_(self):
        clf_step = self.model.named_steps["clf"]
        if self.strategy == "multinomial":
            return clf_step.intercept_
        else:
            return np.array([est.intercept_[0] for est in clf_step.estimators_])


# Modül içi yardımcı aktarımlar ve durum başlatıcı
import time
from typing import List, Tuple
from .models import ClassTopFeatures, DefectClass

_orig_clf_init = MerinosMulticlassClassifier.__init__
def _compat_clf_init(self, strategy: str = "multinomial", class_weight: Optional[str] = "balanced", random_state: int = 42, *args, **kwargs):
    _orig_clf_init(self, strategy=strategy, class_weight=class_weight, random_state=random_state)
    self.is_trained = False
    self.training_time_ms = 0.0

MerinosMulticlassClassifier.__init__ = _compat_clf_init

