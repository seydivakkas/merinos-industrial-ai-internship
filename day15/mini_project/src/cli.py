"""Unified Command Line Interface for Merinos Industrial Vision Toolkit (Day 15).

Commands:
  generate-fixtures  Generate synthetic carpet test images
  inspect            Run end-to-end 6-stage quality inspection with HUD
  benchmark          Run Phase 2 master latency and throughput profiling
  release-info       Display Phase 2 release manifest and integrated modules
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from day15.mini_project.src.benchmark_suite import Phase2BenchmarkSuite
from day15.mini_project.src.generator import VisionToolkitFixtureGenerator
from day15.mini_project.src.inspect_pipeline import CarpetInspectionPipeline
from day15.mini_project.src.models import QualityVerdict
from day15.mini_project.src.toolkit import safe_write_image


def cmd_generate_fixtures(args: argparse.Namespace) -> int:
    """Generate synthetic test fixtures."""
    out_dir = Path(args.output_dir).resolve()
    print(f"\n[INFO] Generating Merinos Phase 2 test fixtures into: {out_dir}")
    generator = VisionToolkitFixtureGenerator(size=(args.width, args.height))
    saved_paths = generator.generate_all_fixtures(output_dir=out_dir)

    print(f"[SUCCESS] Generated {len(saved_paths)} fixtures:")
    for name, path in saved_paths.items():
        print(f"  * {name:20s} -> {path}")
    print()
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    """Run full 6-stage carpet inspection."""
    img_path = Path(args.image).resolve()
    if not img_path.exists():
        print(f"[ERROR] Specified image does not exist: {img_path}", file=sys.stderr)
        return 1

    print(f"\n==================================================================")
    print(f" MERINOS INDUSTRIAL VISION QA INSPECTION — CARPET SAMPLE")
    print(f" Target Image: {img_path.name}")
    print(f" Carpet ID   : {args.carpet_id}")
    print(f"==================================================================")

    pipeline = CarpetInspectionPipeline()
    report, hud_img = pipeline.inspect(
        image_or_path=img_path,
        carpet_id=args.carpet_id,
        render_hud=True,
    )

    # Print Stage Breakdown
    print(f"\n{'AŞAMA':<35} | {'DURUM':<7} | {'SÜRE (ms)':<10} | AÇIKLAMA")
    print("-" * 80)
    for key, res in report.stage_results.items():
        print(f"{res.stage_name:<35} | {res.status.value:<7} | {res.execution_time_ms:<10.2f} | {res.notes or ''}")
    print("-" * 80)

    # Print Verdict
    print(f"\n[GENEL KALİTE KARARI] : {report.overall_verdict.value}")
    print(f"[TOPLAM GECİKME]     : {report.total_execution_time_ms:.2f} ms")
    print(f"[KUSUR SAYISI]       : {report.defect_count}")
    print(f"[BORDÜR EĞİKLİĞİ]    : {report.border_skew_deg:.2f}°")
    print(f"[RENK SAPMASI (dE)]  : {report.mean_delta_e:.2f}")
    print(f"[MOTİF KAPSAMI]      : {report.motif_coverage_pct:.1f}%")
    print(f"[DESEN TAHMİNİ]      : {report.predicted_pattern} ({report.confidence*100:.0f}%)")
    print(f"[ÖNERİ / AKSİYON]    : {report.summary_recommendation}\n")

    # Save HUD Overlay
    if args.output_hud and hud_img is not None:
        hud_out = Path(args.output_hud).resolve()
        safe_write_image(hud_out, hud_img)
        print(f"[SAVED] HUD Overlay image written to: {hud_out}")

    # Save JSON Report
    if args.output_json:
        json_out = Path(args.output_json).resolve()
        json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"[SAVED] JSON inspection report written to: {json_out}")

    return 0 if report.overall_verdict in [QualityVerdict.ACCEPT, QualityVerdict.WARNING] else 2


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run master Phase 2 benchmark suite."""
    print(f"\n[INFO] Running Phase 2 Master Benchmark Suite ({args.iterations} iterations per module)...")
    suite = Phase2BenchmarkSuite(iterations=args.iterations)
    manifest = suite.run_all_benchmarks()

    print("\n" + suite.format_markdown_table(manifest) + "\n")
    print(f"Overall System Health: {manifest.overall_health}")
    print(f"Total Integrated Modules: {len(manifest.modules)} / {manifest.total_integrated_days} days")

    if args.output_json:
        json_out = Path(args.output_json).resolve()
        json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] Benchmark manifest saved to: {json_out}")

    return 0


def cmd_release_info(args: argparse.Namespace) -> int:
    """Display Phase 2 release manifest."""
    suite = Phase2BenchmarkSuite(iterations=3)
    manifest = suite.run_all_benchmarks()

    print("\n==================================================================")
    print(f" {manifest.app_name} — v{manifest.version}")
    print(f" {manifest.phase}")
    print(f" Tesis: {manifest.facility}")
    print("==================================================================")
    print(f"Sağlık Durumu  : {manifest.overall_health}")
    print(f"Entegre Modüller: {manifest.total_integrated_days} Faz 2 Günü (Day 07 -> Day 14)")
    print(f"\nSürüm Notları:\n{manifest.release_notes}\n")
    print("Entegre Edilen Modül Detayları:")
    for m in manifest.modules:
        print(f"  * [Day {m.day_number:02d}] {m.module_id:36s} | {m.fps:5.1f} FPS | {m.status}")
    print("==================================================================\n")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="merinos-vision",
        description="Merinos Industrial Vision CLI Toolkit (Day 15 Final Release)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Generate synthetic carpet test images")
    p_gen.add_argument(
        "--output-dir",
        "-o",
        default="day15/mini_project/fixtures",
        help="Target folder for generated PNG fixtures",
    )
    p_gen.add_argument("--width", type=int, default=600, help="Carpet width in pixels")
    p_gen.add_argument("--height", type=int, default=600, help="Carpet height in pixels")
    p_gen.set_defaults(func=cmd_generate_fixtures)

    # Subcommand: inspect
    p_insp = subparsers.add_parser("inspect", help="Run 6-stage carpet inspection pipeline")
    p_insp.add_argument("--image", "-i", required=True, help="Path to input carpet image")
    p_insp.add_argument("--carpet-id", default="CARPET-SAMPLE-01", help="Sample identifier")
    p_insp.add_argument("--output-hud", help="Path to save annotated visual HUD image")
    p_insp.add_argument("--output-json", help="Path to save structured JSON report")
    p_insp.set_defaults(func=cmd_inspect)

    # Subcommand: benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run Phase 2 performance benchmarks")
    p_bench.add_argument("--iterations", "-n", type=int, default=10, help="Profiling iterations")
    p_bench.add_argument("--output-json", help="Path to save benchmark manifest JSON")
    p_bench.set_defaults(func=cmd_benchmark)

    # Subcommand: release-info
    p_rel = subparsers.add_parser("release-info", help="Display Phase 2 release manifest")
    p_rel.set_defaults(func=cmd_release_info)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
