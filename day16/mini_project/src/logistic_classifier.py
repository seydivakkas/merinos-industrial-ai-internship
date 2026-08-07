import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import joblib
import logging

from .models import FeatureWeight, QualityClass

logger = logging.getLogger(__name__)

class MerinosBinaryLogisticClassifier:
    """
    Logistic regression classifier for yarn quality
    (binary: normal vs defective).
    """

    def __init__(
        self,
        class_weight: Optional[Union[str, dict]] = "balanced",
        random_state: int = 42,
        *args,
        **kwargs,
    ):
        self.class_weight = class_weight
        self.random_state = random_state
        self.is_trained: bool = False

        clf_kwargs = {
            "class_weight": class_weight,
            "random_state": random_state,
            "max_iter": kwargs.get("max_iter", 1000),
        }
        if "C" in kwargs:
            clf_kwargs["C"] = kwargs["C"]
        if "solver" in kwargs:
            clf_kwargs["solver"] = kwargs["solver"]
        if "penalty" in kwargs and kwargs["penalty"] != "l2":
            clf_kwargs["penalty"] = kwargs["penalty"]

        self.model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(**clf_kwargs)),
        ])

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the logistic regression model."""
        logger.info("Training logistic regression model...")
        self.model.fit(X, y)
        self.is_trained = True
        return self

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Her örneklem için standart ve kusurlu sınıf olasılıklarını döndürür."""
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")
        return self.model.predict_proba(X)

    def predict(self, X: Union[np.ndarray, pd.DataFrame], threshold: float = 0.50) -> np.ndarray:
        """Belirtilen karar eşiğine (tau) göre sınıf tahminlerini (0 veya 1) üretir."""
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")
        probs = self.predict_proba(X)[:, 1]
        return (probs >= threshold).astype(int)

    def get_intercept(self) -> float:
        """Modelin bias / sabit terimini (beta_0) döndürür."""
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")
        clf = self.model.named_steps["clf"]
        return float(clf.intercept_[0])

    def get_feature_weights(self, feature_names: List[str]) -> List[FeatureWeight]:
        """
        Öznitelik katsayılarını (beta_j) ve Odds Oranlarını (exp(beta_j)) hesaplar, mutlak etkiye göre sıralar.
        """
        if not self.is_trained:
            raise RuntimeError("Model henüz eğitilmemiştir!")

        clf = self.model.named_steps["clf"]
        coefs = clf.coef_[0]
        results: List[FeatureWeight] = []

        for name, w in zip(feature_names, coefs):
            w_float = float(w)
            odds_ratio = float(np.exp(w_float))
            direction = "Kusur Riskini ARTIRICI" if w_float > 0 else "Kusur Riskini AZALTICI"

            results.append(
                FeatureWeight(
                    feature_name=name,
                    weight=round(w_float, 4),
                    odds_ratio=round(odds_ratio, 4),
                    impact_direction=direction,
                )
            )

        results.sort(key=lambda x: abs(x.weight), reverse=True)
        return results

    @property
    def coef_(self):
        return self.model.named_steps["clf"].coef_

    @property
    def intercept_(self):
        return self.model.named_steps["clf"].intercept_
