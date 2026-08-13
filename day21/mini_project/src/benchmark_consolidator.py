"""Consolidates and benchmarks all Phase 3 classical ML models on common telemetry testbed."""

import time
from typing import List, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from day21.mini_project.src.models import (
    Phase3ModelEntry,
    Phase3MasterReport,
    PCAMetrics,
    ClusteringMetrics,
    DBSCANAnomalyMetrics
)


class Phase3BenchmarkConsolidator:
    """Executes standardized cross-model evaluation across all Phase 3 algorithms."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def run_master_benchmark(
        self,
        X_raw: np.ndarray,
        y: np.ndarray,
        pca_metrics: PCAMetrics,
        clustering_metrics: ClusteringMetrics,
        dbscan_metrics: DBSCANAnomalyMetrics
    ) -> Phase3MasterReport:
        """Trains and benchmarks 7 major Phase 3 models under identical test partitions."""
        # Filter out anomaly label (-1) to evaluate supervised models on nominal defect categories
        nominal_mask = y >= 0
        X_nom = X_raw[nominal_mask]
        y_nom = y[nominal_mask]

        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_nom, y_nom, test_size=0.20, random_state=self.random_state, stratify=y_nom
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_test_scaled = scaler.transform(X_test_raw)

        models_to_evaluate = [
            (
                "Multinomial Logistic Regression",
                "Day 17",
                "Doğrusal Hiper-Düzlem (Softmax)",
                LogisticRegression(max_iter=500, random_state=self.random_state),
                True, # uses scaled data
                "Orta (Düşük Parametre)",
                "SCADA İkincil Denetim & İstatistiksel Raporlama"
            ),
            (
                "Cost-Complexity Pruned Decision Tree",
                "Day 18",
                "Eksene Dik Karar Ağacı (Pruned)",
                DecisionTreeClassifier(ccp_alpha=0.0004, random_state=self.random_state),
                False, # tree doesn't strictly need scaling
                "En Düşük (Kural Ağacı)",
                "Kenar PLC / Mikrodenetleyici (Ultra Düşük Gecikme)"
            ),
            (
                "Random Forest Classifier",
                "Day 18",
                "Topluluk Öğrenmesi (Bagging & Subspace)",
                RandomForestClassifier(n_estimators=100, random_state=self.random_state, n_jobs=-1),
                False,
                "Yüksek (100 Ağaç)",
                "Sunucu / MLOps Kalite Triage Katmanı"
            ),
            (
                "XGBoost Classifier",
                "Day 19",
                "Gradient Boosting (2. Derece Taylor)",
                xgb.XGBClassifier(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=self.random_state, n_jobs=-1),
                False,
                "Orta-Yüksek",
                "Yüksek Hızlı Kamera Denetim Hattı"
            ),
            (
                "LightGBM Classifier",
                "Day 19",
                "Gradient Boosting (Leaf-wise & Histogram)",
                lgb.LGBMClassifier(n_estimators=100, learning_rate=0.08, num_leaves=15, random_state=self.random_state, n_jobs=-1, verbose=-1),
                False,
                "Orta (Histogram Sıkıştırma)",
                "Sürekli Yeniden Eğitim (Continuous Retraining)"
            ),
            (
                "Linear Support Vector Machine",
                "Day 20",
                "Maksimum Marjin Hiper-Düzlem",
                SVC(kernel="linear", C=1.0, random_state=self.random_state),
                True,
                "En Düşük (Sadece w ve b Vektörü)",
                "Kenar PLC & Donanımsal FPGA / DSP"
            ),
            (
                "RBF (Gaussian) Support Vector Machine",
                "Day 20",
                "Çekirdek Hilesi (Sonsuz Boyutlu Hilbert)",
                SVC(kernel="rbf", C=10.0, gamma="scale", random_state=self.random_state),
                True,
                "Düşük (Destek Vektörleri)",
                "Laboratuvar İplik & Halı Test Cihazları"
            )
        ]

        model_entries: List[Phase3ModelEntry] = []

        for name, day, paradigm, clf, use_scaled, mem_rank, deploy_tier in models_to_evaluate:
            X_tr = X_train_scaled if use_scaled else X_train_raw
            X_te = X_test_scaled if use_scaled else X_test_raw

            # Train time
            t0 = time.perf_counter()
            clf.fit(X_tr, y_train)
            t1 = time.perf_counter()
            train_time_ms = (t1 - t0) * 1000.0

            # Predictions
            y_pred = clf.predict(X_te)
            acc = float(accuracy_score(y_test, y_pred))
            f1 = float(f1_score(y_test, y_pred, average="macro"))

            # Latency benchmark
            sample = X_te[:1]
            for _ in range(15):
                clf.predict(sample)
            t_lat0 = time.perf_counter()
            n_runs = 150
            for _ in range(n_runs):
                clf.predict(sample)
            t_lat1 = time.perf_counter()
            latency_ms = ((t_lat1 - t_lat0) / n_runs) * 1000.0
            throughput_fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0

            model_entries.append(
                Phase3ModelEntry(
                    model_name=name,
                    day_tag=day,
                    paradigm=paradigm,
                    test_accuracy=round(acc, 4),
                    macro_f1=round(f1, 4),
                    training_time_ms=round(train_time_ms, 2),
                    single_sample_latency_ms=round(latency_ms, 4),
                    throughput_fps=round(throughput_fps, 1),
                    memory_footprint_rank=mem_rank,
                    industrial_deployment_tier=deploy_tier
                )
            )

        # Champion selection
        fastest_edge = min(model_entries, key=lambda m: m.single_sample_latency_ms)
        best_server = max(model_entries, key=lambda m: (m.test_accuracy, m.macro_f1))

        conclusion = (
            f"Faz 3 kapsamında geliştirilen 7 model başarıyla kıyaslanmıştır. "
            f"Kenar PLC konuşlandırması için en düşük gecikmeyle ({fastest_edge.single_sample_latency_ms} ms / {fastest_edge.throughput_fps} FPS) "
            f"'{fastest_edge.model_name}' şampiyon seçilmiştir. "
            f"Merkezi MLOps sunucusu kalite triage'ı için ise %{best_server.test_accuracy*100:.2f} doğrulukla "
            f"'{best_server.model_name}' en kararlı omurga olarak belirlenmiştir."
        )

        return Phase3MasterReport(
            total_models_evaluated=len(model_entries),
            dataset_samples=len(X_raw),
            pca_metrics=pca_metrics,
            clustering_metrics=clustering_metrics,
            dbscan_metrics=dbscan_metrics,
            models=model_entries,
            champion_high_speed_edge=fastest_edge.model_name,
            champion_high_accuracy_server=best_server.model_name,
            phase_conclusion_summary=conclusion
        )
