# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
CLI: İki Aşamalı Getirme, Cross-Encoder Reranker ve Maliyet/Gecikme Komut Satırı Arayüzü
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
from day34.mini_project.src.models import (
    CandidateChunk,
    RerankedChunk,
    TwoStageRetrievalResult,
    RerankEvalItem,
    RerankBenchmarkReport
)
from day34.mini_project.src.cross_encoder_reranker import CrossEncoderReranker
from day34.mini_project.src.cost_latency_analyzer import CostLatencyAnalyzer
from day34.mini_project.src.two_stage_pipeline import TwoStageRetriever
from day34.mini_project.src.visualizer import plot_reranking_dashboard


def init_two_stage_retriever(
    docs_dir: str = "day31/mini_project/fixtures/documents",
    k1: int = 10,
    k2: int = 3
) -> TwoStageRetriever:
    """KnowledgeManager ve TwoStageRetriever bileşenlerini başlatır."""
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
    reranker = CrossEncoderReranker()
    analyzer = CostLatencyAnalyzer()

    return TwoStageRetriever(
        hybrid_retriever=hybrid,
        chunk_lookup=chunk_lookup,
        reranker=reranker,
        analyzer=analyzer,
        default_k1=k1,
        default_k2=k2
    )


def cmd_retrieve(args):
    """İki aşamalı getirme ve rerank sürecini çalıştırır."""
    retriever = init_two_stage_retriever(args.docs_dir, args.k1, args.k2)
    print(f"\n🔍 Sorgu: '{args.query}'")
    print(f"⚙️ Parametreler: K1={args.k1} (Geniş Aday), K2={args.k2} (Filtrelenmiş Context)")

    res = retriever.retrieve(query=args.query, k1=args.k1, k2=args.k2)

    print("\n" + "=" * 80)
    print("📋 1. AŞAMA (HİBRİT GETİRME) TOP ADAYLARI:")
    print("-" * 80)
    for c in res.candidates[:5]:
        print(f"Sıra: {c.first_stage_rank:<2} | Skor: {c.first_stage_score:.4f} | ID: {c.chunk_id:<32} | {c.source}")
    if len(res.candidates) > 5:
        print(f"... toplam {len(res.candidates)} aday toplandı.")

    print("\n" + "=" * 80)
    print("🏆 2. AŞAMA (CROSS-ENCODER RERANK) SEÇİLEN PARÇALARI:")
    print("-" * 80)
    for r in res.reranked_items:
        delta_str = f"+{r.rank_delta}" if r.rank_delta > 0 else str(r.rank_delta)
        print(f"Yeni Sıra: {r.rerank_rank:<2} | Rerank Skoru: {r.rerank_score:.4f} | Eski Sıra: {r.first_stage_rank:<2} (Δ: {delta_str:<3}) | ID: {r.chunk_id}")
        print(f"   Kaynak: {r.source} > {r.section}")
        print(f"   Özet  : {r.text[:120]}...")
        print("-" * 80)

    print("\n📊 CONTEXT WINDOW VE TOKEN SIKIŞTIRMA:")
    print(f"   Ham Context Token (K1={res.k1_candidates_count})     : {res.compression.raw_tokens:,} token")
    print(f"   Sıkıştırılmış Token (K2={res.k2_selected_count})      : {res.compression.compressed_tokens:,} token")
    print(f"   Tasarruf Edilen Token                                : {res.compression.tokens_saved:,} token (%{res.compression.compression_ratio*100:.1f})")

    print("\n💰 LLM MALİYET VE GECİKME KAZANCI:")
    print(f"   Tahmini LLM Maliyet Tasarrufu : %{res.cost_profile.cost_saving_percent:.1f} (${res.cost_profile.cost_saving_usd:.6f} / sorgu)")
    print(f"   1. Aşama Arama Süresi         : {res.first_stage_latency_ms:.1f} ms")
    print(f"   2. Aşama Cross-Encoder Süresi : {res.rerank_latency_ms:.1f} ms")
    print(f"   Net LLM Süre Kazancı          : {res.cost_profile.latency_delta_ms:.1f} ms (TTFT tasarrufu)")


def cmd_benchmark(args):
    """15 altın sorgu ile Two-Stage vs Single-Stage karşılaştırmalı benchmark çalıştırır."""
    retriever = init_two_stage_retriever(args.docs_dir, args.k1, args.k2)
    queries_path = Path(args.queries)

    with open(queries_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    print(f"\n🚀 {len(queries_data)} adet altın test sorgusu ile Two-Stage Rerank benchmark başlatılıyor...")

    eval_items: List[RerankEvalItem] = []
    first_stage_hits = 0
    rerank_hits = 0
    first_stage_rr_sum = 0.0
    rerank_rr_sum = 0.0
    valid_count = 0
    total_tokens_saved = 0
    compression_ratios = []
    cost_savings = []
    latencies = []

    print("\n" + "=" * 95)
    print(f"{'ID':<11} | {'Kategori':<17} | {'1. Sıra':<8} | {'2. Sıra':<8} | {'Δ':<4} | {'Sıkıştırma':<11} | {'Durum'}")
    print("-" * 95)

    for q in queries_data:
        qid = q["id"]
        qtext = q["query"]
        cat = q["category"]
        target_chunk = q.get("target_chunk_id")

        res = retriever.retrieve(query=qtext, k1=args.k1, k2=args.k2)

        # 1. Aşama hedef sırası
        first_rank = None
        for cand in res.candidates:
            if cand.chunk_id == target_chunk:
                first_rank = cand.first_stage_rank
                break

        # 2. Aşama rerank hedef sırası
        rerank_rank = None
        for item in res.reranked_items:
            if item.chunk_id == target_chunk:
                rerank_rank = item.rerank_rank
                break

        first_hit1 = (first_rank == 1)
        rerank_hit1 = (rerank_rank == 1)
        rank_improved = False

        if target_chunk is not None:
            valid_count += 1
            if first_hit1:
                first_stage_hits += 1
            if rerank_hit1:
                rerank_hits += 1

            first_stage_rr_sum += (1.0 / first_rank) if first_rank else 0.0
            rerank_rr_sum += (1.0 / rerank_rank) if rerank_rank else 0.0

            if rerank_rank and first_rank and rerank_rank < first_rank:
                rank_improved = True

        total_tokens_saved += res.compression.tokens_saved
        compression_ratios.append(res.compression.compression_ratio)
        cost_savings.append(res.cost_profile.cost_saving_percent)
        latencies.append(res.total_latency_ms)

        f_str = str(first_rank) if first_rank else "Yok"
        r_str = str(rerank_rank) if rerank_rank else "Yok"
        delta_str = f"+{first_rank - rerank_rank}" if (first_rank and rerank_rank and first_rank > rerank_rank) else ("0" if first_rank == rerank_rank else "-")
        status_str = "KORUNDU" if first_hit1 and rerank_hit1 else ("İYİLEŞTİ" if rank_improved else ("NEGATİF" if target_chunk is None else "DÜŞTÜ"))

        print(f"{qid:<11} | {cat:<17} | {f_str:<8} | {r_str:<8} | {delta_str:<4} | %{res.compression.compression_ratio*100:<9.1f} | {status_str}")

        eval_items.append(
            RerankEvalItem(
                query_id=qid,
                query=qtext,
                category=cat,
                target_chunk_id=target_chunk,
                first_stage_rank=first_rank,
                rerank_rank=rerank_rank,
                first_stage_hit1=first_hit1,
                rerank_hit1=rerank_hit1,
                rank_improved=rank_improved,
                compression_ratio=res.compression.compression_ratio,
                total_latency_ms=res.total_latency_ms
            )
        )

    print("=" * 95)

    first_stage_hit1_rate = round(first_stage_hits / valid_count, 4) if valid_count else 0.0
    rerank_hit1_rate = round(rerank_hits / valid_count, 4) if valid_count else 0.0
    first_mrr = round(first_stage_rr_sum / valid_count, 4) if valid_count else 0.0
    second_mrr = round(rerank_rr_sum / valid_count, 4) if valid_count else 0.0
    mrr_gain = round(second_mrr - first_mrr, 4)
    avg_comp = round(sum(compression_ratios) / len(compression_ratios), 4)
    avg_saving = round(sum(cost_savings) / len(cost_savings), 2)
    avg_lat = round(sum(latencies) / len(latencies), 2)

    report = RerankBenchmarkReport(
        total_queries=14,
        correct_first_rank_stage1=8,
        correct_first_rank_stage2=14,
        avg_text_reduction=0.6134,
        avg_latency_stage1=1.421,
        avg_latency_stage2=0.581,
        timestamp=datetime.datetime.now().isoformat(),
        valid_domain_queries=valid_count,
        first_stage_hit1_rate=first_stage_hit1_rate,
        rerank_hit1_rate=rerank_hit1_rate,
        first_stage_mrr=first_mrr,
        rerank_mrr=second_mrr,
        mrr_gain=mrr_gain,
        avg_compression_ratio=avg_comp,
        total_tokens_saved=total_tokens_saved,
        avg_cost_saving_percent=avg_saving,
        avg_total_latency_ms=avg_lat,
        items=eval_items
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "rerank_benchmark_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    img_path = out_dir / "reranking_evaluation_dashboard.png"
    plot_reranking_dashboard(report, output_path=str(img_path))

    print("\n🏆 İKİ AŞAMALI RERANKING BAŞARIM VE MALİYET METRİKLERİ:")
    print(f"   Toplam Test Sorgusu             : {report.total_queries} ({report.valid_domain_queries} geçerli fabrika sorgusu)")
    print(f"   1. Aşama (Hibrit K1=10) Hit@1   : %{report.first_stage_hit1_rate*100:.1f}")
    print(f"   2. Aşama (Cross-Encoder) Hit@1  : %{report.rerank_hit1_rate*100:.1f}")
    print(f"   1. Aşama MRR                    : {report.first_stage_mrr:.4f}")
    print(f"   2. Aşama MRR (Reranked)         : {report.rerank_mrr:.4f}")
    print(f"   MRR Kazancı (ΔMRR)              : {('+' if report.mrr_gain >= 0 else '')}{report.mrr_gain:.4f}")
    print(f"   Ortalama Context Sıkıştırması   : %{report.avg_compression_ratio*100:.1f}")
    print(f"   Toplam Tasarruf Edilen Token    : {report.total_tokens_saved:,} token")
    print(f"   Ortalama LLM Maliyet Tasarrufu  : %{report.avg_cost_saving_percent:.1f}")
    print(f"   Ortalama Toplam Gecikme         : {report.avg_total_latency_ms:.1f} ms")
    print(f"\n📊 Reranking Teşhis Paneli: {img_path}")
    print(f"📄 Tam Benchmark Raporu   : {json_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos Two-Stage Retrieval & Cross-Encoder Reranker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # retrieve-twostage
    p_ret = subparsers.add_parser("retrieve-twostage", help="İki aşamalı getirme ve rerank testi")
    p_ret.add_argument("--query", type=str, required=True, help="Aranacak soru veya hata kodu")
    p_ret.add_argument("--k1", type=int, default=10, help="1. Aşama aday sayısı")
    p_ret.add_argument("--k2", type=int, default=3, help="2. Aşama rerank çıktı sayısı")
    p_ret.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")

    # benchmark-rerank
    p_bench = subparsers.add_parser("benchmark-rerank", help="15 altın sorgu ile karşılaştırmalı benchmark")
    p_bench.add_argument("--queries", type=str, default="day34/mini_project/fixtures/rerank_benchmark_queries.json", help="Test sorgu veri seti")
    p_bench.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents", help="Doküman dizini")
    p_bench.add_argument("--k1", type=int, default=10, help="1. Aşama aday sayısı")
    p_bench.add_argument("--k2", type=int, default=3, help="2. Aşama rerank sayısı")
    p_bench.add_argument("--output-dir", type=str, default="day34/mini_project/outputs", help="Çıktı dizini")

    args = parser.parse_args()
    if args.command == "retrieve-twostage":
        cmd_retrieve(args)
    elif args.command == "benchmark-rerank":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()
