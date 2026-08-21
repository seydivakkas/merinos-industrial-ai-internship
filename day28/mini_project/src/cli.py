"""
Merinos Industrial AI Internship - Day 28
Command Line Interface (CLI) for Controlled Carpet Generation & Analysis.
Staj Defteri Yaprak 55 & 56 Uyumlu Komut Satırı Arayüzü.
Copyright (c) 2026 Seydi Eryilmaz (@seydivakkas). All Rights Reserved.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Windows console UTF-8 support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from day28.mini_project.src.comparator_engine import ComparatorEngine
from day28.mini_project.src.models import StructuredDesignBrief
from day28.mini_project.src.prompt_structurer import PromptStructurer
from day28.mini_project.src.sdxl_controller import SDXLController
from day28.mini_project.src.visualizer import Day28Visualizer


def main():
    parser = argparse.ArgumentParser(
        description="Merinos Day 28: Kontrollü Halı Görseli Üretimi & Karşılaştırma CLI (Yaprak 55 & 56)."
    )
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir Komutlar")

    # 1. GENERATE
    gen_p = subparsers.add_parser("generate", help="Tekil bir brif için kontrollü desen üretir.")
    gen_p.add_argument("--style", type=str, default="Klasik Osmanlı Saray", help="Tasarım stili")
    gen_p.add_argument("--motif", type=str, default="Barok Madalyon ve Rumi", help="Ana motif")
    gen_p.add_argument("--color", type=str, default="Krem ve Bordo", help="Renk paleti")
    gen_p.add_argument("--composition", type=str, default="Merkezi madalyon", help="Kompozisyon")
    gen_p.add_argument("--border", type=str, default="Su yolu bordürü", help="Bordür")
    gen_p.add_argument("--symmetry", type=str, default="Çift yönlü 4-çeyrek simetri", help="Simetri")
    gen_p.add_argument("--seed", type=int, default=42, help="Tohum değeri")

    # 2. COMPARE SEEDS (Yaprak 55)
    seeds_p = subparsers.add_parser("compare-seeds", help="Yaprak 55: Sabit prompt ile seed varyasyonu deneyini yürütür.")
    seeds_p.add_argument("--brief-id", type=str, default="BRF-CLS-01", help="Baz brif ID")
    seeds_p.add_argument("--seeds", type=int, nargs="+", default=[42, 108, 256, 777], help="Deneysel tohum listesi")

    # 3. COMPARE VARIABLE (Yaprak 56)
    var_p = subparsers.add_parser("compare-variable", help="Yaprak 56: Sabit seed altında tek değişkenli prompt deneyini yürütür.")
    var_p.add_argument("--brief-id", type=str, default="BRF-CLS-01", help="Baz brif ID")
    var_p.add_argument("--field", type=str, default="color", choices=["style", "motif", "color", "composition", "border", "symmetry"], help="Değiştirilecek alan")
    var_p.add_argument("--new-val", type=str, default="Derin Gece Laciverti Zemin ve Varak Altın Vurgular", help="Yeni değer")

    # 4. VERIFY REPRODUCIBILITY (Yaprak 56)
    rep_p = subparsers.add_parser("verify-reproducibility", help="Yaprak 56: Çıkarım determinizmini ve tekrarlanabilirliği (MSE=0) doğrular.")
    rep_p.add_argument("--seed", type=int, default=42, help="Doğrulanacak tohum değeri")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    base_dir = Path(__file__).resolve().parent.parent
    fixtures_file = base_dir / "fixtures" / "sample_design_briefs.json"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    def load_brief(brief_id: str) -> StructuredDesignBrief:
        if fixtures_file.exists():
            with open(fixtures_file, "r", encoding="utf-8") as f:
                briefs = json.load(f)
            for b in briefs:
                if b.get("brief_id") == brief_id:
                    return StructuredDesignBrief(**b)
        return StructuredDesignBrief(
            brief_id=brief_id,
            style="Klasik Osmanlı Saray",
            motif="Barok Madalyon",
            color="Krem Fildişi ve Koyu Bordo",
            composition="Merkezi madalyon",
            border="Geniş su bordürü",
            symmetry="Çift yönlü 4-çeyrek simetri",
            seed=42
        )

    structurer = PromptStructurer()
    controller = SDXLController(structurer=structurer)
    comparator = ComparatorEngine(controller=controller, structurer=structurer)
    visualizer = Day28Visualizer(dpi=300)

    if args.command == "generate":
        brief = StructuredDesignBrief(
            brief_id="BRF-CLI",
            title="CLI Özel Halı Deseni",
            style=args.style,
            motif=args.motif,
            color=args.color,
            composition=args.composition,
            border=args.border,
            symmetry=args.symmetry,
            seed=args.seed
        )
        img, record = controller.generate(brief)
        print("=" * 60)
        print("✅ HALI DESENİ BAŞARIYLA ÜRETİLDİ (Staj Defteri Yaprak 55)")
        print("=" * 60)
        print(f"Brif ID           : {record.brief_id}")
        print(f"Seed              : {record.seed}")
        print(f"Birleştirilen İstem: {record.prompt_assembled}")
        print(f"Görsel Dosyası     : {record.image_path}")
        print(f"İşlem Süresi      : {record.execution_time_sec} saniye")

    elif args.command == "compare-seeds":
        brief = load_brief(args.brief_id)
        print("=" * 60)
        print("🔬 SEED VARYASYONU DENEYİ ÇALIŞTIRILIYOR (Yaprak 55)")
        print("=" * 60)
        comp_res, images = comparator.run_seed_variation_experiment(
            base_brief=brief,
            seeds=args.seeds,
            output_dir=outputs_dir / "seed_variations"
        )
        panel_path = outputs_dir / "seed_variation_grid.png"
        visualizer.plot_seed_variations(comp_res, images, panel_path)
        comp_res.panel_image_path = str(panel_path)

        print(f"Baz Brif      : {brief.title} ({brief.brief_id})")
        print(f"Denenen Seeds : {args.seeds}")
        print(f"300 DPI Panel : {panel_path}")
        print("\nBulgular:")
        for f in comp_res.findings:
            print(f"  • {f}")

    elif args.command == "compare-variable":
        brief = load_brief(args.brief_id)
        print("=" * 60)
        print(f"🔬 TEK DEĞİŞKENLİ PROMPT DENEYİ: '{args.field}' (Yaprak 56)")
        print("=" * 60)
        comp_res, images = comparator.run_single_variable_experiment(
            base_brief=brief,
            field_to_change=args.field,
            new_values=[args.new_val],
            output_dir=outputs_dir / f"mutation_{args.field}"
        )
        panel_path = outputs_dir / "single_variable_comparison.png"
        visualizer.plot_single_variable_comparison(comp_res, images, panel_path)
        comp_res.panel_image_path = str(panel_path)

        print(f"Baz Brif          : {brief.title} ({brief.brief_id})")
        print(f"Sabit Seed        : {brief.seed}")
        print(f"Değiştirilen Alan : {args.field}")
        print(f"Yeni Değer        : {args.new_val}")
        print(f"300 DPI Panel     : {panel_path}")
        print("\nBulgular:")
        for f in comp_res.findings:
            print(f"  • {f}")

    elif args.command == "verify-reproducibility":
        brief = load_brief("BRF-CLS-01").model_copy(update={"seed": args.seed})
        print("=" * 60)
        print(f"🛡️ TEKRARLANABİLİRLİK DOĞRULAMA (Seed={args.seed}) (Yaprak 56)")
        print("=" * 60)
        verif = comparator.verify_reproducibility(brief)
        print(f"Koşu 1 ID  : {verif.run_1_id}")
        print(f"Koşu 2 ID  : {verif.run_2_id}")
        print(f"Piksel MSE : {verif.pixel_mse}")
        print(f"Eşit mi?   : {verif.is_identical}")
        print(f"Sonuç      : {verif.verdict}")


if __name__ == "__main__":
    main()
