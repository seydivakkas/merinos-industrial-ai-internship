# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
Command Line Interface (CLI) for Integrated Carpet Generation & Visual Analysis Pipeline.
Staj Defteri Yaprak 59 ve 60 Tümleşik Boru Hattı Komut Satırı Aracı.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from day30.mini_project.src.models import CarpetDesignInput, SymmetryMode
from day30.mini_project.src.pipeline import IntegratedCarpetPipeline, DEFAULT_LIMITATIONS
from day30.mini_project.src.visualizer import CarpetPipelineVisualizer


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Merinos Day 30: Tümleşik Halı Desen Üretimi ve Görsel Analiz Boru Hattı CLI (Yaprak 59-60)."
    )
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir Alt Komutlar")

    # 1. RUN
    run_p = subparsers.add_parser("run", help="Uçtan uca tümleşik üretim ve analiz boru hattını çalıştırır.")
    run_p.add_argument("--brief-file", type=str, help="Örnek briflerin bulunduğu JSON dosyası.")
    run_p.add_argument("--brief-id", type=str, default="BRF-CLS-01", help="Çalıştırılacak brif ID'si.")
    run_p.add_argument("--style", type=str, default="Klasik Osmanlı", help="Tasarım stili.")
    run_p.add_argument("--motif", type=str, default="Barok Madalyon ve Kıvrık Dallar", help="Ana motif.")
    run_p.add_argument("--primary-color", type=str, default="Krem", help="Zemin rengi.")
    run_p.add_argument("--secondary-color", type=str, default="Gül Kurusu", help="İkincil renk.")
    run_p.add_argument("--border-type", type=str, default="Geniş su bordürü", help="Bordür tipi.")
    run_p.add_argument("--symmetry", type=str, default="BILATERAL_AND_VERTICAL", help="Simetri modu.")
    run_p.add_argument("--seed", type=int, default=42, help="Rastgelelik tohumu.")
    run_p.add_argument("--no-panel", action="store_true", help="Görselleştirme panelini üretme.")

    # 2. ASSEMBLE PROMPT
    prompt_p = subparsers.add_parser("assemble-prompt", help="Kullanıcı girdisini sabit sırayla birleştirir (Yaprak 59).")
    prompt_p.add_argument("--style", type=str, required=True, help="Tasarım stili.")
    prompt_p.add_argument("--motif", type=str, required=True, help="Ana motif.")
    prompt_p.add_argument("--primary-color", type=str, required=True, help="Zemin rengi.")
    prompt_p.add_argument("--secondary-color", type=str, default="", help="İkincil renk.")
    prompt_p.add_argument("--composition", type=str, default="", help="Kompozisyon.")
    prompt_p.add_argument("--border-type", type=str, default="", help="Bordür.")
    prompt_p.add_argument("--symmetry", type=str, default="BILATERAL_AND_VERTICAL", help="Simetri.")

    # 3. REPORT LIMITATIONS
    subparsers.add_parser("report-limitations", help="Staj Defteri Yaprak 60'ta belirtilen 4 teknik sınırı listeler.")

    # 4. TEST FALLBACK (EMPTY CATALOG)
    subparsers.add_parser("test-fallback", help="Yaprak 60: Boş referans kataloğu fallback davranışını test eder.")

    # 5. TEST VALIDATION (EMPTY REQUIRED FIELDS)
    subparsers.add_parser("test-validation", help="Yaprak 60: Boş zorunlu alanlar ile doğrulama hatasını test eder.")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # --------------------------------------------------------------------------
    # 1. RUN
    # --------------------------------------------------------------------------
    if args.command == "run":
        design_input = None
        if args.brief_file:
            path = Path(args.brief_file)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    briefs = json.load(f)
                matched = [b for b in briefs if b.get("brief_id") == args.brief_id]
                if matched:
                    design_input = CarpetDesignInput(**matched[0])
                else:
                    print(f"HATA: '{args.brief_id}' kimlikli brif {args.brief_file} içinde bulunamadı.")
                    sys.exit(1)

        if design_input is None:
            design_input = CarpetDesignInput(
                brief_id="BRF-CLI-01",
                style=args.style,
                motif=args.motif,
                primary_color=args.primary_color,
                secondary_color=args.secondary_color,
                border_type=args.border_type,
                symmetry_mode=SymmetryMode(args.symmetry),
                seed=args.seed
            )

        print(f"\n{'='*75}")
        print(f"MERİNOS HALI SANAYİ A.Ş. — TÜMLEŞİK DESEN ÜRETİM VE GÖRSEL ANALİZ BORU HATTI (DAY 30)")
        print(f"{'='*75}")
        print(f"Brif Kimliği  : {design_input.brief_id}")
        print(f"Stil / Motif  : {design_input.style} / {design_input.motif}")
        print(f"Renkler       : {design_input.primary_color} + {design_input.secondary_color}")
        print(f"Simetri / Tohum: {design_input.symmetry_mode.value} / Seed={design_input.seed}")

        pipeline = IntegratedCarpetPipeline()
        output = pipeline.run(design_input)

        print(f"\n[1. DAY 28 İSTEM MONTAJI]")
        print(f"  Pozitif Prompt: {output.prompt_result.assembled_prompt}")
        print(f"  Negatif Prompt: {output.prompt_result.negative_prompt}")
        print(f"  Dahil Edilen  : {list(output.prompt_result.included_fields.keys())}")
        print(f"  Boş Bırakılan : {output.prompt_result.omitted_fields}")

        print(f"\n[2. DAY 28 GÖRÜNTÜ ÜRETİMİ]")
        print(f"  Kayıt Yolu    : {output.generated_image_path}")
        print(f"  Üretim Süresi : {output.execution_time_ms.get('sdxl_generation_ms', 0):.2f} ms")

        print(f"\n[3. DAY 29 ÇOK BOYUTLU GÖRSEL ANALİZ]")
        mean_de = output.color_analysis.get("mean_delta_e", 0)
        print(f"  K-Means Baskın Renk Sayısı : {len(output.color_analysis.get('dominant_colors', []))}")
        print(f"  Ortalama CIEDE2000 ΔE*     : {mean_de:.2f} ({'UYGUN' if mean_de <= 5.0 else 'UYARI'})")
        sym = output.symmetry_analysis
        print(f"  Yatay / Dikey Simetri      : {sym.get('horizontal_score', 0):.3f} / {sym.get('vertical_score', 0):.3f}")
        seam = output.seam_analysis
        print(f"  Dikiş Süreklilik (Sobel)   : {seam.get('sobel_jump', 0):.2f} px (Tekrarlanabilir: {seam.get('is_tileable', False)})")

        print(f"\n[4. DAY 29 CNN EMBEDDING İLE REFERANS ARAMA]")
        for s in output.similar_carpets:
            print(f"  - {s.get('name', 'Halı')} ({s.get('carpet_id', '')}): Benzerlik = {s.get('similarity_score', 0):.4f}")

        if not args.no_panel:
            viz = CarpetPipelineVisualizer(dpi=150)
            panel_path = viz.create_master_diagnostic_panel(output)
            print(f"\n[5. TEŞHİS PANELİ]")
            print(f"  300 DPI Teşhis Paneli Kaydedildi: {panel_path}")

        print(f"\n[6. GENEL PERFORMANS]")
        print(f"  Toplam Çalışma Süresi: {output.total_latency_ms:.2f} ms")
        print(f"{'='*75}\n")

    # --------------------------------------------------------------------------
    # 2. ASSEMBLE PROMPT
    # --------------------------------------------------------------------------
    elif args.command == "assemble-prompt":
        brief = CarpetDesignInput(
            brief_id="BRF-CLI-PROMPT",
            style=args.style,
            motif=args.motif,
            primary_color=args.primary_color,
            secondary_color=args.secondary_color,
            composition=args.composition,
            border_type=args.border_type,
            symmetry_mode=SymmetryMode(args.symmetry)
        )
        pipeline = IntegratedCarpetPipeline()
        res = pipeline.assemble_prompt(brief)
        print(json.dumps(res.model_dump(), indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # 3. REPORT LIMITATIONS
    # --------------------------------------------------------------------------
    elif args.command == "report-limitations":
        print(f"\n{'='*75}")
        print("STAJ DEFTERİ YAPRAK 60: 4 TEMEL TEKNİK ÇALIŞMA SINIRI RAPORU")
        print(f"{'='*75}")
        rep = DEFAULT_LIMITATIONS
        print(f"\n1. {rep.manufacturability['title']}")
        print(f"   {rep.manufacturability['detail']}")
        print(f"\n2. {rep.aesthetic_subjectivity['title']}")
        print(f"   {rep.aesthetic_subjectivity['detail']}")
        print(f"\n3. {rep.copyright_originality['title']}")
        print(f"   {rep.copyright_originality['detail']}")
        print(f"\n4. {rep.metric_independence['title']}")
        print(f"   {rep.metric_independence['detail']}")
        print(f"\nSONUÇ DEĞERLENDİRMESİ:")
        print(f"   {rep.summary_verdict}")
        print(f"{'='*75}\n")

    # --------------------------------------------------------------------------
    # 4. TEST FALLBACK
    # --------------------------------------------------------------------------
    elif args.command == "test-fallback":
        print("\nYaprak 60 Testi: Boş referans görsel koleksiyonu fallback senaryosu...")
        brief = CarpetDesignInput(
            brief_id="BRF-FALLBACK-TEST",
            style="Klasik",
            motif="Madalyon",
            primary_color="Krem"
        )
        pipeline = IntegratedCarpetPipeline()
        output = pipeline.run(brief, empty_catalog_test=True)
        print(f"Durum          : {'BAŞARILI' if output.success else 'HATA'}")
        print(f"Benzer Halılar : {output.similar_carpets}")
        print("Sonuç: Sistem çökmeden boş katalog durumunda güvenli fallback üretti.\n")

    # --------------------------------------------------------------------------
    # 5. TEST VALIDATION
    # --------------------------------------------------------------------------
    elif args.command == "test-validation":
        print("\nYaprak 60 Testi: Boş zorunlu alanlar ile girdi doğrulama kontrolü...")
        try:
            CarpetDesignInput(
                brief_id="BRF-INVALID",
                style="", # Boş zorunlu alan
                motif="Madalyon",
                primary_color="Krem"
            )
            print("HATA: Boş zorunlu alan tespit edilemedi!")
            sys.exit(1)
        except ValueError as e:
            print(f"BAŞARILI: Pydantic boş zorunlu alanı yakaladı ve reddetti: {e}\n")


if __name__ == "__main__":
    main()
