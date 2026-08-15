"""
Merinos Industrial AI Internship - Day 23
Dense Retrieval & Re-ranking CLI Interface

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import sys
import argparse
from pathlib import Path
import json

# Windows terminal UTF-8 uyumluluğu
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from day23.mini_project.src.models import RawDocument
from day23.mini_project.src.bi_encoder import BiEncoderDenseRetriever
from day23.mini_project.src.vector_store import QdrantVectorStore
from day23.mini_project.src.cross_encoder_reranker import CrossEncoderReranker
from day23.mini_project.src.pipeline import TwoStageRetrievalPipeline
from day23.mini_project.src.evaluator import DenseRetrievalEvaluator
from day23.mini_project.src.visualizer import plot_dense_retrieval_panel


def load_corpus(corpus_path: str) -> list:
    path = Path(corpus_path)
    if not path.exists():
        # Alternatif yolları kontrol et
        alt_path = Path("day23") / corpus_path
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(f"Külliyat dosyası bulunamadı: {corpus_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [RawDocument(**doc) for doc in data]


def get_default_paths():
    base = Path("day23/mini_project")
    if not base.exists():
        base = Path("mini_project")
    corpus = base / "fixtures" / "merinos_technical_corpus.json"
    output_dir = base / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(corpus), str(output_dir)


def main():
    default_corpus, default_output_dir = get_default_paths()

    parser = argparse.ArgumentParser(
        description="Merinos Halı Sanayi - Day 23: Yoğun Getirme & Cross-Encoder Re-ranking CLI Arayüzü"
    )
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir komutlar")

    # 1. index-vectors
    idx_parser = subparsers.add_parser("index-vectors", help="Külliyatı vektörleştir ve Qdrant koleksiyonuna yükle")
    idx_parser.add_argument("--corpus", default=default_corpus, help="Külliyat JSON dosya yolu")

    # 2. search-dense
    s_parser = subparsers.add_parser("search-dense", help="Bi-Encoder ve Qdrant ile semantik arama yap")
    s_parser.add_argument("--query", required=True, help="Aranacak teknik arıza sorgusu")
    s_parser.add_argument("--top-k", type=int, default=5, help="Döndürülecek ilk K doküman")
    s_parser.add_argument("--category", default=None, help="Kategori filtresi (WEAVING, JACQUARD, YARN, DYEING_FINISHING)")
    s_parser.add_argument("--corpus", default=default_corpus, help="Külliyat JSON dosya yolu")

    # 3. rerank
    r_parser = subparsers.add_parser("rerank", help="Bi-Encoder ilk aşama + Cross-Encoder re-ranking yap")
    r_parser.add_argument("--query", required=True, help="Aranacak teknik arıza sorgusu")
    r_parser.add_argument("--first-stage-top-k", type=int, default=10, help="İlk aşamada getirilecek aday sayısı")
    r_parser.add_argument("--final-top-k", type=int, default=3, help="Yeniden sıralama sonrası ilk K doküman")
    r_parser.add_argument("--category", default=None, help="Kategori filtresi")
    r_parser.add_argument("--corpus", default=default_corpus, help="Külliyat JSON dosya yolu")

    # 4. benchmark
    b_parser = subparsers.add_parser("benchmark", help="15 kurumsal teknik sorgu ile modelleri kıyasla")
    b_parser.add_argument("--corpus", default=default_corpus, help="Külliyat JSON dosya yolu")
    b_parser.add_argument("--output", default=f"{default_output_dir}/dense_retrieval_benchmark.json", help="JSON rapor yolu")
    b_parser.add_argument("--runs", type=int, default=3, help="Gecikme ölçümü için tekrar sayısı")

    # 5. plot
    p_parser = subparsers.add_parser("plot", help="2x2 Master Teşhis Panelini çizdir")
    p_parser.add_argument("--corpus", default=default_corpus, help="Külliyat JSON dosya yolu")
    p_parser.add_argument("--benchmark-file", default=f"{default_output_dir}/dense_retrieval_benchmark.json", help="Benchmark JSON yolu")
    p_parser.add_argument("--output", default=f"{default_output_dir}/dense_retrieval_panel.png", help="PNG çıktı yolu")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "index-vectors":
        print(f"📖 Külliyat yükleniyor: {args.corpus}")
        corpus = load_corpus(args.corpus)
        bi_enc = BiEncoderDenseRetriever()
        qdrant = QdrantVectorStore(in_memory=True)
        pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=CrossEncoderReranker(), vector_store=qdrant)
        print("⚙️ Cümle gömmeleri hesaplanıyor ve Qdrant'a yükleniyor...")
        pipe.index_corpus(corpus)
        print(f"✅ Başarılı! {len(corpus)} doküman Qdrant vektör veritabanına indekslendi (Boyut: 384).")

    elif args.command == "search-dense":
        corpus = load_corpus(args.corpus)
        bi_enc = BiEncoderDenseRetriever()
        qdrant = QdrantVectorStore(in_memory=True)
        pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=CrossEncoderReranker(), vector_store=qdrant)
        pipe.index_corpus(corpus)

        print(f"\n🔎 Sorgu: '{args.query}' (Kategori Filtresi: {args.category})")
        results = pipe.search_first_stage(args.query, top_k=args.top_k, category_filter=args.category, use_qdrant=True)

        print(f"\n🏆 Bi-Encoder / Qdrant İlk {len(results)} Sonuç:")
        for r in results:
            print(f"  [{r.rank}] {r.doc_id} | Skor: {r.score:.4f} | Kategori: {r.category} | {r.title}")
            print(f"      Özet: {r.snippet}\n")

    elif args.command == "rerank":
        corpus = load_corpus(args.corpus)
        bi_enc = BiEncoderDenseRetriever()
        cross_enc = CrossEncoderReranker()
        qdrant = QdrantVectorStore(in_memory=True)
        pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=cross_enc, vector_store=qdrant)
        pipe.index_corpus(corpus)

        print(f"\n🔎 Sorgu: '{args.query}'")
        print(f"⚙️ Aşama 1: Bi-Encoder Top-{args.first_stage_top_k} aday getiriliyor...")
        print(f"⚙️ Aşama 2: Cross-Encoder ile Top-{args.final_top_k} yeniden sıralanıyor...")

        results, bi_time, ce_time = pipe.search_and_rerank(
            query=args.query,
            first_stage_top_k=args.first_stage_top_k,
            final_top_k=args.final_top_k,
            category_filter=args.category,
            use_qdrant=True
        )

        print(f"\n⏱️ Süreler: Bi-Encoder: {bi_time:.2f} ms | Cross-Encoder: {ce_time:.2f} ms | Toplam: {bi_time+ce_time:.2f} ms")
        print(f"\n🎯 Cross-Encoder Re-ranked Sonuçları:")
        for r in results:
            print(f"  [{r.rank}] {r.doc_id} | CE Skoru: {r.cross_encoder_score:.4f} (Bi-Enc: {r.bi_encoder_score:.4f}) | {r.title}")
            print(f"      Özet: {r.snippet}\n")

    elif args.command == "benchmark":
        corpus = load_corpus(args.corpus)
        bi_enc = BiEncoderDenseRetriever()
        cross_enc = CrossEncoderReranker()
        qdrant = QdrantVectorStore(in_memory=True)
        pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=cross_enc, vector_store=qdrant)
        print("⚙️ Dokümanlar vektörleştiriliyor ve Qdrant'a yükleniyor...")
        pipe.index_corpus(corpus)

        print(f"🚀 15 teknik arıza sorgusu üzerinde Benchmark başlatılıyor ({args.runs} tekrar)...")
        evaluator = DenseRetrievalEvaluator(pipeline=pipe, corpus=corpus)
        report = evaluator.run_benchmark(num_runs=args.runs)

        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        print(f"\n✅ Benchmark tamamlandı! Rapor kaydedildi: {out_path}")
        print("\n=== MERİNOS DENSE RETRIEVAL & RE-RANKING KIYASLAMA TABLOSU ===")
        print(f"{'Model':<25} | {'P@1':<8} | {'P@3':<8} | {'Recall@5':<8} | {'MRR':<8} | {'NDCG@5':<8} | {'Gecikme':<10} | {'QPS':<10}")
        print("-" * 95)
        print(f"{'Okapi BM25':<25} | %{report.bm25_metrics.precision_at_1*100:<6.1f} | %{report.bm25_metrics.precision_at_3*100:<6.1f} | %{report.bm25_metrics.recall_at_5*100:<6.1f} | {report.bm25_metrics.mrr:<8.4f} | {report.bm25_metrics.ndcg_at_5:<8.4f} | {report.bm25_latency_ms:<7.2f} ms | {report.bm25_qps:<10.1f}")
        print(f"{'Bi-Encoder (MiniLM)':<25} | %{report.bi_encoder_metrics.precision_at_1*100:<6.1f} | %{report.bi_encoder_metrics.precision_at_3*100:<6.1f} | %{report.bi_encoder_metrics.recall_at_5*100:<6.1f} | {report.bi_encoder_metrics.mrr:<8.4f} | {report.bi_encoder_metrics.ndcg_at_5:<8.4f} | {report.bi_encoder_latency_ms:<7.2f} ms | {report.bi_encoder_qps:<10.1f}")
        print(f"{'Two-Stage Re-ranked':<25} | %{report.reranked_metrics.precision_at_1*100:<6.1f} | %{report.reranked_metrics.precision_at_3*100:<6.1f} | %{report.reranked_metrics.recall_at_5*100:<6.1f} | {report.reranked_metrics.mrr:<8.4f} | {report.reranked_metrics.ndcg_at_5:<8.4f} | {report.reranked_latency_ms:<7.2f} ms | {report.reranked_qps:<10.1f}")

    elif args.command == "plot":
        corpus = load_corpus(args.corpus)
        bench_file = Path(args.benchmark_file)
        if not bench_file.exists():
            print(f"⚠️ Benchmark raporu bulunamadı, otomatik çalıştırılıyor...")
            bi_enc = BiEncoderDenseRetriever()
            cross_enc = CrossEncoderReranker()
            qdrant = QdrantVectorStore(in_memory=True)
            pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=cross_enc, vector_store=qdrant)
            pipe.index_corpus(corpus)
            evaluator = DenseRetrievalEvaluator(pipeline=pipe, corpus=corpus)
            report = evaluator.run_benchmark(num_runs=2)
            bench_file.parent.mkdir(parents=True, exist_ok=True)
            with open(bench_file, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
        else:
            with open(bench_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            from day23.mini_project.src.models import DenseRetrievalBenchmarkReport
            report = DenseRetrievalBenchmarkReport(**report_data)

        bi_enc = BiEncoderDenseRetriever()
        cross_enc = CrossEncoderReranker()
        qdrant = QdrantVectorStore(in_memory=True)
        pipe = TwoStageRetrievalPipeline(bi_encoder=bi_enc, reranker=cross_enc, vector_store=qdrant)
        pipe.index_corpus(corpus)

        print(f"🎨 2x2 Master Teşhis Paneli çizdiriliyor...")
        out_png = plot_dense_retrieval_panel(
            report=report,
            bi_encoder=bi_enc,
            reranker=cross_enc,
            corpus=corpus,
            output_path=args.output
        )
        print(f"✅ Master Teşhis Paneli kaydedildi: {out_png}")


if __name__ == "__main__":
    main()
