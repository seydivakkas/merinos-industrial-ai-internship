"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Kusur Sınıflandırma CLI Aracı

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict
import numpy as np
import pandas as pd

from .data_generator import MulticlassQualityDataGenerator
from .evaluator import MulticlassEvaluator
from .models import DefectClass, MulticlassEvaluationReport
from .multiclass_classifier import MerinosMulticlassClassifier
from .preprocessor import MulticlassDataPreprocessor
from .visualizer import MulticlassVisualizer

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
        "config": base_dir / "configs" / "multiclass_config.json",
        "data_csv": base_dir / "fixtures" / "multiclass_defect_dataset.csv",
        "report_json": base_dir / "outputs" / "multiclass_master_report.json",
        "plot_png": base_dir / "outputs" / "multiclass_diagnostic_panel.png",
    }


def cmd_generate_data(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    out_path = Path(args.output) if args.output else paths["data_csv"]

    print(f"[*] Çok sınıflı sentetik sensör verisi üretiliyor (n={args.samples})...")
    gen = MulticlassQualityDataGenerator(config_path=str(paths["config"]))
    df = gen.generate_dataset(n_samples=args.samples, random_state=args.seed)

    saved_p = gen.save_dataset(df, str(out_path))
    counts = df["defect_class"].value_counts().sort_index()

    print(f"[+] Veri kümesi başarıyla oluşturuldu: {saved_p}")
    print(f"    - Toplam Satır Sayısı: {len(df)}")
    for k, cnt in counts.items():
        cname = DefectClass(k).name
        print(f"    - Sınıf {k} ({cname:<22}): {cnt:4d} numune (%{cnt/len(df)*100:5.1f})")


def _train_and_evaluate_pipeline(data_csv: Path, config_path: Path):
    if not data_csv.exists():
        print(f"[-] Veri kümesi bulunamadı: {data_csv}. Otomatik üretiliyor...")
        gen = MulticlassQualityDataGenerator(config_path=str(config_path))
        df = gen.generate_dataset()
        gen.save_dataset(df, str(data_csv))
    else:
        df = pd.read_csv(data_csv)

    preprocessor = MulticlassDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df)

    # 1. Softmax Multinomial Lojistik Regresyon
    clf_multi = MerinosMulticlassClassifier(strategy="multinomial", random_state=42)
    clf_multi.fit(X_train, y_train)

    # 2. One-vs-Rest (OvR) Lojistik Regresyon
    clf_ovr = MerinosMulticlassClassifier(strategy="ovr", random_state=42)
    clf_ovr.fit(X_train, y_train)

    evaluator = MulticlassEvaluator()
    summary_multi = evaluator.evaluate_model(clf_multi, X_test, y_test)
    summary_ovr = evaluator.evaluate_model(clf_ovr, X_test, y_test)

    report = evaluator.generate_master_report(
        multinomial_summary=summary_multi,
        ovr_summary=summary_ovr,
        y_test=y_test,
        feature_names=preprocessor.feature_names,
        clf_multinomial=clf_multi,
    )

    cm = evaluator.compute_confusion_matrix(y_test, clf_multi.predict(X_test))
    roc_curves = evaluator.get_ovr_roc_curves(y_test, clf_multi.predict_proba(X_test))

    return preprocessor, clf_multi, clf_ovr, report, cm, roc_curves, X_test, y_test


def cmd_train(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]

    print(f"[*] Çok sınıflı modeller eğitiliyor (Veri: {data_csv})...")
    preprocessor, clf_multi, clf_ovr, report, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    print("[+] Model eğitimi tamamlandı.")
    print(f"    - Softmax Multinomial Eğitim Süresi: {clf_multi.training_time_ms:.2f} ms")
    print(f"    - One-vs-Rest (OvR)   Eğitim Süresi: {clf_ovr.training_time_ms:.2f} ms")
    print("\n    - Sınıf Bazlı En Belirleyici Pozitif Öznitelikler:")
    for c_imp in report.feature_importance:
        top_pos = [f"{list(d.keys())[0]} (+{list(d.values())[0]:.2f})" for d in c_imp.top_positive_features[:2]]
        print(f"      * {c_imp.class_name:<22}: {', '.join(top_pos)}")


def cmd_evaluate(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]
    out_json = Path(args.output) if args.output else paths["report_json"]

    print("[*] Kapsamlı çok sınıflı değerlendirme ve mimari kıyaslama yürütülüyor...")
    _, _, _, report, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    print(f"[+] Değerlendirme raporu kaydedildi: {out_json}")
    print("\n================ DAY 17 ÇOK SINIFLI MODEL KIYASLAMASI ================")
    print(f"{'Metrik':<30} | {'Softmax (Multinomial)':<22} | {'One-vs-Rest (OvR)':<20}")
    print("-" * 78)
    m1 = report.multinomial_model.metrics
    m2 = report.ovr_model.metrics
    print(f"{'Genel Doğruluk (Accuracy)':<30} | %{m1.accuracy*100:<21.2f} | %{m2.accuracy*100:<19.2f}")
    print(f"{'Makro F1-Skoru':<30} | {m1.macro_f1:<22.4f} | {m2.macro_f1:<20.4f}")
    print(f"{'Ağırlıklı F1-Skoru':<30} | {m1.weighted_f1:<22.4f} | {m2.weighted_f1:<20.4f}")
    print(f"{'Cohen Kappa Skoru':<30} | {m1.cohen_kappa:<22.4f} | {m2.cohen_kappa:<20.4f}")
    print(f"{'Log-Loss (Çapraz Entropi)':<30} | {m1.log_loss:<22.4f} | {m2.log_loss:<20.4f}")
    print(f"{'Makro ROC-AUC (OvR)':<30} | {m1.roc_auc_ovr_macro:<22.4f} | {m2.roc_auc_ovr_macro:<20.4f}")
    print(f"{'Çıkarım Gecikmesi (Tekil)':<30} | {report.multinomial_model.inference_latency_ms:<19.4f} ms | {report.ovr_model.inference_latency_ms:<17.4f} ms")
    print(f"{'Çıkarım Kapasitesi (FPS)':<30} | {report.multinomial_model.throughput_fps:<19.1f} FPS| {report.ovr_model.throughput_fps:<17.1f} FPS")
    print("=" * 78)
    print("\n--- Sınıf Bazlı Softmax Başarım Karnesi ---")
    for pc in report.multinomial_model.per_class:
        print(f"  * {pc.class_name:<22}: Precision = %{pc.precision*100:5.1f} | Recall = %{pc.recall*100:5.1f} | F1 = {pc.f1_score:6.4f} (Support: {pc.support})")


def cmd_plot(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = Path(args.data) if args.data else paths["data_csv"]
    out_png = Path(args.output) if args.output else paths["plot_png"]

    print("[*] 2x2 Teşhis paneli grafiği oluşturuluyor...")
    _, _, _, report, cm, roc_curves, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

    viz = MulticlassVisualizer()
    saved_p = viz.plot_diagnostic_panel(report, cm, roc_curves, str(out_png))
    print(f"[+] Teşhis paneli kaydedildi: {saved_p}")


def cmd_predict(args: argparse.Namespace) -> None:
    paths = get_default_paths()
    data_csv = paths["data_csv"]

    preprocessor, clf_multi, _, _, _, _, _, _ = _train_and_evaluate_pipeline(data_csv, paths["config"])

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
    probs = clf_multi.predict_proba(X_sample)[0]
    pred_idx = int(np.argmax(probs))
    conf = float(probs[pred_idx])

    predicted_cls = DefectClass(pred_idx)

    emoji_map = {
        DefectClass.YARN_BREAKAGE: "🧵",
        DefectClass.OIL_STAIN: "🛢️",
        DefectClass.JACQUARD_PATTERN_SHIFT: "📐",
        DefectClass.BORDER_SEWING_DEFECT: "✂️",
    }

    print("\n============== MERİNOS ÇOK SINIFLI KUSUR TEŞHİSİ ==============")
    print(f"Teşhis Edilen Kusur: {emoji_map.get(predicted_cls, '⚠️')} {predicted_cls.name} (Sınıf {pred_idx})")
    print(f"Model Güven Skoru  : %{conf*100:.2f}")
    print("\nOlasılık Dağılımı:")
    for k, p in enumerate(probs):
        cls_name = DefectClass(k).name
        bar = "█" * int(p * 30)
        print(f"  [{k}] {cls_name:<22}: %{p*100:5.1f} | {bar}")
    print("================================================================")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Halı & İplik — Çok Sınıflı Kusur Sınıflandırma CLI Aracı"
    )
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # generate-data
    p_gen = subparsers.add_parser("generate-data", help="Sentetik çok sınıflı sensör verisi üretir")
    p_gen.add_argument("--samples", type=int, default=3000, help="Toplam örneklem sayısı")
    p_gen.add_argument("--seed", type=int, default=42, help="Rastgelelik tohumu")
    p_gen.add_argument("-o", "--output", type=str, default=None, help="Çıktı CSV dosyası yolu")

    # train
    p_train = subparsers.add_parser("train", help="Softmax ve OvR modellerini eğitir")
    p_train.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Çok sınıflı model kıyaslama raporu çıkarır")
    p_eval.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")
    p_eval.add_argument("-o", "--output", type=str, default=None, help="Çıktı JSON rapor yolu")

    # plot
    p_plot = subparsers.add_parser("plot", help="2x2 Teşhis paneli PNG grafiğini üretir")
    p_plot.add_argument("-d", "--data", type=str, default=None, help="Giriş CSV dosyası")
    p_plot.add_argument("-o", "--output", type=str, default=None, help="Çıktı PNG dosyası yolu")

    # predict
    p_pred = subparsers.add_parser("predict", help="Canlı sensör ölçümünden çok sınıflı kusur teşhisi yapar")
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
