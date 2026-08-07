"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
Kalite Verisi Ön İşleme, Standartlaştırma ve Stratified Bölümleme

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class QualityDataPreprocessor:
    """Veri sızıntısını engelleyen tabakalı bölümleme ve özellik ölçekleyici."""

    def __init__(self, target_column: str = "quality_label"):
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
        Veri çerçevesini tabakalı olarak Train/Test kümelerine ayırır ve SADECE Train üzerinde fit edilen StandardScaler ile ölçekler.
        
        Args:
            df: Giriş veri çerçevesi.
            test_size: Test kümesi oranı (Varsayılan: 0.20).
            random_state: Bölümleme tohumu (Varsayılan: 42).
            
        Returns:
            X_train_scaled, X_test_scaled, y_train, y_test
        """
        feature_cols = [c for c in df.columns if c != self.target_column]
        self.feature_names = list(feature_cols)

        X = df[feature_cols].values
        y = df[self.target_column].values.astype(int)

        # Dengesiz sınıfların her iki kümeye de eşit oranda dağıtılması için stratify=y
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Veri sızıntısını (Data Leakage) önlemek için SADECE X_train üzerinde fit edilir
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.is_fitted = True

        return X_train_scaled, X_test_scaled, y_train, y_test

    def transform_single(self, features_dict: Dict[str, float]) -> np.ndarray:
        """
        Tekil sensör ölçüm sözlüğünü ölçeklenmiş 2D NumPy dizisine dönüştürür.
        
        Args:
            features_dict: Öznitelik isimlerini ve değerlerini içeren sözlük.
            
        Returns:
            np.ndarray: (1, n_features) boyutunda ölçeklenmiş tensör.
        """
        if not self.is_fitted:
            raise RuntimeError("Ön işleyici henüz eğitim verisi üzerinde fit edilmemiştir!")

        ordered_values = [features_dict[name] for name in self.feature_names]
        arr = np.array(ordered_values, dtype=float).reshape(1, -1)
        return self.scaler.transform(arr)

    def get_scaler_parameters(self) -> Dict[str, Dict[str, float]]:
        """Öznitelik bazlı ortalama ve standart sapma parametrelerini döndürür."""
        if not self.is_fitted:
            raise RuntimeError("Ön işleyici henüz fit edilmemiştir.")

        params = {}
        for idx, fname in enumerate(self.feature_names):
            params[fname] = {
                "mean": float(self.scaler.mean_[idx]),
                "scale": float(self.scaler.scale_[idx]),
            }
        return params
