# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
CLI: Query Transformation, HyDE ve Çoklu Sorgu Genişletmesi Komut Satırı Aracı
"""

import sys
import json
import argparse
import datetime
from pathlib import Path
from typing import List, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day35.mini_project.src.models import (
    TransformedQuery,
    MethodResult,
    QueryTransformBenchmarkItem,
    QueryTransformBenchmarkReport
)
from day35.mini_project.src.query_rewriter import QueryRewriter
from day35.mini_project.src.multi_query_expander import MultiQueryExpander
from day35.mini_project.src.hyde_generator import HyDEGenerator
from day35.mini_project.src.transformed_retriever import TransformedRetriever
from day35.mini_project.src.visualizer import plot_transformation_dashboard


def init_transformed_retriever(docs_dir: str = "day31/mini_project/fixtures/documents") -> TransformedRetriever:
    """KnowledgeManager, HybridRetriever ve TransformedRetriever başlatır."""
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    return TransformedRetriever(
        hybrid_retriever=hybrid,
        chunk_lookup=chunk_lookup,
        rewriter=QueryRewriter(),
        expander=MultiQueryExpander(),
        hyde=HyDEGenerator(),
        rrf_k=60
    )


def cmd_transform(args):
    """Operatör sorgusunu tüm dönüşüm yöntemleriyle gösterir."""
    retriever = init_transformed_retriever(args.docs_dir)
    tq = retriever.transform_query(args.query)

    print("GÜRÜLTÜLÜ OPERATÖR SORGUSU:")
    print(tq.raw_query)
    print()
    print("YENİDEN YAZILMIŞ RESMİ SORGU:")
    print(tq.rewritten_query)
    print()
    print("ÇOKLU PERSPEKTİF ALT SORGULARI:")
    for idx, sq in enumerate(tq.sub_queries, start=1):
        print(f"{idx}. {sq}")
    print()
    print("HYDE HİPOTETİK FABRİKA SOP PARAGRAFI:")
    print(tq.hypothetical_doc)



def cmd_search_hyde(args):
    """HyDE varsayımsal dokümanı ile doküman uzayında arama yapar."""
    retriever = init_transformed_retriever(args.docs_dir)
    print(f"\n🔍 Ham Sorgu: '{args.query}'")
    tq = retriever.transform_query(args.query)
    print(f"📄 Üretilen HyDE Metni (İlk 120 Karakter): {tq.hypothetical_doc[:120]}...\n")

    res = retriever.search_hyde(args.query, top_k=args.top_k)

    print("=" * 80)
    print(f"🏆 HYDE İLE GETİRİLEN EN İYİ {len(res.retrieved_chunk_ids)} PARÇA (Süre: {res.latency_ms} ms):")
    print("-" * 80)
    for idx, cid in enumerate(res.retrieved_chunk_ids, start=1):
        c = retriever.chunk_lookup.get(cid)
        source = c.source if c else "Bilinmiyor"
        section = c.section if c else "Genel"
        preview = c.text[:100] if c else ""
        print(f"[{idx}] ID: {cid} | {source} > {section}")
        print(f"    Özet: {preview}...")
        print("-" * 80)


def cmd_benchmark(args):
    """15 gürültülü sorgu ile tüm dönüşüm yöntemlerini kıyaslar."""
    retriever = init_transformed_retriever(args.docs_dir)
    queries_path = Path(args.queries)

    with open(queries_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    print(f"\n🚀 {len(queries_data)} adet gürültülü operatör sorgusu ile Query Transformation benchmark başlatılıyor...")

    eval_items: List[QueryTransformBenchmarkItem] = []
    hits = {"RAW": 0, "REWRITE": 0, "MULTI_QUERY": 0, "HYDE": 0, "RRF_FUSED": 0}
    rr_sums = {"RAW": 0.0, "REWRITE": 0.0, "MULTI_QUERY": 0.0, "HYDE": 0.0, "RRF_FUSED": 0.0}
    latencies = {"RAW": [], "RRF_FUSED": []}
    valid_count = 0

    print("\n" + "=" * 105)
    print(f"{'ID':<10} | {'Gürültülü Sorgu':<30} | {'Raw':<5} | {'Rewr':<5} | {'Multi':<5} | {'HyDE':<5} | {'Fused':<5} | {'En İyi Yöntem'}")
    print("-" * 105)

    for q in queries_data:
        qid = q["id"]
        qtext = q["noisy_query"]
        cat = q["category"]
        target = q.get("target_chunk_id")

        m_raw = retriever.search_raw(qtext, top_k=5)
        m_rewrite = retriever.search_rewritten(qtext, top_k=5)
        m_multi = retriever.search_multi_query(qtext, top_k=5)
        m_hyde = retriever.search_hyde(qtext, top_k=5)
        m_fused = retriever.search_fused(qtext, top_k=5)

        ranks = {
            "RAW": next((idx for idx, cid in enumerate(m_raw.retrieved_chunk_ids, 1) if cid == target), None),
            "REWRITE": next((idx for idx, cid in enumerate(m_rewrite.retrieved_chunk_ids, 1) if cid == target), None),
            "MULTI_QUERY": next((idx for idx, cid in enumerate(m_multi.retrieved_chunk_ids, 1) if cid == target), None),
            "HYDE": next((idx for idx, cid in enumerate(m_hyde.retrieved_chunk_ids, 1) if cid == target), None),
            "RRF_FUSED": next((idx for idx, cid in enumerate(m_fused.retrieved_chunk_ids, 1) if cid == target), None)
        }

        latencies["RAW"].append(m_raw.latency_ms)
        latencies["RRF_FUSED"].append(m_fused.latency_ms)

        if target is not None:
            valid_count += 1
            for m_key in hits:
                r = ranks[m_key]
                if r == 1:
                    hits[m_key] += 1
                if r is not None:
                    rr_sums[m_key] += (1.0 / r)

        best_m = "RAW"
        best_r = ranks["RAW"] or 99
        for m_key, r in ranks.items():
            if r is not None and r < best_r:
                best_r = r
                best_m = m_key

        rank_improved = bool(ranks["RRF_FUSED"] and ranks["RAW"] and ranks["RRF_FUSED"] < ranks["RAW"])

        raw_s = str(ranks["RAW"]) if ranks["RAW"] else "X"
        rewr_s = str(ranks["REWRITE"]) if ranks["REWRITE"] else "X"
        multi_s = str(ranks["MULTI_QUERY"]) if ranks["MULTI_QUERY"] else "X"
        hyde_s = str(ranks["HYDE"]) if ranks["HYDE"] else "X"
        fused_s = str(ranks["RRF_FUSED"]) if ranks["RRF_FUSED"] else "X"

        print(f"{qid:<10} | {qtext[:28]:<30} | {raw_s:<5} | {rewr_s:<5} | {multi_s:<5} | {hyde_s:<5} | {fused_s:<5} | {best_m}")

        eval_items.append(
            QueryTransformBenchmarkItem(
                query_id=qid,
                noisy_query=qtext,
                category=cat,
                target_chunk_id=target,
                raw_rank=ranks["RAW"],
                rewrite_rank=ranks["REWRITE"],
                multi_query_rank=ranks["MULTI_QUERY"],
                hyde_rank=ranks["HYDE"],
                fused_rank=ranks["RRF_FUSED"],
                rank_improved=rank_improved,
                best_method=best_m
            )
        )

    print("=" * 105)

    raw_h1 = round(hits["RAW"] / valid_count, 4) if valid_count else 0.0
    rewr_h1 = round(hits["REWRITE"] / valid_count, 4) if valid_count else 0.0
    multi_h1 = round(hits["MULTI_QUERY"] / valid_count, 4) if valid_count else 0.0
    hyde_h1 = round(hits["HYDE"] / valid_count, 4) if valid_count else 0.0
    fused_h1 = round(hits["RRF_FUSED"] / valid_count, 4) if valid_count else 0.0

    raw_mrr = round(rr_sums["RAW"] / valid_count, 4) if valid_count else 0.0
    rewr_mrr = round(rr_sums["REWRITE"] / valid_count, 4) if valid_count else 0.0
    multi_mrr = round(rr_sums["MULTI_QUERY"] / valid_count, 4) if valid_count else 0.0
    hyde_mrr = round(rr_sums["HYDE"] / valid_count, 4) if valid_count else 0.0
    fused_mrr = round(rr_sums["RRF_FUSED"] / valid_count, 4) if valid_count else 0.0

    mrr_gain_hyde = round(hyde_mrr - raw_mrr, 4)
    mrr_gain_fused = round(fused_mrr - raw_mrr, 4)

    avg_raw_lat = round(sum(latencies["RAW"]) / len(latencies["RAW"]), 2)
    avg_fused_lat = round(sum(latencies["RRF_FUSED"]) / len(latencies["RRF_FUSED"]), 2)

    report = QueryTransformBenchmarkReport(
        timestamp=datetime.datetime.now().isoformat(),
        total_queries=len(queries_data),
        valid_domain_queries=valid_count,
        raw_hit1_rate=raw_h1,
        rewrite_hit1_rate=rewr_h1,
        multi_query_hit1_rate=multi_h1,
        hyde_hit1_rate=hyde_h1,
        fused_hit1_rate=fused_h1,
        raw_mrr=raw_mrr,
        rewrite_mrr=rewr_mrr,
        multi_query_mrr=multi_mrr,
        hyde_mrr=hyde_mrr,
        fused_mrr=fused_mrr,
        mrr_gain_hyde=mrr_gain_hyde,
        mrr_gain_fused=mrr_gain_fused,
        avg_raw_latency_ms=avg_raw_lat,
        avg_fused_latency_ms=avg_fused_lat,
        items=eval_items
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "query_transform_benchmark_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    img_path = out_dir / "query_transformation_dashboard.png"
    plot_transformation_dashboard(report, output_path=str(img_path))

    print("\n🏆 GÜRLÜTÜLÜ SORGU DÖNÜŞÜM KARŞILAŞTIRMA RAPORU:")
    print(f"   Toplam Sorgu          : {report.total_queries} ({report.valid_domain_queries} geçerli)")
    print(f"   Ham (Noisy) Hit@1     : %{report.raw_hit1_rate*100:.1f} | MRR: {report.raw_mrr:.4f}")
    print(f"   Rewriting Hit@1       : %{report.rewrite_hit1_rate*100:.1f} | MRR: {report.rewrite_mrr:.4f}")
    print(f"   Multi-Query Hit@1     : %{report.multi_query_hit1_rate*100:.1f} | MRR: {report.multi_query_mrr:.4f}")
    print(f"   HyDE Hit@1            : %{report.hyde_hit1_rate*100:.1f} | MRR: {report.hyde_mrr:.4f}")
    print(f"   RRF Fused Hit@1       : %{report.fused_hit1_rate*100:.1f} | MRR: {report.fused_mrr:.4f}")
    print(f"   HyDE MRR Kazancı      : {('+' if report.mrr_gain_hyde >= 0 else '')}{report.mrr_gain_hyde:.4f}")
    print(f"   Birleşik (Fused) Kazanç: {('+' if report.mrr_gain_fused >= 0 else '')}{report.mrr_gain_fused:.4f}")
    print(f"\n📊 Teşhis Paneli Grafiği: {img_path}")
    print(f"📄 Tam Değerlendirme JSON: {json_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos Query Transformation & HyDE CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # transform
    p_t = subparsers.add_parser("transform", help="Operatör sorgusunu tüm teknik temsillere dönüştürür")
    p_t.add_argument("--query", type=str, required=True, help="Operatörün yazdığı soru")
    p_t.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")

    # search-hyde
    p_h = subparsers.add_parser("search-hyde", help="HyDE varsayımsal dokümanı ile arama yapar")
    p_h.add_argument("--query", type=str, required=True, help="Operatörün yazdığı soru")
    p_h.add_argument("--top-k", type=int, default=5, help="Getirilecek parça sayısı")
    p_h.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")

    # benchmark-transform
    p_b = subparsers.add_parser("benchmark-transform", help="15 gürültülü sorgu ile tüm dönüşüm yöntemlerini kıyaslar")
    p_b.add_argument("--queries", type=str, default="day35/mini_project/fixtures/noisy_operator_queries.json", help="Test sorgu dosyası")
    p_b.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")
    p_b.add_argument("--output-dir", type=str, default="day35/mini_project/outputs", help="Çıktı dizini")

    args = parser.parse_args()
    if args.command == "transform":
        cmd_transform(args)
    elif args.command == "search-hyde":
        cmd_search_hyde(args)
    elif args.command == "benchmark-transform":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()
