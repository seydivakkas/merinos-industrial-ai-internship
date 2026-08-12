import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split


class SVMQualityDataGenerator:
    """Merinos halı üretim süreci için sentetik veri üreteci."""

    def __init__(self, n_samples: int = 5000, random_state: int = 42):
        self.n_samples = n_samples
        self.random_state = random_state
        self.rng = np.random.default_rng(random_state)
        self.defect_classes = [
            "NORMAL",
            "YARN_BREAKAGE",
            "OIL_STAIN",
            "JACQUARD_PATTERN_SHIFT",
            "BORDER_SEWING_DEFECT"
        ]

    def _generate_features(self, n: int) -> pd.DataFrame:
        data = pd.DataFrame({
            "yarn_tensile_strength": self.rng.normal(28.0, 5.0, n),
            "yarn_elongation_at_break": self.rng.normal(6.5, 1.2, n),
            "yarn_hairiness_index": self.rng.normal(3.0, 0.8, n),
            "loom_rpm": self.rng.normal(850.0, 120.0, n),
            "loom_tension_variation": self.rng.normal(0.8, 0.3, n),
            "ambient_temperature_c": self.rng.normal(24.0, 2.5, n),
            "weft_insertion_rate": self.rng.normal(520.0, 60.0, n),
        })
        return data

    def generate(self, n_samples: Optional[int] = None) -> pd.DataFrame:
        """Generates realistic telemetry dataset with full sensor suite and defect classes."""
        total_n = n_samples or self.n_samples
        n_classes = len(self.defect_classes)
        n_per_class = total_n // n_classes

        dfs = []
        for class_idx, class_name in enumerate(self.defect_classes):
            df_class = self._generate_features(n_per_class).copy()

            # Ek telemetri sensörleri (10 öznitelik standardı)
            df_class["twist_per_meter"] = self.rng.normal(430.0, 25.0, n_per_class)
            df_class["yarn_linear_density_dtex"] = self.rng.normal(2220.0, 80.0, n_per_class)
            df_class["ambient_relative_humidity"] = self.rng.normal(58.0, 5.0, n_per_class)

            if class_name == "NORMAL":
                # Standart Merinos üretim sınırları
                df_class["loom_tension_variation"] = np.clip(df_class["loom_tension_variation"] + 15.0, 10.0, 30.0)
            elif class_name == "YARN_BREAKAGE":
                df_class["yarn_tensile_strength"] = self.rng.normal(15.0, 2.0, n_per_class)
                df_class["yarn_elongation_at_break"] = self.rng.normal(9.5, 1.5, n_per_class)
                df_class["yarn_hairiness_index"] = self.rng.normal(4.5, 0.8, n_per_class)
                df_class["loom_tension_variation"] = self.rng.normal(42.0, 4.0, n_per_class)
                df_class["loom_rpm"] = self.rng.normal(610.0, 35.0, n_per_class)
            elif class_name == "OIL_STAIN":
                df_class["yarn_tensile_strength"] = self.rng.normal(26.0, 3.0, n_per_class)
                df_class["yarn_elongation_at_break"] = self.rng.normal(17.0, 2.5, n_per_class)
                df_class["yarn_hairiness_index"] = self.rng.normal(7.5, 0.9, n_per_class)
                df_class["ambient_temperature_c"] = self.rng.normal(31.5, 1.8, n_per_class)
                df_class["ambient_relative_humidity"] = self.rng.normal(43.0, 3.5, n_per_class)
                df_class["loom_tension_variation"] = self.rng.normal(22.0, 3.5, n_per_class)
            elif class_name == "JACQUARD_PATTERN_SHIFT":
                df_class["loom_rpm"] = self.rng.normal(710.0, 25.0, n_per_class)
                df_class["weft_insertion_rate"] = self.rng.normal(630.0, 25.0, n_per_class)
                df_class["yarn_linear_density_dtex"] = self.rng.normal(2480.0, 70.0, n_per_class)
                df_class["twist_per_meter"] = self.rng.normal(460.0, 20.0, n_per_class)
                df_class["loom_tension_variation"] = self.rng.normal(24.0, 3.0, n_per_class)
            elif class_name == "BORDER_SEWING_DEFECT":
                df_class["yarn_tensile_strength"] = self.rng.normal(24.0, 3.0, n_per_class)
                df_class["yarn_elongation_at_break"] = self.rng.normal(16.0, 2.5, n_per_class)
                df_class["twist_per_meter"] = self.rng.normal(315.0, 20.0, n_per_class)
                df_class["yarn_linear_density_dtex"] = self.rng.normal(1960.0, 60.0, n_per_class)
                df_class["loom_rpm"] = self.rng.normal(590.0, 35.0, n_per_class)
                df_class["loom_tension_variation"] = self.rng.normal(20.0, 3.5, n_per_class)

            # Sınır kırpmaları
            df_class["yarn_tensile_strength"] = np.clip(df_class["yarn_tensile_strength"], 10.0, 40.0)
            df_class["yarn_elongation_at_break"] = np.clip(df_class["yarn_elongation_at_break"], 6.0, 28.0)
            df_class["yarn_hairiness_index"] = np.clip(df_class["yarn_hairiness_index"], 2.0, 10.0)
            df_class["twist_per_meter"] = np.clip(df_class["twist_per_meter"], 250.0, 650.0)
            df_class["yarn_linear_density_dtex"] = np.clip(df_class["yarn_linear_density_dtex"], 1700.0, 2800.0)
            df_class["loom_rpm"] = np.clip(df_class["loom_rpm"], 450.0, 800.0)
            df_class["loom_tension_variation"] = np.clip(df_class["loom_tension_variation"], 5.0, 60.0)
            df_class["ambient_relative_humidity"] = np.clip(df_class["ambient_relative_humidity"], 35.0, 80.0)
            df_class["ambient_temperature_c"] = np.clip(df_class["ambient_temperature_c"], 16.0, 38.0)
            df_class["weft_insertion_rate"] = np.clip(df_class["weft_insertion_rate"], 400.0, 700.0)

            df_class["defect_class"] = class_idx
            df_class["defect_name"] = class_name
            dfs.append(df_class)

        df = pd.concat(dfs, ignore_index=True)

        ordered_cols = [
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
            "defect_class",
            "defect_name"
        ]
        df = df[ordered_cols].round(2)
        return df.sample(frac=1.0, random_state=self.random_state).reset_index(drop=True)
