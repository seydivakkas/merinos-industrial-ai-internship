"""CLI interface for Day 24 Hybrid Retrieval (BM25 + Qdrant Dense Fusion via RRF).

Merinos Halı Sanayi ve Ticaret A.Ş. - Faz 4: Retrieval & Hibrit Arama
Day 24: Hibrit Arama ve Karşılıklı Sıra Füzyonu (Reciprocal Rank Fusion - RRF)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# UTF-8 stdout configuration for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from day24.mini_project.src.evaluator import HybridRetrievalEvaluator
from day24.mini_project.src.pipeline import ThreeStageHybridPipeline
from day24.mini_project.src.visualizer import plot_hybrid_retrieval_panel


def get_default_corpus_path() -> Path:
    """Returns default path to merinos technical corpus."""
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "fixtures" / "merinos_technical_corpus.json"


def get_default_config_path() -> Path:
    """Returns default path to hybrid configuration file."""
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "configs" / "hybrid_config.json"


def cmd_search_hybrid(args: argparse.Namespace) -> int:
    """Performs hybrid search for a given technical query."""
    corpus_path = Path(args.corpus) if args.corpus else get_default_corpus_path()
    if not corpus_path.exists():
        print(f"HATA: Külliyat dosyası bulunamadı: {corpus_path}", file=sys.stderr)
        return 1

    print(f"\n" + "=" * 80)
    print(f"🔍 MERİNOS HİBRİT ARAMA MOTORU (Day 24 - BM25 + Qdrant Dense)")
    print(f"=" * 80)
    print(f"Sorgu:           {args.query}")
    print(f"Füzyon Modu:     {args.mode.upper()}")
    print(f"Kategori Filtre: {args.category or 'TÜMÜ'}")
    print(f"Top-K Sonuç:     {args.top_k}")
    print(f"Cross-Encoder:   {'AKTİF' if args.rerank else 'PASİF'}")
    if args.mode == "weighted":
        print(f"Alpha (BM25):    {args.alpha:.2f} | 1-Alpha (Dense): {1.0 - args.alpha:.2f}")
    print("-" * 80)

    pipeline = ThreeStageHybridPipeline(
        use_cross_encoder=args.rerank,
        cross_encoder_top_n=max(args.top_k, 10),
        rrf_k=args.rrf_k,
        default_alpha=args.alpha,
    )
    pipeline.index_corpus(corpus_path)

    results = pipeline.search(
        query=args.query,
        mode=args.mode,
        category_filter=args.category,
        top_k=args.top_k,
        rerank=args.rerank,
        alpha=args.alpha,
    )

    if not results:
        print("Uyarı: Arama kriterine uygun sonuç bulunamadı.")
        return 0

    print(f"\n🎯 BULUNAN SONUÇLAR ({len(results)} adet):\n")
    for i, res in enumerate(results, 1):
        if args.rerank:
            print(f"[{i}] {res.doc_id} | Skor: {res.final_score:.4f} (Cross-Encoder) | Ön-Sıra: #{res.pre_rerank_rank}")
        else:
            print(f"[{i}] {res.doc_id} | Skor: {res.fusion_score:.4f} ({res.fusion_mode.upper()}) | BM25: #{res.bm25_rank or '-'}, Dense: #{res.dense_rank or '-'}")
        print(f"    Başlık:   {res.title}")
        print(f"    Kategori: {res.category}")
        print(f"    İçerik:   {res.content[:140]}...")
        print("-" * 80)

    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Runs comprehensive benchmark on 15 corporate queries across 5 models."""
    corpus_path = Path(args.corpus) if args.corpus else get_default_corpus_path()
    output_path = Path(args.output) if args.output else (Path(__file__).resolve().parent.parent / "outputs" / "hybrid_retrieval_benchmark.json")

    evaluator = HybridRetrievalEvaluator(corpus_path=corpus_path)
    evaluator.initialize()

    report = evaluator.evaluate_all(top_k=args.top_k, rrf_k=args.rrf_k, alpha=args.alpha)
    report_dict = evaluator.save_benchmark_report(report, output_path)

    print(f"\n📊 HİBRİT ARAMA BÜYÜK KIYASLAMA TABLOSU (Top-{args.top_k}):")
    print("-" * 85)
    print(f"{'Model':<24} | {'MRR@5':<8} | {'NDCG@5':<8} | {'Hit@1':<8} | {'Hit@3':<8} | {'Hit@5':<8}")
    print("-" * 85)
    for model_name, metrics in report.models.items():
        print(
            f"{model_name:<24} | "
            f"{metrics.mrr_at_5:<8.4f} | "
            f"{metrics.ndcg_at_5:<8.4f} | "
            f"{metrics.hit_rate_at_1 * 100:>5.1f}%% | "
            f"{metrics.hit_rate_at_3 * 100:>5.1f}%% | "
            f"{metrics.hit_rate_at_5 * 100:>5.1f}%%"
        )
    print("-" * 85)
    print(f"✅ Kıyaslama raporu başarıyla kaydedildi: {output_path}\n")
    return 0


def cmd_tune_alpha(args: argparse.Namespace) -> int:
    """Performs alpha grid search to find optimal linear combination weight."""
    corpus_path = Path(args.corpus) if args.corpus else get_default_corpus_path()
    evaluator = HybridRetrievalEvaluator(corpus_path=corpus_path)
    evaluator.initialize()

    print(f"\n🔬 ALPHA GRİD SEARCH: AĞIRLIKLI HİBRİT SKOR OPTİMİZASYONU")
    print(f"Formül: S_hybrid = alpha * S_bm25_norm + (1 - alpha) * S_dense_norm")
    print("-" * 75)
    print(f"{'Alpha':<8} | {'NDCG@5':<10} | {'MRR@5':<10} | {'HitRate@5':<12}")
    print("-" * 75)

    tuning_results = evaluator.tune_alpha_grid(top_k=args.top_k)
    best_entry = max(tuning_results, key=lambda x: (x["ndcg_at_5"], x["mrr_at_5"]))

    for res in tuning_results:
        marker = " 🌟 (EN İYİ)" if res["alpha"] == best_entry["alpha"] else ""
        print(f"{res['alpha']:<8.2f} | {res['ndcg_at_5']:<10.4f} | {res['mrr_at_5']:<10.4f} | {res['hit_rate_at_5'] * 100:>8.1f}%%{marker}")

    print("-" * 75)
    print(f"Optimal Alpha: {best_entry['alpha']:.2f} (NDCG@5: {best_entry['ndcg_at_5']:.4f}, MRR@5: {best_entry['mrr_at_5']:.4f})\n")
    return 0


def cmd_plot(args: argparse.Namespace) -> int:
    """Generates the 2x2 master diagnostic panel."""
    benchmark_path = Path(args.benchmark_json) if args.benchmark_json else (
        Path(__file__).resolve().parent.parent / "outputs" / "hybrid_retrieval_benchmark.json"
    )
    output_png = Path(args.output_png) if args.output_png else (
        Path(__file__).resolve().parent.parent / "outputs" / "hybrid_retrieval_panel.png"
    )

    if not benchmark_path.exists():
        print(f"Kıyaslama JSON dosyası bulunamadı ({benchmark_path}), önce benchmark çalıştırılıyor...")
        corpus_path = get_default_corpus_path()
        evaluator = HybridRetrievalEvaluator(corpus_path=corpus_path)
        evaluator.initialize()
        report = evaluator.evaluate_all(top_k=5, rrf_k=60, alpha=0.5)
        evaluator.save_benchmark_report(report, benchmark_path)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    plot_path = plot_hybrid_retrieval_panel(benchmark_data, output_png)
    print(f"✅ 2x2 Hibrit Arama Teşhis Paneli üretildi: {plot_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Builds the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="merinos-hybrid",
        description="Merinos Halı Sanayi A.Ş. - Hibrit Arama ve RRF Füzyon CLI (Day 24)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir komutlar")

    # search-hybrid
    search_p = subparsers.add_parser("search-hybrid", help="Hibrit sorgulama yap")
    search_p.add_argument("--query", "-q", type=str, required=True, help="Teknik arama sorgusu")
    search_p.add_argument("--mode", "-m", type=str, choices=["rrf", "weighted"], default="rrf", help="Füzyon algoritması")
    search_p.add_argument("--category", "-c", type=str, default=None, help="Kategori filtresi")
    search_p.add_argument("--top-k", "-k", type=int, default=5, help="Döndürülecek sonuç sayısı")
    search_p.add_argument("--rerank", "-r", action="store_true", help="Cross-Encoder ile son aşama re-ranking uygula")
    search_p.add_argument("--alpha", "-a", type=float, default=0.5, help="Weighted mod için BM25 ağırlığı (0.0 - 1.0)")
    search_p.add_argument("--rrf-k", type=int, default=60, help="RRF k sabiti (varsayılan: 60)")
    search_p.add_argument("--corpus", type=str, default=None, help="Özel külliyat dosya yolu")

    # benchmark
    bench_p = subparsers.add_parser("benchmark", help="5 model kıyaslama raporunu çalıştır ve kaydet")
    bench_p.add_argument("--corpus", type=str, default=None, help="Özel külliyat dosya yolu")
    bench_p.add_argument("--output", "-o", type=str, default=None, help="Çıktı JSON dosya yolu")
    bench_p.add_argument("--top-k", "-k", type=int, default=5, help="Top-K sınırı")
    bench_p.add_argument("--rrf-k", type=int, default=60, help="RRF k sabiti")
    bench_p.add_argument("--alpha", "-a", type=float, default=0.5, help="Weighted füzyon alpha")

    # tune-alpha
    tune_p = subparsers.add_parser("tune-alpha", help="Weighted fusion alpha parametresini grid search ile optimize et")
    tune_p.add_argument("--corpus", type=str, default=None, help="Özel külliyat dosya yolu")
    tune_p.add_argument("--top-k", "-k", type=int, default=5, help="Top-K sınırı")

    # plot
    plot_p = subparsers.add_parser("plot", help="2x2 master teşhis panelini oluştur")
    plot_p.add_argument("--benchmark-json", "-b", type=str, default=None, help="Kıyaslama JSON yolu")
    plot_p.add_argument("--output-png", "-o", type=str, default=None, help="Çıktı PNG görsel yolu")

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "search-hybrid": cmd_search_hybrid,
        "benchmark": cmd_benchmark,
        "tune-alpha": cmd_tune_alpha,
        "plot": cmd_plot,
    }

    handler = handlers.get(args.command)
    if handler:
        sys.exit(handler(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
