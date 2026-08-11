import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
import os

from day19.mini_project.src.models import DefectClass


class BoostingQualityDataGenerator:
    """Merinos halı dokuma kalite kontrolü için
    sentetik veri üreten sınıf.

    Gradient boosting modelleri (XGBoost, LightGBM)
    ile kullanılmak üzere gerçekçi özellik dağılımları
    oluşturur."""

    def __init__(
        self,
        n_samples: int = 5000,
        random_state: int = 42,
        output_dir: Optional[str] = None,
        **kwargs
    ):
        self.n_samples = n_samples
        self.random_state = random_state
        self.output_dir = output_dir or "../fixtures"

        self.feature_columns = [
            "yarn_tensile_strength",
            "yarn_elongation_at_break",
            "yarn_hairiness_index",
            "twist_per_meter",
            "yarn_linear_density_dtex",
            "loom_rpm",
            "loom_tension_variation",
            "ambient_relative_humidity",
            "ambient_temperature_c",
            "weft_insertion_rate",
        ]
        self.feature_names = self.feature_columns
        self.noise_level = kwargs.get("noise_level", 0.04)
        self.rng = np.random.default_rng(seed=random_state)

    def generate(self) -> pd.DataFrame:
        """
        Generates realistic non-linear sensor measurements and assigns 4 defect classes
        with complex residual boundaries.
        """
        n = self.n_samples

        # Base distributions (normal operational ranges)
        tensile = self.rng.normal(loc=24.0, scale=4.5, size=n)
        elongation = self.rng.normal(loc=16.0, scale=3.5, size=n)
        hairiness = self.rng.normal(loc=4.8, scale=1.4, size=n)
        twist = self.rng.normal(loc=430.0, scale=55.0, size=n)
        dtex = self.rng.normal(loc=2200.0, scale=180.0, size=n)
        rpm = self.rng.normal(loc=610.0, scale=45.0, size=n)
        tension_var = self.rng.normal(loc=26.0, scale=7.5, size=n)
        humidity = self.rng.normal(loc=58.0, scale=7.0, size=n)
        temp = self.rng.normal(loc=24.5, scale=3.2, size=n)
        weft_rate = self.rng.normal(loc=530.0, scale=48.0, size=n)

        # Enforce physical constraints
        tensile = np.clip(tensile, 10.0, 45.0)
        elongation = np.clip(elongation, 4.0, 30.0)
        hairiness = np.clip(hairiness, 1.5, 12.0)
        twist = np.clip(twist, 250.0, 650.0)
        dtex = np.clip(dtex, 1600.0, 2900.0)
        rpm = np.clip(rpm, 450.0, 800.0)
        tension_var = np.clip(tension_var, 8.0, 60.0)
        humidity = np.clip(humidity, 30.0, 85.0)
        temp = np.clip(temp, 16.0, 42.0)
        weft_rate = np.clip(weft_rate, 380.0, 720.0)

        # Allocate 4 defect classes
        labels = np.zeros(n, dtype=int)
        n_breakage = int(n * 0.35)
        n_oil = int(n * 0.20)
        n_jacquard = int(n * 0.25)
        n_border = n - (n_breakage + n_oil + n_jacquard)

        # 0: YARN_BREAKAGE (Low tensile strength, high tension variation, low elongation)
        idx_breakage = np.arange(0, n_breakage)
        tensile[idx_breakage] = self.rng.uniform(10.5, 17.5, size=n_breakage)
        tension_var[idx_breakage] = self.rng.uniform(36.0, 58.0, size=n_breakage)
        elongation[idx_breakage] = self.rng.uniform(4.5, 11.0, size=n_breakage)
        labels[idx_breakage] = DefectClass.YARN_BREAKAGE.value

        # 1: OIL_STAIN (High temp, high hairiness, low humidity)
        idx_oil = np.arange(n_breakage, n_breakage + n_oil)
        temp[idx_oil] = self.rng.uniform(29.5, 40.0, size=n_oil)
        hairiness[idx_oil] = self.rng.uniform(6.8, 11.5, size=n_oil)
        humidity[idx_oil] = self.rng.uniform(32.0, 48.0, size=n_oil)
        labels[idx_oil] = DefectClass.OIL_STAIN.value

        # 2: JACQUARD_PATTERN_SHIFT (High RPM, high weft rate, high dtex)
        idx_jacquard = np.arange(n_breakage + n_oil, n_breakage + n_oil + n_jacquard)
        rpm[idx_jacquard] = self.rng.uniform(660.0, 780.0, size=n_jacquard)
        weft_rate[idx_jacquard] = self.rng.uniform(590.0, 710.0, size=n_jacquard)
        dtex[idx_jacquard] = self.rng.uniform(2380.0, 2850.0, size=n_jacquard)
        labels[idx_jacquard] = DefectClass.JACQUARD_PATTERN_SHIFT.value

        # 3: BORDER_SEWING_DEFECT (Low twist, low dtex, moderate-high tension)
        idx_border = np.arange(n_breakage + n_oil + n_jacquard, n)
        twist[idx_border] = self.rng.uniform(260.0, 340.0, size=n_border)
        dtex[idx_border] = self.rng.uniform(1650.0, 2050.0, size=n_border)
        tension_var[idx_border] = self.rng.uniform(32.0, 46.0, size=n_border)
        labels[idx_border] = DefectClass.BORDER_SEWING_DEFECT.value

        # Boundary perturbation to simulate subtle sensor noise
        if self.noise_level > 0:
            noise_idx = self.rng.choice(n, size=int(n * self.noise_level), replace=False)
            tensile[noise_idx] += self.rng.normal(0, 1.8, size=len(noise_idx))
            tension_var[noise_idx] += self.rng.normal(0, 2.5, size=len(noise_idx))
            temp[noise_idx] += self.rng.normal(0, 1.5, size=len(noise_idx))
            rpm[noise_idx] += self.rng.normal(0, 15.0, size=len(noise_idx))

        # Re-enforce physical limits
        tensile = np.clip(tensile, 10.0, 45.0)
        elongation = np.clip(elongation, 4.0, 30.0)
        hairiness = np.clip(hairiness, 1.5, 12.0)
        twist = np.clip(twist, 250.0, 650.0)
        dtex = np.clip(dtex, 1600.0, 2900.0)
        rpm = np.clip(rpm, 450.0, 800.0)
        tension_var = np.clip(tension_var, 8.0, 60.0)
        humidity = np.clip(humidity, 30.0, 85.0)
        temp = np.clip(temp, 16.0, 42.0)
        weft_rate = np.clip(weft_rate, 380.0, 720.0)

        # Shuffle observations
        shuffle_idx = self.rng.permutation(n)

        df = pd.DataFrame({
            "yarn_tensile_strength": np.round(tensile[shuffle_idx], 2),
            "yarn_elongation_at_break": np.round(elongation[shuffle_idx], 2),
            "yarn_hairiness_index": np.round(hairiness[shuffle_idx], 2),
            "twist_per_meter": np.round(twist[shuffle_idx], 1),
            "yarn_linear_density_dtex": np.round(dtex[shuffle_idx], 1),
            "loom_rpm": np.round(rpm[shuffle_idx], 1),
            "loom_tension_variation": np.round(tension_var[shuffle_idx], 2),
            "ambient_relative_humidity": np.round(humidity[shuffle_idx], 1),
            "ambient_temperature_c": np.round(temp[shuffle_idx], 1),
            "weft_insertion_rate": np.round(weft_rate[shuffle_idx], 1),
            "defect_class": labels[shuffle_idx]
        })

        class_map = {
            DefectClass.YARN_BREAKAGE.value: "YARN_BREAKAGE",
            DefectClass.OIL_STAIN.value: "OIL_STAIN",
            DefectClass.JACQUARD_PATTERN_SHIFT.value: "JACQUARD_PATTERN_SHIFT",
            DefectClass.BORDER_SEWING_DEFECT.value: "BORDER_SEWING_DEFECT"
        }
        df["defect_name"] = df["defect_class"].map(class_map)

        return df

    def save_to_csv(self, filepath: str) -> str:
        """Persists the generated dataset to CSV."""
        df = self.generate()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False, encoding="utf-8")
        return filepath
