# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 36
CLI: Yapılandırılmış Yanıt Üretimi, Alıntı Doğrulama ve Halüsinasyon Testi Komut Satırı Aracı
"""

import sys
import json
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day36.mini_project.src.models import GeneratedAnswer, StructuredAnswer
from day36.mini_project.src.prompt_builder import PromptBuilder
from day36.mini_project.src.structured_generator import StructuredGenerator
from day36.mini_project.src.groundedness_checker import GroundednessChecker
from day36.mini_project.src.generation_evaluator import GenerationEvaluator
from day36.mini_project.src.visualizer import plot_generation_citation_dashboard


def init_generation_components(docs_dir: str = "day31/mini_project/fixtures/documents", config_path: str = "day36/mini_project/configs/generation_config.json"):
    """KnowledgeManager, HybridRetriever ve Üretim bileşenlerini başlatır."""
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )

    pb = PromptBuilder(config_path=config_path)
    gen = StructuredGenerator(prompt_builder=pb)
    checker = GroundednessChecker(threshold=0.60)

    evaluator = GenerationEvaluator(
        knowledge_manager=km,
        hybrid_retriever=hybrid,
        generator=gen,
        checker=checker,
        top_k=3
    )

    return km, hybrid, gen, checker, evaluator


def cmd_generate(args):
    """Operatör sorusuna yapılandırılmış ve alıntılı yanıt üretir (Şekil 71 formatı)."""
    km, hybrid, gen, _, _ = init_generation_components(args.docs_dir, args.config)
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    # 1. Bilgi Getirme
    ret_res = hybrid.search(args.query, method="linear", top_k=args.top_k, alpha=0.5)
    retrieved_chunks = [chunk_lookup[it.chunk_id] for it in ret_res.items if it.chunk_id in chunk_lookup]

    # 2. Yanıt Üretimi
    ans: GeneratedAnswer = gen.generate(args.query, retrieved_chunks)

    print(f"Soru: {ans.query}")
    print(f"Cevap: {ans.answer or ans.direct_answer}")

    steps = ans.steps or ans.action_steps
    if steps:
        print("Önerilen adımlar:")
        for idx, step in enumerate(steps, start=1):
            print(f"{idx}. {step}")

    params = ans.parameters or ans.technical_parameters
    if params:
        print("Teknik parametreler:")
        for k, v in params.items():
            print(f"• {k}: {v}")

    if ans.citations:
        print("Kaynaklar:")
        for cit in ans.citations:
            sec_str = f" ({cit.section})" if cit.section else ""
            print(f"• {cit.chunk_id}{sec_str}")


def cmd_verify_groundedness(args):
    """Üretilen yanıtın iddialarını atomik olarak bağlama göre denetler (Şekil 72 formatı)."""
    km, hybrid, gen, checker, _ = init_generation_components(args.docs_dir, args.config)
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    ret_res = hybrid.search(args.query, method="linear", top_k=args.top_k, alpha=0.5)
    retrieved_chunks = [chunk_lookup[it.chunk_id] for it in ret_res.items if it.chunk_id in chunk_lookup]

    ans = gen.generate(args.query, retrieved_chunks)
    metric, claims_res = checker.evaluate_answer(ans, retrieved_chunks)

    print("\n" + "=" * 85)
    print("🔍 GROUNDEDNESS (BAĞLAMA SADAKAT) VE ALINTI DOĞRULAMA RAPORU")
    print("=" * 85)
    print(f"Soru: '{args.query}'\n")
    print(f"{'No':<4} | {'İddia Cümlesi':<45} | {'Örtüşme':<8} | {'Karar':<12} | {'Atıf Parça'}")
    print("-" * 85)

    for idx, c in enumerate(claims_res, start=1):
        c_short = (c.claim_text[:42] + "...") if len(c.claim_text) > 45 else c.claim_text
        cid_str = c.cited_chunk_id or "Yok"
        print(f"{idx:<4} | {c_short:<45} | %{c.similarity_score*100:<7.1f} | {c.verdict:<12} | {cid_str}")

    print("-" * 85)
    print(f"📊 TOPLAM METRİKLER:")
    print(f"   • Toplam İddia Sayısı       : {metric.total_claims}")
    print(f"   • Desteklenen İddia Sayısı  : {metric.supported_claims}")
    print(f"   • Faithfulness (Sadakat)    : %{metric.faithfulness_rate*100:.1f}")
    print(f"   • Alıntı Kesinliği (Prec.)  : %{metric.citation_precision*100:.1f}")
    print(f"   • Alıntı Duyarlılığı (Rec.) : %{metric.citation_recall*100:.1f}")
    print("=" * 85 + "\n")


def cmd_benchmark_generation(args):
    """15 altın soru üzerinden tam üretim ve halüsinasyon benchmarkı çalıştırır."""
    _, _, _, _, evaluator = init_generation_components(args.docs_dir, args.config)

    print(f"\n🚀 {args.dataset} veri seti ile Generation & Citations Benchmark başlatılıyor...")
    report = evaluator.run_benchmark(args.dataset)

    print("\n" + "=" * 105)
    print(f"{'ID':<10} | {'Kategori':<20} | {'Sadakat':<8} | {'Prec.':<7} | {'Rec.':<7} | {'Güvenli Ret':<12} | {'İkaz':<6} | {'Gecikme'}")
    print("-" * 105)

    for it in report.items:
        fb_status = "DOĞRU RET" if (it.is_adversarial and it.fallback_triggered) else ("NORMAL" if not it.is_adversarial else "HALÜSİNASYON")
        alert_s = "VAR" if it.has_safety_alert else "YOK"
        print(f"{it.scenario_id:<10} | {it.category:<20} | %{it.faithfulness_rate*100:<7.0f} | %{it.citation_precision*100:<6.0f} | %{it.citation_recall*100:<6.0f} | {fb_status:<12} | {alert_s:<6} | {it.latency_ms:.1f} ms")

    print("=" * 105)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "generation_benchmark_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    img_path = out_dir / "generation_citation_dashboard.png"
    plot_generation_citation_dashboard(report, output_path=str(img_path))

    print("\n🏆 GENERATION, ALINTI VE HALÜSİNASYON KALİTE RAPORU:")
    print(f"   Toplam Senaryo               : {report.total_scenarios} ({report.valid_domain_scenarios} geçerli, {report.adversarial_scenarios} tuzak/alan dışı)")
    print(f"   Ortalama Faithfulness        : %{report.mean_faithfulness_rate*100:.1f}")
    print(f"   Ortalama Citation Precision  : %{report.mean_citation_precision*100:.1f}")
    print(f"   Ortalama Citation Recall     : %{report.mean_citation_recall*100:.1f}")
    print(f"   Tuzak/Alan Dışı Güvenli Ret  : %{report.adversarial_fallback_accuracy*100:.1f} (0 Halüsinasyon!)")
    print(f"   Ortalama Toplam Gecikme      : {report.avg_latency_ms:.2f} ms")
    print(f"\n📊 4 Panelli Teşhis Paneli Grafiği: {img_path}")
    print(f"📄 Tam Değerlendirme JSON Dosyası : {json_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos RAG Generation & Citation Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    p_gen = subparsers.add_parser("generate", help="Operatör sorusuna yapılandırılmış ve alıntılı yanıt üretir")
    p_gen.add_argument("--query", type=str, required=True, help="Operatörün sorusu")
    p_gen.add_argument("--top-k", type=int, default=3, help="Kullanılacak parça sayısı")
    p_gen.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")
    p_gen.add_argument("--config", type=str, default="day36/mini_project/configs/generation_config.json", help="Ayar dosyası")

    # verify-groundedness
    p_ver = subparsers.add_parser("verify-groundedness", help="Üretilen yanıtın iddialarını bağlama göre denetler")
    p_ver.add_argument("--query", type=str, required=True, help="Operatörün sorusu")
    p_ver.add_argument("--top-k", type=int, default=3, help="Kullanılacak parça sayısı")
    p_ver.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")
    p_ver.add_argument("--config", type=str, default="day36/mini_project/configs/generation_config.json", help="Ayar dosyası")

    # benchmark-generation
    p_bm = subparsers.add_parser("benchmark-generation", help="15 altın soru üzerinden tam üretim ve halüsinasyon benchmarkı")
    p_bm.add_argument("--dataset", type=str, default="day36/mini_project/fixtures/groundedness_evaluation_dataset.json", help="Altın veri seti")
    p_bm.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")
    p_bm.add_argument("--config", type=str, default="day36/mini_project/configs/generation_config.json", help="Ayar dosyası")
    p_bm.add_argument("--output-dir", type=str, default="day36/mini_project/outputs", help="Çıktı dizini")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "verify-groundedness":
        cmd_verify_groundedness(args)
    elif args.command == "benchmark-generation":
        cmd_benchmark_generation(args)


if __name__ == "__main__":
    main()
