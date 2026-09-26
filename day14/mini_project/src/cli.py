"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Klasik Segmentasyon Kıyaslaması CLI Komut Satırı Arayüzü

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import json
from pathlib import Path
import time
from typing import Any, Dict
import cv2
import numpy as np

from .benchmark import SegmentationBenchmarkEngine
from .evaluator import SegmentationEvaluator
from .generator import CarpetSegmentationFixtureGenerator, _safe_imread, _safe_imwrite
from .grabcut_segmenter import GrabCutSegmenter
from .otsu_segmenter import OtsuSegmenter
from .watershed_segmenter import WatershedSegmenter


def load_config() -> Dict[str, Any]:
    """Konfigürasyon dosyasını yükler."""
    cfg_path = Path(__file__).parent.parent / "configs" / "segmentation_config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def cmd_generate_fixtures(args: argparse.Namespace) -> None:
    """Sentetik test halılarını ve birebir Ground Truth maskelerini üretir."""
    out_dir = Path(args.output_dir)
    generator = CarpetSegmentationFixtureGenerator()
    paths = generator.generate_all_fixtures(out_dir)
    print(f"[OK] {len(paths)} adet sentetik halı ve GT maske fikstürü üretildi:")
    for name, p in paths.items():
        print(f"  - {name} -> {p}")


def cmd_segment(args: argparse.Namespace) -> None:
    """Belirtilen halı üzerinde segmentasyon algoritmasını çalıştırır."""
    img_path = Path(args.image)
    image = _safe_imread(img_path)
    if image is None:
        print(f"[HATA] Görsel okunamadı: {img_path}")
        return

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_config()
    method = args.method.upper()

    print(f"[*] Segmentasyon çalıştırılıyor ({method}): {img_path.name}...")

    masks: Dict[str, np.ndarray] = {}

    if method in ("ALL", "OTSU"):
        otsu = OtsuSegmenter(config)
        mask_otsu, t_val = otsu.segment_global(image)
        masks["OTSU"] = mask_otsu
        _safe_imwrite(out_dir / f"{img_path.stem}_otsu_mask.png", mask_otsu)
        print(f"  [+] Otsu maskesi kaydedildi (Eşik: {t_val:.1f})")

    if method in ("ALL", "WATERSHED"):
        ws = WatershedSegmenter(config)
        mask_ws, _, _ = ws.segment(image)
        masks["WATERSHED"] = mask_ws
        _safe_imwrite(out_dir / f"{img_path.stem}_watershed_mask.png", mask_ws)
        print(f"  [+] Watershed maskesi kaydedildi")

    if method in ("ALL", "GRABCUT"):
        gc = GrabCutSegmenter(config)
        mask_gc, _ = gc.segment_with_rect(image, iterations=3)
        masks["GRABCUT"] = mask_gc
        _safe_imwrite(out_dir / f"{img_path.stem}_grabcut_mask.png", mask_gc)
        print(f"  [+] GrabCut maskesi kaydedildi")

    # Karşılaştırma grid görselini oluştur
    gt_mask = None
    if args.gt_mask:
        gt_mask = _safe_imread(Path(args.gt_mask), cv2.IMREAD_GRAYSCALE)

    grid = SegmentationBenchmarkEngine.create_comparison_grid(image, masks, gt_mask)
    grid_path = out_dir / f"{img_path.stem}_segmentation_comparison_grid.png"
    _safe_imwrite(grid_path, grid)
    print(f"  [+] Karşılaştırma grid görseli kaydedildi: {grid_path}")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Tahmin maskesi ile Ground Truth maskeyi kıyaslayıp metrikleri hesaplar."""
    pred_path = Path(args.pred_mask)
    gt_path = Path(args.gt_mask)

    pred = _safe_imread(pred_path, cv2.IMREAD_GRAYSCALE)
    gt = _safe_imread(gt_path, cv2.IMREAD_GRAYSCALE)

    if pred is None or gt is None:
        print("[HATA] Maske dosyaları okunamadı.")
        return

    evaluator = SegmentationEvaluator()
    metrics = evaluator.evaluate_all(pred, gt)

    print("\n" + "=" * 50)
    print("SEGMENTASYON DOĞRULAMA METRİK RAPORU")
    print("=" * 50)
    print(f"  - Intersection over Union (IoU): {metrics.iou:.4f}")
    print(f"  - Dice Katsayısı (F1):          {metrics.dice:.4f}")
    print(f"  - Piksel Doğruluğu:             {metrics.pixel_accuracy:.4f}")
    print(f"  - Hassasiyet (Precision):       {metrics.precision:.4f}")
    print(f"  - Duyarlılık (Recall):          {metrics.recall:.4f}")
    if metrics.boundary_f1 is not None:
        print(f"  - Sınır F1 Skoru (BF-Score):    {metrics.boundary_f1:.4f}")
    print("=" * 50)

    if args.output_json:
        out_p = Path(args.output_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(metrics.model_dump_json(indent=2))
        print(f"[+] Metrik JSON kaydedildi: {out_p}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Tüm segmentasyon yöntemlerini hız ve doğruluk yönünden kıyaslar."""
    config = load_config()
    engine = SegmentationBenchmarkEngine(config)
    generator = CarpetSegmentationFixtureGenerator()

    carpet, gt_mask, _ = generator.generate_medallion_carpet(width=600, height=600)

    print("=" * 65)
    print("Merinos Halı — Day 13 Klasik Segmentasyon Kıyaslama Laboratuvarı")
    print("=" * 65)

    report, masks = engine.run_benchmark(carpet, gt_mask, iterations=10)

    print("\n[1] Algoritma Performans ve Doğruluk Özeti:")
    print(f"{'Metod':<12} | {'Süre (ms)':<10} | {'Throughput':<12} | {'IoU':<8} | {'Dice':<8} | {'BF-Score':<8}")
    print("-" * 65)
    for name, res in report.results.items():
        iou_str = f"{res.metrics.iou:.4f}" if res.metrics else "N/A"
        dice_str = f"{res.metrics.dice:.4f}" if res.metrics else "N/A"
        bf_str = f"{res.metrics.boundary_f1:.4f}" if res.metrics and res.metrics.boundary_f1 else "N/A"
        print(f"{name:<12} | {res.latency_ms:<10.3f} | {res.fps:<6.1f} FPS | {iou_str:<8} | {dice_str:<8} | {bf_str:<8}")

    print("\n[2] Endüstriyel Tavsiyeler:")
    for note in report.industrial_notes:
        print(f"  - {note}")
    print(f"  -> Canlı Hat Önerisi:  {report.recommended_online_method.value}")
    print(f"  -> Kalite Lab Önerisi: {report.recommended_offline_method.value}")

    # Çıktıları kaydet
    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "segmentation_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"\n[+] Benchmark JSON kaydedildi: {json_path}")

    # Karşılaştırma grid görseli
    grid = engine.create_comparison_grid(carpet, masks, gt_mask)
    grid_path = out_dir / "benchmark_comparison_grid.png"
    _safe_imwrite(grid_path, grid)
    print(f"[+] Karşılaştırma Grid görseli kaydedildi: {grid_path}")

    # Markdown Özeti
    summary_path = out_dir / "segmentation_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Day 13: Klasik Segmentasyon Kıyaslama Özeti\n\n")
        f.write("| Yöntem | Ortalama Süre (ms) | Throughput (FPS) | IoU | Dice | BF-Score | Kapsama (%) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for name, res in report.results.items():
            m = res.metrics
            iou = f"{m.iou:.4f}" if m else "-"
            dice = f"{m.dice:.4f}" if m else "-"
            bf = f"{m.boundary_f1:.4f}" if m and m.boundary_f1 else "-"
            f.write(f"| **{name}** | {res.latency_ms} ms | {res.fps} FPS | {iou} | {dice} | {bf} | %{res.foreground_coverage_pct} |\n")

        f.write(f"\n- **Önerilen Canlı Hat Yöntemi:** `{report.recommended_online_method.value}`\n")
        f.write(f"- **Önerilen Laboratuvar Yöntemi:** `{report.recommended_offline_method.value}`\n")
    print(f"[+] Özet Markdown kaydedildi: {summary_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Halı — Day 13 Klasik Segmentasyon Kıyaslama CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Sentetik halı ve GT maske fikstürlerini üretir")
    p_gen.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).parent.parent / "fixtures" / "synthetic_carpets"),
        help="Çıktı klasörü yolu",
    )

    # segment
    p_seg = subparsers.add_parser("segment", help="Halı görüntüsü üzerinde segmentasyon yapar")
    p_seg.add_argument("--image", type=str, required=True, help="Giriş görseli yolu")
    p_seg.add_argument("--method", type=str, default="ALL", choices=["ALL", "OTSU", "WATERSHED", "GRABCUT"])
    p_seg.add_argument("--gt-mask", type=str, default=None, help="İsteğe bağlı GT maskesi")
    p_seg.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).parent.parent / "outputs"),
        help="Maskeler çıktı klasörü",
    )

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Tahmin maskesini GT maskesi ile değerlendirir")
    p_eval.add_argument("--pred-mask", type=str, required=True, help="Tahmin segmentasyon maskesi")
    p_eval.add_argument("--gt-mask", type=str, required=True, help="Ground Truth referans maskesi")
    p_eval.add_argument("--output-json", type=str, default=None, help="JSON çıktı yolu")

    # benchmark
    subparsers.add_parser("benchmark", help="Hız ve doğruluk kıyaslama testini çalıştırır")

    args = parser.parse_args()
    if args.command == "generate-fixtures":
        cmd_generate_fixtures(args)
    elif args.command == "segment":
        cmd_segment(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()
