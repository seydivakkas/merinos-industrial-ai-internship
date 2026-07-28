"""Command Line Interface and Benchmark Orchestrator for OpenCV Image Analytics Toolkit.

Usage examples:
    python -m day07.mini_project.src.cli analyze --input fixtures/synthetic_carpets/carpet_normal.png
    python -m day07.mini_project.src.cli enhance --input fixtures/synthetic_carpets/carpet_low_contrast.png --method clahe_lab --output outputs/enhanced.png
    python -m day07.mini_project.src.cli benchmark
"""

import argparse
import json
from pathlib import Path
import time
from typing import Any
import cv2
import numpy as np

from day07.mini_project.src.analytics import ImageAnalyticsEngine
from day07.mini_project.src.color_spaces import ColorSpaceConverter
from day07.mini_project.src.equalization import HistogramEqualizer
from day07.mini_project.src.filters import IndustrialFilterPipeline
from day07.mini_project.src.io_validator import ImageIOValidator
from day07.mini_project.src.resizer import AspectPreservingResizer


def run_full_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    """Runs complete end-to-end benchmark across all synthetic carpet fixtures."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    if not fixtures_dir.exists():
        from day07.mini_project.src.generator import SyntheticCarpetGenerator

        SyntheticCarpetGenerator().create_fixture_suite(fixtures_dir)

    fixture_files = {
        "normal": fixtures_dir / "carpet_normal.png",
        "low_contrast": fixtures_dir / "carpet_low_contrast.png",
        "noisy": fixtures_dir / "carpet_noisy.png",
        "uneven": fixtures_dir / "carpet_uneven_illumination.png",
    }

    # 1. Image Profiles
    profiles: dict[str, Any] = {}
    for name, path in fixture_files.items():
        img = ImageIOValidator.read_image(path)
        meta = ImageIOValidator.extract_metadata(img, path)
        prof = ImageAnalyticsEngine.profile_image(img)
        ch_stats = ColorSpaceConverter.channel_statistics(img, "BGR")
        profiles[name] = {
            "metadata": meta.to_dict(),
            "profile": prof.to_dict(),
            "bgr_channel_stats": ch_stats,
        }

    # Save sample analysis report
    sample_report_path = output_dir / "sample_analysis_report.json"
    with open(sample_report_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

    # 2. Timing and Quality Benchmark
    benchmarks: list[dict[str, Any]] = []
    normal_img = ImageIOValidator.read_image(fixture_files["normal"])
    low_con_img = ImageIOValidator.read_image(fixture_files["low_contrast"])
    noisy_img = ImageIOValidator.read_image(fixture_files["noisy"])

    test_ops = [
        ("Gaussian Filter (5x5)", lambda: IndustrialFilterPipeline.gaussian_filter(noisy_img), noisy_img),
        ("Median Filter (k=5)", lambda: IndustrialFilterPipeline.median_filter(noisy_img), noisy_img),
        ("Bilateral Filter (d=9)", lambda: IndustrialFilterPipeline.bilateral_filter(noisy_img), noisy_img),
        ("Unsharp Mask (strength=1.5)", lambda: IndustrialFilterPipeline.unsharp_mask(normal_img), normal_img),
        ("CLAHE Perceptual (LAB L*)", lambda: HistogramEqualizer.enhance_color_perceptual(low_con_img, method="clahe", space="lab"), low_con_img),
        ("CLAHE Perceptual (YCrCb Y)", lambda: HistogramEqualizer.enhance_color_perceptual(low_con_img, method="clahe", space="ycrcb"), low_con_img),
        ("Global HE Perceptual (LAB L*)", lambda: HistogramEqualizer.enhance_color_perceptual(low_con_img, method="global", space="lab"), low_con_img),
        ("Letterbox Resize (512x512)", lambda: AspectPreservingResizer.letterbox(normal_img, (512, 512)).image, normal_img),
    ]

    for op_name, fn, base_img in test_ops:
        # Warmup
        for _ in range(5):
            _ = fn()

        # Timed execution (50 runs)
        num_runs = 50
        start = time.perf_counter()
        res_img = None
        for _ in range(num_runs):
            res_img = fn()
        elapsed_sec = (time.perf_counter() - start) / num_runs
        elapsed_ms = elapsed_sec * 1000.0

        comp = ImageAnalyticsEngine.compare_enhancement(base_img, res_img)
        throughput_fps = round(1.0 / elapsed_sec, 1) if elapsed_sec > 0 else 0.0

        benchmarks.append({
            "operation": op_name,
            "avg_latency_ms": round(elapsed_ms, 3),
            "throughput_fps": throughput_fps,
            "contrast_gain": comp["deltas"]["contrast_gain"],
            "entropy_gain": comp["deltas"]["entropy_gain"],
            "sharpness_gain": comp["deltas"]["sharpness_gain"],
        })

    benchmark_path = output_dir / "image_enhancement_benchmark.json"
    with open(benchmark_path, "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2)

    # 3. Generate Markdown Summary
    md_lines = [
        "# Merinos Görüntü Analitiği ve Zenginleştirme Kıyaslama Raporu",
        "",
        "> **Tarih:** 2026-09-04  ",
        "> **Kapsam:** Day 07 - OpenCV Görüntü İşleme ve Analitik Araç Kiti  ",
        "> **Lisans:** Özel Lisans — Tüm Hakları Saklıdır (c) 2026 Seydi Eryılmaz  ",
        "",
        "## 1. Operasyon Performans ve Kalite Tablosu",
        "",
        "| Operasyon | Ortalama Gecikme (ms) | Throughput (FPS) | Kontrast Farkı (RMS) | Entropi Değişimi | Keskinlik Değişimi |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for row in benchmarks:
        md_lines.append(
            f"| **{row['operation']}** | `{row['avg_latency_ms']} ms` | **{row['throughput_fps']} FPS** | `{row['contrast_gain']:+.4f}` | `{row['entropy_gain']:+.4f}` | `{row['sharpness_gain']:+.2f}` |"
        )

    md_lines.extend([
        "",
        "## 2. Temel Mühendislik Çıkarımları",
        "- **CLAHE (CIELAB L*):** Düşük kontrastlı halı görüntüsünde renk tonlarını bozmadan RMS kontrastını belirgin şekilde artırır.",
        "- **Bilateral Filtre:** İplik dokusu dalgalanmalarını pürüzsüzleştirirken bordür ve madalyon keskinliğini korur (Kenar korumalı yumuşatma).",
        "- **Letterbox Resizing:** Halıların özgün en-boy oranını bozmadan derin öğrenme modelleri için 512x512 kare tensör üretir.",
    ])

    summary_md_path = output_dir / "toolkit_summary.md"
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    return {
        "sample_report": str(sample_report_path),
        "benchmark_report": str(benchmark_path),
        "summary_markdown": str(summary_md_path),
        "benchmarks_count": len(benchmarks),
    }


def main():
    parser = argparse.ArgumentParser(description="OpenCV Image Analytics Toolkit for Industrial Textile Inspection")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image file and output statistical profile")
    analyze_parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image")

    # enhance
    enhance_parser = subparsers.add_parser("enhance", help="Enhance image with selected filter or equalization")
    enhance_parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image")
    enhance_parser.add_argument(
        "--method",
        "-m",
        type=str,
        default="clahe_lab",
        choices=["clahe_lab", "clahe_ycrcb", "bilateral", "median", "unsharp", "gaussian"],
        help="Enhancement method",
    )
    enhance_parser.add_argument("--output", "-o", type=str, default="enhanced.png", help="Path to save enhanced image")

    # resize
    resize_parser = subparsers.add_parser("resize", help="Letterbox resize image preserving aspect ratio")
    resize_parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image")
    resize_parser.add_argument("--size", "-s", type=int, nargs=2, default=[512, 512], help="Target size: H W")
    resize_parser.add_argument("--output", "-o", type=str, default="resized.png", help="Path to save resized image")

    # benchmark
    subparsers.add_parser("benchmark", help="Run full toolkit benchmark and generate output reports")

    args = parser.parse_args()

    if args.command == "analyze":
        img = ImageIOValidator.read_image(args.input)
        meta = ImageIOValidator.extract_metadata(img, args.input)
        profile = ImageAnalyticsEngine.profile_image(img)
        result = {
            "metadata": meta.to_dict(),
            "profile": profile.to_dict(),
        }
        print(json.dumps(result, indent=2))

    elif args.command == "enhance":
        img = ImageIOValidator.read_image(args.input)
        if args.method == "clahe_lab":
            enhanced = HistogramEqualizer.enhance_color_perceptual(img, method="clahe", space="lab")
        elif args.method == "clahe_ycrcb":
            enhanced = HistogramEqualizer.enhance_color_perceptual(img, method="clahe", space="ycrcb")
        elif args.method == "bilateral":
            enhanced = IndustrialFilterPipeline.bilateral_filter(img)
        elif args.method == "median":
            enhanced = IndustrialFilterPipeline.median_filter(img)
        elif args.method == "unsharp":
            enhanced = IndustrialFilterPipeline.unsharp_mask(img)
        elif args.method == "gaussian":
            enhanced = IndustrialFilterPipeline.gaussian_filter(img)
        else:
            raise ValueError(f"Unknown method {args.method}")

        out_path = ImageIOValidator.write_image(enhanced, args.output)
        comp = ImageAnalyticsEngine.compare_enhancement(img, enhanced)
        print(f"Saved enhanced image to {out_path}")
        print(json.dumps(comp["deltas"], indent=2))

    elif args.command == "resize":
        img = ImageIOValidator.read_image(args.input)
        target_h, target_w = args.size
        res = AspectPreservingResizer.letterbox(img, (target_h, target_w))
        out_path = ImageIOValidator.write_image(res.image, args.output)
        print(f"Saved letterbox resized image to {out_path}")
        print(f"Scale: {res.scale}, Padding: (top={res.pad_top}, bottom={res.pad_bottom}, left={res.pad_left}, right={res.pad_right})")

    elif args.command == "benchmark":
        out = run_full_benchmark()
        print("Benchmark completed successfully:")
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
