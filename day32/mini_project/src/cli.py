# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
CLI: Komut Satırı Hibrit Arama, IR Metrikleri Değerlendirme ve Hata Analiz Aracı
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
from day32.mini_project.src.models import (
    GoldenQuery,
    ComprehensiveBenchmarkReport
)
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day32.mini_project.src.retrieval_evaluator import RetrievalEvaluator
from day32.mini_project.src.error_analyzer import ErrorAnalyzer
from day32.mini_project.src.visualizer import plot_comprehensive_evaluation


def load_golden_queries(filepath: str) -> List[GoldenQuery]:
    """Altın veri seti JSON dosyasını okur."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Altın veri seti bulunamadı: {filepath}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [GoldenQuery(**item) for item in data]


def init_system(
    docs_dir: str = "day31/mini_project/fixtures/documents"
) -> Tuple_Init:
    """KnowledgeManager ve HybridRetriever'ı başlatıp indeksler."""
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()
    retriever = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )
    return km, retriever


class Tuple_Init:
    def __init__(self, km, retriever):
        self.km = km
        self.retriever = retriever

    def __iter__(self):
        return iter((self.km, self.retriever))


def cmd_search(args):
    """Hibrit arama komutu."""
    _, retriever = init_system(args.docs_dir)
    print(f"\n🔍 Arama Sorgusu: '{args.query}'")
    print(f"⚙️ Füzyon Yöntemi: {args.method.upper()} (Alpha: {args.alpha}, RRF k: {args.k_rrf})")

    res = retriever.search(
        args.query,
        method=args.method,
        top_k=args.top_k,
        alpha=args.alpha,
        k_rrf=args.k_rrf
    )

    print(f"⚡ Yanıt Süresi: {res.latency_ms} ms | Bulunan Sonuç: {len(res.items)}")
    print("=" * 78)
    for item in res.items:
        print(f"[{item.rank}] Skor: {item.final_score:.6f} | Chunk: {item.chunk_id} ({item.doc_id})")
        print(f"    Yol: {item.breadcrumbs}")
        print(f"    BM25 Sıra: {item.bm25_rank} (Skor: {item.bm25_score}) | Dense Sıra: {item.dense_rank} (Skor: {item.dense_score})")
        print(f"    Metin: {item.text_snippet}")
        print("-" * 78)


def cmd_evaluate(args):
    """Tüm sistemleri altın kıyaslama veri setiyle değerlendirir."""
    _, retriever = init_system(args.docs_dir)
    queries = load_golden_queries(args.dataset)
    evaluator = RetrievalEvaluator(retriever)
    analyzer = ErrorAnalyzer()

    print(f"\n📊 {len(queries)} adet altın test sorgusu üzerinden değerlendirme başlatılıyor...")
    reports = evaluator.evaluate_all_standard_systems(queries)
    alpha_sweep = evaluator.sweep_alpha(queries)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Özet tablosu
    print("\n" + "=" * 80)
    print(f"{'Sistem':<15} | {'Hit@1':<8} | {'Hit@3':<8} | {'Hit@5':<8} | {'MRR':<8} | {'NDCG@5':<8}")
    print("-" * 80)
    best_mrr = -1.0
    best_mrr_sys = ""
    best_hit1 = -1.0
    best_hit1_sys = ""

    for sname, rep in reports.items():
        m = rep.overall_metrics
        h1 = m.hit_at_k.get(1, 0.0)
        h3 = m.hit_at_k.get(3, 0.0)
        h5 = m.hit_at_k.get(5, 0.0)
        mrr = m.mrr
        ndcg5 = m.ndcg_at_k.get(5, 0.0)

        if mrr > best_mrr:
            best_mrr = mrr
            best_mrr_sys = sname
        if h1 > best_hit1:
            best_hit1 = h1
            best_hit1_sys = sname

        print(f"{sname:<15} | {h1:<8.4f} | {h3:<8.4f} | {h5:<8.4f} | {mrr:<8.4f} | {ndcg5:<8.4f}")
    print("=" * 80)

    print(f"\n🏆 En Yüksek MRR: {best_mrr_sys} ({best_mrr:.4f})")
    print(f"🎯 En Yüksek Hit@1: {best_hit1_sys} ({best_hit1:.4f})")

    # Görselleştirme üret
    fig_path = plot_comprehensive_evaluation(reports, alpha_sweep, queries, str(out_dir / "hybrid_retrieval_evaluation.png"))
    print(f"📈 Değerlendirme Grafikleri Üretildi: {fig_path}")

    # Hata analizi
    err_records = []
    for sname, rep in reports.items():
        err_records.extend(analyzer.analyze_report(rep, queries))

    best_alpha_pt = max(alpha_sweep, key=lambda p: p.mrr)
    summary_text = (
        f"Altın veri seti değerlendirmesinde {best_mrr_sys} mimarisi MRR={best_mrr:.4f} ile en yüksek başarıyı elde etmiştir. "
        f"Lineer birleştirmede optimum ağırlık alpha={best_alpha_pt.alpha:.1f} olarak ölçülmüştür. "
        f"RRF (k=60) sıralama tabanlı füzyon, skor normalizasyonuna ihtiyaç duymaksızın endüstriyel standartta dengeli sonuç sağlamıştır."
    )

    comprehensive = ComprehensiveBenchmarkReport(
        generated_at=datetime.datetime.now().isoformat(),
        systems=reports,
        alpha_sweep=alpha_sweep,
        error_records=err_records,
        best_system_mrr=best_mrr_sys,
        best_system_hit1=best_hit1_sys,
        best_alpha=best_alpha_pt.alpha,
        executive_summary=summary_text
    )

    report_json_path = out_dir / "benchmark_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        f.write(comprehensive.model_dump_json(indent=2))
    print(f"📄 Tam Değerlendirme Raporu Kaydedildi: {report_json_path}")


def cmd_alpha_sweep(args):
    """Alpha duyarlılık taraması tablosu."""
    _, retriever = init_system(args.docs_dir)
    queries = load_golden_queries(args.dataset)
    evaluator = RetrievalEvaluator(retriever)

    step = args.step
    alphas = []
    cur = 0.0
    while cur <= 1.0001:
        alphas.append(round(cur, 2))
        cur += step

    print(f"\n🔬 Alpha Duyarlılık Taraması (Adım: {step}):")
    points = evaluator.sweep_alpha(queries, alphas)

    print("=" * 68)
    print(f"{'Alpha (α)':<10} | {'Hit@1':<10} | {'Hit@3':<10} | {'Hit@5':<10} | {'MRR':<10} | {'NDCG@5':<10}")
    print("-" * 68)
    for p in points:
        print(f"{p.alpha:<10.2f} | {p.hit_at_1:<10.4f} | {p.hit_at_3:<10.4f} | {p.hit_at_5:<10.4f} | {p.mrr:<10.4f} | {p.ndcg_at_5:<10.4f}")
    print("=" * 68)


def cmd_errors(args):
    """Hata taksonomisi analizi komutu."""
    _, retriever = init_system(args.docs_dir)
    queries = load_golden_queries(args.dataset)
    evaluator = RetrievalEvaluator(retriever)
    analyzer = ErrorAnalyzer()

    reports = evaluator.evaluate_all_standard_systems(queries)
    failures = analyzer.compare_system_failures(reports, queries)

    print("\n🔍 Sistem Bazlı Hata Modları Frekans Tablosu:")
    print("=" * 75)
    print(f"{'Sistem':<15} | {'Keyword Mismatch':<18} | {'Code Drift':<12} | {'Boundary':<10} | {'Out of Domain':<14}")
    print("-" * 75)
    for sname, counts in failures.items():
        print(f"{sname:<15} | {counts['KEYWORD_MISMATCH']:<18} | {counts['CODE_DRIFT']:<12} | {counts['CHUNK_BOUNDARY']:<10} | {counts['OUT_OF_DOMAIN']:<14}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Merinos Day 32 Hybrid Search & IR Evaluation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    p_search = subparsers.add_parser("search", help="Hibrit arama gerçekleştir")
    p_search.add_argument("query", type=str, help="Arama sorgusu")
    p_search.add_argument("--method", type=str, default="rrf", choices=["linear", "rrf"], help="Füzyon yöntemi")
    p_search.add_argument("--top-k", type=int, default=5, help="Dönecek sonuç sayısı")
    p_search.add_argument("--alpha", type=float, default=0.5, help="Lineer ağırlık (alpha)")
    p_search.add_argument("--k-rrf", type=int, default=60, help="RRF k sabiti")
    p_search.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")

    # Evaluate
    p_eval = subparsers.add_parser("evaluate", help="Tüm sistemleri değerlendir ve raporla")
    p_eval.add_argument("--dataset", type=str, default="day32/mini_project/fixtures/golden_benchmark_dataset.json")
    p_eval.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")
    p_eval.add_argument("--output-dir", type=str, default="day32/mini_project/outputs")

    # Alpha Sweep
    p_sweep = subparsers.add_parser("alpha-sweep", help="Lineer alpha parametre taraması yap")
    p_sweep.add_argument("--dataset", type=str, default="day32/mini_project/fixtures/golden_benchmark_dataset.json")
    p_sweep.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")
    p_sweep.add_argument("--step", type=float, default=0.1, help="Tarama adımı")

    # Errors
    p_err = subparsers.add_parser("error-analysis", help="Hata taksonomisi analizini göster")
    p_err.add_argument("--dataset", type=str, default="day32/mini_project/fixtures/golden_benchmark_dataset.json")
    p_err.add_argument("--docs-dir", type=str, default="day31/mini_project/fixtures/documents")

    args = parser.parse_args()
    if args.command == "search":
        cmd_search(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "alpha-sweep":
        cmd_alpha_sweep(args)
    elif args.command == "error-analysis":
        cmd_errors(args)


if __name__ == "__main__":
    main()
