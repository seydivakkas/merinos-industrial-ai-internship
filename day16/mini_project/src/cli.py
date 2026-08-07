"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
İkili Sınıflandırma ve Lojistik Regresyon CLI Arayüzü

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import pandas as pd

from .data_generator import YarnQualityDataGenerator
from .evaluator import ClassificationEvaluator
from .logistic_classifier import MerinosBinaryLogisticClassifier
from .models import BinaryClassificationReport
from .preprocessor import QualityDataPreprocessor
from .visualizer import ClassificationVisualizer

# Windows konsol UTF-8 çıktı güvenliği
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_default_paths() -> Dict[str, Path]:
    base_dir = Path(__file__).resolve().parent.parent
    return {
        "config": base_dir / "configs" / "classification_config.json",
        "data_csv": base_dir / "fixtures" / "yarn_quality_dataset.csv",
        "report_json": base_dir / "outputs" / "classification_master_report.json",
        "plot_png": base_dir / "outputs" / "classification_diagnostic_panel.png",
    }


def cmd_generate_data(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    out_path = Path(args.output) if args.output else paths["data_csv"]
    
    print(f"[*] Sentetik iplik kalite verisi üretiliyor (n={args.samples}, kusur_orani={args.defect_ratio})...")
    gen = YarnQualityDataGenerator(config_path=str(paths["config"]))
    df = gen.generate_dataset(n_samples=args.samples, defect_ratio=args.defect_ratio, random_state=args.seed)
    
    saved_path = gen.save_dataset(df, str(out_path))
    defects = int(df["quality_label"].sum())
    normals = len(df) - defects
    print(f"[+] Veri seti başarıyla oluşturuldu: {saved_path}")
    print(f"    - Toplam Örneklem : {len(df)}")
    print(f"    - Standart (0)   : {normals} (%{normals/len(df)*100:.1f})")
    print(f"    - Kusurlu (1)    : {defects} (%{defects/len(df)*100:.1f})")


def _train_and_evaluate_pipeline(data_csv: Path, config_path: Path):
    if not data_csv.exists():
        print(f"[-] Veri seti bulunamadı: {data_csv}. Otomatik üretiliyor...")
        gen = YarnQualityDataGenerator(config_path=str(config_path))
        df = gen.generate_dataset()
        gen.save_dataset(df, str(data_csv))
    else:
        df = pd.read_csv(data_csv)

    preprocessor = QualityDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    # 1. Baseline Model (Standart Ağırlıklar)
    base_clf = MerinosBinaryLogisticClassifier(class_weight=None, random_state=42)
    base_clf.fit(X_train, y_train)

    # 2. Balanced Model (class_weight='balanced')
    bal_clf = MerinosBinaryLogisticClassifier(class_weight="balanced", random_state=42)
    bal_clf.fit(X_train, y_train)

    base_probs = base_clf.predict_proba(X_test)[:, 1]
    bal_probs = bal_clf.predict_proba(X_test)[:, 1]

    feature_weights = base_clf.get_feature_weights(preprocessor.feature_names)

    evaluator = ClassificationEvaluator(cost_fn=10.0, cost_fp=1.0)
    report = evaluator.generate_master_report(
        y_true=y_test,
        baseline_probs=base_probs,
        balanced_probs=bal_probs,
        feature_weights=feature_weights,
    )

    roc_metrics, evals, curve_data = evaluator.evaluate_probabilities(y_test, base_probs)
    return preprocessor, base_clf, bal_clf, report, curve_data, evals, X_test, y_test


def cmd_train(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]
    print(f"[*] Lojistik Regresyon modelleri eğitiliyor (Veri: {data_csv})...")
    
    _, base_clf, bal_clf, report, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])
    
    print("[+] Model eğitimi tamamlandı.")
    print(f"    - Sabit Terim (Intercept, beta_0): {base_clf.get_intercept():.4f}")
    print("    - En Önemli 5 Öznitelik Katsayısı ve Odds Oranları:")
    for fw in report.feature_weights[:5]:
        print(f"      * {fw.feature_name:<26}: beta = {fw.weight:+6.4f} | OR = {fw.odds_ratio:6.4f} ({fw.impact_direction})")


def cmd_evaluate(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]
    out_json = Path(args.output) if args.output else paths["report_json"]

    print(f"[*] Kapsamlı değerlendirme ve ROC/PR analizi yürütülüyor...")
    _, _, _, report, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    print(f"[+] Değerlendirme raporu kaydedildi: {out_json}")
    print("\n================== DAY 16 DEĞERLENDİRME ÖZETİ ==================")
    print(f"Veri Kümesi (Test)   : {report.dataset_samples} adet (Kusur Oranı: %{report.defect_ratio*100:.1f})")
    print(f"ROC-AUC Skoru        : {report.roc_auc_metrics.roc_auc:.4f}")
    print(f"PR-AUC (Avg Prec)    : {report.roc_auc_metrics.pr_auc:.4f}")
    print(f"Brier Kalibrasyon    : {report.roc_auc_metrics.brier_score:.4f}")
    print(f"Optimal Eşik (Youden): tau = {report.roc_auc_metrics.optimal_threshold_youden:.2f}")
    print(f"Optimal Eşik (Maliyet): tau = {report.roc_auc_metrics.optimal_threshold_cost:.2f}")
    print("----------------------------------------------------------------")
    print(f"{'Model / Eşik':<35} | {'Recall':<8} | {'Precision':<10} | {'F2-Score':<8} | {'Maliyet':<8}")
    print("----------------------------------------------------------------")
    for s in [report.baseline_model, report.balanced_model, report.tuned_threshold_model]:
        m = s.metrics
        print(f"{s.model_type[:35]:<35} | %{m.recall*100:<7.1f} | %{m.precision*100:<9.1f} | {m.f2_score:<8.4f} | {s.cost:<8.1f}")
    print("================================================================")


def cmd_plot(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]
    out_png = Path(args.output) if args.output else paths["plot_png"]

    print(f"[*] 2x2 Teşhis paneli grafiği oluşturuluyor...")
    _, _, _, report, curve_data, evals, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    viz = ClassificationVisualizer()
    saved_p = viz.plot_diagnostic_panel(report, curve_data, evals, str(out_png))
    print(f"[+] Teşhis paneli başarıyla kaydedildi: {saved_p}")


def cmd_predict(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = paths["data_csv"]

    preprocessor, base_clf, _, report, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    sample_dict = {
        "yarn_tensile_strength": args.tensile,
        "yarn_elongation_at_break": args.elongation,
        "yarn_hairiness_index": args.hairiness,
        "twist_per_meter": args.twist,
        "yarn_linear_density_dtex": args.dtex,
        "loom_speed_rpm": args.rpm,
        "loom_tension_variation": args.tension,
        "ambient_humidity_percent": args.humidity,
        "ambient_temperature_c": args.temp,
        "weft_insertion_rate": args.weft,
    }

    X_sample = preprocessor.transform_single(sample_dict)
    prob_defect = float(base_clf.predict_proba(X_sample)[0, 1])

    threshold = args.threshold if args.threshold is not None else report.tuned_threshold_model.threshold
    pred_class = int(prob_defect >= threshold)

    label_str = "KUSURLU / DEFECTIVE" if pred_class == 1 else "STANDART / ACCEPT"
    color_bullet = "🔴" if pred_class == 1 else "🟢"

    print("\n============== MERİNOS ENDÜSTRİYEL KALİTE TAHMİNİ ==============")
    print(f"Kusurlu Olma Olasılığı P(Y=1|x) : %{prob_defect*100:.2f}")
    print(f"Uygulanan Karar Eşiği (tau)      : {threshold:.2f}")
    print(f"Sınıflandırma Kararı             : {color_bullet} {label_str}")
    if pred_class == 1:
        print("UYARI: Parti kalite standartlarının altındadır! Tezgâh gerilimi ve iplik mukavemeti denetlenmelidir.")
    else:
        print("ONAY: Parti kalite standartlarına uygundur. Dokuma hattına sevk edilebilir.")
    print("=================================================================")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Halı & İplik Kalite Kontrolü — İkili Sınıflandırma CLI Aracı"
    )
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik sensör veri kümesi üretir")
    p_gen.add_argument("--samples", type=int, default=2500, help="Toplam örneklem sayısı")
    p_gen.add_argument("--defect-ratio", type=float, default=0.10, help="Kusurlu sınıf oranı")
    p_gen.add_argument("--seed", type=int, default=42, help="Rastgelelik tohumu")
    p_gen.add_argument("-o", "--output", type=str, default=None, help="Çıktı CSV dosyası yolu")

    # train
    p_train = subparsers.add_parser("train", help="Lojistik regresyon modellerini eğitir")
    p_train.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Kapsamlı metrik, ROC-AUC ve eşik analizi yapar")
    p_eval.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")
    p_eval.add_argument("-o", "--output", type=str, default=None, help="Çıktı JSON rapor yolu")

    # plot
    p_plot = subparsers.add_parser("plot", help="2x2 Teşhis paneli PNG grafiğini üretir")
    p_plot.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")
    p_plot.add_argument("-o", "--output", type=str, default=None, help="Çıktı PNG dosyası yolu")

    # predict
    p_pred = subparsers.add_parser("predict", help="Tekil sensör ölçümü için kalite tahmini yapar")
    p_pred.add_argument("--tensile", type=float, required=True, help="İplik kopma mukavemeti (cN/tex)")
    p_pred.add_argument("--elongation", type=float, required=True, help="Kopma uzaması (%%)")
    p_pred.add_argument("--hairiness", type=float, required=True, help="Uster H tüylülük indeksi")
    p_pred.add_argument("--twist", type=float, required=True, help="Büküm sayısı (tpm)")
    p_pred.add_argument("--dtex", type=float, required=True, help="İplik numarası (dtex)")
    p_pred.add_argument("--rpm", type=float, required=True, help="Tezgâh devir hızı (rpm)")
    p_pred.add_argument("--tension", type=float, required=True, help="Gerilim dalgalanması (cN)")
    p_pred.add_argument("--humidity", type=float, required=True, help="Ortam bağıl nemi (%%)")
    p_pred.add_argument("--temp", type=float, required=True, help="Ortam sıcaklığı (C)")
    p_pred.add_argument("--weft", type=float, required=True, help="Atkı atım sıklığı (picks/min)")
    p_pred.add_argument("--threshold", type=float, default=None, help="Özel karar eşiği (varsayılan: opt maliyet eşiği)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate-data":
        cmd_generate_data(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "plot":
        cmd_plot(args)
    elif args.command == "predict":
        cmd_predict(args)


if __name__ == "__main__":
    main()
