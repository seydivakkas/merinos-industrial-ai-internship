"""Synthetic telemetry generator supporting 4 defect classes and novel anomalies for unsupervised learning."""

import numpy as np
import pandas as pd


class UnsupervisedQualityDataGenerator:
    """Generates synthetic loom telemetry with 4 primary defect classes plus extreme noise anomalies."""

    def __init__(self, n_samples: int = 3000, n_anomalies: int = 60, random_state: int = 42):
        self.n_samples = n_samples
        self.n_anomalies = n_anomalies
        self.random_state = random_state

    def generate(self) -> pd.DataFrame:
        """Generates realistic telemetry dataset with 10 features, 4 standard classes, and outlier anomalies."""
        rng = np.random.RandomState(self.random_state)
        n_per_class = self.n_samples // 4

        # 1. YARN_BREAKAGE (0): Düşük mukavemet, yüksek gerilim
        tensile_0 = rng.normal(15.0, 2.0, n_per_class)
        elongation_0 = rng.normal(9.5, 1.5, n_per_class)
        hairiness_0 = rng.normal(4.5, 0.8, n_per_class)
        twist_0 = rng.normal(430.0, 25.0, n_per_class)
        dtex_0 = rng.normal(2220.0, 80.0, n_per_class)
        rpm_0 = rng.normal(610.0, 35.0, n_per_class)
        tension_0 = rng.normal(42.0, 4.0, n_per_class)
        humidity_0 = rng.normal(58.0, 5.0, n_per_class)
        temp_0 = rng.normal(23.5, 2.0, n_per_class)
        weft_0 = rng.normal(525.0, 30.0, n_per_class)
        labels_0 = np.zeros(n_per_class, dtype=int)

        # 2. OIL_STAIN (1): Yüksek sıcaklık, düşük nem, yüksek tüylülük
        tensile_1 = rng.normal(26.0, 3.0, n_per_class)
        elongation_1 = rng.normal(17.0, 2.5, n_per_class)
        hairiness_1 = rng.normal(7.5, 0.9, n_per_class)
        twist_1 = rng.normal(440.0, 25.0, n_per_class)
        dtex_1 = rng.normal(2240.0, 80.0, n_per_class)
        rpm_1 = rng.normal(625.0, 35.0, n_per_class)
        tension_1 = rng.normal(22.0, 3.5, n_per_class)
        humidity_1 = rng.normal(43.0, 3.5, n_per_class)
        temp_1 = rng.normal(31.5, 1.8, n_per_class)
        weft_1 = rng.normal(540.0, 30.0, n_per_class)
        labels_1 = np.ones(n_per_class, dtype=int)

        # 3. JACQUARD_PATTERN_SHIFT (2): Yüksek devir ve atkı frekansı
        tensile_2 = rng.normal(27.5, 2.5, n_per_class)
        elongation_2 = rng.normal(18.0, 2.0, n_per_class)
        hairiness_2 = rng.normal(4.2, 0.7, n_per_class)
        twist_2 = rng.normal(460.0, 20.0, n_per_class)
        dtex_2 = rng.normal(2480.0, 70.0, n_per_class)
        rpm_2 = rng.normal(710.0, 25.0, n_per_class)
        tension_2 = rng.normal(24.0, 3.0, n_per_class)
        humidity_2 = rng.normal(60.0, 4.5, n_per_class)
        temp_2 = rng.normal(24.5, 2.0, n_per_class)
        weft_2 = rng.normal(630.0, 25.0, n_per_class)
        labels_2 = np.full(n_per_class, 2, dtype=int)

        # 4. BORDER_SEWING_DEFECT (3): Düşük büküm ve düşük dtex
        tensile_3 = rng.normal(24.0, 3.0, n_per_class)
        elongation_3 = rng.normal(16.0, 2.5, n_per_class)
        hairiness_3 = rng.normal(4.0, 0.8, n_per_class)
        twist_3 = rng.normal(315.0, 20.0, n_per_class)
        dtex_3 = rng.normal(1960.0, 60.0, n_per_class)
        rpm_3 = rng.normal(590.0, 35.0, n_per_class)
        tension_3 = rng.normal(20.0, 3.5, n_per_class)
        humidity_3 = rng.normal(62.0, 4.5, n_per_class)
        temp_3 = rng.normal(23.0, 2.0, n_per_class)
        weft_3 = rng.normal(510.0, 30.0, n_per_class)
        labels_3 = np.full(n_per_class, 3, dtype=int)

        # 5. NOVEL ANOMALIES (label -1): Ekstrem sensör hataları ve mekanik şok anomalileri
        tensile_anom = rng.uniform(5.0, 45.0, self.n_anomalies)
        elongation_anom = rng.uniform(3.0, 32.0, self.n_anomalies)
        hairiness_anom = rng.uniform(1.0, 12.0, self.n_anomalies)
        twist_anom = rng.uniform(200.0, 700.0, self.n_anomalies)
        dtex_anom = rng.uniform(1500.0, 3000.0, self.n_anomalies)
        rpm_anom = rng.uniform(400.0, 850.0, self.n_anomalies)
        tension_anom = rng.uniform(60.0, 85.0, self.n_anomalies)  # Ekstrem gerilim şoku
        humidity_anom = rng.uniform(25.0, 90.0, self.n_anomalies) # Ekstrem iklim sapması
        temp_anom = rng.uniform(12.0, 45.0, self.n_anomalies)     # Ekstrem motor ısınması
        weft_anom = rng.uniform(350.0, 750.0, self.n_anomalies)
        labels_anom = np.full(self.n_anomalies, -1, dtype=int)

        tensile = np.concatenate([tensile_0, tensile_1, tensile_2, tensile_3, tensile_anom])
        elongation = np.concatenate([elongation_0, elongation_1, elongation_2, elongation_3, elongation_anom])
        hairiness = np.concatenate([hairiness_0, hairiness_1, hairiness_2, hairiness_3, hairiness_anom])
        twist = np.concatenate([twist_0, twist_1, twist_2, twist_3, twist_anom])
        dtex = np.concatenate([dtex_0, dtex_1, dtex_2, dtex_3, dtex_anom])
        rpm = np.concatenate([rpm_0, rpm_1, rpm_2, rpm_3, rpm_anom])
        tension = np.concatenate([tension_0, tension_1, tension_2, tension_3, tension_anom])
        humidity = np.concatenate([humidity_0, humidity_1, humidity_2, humidity_3, humidity_anom])
        temp = np.concatenate([temp_0, temp_1, temp_2, temp_3, temp_anom])
        weft = np.concatenate([weft_0, weft_1, weft_2, weft_3, weft_anom])
        labels = np.concatenate([labels_0, labels_1, labels_2, labels_3, labels_anom])

        defect_names = {
            0: "YARN_BREAKAGE",
            1: "OIL_STAIN",
            2: "JACQUARD_PATTERN_SHIFT",
            3: "BORDER_SEWING_DEFECT",
            -1: "ANOMALOUS_NOISE"
        }

        df = pd.DataFrame({
            "yarn_tensile_strength": np.round(tensile, 2),
            "yarn_elongation_at_break": np.round(elongation, 2),
            "yarn_hairiness_index": np.round(hairiness, 2),
            "twist_per_meter": np.round(twist, 1),
            "yarn_linear_density_dtex": np.round(dtex, 1),
            "loom_rpm": np.round(rpm, 1),
            "loom_tension_variation": np.round(tension, 2),
            "ambient_relative_humidity": np.round(humidity, 1),
            "ambient_temperature_c": np.round(temp, 1),
            "weft_insertion_rate": np.round(weft, 1),
            "defect_class": labels,
            "defect_name": [defect_names[l] for l in labels],
            "is_anomaly": labels == -1
        })

        return df.sample(frac=1.0, random_state=self.random_state).reset_index(drop=True)
