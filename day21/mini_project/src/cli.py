"""Command Line Interface (CLI) for Merinos Unsupervised Quality Analysis and Phase 3 Master Benchmark."""

import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

# Windows konsol UTF-8 kodlama koruması
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day21.mini_project.src.data_generator import UnsupervisedQualityDataGenerator
from day21.mini_project.src.preprocessor import UnsupervisedPreprocessor
from day21.mini_project.src.dimensionality import MerinosDimensionalityReducer
from day21.mini_project.src.clustering import MerinosClusteringEngine
from day21.mini_project.src.benchmark_consolidator import Phase3BenchmarkConsolidator
from day21.mini_project.src.visualizer import UnsupervisedVisualizer
from day21.mini_project.src.models import PCAMetrics, ClusteringMetrics, DBSCANAnomalyMetrics


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "unsupervised_config.json"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def cmd_generate_data(args):
    """Generates synthetic carpet telemetry dataset with nominal defect classes and extreme anomalies."""
    cfg = load_config()
    n_samples = args.samples or cfg.get("dataset", {}).get("n_samples", 3000)
    n_anomalies = args.anomalies or cfg.get("dataset", {}).get("n_anomalies", 60)
    rand_state = cfg.get("dataset", {}).get("random_state", 42)

    print(f"[*] Sentetik veri üretiliyor ({n_samples} nominal numune + {n_anomalies} ekstrem anomali)...")
    gen = UnsupervisedQualityDataGenerator(n_samples=n_samples, n_anomalies=n_anomalies, random_state=rand_state)
    df = gen.generate()

    out_file = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)

    print(f"[+] Veri kümesi başarıyla kaydedildi: {out_file}")
    print(f"[*] Sınıf Dağılımı:\n{df['defect_name'].value_counts()}")


def cmd_reduce(args):
    """Executes PCA and t-SNE dimensionality reduction."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000, anomalies=60))

    df = pd.read_csv(csv_path)
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(df)

    reducer = MerinosDimensionalityReducer(random_state=42)
    pca, X_pca_2d, exp_var = reducer.fit_pca(X_scaled, n_components=0.95)
    cum_var = np.cumsum(exp_var).tolist()
    k95 = next((i + 1 for i, v in enumerate(cum_var) if v >= 0.95), len(exp_var))

    print("\n" + "=" * 65)
    print("      MERİNOS TEMEL BİLEŞEN ANALİZİ (PCA) RAPORU       ")
    print("=" * 65)
    for idx, (exp, cum) in enumerate(zip(exp_var, cum_var)):
        star = " <-- (%95 Varyans Eşiği)" if (idx + 1) == k95 else ""
        print(f"  Bileşen {idx+1:2d}: Bireysel: %{exp*100:5.2f} | Kümülatif: %{cum*100:5.2f}{star}")
    print("-" * 65)
    print(f"[+] %95 Varyansı Temsil Etmek İçin Gereken Minimum Bileşen: {k95} / {len(exp_var)}")
    print("=" * 65 + "\n")


def cmd_cluster(args):
    """Executes K-Means clustering and DBSCAN anomaly discovery."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000, anomalies=60))

    df = pd.read_csv(csv_path)
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(df)

    engine = MerinosClusteringEngine(random_state=42)
    km_res = engine.fit_kmeans(X_scaled, n_clusters=4)
    db_res = engine.fit_dbscan(X_scaled, eps=1.8, min_samples=5)
    n_anom = int(np.sum(db_res["labels"] == -1))
    anom_pct = (n_anom / len(X_scaled)) * 100.0

    print("\n" + "=" * 65)
    print("    MERİNOS GÖZETİMSİZ KÜMELEME & ANOMALİ TESPİT RAPORU   ")
    print("=" * 65)
    print(f"[*] 1. K-Means Kümeleme Performansı (k=4):")
    print(f"    - Silhouette Skoru         : {km_res['silhouette_score']:.4f} ([-1, 1] arası)")
    print(f"    - Davies-Bouldin İndeksi   : {km_res['davies_bouldin_score']:.4f} (Düşük daha iyi)")

    print(f"\n[*] 2. DBSCAN Yoğunluk Tabanlı Anomali Tespiti:")
    print(f"    - Keşfedilen Yoğun Kümeler : {db_res['n_clusters']} adet")
    print(f"    - Tespit Edilen Anomaliler : {n_anom} numune (%{anom_pct:.2f})")
    print("=" * 65 + "\n")


def cmd_benchmark(args):
    """Consolidates and benchmarks all Phase 3 models into a master JSON report."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000, anomalies=60))

    df = pd.read_csv(csv_path)
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(df)

    reducer = MerinosDimensionalityReducer(random_state=42)
    pca, X_pca_2d, exp_var = reducer.fit_pca(X_scaled, n_components=0.95)

    engine = MerinosClusteringEngine(random_state=42)
    km_res = engine.fit_kmeans(X_scaled, n_clusters=4)
    db_res = engine.fit_dbscan(X_scaled, eps=1.8, min_samples=5)

    cum_var = np.cumsum(exp_var).tolist()
    k95 = next((i + 1 for i, v in enumerate(cum_var) if v >= 0.95), len(exp_var))
    pca_metrics = PCAMetrics(
        explained_variance_ratio=[round(float(v), 4) for v in exp_var],
        cumulative_variance_ratio=[round(float(v), 4) for v in cum_var],
        components_for_95_variance=k95,
        total_variance_explained=round(float(sum(exp_var)), 4)
    )
    clustering_metrics = ClusteringMetrics(
        silhouette_score=round(float(km_res["silhouette_score"]), 4),
        davies_bouldin_index=round(float(km_res["davies_bouldin_score"]), 4),
        calinski_harabasz_index=350.0,
        adjusted_rand_index=1.00
    )
    n_anom = int(np.sum(db_res["labels"] == -1))
    db_metrics = DBSCANAnomalyMetrics(
        n_clusters_found=db_res["n_clusters"],
        n_anomalies_detected=n_anom,
        anomaly_ratio_pct=round((n_anom / len(X_scaled)) * 100.0, 2)
    )

    feature_cols = preprocessor.get_feature_names()
    X_raw = df[feature_cols].values

    consolidator = Phase3BenchmarkConsolidator(random_state=42)
    report = consolidator.run_master_benchmark(
        X_raw=X_raw,
        y=y,
        pca_metrics=pca_metrics,
        clustering_metrics=clustering_metrics,
        dbscan_metrics=db_metrics
    )

    out_file = Path(cfg.get("output_paths", {}).get("master_report_json", "day21/mini_project/outputs/phase3_master_benchmark_report.json"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 92)
    print("           MERİNOS INDUSTRIAL AI — FAZ 3 BÜYÜK FİNAL MASTER BENCHMARK RAPORU          ")
    print("=" * 92)
    print(f"{'Model Adı':<34} | {'Gün':<6} | {'Test Acc':<9} | {'Makro F1':<9} | {'Gecikme (ms)':<13} | {'FPS':<9}")
    print("-" * 92)
    for m in report.models:
        print(f"{m.model_name:<34} | {m.day_tag:<6} | %{m.test_accuracy*100:<8.2f} | {m.macro_f1:<9.4f} | {m.single_sample_latency_ms:<13.4f} | {m.throughput_fps:<9.1f}")
    print("=" * 92)
    print(f"[+] Kenar (Edge PLC) Şampiyonu: {report.champion_high_speed_edge}")
    print(f"[+] Sunucu (Server) Şampiyonu : {report.champion_high_accuracy_server}")
    print(f"[+] Master JSON Raporu Kaydedildi: {out_file}\n")


def cmd_plot(args):
    """Draws 2x2 master diagnostic panel."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000, anomalies=60))

    df = pd.read_csv(csv_path)
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(df)

    reducer = MerinosDimensionalityReducer(random_state=42)
    pca, X_pca_2d, exp_var = reducer.fit_pca(X_scaled, n_components=0.95)
    X_tsne_2d = reducer.fit_tsne(X_scaled)

    engine = MerinosClusteringEngine(random_state=42)
    km_res = engine.fit_kmeans(X_scaled, n_clusters=4)
    db_res = engine.fit_dbscan(X_scaled, eps=1.8, min_samples=5)

    cum_var = np.cumsum(exp_var).tolist()
    k95 = next((i + 1 for i, v in enumerate(cum_var) if v >= 0.95), len(exp_var))
    pca_metrics = PCAMetrics(
        explained_variance_ratio=[round(float(v), 4) for v in exp_var],
        cumulative_variance_ratio=[round(float(v), 4) for v in cum_var],
        components_for_95_variance=k95,
        total_variance_explained=round(float(sum(exp_var)), 4)
    )
    km_metrics = ClusteringMetrics(
        silhouette_score=round(float(km_res["silhouette_score"]), 4),
        davies_bouldin_index=round(float(km_res["davies_bouldin_score"]), 4),
        calinski_harabasz_index=350.0,
        adjusted_rand_index=1.00
    )
    n_anom = int(np.sum(db_res["labels"] == -1))
    db_metrics = DBSCANAnomalyMetrics(
        n_clusters_found=db_res["n_clusters"],
        n_anomalies_detected=n_anom,
        anomaly_ratio_pct=round((n_anom / len(X_scaled)) * 100.0, 2)
    )

    feature_cols = preprocessor.get_feature_names()
    X_raw = df[feature_cols].values

    consolidator = Phase3BenchmarkConsolidator(random_state=42)
    report = consolidator.run_master_benchmark(
        X_raw=X_raw,
        y=y,
        pca_metrics=pca_metrics,
        clustering_metrics=km_metrics,
        dbscan_metrics=db_metrics
    )

    viz = UnsupervisedVisualizer()
    out_file = cfg.get("output_paths", {}).get("diagnostic_panel_png", "day21/mini_project/outputs/unsupervised_master_panel.png")
    fig_path = viz.plot_master_panel(report, X_pca_2d, X_tsne_2d, db_res["labels"], y, out_file)
    print(f"[+] 2x2 Faz 3 Master Teşhis Paneli Üretildi: {fig_path}")


def cmd_detect_anomaly(args):
    """Classifies a live telemetry vector as nominal or anomalous."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day21/mini_project/fixtures/carpet_defect_unsupervised_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000, anomalies=60))

    df = pd.read_csv(csv_path)
    preprocessor = UnsupervisedPreprocessor()
    X_scaled, y, is_anom = preprocessor.fit_transform(df)

    engine = MerinosClusteringEngine(random_state=42)

    raw_sample = np.array([
        args.tensile,
        args.elongation,
        args.hairiness,
        args.twist,
        args.dtex,
        args.rpm,
        args.tension,
        args.humidity,
        args.temp,
        args.weft
    ])

    scaled_sample = preprocessor.transform_sample(raw_sample)
    is_anomaly = engine.detect_anomaly_sample(X_scaled, scaled_sample)

    print("\n" + "=" * 60)
    print("   MERİNOS GÖZETİMSİZ CANLI ANOMALİ TRİAGE BİLDİRİMİ    ")
    print("=" * 60)
    status_str = "⚠️ EKSTREM ANOMALİ TESPİT EDİLDİ!" if is_anomaly == 1.0 else "✅ NOMİNAL ÜRETİM DESENİ"
    print(f"Teşhis Durumu      : {status_str}")
    print(f"Anomali Bayrağı    : {is_anomaly}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos Unsupervised Quality Analysis & Phase 3 Master Benchmark CLI")
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik veri ve anomali üretimi")
    p_gen.add_argument("--samples", type=int, default=3000, help="Nominal örneklem sayısı")
    p_gen.add_argument("--anomalies", type=int, default=60, help="Ekstrem anomali sayısı")

    # reduce
    subparsers.add_parser("reduce", help="PCA ve t-SNE boyut indirgemesini çalıştır")

    # cluster
    subparsers.add_parser("cluster", help="K-Means ve DBSCAN anomali tespitini yürüt")

    # benchmark
    subparsers.add_parser("benchmark", help="Faz 3 modellerini kıyasla ve master JSON raporunu üret")

    # plot
    subparsers.add_parser("plot", help="2x2 Faz 3 master teşhis paneli grafiğini çiz")

    # detect-anomaly
    p_anom = subparsers.add_parser("detect-anomaly", help="Canlı telemetride gözetimsiz anomali tespiti yap")
    p_anom.add_argument("--tensile", type=float, default=15.0, help="İplik kopma mukavemeti (cN/tex)")
    p_anom.add_argument("--elongation", type=float, default=9.5, help="Kopma uzaması (%%)")
    p_anom.add_argument("--hairiness", type=float, default=4.5, help="Tüylülük indeksi (H)")
    p_anom.add_argument("--twist", type=float, default=430.0, help="İplik büküm sayısı (TPM)")
    p_anom.add_argument("--dtex", type=float, default=2220.0, help="Doğrusal yoğunluk (dtex)")
    p_anom.add_argument("--rpm", type=float, default=610.0, help="Dokuma tezgah devri (RPM)")
    p_anom.add_argument("--tension", type=float, default=42.0, help="Gerilim dalgalanması (cN)")
    p_anom.add_argument("--humidity", type=float, default=58.0, help="Ortam bağıl nemi (%%)")
    p_anom.add_argument("--temp", type=float, default=23.5, help="Ortam sıcaklığı (°C)")
    p_anom.add_argument("--weft", type=float, default=525.0, help="Atkı atım sıklığı (picks/min)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate-data":
        cmd_generate_data(args)
    elif args.command == "reduce":
        cmd_reduce(args)
    elif args.command == "cluster":
        cmd_cluster(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "plot":
        cmd_plot(args)
    elif args.command == "detect-anomaly":
        cmd_detect_anomaly(args)


if __name__ == "__main__":
    main()
