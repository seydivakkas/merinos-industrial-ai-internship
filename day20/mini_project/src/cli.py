"""Command Line Interface (CLI) for Merinos SVM Defect Classification."""

import argparse
import json
from pathlib import Path
import sys
import numpy as np

# Windows konsol UTF-8 kodlama koruması
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day20.mini_project.src.data_generator import SVMQualityDataGenerator
from day20.mini_project.src.preprocessor import SVMDataPreprocessor
from day20.mini_project.src.svm_models import MerinosSVMClassifier
from day20.mini_project.src.evaluator import SVMEvaluator
from day20.mini_project.src.visualizer import SVMVisualizer
from day20.mini_project.src.models import DefectClass


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "svm_config.json"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def cmd_generate_data(args):
    """Generates synthetic carpet defect telemetry dataset for SVM."""
    cfg = load_config()
    n_samples = args.samples or cfg.get("dataset", {}).get("n_samples", 3000)
    rand_state = cfg.get("dataset", {}).get("random_state", 42)

    print(f"[*] Sentetik SVM telemetri verisi üretiliyor (Örneklem: {n_samples})...")
    gen = SVMQualityDataGenerator(n_samples=n_samples, random_state=rand_state)
    df = gen.generate()

    out_file = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)

    print(f"[+] Veri kümesi başarıyla kaydedildi: {out_file}")
    print(f"[*] Sınıf Dağılımı:\n{df['defect_name'].value_counts()}")


def cmd_train(args):
    """Trains Linear, Polynomial, and RBF SVM models and prints performance."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000))

    import pandas as pd
    df = pd.read_csv(csv_path)

    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    print("\n" + "=" * 65)
    print("        MERİNOS DESTEK VEKTÖR MAKİNELERİ (SVM) EĞİTİMİ        ")
    print("=" * 65)

    # 1. Linear SVM
    lin_clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42)
    lin_clf.fit(X_train, y_train)
    lin_m = SVMEvaluator.evaluate_model(lin_clf, X_train, y_train, X_test, y_test)
    print(f"[*] 1. Linear SVM (C=1.0):")
    print(f"    - Test Doğruluğu: %{lin_m.test_accuracy * 100:.2f} | Makro F1: {lin_m.macro_f1:.4f}")
    print(f"    - Destek Vektörü: {lin_m.support_vectors.total_support_vectors} adet (%{lin_m.support_vectors.support_vector_ratio_pct:.1f})")
    print(f"    - Eğitim Süresi : {lin_m.training_time_ms:.1f} ms | Gecikme: {lin_m.single_sample_latency_ms:.4f} ms")

    # 2. Polynomial SVM
    poly_clf = MerinosSVMClassifier(kernel="poly", degree=3, coef0=1.0, C=1.0, random_state=42)
    poly_clf.fit(X_train, y_train)
    poly_m = SVMEvaluator.evaluate_model(poly_clf, X_train, y_train, X_test, y_test)
    print(f"\n[*] 2. Polynomial SVM (Degree=3, Coef0=1.0, C=1.0):")
    print(f"    - Test Doğruluğu: %{poly_m.test_accuracy * 100:.2f} | Makro F1: {poly_m.macro_f1:.4f}")
    print(f"    - Destek Vektörü: {poly_m.support_vectors.total_support_vectors} adet (%{poly_m.support_vectors.support_vector_ratio_pct:.1f})")
    print(f"    - Eğitim Süresi : {poly_m.training_time_ms:.1f} ms | Gecikme: {poly_m.single_sample_latency_ms:.4f} ms")

    # 3. RBF SVM
    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42)
    rbf_clf.fit(X_train, y_train)
    rbf_m = SVMEvaluator.evaluate_model(rbf_clf, X_train, y_train, X_test, y_test)
    print(f"\n[*] 3. RBF (Gaussian) SVM (C=10.0, gamma='scale'):")
    print(f"    - Test Doğruluğu: %{rbf_m.test_accuracy * 100:.2f} | Makro F1: {rbf_m.macro_f1:.4f}")
    print(f"    - Destek Vektörü: {rbf_m.support_vectors.total_support_vectors} adet (%{rbf_m.support_vectors.support_vector_ratio_pct:.1f})")
    print(f"    - Eğitim Süresi : {rbf_m.training_time_ms:.1f} ms | Gecikme: {rbf_m.single_sample_latency_ms:.4f} ms")
    print("=" * 65 + "\n")


def cmd_tune(args):
    """Executes grid search over C and gamma regularization parameters."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000))

    import pandas as pd
    df = pd.read_csv(csv_path)

    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    c_vals = cfg.get("grid_search", {}).get("C_values", [0.1, 1.0, 10.0, 100.0])
    g_vals = cfg.get("grid_search", {}).get("gamma_values", [0.001, 0.01, 0.1, 1.0])

    print("\n[*] RBF SVM Hiperparametre Optimizasyonu Başlatılıyor...")
    print(f"[*] Parametre Ağı: C={c_vals}, gamma={g_vals}\n")

    grid_res = SVMEvaluator.tune_hyperparameters(
        X_train, y_train, X_test, y_test,
        C_values=c_vals,
        gamma_values=g_vals,
        cv_folds=3
    )

    print("=" * 65)
    print(f"{'C Değeri':<12} | {'Gamma (γ)':<12} | {'CV Doğruluk':<16} | {'Test Doğruluk':<16}")
    print("-" * 65)
    for rec in grid_res.grid_records:
        print(f"{rec.C:<12} | {rec.gamma:<12} | %{rec.mean_cv_accuracy * 100:<15.2f} | %{rec.test_accuracy * 100:<15.2f}")
    print("=" * 65)
    print(f"[+] Optimal Konfigürasyon: C={grid_res.best_C}, gamma={grid_res.best_gamma} (CV Acc: %{grid_res.best_score * 100:.2f})\n")


def cmd_evaluate(args):
    """Evaluates all SVM kernels and dumps the master comparison JSON report."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000))

    import pandas as pd
    df = pd.read_csv(csv_path)

    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    lin_clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42).fit(X_train, y_train)
    poly_clf = MerinosSVMClassifier(kernel="poly", degree=3, coef0=1.0, C=1.0, random_state=42).fit(X_train, y_train)
    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    grid_res = SVMEvaluator.tune_hyperparameters(X_train, y_train, X_test, y_test)

    report = SVMEvaluator.generate_comparison_report(
        linear_model=lin_clf,
        poly_model=poly_clf,
        rbf_model=rbf_clf,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        grid_result=grid_res
    )

    out_file = Path(cfg.get("output_paths", {}).get("master_report_json", "day20/mini_project/outputs/svm_master_report.json"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 74)
    print("      MERİNOS DESTEK VEKTÖR MAKİNELERİ (SVM) KIYASLAMA RAPORU     ")
    print("=" * 74)
    print(f"{'Metrik':<28} | {'Linear SVM':<14} | {'Poly SVM':<14} | {'RBF SVM':<14}")
    print("-" * 74)
    print(f"{'Test Doğruluğu':<28} | %{report.linear_metrics.test_accuracy * 100:<13.2f} | %{report.polynomial_metrics.test_accuracy * 100:<13.2f} | %{report.rbf_metrics.test_accuracy * 100:<13.2f}")
    print(f"{'Makro F1 Skoru':<28} | {report.linear_metrics.macro_f1:<14.4f} | {report.polynomial_metrics.macro_f1:<14.4f} | {report.rbf_metrics.macro_f1:<14.4f}")
    print(f"{'Cohen Kappa (κ)':<28} | {report.linear_metrics.cohen_kappa:<14.4f} | {report.polynomial_metrics.cohen_kappa:<14.4f} | {report.rbf_metrics.cohen_kappa:<14.4f}")
    print(f"{'Destek Vektörü (Adet)':<28} | {report.linear_metrics.support_vectors.total_support_vectors:<14} | {report.polynomial_metrics.support_vectors.total_support_vectors:<14} | {report.rbf_metrics.support_vectors.total_support_vectors:<14}")
    print(f"{'Destek Vektör Oranı':<28} | %{report.linear_metrics.support_vectors.support_vector_ratio_pct:<13.1f} | %{report.polynomial_metrics.support_vectors.support_vector_ratio_pct:<13.1f} | %{report.rbf_metrics.support_vectors.support_vector_ratio_pct:<13.1f}")
    print(f"{'Eğitim Süresi (ms)':<28} | {report.linear_metrics.training_time_ms:<14.1f} | {report.polynomial_metrics.training_time_ms:<14.1f} | {report.rbf_metrics.training_time_ms:<14.1f}")
    print(f"{'Tekil Gecikme (ms)':<28} | {report.linear_metrics.single_sample_latency_ms:<14.4f} | {report.polynomial_metrics.single_sample_latency_ms:<14.4f} | {report.rbf_metrics.single_sample_latency_ms:<14.4f}")
    print(f"{'Throughput (FPS)':<28} | {report.linear_metrics.throughput_fps:<14.1f} | {report.polynomial_metrics.throughput_fps:<14.1f} | {report.rbf_metrics.throughput_fps:<14.1f}")
    print("=" * 74)
    print(f"[+] Şampiyon Model: {report.winner_model}")
    print(f"[+] JSON Raporu Kaydedildi: {out_file}\n")


def cmd_plot(args):
    """Generates 2x2 diagnostic figure including 2D decision boundaries."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000))

    import pandas as pd
    df = pd.read_csv(csv_path)

    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    lin_clf = MerinosSVMClassifier(kernel="linear", C=1.0, random_state=42).fit(X_train, y_train)
    poly_clf = MerinosSVMClassifier(kernel="poly", degree=3, coef0=1.0, C=1.0, random_state=42).fit(X_train, y_train)
    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42).fit(X_train, y_train)

    grid_res = SVMEvaluator.tune_hyperparameters(X_train, y_train, X_test, y_test)
    report = SVMEvaluator.generate_comparison_report(lin_clf, poly_clf, rbf_clf, X_train, y_train, X_test, y_test, grid_res)

    viz = SVMVisualizer()
    out_file = cfg.get("output_paths", {}).get("diagnostic_panel_png", "day20/mini_project/outputs/svm_diagnostic_panel.png")
    fig_path = viz.plot_diagnostic_panel(report, grid_res, X_train, y_train, out_file)
    print(f"[+] 2x2 SVM Teşhis Paneli Grafiği Üretildi: {fig_path}")


def cmd_predict(args):
    """Classifies a single telemetry vector using trained RBF SVM model."""
    cfg = load_config()
    csv_path = Path(cfg.get("output_paths", {}).get("dataset_csv", "day20/mini_project/fixtures/carpet_defect_svm_dataset.csv"))
    if not csv_path.exists():
        cmd_generate_data(argparse.Namespace(samples=3000))

    import pandas as pd
    df = pd.read_csv(csv_path)

    preprocessor = SVMDataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    rbf_clf = MerinosSVMClassifier(kernel="rbf", C=10.0, gamma="scale", random_state=42)
    rbf_clf.fit(X_train, y_train)

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
    pred_idx = rbf_clf.predict(scaled_sample)[0]
    pred_probs = rbf_clf.predict_proba(scaled_sample)[0]

    defect_tr_map = {
        0: ("YARN_BREAKAGE", "İplik Kopması"),
        1: ("OIL_STAIN", "Yağ Lekesi"),
        2: ("JACQUARD_PATTERN_SHIFT", "Jakar Desen Kayması"),
        3: ("BORDER_SEWING_DEFECT", "Kenar Dikiş Hatası")
    }

    class_key, class_tr = defect_tr_map[pred_idx]

    print("\n" + "=" * 60)
    print("      MERİNOS SVM CANLI TEZGÂH KUSUR TEŞHİSİ (INFERENCE)    ")
    print("=" * 60)
    print(f"Teşhis Edilen Kusur : {class_key} ({class_tr})")
    print(f"Sınıf Güven Skoru   : %{pred_probs[pred_idx] * 100:.2f}")
    print("-" * 60)
    print("Tahmin Olasılık Dağılımı (Platt Scaling):")
    for idx, (ck, ctr) in defect_tr_map.items():
        print(f"  [{idx}] {ck:<24} ({ctr:<20}): %{pred_probs[idx] * 100:.2f}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos SVM Defect Classification CLI Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik veri üretimi")
    p_gen.add_argument("--samples", type=int, default=3000, help="Örneklem sayısı")

    # train
    subparsers.add_parser("train", help="Linear, Poly ve RBF SVM modellerini eğit")

    # tune
    subparsers.add_parser("tune", help="C ve gamma parametrelerinde grid araması yap")

    # evaluate
    subparsers.add_parser("evaluate", help="Kapsamlı kıyaslama ve JSON master raporu üret")

    # plot
    subparsers.add_parser("plot", help="2x2 Teşhis paneli grafiği çiz")

    # predict
    p_pred = subparsers.add_parser("predict", help="Canlı telemetri ile kusur teşhisi yap")
    p_pred.add_argument("--tensile", type=float, default=15.0, help="İplik kopma mukavemeti (cN/tex)")
    p_pred.add_argument("--elongation", type=float, default=9.5, help="Kopma uzaması (%%)")
    p_pred.add_argument("--hairiness", type=float, default=4.5, help="Tüylülük indeksi (H)")
    p_pred.add_argument("--twist", type=float, default=430.0, help="İplik büküm sayısı (TPM)")
    p_pred.add_argument("--dtex", type=float, default=2220.0, help="Doğrusal yoğunluk (dtex)")
    p_pred.add_argument("--rpm", type=float, default=610.0, help="Dokuma tezgah devri (RPM)")
    p_pred.add_argument("--tension", type=float, default=42.0, help="Gerilim dalgalanması (cN)")
    p_pred.add_argument("--humidity", type=float, default=58.0, help="Ortam bağıl nemi (%%)")
    p_pred.add_argument("--temp", type=float, default=23.5, help="Ortam sıcaklığı (°C)")
    p_pred.add_argument("--weft", type=float, default=525.0, help="Atkı atım sıklığı (picks/min)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate-data":
        cmd_generate_data(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "tune":
        cmd_tune(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "plot":
        cmd_plot(args)
    elif args.command == "predict":
        cmd_predict(args)


if __name__ == "__main__":
    main()
