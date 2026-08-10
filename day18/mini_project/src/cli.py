"""
Merinos Industrial AI Internship - Day 18
Command Line Interface (CLI) for Decision Tree & Random Forest Pipeline

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from day18.mini_project.src.data_generator import TreeQualityDataGenerator
from day18.mini_project.src.preprocessor import TreeDataPreprocessor
from day18.mini_project.src.tree_models import (
    MerinosDecisionTreeClassifier,
    MerinosRandomForestClassifier,
)
from day18.mini_project.src.evaluator import TreeEnsembleEvaluator
from day18.mini_project.src.visualizer import TreeVisualizer
from day18.mini_project.src.models import DefectClass


DEFAULT_CONFIG_PATH = "day18/mini_project/configs/tree_config.json"


def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Loads JSON configuration file."""
    p = Path(config_path)
    if not p.exists():
        # Fallback relative to project root
        p = Path(__file__).resolve().parent.parent / "configs" / "tree_config.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_generate_data(args: argparse.Namespace) -> None:
    """Generates synthetic textile quality dataset."""
    cfg = load_config(args.config)
    n_samples = args.samples or cfg["dataset"]["n_samples"]
    output_path = args.output or cfg["paths"]["raw_data"]

    print(f"[*] Sentetik veri üretimi başlatılıyor (Örneklem: {n_samples})...")
    gen = TreeQualityDataGenerator(n_samples=n_samples, random_state=cfg["dataset"]["random_state"])
    saved_path = gen.save_to_csv(output_path)
    print(f"[+] Veri kümesi başarıyla oluşturuldu: {saved_path}")


def _load_data_and_split(cfg: dict):
    data_path = cfg["paths"]["raw_data"]
    if not os.path.exists(data_path):
        print(f"[*] Veri dosyası bulunamadı, otomatik üretiliyor: {data_path}")
        gen = TreeQualityDataGenerator(
            n_samples=cfg["dataset"]["n_samples"],
            random_state=cfg["dataset"]["random_state"]
        )
        gen.save_to_csv(data_path)

    df = pd.read_csv(data_path)
    preprocessor = TreeDataPreprocessor(
        test_size=cfg["dataset"]["test_size"],
        random_state=cfg["dataset"]["random_state"],
        target_column=cfg["dataset"]["target_column"],
        feature_names=cfg["dataset"]["feature_names"]
    )
    X_train, X_test, y_train, y_test = preprocessor.split(df)
    return X_train, X_test, y_train, y_test, preprocessor.get_feature_names()


def cmd_train(args: argparse.Namespace) -> None:
    """Trains unpruned Decision Tree and Random Forest models."""
    cfg = load_config(args.config)
    X_train, X_test, y_train, y_test, _ = _load_data_and_split(cfg)

    print("\n" + "=" * 65)
    print("      MERİNOS KARAR AĞAÇLARI & RANDOM FOREST MODEL EĞİTİMİ     ")
    print("=" * 65)

    # 1. Unpruned Decision Tree
    print("\n[*] 1. Budanmamış Karar Ağacı Eğitiliyor (Unpruned Decision Tree)...")
    dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        random_state=cfg["decision_tree"]["random_state"]
    )
    dt.fit(X_train, y_train)
    dt_comp = dt.get_complexity()
    dt_eval = TreeEnsembleEvaluator.evaluate_model(dt, X_train, y_train, X_test, y_test)

    print(f"    - Derinlik (Depth): {dt_comp.depth}")
    print(f"    - Düğüm Sayısı (Node Count): {dt_comp.node_count}")
    print(f"    - Yaprak Sayısı (Leaves): {dt_comp.leaf_count}")
    print(f"    - Eğitim Doğruluğu: %{dt_eval.train_accuracy * 100:.2f}")
    print(f"    - Test Doğruluğu: %{dt_eval.test_accuracy * 100:.2f}")
    print(f"    - Overfitting Boşluğu: %{dt_eval.overfitting_gap * 100:.2f}")

    # 2. Random Forest
    print("\n[*] 2. Random Forest Topluluğu Eğitiliyor (n_estimators=100)...")
    rf = MerinosRandomForestClassifier(
        n_estimators=cfg["random_forest"]["n_estimators"],
        criterion=cfg["random_forest"]["criterion"],
        max_features=cfg["random_forest"]["max_features"],
        bootstrap=cfg["random_forest"]["bootstrap"],
        oob_score=cfg["random_forest"]["oob_score"],
        n_jobs=cfg["random_forest"]["n_jobs"],
        random_state=cfg["random_forest"]["random_state"]
    )
    rf.fit(X_train, y_train)
    oob_score, oob_error = rf.get_oob_metrics()
    rf_eval = TreeEnsembleEvaluator.evaluate_model(rf, X_train, y_train, X_test, y_test)

    print(f"    - Topluluktaki Ağaç Sayısı: {rf.n_estimators}")
    print(f"    - Out-Of-Bag (OOB) Doğruluğu: %{oob_score * 100:.2f}")
    print(f"    - OOB Hatası: %{oob_error * 100:.2f}")
    print(f"    - Test Doğruluğu: %{rf_eval.test_accuracy * 100:.2f}")
    print(f"    - Makro F1-Skoru: {rf_eval.macro_f1:.4f}")
    print(f"    - Cohen's Kappa: {rf_eval.cohen_kappa:.4f}")
    print("=" * 65)


def cmd_prune(args: argparse.Namespace) -> None:
    """Computes Minimal Cost-Complexity Pruning Path (ccp_alpha)."""
    cfg = load_config(args.config)
    X_train, X_test, y_train, y_test, _ = _load_data_and_split(cfg)

    print("\n[*] Minimal Maliyet-Karmaşıklık Budama Yolu Hesaplanıyor (ccp_alpha)...")
    dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        random_state=cfg["decision_tree"]["random_state"]
    )
    path_res = dt.compute_pruning_path(X_train, y_train, X_test, y_test)

    print(f"[+] Değerlendirilen Efektif Alpha Sayısı: {len(path_res.ccp_alphas)}")
    print(f"[+] Optimal Pruning Alpha (alpha*): {path_res.optimal_ccp_alpha:.6f}")
    print(f"[+] Budanmamış Yaprak Sayısı: {path_res.unpruned_leaf_count}")
    print(f"[+] Budanmış Yaprak Sayısı: {path_res.optimal_leaf_count}")
    print(f"[+] Karmaşıklık Azaltma Oranı: %{path_res.leaf_reduction_pct:.1f}")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluates all three models and outputs master JSON benchmark report."""
    cfg = load_config(args.config)
    X_train, X_test, y_train, y_test, feature_names = _load_data_and_split(cfg)

    # 1. Unpruned Tree
    unpruned_dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        random_state=cfg["decision_tree"]["random_state"]
    ).fit(X_train, y_train)

    # 2. Pruning Path & Pruned Tree
    path_res = unpruned_dt.compute_pruning_path(X_train, y_train, X_test, y_test)
    pruned_dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        ccp_alpha=path_res.optimal_ccp_alpha,
        random_state=cfg["decision_tree"]["random_state"]
    ).fit(X_train, y_train)

    # 3. Random Forest
    rf = MerinosRandomForestClassifier(
        n_estimators=cfg["random_forest"]["n_estimators"],
        criterion=cfg["random_forest"]["criterion"],
        max_features=cfg["random_forest"]["max_features"],
        bootstrap=cfg["random_forest"]["bootstrap"],
        oob_score=cfg["random_forest"]["oob_score"],
        n_jobs=cfg["random_forest"]["n_jobs"],
        random_state=cfg["random_forest"]["random_state"]
    ).fit(X_train, y_train)

    report = TreeEnsembleEvaluator.generate_report(
        unpruned_tree=unpruned_dt,
        pruned_tree=pruned_dt,
        random_forest=rf,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    out_path = args.output or cfg["paths"]["evaluation_report"]
    saved_p = TreeEnsembleEvaluator.save_report_to_json(report, out_path)

    print("\n" + "=" * 76)
    print("         MERİNOS KARAR AĞAÇLARI & RANDOM FOREST KIYASLAMA RAPORU        ")
    print("=" * 76)
    print(f"{'Performans Metriği':<30} | {'Budanmamış Ağaç':<12} | {'Budanmış Ağaç':<12} | {'Random Forest':<12}")
    print("-" * 76)
    print(f"{'Eğitim Doğruluğu':<30} | %{report.unpruned_tree.train_accuracy*100:<11.2f} | %{report.pruned_tree.train_accuracy*100:<11.2f} | %{report.random_forest.train_accuracy*100:<11.2f}")
    print(f"{'Test Doğruluğu':<30} | %{report.unpruned_tree.test_accuracy*100:<11.2f} | %{report.pruned_tree.test_accuracy*100:<11.2f} | %{report.random_forest.test_accuracy*100:<11.2f}")
    print(f"{'Overfitting Boşluğu':<30} | %{report.unpruned_tree.overfitting_gap*100:<11.2f} | %{report.pruned_tree.overfitting_gap*100:<11.2f} | %{report.random_forest.overfitting_gap*100:<11.2f}")
    print(f"{'Makro F1-Skoru':<30} | {report.unpruned_tree.macro_f1:<12.4f} | {report.pruned_tree.macro_f1:<12.4f} | {report.random_forest.macro_f1:<12.4f}")
    print(f"{'Cohen Kappa Katsayısı':<30} | {report.unpruned_tree.cohen_kappa:<12.4f} | {report.pruned_tree.cohen_kappa:<12.4f} | {report.random_forest.cohen_kappa:<12.4f}")
    print(f"{'Yaprak Sayısı':<30} | {report.unpruned_complexity.leaf_count:<12} | {report.pruned_complexity.leaf_count:<12} | {'100 Ağaç':<12}")
    print(f"{'Tekil Gecikme (ms)':<30} | {report.unpruned_tree.latency_ms:<12.4f} | {report.pruned_tree.latency_ms:<12.4f} | {report.random_forest.latency_ms:<12.4f}")
    print("=" * 76)
    print(f"[+] Şampiyon Model: {report.best_model_name}")
    print(f"[+] Master JSON Raporu Kaydedildi: {saved_p}")


def cmd_plot(args: argparse.Namespace) -> None:
    """Generates 2x2 diagnostic panel graphic."""
    cfg = load_config(args.config)
    X_train, X_test, y_train, y_test, feature_names = _load_data_and_split(cfg)

    unpruned_dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        random_state=cfg["decision_tree"]["random_state"]
    ).fit(X_train, y_train)

    path_res = unpruned_dt.compute_pruning_path(X_train, y_train, X_test, y_test)
    pruned_dt = MerinosDecisionTreeClassifier(
        criterion=cfg["decision_tree"]["criterion"],
        min_samples_split=cfg["decision_tree"]["min_samples_split"],
        min_samples_leaf=cfg["decision_tree"]["min_samples_leaf"],
        ccp_alpha=path_res.optimal_ccp_alpha,
        random_state=cfg["decision_tree"]["random_state"]
    ).fit(X_train, y_train)

    rf = MerinosRandomForestClassifier(
        n_estimators=cfg["random_forest"]["n_estimators"],
        criterion=cfg["random_forest"]["criterion"],
        max_features=cfg["random_forest"]["max_features"],
        bootstrap=cfg["random_forest"]["bootstrap"],
        oob_score=cfg["random_forest"]["oob_score"],
        n_jobs=cfg["random_forest"]["n_jobs"],
        random_state=cfg["random_forest"]["random_state"]
    ).fit(X_train, y_train)

    report = TreeEnsembleEvaluator.generate_report(
        unpruned_tree=unpruned_dt,
        pruned_tree=pruned_dt,
        random_forest=rf,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    print("[*] Out-Of-Bag hata yakınsaması hesaplanıyor...")
    oob_convergence = rf.compute_oob_convergence(X_train, y_train, min_trees=5, max_trees=100, step=5)

    out_path = args.output or cfg["paths"]["diagnostic_panel"]
    viz = TreeVisualizer()
    saved_panel = viz.plot_diagnostic_panel(report, path_res, oob_convergence, out_path)
    print(f"[+] 2x2 Model Teşhis Paneli üretildi: {saved_panel}")


def cmd_predict(args: argparse.Namespace) -> None:
    """Predicts carpet defect class for single telemetry input sample."""
    cfg = load_config(args.config)
    X_train, _, y_train, _, feature_names = _load_data_and_split(cfg)

    # Train production champion model
    rf = MerinosRandomForestClassifier(
        n_estimators=cfg["random_forest"]["n_estimators"],
        criterion=cfg["random_forest"]["criterion"],
        max_features=cfg["random_forest"]["max_features"],
        bootstrap=cfg["random_forest"]["bootstrap"],
        oob_score=cfg["random_forest"]["oob_score"],
        n_jobs=cfg["random_forest"]["n_jobs"],
        random_state=cfg["random_forest"]["random_state"]
    ).fit(X_train, y_train)

    sample_vals = [
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
    ]

    sample_arr = np.array([sample_vals], dtype=np.float64)
    pred_id = int(rf.predict(sample_arr)[0])
    probs = rf.predict_proba(sample_arr)[0]

    class_names = [
        "YARN_BREAKAGE (İplik Kopması)",
        "OIL_STAIN (Yağ Lekesi)",
        "JACQUARD_PATTERN_SHIFT (Jakar Desen Kayması)",
        "BORDER_SEWING_DEFECT (Kenar Dikiş Hatası)"
    ]
    pred_name = class_names[pred_id]
    confidence = float(probs[pred_id])

    print("\n" + "=" * 60)
    print("      MERİNOS CANLI TEZGÂH KUSUR TEŞHİSİ (INFERENCE)      ")
    print("=" * 60)
    print(f"Teşhis Edilen Kusur Sınıfı : {pred_name}")
    print(f"Sınıf Güven Skoru          : %{confidence * 100:.2f}")
    print("-" * 60)
    print("Tahmin Olasılık Dağılımı:")
    for idx, name in enumerate(class_names):
        print(f"  [{idx}] {name:<42} : %{probs[idx]*100:.2f}")
    print("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    """Constructs command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Merinos Karar Ağaçları & Random Forest Kalite Sınıflandırma CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Konfigürasyon JSON dosya yolu")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik endüstriyel veri seti üretir")
    p_gen.add_argument("--samples", type=int, default=3000, help="Üretilecek örneklem sayısı")
    p_gen.add_argument("--output", type=str, default=None, help="Çıktı CSV dosya yolu")

    # train
    subparsers.add_parser("train", help="Budanmamış Ağaç ve Random Forest modellerini eğitir")

    # prune
    subparsers.add_parser("prune", help="Minimal Cost-Complexity Pruning (ccp_alpha) yolunu hesaplar")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Tüm modelleri değerlendirip JSON raporu üretir")
    p_eval.add_argument("--output", type=str, default=None, help="Çıktı JSON rapor dosya yolu")

    # plot
    p_plot = subparsers.add_parser("plot", help="2x2 Teşhis panelini görselleştirir")
    p_plot.add_argument("--output", type=str, default=None, help="Çıktı PNG dosya yolu")

    # predict
    p_pred = subparsers.add_parser("predict", help="Tekil telemetri ölçümünden anlık kusur teşhisi yapar")
    p_pred.add_argument("--tensile", type=float, default=24.0, help="İplik kopma mukavemeti (cN/tex)")
    p_pred.add_argument("--elongation", type=float, default=16.0, help="Kopma uzaması")
    p_pred.add_argument("--hairiness", type=float, default=4.8, help="Tüylülük indeksi (H)")
    p_pred.add_argument("--twist", type=float, default=430.0, help="Büküm sayısı (TPM)")
    p_pred.add_argument("--dtex", type=float, default=2200.0, help="İplik doğrusal yoğunluğu (dtex)")
    p_pred.add_argument("--rpm", type=float, default=610.0, help="Dokuma tezgâh devri (RPM)")
    p_pred.add_argument("--tension", type=float, default=26.0, help="Tezgâh gerilim dalgalanması (cN)")
    p_pred.add_argument("--humidity", type=float, default=58.0, help="Ortam bağıl nemi")
    p_pred.add_argument("--temp", type=float, default=24.5, help="Ortam sıcaklığı (C)")
    p_pred.add_argument("--weft", type=float, default=530.0, help="Atkı atım sıklığı (picks/min)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "generate-data": cmd_generate_data,
        "train": cmd_train,
        "prune": cmd_prune,
        "evaluate": cmd_evaluate,
        "plot": cmd_plot,
        "predict": cmd_predict
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
