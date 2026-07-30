"""
cli.py - Terminal Command-Line Interface for Dominant Palette & CIEDE2000 Engine.
"""

import argparse
import json
from pathlib import Path
import time
import numpy as np
import cv2

from .color_models import ExtractedColor
from .ciede2000 import (
    ciede2000_scalar,
    ciede2000_vectorized,
)
from .kmeans_palette import KMeansPaletteExtractor
from .yarn_matcher import YarnMatcher
from .quantizer import CarpetQuantizer
from .generator import create_all_synthetic_fixtures


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
    success, enc = cv2.imencode(".png", img)
    if not success:
        raise RuntimeError(f"Failed to encode image for {path}")
    enc.tofile(str(path))


def cmd_extract(args: argparse.Namespace) -> None:
    """Extract dominant palette and print summary."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)

    extractor = KMeansPaletteExtractor(
        default_k=args.k,
        color_space=args.space,
        subsample_size=args.subsample,
    )

    result = extractor.extract_palette(img, k=args.k, color_space=args.space)

    print(f"\n=======================================================")
    print(f"  DOMINANT PALETTE EXTRACTION (K={result.k}, Space={result.space_used})")
    print(f"=======================================================")
    print(f"Total Pixels : {result.total_pixels:,}")
    print(f"Sample Ratio : {result.sample_ratio * 100:.1f}%")
    print(f"Latency      : {result.elapsed_ms:.2f} ms")
    print(f"Inertia      : {result.inertia:.2f}")
    print("-------------------------------------------------------")
    print(f"{'Rank':<5} | {'Coverage':<10} | {'RGB [R, G, B]':<16} | {'CIE L*a*b*':<22}")
    print("-------------------------------------------------------")
    for c in result.palette:
        rgb_str = f"[{c.rgb[0]:3d}, {c.rgb[1]:3d}, {c.rgb[2]:3d}]"
        lab_str = f"[{c.cielab[0]:6.2f}, {c.cielab[1]:6.2f}, {c.cielab[2]:6.2f}]"
        print(f"#{c.cluster_id:<4} | {c.percentage:6.2f}%    | {rgb_str:<16} | {lab_str:<22}")
    print("=======================================================\n")

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2)
        print(f"Saved extraction report to: {out_p}")


def cmd_match(args: argparse.Namespace) -> None:
    """Extract dominant palette and match against Merinos yarn catalog."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)
    extractor = KMeansPaletteExtractor(default_k=args.k, subsample_size=args.subsample)
    palette_res = extractor.extract_palette(img, k=args.k)

    matcher = YarnMatcher(config_path=args.config)
    plan = matcher.generate_creel_allocation_plan(
        palette_res.palette,
        pattern_name=img_path.stem
    )

    print(f"\n===============================================================================")
    print(f"  MERINOS JACQUARD BOBBIN ALLOCATION PLAN ({plan.allocation_id})")
    print(f"===============================================================================")
    print(f"Pattern Name          : {plan.pattern_name}")
    print(f"Target Creel Size     : {plan.target_creel_size} bobbins")
    print(f"Unique Bobbins Used   : {plan.unique_yarn_count}")
    print(f"Estimated Cost / m^2  : ${plan.total_estimated_yarn_cost_per_m2:.2f} USD")
    print(f"Out-of-Spec Colors    : {plan.uncatalogued_colors_count}")
    print("-------------------------------------------------------------------------------")
    print(f"{'Cluster':<8} | {'Cov%':<6} | {'Matched Bobbin':<20} | {'dE00':<7} | {'dE76':<7} | {'QA Grade':<10}")
    print("-------------------------------------------------------------------------------")
    for m in plan.active_bobbins:
        cov = f"{m.extracted_color.percentage:.1f}%"
        bobbin_str = f"{m.matched_yarn.name} ({m.matched_yarn.yarn_id})"
        print(
            f"#{m.extracted_color.cluster_id:<7} | {cov:<6} | {bobbin_str:<20} | "
            f"{m.delta_e_00:<7.2f} | {m.delta_e_76:<7.2f} | {m.match_grade.value.upper():<10}"
        )
    print("===============================================================================\n")

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)
        print(f"Saved creel plan report to: {out_p}")


def cmd_quantize(args: argparse.Namespace) -> None:
    """Quantize carpet image and export indexed pattern map and error heatmap."""
    img_path = Path(args.image)
    img = _safe_imread(img_path)
    matcher = YarnMatcher(config_path=args.config)
    quantizer = CarpetQuantizer()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.target == "catalog":
        indexed_map, quantized_bgr, error_map, report = quantizer.quantize_to_catalog(
            img, matcher.catalog
        )
    else:
        extractor = KMeansPaletteExtractor(default_k=args.k)
        palette_res = extractor.extract_palette(img, k=args.k)
        indexed_map, quantized_bgr, error_map, report = quantizer.quantize_to_palette(
            img, palette_res.palette
        )

    # Save reconstructed quantized image
    quant_path = out_dir / f"{img_path.stem}_quantized.png"
    _safe_imwrite(quant_path, quantized_bgr)

    # Save indexed map (scaled for visibility 0..255)
    indexed_viz = ((indexed_map.astype(np.float32) / max(1, report.num_colors_used - 1)) * 255).astype(np.uint8)
    indexed_path = out_dir / f"{img_path.stem}_indexed_map.png"
    _safe_imwrite(indexed_path, indexed_viz)

    # Save error heatmap with colormap
    norm_err = np.clip((error_map / 10.0) * 255.0, 0, 255).astype(np.uint8)
    heatmap_bgr = cv2.applyColorMap(norm_err, cv2.COLORMAP_JET)
    heatmap_path = out_dir / f"{img_path.stem}_error_heatmap.png"
    _safe_imwrite(heatmap_path, heatmap_bgr)

    # Save report
    report_path = out_dir / f"{img_path.stem}_quantization_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    print(f"\n=======================================================")
    print(f"  QUANTIZATION SUMMARY ({img_path.stem})")
    print(f"=======================================================")
    print(f"Target Mode       : {args.target}")
    print(f"Unique Colors     : {report.num_colors_used}")
    print(f"Mean Delta E_00   : {report.mean_delta_e_00:.2f}")
    print(f"Max Delta E_00    : {report.max_delta_e_00:.2f}")
    print(f"Quantized Image   : {quant_path}")
    print(f"Error Heatmap     : {heatmap_path}")
    print(f"Report JSON       : {report_path}")
    print("=======================================================\n")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Run comprehensive performance benchmarks for K-Means and CIEDE2000."""
    print("\nRunning Day 09 Benchmark Suite...")
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    paths = create_all_synthetic_fixtures(fixtures_dir)

    test_img = _safe_imread(Path(paths["oriental_classic"]))
    total_pixels = test_img.shape[0] * test_img.shape[1]

    # Benchmark 1: K-Means Subsampling Speedup
    subsample_sizes = [5000, 15000, 50000, 0]  # 0 means full image
    kmeans_results = []

    for size in subsample_sizes:
        size_label = f"{size:,}" if size > 0 else "Full (262,144)"
        extractor = KMeansPaletteExtractor(default_k=6, subsample_size=size, random_state=42)

        times = []
        for _ in range(3):
            t0 = time.perf_counter()
            res = extractor.extract_palette(test_img, k=6)
            times.append((time.perf_counter() - t0) * 1000.0)

        mean_ms = round(float(np.mean(times)), 2)
        fps = round(1000.0 / mean_ms, 1)
        kmeans_results.append({
            "subsample_size": size_label,
            "mean_ms": mean_ms,
            "throughput_fps": fps,
            "inertia": round(res.inertia, 2),
        })

    # Benchmark 2: CIEDE2000 vs CIE 1976 Calculation Speed
    num_pairs = 10000
    rng = np.random.default_rng(42)
    labs1 = rng.uniform([0, -80, -80], [100, 80, 80], size=(num_pairs, 3))
    labs2 = rng.uniform([0, -80, -80], [100, 80, 80], size=(num_pairs, 3))

    # CIE 1976 Vectorized
    t0 = time.perf_counter()
    _ = np.linalg.norm(labs1 - labs2, axis=1)
    cie76_ms = (time.perf_counter() - t0) * 1000.0

    # CIEDE2000 Vectorized
    t0 = time.perf_counter()
    _ = ciede2000_vectorized(labs1, labs2)
    ciede00_ms = (time.perf_counter() - t0) * 1000.0

    # Benchmark 3: Sharma et al. (2005) Standard Verification Pairs
    sharma_pairs = [
        {"pair": 1, "lab1": [50.0, 2.6772, -79.7751], "lab2": [50.0, 0.0, -82.7485], "expected": 2.0425},
        {"pair": 2, "lab1": [50.0, 3.1571, -77.2803], "lab2": [50.0, 0.0, -82.7485], "expected": 2.8615},
        {"pair": 3, "lab1": [50.0, 2.4972, -80.9360], "lab2": [50.0, 0.0, -82.7485], "expected": 1.6982},
        {"pair": 4, "lab1": [50.0, 2.8398, -79.2084], "lab2": [50.0, 0.0, -82.7485], "expected": 2.2549},
        {"pair": 5, "lab1": [50.0, -1.3802, -84.9583], "lab2": [50.0, 0.0, -82.7485], "expected": 1.1271},
    ]

    sharma_evaluations = []
    for sp in sharma_pairs:
        computed = ciede2000_scalar(sp["lab1"], sp["lab2"])
        err = abs(computed - sp["expected"])
        sharma_evaluations.append({
            "pair": sp["pair"],
            "computed": round(computed, 4),
            "expected": sp["expected"],
            "abs_error": round(err, 6),
            "status": "PASSED" if err < 1e-3 else "FAILED",
        })

    benchmark_data = {
        "kmeans_benchmarks": kmeans_results,
        "delta_e_vectorized_benchmark_10k_pairs": {
            "cie1976_ms": round(cie76_ms, 3),
            "ciede2000_ms": round(ciede00_ms, 3),
            "ratio_ciede2000_over_cie76": round(ciede00_ms / max(0.001, cie76_ms), 1),
            "ciede2000_pairs_per_sec": int(num_pairs / (ciede00_ms / 1000.0)),
        },
        "sharma_standard_pairs_verification": sharma_evaluations,
    }

    out_file = Path(__file__).resolve().parent.parent / "outputs" / "ciede2000_benchmark.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)

    # Also create palette_summary.md
    summary_md = Path(__file__).resolve().parent.parent / "outputs" / "palette_summary.md"
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("# Day 09: Dominant Renk Paleti ve CIEDE2000 Benchmark Raporu\n\n")
        f.write("## 1. K-Means Alt-Örnekleme Performans Kıyaslaması (512x512)\n\n")
        f.write("| Örnekleme Boyutu | Ortalama Süre (ms) | Throughput (FPS) | İnertia |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for kr in kmeans_results:
            f.write(f"| {kr['subsample_size']} | {kr['mean_ms']} ms | {kr['throughput_fps']} FPS | {kr['inertia']} |\n")
        f.write("\n## 2. Metrik Hesaplama Hızı (10,000 Renk Çifti)\n\n")
        f.write(f"- **CIE 1976 (Öklid):** {cie76_ms:.2f} ms ({int(num_pairs/(cie76_ms/1000.0)):,} çift/sn)\n")
        f.write(f"- **CIEDE2000:** {ciede00_ms:.2f} ms ({int(num_pairs/(ciede00_ms/1000.0)):,} çift/sn)\n\n")
        f.write("## 3. Sharma et al. (2005) Standart Doğrulama Çiftleri\n\n")
        f.write("| Çift | Hesaplanan | Beklenen | Mutlak Hata | Durum |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for se in sharma_evaluations:
            f.write(f"| Çift {se['pair']} | {se['computed']} | {se['expected']} | {se['abs_error']} | {se['status']} |\n")

    print(f"\nSaved benchmark outputs to {out_file} and {summary_md}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Dominant Palette Extraction & CIEDE2000 Matching Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract
    p_ext = subparsers.add_parser("extract", help="Extract dominant color palette")
    p_ext.add_argument("--image", required=True, help="Path to input carpet image")
    p_ext.add_argument("--k", type=int, default=6, help="Number of clusters (default: 6)")
    p_ext.add_argument("--space", choices=["LAB", "RGB"], default="LAB", help="Clustering color space")
    p_ext.add_argument("--subsample", type=int, default=15000, help="Subsample pixel count")
    p_ext.add_argument("--output", help="Path to export JSON report")

    # match
    p_mat = subparsers.add_parser("match", help="Match palette to factory yarn catalog")
    p_mat.add_argument("--image", required=True, help="Path to input carpet image")
    p_mat.add_argument("--k", type=int, default=6, help="Number of clusters (default: 6)")
    p_mat.add_argument("--subsample", type=int, default=15000, help="Subsample pixel count")
    p_mat.add_argument("--config", help="Path to palette_config.json")
    p_mat.add_argument("--output", help="Path to export JSON report")

    # quantize
    p_qnt = subparsers.add_parser("quantize", help="Quantize carpet image to catalog or palette")
    p_qnt.add_argument("--image", required=True, help="Path to input carpet image")
    p_qnt.add_argument("--target", choices=["catalog", "palette"], default="catalog", help="Target colors")
    p_qnt.add_argument("--k", type=int, default=6, help="K for palette mode")
    p_qnt.add_argument("--config", help="Path to palette_config.json")
    p_qnt.add_argument("--output-dir", default="outputs", help="Output directory")

    # benchmark
    subparsers.add_parser("benchmark", help="Run K-Means and CIEDE2000 performance benchmark")

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Generate synthetic carpet images")
    default_fixtures_dir = str(Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets")
    p_gen.add_argument("--output-dir", default=default_fixtures_dir, help="Output directory")

    args = parser.parse_args()

    if args.command == "extract":
        cmd_extract(args)
    elif args.command == "match":
        cmd_match(args)
    elif args.command == "quantize":
        cmd_quantize(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "generate-fixtures":
        out = Path(args.output_dir)
        paths = create_all_synthetic_fixtures(out)
        print("Generated synthetic benchmark fixtures:")
        for k, v in paths.items():
            print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()
