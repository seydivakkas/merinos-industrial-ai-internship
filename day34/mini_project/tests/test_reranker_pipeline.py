# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Birim ve Entegrasyon Testleri: Two-Stage Retrieval, Cross-Encoder Reranker ve Token Sıkıştırması
"""

import json
from pathlib import Path
import pytest

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day34.mini_project.src.models import (
    CandidateChunk,
    RerankedChunk,
    CompressionMetric,
    CostLatencyProfile,
    TwoStageRetrievalResult
)
from day34.mini_project.src.cross_encoder_reranker import CrossEncoderReranker
from day34.mini_project.src.cost_latency_analyzer import CostLatencyAnalyzer
from day34.mini_project.src.two_stage_pipeline import TwoStageRetriever


# =====================================================================
# 1. Veri Modelleri Doğrulama Testleri
# =====================================================================

def test_candidate_and_reranked_models():
    cand = CandidateChunk(
        chunk_id="c1",
        doc_id="d1",
        first_stage_rank=4,
        first_stage_score=0.65,
        source="SOP",
        section="Bakım",
        breadcrumbs="SOP > Bakım",
        text="E-401 motor sıcaklığı 85 dereceyi geçince stop eder."
    )
    assert cand.chunk_id == "c1"
    assert cand.first_stage_rank == 4

    reranked = RerankedChunk(
        chunk_id="c1",
        doc_id="d1",
        first_stage_rank=4,
        rerank_rank=1,
        rerank_score=0.92,
        rank_delta=3,
        source="SOP",
        section="Bakım",
        breadcrumbs="SOP > Bakım",
        text=cand.text
    )
    assert reranked.rerank_rank == 1
    assert reranked.rank_delta == 3


# =====================================================================
# 2. Cross-Encoder Çapraz Puanlama Testleri
# =====================================================================

def test_cross_encoder_scoring_relevance():
    reranker = CrossEncoderReranker()
    q = "E-401 ana tahrik motoru arıza kodu"

    cand_relevant = CandidateChunk(
        chunk_id="c_rel",
        doc_id="d1",
        first_stage_rank=2,
        first_stage_score=0.6,
        source="Dokuma SOP",
        section="Arıza Kodları",
        breadcrumbs="SOP",
        text="E-401 arıza kodu ana tahrik motoru aşırı ısınması durumunda verilir."
    )

    cand_irrelevant = CandidateChunk(
        chunk_id="c_irrel",
        doc_id="d2",
        first_stage_rank=1,
        first_stage_score=0.7,
        source="Terbiye Kılavuzu",
        section="Overlok",
        breadcrumbs="Terbiye",
        text="Overlok dikişinde poliamid iplik mukavemeti 45 newton olmalıdır."
    )

    score_rel = reranker.compute_cross_score(q, cand_relevant)
    score_irrel = reranker.compute_cross_score(q, cand_irrelevant)

    assert score_rel > score_irrel
    assert score_rel >= 0.50
    assert score_irrel <= 0.30


def test_cross_encoder_rerank_ordering():
    reranker = CrossEncoderReranker()
    q = "E-256 çözgü çerçeve kilit mekanizması basıncı"

    # İlk aşamada alakasız parça 1. sırada, hedef parça 3. sırada olsun
    c1_irrel = CandidateChunk(
        chunk_id="c1",
        doc_id="d1",
        first_stage_rank=1,
        first_stage_score=0.8,
        source="SOP",
        section="Genel",
        breadcrumbs="SOP",
        text="Vardiya başlangıcında acil stop butonu kontrol edilir."
    )
    c2_med = CandidateChunk(
        chunk_id="c2",
        doc_id="d2",
        first_stage_rank=2,
        first_stage_score=0.75,
        source="SOP",
        section="Genel",
        breadcrumbs="SOP",
        text="Dokuma tezgâhında hava basıncı kontrolü yapılır."
    )
    c3_target = CandidateChunk(
        chunk_id="c3",
        doc_id="d3",
        first_stage_rank=3,
        first_stage_score=0.70,
        source="SOP",
        section="Arızalar",
        breadcrumbs="SOP",
        text="E-256 arıza kodu: Çözgü çerçeve kilit mekanizması basıncı 6 bar altına düşerse stop eder."
    )

    reranked, latency = reranker.rerank(q, [c1_irrel, c2_med, c3_target], top_k=2)

    assert len(reranked) == 2
    # Hedef parça 1. sıraya çıkmalı
    assert reranked[0].chunk_id == "c3"
    assert reranked[0].rerank_rank == 1
    assert reranked[0].first_stage_rank == 3
    assert reranked[0].rank_delta == 2  # 3 - 1 = 2 basamak yükseldi!
    assert latency >= 0.0


# =====================================================================
# 3. Context Sıkıştırma ve Maliyet Analizörü Testleri
# =====================================================================

def test_cost_latency_analyzer_compression():
    analyzer = CostLatencyAnalyzer()

    candidates = [
        CandidateChunk(chunk_id=f"c{i}", doc_id="d", first_stage_rank=i, first_stage_score=0.5,
                       source="S", section="S", breadcrumbs="S", text="Bu doküman halı fabrikası ile ilgili " * 20)
        for i in range(1, 11)
    ]
    reranked = [
        RerankedChunk(chunk_id=f"c{i}", doc_id="d", first_stage_rank=i, rerank_rank=i, rerank_score=0.8,
                      rank_delta=0, source="S", section="S", breadcrumbs="S", text=candidates[i-1].text)
        for i in range(1, 4)
    ]

    comp = analyzer.analyze_compression(candidates, reranked)

    assert comp.raw_tokens > comp.compressed_tokens
    assert comp.tokens_saved > 0
    # 10 parçadan 3 parçaya düşüş ≈ %70 sıkıştırma
    assert 0.65 <= comp.compression_ratio <= 0.75

    profile = analyzer.analyze_cost_and_latency(comp, reranker_overhead_ms=25.0)

    assert profile.cost_saving_usd > 0
    assert profile.cost_saving_percent >= 65.0
    assert profile.raw_llm_latency_ms > profile.reranked_llm_latency_ms
    # Net gecikme kazancı (TTFT tasarrufu) pozitif olmalı
    assert profile.latency_delta_ms > 0


# =====================================================================
# 4. İki Aşamalı Pipeline Entegrasyon Testleri (Real Chunks)
# =====================================================================

def test_two_stage_pipeline_real_retrieval():
    docs_dir = Path("day31/mini_project/fixtures/documents")
    assert docs_dir.exists()

    km = KnowledgeManager(documents_dir=str(docs_dir))
    km.sync()
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )

    pipeline = TwoStageRetriever(
        hybrid_retriever=hybrid,
        chunk_lookup=chunk_lookup,
        default_k1=10,
        default_k2=3
    )

    query = "E-401 ana tahrik motoru aşırı ısınma ve akım uyarısı"
    res = pipeline.retrieve(query=query, k1=10, k2=3)

    assert res.k1_candidates_count >= 5
    assert res.k2_selected_count == 3
    assert len(res.reranked_items) == 3

    # Top-1 parça E-401'i içeren DOC_MERINOS_WEAVING_SOP_c004 olmalı
    assert res.reranked_items[0].chunk_id == "DOC_MERINOS_WEAVING_SOP_c004"
    assert res.compression.compression_ratio >= 0.50
    assert res.total_latency_ms > 0


# =====================================================================
# 5. Uçtan Uca Rerank Benchmark Testi (15 Altın Sorgu)
# =====================================================================

def test_end_to_end_rerank_benchmark():
    docs_dir = Path("day31/mini_project/fixtures/documents")
    queries_path = Path("day34/mini_project/fixtures/rerank_benchmark_queries.json")

    assert docs_dir.exists()
    assert queries_path.exists()

    km = KnowledgeManager(documents_dir=str(docs_dir))
    km.sync()
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )

    pipeline = TwoStageRetriever(
        hybrid_retriever=hybrid,
        chunk_lookup=chunk_lookup,
        default_k1=10,
        default_k2=3
    )

    with open(queries_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    assert len(queries_data) == 15

    rerank_top1_count = 0
    valid_domain_count = 0

    for q in queries_data:
        qtext = q["query"]
        target = q.get("target_chunk_id")

        res = pipeline.retrieve(query=qtext, k1=10, k2=3)

        if target is not None:
            valid_domain_count += 1
            if res.reranked_items and res.reranked_items[0].chunk_id == target:
                rerank_top1_count += 1

    assert valid_domain_count == 14
    # Cross-Encoder ile 14 geçerli sorgunun en az %90'ı 1. sırada yakalanmalı
    rerank_hit1_rate = rerank_top1_count / valid_domain_count
    assert rerank_hit1_rate >= 0.90
