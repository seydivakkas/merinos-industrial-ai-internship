"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Veri Ön İşleme, Standartlaştırma ve Tabakalı Bölme

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class MulticlassDataPreprocessor:
    """Çok sınıflı tabakalı (stratified) veri bölücü ve sızıntısız özellik ölçekleyici."""

    def __init__(self, target_column: str = "defect_class"):
        self.target_column = target_column
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def split_and_scale(
        self,
        df: pd.DataFrame,
        test_size: float = 0.20,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Çok sınıflı etiketi (0, 1, 2, 3) koruyarak veriyi böler ve StandardScaler ile ölçekler.
        """
        feature_cols = [c for c in df.columns if c != self.target_column]
        self.feature_names = list(feature_cols)

        X = df[feature_cols].values
        y = df[self.target_column].values.astype(int)

        # Tabakalı çok sınıflı bölme
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # SADECE train kümesi üzerinde fit
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.is_fitted = True

        return X_train_scaled, X_test_scaled, y_train, y_test

    def transform_single(self, features_dict: Dict[str, float]) -> np.ndarray:
        """Tekil sensör ölçümünü ölçeklenmiş 2D NumPy dizisine dönüştürür."""
        if not self.is_fitted:
            raise RuntimeError("Ön işleyici henüz eğitim verisi üzerinde eğitilmemiştir!")

        vals = [features_dict[name] for name in self.feature_names]
        arr = np.array(vals, dtype=float).reshape(1, -1)
        return self.scaler.transform(arr)
