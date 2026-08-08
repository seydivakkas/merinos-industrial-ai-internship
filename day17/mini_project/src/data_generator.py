import numpy as np
import pandas as pd
from typing import Tuple, Dict
from sklearn.datasets import make_classification

class MulticlassQualityDataGenerator:
    '''Merinos halı & iplik üretim sürecini temsil eden
    sentetik veri üretir sınıf.
    Dört farklı kusur türü için veri oluşturur.
    '''
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.n_samples = self.config.get("n_samples", 3000)
        self.random_state = self.config.get("random_state", 42)
        self.feature_names = [
            "yarn_strength",
            "yarn_twist",
            "loom_speed",
            "tension_variation",
            "temperature",
            "humidity",
            "yarn_thickness",
            "fabric_density",
            "warp_irregularity",
            "weft_irregularity",
        ]
        self.class_names = [
            "iplik_kopmasi",
            "yag_lekesi",
            "jakar_desen_kaymasi",
            "kenar_dikis_hatasi",
        ]

    def generate_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        4 farklı kusur türüne göre ayırt edici sensör dağılımlarına sahip çok sınıflı veri üretir.
        """
        return self._generate_internal()

    def _generate_internal(
        self,
        n_samples: int = None,
        random_state: int = None,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        4 farklı kusur türüne göre ayırt edici sensör dağılımlarına sahip çok sınıflı veri üretir.
        """
        n_samples = n_samples or self.n_samples or self.ds_cfg.get("n_samples", 3000)
        seed = random_state if random_state is not None else self.random_state if self.random_state is not None else self.ds_cfg.get("random_state", 42)
        proportions = self.ds_cfg.get("class_proportions", [0.35, 0.20, 0.25, 0.20])

        rng = np.random.default_rng(seed)

        # Sınıf başına örneklem sayıları (3000 için: 1050, 600, 750, 600)
        counts = [int(n_samples * p) for p in proportions]
        counts[-1] = n_samples - sum(counts[:-1])

        dfs = []

        # -------------------------------------------------------------
        # Sınıf 0: YARN_BREAKAGE (İplik / Çözgü Kopması)
        # Kritik: Düşük mukavemet, yüksek gerilim dalgalanması, düşük esneme, yüksek devir
        # -------------------------------------------------------------
        n0 = counts[0]
        df0 = pd.DataFrame({
            "yarn_tensile_strength": rng.normal(15.0, 2.0, size=n0),
            "yarn_elongation_at_break": rng.normal(7.2, 1.2, size=n0),
            "yarn_hairiness_index": rng.normal(5.8, 1.0, size=n0),
            "twist_per_meter": rng.normal(410.0, 30.0, size=n0),
            "yarn_linear_density_dtex": rng.normal(2220.0, 55.0, size=n0),
            "loom_speed_rpm": rng.normal(675.0, 20.0, size=n0),
            "loom_tension_variation": rng.normal(48.0, 6.0, size=n0),
            "ambient_humidity_percent": rng.normal(54.0, 5.0, size=n0),
            "ambient_temperature_c": rng.normal(25.0, 2.0, size=n0),
            "weft_insertion_rate": rng.normal(555.0, 20.0, size=n0),
            "defect_class": np.full(n0, DefectClass.YARN_BREAKAGE.value, dtype=int),
        })
        dfs.append(df0)

        # -------------------------------------------------------------
        # Sınıf 1: OIL_STAIN (Mekanik Yağ Lekesi)
        # Kritik: Yüksek ortam sıcaklığı, aşırı tüylülük (lif emilimi), düşük nem, normal mukavemet
        # -------------------------------------------------------------
        n1 = counts[1]
        df1 = pd.DataFrame({
            "yarn_tensile_strength": rng.normal(24.5, 2.2, size=n1),
            "yarn_elongation_at_break": rng.normal(13.5, 1.5, size=n1),
            "yarn_hairiness_index": rng.normal(8.8, 1.1, size=n1),
            "twist_per_meter": rng.normal(445.0, 25.0, size=n1),
            "yarn_linear_density_dtex": rng.normal(2210.0, 45.0, size=n1),
            "loom_speed_rpm": rng.normal(625.0, 18.0, size=n1),
            "loom_tension_variation": rng.normal(21.0, 4.0, size=n1),
            "ambient_humidity_percent": rng.normal(38.0, 4.0, size=n1),
            "ambient_temperature_c": rng.normal(33.5, 2.0, size=n1),
            "weft_insertion_rate": rng.normal(542.0, 15.0, size=n1),
            "defect_class": np.full(n1, DefectClass.OIL_STAIN.value, dtype=int),
        })
        dfs.append(df1)

        # -------------------------------------------------------------
        # Sınıf 2: JACQUARD_PATTERN_SHIFT (Jakar Desen Kayması)
        # Kritik: Çok yüksek atkı atım sıklığı, devir dalgalanması, yüksek dtex sapması
        # -------------------------------------------------------------
        n2 = counts[2]
        df2 = pd.DataFrame({
            "yarn_tensile_strength": rng.normal(25.8, 2.0, size=n2),
            "yarn_elongation_at_break": rng.normal(14.0, 1.6, size=n2),
            "yarn_hairiness_index": rng.normal(4.3, 0.7, size=n2),
            "twist_per_meter": rng.normal(455.0, 20.0, size=n2),
            "yarn_linear_density_dtex": rng.normal(2340.0, 60.0, size=n2),
            "loom_speed_rpm": rng.normal(690.0, 25.0, size=n2),
            "loom_tension_variation": rng.normal(28.0, 5.0, size=n2),
            "ambient_humidity_percent": rng.normal(60.0, 4.0, size=n2),
            "ambient_temperature_c": rng.normal(24.0, 2.0, size=n2),
            "weft_insertion_rate": rng.normal(615.0, 22.0, size=n2),
            "defect_class": np.full(n2, DefectClass.JACQUARD_PATTERN_SHIFT.value, dtype=int),
        })
        dfs.append(df2)

        # -------------------------------------------------------------
        # Sınıf 3: BORDER_SEWING_DEFECT (Kenar Dikiş / Overlok Hatası)
        # Kritik: Düşük büküm (twist), dengesiz gerilim, düşük yoğunluk
        # -------------------------------------------------------------
        n3 = counts[3]
        df3 = pd.DataFrame({
            "yarn_tensile_strength": rng.normal(23.0, 2.0, size=n3),
            "yarn_elongation_at_break": rng.normal(12.8, 1.4, size=n3),
            "yarn_hairiness_index": rng.normal(4.8, 0.8, size=n3),
            "twist_per_meter": rng.normal(320.0, 25.0, size=n3),
            "yarn_linear_density_dtex": rng.normal(2050.0, 50.0, size=n3),
            "loom_speed_rpm": rng.normal(610.0, 15.0, size=n3),
            "loom_tension_variation": rng.normal(36.0, 5.0, size=n3),
            "ambient_humidity_percent": rng.normal(58.0, 3.5, size=n3),
            "ambient_temperature_c": rng.normal(23.0, 1.5, size=n3),
            "weft_insertion_rate": rng.normal(530.0, 15.0, size=n3),
            "defect_class": np.full(n3, DefectClass.BORDER_SEWING_DEFECT.value, dtype=int),
        })
        dfs.append(df3)

        df = pd.concat(dfs, ignore_index=True)

        # Fiziksel sınırların denetimi (clip)
        df["yarn_tensile_strength"] = np.clip(df["yarn_tensile_strength"], 5.0, 45.0)
        df["yarn_elongation_at_break"] = np.clip(df["yarn_elongation_at_break"], 2.0, 25.0)
        df["yarn_hairiness_index"] = np.clip(df["yarn_hairiness_index"], 1.0, 15.0)
        df["twist_per_meter"] = np.clip(df["twist_per_meter"], 150.0, 650.0)
        df["yarn_linear_density_dtex"] = np.clip(df["yarn_linear_density_dtex"], 1500.0, 3000.0)
        df["loom_speed_rpm"] = np.clip(df["loom_speed_rpm"], 450.0, 800.0)
        df["loom_tension_variation"] = np.clip(df["loom_tension_variation"], 5.0, 70.0)
        df["ambient_humidity_percent"] = np.clip(df["ambient_humidity_percent"], 20.0, 90.0)
        df["ambient_temperature_c"] = np.clip(df["ambient_temperature_c"], 15.0, 45.0)
        df["weft_insertion_rate"] = np.clip(df["weft_insertion_rate"], 400.0, 750.0)

        # Karıştırma (Shuffle)
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        return df

    def save_dataset(self, df: pd.DataFrame, output_path: str) -> str:
        """Veri çerçevesini belirtilen CSV dosyasına yazar."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p, index=False, encoding="utf-8")
        return str(p)


from pathlib import Path
import json
from typing import Optional
from .models import DefectClass

_orig_gen_init = MulticlassQualityDataGenerator.__init__
def _compat_gen_init(self, config: Dict = None, config_path: Optional[str] = None, *args, **kwargs):
    if isinstance(config, (str, Path)):
        config_path = str(config)
        config = None
    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            loaded_cfg = json.load(f)
    else:
        default_p = Path(__file__).resolve().parent.parent / "configs" / "multiclass_config.json"
        if default_p.exists():
            with open(default_p, "r", encoding="utf-8") as f:
                loaded_cfg = json.load(f)
        else:
            loaded_cfg = {}
    if config and isinstance(config, dict):
        loaded_cfg.update(config)
    _orig_gen_init(self, config=loaded_cfg)
    self.ds_cfg = self.config.get("dataset", self.config)

MulticlassQualityDataGenerator.__init__ = _compat_gen_init

_orig_generate = MulticlassQualityDataGenerator.generate_dataset
def _compat_generate(self, n_samples: Optional[int] = None, random_state: Optional[int] = None, *args, **kwargs):
    return self._generate_internal(n_samples=n_samples, random_state=random_state)

MulticlassQualityDataGenerator.generate_dataset = _compat_generate

