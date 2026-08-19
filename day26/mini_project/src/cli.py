"""
Merinos Industrial AI Internship - Day 26
Command-Line Interface (CLI) for Vector Indexing & Optimization

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from day26.mini_project.src.models import VectorPoint, PayloadFilter
from day26.mini_project.src.benchmarker import VectorIndexBenchmarker, ExactFlatSearcher
from day26.mini_project.src.ivf_index import InvertedFileIndex
from day26.mini_project.src.hnsw_index import HNSWVectorIndex
from day26.mini_project.src.visualizer import plot_vector_index_diagnostic_panel
from day26.mini_project.src.qdrant_manager import QdrantVectorStore


def _load_points(path: Path) -> List[VectorPoint]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [VectorPoint(**item) for item in data]


def _load_queries(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_search(args: argparse.Namespace) -> None:
    """Belirtilen indeks türü üzerinde filtreli/filtresiz vektör araması yapar."""
    base_dir = Path(__file__).resolve().parent.parent
    corpus_path = base_dir / "fixtures" / "merinos_vector_corpus.json"
    points = _load_points(corpus_path)

    queries_path = base_dir / "fixtures" / "filtered_benchmark_queries.json"
    queries = _load_queries(queries_path)

    # Sorgu seçimi (query-index veya metin eşleştirme)
    if args.query_index is not None and 0 <= args.query_index < len(queries):
        matched_q = queries[args.query_index]
        q_text = matched_q["query"]
        q_vec = matched_q["vector"]
    elif args.query:
        matched_q = next((q for q in queries if args.query.lower() in q["query"].lower()), queries[0])
        q_text = args.query
        q_vec = matched_q["vector"]
    else:
        matched_q = queries[0]
        q_text = matched_q["query"]
        q_vec = matched_q["vector"]

    # Payload filtresi oluştur
    filter_dict = {}
    if args.department:
        filter_dict["department"] = args.department
    if args.machine:
        filter_dict["machine"] = args.machine

    p_filter = PayloadFilter.from_dict(filter_dict) if filter_dict else None

    # İndeks seçimi
    index_type = getattr(args, "index_type", "hnsw").lower()
    q_vec_arr = np.array(q_vec, dtype=np.float32)

    if index_type == "hnsw":
        idx = HNSWVectorIndex(dim=len(q_vec), m=16, ef_construct=64, ef_search=32, use_quantization=args.quantize)
        idx.build_index(points)
        results = idx.search(q_vec_arr, top_k=args.top_k, payload_filter=p_filter)
    elif index_type == "ivf":
        idx = InvertedFileIndex(nlist=8, nprobe=3)
        idx.build_index(points)
        results = idx.search(q_vec_arr, top_k=args.top_k, payload_filter=p_filter)
    elif index_type == "flat":
        searcher = ExactFlatSearcher(points)
        results = searcher.search(q_vec_arr, top_k=args.top_k, payload_filter=p_filter)
    else:
        # Qdrant Vector Store
        store = QdrantVectorStore(collection_name="merinos_cli_demo")
        store.create_collection(m=16, ef_construct=64, use_quantization=args.quantize)
        store.create_payload_index("department")
        store.create_payload_index("machine")
        store.upsert_points(points)
        results = store.search(q_vec, top_k=args.top_k, payload_filter=p_filter)

    print(f"\n🔍 Vektör Arama Sonuçları (İndeks: {index_type.upper()}, Sorgu: '{q_text}')")
    if p_filter:
        print(f"   Uygulanan Filtre: {filter_dict}")
    print(f"   Bulunan Nokta: {len(results)}\n" + "-" * 75)

    for r in results:
        payload = r.payload
        print(f"[{r.rank}] Skor: {r.score:.4f} | Makine: {payload.get('machine')} | Dept: {payload.get('department')}")
        print(f"    Başlık: {payload.get('title')}")
        print(f"    Yol: {payload.get('breadcrumbs')}\n")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Flat, IVF, HNSW ve Kuantize HNSW indekslerini kıyaslar."""
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "configs" / "vector_index_config.json"
    corpus_path = base_dir / "fixtures" / "merinos_vector_corpus.json"
    queries_path = base_dir / "fixtures" / "filtered_benchmark_queries.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    points = _load_points(corpus_path)
    queries = _load_queries(queries_path)

    print(f"\n🚀 Merinos Vektör İndeks ve Kuantizasyon Kıyaslaması Başlatılıyor...")
    print(f"   Vektör Sayısı: {len(points)} | Boyut: {len(points[0].vector)} | Test Sorgusu: {len(queries)}")

    benchmarker = VectorIndexBenchmarker(config=config)
    report = benchmarker.run_benchmark(points, queries)

    # Konsola kurumsal özet tablosu bas
    print("\n" + "=" * 94)
    print("📊 MERİNOS VEKTÖR VERİTABANI & İNDEKS KIYASLAMA TABLOSU")
    print("=" * 94)
    header = f"{'İndeks Türü':<18} | {'İnşa(ms)':<9} | {'Latans(ms)':<10} | {'QPS':<8} | {'Bellek(KB)':<10} | {'Recall@5':<9} | {'Filt.Recall':<11}"
    print(header)
    print("-" * 94)

    for k, m in report.indices.items():
        row = (
            f"{m.index_type:<18} | {m.indexing_time_ms:<9.1f} | {m.query_latency_ms:<10.2f} | "
            f"{m.qps:<8.0f} | {m.memory_kb:<10.1f} | %{m.recall_at_5*100:<8.1f} | %{m.filtered_recall_at_5*100:<10.1f}"
        )
        print(row)
    print("=" * 94)
    print(f"🏆 En Yüksek QPS (Hız): {report.best_qps_index.upper()}")
    print(f"🏆 En Yüksek Doğruluk (Recall): {report.best_recall_index.upper()}")
    print(f"🏆 En Düşük Bellek Tüketimi: {report.most_memory_efficient_index.upper()}")

    # Raporu kaydet
    out_file = base_dir / "outputs" / "vector_index_benchmark_report.json"
    if args.output:
        out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"\n[BAŞARILI] Kıyaslama raporu kaydedildi: {out_file}")

    if args.plot:
        plot_p = base_dir / "outputs" / "vector_index_diagnostic_panel.png"
        plot_vector_index_diagnostic_panel(report, plot_p)
        print(f"[BAŞARILI] 2x2 Tanı paneli oluşturuldu: {plot_p}")


def cmd_plot(args: argparse.Namespace) -> None:
    """Mevcut rapordan 2x2 Master Tanı Panelini çizer."""
    base_dir = Path(__file__).resolve().parent.parent
    report_file = base_dir / "outputs" / "vector_index_benchmark_report.json"

    from day26.mini_project.src.models import VectorIndexReport

    if report_file.exists() and not args.recompute:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        report = VectorIndexReport(**data)
    else:
        config_path = base_dir / "configs" / "vector_index_config.json"
        corpus_path = base_dir / "fixtures" / "merinos_vector_corpus.json"
        queries_path = base_dir / "fixtures" / "filtered_benchmark_queries.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        points = _load_points(corpus_path)
        queries = _load_queries(queries_path)
        benchmarker = VectorIndexBenchmarker(config=config)
        report = benchmarker.run_benchmark(points, queries)

    out_plot = Path(args.output) if args.output else base_dir / "outputs" / "vector_index_diagnostic_panel.png"
    plot_vector_index_diagnostic_panel(report, out_plot)
    print(f"\n[BAŞARILI] 2x2 Tanı Paneli üretildi: {out_plot}")


def main() -> None:
    """CLI giriş noktası."""
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Merinos Industrial AI Internship - Day 26 Vector Indexing CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: search
    p_search = subparsers.add_parser("search", help="Vektör indeksi veya Qdrant üzerinde filtreli arama yap")
    p_search.add_argument("-q", "--query", type=str, default=None, help="Arama sorgusu metni")
    p_search.add_argument("--query-index", type=int, default=0, help="Test sorgu kütüphanesinden sorgu indeksi")
    p_search.add_argument("--index-type", type=str, default="hnsw", choices=["hnsw", "ivf", "flat", "qdrant"], help="İndeks mimarisi")
    p_search.add_argument("--filter-dept", "--department", dest="department", type=str, default=None, help="Departman filtresi")
    p_search.add_argument("--filter-machine", "--machine", dest="machine", type=str, default=None, help="Makine modeli filtresi")
    p_search.add_argument("-k", "--top-k", type=int, default=5, help="Top-K sonuç sayısı")
    p_search.add_argument("--quantize", action="store_true", help="Int8 skaler kuantizasyon kullan")
    p_search.set_defaults(func=cmd_search)

    # Subcommand: benchmark
    p_bench = subparsers.add_parser("benchmark", help="Flat, IVF, HNSW ve Quantized HNSW kıyaslamasını çalıştır")
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
