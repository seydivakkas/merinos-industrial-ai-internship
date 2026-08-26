# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
Unit & Integration Tests: Hybrid Search Fusion, RRF Mathematics, IR Evaluator Metrics
"""

import pytest
import math
from pathlib import Path

from day31.mini_project.src.models import ChunkRecord
from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.models import (
    GoldenQuery,
    FusedItem,
    MetricScore,
    QueryEvaluationResult,
    SystemEvaluationReport
)
from day32.mini_project.src.hybrid_retriever import (
    HybridRetriever,
    min_max_normalize,
    compute_rrf_score
)
from day32.mini_project.src.retrieval_evaluator import (
    RetrievalEvaluator,
    compute_dcg,
    compute_idcg
)
from day32.mini_project.src.error_analyzer import ErrorAnalyzer
from day32.mini_project.src.cli import load_golden_queries


# =====================================================================
# 1. Matematiksel Birim Testleri: Min-Max Normalizasyon & RRF
# =====================================================================

def test_min_max_normalize_normal():
    scores = {"doc1": 10.0, "doc2": 20.0, "doc3": 30.0}
    norm = min_max_normalize(scores)
    assert norm["doc1"] == 0.0
    assert norm["doc2"] == 0.5
    assert norm["doc3"] == 1.0


def test_min_max_normalize_edge_cases():
    # Boş sözlük
    assert min_max_normalize({}) == {}

    # Tek eleman
    assert min_max_normalize({"doc1": 15.0}) == {"doc1": 1.0}
    assert min_max_normalize({"doc1": 0.0}) == {"doc1": 0.0}

    # Eşit skorlar
    equal_scores = {"doc1": 5.0, "doc2": 5.0}
    res = min_max_normalize(equal_scores)
    assert res["doc1"] == 1.0
    assert res["doc2"] == 1.0


def test_compute_rrf_score_analytic():
    # Cormack 2009: k=60
    # Sıra 1: 1 / (60 + 1) = 1/61
    assert pytest.approx(compute_rrf_score(1, k=60), rel=1e-5) == 1.0 / 61.0
    # Sıra 2: 1 / (60 + 2) = 1/62
    assert pytest.approx(compute_rrf_score(2, k=60), rel=1e-5) == 1.0 / 62.0
    # Sıra 3: 1 / (60 + 3) = 1/63
    assert pytest.approx(compute_rrf_score(3, k=60), rel=1e-5) == 1.0 / 63.0

    # İki sistemde 1. ve 2. olan dökümanın toplam RRF skoru
    combined = compute_rrf_score(1, k=60) + compute_rrf_score(2, k=60)
    assert pytest.approx(combined, rel=1e-5) == (1.0 / 61.0 + 1.0 / 62.0)


def test_compute_rrf_invalid_rank():
    with pytest.raises(ValueError):
        compute_rrf_score(0, k=60)
    with pytest.raises(ValueError):
        compute_rrf_score(-1, k=60)


# =====================================================================
# 2. DCG ve IDCG Hesaplama Testleri
# =====================================================================

def test_dcg_and_idcg_values():
    # Rank 1'deki doküman için DCG@5
    dcg1 = compute_dcg([1], k=5)
    assert pytest.approx(dcg1, rel=1e-5) == 1.0 / math.log2(2.0)  # = 1.0

    # Rank 2'deki doküman için DCG@5
    dcg2 = compute_dcg([2], k=5)
    assert pytest.approx(dcg2, rel=1e-5) == 1.0 / math.log2(3.0)

    # Rank 10'daki doküman DCG@5 sınırının dışındadır
    dcg_out = compute_dcg([10], k=5)
    assert dcg_out == 0.0

    # 1 adet ilgili doküman için IDCG@5
    idcg = compute_idcg(1, k=5)
    assert pytest.approx(idcg, rel=1e-5) == 1.0


# =====================================================================
# 3. Retrieval Değerlendirici (RetrievalEvaluator) Sentetik Testleri
# =====================================================================

def test_evaluator_synthetic_query_scoring():
    evaluator = RetrievalEvaluator(hybrid_retriever=None, k_values=[1, 3, 5, 10])

    q = GoldenQuery(
        id="Q_TEST_1",
        query="test query",
        category="EXACT_CODE",
        target_chunk_id="chunk_A",
        target_doc_id="doc_A",
        keywords=["test"]
    )

    # Durum 1: Hedef 1. sırada bulundu
    res1 = evaluator.evaluate_query(q, ["chunk_A", "chunk_B", "chunk_C"], ["doc_A", "doc_B", "doc_C"])
    assert res1.found_rank == 1
    assert res1.top1_correct is True
    assert res1.reciprocal_rank == 1.0
    assert res1.hit_at_k[1] is True
    assert res1.hit_at_k[3] is True

    # Durum 2: Hedef 2. sırada bulundu
    res2 = evaluator.evaluate_query(q, ["chunk_B", "chunk_A", "chunk_C"], ["doc_B", "doc_A", "doc_C"])
    assert res2.found_rank == 2
    assert res2.top1_correct is False
    assert res2.reciprocal_rank == 0.5
    assert res2.hit_at_k[1] is False
    assert res2.hit_at_k[3] is True

    # Durum 3: Hedef ilk 5'te yok
    res3 = evaluator.evaluate_query(q, ["chunk_X", "chunk_Y"], ["doc_X", "doc_Y"])
    assert res3.found_rank is None
    assert res3.top1_correct is False
    assert res3.reciprocal_rank == 0.0
    assert res3.hit_at_k[1] is False
    assert res3.hit_at_k[5] is False


def test_evaluator_out_of_domain_query():
    evaluator = RetrievalEvaluator(hybrid_retriever=None, k_values=[1, 3, 5])
    q_ood = GoldenQuery(
        id="Q_OOD",
        query="alakasız sorgu",
        category="OUT_OF_DOMAIN",
        target_chunk_id=None,
        target_doc_id=None
    )
    res = evaluator.evaluate_query(q_ood, ["chunk_A", "chunk_B"], ["doc_A", "doc_B"])
    assert res.found_rank is None
    assert res.reciprocal_rank == 0.0
    assert res.hit_at_k[1] is False


# =====================================================================
# 4. Hata Teşhis Motoru (ErrorAnalyzer) Testleri
# =====================================================================

def test_error_analyzer_diagnose():
    analyzer = ErrorAnalyzer()

    # A. Out of Domain
    q_ood = GoldenQuery(id="Q_OOD", query="yemekhane menüsü", category="OUT_OF_DOMAIN")
    res_ood = QueryEvaluationResult(
        query_id="Q_OOD",
        query="yemekhane menüsü",
        category="OUT_OF_DOMAIN",
        target_chunk_id=None,
        target_doc_id=None,
        found_rank=None,
        hit_at_k={1: False},
        reciprocal_rank=0.0,
        top1_retrieved_chunk_id="c1",
        top1_correct=False
    )
    err_ood = analyzer.diagnose_query_failure("RRF_k60", q_ood, res_ood)
    assert err_ood is not None
    assert err_ood.failure_type == "OUT_OF_DOMAIN"

    # B. Dense üzerinde Kod Sapması (CODE_DRIFT)
    q_code = GoldenQuery(
        id="Q_CODE",
        query="E-401 arıza kodu",
        category="EXACT_CODE",
        target_chunk_id="chunk_target",
        keywords=["E-401"]
    )
    res_code = QueryEvaluationResult(
        query_id="Q_CODE",
        query="E-401 arıza kodu",
        category="EXACT_CODE",
        target_chunk_id="chunk_target",
        target_doc_id="doc1",
        found_rank=3,
        hit_at_k={1: False, 3: True},
        reciprocal_rank=1/3,
        top1_retrieved_chunk_id="chunk_other",
        top1_correct=False
    )
    err_code = analyzer.diagnose_query_failure("Dense", q_code, res_code)
    assert err_code is not None
    assert err_code.failure_type == "CODE_DRIFT"

    # C. BM25 üzerinde Kelime Eşleşmeme (KEYWORD_MISMATCH)
    q_sem = GoldenQuery(
        id="Q_SEM",
        query="motorun sıcaklık artışı operatör refleksi",
        category="SEMANTIC_SYMPTOM",
        target_chunk_id="chunk_target",
        keywords=["aşırı ısınma"]
    )
    res_sem = QueryEvaluationResult(
        query_id="Q_SEM",
        query="motorun sıcaklık artışı operatör refleksi",
        category="SEMANTIC_SYMPTOM",
        target_chunk_id="chunk_target",
        target_doc_id="doc1",
        found_rank=4,
        hit_at_k={1: False},
        reciprocal_rank=0.25,
        top1_retrieved_chunk_id="chunk_other",
        top1_correct=False
    )
    err_sem = analyzer.diagnose_query_failure("BM25", q_sem, res_sem)
    assert err_sem is not None
    assert err_sem.failure_type == "KEYWORD_MISMATCH"


# =====================================================================
# 5. Uçtan Uca Entegrasyon Testi (Real Chunks & Golden Queries)
# =====================================================================

def test_end_to_end_hybrid_evaluation():
    docs_dir = Path("day31/mini_project/fixtures/documents")
    golden_path = Path("day32/mini_project/fixtures/golden_benchmark_dataset.json")

    assert docs_dir.exists(), "Day 31 documents dizini mevcut olmalıdır."
    assert golden_path.exists(), "Day 32 golden dataset mevcut olmalıdır."

    km = KnowledgeManager(documents_dir=str(docs_dir))
    km.sync()
    assert len(km.chunks) >= 8, f"En az 8 parça indekslenmeliydi, bulunan: {len(km.chunks)}"

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )

    # 1. Lineer Arama Testi
    res_lin = hybrid.search_linear("E-401 motor aşırı ısınması", top_k=3, alpha=0.5)
    assert len(res_lin.items) > 0
    assert res_lin.fusion_method == "linear"
    assert res_lin.alpha == 0.5
    assert res_lin.items[0].final_score >= 0.0

    # 2. RRF Arama Testi
    res_rrf = hybrid.search_rrf("14 bar tansiyon basıncı vana 3", top_k=3, k=60)
    assert len(res_rrf.items) > 0
    assert res_rrf.fusion_method == "rrf"
    assert res_rrf.k_rrf == 60
    assert res_rrf.items[0].final_score > 0.0

    # 3. Değerlendirme Testi
    queries = load_golden_queries(str(golden_path))
    assert len(queries) == 15

    evaluator = RetrievalEvaluator(hybrid, k_values=[1, 3, 5])
    reports = evaluator.evaluate_all_standard_systems(queries)

    assert "BM25" in reports
    assert "Dense" in reports
    assert "Linear_0.5" in reports
    assert "RRF_k60" in reports

    # Metriklerin [0, 1] aralığında olduğunu doğrula
    for sname, rep in reports.items():
        m = rep.overall_metrics
        assert 0.0 <= m.hit_at_k[1] <= 1.0
        assert 0.0 <= m.hit_at_k[3] <= 1.0
        assert 0.0 <= m.mrr <= 1.0
        assert rep.valid_queries == 14  # 15 sorgudan 1'i OUT_OF_DOMAIN
        assert rep.total_queries == 15

    # 4. Alpha Sweep Testi
    sweep = evaluator.sweep_alpha(queries, alphas=[0.0, 0.5, 1.0])
    assert len(sweep) == 3
    assert sweep[0].alpha == 0.0
    assert sweep[1].alpha == 0.5
    assert sweep[2].alpha == 1.0
