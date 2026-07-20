"""
Merinos Industrial AI Internship - Day 29
Command Line Interface for LLM Profiling, Custom Nano-LLM Generation & Hardware Benchmarking.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

# Ensure standard UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import torch

from day29.mini_project.src.custom_nlp_engine import MerinosBPETokenizer, MerinosCausalLM
from day29.mini_project.src.expert_agent import MerinosTextileExpertEngine
from day29.mini_project.src.functional_backend import FunctionalEquivalenceEngine
from day29.mini_project.src.hardware_profiler import HardwareProfiler
from day29.mini_project.src.models import GenerationRequest, NanoLLMConfig
from day29.mini_project.src.visualizer import generate_diagnostic_panel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merinos Day 29: Minimal SLM Selection, Custom Nano-LLM Engine & Hardware Profiling."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: profile
    p_prof = subparsers.add_parser("profile", help="Profiles VRAM and KV cache for candidate models.")
    p_prof.add_argument("--hardware", type=str, default="rtx_4060_8gb", help="Target hardware profile ID.")
    p_prof.add_argument("--model-id", type=str, default="qwen2.5-0.5b", help="Candidate model ID to profile.")

    # Command: generate
    p_gen = subparsers.add_parser("generate", help="Generates domain text using custom Merinos Nano-LLM engine.")
    p_gen.add_argument("--prompt", type=str, default="[ATKI] kopma tespit edildi", help="Text prompt.")
    p_gen.add_argument("--max-new-tokens", type=int, default=25, help="Number of tokens to generate.")
    p_gen.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature.")
    p_gen.add_argument("--top-k", type=int, default=20, help="Top-K sampling.")
    p_gen.add_argument("--moe", action="store_true", help="Enable Sparse Mixture of Experts (MoE) with DeepSeek-style shared expert.")
    p_gen.add_argument("--no-cache", action="store_true", help="Disable KV caching in autoregressive generation.")

    # Command: benchmark
    p_bench = subparsers.add_parser("benchmark", help="Runs SLM candidate evaluation and rankings.")
    p_bench.add_argument("--hardware", type=str, default="rtx_4060_8gb", help="Target hardware ID.")
    p_bench.add_argument("--precision", type=str, default="INT4", help="Preferred quantization precision.")
    p_bench.add_argument("--plot", action="store_true", help="Generate 300 DPI 2x2 master diagnostic panel.")

    # Command: compare-backends
    p_comp = subparsers.add_parser("compare-backends", help="Displays PyTorch vs TensorFlow equivalence catalog.")

    # Command: expert-diagnose
    p_diag = subparsers.add_parser("expert-diagnose", help="Runs industrial expert fault diagnosis and SOP recommendation.")
    p_diag.add_argument("--machine", type=str, default="Van de Wiele RCE02", help="Machine name/id.")
    p_diag.add_argument("--symptom", type=str, default="Sağ rapyer atkı bırakma hatası", help="Observed symptom.")
    p_diag.add_argument("--department", type=str, default="DOKUMA", help="Department (DOKUMA, IPLIK_BCF, RAMOZ_TERBIYE, MEKATRONIK_PLC, DESEN_TASARIM).")
    p_diag.add_argument("--fault-code", type=str, default=None, help="Optional fault code (e.g. ERR-ATK-01, ERR-DES-02).")
    p_diag.add_argument("--temp", type=float, default=None, help="Operating temperature in Celsius.")
    p_diag.add_argument("--pressure", type=float, default=None, help="Operating pressure in bar.")

    # Command: lexicon-lookup
    p_lex = subparsers.add_parser("lexicon-lookup", help="Looks up technical carpet manufacturing terms in factory glossary.")
    p_lex.add_argument("--term", type=str, required=True, help="Term to search (e.g., 'atkı', 'bcf', 'ramöz', 'jakar', 'raport', 'aspect_ratio').")

    # Command: train-domain
    p_train = subparsers.add_parser("train-domain", help="Fine-tunes Nano-LLM on company expert Q&A corpus.")
    p_train.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    p_train.add_argument("--lr", type=float, default=3e-3, help="Learning rate.")

    # Command: design-calc
    p_des = subparsers.add_parser("design-calc", help="Calculates CAD pixel aspect ratio, point density, and creel limits for carpet designers.")
    p_des.add_argument("--reed", type=int, default=700, help="Reed density in ends/meter (e.g. 500, 700, 1000, 1200).")
    p_des.add_argument("--pick", type=int, default=1200, help="Pick density in picks/meter (e.g. 1000, 1200, 1400, 1600).")
    p_des.add_argument("--colors", type=int, default=8, help="Number of yarn colors in the design.")
    p_des.add_argument("--width", type=float, default=2.0, help="Carpet width in meters.")
    p_des.add_argument("--height", type=float, default=3.0, help="Carpet height in meters.")
    p_des.add_argument("--creel-max", type=int, default=8, help="Maximum creel frames/colors supported by machine.")
    p_des.add_argument("--relief", action="store_true", help="Enable 3D relief / drop-stitch carving analysis.")
    p_des.add_argument("--relief-depth", type=float, default=3.0, help="Relief pile height difference in mm.")

    # Command: quality-audit
    p_qual = subparsers.add_parser("quality-audit", help="Audits carpet laboratory test metrics against TSE 2104, ISO 4919 and OEKO-TEX standards.")
    p_qual.add_argument("--gsm-actual", type=float, required=True, help="Actual measured carpet weight (g/m²).")
    p_qual.add_argument("--gsm-target", type=float, default=2400.0, help="Target specification carpet weight (g/m²).")
    p_qual.add_argument("--tuft-lock", type=float, default=28.0, help="Tuft lock withdrawal force in Newton (ISO 4919).")
    p_qual.add_argument("--rubbing", type=float, default=4.5, help="Rubbing color fastness rating on grey scale (ISO 105-X12, 1-5).")
    p_qual.add_argument("--light", type=float, default=6.0, help="Light fastness rating on Blue Wool scale (ISO 105-B02, 1-8).")
    p_qual.add_argument("--martindale", type=int, default=55000, help="Martindale abrasion cycles (ISO 12947).")
    p_qual.add_argument("--no-oeko-tex", action="store_true", help="Flag if OEKO-TEX Standard 100 compliance failed.")

    # Command: oee-calc
    p_oee = subparsers.add_parser("oee-calc", help="Calculates shift downtime cost, lost carpet sqm, and OEE availability.")
    p_oee.add_argument("--downtime", type=float, required=True, help="Unplanned downtime duration in minutes.")
    p_oee.add_argument("--rpm", type=float, default=165.0, help="Loom rotational speed (rpm).")
    p_oee.add_argument("--pick", type=int, default=1200, help="Pick density (picks/meter).")
    p_oee.add_argument("--width", type=float, default=4.0, help="Weaving width in meters.")
    p_oee.add_argument("--shift-min", type=float, default=480.0, help="Planned shift duration in minutes.")
    p_oee.add_argument("--cost-sqm", type=float, default=450.0, help="Carpet unit cost (TL/m²).")
    p_oee.add_argument("--overhead", type=float, default=1850.0, help="Hourly plant overhead cost (TL/hour).")
    p_oee.add_argument("--single-piece", action="store_true", help="Single piece weaving instead of double face-to-face.")
    p_oee.add_argument("--spare-code", type=str, default=None, help="Optional MRP spare part code consumed during repair.")

    # Command: spare-part
    p_sp = subparsers.add_parser("spare-part", help="Queries Merinos ERP spare parts catalog by MRP code.")
    p_sp.add_argument("--code", type=str, required=True, help="Merinos MRP spare part code (e.g. MRP-RAP-101, MRP-EXT-412).")

    return parser.parse_args()


def handle_profile(args: argparse.Namespace) -> None:
    profiler = HardwareProfiler()
    target_model = next((m for m in profiler.candidate_models if m.model_id == args.model_id), None)
    if not target_model:
        print(f"Error: Model ID '{args.model_id}' not found. Available: {[m.model_id for m in profiler.candidate_models]}")
        sys.exit(1)

    print(f"\n========================================================")
    print(f"   HARDWARE PROFILING: {target_model.model_name} ({target_model.params_billion}B params)")
    print(f"   Hardware Target: {args.hardware}")
    print(f"========================================================")

    profiles = profiler.profile_model_quantization(target_model, hardware_id=args.hardware)
    for p in profiles:
        print(f"[{p.precision_type:>4}] Model Size: {p.model_size_gb:>5.2f} GB | KV/1K: {p.kv_cache_per_1k_tokens_mb:>5.2f} MB | "
              f"Compression: {p.compression_ratio:>4.1f}x | Speedup: {p.estimated_speedup:>4.1f}x")


def handle_generate(args: argparse.Namespace) -> None:
    print(f"\n========================================================")
    print(f"   MERINOS NANO-LLM AUTOREGRESSIVE GENERATION ENGINE")
    print(f"========================================================")

    tokenizer = MerinosBPETokenizer(vocab_size=1024)
    config = NanoLLMConfig(
        vocab_size=1024,
        d_model=192,
        n_heads=6,
        n_kv_heads=2,
        n_layers=4,
        intermediate_size=512,
        max_seq_len=256,
        use_moe=args.moe,
        num_experts=4,
        num_experts_per_tok=2,
        use_shared_expert=True,
        attention_logit_soft_capping=30.0 if args.moe else None
    )
    model = MerinosCausalLM(config)
    model.eval()

    params = model.count_parameters()
    arch_type = "Sparse MoE (4 Experts, Top-2 + Shared Expert)" if args.moe else "Dense Causal Transformer"
    print(f"Architecture    : {arch_type}")
    print(f"Total Params    : {params['total']:,} ({params['total'] / 1e6:.2f}M)")
    print(f"Active per Token: {params['active_per_token']:,} ({params['active_per_token'] / 1e6:.2f}M)")
    print(f"KV Caching      : {'Disabled' if args.no_cache else 'Enabled (O(1) Step-by-Step)'}")
    print(f"Model Parameters: {params['total']:,} total ({params['total'] / 1e6:.2f}M)")

    # Encode prompt
    input_ids = tokenizer.encode(args.prompt, add_special_tokens=False)
    print(f"Prompt: '{args.prompt}'")
    print(f"Token IDs: {input_ids}")

    # Generate
    generated_ids = model.generate(
        prompt_tokens=input_ids,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        eos_id=tokenizer.eos_id,
        use_cache=not args.no_cache
    )

    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=False)
    print(f"\nGenerated Output Tokens ({len(generated_ids)} total):")
    print(f"'{generated_text}'")


def handle_benchmark(args: argparse.Namespace) -> None:
    profiler = HardwareProfiler()
    results = profiler.benchmark_all_candidates(hardware_id=args.hardware, preferred_precision=args.precision)

    print(f"\n=========================================================================================")
    print(f"   MERINOS INDUSTRIAL SLM BENCHMARK & SELECTION MATRIX")
    print(f"   Target Hardware: {results['hardware_target']['name']} ({results['hardware_target']['vram_gb']} GB VRAM)")
    print(f"   Preferred Quantization: {results['preferred_precision']}")
    print(f"=========================================================================================")

    print(f"{'Model ID':<18} | {'Params(B)':<9} | {'VRAM(GB)':<8} | {'Fits':<5} | {'TPS':<6} | {'MMLU':<5} | {'Score':<5} | {'Recommended For'}")
    print("-" * 115)

    for item in results["candidates_ranked"]:
        fits_str = "YES" if item["fits_in_vram"] else "NO"
        print(f"{item['model_id']:<18} | {item['params_billion']:<9.2f} | {item['total_vram_gb']:<8.2f} | "
              f"{fits_str:<5} | {item['estimated_tps']:<6.1f} | {item['mmlu_score']:<5.1f} | "
              f"{item['suitability_score']:<5.2f} | {item['recommended_for']}")

    print(f"\nOptimal Minimal SLM Selected: {results['selected_slm'].upper()}")

    # Save benchmark report to disk
    base_dir = Path(__file__).resolve().parent.parent
    out_dir = base_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "llm_profiling_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Benchmark report saved to: {report_file}")

    if args.plot:
        plot_path = out_dir / "llm_profiling_diagnostic_panel.png"
        generate_diagnostic_panel(profiler=profiler, output_path=plot_path)
        print(f"300 DPI Diagnostic Panel generated at: {plot_path}")


def handle_compare_backends(args: argparse.Namespace) -> None:
    catalog = FunctionalEquivalenceEngine.get_catalog()
    print(f"\n=========================================================================================")
    print(f"   PYTORCH VS TENSORFLOW FUNCTIONAL MECHANICS EQUIVALENCE CATALOG")
    print(f"=========================================================================================")
    for item in catalog:
        print(f"\n[{item.category}] -> {item.operation_name}")
        print(f"  Concept   : {item.mathematical_concept}")
        print(f"  PyTorch   : {item.pytorch_syntax}")
        print(f"  TensorFlow: {item.tensorflow_syntax}")
        print(f"  Mechanics : {item.description}")


def handle_expert_diagnose(args: argparse.Namespace) -> None:
    print(f"\n=========================================================================================")
    print(f"   MERINOS INDUSTRIAL EXPERT FAULT DIAGNOSTIC ENGINE")
    print(f"=========================================================================================")
    engine = MerinosTextileExpertEngine()
    params = {}
    if args.temp is not None:
        params["temperature_c"] = args.temp
    if args.pressure is not None:
        params["pressure_bar"] = args.pressure

    result = engine.diagnose_fault(
        machine=args.machine,
        symptom=args.symptom,
        department=args.department,
        fault_code=args.fault_code,
        parameters=params if params else None
    )

    print(f"Machine          : {result['machine']}")
    print(f"Department       : {result['department']}")
    print(f"Assigned Expert  : MoE Expert #{result['assigned_expert']['expert_id']} ({result['assigned_expert']['expert_title']})")
    print(f"Data Source      : {result['data_source']} (Confidence: {result['confidence_score'] * 100:.1f}%)")
    print(f"Structured Prompt: {result['prompt_formatted']}")
    print(f"\nRoot Cause:")
    print(f"  {result['root_cause']}")
    print(f"\nRecommended Action & SOP:")
    print(f"  {result['recommended_action']}")
    print(f"\nSafety Gate Audit:")
    passed_str = "PASSED (Safe to Execute)" if result['safety_audit']['passed'] else "FAILED (Safety Interlock Triggered)"
    print(f"  Status    : {passed_str}")
    if result['safety_audit']['violations']:
        print(f"  Violations:")
        for v in result['safety_audit']['violations']:
            print(f"    - {v}")


def handle_lexicon_lookup(args: argparse.Namespace) -> None:
    print(f"\n=========================================================================================")
    print(f"   MERINOS TEXTILE & CARPET GLOSSARY LOOKUP")
    print(f"=========================================================================================")
    engine = MerinosTextileExpertEngine()
    definition = engine.lookup_term(args.term)
    if definition:
        print(f"Term      : '{args.term}'")
        print(f"Definition: {definition}")
    else:
        print(f"Term '{args.term}' not found in factory glossary.")


def handle_train_domain(args: argparse.Namespace) -> None:
    print(f"\n=========================================================================================")
    print(f"   MERINOS NANO-LLM DOMAIN ADAPTATION FINE-TUNING")
    print(f"=========================================================================================")
    engine = MerinosTextileExpertEngine()
    print(f"Corpus samples loaded: {len(engine.expert_corpus)}")
    print(f"Training for {args.epochs} epochs with lr={args.lr}...")
    metrics = engine.train_domain_adaptation(epochs=args.epochs, learning_rate=args.lr)
    print(f"\nTraining Complete!")
    print(f"  Initial Loss       : {metrics['initial_loss']:.4f}")
    print(f"  Final Loss         : {metrics['final_loss']:.4f}")
    print(f"  Loss Reduction     : {metrics['loss_reduction_pct']}%")
    print(f"  Loss Convergence   : {' -> '.join(str(l) for l in metrics['loss_history'][:4])} ... -> {metrics['final_loss']:.4f}")


def handle_design_calc(args: argparse.Namespace) -> None:
    print(f"\n=========================================================================================")
    print(f"   MERINOS CARPET DESIGNER & CAD DRAFTING SPECIFICATION ENGINE")
    print(f"=========================================================================================")
    engine = MerinosTextileExpertEngine()
    spec = engine.analyze_design_spec(
        reed_density=args.reed,
        pick_density_per_m=args.pick,
        colors_count=args.colors,
        width_m=args.width,
        height_m=args.height,
        max_creel_colors=args.creel_max,
        is_relief=args.relief,
        relief_depth_mm=args.relief_depth
    )

    print(f"Reed Density (Tarak)  : {spec['reed_density_ends_per_m']} tarak/metre")
    print(f"Pick Density (Atkı)   : {spec['pick_density_per_m']} atkı/metre")
    print(f"Carpet Dimensions     : {spec['dimensions_m']}")
    print(f"Color Count           : {spec['colors_count']} renk")
    print(f"Point Density         : {spec['point_density_sqm']:,} nokta/m²")
    print(f"Total Carpet Points   : {spec['total_points_carpet']:,} ilme")
    print(f"Pixel Aspect Ratio    : {spec['pixel_aspect_ratio']:.3f} ({spec['grid_ratio_display']})")
    print(f"Total Reed Dents (En) : {spec['total_reed_dents']} kanca/tarak dişi")
    print(f"Total Picks (Boy)     : {spec['total_picks']} atkı sırası")
    print(f"\nCAD Drawing Recommendation:")
    print(f"  {spec['cad_recommendation']}")
    print(f"\nDesign Rule Audit:")
    passed_str = "PASSED (Safe to Draft)" if spec['design_audit']['passed'] else "WARNING (Design Adjustments Required)"
    print(f"  Status   : {passed_str}")
    if spec['design_audit']['warnings']:
        print(f"  Warnings :")
        for w in spec['design_audit']['warnings']:
            print(f"    - {w}")


def handle_quality_audit(args: argparse.Namespace) -> None:
    print(f"\n========================================================")
    print(f"   MERİNOS KALİTE GÜVENCE & TEST LABORATUVARI STANDART DENETİMİ")
    print(f"   TSE 2104 | ISO 4919 | ISO 105 | OEKO-TEX Standard 100")
    print(f"========================================================")

    engine = MerinosTextileExpertEngine()
    audit_res = engine.audit_carpet_quality(
        gsm_actual=args.gsm_actual,
        gsm_target=args.gsm_target,
        tuft_lock_newton=args.tuft_lock,
        rubbing_fastness=args.rubbing,
        light_fastness=args.light,
        martindale_cycles=args.martindale,
        oeko_tex_certified=not args.no_oeko_tex
    )

    m = audit_res["metrics"]
    cf = audit_res["compliance_flags"]

    print(f"\n[Laboratuvar Ölçümleri & Tolerans Değerlendirmesi]")
    tse_status = "UYGUN (TSE 2104 ±%5 Bandında)" if cf["tse_2104_passed"] else "UYGUN DEĞİL (TSE 2104 Sapması)"
    print(f"  Hedef Metrekare Gramajı (GSM): {m['gsm_target']:.1f} g/m²")
    print(f"  Ölçülen Metrekare Gramajı    : {m['gsm_actual']:.1f} g/m² ({m['gsm_deviation_pct']:+.2f}%) -> {tse_status}")

    tl_status = "UYGUN (ISO 4919 >= 25 N)" if cf["iso_4919_passed"] else "KRİTİK YETERSİZ (< 25 N)"
    print(f"  Tuft-Lock İlme Çekme Kuvveti : {m['tuft_lock_newton']:.1f} N -> {tl_status}")

    rf_status = "UYGUN" if cf["iso_105_rubbing_passed"] else "DÜŞÜK (< 3.0)"
    print(f"  Sürtünme Haslığı (ISO 105-X12): {m['rubbing_fastness']:.1f} (Gri Skala 1-5) -> {rf_status}")

    lf_status = "UYGUN" if cf["iso_105_light_passed"] else "DÜŞÜK (< 6.0)"
    print(f"  Xenon Işık Haslığı (ISO 105-B02): {m['light_fastness']:.1f} (Mavi Yün 1-8) -> {lf_status}")

    mart_status = "UYGUN" if cf["martindale_passed"] else "YETERSİZ (< 50,000)"
    print(f"  Martindale Aşınma Dayanımı   : {m['martindale_cycles']:,} devir -> {mart_status}")

    oeko_status = "UYGUN" if cf["oeko_tex_passed"] else "SERTİFİKASIZ / LİMİT AŞIMI"
    print(f"  OEKO-TEX Standard 100 Class II: {oeko_status}")

    print(f"\n[Genel Kalite Denetim Kararı]")
    print(f"  Karar   : {audit_res['audit_verdict']}")
    print(f"  Durum   : {'ONAYLANDI' if audit_res['overall_passed'] else 'RED / ŞARTLI'}")

    if audit_res["violations"]:
        print(f"\n[Tespit Edilen Standart İhlalleri & Güvenlik Uyarıları]")
        for v in audit_res["violations"]:
            print(f"  - {v}")

    print(f"\n[Laboratuvar Düzeltici Eylemleri (SOP)]")
    for action in audit_res["corrective_actions"]:
        print(f"  * {action}")


def handle_oee_calc(args: argparse.Namespace) -> None:
    print(f"\n========================================================")
    print(f"   MERİNOS OEE DURUŞ & KAYBEDİLEN METREKARE HALI ANALİZİ")
    print(f"   Vardiya Bazlı Maliyet & Üretim Kaybı Hesaplama Modülü")
    print(f"========================================================")

    engine = MerinosTextileExpertEngine()
    res = engine.calculate_oee_and_downtime_loss(
        downtime_minutes=args.downtime,
        loom_speed_rpm=args.rpm,
        pick_density_per_m=args.pick,
        fabric_width_m=args.width,
        planned_shift_minutes=args.shift_min,
        carpet_unit_cost_tl_sqm=args.cost_sqm,
        hourly_overhead_tl=args.overhead,
        is_double_piece=not args.single_piece,
        spare_part_code=args.spare_code
    )

    pr = res["production_rate"]
    lm = res["loss_metrics"]

    print(f"\n[Tezgah & Vardiya Parametreleri]")
    print(f"  Planlanan Vardiya Süresi : {res['planned_shift_minutes']:.0f} dakika (8 saat)")
    print(f"  Plansız Duruş Süresi     : {res['downtime_minutes']:.1f} dakika")
    print(f"  Fiili Çalışma Süresi     : {res['operating_minutes']:.1f} dakika")
    print(f"  OEE Kullanılabilirlik    : %{res['oee_availability_pct']:.2f} (Availability)")
    print(f"  Tezgah Tipi / Dokuma Modu: {'Çift Yüzlü (Face-to-Face x2)' if pr['is_double_piece'] else 'Tek Parça'}")
    print(f"  Dokuma Eni               : {pr['fabric_width_m']:.2f} metre")
    print(f"  Tezgah Hızı / Sıklık     : {pr['loom_speed_rpm']:.0f} rpm | {pr['pick_density_per_m']} atkı/m")
    print(f"  Dakikalık Üretim Hızı    : {pr['linear_speed_m_per_min']:.4f} m/dk ({pr['sqm_per_min']:.2f} m²/dk)")

    print(f"\n[Üretim Kaybı & Finansal Maliyet]")
    print(f"  Kaybedilen Halı Alanı    : {lm['lost_carpet_sqm']:,.2f} m²")
    print(f"  Doğrudan Halı Ciro Kaybı : {lm['carpet_loss_cost_tl']:,.2f} TL (Birim: {args.cost_sqm:.1f} TL/m²)")
    print(f"  Sabit Genel Gider Kaybı  : {lm['overhead_cost_tl']:,.2f} TL (Birim: {args.overhead:.1f} TL/saat)")
    if lm['spare_part_cost_tl'] > 0:
        print(f"  Yedek Parça Bedeli       : {lm['spare_part_cost_tl']:,.2f} TL ({args.spare_code})")
    print(f"  TOPLAM DURUŞ MALİYETİ    : {lm['total_financial_loss_tl']:,.2f} TL")

    if res.get("spare_part_analysis") and res["spare_part_analysis"].get("found"):
        spa = res["spare_part_analysis"]
        print(f"\n[Kullanılan Yedek Parça Durumu]")
        print(f"  Parça: {spa['part_code']} - {spa['name']} ({spa['shelf_location']})")
        print(f"  Kalan Stok: {spa['current_stock']} adet (Eşik: {spa['critical_threshold']}) -> {spa['replenishment_status']}")

    print(f"\n[Denetim & Uzman Tavsiyeleri]")
    for rec in res["audit_recommendations"]:
        print(f"  * {rec}")

    if res["audit"]["warnings"]:
        print(f"\n[Risk & Güvenlik Uyarıları]")
        for w in res["audit"]["warnings"]:
            print(f"  ! {w}")


def handle_spare_part(args: argparse.Namespace) -> None:
    print(f"\n========================================================")
    print(f"   MERİNOS ERP YEDEK PARÇA & KRİTİK STOK SORGULAMA")
    print(f"   SAP/IFS Parça Kodu ve Tedarik Güvenlik Denetimi")
    print(f"========================================================")

    engine = MerinosTextileExpertEngine()
    part = engine.query_spare_part(args.code)

    if not part.get("found"):
        print(f"\n[HATA] {part.get('error')}")
        return

    print(f"\n[Parça Kimlik Kartı]")
    print(f"  Parça Kodu       : {part['part_code']}")
    print(f"  Tanım            : {part['name']}")
    print(f"  Uyumlu Makine    : {part['machine']}")
    print(f"  Departman        : {part['department']}")
    print(f"  Raf / Ambar Yeri : {part['shelf_location']}")
    print(f"  Birim Maliyet    : {part['unit_cost_tl']:,.2f} TL")

    print(f"\n[Stok & İkmal Durumu]")
    print(f"  Mevcut Stok      : {part['current_stock']} adet")
    print(f"  Kritik Emniyet   : {part['critical_threshold']} adet")
    print(f"  Tedarik Süresi   : {part['lead_time_days']} gün ({part['supplier_origin']})")
    print(f"  İkmal Statüsü    : {part['replenishment_status']} -> {part['action_code']}")
    print(f"  Bildirim         : {part['urgency_notice']}")

    print(f"\n[Uyumlu Arıza Kodları]")
    print(f"  Hata Kodları     : {', '.join(part['compatible_fault_codes'])}")

    print(f"\n[Endüstriyel Gerekçe]")
    print(f"  {part['industrial_rationale']}")

    if part["safety_audit"]["warnings"]:
        print(f"\n[Emniyet Stoku Uyarıları]")
        for w in part["safety_audit"]["warnings"]:
            print(f"  ! {w}")


def main() -> None:
    args = parse_args()
    if args.command == "profile":
        handle_profile(args)
    elif args.command == "generate":
        handle_generate(args)
    elif args.command == "benchmark":
        handle_benchmark(args)
    elif args.command == "compare-backends":
        handle_compare_backends(args)
    elif args.command == "expert-diagnose":
        handle_expert_diagnose(args)
    elif args.command == "lexicon-lookup":
        handle_lexicon_lookup(args)
    elif args.command == "train-domain":
        handle_train_domain(args)
    elif args.command == "design-calc":
        handle_design_calc(args)
    elif args.command == "quality-audit":
        handle_quality_audit(args)
    elif args.command == "oee-calc":
        handle_oee_calc(args)
    elif args.command == "spare-part":
        handle_spare_part(args)
    else:
        class DummyArgs:
            hardware = "rtx_4060_8gb"
            precision = "INT4"
            plot = True
        handle_benchmark(DummyArgs())


if __name__ == "__main__":
    main()
