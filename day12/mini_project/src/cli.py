"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Bordür Paralellik ve Kenar Tespiti CLI Komut Satırı Arayüzü

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

from .border_analyzer import CarpetBorderAnalyzer
from .edge_operators import EdgeOperatorEngine
from .generator import CarpetBorderFixtureGenerator, _safe_imread, _safe_imwrite


def load_config() -> Dict[str, Any]:
    """Konfigürasyon dosyasını yükler."""
    cfg_path = Path(__file__).parent.parent / "configs" / "border_config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def cmd_generate_fixtures(args: argparse.Namespace) -> None:
    """Sentetik test fikstürlerini üretir."""
    out_dir = Path(args.output_dir)
    generator = CarpetBorderFixtureGenerator()
    paths = generator.generate_all_fixtures(out_dir)
    print(f"[OK] {len(paths)} adet sentetik bordür fikstürü başarıyla üretildi:")
    for name, p in paths.items():
        print(f"  - {name} -> {p}")


def cmd_detect_edges(args: argparse.Namespace) -> None:
    """Belirtilen görüntü üzerinde kenar operatörlerini çalıştırır."""
    img_path = Path(args.image)
    image = _safe_imread(img_path)
    if image is None:
        print(f"[HATA] Görsel okunamadı: {img_path}")
        return

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_config()
    engine = EdgeOperatorEngine(config)
    gray = engine.preprocess_gray(image, apply_blur=True)

    op = args.operator.upper()
    print(f"[*] Kenar tespiti çalıştırılıyor: {op}...")

    if op in ("ALL", "SOBEL"):
        sobel_res = engine.compute_sobel(gray)
        _safe_imwrite(out_dir / f"{img_path.stem}_sobel_magnitude.png", sobel_res["magnitude_uint8"])
        color_sobel = engine.create_color_orientation_map(sobel_res["grad_x"], sobel_res["grad_y"])
        _safe_imwrite(out_dir / f"{img_path.stem}_sobel_orientation.png", color_sobel)
        print(f"  [+] Sobel haritaları kaydedildi: {out_dir}")

    if op in ("ALL", "SCHARR"):
        scharr_res = engine.compute_scharr(gray)
        _safe_imwrite(out_dir / f"{img_path.stem}_scharr_magnitude.png", scharr_res["magnitude_uint8"])
        color_scharr = engine.create_color_orientation_map(scharr_res["grad_x"], scharr_res["grad_y"])
        _safe_imwrite(out_dir / f"{img_path.stem}_scharr_orientation.png", color_scharr)
        print(f"  [+] Scharr haritaları kaydedildi: {out_dir}")

    if op in ("ALL", "LAPLACIAN"):
        lap_res = engine.compute_laplacian(gray, detect_zero_crossings=True)
        _safe_imwrite(out_dir / f"{img_path.stem}_laplacian_abs.png", lap_res["laplacian_uint8"])
        _safe_imwrite(out_dir / f"{img_path.stem}_laplacian_zero_crossings.png", lap_res["zero_crossings"])
        print(f"  [+] Laplacian haritaları kaydedildi: {out_dir}")

    if op in ("ALL", "CANNY"):
        canny_edges = engine.compute_canny(gray)
        _safe_imwrite(out_dir / f"{img_path.stem}_canny_edges.png", canny_edges)
        print(f"  [+] Canny kenar haritası kaydedildi: {out_dir}")


def cmd_analyze_borders(args: argparse.Namespace) -> None:
    """Halı görüntüsünü analiz eder ve paralellik raporu oluşturur."""
    img_path = Path(args.image)
    image = _safe_imread(img_path)
    if image is None:
        print(f"[HATA] Görsel okunamadı: {img_path}")
        return

    config = load_config()
    analyzer = CarpetBorderAnalyzer(config)

    print(f"[*] Bordür paralellik analizi yapılıyor: {img_path.name}...")
    report, intermediates = analyzer.analyze_carpet(image, edge_method=args.method)

    print(f"[SONUÇ] Karar: {report.decision.value} (Süre: {report.processing_time_ms} ms)")
    if report.horizontal_parallelism:
        hp = report.horizontal_parallelism
        print(f"  - Yatay Paralellik (TOP-BOTTOM): Açı Farkı={hp.angle_difference_deg}° (Paralel: {hp.is_parallel})")
    if report.vertical_parallelism:
        vp = report.vertical_parallelism
        print(f"  - Dikey Paralellik (LEFT-RIGHT): Açı Farkı={vp.angle_difference_deg}° (Paralel: {vp.is_parallel})")
    if report.orthogonality_deviation_deg is not None:
        print(f"  - Diklik Sapması (90°): {report.orthogonality_deviation_deg}°")

    # Çıktıları kaydet
    if args.output_report:
        out_report_p = Path(args.output_report)
        out_report_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_report_p, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
        print(f"  [+] JSON raporu kaydedildi: {out_report_p}")

    if args.output_image:
        out_img_p = Path(args.output_image)
        overlay = analyzer.annotate_borders(image, report, intermediates.get("segments"))
        _safe_imwrite(out_img_p, overlay)
        print(f"  [+] Overlay görseli kaydedildi: {out_img_p}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Operatör hızları ve uçtan uca hat benchmark testlerini çalıştırır."""
    config = load_config()
    engine = EdgeOperatorEngine(config)
    analyzer = CarpetBorderAnalyzer(config)

    print("=" * 60)
    print("Merinos Halı — Day 12 Kenar & Bordür Analiz Benchmark Laboratuvarı")
    print("=" * 60)

    # 1. Operatör Karşılaştırması (1024x1024 Sentetik Halı)
    gen = CarpetBorderFixtureGenerator()
    test_img = gen.generate_clean_parallel_carpet(width=1024, height=1024)
    gray = engine.preprocess_gray(test_img, apply_blur=True)

    operators = {
        "Sobel (3x3)": lambda: engine.compute_sobel(gray),
        "Scharr (3x3)": lambda: engine.compute_scharr(gray),
        "Laplacian (3x3)": lambda: engine.compute_laplacian(gray, detect_zero_crossings=True),
        "Canny": lambda: engine.compute_canny(gray),
    }

    n_warmup = 5
    n_iters = 25
    op_results: Dict[str, Any] = {}

    print("\n[1] Temel Kenar Operatör Latansları (1024x1024, 25 Tekrar):")
    for name, fn in operators.items():
        for _ in range(n_warmup):
            fn()
        t0 = time.perf_counter()
        for _ in range(n_iters):
            fn()
        t_total = time.perf_counter() - t0
        avg_ms = (t_total / n_iters) * 1000.0
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0.0
        op_results[name] = {"avg_latency_ms": round(avg_ms, 3), "fps": round(fps, 1)}
        print(f"  - {name:<18}: {avg_ms:6.3f} ms | Throughput: {fps:7.1f} FPS")

    # 2. Uçtan Uca Çözünürlük Ölçekleme
    resolutions = [(512, 512), (1024, 1024), (2048, 2048)]
    res_results: Dict[str, Any] = {}

    print("\n[2] Uçtan Uca Bordür Analiz Hattı Ölçekleme (Canny + PPHT + Bordür Fit):")
    for w, h in resolutions:
        scale_img = gen.generate_clean_parallel_carpet(width=w, height=h)
        for _ in range(3):
            analyzer.analyze_carpet(scale_img, edge_method="CANNY")

        t0 = time.perf_counter()
        n_res_iters = 10
        for _ in range(n_res_iters):
            analyzer.analyze_carpet(scale_img, edge_method="CANNY")
        t_total = time.perf_counter() - t0
        avg_ms = (t_total / n_res_iters) * 1000.0
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0.0
        label = f"{w}x{h}"
        mp = round((w * h) / 1e6, 2)
        res_results[label] = {
            "megapixels": mp,
            "avg_latency_ms": round(avg_ms, 2),
            "fps": round(fps, 1),
        }
        print(f"  - {label:<12} ({mp:4.2f} MP): {avg_ms:6.2f} ms | Throughput: {fps:6.1f} FPS")

    # Çıktıları kaydet
    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    benchmark_data = {
        "operators": op_results,
        "full_pipeline": res_results,
    }

    json_path = out_dir / "edge_line_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)
    print(f"\n[+] Benchmark JSON kaydedildi: {json_path}")

    # Özet Markdown
    summary_path = out_dir / "border_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Day 12: Kenar ve Çizgi Tespiti Benchmark Özeti\n\n")
        f.write("## Operatör Hızları (1024x1024)\n\n")
        f.write("| Operatör | Ortalama Süre (ms) | Throughput (FPS) |\n")
        f.write("| :--- | :--- | :--- |\n")
        for k, v in op_results.items():
            f.write(f"| {k} | {v['avg_latency_ms']} ms | {v['fps']} FPS |\n")

        f.write("\n## Uçtan Uca Hat Ölçekleme\n\n")
        f.write("| Çözünürlük | Megapiksel | Toplam Süre (ms) | FPS |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for k, v in res_results.items():
            f.write(f"| {k} | {v['megapixels']} MP | {v['avg_latency_ms']} ms | {v['fps']} FPS |\n")
    print(f"[+] Özet Markdown kaydedildi: {summary_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Halı — Day 12 Kenar ve Çizgi Tespiti & Bordür Paralellik Analizi CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Sentetik halı bordür fikstürlerini üretir")
    p_gen.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).parent.parent / "fixtures" / "synthetic_carpets"),
        help="Çıktı klasörü yolu",
    )

    # detect-edges
    p_edge = subparsers.add_parser("detect-edges", help="Kenar operatörlerini çalıştırır")
    p_edge.add_argument("--image", type=str, required=True, help="Giriş görseli yolu")
    p_edge.add_argument(
        "--operator",
        type=str,
        default="ALL",
        choices=["ALL", "SOBEL", "SCHARR", "LAPLACIAN", "CANNY"],
        help="Kenar operatörü",
    )
    p_edge.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).parent.parent / "outputs"),
        help="Kenar haritaları çıktı klasörü",
    )

    # analyze-borders
    p_an = subparsers.add_parser("analyze-borders", help="Bordür paralellik ve kalite analizini yapar")
    p_an.add_argument("--image", type=str, required=True, help="Giriş halı görseli")
    p_an.add_argument("--method", type=str, default="CANNY", choices=["CANNY", "SOBEL", "SCHARR", "LAPLACIAN"])
    p_an.add_argument("--output-report", type=str, default=None, help="JSON raporu çıktı yolu")
    p_an.add_argument("--output-image", type=str, default=None, help="Açıklamalı overlay görseli çıktı yolu")

    # benchmark
    subparsers.add_parser("benchmark", help="Hız ve throughput testlerini çalıştırır")

    args = parser.parse_args()
    if args.command == "generate-fixtures":
        cmd_generate_fixtures(args)
    elif args.command == "detect-edges":
        cmd_detect_edges(args)
    elif args.command == "analyze-borders":
        cmd_analyze_borders(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()
