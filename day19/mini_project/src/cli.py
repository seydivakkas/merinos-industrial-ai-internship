"""
Merinos Industrial AI Internship - Day 19
Command Line Interface (CLI) for Gradient Boosting (XGBoost & LightGBM)

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

from day19.mini_project.src.data_generator import BoostingQualityDataGenerator
from day19.mini_project.src.preprocessor import BoostingDataPreprocessor
from day19.mini_project.src.boosting_models import (
    MerinosXGBoostClassifier,
    MerinosLightGBMClassifier,
)
from day19.mini_project.src.evaluator import BoostingEvaluator
from day19.mini_project.src.visualizer import BoostingVisualizer
from day19.mini_project.src.models import DefectClass


DEFAULT_CONFIG_PATH = "day19/mini_project/configs/boosting_config.json"


def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Loads JSON configuration file."""
    p = Path(config_path)
    if not p.exists():
        p = Path(__file__).resolve().parent.parent / "configs" / "boosting_config.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_data_and_split(cfg: dict):
    data_path = cfg["paths"]["raw_data"]
    if not os.path.exists(data_path):
        print(f"[*] Veri dosyası bulunamadı, otomatik üretiliyor: {data_path}")
        gen = BoostingQualityDataGenerator(
            n_samples=cfg["dataset"]["n_samples"],
            random_state=cfg["dataset"]["random_state"]
        )
        gen.save_to_csv(data_path)

    df = pd.read_csv(data_path)
    preprocessor = BoostingDataPreprocessor(
        train_ratio=cfg["dataset"]["train_ratio"],
        val_ratio=cfg["dataset"]["val_ratio"],
        test_ratio=cfg["dataset"]["test_ratio"],
        random_state=cfg["dataset"]["random_state"],
        target_column=cfg["dataset"]["target_column"],
        feature_names=cfg["dataset"]["feature_names"]
    )
    X_train, y_train, X_val, y_val, X_test, y_test = preprocessor.split_3way(df)
    return X_train, y_train, X_val, y_val, X_test, y_test, preprocessor.get_feature_names()


def cmd_generate_data(args: argparse.Namespace) -> None:
    """Generates synthetic textile quality dataset."""
    cfg = load_config(args.config)
    n_samples = args.samples or cfg["dataset"]["n_samples"]
    output_path = args.output or cfg["paths"]["raw_data"]

    print(f"[*] Sentetik telemetri verisi üretiliyor (Örneklem: {n_samples})...")
    gen = BoostingQualityDataGenerator(
        n_samples=n_samples,
        random_state=cfg["dataset"]["random_state"]
    )
    saved_path = gen.save_to_csv(output_path)
    print(f"[+] Veri kümesi başarıyla oluşturuldu: {saved_path}")


def cmd_train(args: argparse.Namespace) -> None:
    """Trains XGBoost and LightGBM models with early stopping."""
    cfg = load_config(args.config)
    X_train, y_train, X_val, y_val, X_test, y_test, _ = _load_data_and_split(cfg)

    print("\n" + "=" * 70)
    print("       MERİNOS GRADIENT BOOSTING (XGBOOST & LIGHTGBM) MODEL EĞİTİMİ      ")
    print("=" * 70)

    # 1. XGBoost
    print("\n[*] 1. XGBoost Modeli Eğitiliyor (Early Stopping = 15 iterasyon)...")
    xgb_model = MerinosXGBoostClassifier(
        n_estimators=cfg["xgboost"]["n_estimators"],
        learning_rate=cfg["xgboost"]["learning_rate"],
        max_depth=cfg["xgboost"]["max_depth"],
        subsample=cfg["xgboost"]["subsample"],
        colsample_bytree=cfg["xgboost"]["colsample_bytree"],
        early_stopping_rounds=cfg["xgboost"]["early_stopping_rounds"],
        eval_metric=cfg["xgboost"]["eval_metric"],
        random_state=cfg["xgboost"]["random_state"],
        n_jobs=cfg["xgboost"]["n_jobs"]
    )
    xgb_model.fit(X_train, y_train, X_val, y_val)
    xgb_es = xgb_model.get_early_stopping_result()
    xgb_metrics = BoostingEvaluator.evaluate_model(
        xgb_model, X_train, y_train, X_val, y_val, X_test, y_test
    )

    print(f"    - En İyi İterasyon (Best Iteration) : {xgb_es.best_iteration} / {xgb_es.stopping_iteration}")
    print(f"    - Minimum Doğrulama Kaybı (Val Loss): {xgb_es.best_val_loss:.4f}")
    print(f"    - Test Doğruluğu (Test Accuracy)   : %{xgb_metrics.accuracy * 100:.2f}")
    print(f"    - Makro F1-Skoru                   : {xgb_metrics.macro_f1:.4f}")
    print(f"    - Eğitim Süresi                    : {xgb_metrics.training_time_ms:.1f} ms")

    # 2. LightGBM
    print("\n[*] 2. LightGBM Modeli Eğitiliyor (Leaf-wise & Early Stopping = 15)...")
    lgb_model = MerinosLightGBMClassifier(
        n_estimators=cfg["lightgbm"]["n_estimators"],
        learning_rate=cfg["lightgbm"]["learning_rate"],
        num_leaves=cfg["lightgbm"]["num_leaves"],
        max_depth=cfg["lightgbm"]["max_depth"],
        subsample=cfg["lightgbm"]["subsample"],
        colsample_bytree=cfg["lightgbm"]["colsample_bytree"],
        early_stopping_rounds=cfg["lightgbm"]["early_stopping_rounds"],
        random_state=cfg["lightgbm"]["random_state"],
        n_jobs=cfg["lightgbm"]["n_jobs"]
    )
    lgb_model.fit(X_train, y_train, X_val, y_val)
    lgb_es = lgb_model.get_early_stopping_result()
    lgb_metrics = BoostingEvaluator.evaluate_model(
        lgb_model, X_train, y_train, X_val, y_val, X_test, y_test
    )

    speedup = (
        round(xgb_metrics.training_time_ms / lgb_metrics.training_time_ms, 2)
        if lgb_metrics.training_time_ms > 0 else 1.0
    )

    print(f"    - En İyi İterasyon (Best Iteration) : {lgb_es.best_iteration} / {lgb_es.stopping_iteration}")
    print(f"    - Minimum Doğrulama Kaybı (Val Loss): {lgb_es.best_val_loss:.4f}")
    print(f"    - Test Doğruluğu (Test Accuracy)   : %{lgb_metrics.accuracy * 100:.2f}")
    print(f"    - Makro F1-Skoru                   : {lgb_metrics.macro_f1:.4f}")
    print(f"    - Eğitim Süresi                    : {lgb_metrics.training_time_ms:.1f} ms ({speedup}x Daha Hızlı)")
    print("=" * 70)


def cmd_tune(args: argparse.Namespace) -> None:
    """Performs learning rate and depth hyperparameter optimization."""
    cfg = load_config(args.config)
    X_train, y_train, X_val, y_val, X_test, y_test, _ = _load_data_and_split(cfg)

    lrs = cfg["tuning"]["learning_rates"]
    depths = cfg["tuning"]["max_depths"]

    print("\n[*] Gradient Boosting Hiperparametre Optimizasyonu Başlatılıyor...")
    print(f"[*] Değerlendirilecek Grid: learning_rate={lrs}, max_depth={depths}")

    res = BoostingEvaluator.tune_hyperparameters(
        X_train, y_train, X_val, y_val, X_test, y_test,
        learning_rates=lrs,
        max_depths=depths,
        model_type="xgboost"
    )

    print("\n" + "=" * 62)
    print(f"{'Öğrenme Oranı (η)':<18} | {'Derinlik':<10} | {'Val Acc (%)':<14} | {'Test Acc (%)':<14}")
    print("-" * 62)
    for r in res.records:
        print(f"{r.learning_rate:<18} | {r.max_depth:<10} | %{r.val_accuracy*100:<12.2f} | %{r.test_accuracy*100:<12.2f}")
    print("=" * 62)
    print(f"[+] Optimal Konfigürasyon: learning_rate={res.best_learning_rate}, max_depth={res.best_max_depth} (Val Acc: %{res.best_accuracy*100:.2f})")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluates models and writes master JSON comparison report."""
    cfg = load_config(args.config)
    X_train, y_train, X_val, y_val, X_test, y_test, feature_names = _load_data_and_split(cfg)

    xgb_model = MerinosXGBoostClassifier(
        n_estimators=cfg["xgboost"]["n_estimators"],
        learning_rate=cfg["xgboost"]["learning_rate"],
        max_depth=cfg["xgboost"]["max_depth"],
        subsample=cfg["xgboost"]["subsample"],
        colsample_bytree=cfg["xgboost"]["colsample_bytree"],
        early_stopping_rounds=cfg["xgboost"]["early_stopping_rounds"],
        eval_metric=cfg["xgboost"]["eval_metric"],
        random_state=cfg["xgboost"]["random_state"],
        n_jobs=cfg["xgboost"]["n_jobs"]
    ).fit(X_train, y_train, X_val, y_val)

    lgb_model = MerinosLightGBMClassifier(
        n_estimators=cfg["lightgbm"]["n_estimators"],
        learning_rate=cfg["lightgbm"]["learning_rate"],
        num_leaves=cfg["lightgbm"]["num_leaves"],
        max_depth=cfg["lightgbm"]["max_depth"],
        subsample=cfg["lightgbm"]["subsample"],
        colsample_bytree=cfg["lightgbm"]["colsample_bytree"],
        early_stopping_rounds=cfg["lightgbm"]["early_stopping_rounds"],
        random_state=cfg["lightgbm"]["random_state"],
        n_jobs=cfg["lightgbm"]["n_jobs"]
    ).fit(X_train, y_train, X_val, y_val)

    report = BoostingEvaluator.generate_report(
        xgb_model=xgb_model,
        lgb_model=lgb_model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    out_path = args.output or cfg["paths"]["evaluation_report"]
    saved_p = BoostingEvaluator.save_report_to_json(report, out_path)

    print("\n" + "=" * 74)
    print("      MERİNOS GRADIENT BOOSTING (XGBOOST vs LIGHTGBM) KIYASLAMA RAPORU     ")
    print("=" * 74)
    print(f"{'Performans Metriği':<30} | {'XGBoost':<18} | {'LightGBM':<18}")
    print("-" * 74)
    print(f"{'Test Doğruluğu':<30} | %{report.xgboost.accuracy*100:<16.2f} | %{report.lightgbm.accuracy*100:<16.2f}")
    print(f"{'Makro F1-Skoru':<30} | {report.xgboost.macro_f1:<18.4f} | {report.lightgbm.macro_f1:<18.4f}")
    print(f"{'Ağırlıklı F1-Skoru':<30} | {report.xgboost.weighted_f1:<18.4f} | {report.lightgbm.weighted_f1:<18.4f}")
    print(f"{'Cohen Kappa Katsayısı':<30} | {report.xgboost.cohen_kappa:<18.4f} | {report.lightgbm.cohen_kappa:<18.4f}")
    print(f"{'Doğrulama Kaybı (Val Loss)':<30} | {report.xgboost.val_loss:<18.4f} | {report.lightgbm.val_loss:<18.4f}")
    print(f"{'Optimal Ağaç / İterasyon':<30} | {report.xgboost.best_iteration:<18} | {report.lightgbm.best_iteration:<18}")
    print(f"{'Eğitim Süresi (ms)':<30} | {report.xgboost.training_time_ms:<18.1f} | {report.lightgbm.training_time_ms:<18.1f}")
    print(f"{'Tekil Çıkarım Gecikmesi (ms)':<30} | {report.xgboost.latency_ms:<18.4f} | {report.lightgbm.latency_ms:<18.4f}")
    print(f"{'Çıkarım Throughput (FPS)':<30} | {report.xgboost.throughput_fps:<18.1f} | {report.lightgbm.throughput_fps:<18.1f}")
    print("=" * 74)
    print(f"[+] Şampiyon Model : {report.champion_model}")
    print(f"[+] Hız Üstünlüğü  : LightGBM, XGBoost'a göre {report.speedup_factor} kat daha hızlı eğitildi.")
    print(f"[+] Master JSON Raporu Kaydedildi: {saved_p}")


def cmd_plot(args: argparse.Namespace) -> None:
    """Generates 2x2 diagnostic panel."""
    cfg = load_config(args.config)
    X_train, y_train, X_val, y_val, X_test, y_test, feature_names = _load_data_and_split(cfg)

    xgb_model = MerinosXGBoostClassifier(
        n_estimators=cfg["xgboost"]["n_estimators"],
        learning_rate=cfg["xgboost"]["learning_rate"],
        max_depth=cfg["xgboost"]["max_depth"],
        subsample=cfg["xgboost"]["subsample"],
        colsample_bytree=cfg["xgboost"]["colsample_bytree"],
        early_stopping_rounds=cfg["xgboost"]["early_stopping_rounds"],
        eval_metric=cfg["xgboost"]["eval_metric"],
        random_state=cfg["xgboost"]["random_state"],
        n_jobs=cfg["xgboost"]["n_jobs"]
    ).fit(X_train, y_train, X_val, y_val)

    lgb_model = MerinosLightGBMClassifier(
        n_estimators=cfg["lightgbm"]["n_estimators"],
        learning_rate=cfg["lightgbm"]["learning_rate"],
        num_leaves=cfg["lightgbm"]["num_leaves"],
        max_depth=cfg["lightgbm"]["max_depth"],
        subsample=cfg["lightgbm"]["subsample"],
        colsample_bytree=cfg["lightgbm"]["colsample_bytree"],
        early_stopping_rounds=cfg["lightgbm"]["early_stopping_rounds"],
        random_state=cfg["lightgbm"]["random_state"],
        n_jobs=cfg["lightgbm"]["n_jobs"]
    ).fit(X_train, y_train, X_val, y_val)

    report = BoostingEvaluator.generate_report(
        xgb_model=xgb_model,
        lgb_model=lgb_model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_names
    )

    xgb_es = xgb_model.get_early_stopping_result()
    lgb_es = lgb_model.get_early_stopping_result()

    tuning_res = BoostingEvaluator.tune_hyperparameters(
        X_train, y_train, X_val, y_val, X_test, y_test,
        learning_rates=cfg["tuning"]["learning_rates"],
        max_depths=cfg["tuning"]["max_depths"],
        model_type="xgboost"
    )

    out_path = args.output or cfg["paths"]["diagnostic_panel"]
    viz = BoostingVisualizer()
    saved_panel = viz.plot_diagnostic_panel(report, xgb_es, lgb_es, tuning_res, out_path)
    print(f"[+] 2x2 Teşhis Paneli Grafiği Üretildi: {saved_panel}")


def cmd_predict(args: argparse.Namespace) -> None:
    """Predicts carpet defect class from 10 sensor measurements."""
    cfg = load_config(args.config)
    X_train, y_train, X_val, y_val, _, _, feature_names = _load_data_and_split(cfg)

    # Train production champion model (LightGBM for speed and high accuracy)
    model = MerinosLightGBMClassifier(
        n_estimators=cfg["lightgbm"]["n_estimators"],
        learning_rate=cfg["lightgbm"]["learning_rate"],
        num_leaves=cfg["lightgbm"]["num_leaves"],
        max_depth=cfg["lightgbm"]["max_depth"],
        subsample=cfg["lightgbm"]["subsample"],
        colsample_bytree=cfg["lightgbm"]["colsample_bytree"],
        early_stopping_rounds=cfg["lightgbm"]["early_stopping_rounds"],
        random_state=cfg["lightgbm"]["random_state"],
        n_jobs=cfg["lightgbm"]["n_jobs"]
    ).fit(X_train, y_train, X_val, y_val)

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

    pred_id = int(model.predict(sample_arr)[0])
    probs = model.predict_proba(sample_arr)[0]

    class_names = [
        "YARN_BREAKAGE (İplik Kopması)",
        "OIL_STAIN (Yağ Lekesi)",
        "JACQUARD_PATTERN_SHIFT (Jakar Desen Kayması)",
        "BORDER_SEWING_DEFECT (Kenar Dikiş Hatası)"
    ]
    confidence = float(probs[pred_id])

    print("\n" + "=" * 60)
    print("      MERİNOS CANLI TEZGÂH KUSUR TEŞHİSİ (INFERENCE)      ")
    print("=" * 60)
    print(f"Teşhis Edilen Kusur Sınıfı : {class_names[pred_id]}")
    print(f"Sınıf Güven Skoru          : %{confidence * 100:.2f}")
    print("-" * 60)
    print("Tahmin Olasılık Dağılımı:")
    for idx, name in enumerate(class_names):
        print(f"  [{idx}] {name:<42} : %{probs[idx]*100:.2f}")
    print("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    """Constructs command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Merinos Gradient Boosting (XGBoost & LightGBM) Kalite Sınıflandırma CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Konfigürasyon JSON dosya yolu")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik endüstriyel veri seti üretir")
    p_gen.add_argument("--samples", type=int, default=3000, help="Üretilecek örneklem sayısı")
    p_gen.add_argument("--output", type=str, default=None, help="Çıktı CSV dosya yolu")

    # train
    subparsers.add_parser("train", help="XGBoost ve LightGBM modellerini erken durdurma ile eğitir")

    # tune
    subparsers.add_parser("tune", help="Öğrenme oranı ve ağaç derinliği grid optimizasyonu yapar")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Modelleri değerlendirip JSON raporu üretir")
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
        "tune": cmd_tune,
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
