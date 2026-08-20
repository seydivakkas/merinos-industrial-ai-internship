"""
Merinos Industrial AI Internship - Day 27
Command-Line Interface (CLI) for Ragas RAG Evaluation & Benchmarking

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from day27.mini_project.src.models import EvalSample, RagasBenchmarkReport
from day27.mini_project.src.ragas_engine import MerinosRagasEngine
from day27.mini_project.src.visualizer import plot_ragas_diagnostic_panel


def _load_dataset(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Tek bir soruyu veya senaryoyu değerlendirir."""
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "fixtures" / "merinos_rag_eval_dataset.json"
    dataset = _load_dataset(dataset_path)

    matched = [d for d in dataset if d["question_id"] == args.question_id]
    if not matched:
        print(f"❌ Soru ID bulunamadı: {args.question_id}")
        sys.exit(1)

    item = matched[0]
    p_id = args.pipeline
    ctx_key = f"contexts_{p_id}"
    ans_key = f"answer_{p_id}"

    if ctx_key not in item or ans_key not in item:
        print(f"❌ Pipeline verisi bulunamadı: {p_id}")
        sys.exit(1)

    sample = EvalSample(
        question_id=item["question_id"],
        question=item["question"],
        department=item["department"],
        machine=item["machine"],
        ground_truth=item["ground_truth"],
        contexts=item[ctx_key],
        answer=item[ans_key],
        pipeline_id=p_id
    )

    engine = MerinosRagasEngine()
    ev = engine.evaluate_sample(sample)

    print("\n" + "=" * 80)
    print(f"📋 MERİNOS RAGAS TEKİL DEĞERLENDİRME: {ev.question_id} [{ev.pipeline_id.upper()}]")
    print("=" * 80)
    print(f"Soru: {sample.question}")
    print(f"Departman: {sample.department} | Makine: {sample.machine}")
    print(f"Altın Standart: {sample.ground_truth}")
    print(f"Model Cevabı: {sample.answer}")
    print("-" * 80)
    print(f"🎯 Bağlamsal Kesinlik (Context Precision): %{ev.context_precision * 100:.1f}")
    print(f"🎯 Bağlamsal Kapsama (Context Recall):      %{ev.context_recall * 100:.1f}")
    print(f"🎯 Sadakat (Faithfulness):                 %{ev.faithfulness * 100:.1f}")
    print(f"🎯 Cevap Uygunluğu (Answer Relevance):     %{ev.answer_relevance * 100:.1f}")
    print(f"⭐ Harmonik Ragas Skoru:                   %{ev.ragas_composite_score * 100:.1f}")
    print("-" * 80)
    print(f"Atomik İddia Analizi ({len(ev.claims)} iddia):")
    for idx, c in enumerate(ev.claims, start=1):
        status = "✅ DOĞRULANDI" if c.supported else "❌ HALÜSİNASYON / DESTEKLENMEDİ"
        print(f"  {idx}. [{status}] '{c.claim_text}' (Sim: {c.similarity_score})")
    print("=" * 80 + "\n")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Tüm 20 Merinos senaryosu üzerinde 3 RAG mimarisini kıyaslar."""
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "fixtures" / "merinos_rag_eval_dataset.json"
    dataset = _load_dataset(dataset_path)

    print(f"\n🚀 Merinos RAG Değerlendirme Kıyaslaması Başlatılıyor...")
    print(f"   Senaryo Sayısı: {len(dataset)} | Kıyaslanan Mimari: 3\n")

    engine = MerinosRagasEngine()
    report = engine.run_full_benchmark(dataset)

    print("=" * 105)
    print("📊 MERİNOS ENDÜSTRİYEL RAG VE RAGAS METRİK KIYASLAMA TABLOSU")
    print("=" * 105)
    print(f"{'Pipeline ID':<15} | {'Pipeline Adı':<26} | {'Ctx Prec':<9} | {'Ctx Recall':<10} | {'Faithful':<9} | {'Ans Relev':<9} | {'Ragas Skoru'}")
    print("-" * 105)

    for p in report.pipelines:
        print(
            f"{p.pipeline_id:<15} | {p.pipeline_name:<26} | "
            f"%{p.avg_context_precision*100:<8.1f} | %{p.avg_context_recall*100:<9.1f} | "
            f"%{p.avg_faithfulness*100:<8.1f} | %{p.avg_answer_relevance*100:<8.1f} | "
            f"%{p.avg_ragas_composite*100:.2f}"
        )
    print("=" * 105)
    print(f"🏆 En Başarılı RAG Mimarisi: {report.best_pipeline_id.upper()} (Skor: %{report.best_ragas_score*100:.2f})")
    
    compliance = report.threshold_compliance
    print(f"Üretim Onay Eşikleri:")
    print(f"  - Sadakat Eşiği (>= %75): {'✅ SAĞLANDI' if compliance.get('faithfulness_met') else '❌ SAĞLANAMADI'}")
    print(f"  - Bağlamsal Kesinlik (>= %70): {'✅ SAĞLANDI' if compliance.get('context_precision_met') else '❌ SAĞLANAMADI'}")
    print(f"  - Bağlamsal Kapsama (>= %70): {'✅ SAĞLANDI' if compliance.get('context_recall_met') else '❌ SAĞLANAMADI'}")
    print(f"  - Cevap Uygunluğu (>= %70): {'✅ SAĞLANDI' if compliance.get('answer_relevance_met') else '❌ SAĞLANAMADI'}")
    print(f"  - Ragas Bileşik Skoru (>= %72): {'✅ ONAYLANDI (CANLIYA GEÇEBİLİR)' if compliance.get('composite_score_met') else '❌ REDDEDİLDİ'}\n")

    # JSON Raporunu Kaydet
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = output_dir / "ragas_benchmark_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"[BAŞARILI] Kıyaslama raporu kaydedildi: {report_file}")

    # Görselleştirme Paneli
    if args.plot:
        panel_file = output_dir / "ragas_diagnostic_panel.png"
        plot_ragas_diagnostic_panel(report, str(panel_file))


def cmd_plot(args: argparse.Namespace) -> None:
    """Mevcut benchmark raporundan 2x2 Master Tanı Panelini yeniden oluşturur."""
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"❌ Rapor dosyası bulunamadı: {report_path}")
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    report = RagasBenchmarkReport(**data)
    plot_ragas_diagnostic_panel(report, args.output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merinos Industrial Ragas RAG Evaluation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Tek bir soruyu değerlendir")
    p_eval.add_argument("--question-id", default="Q01", help="Soru ID (örn: Q01)")
    p_eval.add_argument("--pipeline", default="pipeline_c", choices=["pipeline_a", "pipeline_b", "pipeline_c"], help="Değerlendirilecek pipeline")

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Tüm pipeline'ları kıyasla")
    p_bench.add_argument("--plot", action="store_true", help="2x2 Tanı Panelini çiz ve kaydet")

    # plot
    p_plot = subparsers.add_parser("plot", help="Rapor dosyasından tanı panelini çiz")
    p_plot.add_argument("--report", default="day27/mini_project/outputs/ragas_benchmark_report.json", help="Rapor JSON yolu")
    p_plot.add_argument("--output", default="day27/mini_project/outputs/ragas_diagnostic_panel.png", help="PNG çıktı yolu")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "plot":
        cmd_plot(args)


if __name__ == "__main__":
    main()
