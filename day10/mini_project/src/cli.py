"""
cli.py - Terminal Command-Line Interface for Perspective Rectification & Homography Engine.
"""

import argparse
import json
from pathlib import Path
import time
from typing import Optional
import numpy as np
import cv2

from .models import StandardCarpetRatio, QuadCorners
from .corner_detector import CornerDetector, order_points
from .homography import compute_homography, warp_perspective
from .rectifier import CarpetPerspectiveRectifier
from .generator import generate_all_synthetic_rectification_fixtures


def _safe_imread(path: Path) -> np.ndarray:
    """Safely read image on Windows when path contains Unicode characters."""
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    raw_bytes = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to decode image from {path}")
    return img


def _safe_imwrite(path: Path, img: np.ndarray) -> None:
    """Safely write image on Windows when path contains Unicode characters."""
    path.parent.mkdir(parents=True, exist_ok=True)
    success, enc = cv2.imencode(".png", img)
    if not success:
        raise RuntimeError(f"Failed to encode image for {path}")
    enc.tofile(str(path))


def cmd_detect_corners(args: argparse.Namespace) -> None:
    """Detect 4 exterior carpet corners and optionally export overlay visualization."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)

    detector = CornerDetector()
    raw_corners = detector.detect_corners(img)
    ordered = order_points(raw_corners)
    quad = QuadCorners.from_numpy(ordered)

    lengths = quad.edge_lengths()
    angles = quad.corner_angles()

    print("\n=======================================================")
    print("  CARPET CORNER DETECTION RESULT")
    print("=======================================================")
    print(f"Image Path     : {img_path}")
    print(f"Resolution     : {img.shape[1]}x{img.shape[0]} px")
    print("-------------------------------------------------------")
    print(f"Top-Left (TL)     : ({quad.top_left.x:6.1f}, {quad.top_left.y:6.1f})")
    print(f"Top-Right (TR)    : ({quad.top_right.x:6.1f}, {quad.top_right.y:6.1f})")
    print(f"Bottom-Right (BR) : ({quad.bottom_right.x:6.1f}, {quad.bottom_right.y:6.1f})")
    print(f"Bottom-Left (BL)  : ({quad.bottom_left.x:6.1f}, {quad.bottom_left.y:6.1f})")
    print("-------------------------------------------------------")
    print(f"Edge Lengths (px) : Top={lengths['top']:.1f}, Right={lengths['right']:.1f}, "
          f"Bottom={lengths['bottom']:.1f}, Left={lengths['left']:.1f}")
    print(f"Corner Angles (deg): TL={angles[0]:.1f}°, TR={angles[1]:.1f}°, "
          f"BR={angles[2]:.1f}°, BL={angles[3]:.1f}°")
    print("=======================================================\n")

    if args.overlay_output:
        overlay = detector.draw_corners_overlay(img, ordered)
        out_p = Path(args.overlay_output)
        _safe_imwrite(out_p, overlay)
        print(f"Saved corner overlay visualization to: {out_p}")

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(quad.model_dump(), f, indent=2)
        print(f"Saved corner coordinates JSON to: {out_p}")


def cmd_rectify(args: argparse.Namespace) -> None:
    """Rectify perspective distortion of carpet to orthographic top-down view."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)

    rectifier = CarpetPerspectiveRectifier(config_path=args.config)
    std_ratio = StandardCarpetRatio(args.ratio) if args.ratio else None

    rectified, report = rectifier.rectify(
        img,
        mode=args.mode,
        standard_ratio=std_ratio,
    )

    print("\n===============================================================================")
    print("  CARPET PERSPECTIVE RECTIFICATION REPORT")
    print("===============================================================================")
    print(f"Source Image          : {img_path}")
    print(f"Rectification Mode    : {report.rectification_mode.upper()}")
    print(f"Output Resolution     : {report.target_dimensions[0]}x{report.target_dimensions[1]} px")
    print(f"Output Aspect Ratio   : {report.aspect_ratio:.4f}")
    print(f"Homography Det(H)     : {report.homography.determinant:.6f}")
    print(f"Homography Cond(H)    : {report.homography.condition_number:.2f}")
    print(f"Invertibility Error   : {report.homography.inverse_frobenius_error:.2e}")
    print(f"Max Corner Deviation  : {report.max_angle_deviation:.2f}° from 90.0°")
    print(f"QA Status Grade       : {report.qa_grade.value.upper()}")
    print(f"Status Message        : {report.message}")
    print("===============================================================================\n")

    if args.output_image:
        out_img_p = Path(args.output_image)
        _safe_imwrite(out_img_p, rectified)
        print(f"Saved rectified image to: {out_img_p}")

    if args.output_report:
        out_rep_p = Path(args.output_report)
        out_rep_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_rep_p, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)
        print(f"Saved rectification report to: {out_rep_p}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Run performance benchmarks on corner detection, homography solve, and warping."""
    print("\nRunning Day 10 Benchmark Suite...")
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    paths = generate_all_synthetic_rectification_fixtures(fixtures_dir)

    img_25 = _safe_imread(Path(paths["oblique_25deg"]))
    img_35 = _safe_imread(Path(paths["conveyor_35deg"]))
    img_45 = _safe_imread(Path(paths["severe_45deg"]))

    detector = CornerDetector()
    rectifier = CarpetPerspectiveRectifier()

    test_images = [
        ("Oblique 25 deg", img_25),
        ("Conveyor 35 deg", img_35),
        ("Severe 45 deg", img_45),
    ]

    benchmark_records = []
    for label, img in test_images:
        # Measure corner detection latency
        t0 = time.perf_counter()
        for _ in range(5):
            corners = detector.detect_corners(img)
        corner_ms = round(((time.perf_counter() - t0) / 5) * 1000.0, 2)

        # Measure rectification latency
        t0 = time.perf_counter()
        for _ in range(5):
            rectified, report = rectifier.rectify(img, corners=corners)
        rect_ms = round(((time.perf_counter() - t0) / 5) * 1000.0, 2)

        orig_quad = QuadCorners.from_numpy(corners)
        orig_angles = orig_quad.corner_angles()
        orig_max_dev = max(abs(a - 90.0) for a in orig_angles)

        benchmark_records.append({
            "distortion_case": label,
            "corner_detect_ms": corner_ms,
            "full_rectify_ms": rect_ms,
            "throughput_fps": round(1000.0 / rect_ms, 1),
            "original_max_angle_skew_deg": round(orig_max_dev, 2),
            "rectified_max_angle_skew_deg": report.max_angle_deviation,
            "homography_cond_number": report.homography.condition_number,
            "qa_grade": report.qa_grade.value.upper(),
        })

    # Benchmark 2: Scaling across resolutions (512, 1024, 2048)
    resolutions = [(512, 512), (1024, 1024), (2048, 2048)]
    scaling_records = []
    H_mock = np.array([
        [1.2, 0.1, -50.0],
        [-0.05, 1.15, -30.0],
        [0.0002, 0.0001, 1.0],
    ], dtype=np.float64)

    for w, h in resolutions:
        dummy = np.full((h, w, 3), 128, dtype=np.uint8)
        t0 = time.perf_counter()
        for _ in range(10):
            _ = warp_perspective(dummy, H_mock, (w, h))
        mean_warp_ms = round(((time.perf_counter() - t0) / 10) * 1000.0, 2)
        scaling_records.append({
            "resolution": f"{w}x{h}",
            "megapixels": round((w * h) / 1e6, 2),
            "warp_latency_ms": mean_warp_ms,
            "fps": round(1000.0 / mean_warp_ms, 1),
        })

    benchmark_data = {
        "distortion_angle_benchmarks": benchmark_records,
        "resolution_scaling_benchmarks": scaling_records,
    }

    out_file = Path(__file__).resolve().parent.parent / "outputs" / "rectification_benchmark.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)

    summary_md = Path(__file__).resolve().parent.parent / "outputs" / "rectification_summary.md"
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("# Day 10: Perspektif Düzeltme ve Homografi Benchmark Raporu\n\n")
        f.write("## 1. Farklı Perspektif Açılarında Düzeltme Performansı\n\n")
        f.write("| Açı Durumu | Köşe Tespiti (ms) | Tam Düzeltme (ms) | FPS | Ham Skew (°) | Düzeltilmiş Skew (°) | Cond(H) | Kalite |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for br in benchmark_records:
            f.write(
                f"| {br['distortion_case']} | {br['corner_detect_ms']} ms | {br['full_rectify_ms']} ms | "
                f"{br['throughput_fps']} FPS | {br['original_max_angle_skew_deg']}° | "
                f"{br['rectified_max_angle_skew_deg']}° | {br['homography_cond_number']} | {br['qa_grade']} |\n"
            )

        f.write("\n## 2. Çözünürlük Ölçekleme Performansı (Homografi Warping)\n\n")
        f.write("| Çözünürlük | Megapiksel | Ortalama Süre (ms) | Throughput (FPS) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for sr in scaling_records:
            f.write(f"| {sr['resolution']} | {sr['megapixels']} MP | {sr['warp_latency_ms']} ms | {sr['fps']} FPS |\n")

    print(f"\nSaved benchmark outputs to {out_file} and {summary_md}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Carpet Perspective Rectification & Homography Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect-corners
    p_det = subparsers.add_parser("detect-corners", help="Detect 4 carpet corners")
    p_det.add_argument("--image", required=True, help="Path to input carpet image")
    p_det.add_argument("--output", help="Path to export JSON coordinates")
    p_det.add_argument("--overlay-output", help="Path to export overlay visualization PNG")

    # rectify
    p_rec = subparsers.add_parser("rectify", help="Rectify carpet image perspective")
    p_rec.add_argument("--image", required=True, help="Path to input carpet image")
    p_rec.add_argument("--mode", choices=["adaptive", "standard"], default="adaptive", help="Rectification mode")
    p_rec.add_argument("--ratio", choices=["160x230", "200x290", "80x150", "100x100"], help="Standard size ratio")
    p_rec.add_argument("--config", help="Path to rectification_config.json")
    p_rec.add_argument("--output-image", help="Path to save rectified PNG")
    p_rec.add_argument("--output-report", help="Path to save report JSON")

    # benchmark
    subparsers.add_parser("benchmark", help="Run rectification benchmark suite")

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Generate synthetic perspective-distorted carpets")
    default_fix = str(Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets")
    p_gen.add_argument("--output-dir", default=default_fix, help="Output directory")

    args = parser.parse_args()

    if args.command == "detect-corners":
        cmd_detect_corners(args)
    elif args.command == "rectify":
        cmd_rectify(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "generate-fixtures":
        out = Path(args.output_dir)
        paths = generate_all_synthetic_rectification_fixtures(out)
        print("Generated synthetic rectification fixtures:")
        for k, v in paths.items():
            print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()
