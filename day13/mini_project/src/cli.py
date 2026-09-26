"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Morfolojik İşlemler, Kenar ve Çizgi Tespiti CLI Arayüzü

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import sys
from pathlib import Path

from .border_cli import (
    cmd_generate_fixtures as cmd_border_fixtures,
    cmd_detect_edges,
    cmd_analyze_borders,
    cmd_benchmark as cmd_border_benchmark,
)
from .defect_cli import (
    inspect_command,
    benchmark_command as cmd_defect_benchmark,
    generate_fixtures_command as cmd_defect_fixtures,
)


def main():
    parser = argparse.ArgumentParser(
        prog="day13_cli",
        description="Merinos Halı Sanayi — Day 13: Morfolojik İşlemler, Kenar ve Çizgi Tespiti CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Alt komutlar")

    # detect-edges
    p_edges = subparsers.add_parser("detect-edges", help="Kenar filtrelerini çalıştır (Sobel, Canny vb.)")
    p_edges.add_argument("--image", required=True, help="Giriş halı görseli yolu")
    p_edges.add_argument("--operator", default="ALL", help="Operatör: SOBEL, SCHARR, LAPLACIAN, CANNY, ALL")
    p_edges.add_argument("--output-dir", default="day13/mini_project/outputs", help="Çıktı dizini")

    # analyze-borders
    p_borders = subparsers.add_parser("analyze-borders", help="Halı bordür paralellik ve diklik analizi")
    p_borders.add_argument("--image", required=True, help="Giriş görseli yolu")
    p_borders.add_argument("--output-image", default=None, help="Overlay görseli çıktı yolu")
    p_borders.add_argument("--output-report", default=None, help="JSON rapor çıktı yolu")

    # inspect-defects
    p_defects = subparsers.add_parser("inspect-defects", help="Morfolojik dokuma kusuru tespiti")
    p_defects.add_argument("--input", required=True, help="Giriş halı görseli")
    p_defects.add_argument("--output-dir", default="day13/mini_project/outputs", help="Çıktı dizini")
    p_defects.add_argument("--report", default=None, help="JSON rapor çıktısı")

    # generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Sentetik fikstürleri üret")
    p_gen.add_argument("--output-dir", default="day13/mini_project/fixtures/borders", help="Bordür fikstürleri çıktı dizini")

    args = parser.parse_args()

    if args.subcommand == "detect-edges":
        cmd_detect_edges(args)
    elif args.subcommand == "analyze-borders":
        cmd_analyze_borders(args)
    elif args.subcommand == "inspect-defects":
        inspect_command(args)
    elif args.subcommand == "generate-fixtures":
        cmd_border_fixtures(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
