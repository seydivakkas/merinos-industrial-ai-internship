"""
Merinos Industrial AI Internship - Day 27
Unit & Integration Tests for Ragas RAG Retrieval & Generation Evaluation

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import json
from pathlib import Path
import pytest
import matplotlib
matplotlib.use("Agg")

from day27.mini_project.src.models import EvalSample, SampleEvaluation
from day27.mini_project.src.claim_extractor import ClaimExtractor
from day27.mini_project.src.context_metrics import ContextPrecisionEvaluator, ContextRecallEvaluator
from day27.mini_project.src.generation_metrics import FaithfulnessEvaluator, AnswerRelevanceEvaluator
from day27.mini_project.src.ragas_engine import MerinosRagasEngine
from day27.mini_project.src.visualizer import plot_ragas_diagnostic_panel


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def eval_dataset(fixtures_dir: Path):
    with open(fixtures_dir / "merinos_rag_eval_dataset.json", "r", encoding="utf-8") as f:
        return json.load(f)


def test_claim_extractor_atomic_propositions():
    """Cümlelerin ve yan tümcelerin atomik teknik iddialara doğru ayrıştırıldığını test eder."""
    extractor = ClaimExtractor(min_words=3)
    text = (
        "Merhaba, Van de Wiele RCE02 tezgâhında rapier şeridi merkezleme toleransı ±0.08 mm olmalıdır. "
        "Ayrıca tekrarlayan atkı kopuşlarında ilk kontrol adımı fren gerginliğinin kontrolüdür."
    )
    claims = extractor.extract_claims(text)
    assert len(claims) >= 2
    assert any("±0.08 mm" in c for c in claims)
    assert not any(c.lower().startswith("merhaba") for c in claims)


def test_context_precision_ranking_penalty():
    """Alakasız bağlamın 1. sırada (rank 1) gelmesinin Context Precision'ı belirgin şekilde düşürdüğünü test eder."""
    evaluator = ContextPrecisionEvaluator()
    gt = "Levent fren pnömatik basıncı 4.2 bar ile 4.8 bar aralığında stabil tutulmalıdır."
    q = "RCE02 fren basıncı kaç bar olmalıdır?"

    # Senaryo 1: İlk sırada mükemmel eşleşen bağlam (İyi sıralama)
    good_contexts = [
        "Van de Wiele RCE02 tezgâhında çözgü levent fren pnömatik basıncı 4.2 bar ile 4.8 bar aralığında tutulmalıdır.",
        "Kompresör hava basıncı 7.5 bar seviyesindedir."
    ]
    score_good = evaluator.evaluate(good_contexts, gt, q)
    assert score_good.score >= 0.80

    # Senaryo 2: İlk sırada alakasız bağlam, 2. sırada ilgili bağlam (Kötü sıralama)
    bad_contexts = [
        "Genel zemin mikrofiber paspas ile temizlenmelidir.",
        "Van de Wiele RCE02 tezgâhında çözgü levent fren pnömatik basıncı 4.2 bar ile 4.8 bar aralığında tutulmalıdır."
    ]
    score_bad = evaluator.evaluate(bad_contexts, gt, q)
    assert score_bad.score < score_good.score


def test_context_recall_completeness():
    """Altın standarttaki tüm teknik iddiaların bağlamda bulunması durumunda Recall'ın yüksek olduğunu test eder."""
    evaluator = ContextRecallEvaluator()
    gt = "Schönherr Alpha 500 armür şedding yüksekliği 145 mm olmalı ve kapanma krank mili 310 derecede gerçekleşmelidir."

    full_contexts = [
        "Schönherr Alpha 500 tezgâhında armür şedding açılma yüksekliği 145 mm (±2 mm) olmalıdır.",
        "Şedding kapanma zamanlaması ana krank mili 310 derece pozisyonunda gerçekleşmelidir."
    ]
    res_full = evaluator.evaluate(full_contexts, gt)
    assert res_full.score >= 0.80

    incomplete_contexts = [
        "Halı fabrikasında havalandırma şartlandırması %65 nemde tutulur.",
        "Schönherr Alpha 500 tezgâhında armür şedding açılma yüksekliği 145 mm olmalıdır."
    ]
    res_inc = evaluator.evaluate(incomplete_contexts, gt)
    assert res_inc.score <= res_full.score


def test_faithfulness_hallucination_detection():
    """Bağlamda geçmeyen sahte/uydurma sayısal değerlerin (halüsinasyon) tespit edilip düşük puan aldığını test eder."""
    evaluator = FaithfulnessEvaluator()
    contexts = [
        "Van de Wiele RCE02 tezgâhında rapier şeritleri merkezleme kaçıklığı maksimum ±0.08 mm tolerans aralığında olmalıdır.",
        "Tekrarlayan atkı kopuşlarında ilk kontrol adımı atkı ipliği fren gerginliğinin kontrol edilmesidir."
    ]

    # Halüsinasyon içeren cevap: ±0.20 mm ve 50 bar uydurulmuş
    hallucinated_answer = "Rapier merkezleme toleransı ±0.20 mm olmalıdır ve hava basıncı 50 bar seviyesine ayarlanmalıdır."
    score_hallucinated, claims = evaluator.evaluate(contexts, hallucinated_answer)
    assert score_hallucinated.score < 0.50
    assert any(not c.supported for c in claims)


def test_faithfulness_grounded_answer():
    """Bağlama harfiyen dayanan ve doğru teknik verileri içeren cevabın %100 sadakat aldığını test eder."""
    evaluator = FaithfulnessEvaluator()
    contexts = [
        "Barmag ekstrüder eriyik filtresinde diferansiyel basınç (Delta P) 65 bar değerini aştığında filtre değişimi zorunludur."
    ]
    grounded_answer = "Barmag ekstrüder eriyik filtresinde diferansiyel basınç 65 barı aştığında filtre elemanı değiştirilmelidir."
    score_grounded, claims = evaluator.evaluate(contexts, grounded_answer)
    assert score_grounded.score >= 0.90
    assert all(c.supported for c in claims)


def test_answer_relevance_pertinence():
    """Teknik soruya doğrudan cevap veren ifadelerin yüksek, konu dışı cevapların düşük uygunluk aldığını test eder."""
    evaluator = AnswerRelevanceEvaluator()
    question = "PA6 halı ipliği bobin boyama prosesinde boya banyosu pH değeri hangi aralıkta olmalıdır?"

    relevant_answer = "PA6 boyama prosesinde banyo pH değeri 4.5 ile 5.0 aralığında tutulmalıdır."
    score_rel = evaluator.evaluate(question, relevant_answer)
    assert score_rel.score >= 0.70

    irrelevant_answer = "Dokuma salonunda güvenlik amacıyla çelik burunlu iş ayakkabısı giyilmesi zorunludur."
    score_irrel = evaluator.evaluate(question, irrelevant_answer)
    assert score_irrel.score < score_rel.score


def test_ragas_composite_harmonic_score():
    """Harmonik ortalama bileşik skorunun herhangi bir sıfır veya zayıf metriğe karşı duyarlılığını test eder."""
    engine = MerinosRagasEngine()
    
    # Dengeli yüksek skorlar
    score_balanced = engine.compute_composite_score(0.9, 0.9, 0.9, 0.9, method="harmonic")
    assert 0.85 <= score_balanced <= 0.95

    # Bir metrik sıfır olduğunda harmonik ortalama çöker (halüsinasyon veya alakasız bağlam cezası)
    score_zero = engine.compute_composite_score(0.0, 0.9, 0.9, 0.9, method="harmonic")
    assert score_zero < 0.05


def test_merinos_ragas_engine_single_sample(eval_dataset):
    """Tek bir EvalSample üzerinde 4 metriğin de [0.0, 1.0] aralığında geçerli hesaplandığını test eder."""
    engine = MerinosRagasEngine()
    first = eval_dataset[0]
    sample = EvalSample(
        question_id=first["question_id"],
        question=first["question"],
        department=first["department"],
        machine=first["machine"],
        ground_truth=first["ground_truth"],
        contexts=first["contexts_pipeline_c"],
        answer=first["answer_pipeline_c"],
        pipeline_id="pipeline_c"
    )

    ev = engine.evaluate_sample(sample)
    assert isinstance(ev, SampleEvaluation)
    assert 0.0 <= ev.faithfulness <= 1.0
    assert 0.0 <= ev.context_precision <= 1.0
    assert 0.0 <= ev.context_recall <= 1.0
    assert 0.0 <= ev.answer_relevance <= 1.0
    assert 0.0 <= ev.ragas_composite_score <= 1.0
    assert ev.faithfulness >= 0.80  # Pipeline C yüksek sadakatli olmalı


def test_merinos_ragas_engine_full_benchmark(eval_dataset):
    """20 Merinos senaryosu üzerinde Pipeline C'nin Pipeline A'dan üstün olduğunu doğrular."""
    engine = MerinosRagasEngine()
    report = engine.run_full_benchmark(eval_dataset)

    assert len(report.pipelines) == 3
    pipe_a = next(p for p in report.pipelines if p.pipeline_id == "pipeline_a")
    pipe_b = next(p for p in report.pipelines if p.pipeline_id == "pipeline_b")
    pipe_c = next(p for p in report.pipelines if p.pipeline_id == "pipeline_c")

    # Pipeline C (Hybrid + Reranked) en yüksek skora sahip olmalı
    assert pipe_c.avg_ragas_composite > pipe_b.avg_ragas_composite
    assert pipe_b.avg_ragas_composite > pipe_a.avg_ragas_composite

    # Pipeline C sadakat ve bağlamsal kesinlikte %80 üzerinde olmalı
    assert pipe_c.avg_faithfulness >= 0.80
    assert pipe_c.avg_context_precision >= 0.70
    assert report.best_pipeline_id == "pipeline_c"


def test_diagnostic_panel_generation(eval_dataset, tmp_path):
    """2x2 Master Tanı Panelinin geçerli bir 300 DPI PNG dosyası olarak kaydedildiğini test eder."""
    engine = MerinosRagasEngine()
    report = engine.run_full_benchmark(eval_dataset[:5])  # Hızlı test için ilk 5 örnek

    out_png = tmp_path / "test_panel.png"
    fig = plot_ragas_diagnostic_panel(report, str(out_png))
    assert out_png.exists()
    assert out_png.stat().st_size > 50000  # En az 50 KB görsel
