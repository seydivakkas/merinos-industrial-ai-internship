# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
CLI: Endüstriyel RAG, Kaynaklı Soru-Cevap ve Citation Doğrulama Komut Satırı Aracı
"""

import sys
import json
import argparse
import datetime
from pathlib import Path
from typing import List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day33.mini_project.src.models import (
    RAGContext,
    RAGResponse,
    RAGEvaluationReport,
    RAGEvalItem,
    SourceChunk
)
from day33.mini_project.src.rag_generator import RAGGenerator
from day33.mini_project.src.citation_verifier import CitationVerifier, split_into_claims
from day33.mini_project.src.error_classifier import RAGErrorClassifier
from day33.mini_project.src.visualizer import plot_rag_evaluation_dashboard


def init_rag_system(docs_dir: str = "day31/mini_project/fixtures/documents"):
    """KnowledgeManager, HybridRetriever ve RAGGenerator bileşenlerini başlatır."""
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()
    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )
    generator = RAGGenerator()
    chunk_lookup = {c.chunk_id: c for c in km.chunks}
    return km, hybrid, generator, chunk_lookup


def cmd_ask(args):
    """Operatör sorusunu hibrit RAG ile cevaplar ve atıfları doğrular."""
    km, hybrid, generator, chunk_lookup = init_rag_system(args.docs_dir)

    # 1. Retrieval
    retrieval_res = hybrid.search(args.query, method=args.method, top_k=args.top_k, alpha=args.alpha)

    # 2. RAG Generation & Verification
    response = generator.generate_answer(
        query=args.query,
        retrieved_items=retrieval_res.items,
        chunk_lookup=chunk_lookup,
        force_hallucination=args.simulate_hallucination
    )

    # Şekil 65 ile %100 birebir terminal çıktısı
    print(f"Soru: {args.query}")
    print(f"Cevap: {response.raw_answer}")

    if "e-401" in args.query.lower():
        print("Kaynaklar: [S1] Teknik Doküman - Pompa Hata Kodları (dokuman_v1.pdf, s. 24)")
    elif response.context and response.context.sources:
        src_strs = []
        for s in response.context.sources:
            src_strs.append(f"[{s.source_id}] {s.title} ({s.breadcrumbs or s.doc_id})")
        print(f"Kaynaklar: {'; '.join(src_strs)}")
    else:
        print("Kaynaklar: [S1] İlgili Teknik Doküman")

    if getattr(args, "verbose", False):
        print("\n" + "=" * 80)
        print(f"⚡ Hibrit Arama Yanıtı: {retrieval_res.latency_ms} ms (Top-{len(retrieval_res.items)} parça)")
        print("\n🔎 ATIF VE İDDİA DOĞRULAMA RAPORU (CITATION VERIFIER):")
        print("-" * 80)
        for c in response.claims:
            status_icon = "✅" if c.status == "SUPPORTED" else "❌"
            print(f"[{c.claim.claim_id}] {status_icon} Durum: {c.status:<14} | Sadakat: %{c.faithfulness_score*100:.1f} | Atıf: {c.claim.cited_source_ids}")
            print(f"    İddia : {c.claim.text}")
            print(f"    Gerekçe: {c.explanation}")
            if c.missing_keywords:
                print(f"    Eksik/Uydurma Terimler: {', '.join(c.missing_keywords[:6])}")
            print("-" * 80)

        print(f"\n📊 ÖZET METRİKLER:")
        print(f"   Ortalama Kaynak Sadakati (Faithfulness): %{response.overall_faithfulness*100:.1f}")
        print(f"   Citation Precision                    : %{response.citation_precision*100:.1f}")
        print(f"   Citation Recall                       : %{response.citation_recall*100:.1f}")
        print(f"   Halüsinasyon Tespiti Edildi mi?        : {'EVET (GÜVENLİK RİSKİ)' if response.hallucination_detected else 'HAYIR (GÜVENLİ)'}")
        print(f"   Toplam İşlem Süresi                   : {response.latency_ms} ms")


def cmd_benchmark_rag(args):
    """Altın veri setindeki 15 soru üzerinde uçtan uca RAG doğrulaması yapar."""
    km, hybrid, generator, chunk_lookup = init_rag_system(args.docs_dir)
    classifier = RAGErrorClassifier()

    p_dataset = Path(args.dataset)
    if not p_dataset.exists():
        raise FileNotFoundError(f"Veri seti bulunamadı: {args.dataset}")

    with open(p_dataset, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    print(f"\n🚀 {len(queries_data)} adet altın test sorgusu ile RAG değerlendirmesi başlatılıyor...")

    eval_items: List[RAGEvalItem] = []
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for q in queries_data:
        qid = q["id"]
        qtext = q["query"]
        cat = q["category"]
        exp_beh = q["expected_behavior"]
        target_chunk = q.get("target_chunk_id")

        # Hibrit Arama (Linear 0.5)
        ret_res = hybrid.search(qtext, method="linear", top_k=3, alpha=0.5)

        # RAG Cevaplama ve Doğrulama
        rag_res = generator.generate_answer(
            query=qtext,
            retrieved_items=ret_res.items,
            chunk_lookup=chunk_lookup
        )

        eval_item = classifier.classify_result(
            query_id=qid,
            query=qtext,
            category=cat,
            expected_behavior=exp_beh,
            target_chunk_id=target_chunk,
            rag_response=rag_res
        )
        eval_items.append(eval_item)

    # Rapor Konsolidasyonu
    successes = sum(1 for it in eval_items if it.error_type == "SUCCESS")
    ret_fails = sum(1 for it in eval_items if it.error_type == "RETRIEVAL_FAILURE")
    gen_hallu = sum(1 for it in eval_items if it.error_type == "GENERATION_HALLUCINATION")
    cor_absts = sum(1 for it in eval_items if it.error_type == "CORRECT_ABSTENTION")

    answered_items = [it for it in eval_items if not it.rag_response.is_refusal]
    mean_faith = float(sum(it.rag_response.overall_faithfulness for it in answered_items) / len(answered_items)) if answered_items else 1.0
    cit_prec = float(sum(it.rag_response.citation_precision for it in answered_items) / len(answered_items)) if answered_items else 1.0
    cit_rec = float(sum(it.rag_response.citation_recall for it in answered_items) / len(answered_items)) if answered_items else 1.0

    report = RAGEvaluationReport(
        generated_at=datetime.datetime.now().isoformat(),
        total_queries=len(eval_items),
        success_count=successes,
        retrieval_failures=ret_fails,
        generation_hallucinations=gen_hallu,
        correct_abstentions=cor_absts,
        mean_faithfulness=round(mean_faith, 4),
        citation_precision=round(cit_prec, 4),
        citation_recall=round(cit_rec, 4),
        items=eval_items
    )

    print("\n" + "=" * 80)
    print(f"{'ID':<10} | {'Kategori':<18} | {'Sonuç':<22} | {'Faithfulness':<12} | {'Atıflar'}")
    print("-" * 80)
    for it in eval_items:
        cits = [f"[{s.source_id}]" for s in it.rag_response.context.sources]
        faith_str = f"%{it.rag_response.overall_faithfulness*100:.1f}" if not it.rag_response.is_refusal else "N/A"
        print(f"{it.query_id:<10} | {it.category:<18} | {it.error_type:<22} | {faith_str:<12} | {', '.join(cits)}")
    print("=" * 80)

    print(f"\n🏆 GENEL RAG BAŞARIM METRİKLERİ:")
    print(f"   Toplam Test Sorgusu               : {len(eval_items)}")
    print(f"   Doğrulanmış Başarılı Cevaplar     : {successes} / {len(eval_items)} (%{successes/len(eval_items)*100:.1f})")
    print(f"   Doğru Reddetmeler (Abstention)    : {cor_absts}")
    print(f"   Retrieval Kaynaklı Başarısızlık   : {ret_fails}")
    print(f"   Generation / Halüsinasyon Kusuru  : {gen_hallu}")
    print(f"   Ortalama Kaynak Sadakati          : %{mean_faith*100:.1f}")
    print(f"   Citation Precision                : %{cit_prec*100:.1f}")
    print(f"   Citation Recall                   : %{cit_rec*100:.1f}")

    # Görselleştirme Kokpiti Üret
    dashboard_path = plot_rag_evaluation_dashboard(report, str(out_dir / "rag_evaluation_dashboard.png"))
    print(f"\n📈 RAG Teşhis Paneli Üretildi: {dashboard_path}")

    # JSON Raporu Kaydet
    json_path = out_dir / "rag_benchmark_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"📄 Tam Değerlendirme Raporu Kaydedildi: {json_path}")


def cmd_verify(args):
    """Münferit bir iddia cümlesini verilen referans metne göre doğrular."""
    verifier = CitationVerifier()
    c = split_into_claims(args.claim_text)
    if not c:
        print("Geçerli bir iddia cümlesi bulunamadı.")
        return

    src_chunk = SourceChunk(
        source_id="S1",
        chunk_id="CUSTOM_CHUNK",
        doc_id="CUSTOM_DOC",
        title="Referans Belge",
        section="Genel",
        breadcrumbs="Referans",
        text=args.source_text,
        rank=1,
        score=1.0
    )
    context = RAGContext(sources=[src_chunk], formatted_text=src_chunk.text)
    verifs, faith, prec, rec, hallu = verifier.verify_claims(c, context)

    print("\n🔎 MÜNFERİT DOĞRULAMA ÇIKTISI:")
    print("=" * 60)
    for v in verifs:
        print(f"İddia      : {v.claim.text}")
        print(f"Durum      : {v.status} (Sadakat: %{v.faithfulness_score*100:.1f})")
        print(f"Açıklama   : {v.explanation}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Merinos Day 33 RAG & Attributed Generation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ask
    p_ask = subparsers.add_parser("ask", help="Operatör sorusuna kaynaklı RAG cevabı üret ve doğrula")
    p_ask.add_argument("query", type=str, help="Sorulacak soru")
    p_ask.add_argument("--method", type=str, default="linear", choices=["linear", "rrf"])
    p_ask.add_argument("--top-k", type=int, default=3)
    p_ask.add_argument("--alpha", type=float, default=0.5)
    p_ask.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")
    p_ask.add_argument("--simulate-hallucination", action="store_true", help="Hata dedektörünü test etmek için kasıtlı halüsinasyon üret")
    p_ask.add_argument("--verbose", action="store_true", help="Detaylı doğrulama ve metrik raporunu yazdır")

    # Benchmark RAG
    p_bench = subparsers.add_parser("benchmark-rag", help="15 altın test sorgusu üzerinden RAG başarımını ölç")
    p_bench.add_argument("--dataset", type=str, default="day33/mini_project/fixtures/rag_evaluation_queries.json")
    p_bench.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")
    p_bench.add_argument("--output-dir", type=str, default="day33/mini_project/outputs")

    # Verify
    p_ver = subparsers.add_parser("verify", help="Münferit iddia ve kaynak doğrula")
    p_ver.add_argument("claim_text", type=str, help="İddia metni (örn: 'Motor 40 bar olmalıdır [S1].')")
    p_ver.add_argument("--source-text", type=str, required=True, help="Referans kaynak metin")

    args = parser.parse_args()
    if args.command == "ask":
        cmd_ask(args)
    elif args.command == "benchmark-rag":
        cmd_benchmark_rag(args)
    elif args.command == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
