"""
Merinos Industrial AI Internship - Day 25
Command-Line Interface (CLI) for Document Chunking Strategies

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from day25.mini_project.src.models import DocumentItem
from day25.mini_project.src.chunk_engine import MerinosChunkEngine
from day25.mini_project.src.evaluator import ChunkingBenchmarkEvaluator
from day25.mini_project.src.visualizer import plot_chunking_diagnostic_panel


def _load_corpus(path: Path) -> List[DocumentItem]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [DocumentItem(**item) for item in data]


def _load_queries(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_chunk(args: argparse.Namespace) -> None:
    """Tekil bir dokümanı veya korpusu parçalar."""
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "configs" / "chunking_config.json"
    corpus_path = base_dir / "fixtures" / "merinos_sop_documents.json"

    engine = MerinosChunkEngine.from_config_file(config_path)
    corpus = _load_corpus(corpus_path)

    target_docs = [d for d in corpus if d.doc_id == args.doc_id] if args.doc_id else corpus

    if not target_docs:
        print(f"[HATA] Doküman bulunamadı: {args.doc_id}")
        return

    all_chunks = []
    for d in target_docs:
        chunks = engine.chunk_document(d, args.strategy)
        all_chunks.extend(chunks)

    print(f"[INFO] Performing chunking with strategy: {args.strategy}")
    doc_desc = f"{args.doc_id} (1 document)" if args.doc_id else f"{len(target_docs)} documents"
    print(f"[INFO] Processing document: {doc_desc}")
    preview_chunks = all_chunks[:args.limit]
    print(f"[INFO] Generated {len(preview_chunks)} preview chunks (limit={args.limit})")

    for idx, c in enumerate(preview_chunks, start=1):
        if c.section_headers:
            headers_show = c.section_headers[1:] if len(c.section_headers) > 1 else c.section_headers
            section_str = " > ".join(headers_show) if headers_show else c.title
        elif "breadcrumbs" in c.metadata:
            section_str = c.metadata["breadcrumbs"]
        else:
            section_str = c.title

        print("-" * 80)
        print(f"[Chunk {idx}/{len(preview_chunks)}] ({c.doc_id}) [Bölüm: {section_str}]")
        clean_lines = [l.strip() for l in c.content.split("\n") if l.strip() and not l.strip().startswith("#")]
        content_preview = " ".join(clean_lines)
        if len(content_preview) > 120:
            content_preview = content_preview[:120].rstrip() + " ..."
        print(content_preview)
    print("-" * 80)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in all_chunks], f, ensure_ascii=False, indent=2)
        print(f"\n[BAŞARILI] Parçalar kaydedildi: {out_p}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """4 parçalama stratejisinin tamamını kıyaslar ve rapor üretir."""
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "configs" / "chunking_config.json"
    corpus_path = base_dir / "fixtures" / "merinos_sop_documents.json"
    queries_path = base_dir / "fixtures" / "chunking_evaluation_queries.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    corpus = _load_corpus(corpus_path)
    queries = _load_queries(queries_path)

    print(f"\n🚀 Merinos Halı Doküman Parçalama Kıyaslaması Başlatılıyor...")
    print(f"   Doküman Sayısı: {len(corpus)} | Sorgu Sayısı: {len(queries)}")

    evaluator = ChunkingBenchmarkEvaluator(config=config)
    report = evaluator.run_benchmark(corpus, queries)

    # Konsola kurumsal özet tablosu bas
    print("\n" + "=" * 88)
    print("📊 MERİNOS DOKÜMAN PARÇALAMA STRATEJİLERİ KIYASLAMA TABLOSU")
    print("=" * 88)
    header = f"{'Strateji':<18} | {'Parça':<6} | {'Ort.Boy':<8} | {'Coherence':<10} | {'P@1':<6} | {'R@5':<6} | {'MRR':<6} | {'NDCG@5':<7} | {'Needle@5':<8}"
    print(header)
    print("-" * 88)

    for s_name, res in report.strategies.items():
        st = res.stats
        rt = res.retrieval
        row = (
            f"{s_name:<18} | {st.total_chunks:<6} | {st.mean_char_length:<8.1f} | "
            f"%{st.intra_chunk_coherence*100:<9.1f} | {rt.precision_at_1:<6.2f} | {rt.recall_at_5:<6.2f} | "
            f"{rt.mrr:<6.2f} | {rt.ndcg_at_5:<7.2f} | %{rt.needle_hit_rate_at_5*100:<7.1f}"
        )
        print(row)
    print("=" * 88)
    print(f"🏆 En Yüksek Getirme (NDCG@5): {report.best_retrieval_strategy.upper()}")
    print(f"🏆 En Yüksek Anlamsal Bütünlük (Coherence): {report.best_coherence_strategy.upper()}")

    # Rapor dosyasını kaydet
    out_file = base_dir / "outputs" / "chunking_benchmark_report.json"
    if args.output:
        out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"\n[BAŞARILI] Kıyaslama raporu kaydedildi: {out_file}")

    if args.plot:
        plot_p = base_dir / "outputs" / "chunking_diagnostic_panel.png"
        plot_chunking_diagnostic_panel(report, plot_p)
        print(f"[BAŞARILI] Tanı paneli oluşturuldu: {plot_p}")


def cmd_plot(args: argparse.Namespace) -> None:
    """Mevcut veya yeni çalıştırılan kıyaslama için 2x2 Master Tanı Panelini çizer."""
    base_dir = Path(__file__).resolve().parent.parent
    report_file = base_dir / "outputs" / "chunking_benchmark_report.json"

    from day25.mini_project.src.models import ChunkingBenchmarkReport

    if report_file.exists() and not args.recompute:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        report = ChunkingBenchmarkReport(**data)
    else:
        config_path = base_dir / "configs" / "chunking_config.json"
        corpus_path = base_dir / "fixtures" / "merinos_sop_documents.json"
        queries_path = base_dir / "fixtures" / "chunking_evaluation_queries.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        corpus = _load_corpus(corpus_path)
        queries = _load_queries(queries_path)
        evaluator = ChunkingBenchmarkEvaluator(config=config)
        report = evaluator.run_benchmark(corpus, queries)

    out_plot = Path(args.output) if args.output else base_dir / "outputs" / "chunking_diagnostic_panel.png"
    plot_chunking_diagnostic_panel(report, out_plot)
    print(f"\n[BAŞARILI] 2x2 Tanı Paneli üretildi: {out_plot}")


def main() -> None:
    """CLI giriş noktası."""
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Merinos Industrial AI Internship - Day 25 Document Chunking Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: chunk
    p_chunk = subparsers.add_parser("chunk", help="Belirtilen strateji ile parçalama yap")
    p_chunk.add_argument("--strategy", choices=["fixed_size", "recursive", "semantic", "markdown_aware"], default="markdown_aware", help="Parçalama stratejisi")
    p_chunk.add_argument("--doc-id", type=str, default=None, help="Belirli bir doküman ID'si (örn: SOP-001)")
    p_chunk.add_argument("--limit", type=int, default=5, help="Konsolda gösterilecek maksimum parça sayısı")
    p_chunk.add_argument("--output", type=str, default=None, help="Parçaları JSON olarak kaydetme yolu")
    p_chunk.set_defaults(func=cmd_chunk)

    # Subcommand: benchmark
    p_bench = subparsers.add_parser("benchmark", help="4 parçalama stratejisini kıyasla")
    p_bench.add_argument("--output", type=str, default=None, help="Rapor JSON çıkış yolu")
    p_bench.add_argument("--plot", action="store_true", help="Kıyaslama sonrası tanı panelini de çiz")
    p_bench.set_defaults(func=cmd_benchmark)

    # Subcommand: plot
    p_plot = subparsers.add_parser("plot", help="2x2 Tanı Panelini oluştur")
    p_plot.add_argument("--output", type=str, default=None, help="Görsel çıkış yolu (.png)")
    p_plot.add_argument("--recompute", action="store_true", help="Raporu sıfırdan hesapla")
    p_plot.set_defaults(func=cmd_plot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
