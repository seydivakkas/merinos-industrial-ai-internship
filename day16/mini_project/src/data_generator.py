import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, List, Union
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class YarnQualityDataGenerator:
    """
    Generate synthetic yarn quality data for binary
    classification (normal vs defective).
    """

    def __init__(
        self,
        n_samples: int = 500,
        defect_ratio: float = 0.1,
        random_state: Optional[int] = 42,
        *args,
        **kwargs,
    ):
        if isinstance(n_samples, (str, Path)):
            config_path = str(n_samples)
            n_samples = 500
        else:
            config_path = kwargs.get("config_path", None)

        self.n_samples = n_samples
        self.defect_ratio = defect_ratio
        self.random_state = random_state
        self.rng = np.random.default_rng(random_state)
        self._init_config(config_path)

    def _generate_features(self, n: int) -> pd.DataFrame:
        """Generate realistic yarn process features."""
        data = {
            "length_mm": self.rng.normal(1000, 50, n),
            "diameter_um": self.rng.normal(250, 15, n),
            "tensile_strength": self.rng.normal(4.0, 0.8, n),
            "twist_per_meter": self.rng.normal(650, 100, n),
            "evenness_cv": self.rng.normal(12, 2.5, n),
            "hairiness": self.rng.normal(3.0, 0.6, n),
        }
        return pd.DataFrame(data)

    def _init_config(self, config_path: Optional[str] = None) -> None:
        """Konfigürasyon dosyasını yükler veya varsayılan parametreleri kullanır."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            default_config_path = (
                Path(__file__).resolve().parent.parent / "configs" / "classification_config.json"
            )
            if default_config_path.exists():
                with open(default_config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = self._get_fallback_config()

        self.ds_cfg = self.config.get("dataset", {})
        self.feature_defs = self.ds_cfg.get("features", [])

    def _get_fallback_config(self) -> Dict:
        """Varsayılan yedek konfigürasyon parametreleri."""
        return {
            "dataset": {
                "n_samples": 2500,
                "defect_ratio": 0.10,
                "random_state": 42,
                "features": [
                    {"name": "yarn_tensile_strength", "normal_mean": 26.5, "normal_std": 2.5, "defect_mean": 17.8, "defect_std": 3.2},
                    {"name": "yarn_elongation_at_break", "normal_mean": 14.2, "normal_std": 1.8, "defect_mean": 8.5, "defect_std": 2.1},
                    {"name": "yarn_hairiness_index", "normal_mean": 4.2, "normal_std": 0.6, "defect_mean": 7.8, "defect_std": 1.2},
                    {"name": "twist_per_meter", "normal_mean": 450.0, "normal_std": 25.0, "defect_mean": 360.0, "defect_std": 40.0},
                    {"name": "yarn_linear_density_dtex", "normal_mean": 2200.0, "normal_std": 50.0, "defect_mean": 2380.0, "defect_std": 90.0},
                    {"name": "loom_speed_rpm", "normal_mean": 620.0, "normal_std": 20.0, "defect_mean": 670.0, "defect_std": 35.0},
                    {"name": "loom_tension_variation", "normal_mean": 18.0, "normal_std": 3.5, "defect_mean": 42.0, "defect_std": 8.0},
                    {"name": "ambient_humidity_percent", "normal_mean": 62.0, "normal_std": 3.0, "defect_mean": 48.0, "defect_std": 7.0},
                    {"name": "ambient_temperature_c", "normal_mean": 23.5, "normal_std": 1.5, "defect_mean": 29.0, "defect_std": 3.0},
                    {"name": "weft_insertion_rate", "normal_mean": 540.0, "normal_std": 15.0, "defect_mean": 590.0, "defect_std": 25.0},
                ],
            }
        }

    def generate_dataset(
        self,
        n_samples: Optional[int] = None,
        defect_ratio: Optional[float] = None,
        random_state: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Dengesiz sınıf dağılımına ve endüstriyel korelasyonlara sahip sentetik sensör veri kümesi üretir.
        """
        n_samples = n_samples or self.n_samples or self.ds_cfg.get("n_samples", 2500)
        defect_ratio = defect_ratio or self.defect_ratio or self.ds_cfg.get("defect_ratio", 0.10)
        seed = random_state if random_state is not None else self.random_state if self.random_state is not None else self.ds_cfg.get("random_state", 42)
        rng = np.random.default_rng(seed)

        n_defects = int(n_samples * defect_ratio)
        n_normal = n_samples - n_defects

        data_dict: Dict[str, np.ndarray] = {}

        for f_def in self.feature_defs:
            fname = f_def["name"]
            norm_mean = f_def["normal_mean"]
            norm_std = f_def["normal_std"]
            def_mean = f_def["defect_mean"]
            def_std = f_def["defect_std"]

            norm_vals = rng.normal(norm_mean, norm_std, size=n_normal)
            def_vals = rng.normal(def_mean, def_std, size=n_defects)

            combined = np.concatenate([norm_vals, def_vals])
            data_dict[fname] = combined

        labels = np.concatenate([np.zeros(n_normal, dtype=int), np.ones(n_defects, dtype=int)])
        data_dict["quality_label"] = labels

        df = pd.DataFrame(data_dict)

        # Endüstriyel çapraz korelasyonlar ekleme
        humidity_penalty = np.clip((55.0 - df["ambient_humidity_percent"]) * 0.15, 0.0, 3.0)
        df["yarn_hairiness_index"] += humidity_penalty
        df["yarn_tensile_strength"] -= humidity_penalty * 0.6

        tension_stress = np.clip((df["loom_tension_variation"] - 20.0) * 0.1, 0.0, 4.0)
        df["yarn_elongation_at_break"] -= tension_stress

        # Pozitif değer kısıtlamaları
        df["yarn_tensile_strength"] = np.clip(df["yarn_tensile_strength"], 5.0, 45.0)
        df["yarn_elongation_at_break"] = np.clip(df["yarn_elongation_at_break"], 2.0, 25.0)
        df["yarn_hairiness_index"] = np.clip(df["yarn_hairiness_index"], 1.0, 15.0)
        df["twist_per_meter"] = np.clip(df["twist_per_meter"], 150.0, 700.0)
        df["loom_tension_variation"] = np.clip(df["loom_tension_variation"], 5.0, 80.0)

        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        return df

    def save_dataset(self, df: pd.DataFrame, output_path: str) -> str:
        """Veri çerçevesini belirtilen yola CSV olarak kaydeder."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_p, index=False, encoding="utf-8")
        return str(out_p)
