"""
cli.py - Terminal Command Line Interface for Day 11 Morphological Defect Detection.
"""

import argparse
import json
from pathlib import Path
import time
import numpy as np
import cv2

from day11.mini_project.src.models import RollDecision
from day11.mini_project.src.morphology_engine import MorphologyEngine
from day11.mini_project.src.defect_detector import CarpetDefectDetector
from day11.mini_project.src.generator import (
    generate_all_synthetic_defect_fixtures,
    _safe_imwrite,
)


def _safe_imread(path: Path) -> np.ndarray:
    """Safely read an image from path supporting non-ASCII Windows paths."""
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {path}")
    raw_data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to decode image at {path}")
    return img


def cmd_generate_fixtures(args: argparse.Namespace) -> None:
    """Generate synthetic carpet defect fixtures."""
    out_dir = Path(args.output_dir)
    fixtures = generate_all_synthetic_defect_fixtures(out_dir)
    print("Generated Day 11 Synthetic Carpet Defect Fixtures:")
    for key, fpath in fixtures.items():
        print(f"  - {key}: {fpath}")


def cmd_inspect(args: argparse.Namespace) -> None:
    """Run defect inspection on a carpet image."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)

    detector = CarpetDefectDetector(
        tophat_thresh=args.tophat_thresh,
        blackhat_thresh=args.blackhat_thresh,
    )
    report, _ = detector.inspect(img, image_path=str(img_path))

    print("\n" + "=" * 65)
    print("  MERINOS CARPET MORPHOLOGICAL DEFECT INSPECTION REPORT")
    print("=" * 65)
    print(f"Image Path          : {report.image_path}")
    print(f"Resolution          : {report.resolution[0]}x{report.resolution[1]} px")
    print(f"Processing Time     : {report.processing_time_ms:.2f} ms")
    print(f"Total Defects Found : {report.total_defects}")
    print(f"Roll Quality Grade  : {report.roll_decision.value}")
    print("-" * 65)
    print("Defect Breakdown by Type:")
    if report.defect_counts:
        for dtype, count in report.defect_counts.items():
            print(f"  - {dtype:<20}: {count}")
    else:
        print("  None (Zero Defects Detected - Pristine Surface)")
    print("-" * 65)

    if report.defects:
        print("Detected Anomalies:")
        for i, d in enumerate(report.defects, 1):
            box = d.bbox
            print(
                f"  #{i:02d} [{d.severity.value:<8}] {d.defect_type.value:<16} "
                f"at ({box.x}, {box.y}) size={box.width}x{box.height} "
                f"area={box.area:.0f}px contrast={d.mean_contrast:.1f} conf={d.confidence*100:.0f}%"
            )
    print("=" * 65 + "\n")

    # Save output overlay image if requested
    if args.output_image:
        out_img_path = Path(args.output_image)
        out_img_path.parent.mkdir(parents=True, exist_ok=True)
        annotated = CarpetDefectDetector.annotate_defects(img, report.defects)
        _safe_imwrite(out_img_path, annotated)
        print(f"Saved annotated defect image to: {out_img_path}")

    # Save JSON report if requested
    if args.output_report:
        out_rep_path = Path(args.output_report)
        out_rep_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_rep_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"Saved inspection report JSON to: {out_rep_path}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Run morphological operations latency & throughput benchmark."""
    print("\nRunning Day 11 Morphology Benchmark Suite...")
    resolutions = [(512, 512), (1024, 1024), (2048, 2048)]
    benchmark_data = {"operators": {}, "full_pipeline": {}}

    # 1. Individual Operators Benchmark on 1024x1024
    test_img = np.random.randint(0, 256, (1024, 1024), dtype=np.uint8)
    engine_rect = MorphologyEngine(kernel_size=11)
    k_weft = MorphologyEngine.get_directional_kernel("horizontal", 17, 1)

    ops = {
        "Erosion (11x11)": lambda: engine_rect.erode(test_img),
        "Dilation (11x11)": lambda: engine_rect.dilate(test_img),
        "Opening (11x11)": lambda: engine_rect.opening(test_img),
        "Closing (11x11)": lambda: engine_rect.closing(test_img),
        "Morph Gradient (11x11)": lambda: engine_rect.gradient(test_img),
        "White Top-Hat (11x11)": lambda: engine_rect.white_tophat(test_img),
        "Black Top-Hat (11x11)": lambda: engine_rect.black_tophat(test_img),
        "Directional Weft BTH (1x17)": lambda: cv2.morphologyEx(test_img, cv2.MORPH_BLACKHAT, k_weft),
    }

    print("\n1. Operator-Level Latency on 1024x1024 px:")
    for name, fn in ops.items():
        # Warmup
        for _ in range(5):
            fn()
        t0 = time.perf_counter()
        n_iters = 30
        for _ in range(n_iters):
            fn()
        avg_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        benchmark_data["operators"][name] = {"avg_latency_ms": round(avg_ms, 3), "fps": round(fps, 1)}
        print(f"  - {name:<28}: {avg_ms:6.2f} ms | {fps:7.1f} FPS")

    # 2. Full Pipeline Benchmark across Resolutions
    print("\n2. Full Inspection Pipeline Throughput:")
    detector = CarpetDefectDetector()
    for w_res, h_res in resolutions:
        color_img = np.random.randint(0, 256, (h_res, w_res, 3), dtype=np.uint8)
        # Warmup
        for _ in range(3):
            detector.inspect(color_img)
        t0 = time.perf_counter()
        n_iters = 10
        for _ in range(n_iters):
            detector.inspect(color_img)
        avg_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        mp = (w_res * h_res) / 1e6
        benchmark_data["full_pipeline"][f"{w_res}x{h_res}"] = {
            "megapixels": round(mp, 2),
            "avg_latency_ms": round(avg_ms, 2),
            "fps": round(fps, 1),
        }
        print(f"  - {w_res}x{h_res:<10} ({mp:.2f} MP): {avg_ms:6.2f} ms | {fps:6.1f} FPS")

    out_dir = Path("day11/mini_project/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "morphology_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)

    # Markdown summary
    md_path = out_dir / "morphology_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Day 11: Morfolojik Operasyonlar ve Kusur Tespiti Benchmark Raporu\n\n")
        f.write("## 1. Operatör Bazlı Gecikme ve Throughput (1024x1024 px)\n\n")
        f.write("| Operatör | Ortalama Süre (ms) | Throughput (FPS) |\n")
        f.write("| :--- | :--- | :--- |\n")
        for op_name, stats in benchmark_data["operators"].items():
            f.write(f"| {op_name} | {stats['avg_latency_ms']:.2f} ms | {stats['fps']:.1f} FPS |\n")

        f.write("\n## 2. Çözünürlük Ölçekleme Performansı (Tam Pipeline)\n\n")
        f.write("| Çözünürlük | Megapiksel | Ortalama Süre (ms) | Throughput (FPS) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for res_name, stats in benchmark_data["full_pipeline"].items():
            f.write(f"| {res_name} | {stats['megapixels']} MP | {stats['avg_latency_ms']:.2f} ms | {stats['fps']:.1f} FPS |\n")

    print(f"\nSaved benchmark outputs to {json_path} and {md_path}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Carpet Morphological Defect Detection CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Generate synthetic defect fixtures")
    p_gen.add_argument(
        "--output-dir",
        default="day11/mini_project/fixtures/synthetic_carpets",
        help="Target output directory",
    )
    p_gen.set_defaults(func=cmd_generate_fixtures)

    # inspect
    p_ins = subparsers.add_parser("inspect", help="Inspect carpet image for defects")
    p_ins.add_argument("--image", required=True, help="Path to input carpet image")
    p_ins.add_argument("--output-image", default=None, help="Path to save annotated overlay image")
    p_ins.add_argument("--output-report", default=None, help="Path to save inspection JSON report")
    p_ins.add_argument("--tophat-thresh", type=float, default=30.0, help="White top-hat brightness threshold")
    p_ins.add_argument("--blackhat-thresh", type=float, default=28.0, help="Black top-hat darkness threshold")
    p_ins.set_defaults(func=cmd_inspect)

    # benchmark
    p_bm = subparsers.add_parser("benchmark", help="Run morphology operators and pipeline benchmark")
    p_bm.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
