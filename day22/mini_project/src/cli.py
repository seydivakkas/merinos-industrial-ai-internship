"""Command Line Interface (CLI) for Merinos Sparse Retrieval Engine (TF-IDF & BM25)."""

import argparse
import json
from pathlib import Path
import sys
from typing import List

# Windows konsol UTF-8 kodlama koruması
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day22.mini_project.src.models import RawDocument, CorpusStats
from day22.mini_project.src.tokenizer import MerinosTextTokenizer
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.tfidf_engine import TFIDFRetrievalEngine
from day22.mini_project.src.bm25_engine import OkapiBM25Engine
from day22.mini_project.src.evaluator import RetrievalEvaluator
from day22.mini_project.src.visualizer import SparseRetrievalVisualizer


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "retrieval_config.json"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_tokenizer(cfg: dict) -> MerinosTextTokenizer:
    tok_cfg = cfg.get("tokenizer", {})
    stopwords = set(tok_cfg.get("stopwords", []))
    return MerinosTextTokenizer(
        stopwords=stopwords,
        min_token_len=tok_cfg.get("min_token_len", 2),
        lowercase=tok_cfg.get("lowercase", true_bool := True),
        remove_punct=tok_cfg.get("remove_punct", True),
        use_bigrams=tok_cfg.get("use_bigrams", False)
    )


def load_corpus(corpus_path: Path) -> List[RawDocument]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return [RawDocument(**item) for item in items]


def cmd_build_index(args):
    """Builds and serializes inverted index from technical corpus matching Sekil 43."""
    cfg = load_config()
    corpus_p = Path(cfg.get("corpus_path", "day22/mini_project/fixtures/merinos_technical_corpus.json"))
    out_idx_p = Path(cfg.get("index_output_path", "day22/mini_project/outputs/inverted_index.json"))

    print("İndeks oluşturuluyor...")
    documents = load_corpus(corpus_p)
    tokenizer = get_tokenizer(cfg)

    index = InvertedIndex(tokenizer).build(documents)
    index.save_index(out_idx_p)

    stats = index.get_stats()
    print(f"Toplam Doküman Sayısı : {stats.total_documents}")
    print(f"Tekil Kelime Dağarcığı : {stats.vocabulary_size}")
    print(f"Toplam Kelime/Token   : {stats.total_tokens}")
    print(f"Ortalama Doküman Boyu : {stats.avg_doc_len:.2f} token")
    print("✓ Ters indeks başarıyla oluşturuldu.")


def setup_engines(cfg: dict):
    corpus_p = Path(cfg.get("corpus_path", "day22/mini_project/fixtures/merinos_technical_corpus.json"))
    documents = load_corpus(corpus_p)
    tokenizer = get_tokenizer(cfg)
    index = InvertedIndex(tokenizer).build(documents)

    bm25_cfg = cfg.get("bm25", {})
    bm25_engine = OkapiBM25Engine(
        index=index,
        tokenizer=tokenizer,
        k1=bm25_cfg.get("k1", 1.5),
        b=bm25_cfg.get("b", 0.75),
        epsilon=bm25_cfg.get("epsilon", 0.25)
    )

    tfidf_cfg = cfg.get("tfidf", {})
    tfidf_engine = TFIDFRetrievalEngine(
        index=index,
        tokenizer=tokenizer,
        sublinear_tf=tfidf_cfg.get("sublinear_tf", True)
    )

    return index, bm25_engine, tfidf_engine


def print_search_results(results, query: str, engine_name: str):
    print("\n" + "=" * 80)
    print(f"  MERİNOS SEYREK ARAMA SONUÇLARI: {engine_name.upper()}  ")
    print(f"  Sorgu: '{query}'")
    print("=" * 80)
    if not results:
        print("  [!] Eşleşen teknik doküman bulunamadı.")
        print("=" * 80 + "\n")
        return

    for item in results:
        print(f"[{item.rank}] Skor: {item.score:.4f} | Kimlik: {item.doc_id} | Kategori: {item.category}")
        print(f"    Başlık: {item.title}")
        print(f"    Özet  : {item.snippet}")
        print("-" * 80)
    print("=" * 80 + "\n")


def cmd_search_bm25(args):
    """Executes query with Okapi BM25 ranking."""
    cfg = load_config()
    _, bm25_engine, _ = setup_engines(cfg)
    top_k = args.top_k or cfg.get("search", {}).get("default_top_k", 5)
    results = bm25_engine.search(args.query, top_k=top_k)
    print_search_results(results, args.query, "Okapi BM25")


def cmd_search_tfidf(args):
    """Executes query with TF-IDF cosine similarity."""
    cfg = load_config()
    _, _, tfidf_engine = setup_engines(cfg)
    top_k = args.top_k or cfg.get("search", {}).get("default_top_k", 5)
    results = tfidf_engine.search(args.query, top_k=top_k)
    print_search_results(results, args.query, "TF-IDF Cosine")


def cmd_benchmark(args):
    """Benchmarks BM25 vs TF-IDF on standard test queries."""
    cfg = load_config()
    index, bm25_engine, tfidf_engine = setup_engines(cfg)
    stats = index.get_stats()

    evaluator = RetrievalEvaluator()
    report = evaluator.compare_engines(bm25_engine, tfidf_engine, stats)

    print("\n" + "=" * 92)
    print("         MERİNOS SEYREK GETİRME (SPARSE RETRIEVAL) MASTER BENCHMARK RAPORU         ")
    print("=" * 92)
    print(f"{'Metrik':<24} | {'Okapi BM25':<20} | {'TF-IDF (Cosine)':<20} | {'Üstünlük':<20}")
    print("-" * 92)
    print(f"{'Precision@1':<24} | %{report.bm25_metrics.precision_at_1*100:<19.1f} | %{report.tfidf_metrics.precision_at_1*100:<19.1f} | {'BM25' if report.bm25_metrics.precision_at_1 >= report.tfidf_metrics.precision_at_1 else 'TF-IDF':<20}")
    print(f"{'Precision@3':<24} | %{report.bm25_metrics.precision_at_3*100:<19.1f} | %{report.tfidf_metrics.precision_at_3*100:<19.1f} | {'BM25' if report.bm25_metrics.precision_at_3 >= report.tfidf_metrics.precision_at_3 else 'TF-IDF':<20}")
    print(f"{'Precision@5':<24} | %{report.bm25_metrics.precision_at_5*100:<19.1f} | %{report.tfidf_metrics.precision_at_5*100:<19.1f} | {'BM25' if report.bm25_metrics.precision_at_5 >= report.tfidf_metrics.precision_at_5 else 'TF-IDF':<20}")
    print(f"{'Recall@5':<24} | %{report.bm25_metrics.recall_at_5*100:<19.1f} | %{report.tfidf_metrics.recall_at_5*100:<19.1f} | {'BM25' if report.bm25_metrics.recall_at_5 >= report.tfidf_metrics.recall_at_5 else 'TF-IDF':<20}")
    print(f"{'Mean Reciprocal Rank':<24} | {report.bm25_metrics.mrr:<20.4f} | {report.tfidf_metrics.mrr:<20.4f} | {'BM25' if report.bm25_metrics.mrr >= report.tfidf_metrics.mrr else 'TF-IDF':<20}")
    print(f"{'NDCG@5':<24} | {report.bm25_metrics.ndcg_at_5:<20.4f} | {report.tfidf_metrics.ndcg_at_5:<20.4f} | {'BM25' if report.bm25_metrics.ndcg_at_5 >= report.tfidf_metrics.ndcg_at_5 else 'TF-IDF':<20}")
    print(f"{'Ortalama Gecikme':<24} | {report.bm25_metrics.avg_latency_ms:<17.3f} ms | {report.tfidf_metrics.avg_latency_ms:<17.3f} ms | {'BM25' if report.bm25_metrics.avg_latency_ms <= report.tfidf_metrics.avg_latency_ms else 'TF-IDF':<20}")
    print(f"{'Throughput (QPS)':<24} | {report.bm25_metrics.queries_per_second:<16.1f} QPS | {report.tfidf_metrics.queries_per_second:<16.1f} QPS | {'BM25' if report.bm25_metrics.queries_per_second >= report.tfidf_metrics.queries_per_second else 'TF-IDF':<20}")
    print("=" * 92)
    print(f"[+] Şampiyon Algoritma : {report.champion_algorithm}")
    print(f"[*] Kıyaslama Özeti    : {report.summary}\n")

    out_p = Path(cfg.get("benchmark_report_path", "day22/mini_project/outputs/sparse_retrieval_benchmark.json"))
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"[+] JSON benchmark raporu kaydedildi: {out_p}\n")


def cmd_plot(args):
    """Generates 2x2 diagnostic figure analyzing retrieval metrics, saturation and normalization."""
    cfg = load_config()
    index, bm25_engine, tfidf_engine = setup_engines(cfg)
    stats = index.get_stats()

    evaluator = RetrievalEvaluator()
    report = evaluator.compare_engines(bm25_engine, tfidf_engine, stats)

    vis = SparseRetrievalVisualizer()
    out_png = cfg.get("diagnostic_panel_path", "day22/mini_project/outputs/sparse_retrieval_panel.png")
    generated_p = vis.plot_diagnostic_panel(report, out_png)
    print(f"[+] 2x2 Leksikal Arama Master Paneli Üretildi: {generated_p}")


def main():
    parser = argparse.ArgumentParser(
        description="Merinos Seyrek Getirme Motoru CLI — TF-IDF ve Okapi BM25 İndeksleme ve Arama"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. build-index
    subparsers.add_parser("build-index", help="Teknik doküman külliyatını okuyup ters indeksi oluşturur")

    # 2. search-bm25
    p_bm25 = subparsers.add_parser("search-bm25", help="Okapi BM25 algoritmasıyla Top-K leksikal arama yapar")
    p_bm25.add_argument("--query", "-q", type=str, required=True, help="Arama sorgusu metni")
    p_bm25.add_argument("--top-k", "-k", type=int, default=5, help="Getirilecek doküman sayısı (varsayılan: 5)")

    # 3. search-tfidf
    p_tfidf = subparsers.add_parser("search-tfidf", help="TF-IDF kosinüs benzerliği ile Top-K arama yapar")
    p_tfidf.add_argument("--query", "-q", type=str, required=True, help="Arama sorgusu metni")
    p_tfidf.add_argument("--top-k", "-k", type=int, default=5, help="Getirilecek doküman sayısı (varsayılan: 5)")

    # 4. benchmark
    subparsers.add_parser("benchmark", help="Standart sorgu kümesinde Precision, Recall, MRR ve NDCG ölçer")

    # 5. plot
    subparsers.add_parser("plot", help="2x2 Leksikal arama ve duyarlılık teşhis panelini (PNG) üretir")

    args = parser.parse_args()

    if args.command == "build-index":
        cmd_build_index(args)
    elif args.command == "search-bm25":
        cmd_search_bm25(args)
    elif args.command == "search-tfidf":
        cmd_search_tfidf(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "plot":
        cmd_plot(args)


if __name__ == "__main__":
    main()
