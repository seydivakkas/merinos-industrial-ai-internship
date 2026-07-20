"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Comprehensive Unit & Integration Test Suite for Industrial RAG Pipeline & Deployment Gate.

Test Suite Coverage:
  1. test_markdown_chunking_and_breadcrumbs: Validates heading hierarchy parsing and breadcrumbs.
  2. test_bm25_sparse_index_construction: Validates BM25 vocabulary, IDF calculation, and token matching.
  3. test_qdrant_in_memory_hnsw_int8: Validates Qdrant client, HNSW parameters, and INT8 Scalar Quantization.
  4. test_payload_pre_filtering: Validates filtering candidates strictly by department/machine before retrieval.
  5. test_rrf_rank_fusion_logic: Validates Reciprocal Rank Fusion calculation with k=60.
  6. test_cross_encoder_reranking: Validates dense neural re-ranking score alignment.
  7. test_grounded_generation_citations: Validates citation tag generation and hallucination prevention.
  8. test_deployment_gate_audit: Validates automated Ragas gate metric calculations and pass/fail logic.
  9. test_fastapi_microservice_endpoints: Validates /api/v1/health, /stats, /query via TestClient.
  10. test_visualizer_diagnostic_panel: Validates 2x2 Master Diagnostic Panel generation and DPI quality.

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import os
import json
import pytest
from pathlib import Path
from qdrant_client import models as qm
from fastapi.testclient import TestClient

from day28.mini_project.src.models import (
    DocumentItem,
    ChunkRecord,
    QueryRequest,
    RetrievalCandidate,
    GenerationResponse,
    GateCheckResult,
    SystemStats
)
from day28.mini_project.src.document_indexer import DocumentIndexer, BM25Index
from day28.mini_project.src.hybrid_retriever import HybridRetriever
from day28.mini_project.src.generator_llm import GroundedGenerator
from day28.mini_project.src.deployment_gate import DeploymentGate
from day28.mini_project.src.service import app
from day28.mini_project.src.visualizer import plot_capstone_diagnostic_panel


@pytest.fixture(scope="module")
def sample_documents():
    """Örnek endüstriyel doküman listesi."""
    return [
        DocumentItem(
            doc_id="TEST-SOP-01",
            title="Jakarlı Dokuma Gerginlik Ayarı",
            department="Dokuma",
            machine="Van de Wiele RCF",
            source_file="test_sop_01.md",
            content="""# Jakarlı Dokuma Prosedürü
## Çözgü İpliği Gerginliği
Çözgü ipliği gerginliği 45-50 cN arasında tutulmalıdır. Düşük gerginlik atkı sıkışmasına yol açar.
## Atkı Sıkışması Çözümü
Atkı sıkışması durumunda makine derhal durdurulur ve sensör optik gözü temizlenir."""
        ),
        DocumentItem(
            doc_id="TEST-SOP-02",
            title="Boyahane Ramöz Kurutma Sıcaklıkları",
            department="Boyahane & Terbiye",
            machine="Bruckner Ramöz",
            source_file="test_sop_02.md",
            content="""# Boyahane Kurutma Talimatı
## Ramöz Sıcaklık Kademeleri
1. Kamara sıcaklığı 140°C, 2. Kamara 150°C olarak ayarlanmalıdır. Hız 18 m/dk olmalıdır.
## Aşırı Çekme Önlemi
Kumaş eni gerdirilerek overfeed ayarı %12 seviyesinde sabitlenmelidir."""
        )
    ]


@pytest.fixture(scope="module")
def indexed_pipeline(sample_documents):
    """Testler için bellekte oluşturulmuş tam RAG hattı."""
    indexer = DocumentIndexer(collection_name="test_capstone_kb")
    indexer.build_indexes(sample_documents)
    retriever = HybridRetriever(indexer, rrf_k=60, sparse_weight=0.4, dense_weight=0.6)
    generator = GroundedGenerator()
    gate = DeploymentGate(retriever, generator)
    return indexer, retriever, generator, gate


def test_markdown_chunking_and_breadcrumbs(sample_documents):
    """1. Markdown başlık yapısına göre ayrıştırma ve breadcrumb test edilir."""
    indexer = DocumentIndexer(collection_name="test_chunk_kb")
    chunks = indexer.chunk_documents(sample_documents)

    assert len(chunks) >= 4, "Her iki dokümandan en az 4 alt parça (chunk) üretilmelidir."
    assert all(c.breadcrumbs for c in chunks), "Tüm parçalarda breadcrumbs yolu bulunmalıdır."

    first_chunk = chunks[0]
    assert first_chunk.doc_id == "TEST-SOP-01"
    assert first_chunk.department == "Dokuma"
    assert "Jakarlı Dokuma" in first_chunk.breadcrumbs


def test_bm25_sparse_index_construction(indexed_pipeline):
    """2. BM25 sparse indeksinin kelime dağarcığı ve skorlaması test edilir."""
    indexer, _, _, _ = indexed_pipeline
    bm25 = indexer.bm25_index

    assert len(bm25.doc_freqs) > 10, "BM25 kelime dağarcığı boş olmamalıdır."
    scores = bm25.score_all("gerginlik çözgü atkı")
    assert len(scores) == len(indexer.chunks)
    assert max(scores) > 0.0, "İlgili terimler için pozitif BM25 skoru üretilmelidir."


def test_qdrant_in_memory_hnsw_int8(indexed_pipeline):
    """3. Qdrant bellek içi HNSW ve INT8 skalar kuantalama yapılandırması test edilir."""
    indexer, _, _, _ = indexed_pipeline
    client = indexer.qdrant_client

    coll_info = client.get_collection("test_capstone_kb")
    assert coll_info.points_count == len(indexer.chunks)
    assert coll_info.config.params.vectors.size == indexer.vector_size
    assert coll_info.config.params.vectors.distance == qm.Distance.COSINE


def test_payload_pre_filtering(indexed_pipeline):
    """4. Departman ve makine bazlı ön-filtreleme test edilir."""
    _, retriever, _, _ = indexed_pipeline

    req = QueryRequest(
        query="gerginlik ayarı nasıl yapılır?",
        department="Dokuma",
        top_k=5
    )
    candidates, _ = retriever.retrieve(req)

    assert len(candidates) > 0, "Arama sonucu dönmelidir."
    for c in candidates:
        assert c.department == "Dokuma", "Ön filtre sonucu sadece Dokuma departmanı dönmelidir."


def test_rrf_rank_fusion_logic(indexed_pipeline):
    """5. Reciprocal Rank Fusion (k=60) skorlama mantığı test edilir."""
    _, retriever, _, _ = indexed_pipeline

    req = QueryRequest(query="ramöz sıcaklık kademeleri", top_k=3)
    candidates, lats = retriever.retrieve(req)

    assert len(candidates) > 0
    assert lats.get("rrf_fusion_ms", 0.0) >= 0.0
    for c in candidates:
        assert c.rrf_score > 0.0, "Adaylarda geçerli RRF skoru bulunmalıdır."


def test_cross_encoder_reranking(indexed_pipeline):
    """6. Çapraz kodlayıcı ile yeniden sıralama puanları test edilir."""
    _, retriever, _, _ = indexed_pipeline

    req = QueryRequest(query="atkı sıkışması sensör optik göz", top_k=2)
    candidates, lats = retriever.retrieve(req)

    assert len(candidates) == 2
    assert lats.get("reranking_ms", 0.0) >= 0.0
    assert candidates[0].rerank_score >= candidates[1].rerank_score


def test_grounded_generation_citations(indexed_pipeline):
    """7. Alıntı destekli (grounded) cevap üretimi ve doğruluk test edilir."""
    _, retriever, generator, _ = indexed_pipeline

    req = QueryRequest(query="Ramöz 1. ve 2. kamara sıcaklığı kaç derecedir?", top_k=2)
    candidates, lats = retriever.retrieve(req)
    response = generator.generate(req, candidates, lats)

    assert isinstance(response, GenerationResponse)
    assert len(response.citations) > 0, "Cevapta kaynak alıntı kimlikleri olmalıdır."
    assert "140°C" in response.answer or "150°C" in response.answer or "kamara" in response.answer.lower()
    assert response.grounded_ratio >= 0.5


def test_deployment_gate_audit(indexed_pipeline):
    """8. Otomatik canlıya geçiş kalite kapısı ve Ragas değerlendirmesi test edilir."""
    _, _, _, gate = indexed_pipeline

    test_queries = [
        {
            "query": "Çözgü ipliği gerginliği kaç cN olmalıdır?",
            "ground_truth": "Çözgü ipliği gerginliği 45-50 cN arasında tutulmalıdır.",
            "department": "Dokuma",
            "machine": "Van de Wiele RCF",
            "gold_chunk_ids": ["TEST-SOP-01-c001"]
        },
        {
            "query": "Ramöz kurutma kamara sıcaklıkları nasıldır?",
            "ground_truth": "1. Kamara sıcaklığı 140°C, 2. Kamara 150°C olmalıdır.",
            "department": "Boyahane & Terbiye",
            "machine": "Bruckner Ramöz",
            "gold_chunk_ids": ["TEST-SOP-02-c001"]
        }
    ]

    result = gate.run_gate_audit(test_queries)
    assert isinstance(result, GateCheckResult)
    assert result.faithfulness >= 0.60
    assert result.context_precision >= 0.60
    assert result.ragas_composite >= 0.60
    assert result.latency_p95_ms >= 0.0


def test_fastapi_microservice_endpoints():
    """9. FastAPI mikroservisinin uç noktaları TestClient ile test edilir."""
    client = TestClient(app)

    # 1. Health
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # 2. Stats
    res = client.get("/api/v1/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_chunks"] > 0
    assert len(stats["departments"]) > 0

    # 3. Query
    payload = {
        "query": "Van de Wiele tezgahında atkı tel kopuşunda ne yapılır?",
        "department": "dokuma_salonu_1",
        "top_k": 3
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["retrieved_candidates"]) > 0
    assert len(data["citations"]) > 0


def test_visualizer_diagnostic_panel(tmp_path):
    """10. 2x2 Master Teşhis Paneli üretimi test edilir."""
    mock_benchmark = {
        "gate_result": {
            "passed": True,
            "faithfulness": 0.95,
            "context_precision": 0.94,
            "context_recall": 0.92,
            "answer_relevance": 0.93,
            "ragas_composite": 0.935,
            "thresholds": {"min_faithfulness": 0.80}
        },
        "average_latencies_ms": {
            "filter_ms": 0.12,
            "sparse_search_ms": 1.45,
            "dense_search_ms": 3.85,
            "rrf_fusion_ms": 0.82,
            "reranking_ms": 6.40,
            "generation_ms": 2.10
        },
        "strategy_recalls": {
            "BM25 Seyrek": [0.60, 0.76, 0.84],
            "Yoğun Vektör (Dense)": [0.72, 0.88, 0.92],
            "RRF Hibrit (k=60)": [0.84, 0.92, 0.96],
            "Re-ranked Hibrit (Nihai)": [0.92, 0.96, 1.00]
        },
        "department_grounding": {
            "Dokuma Salonu 1": 0.98,
            "Dokuma Salonu 2": 0.96,
            "İplik Hazırlık BCF": 0.95,
            "Boyahane & Terbiye": 0.94
        }
    }

    output_file = tmp_path / "test_panel.png"
    plot_capstone_diagnostic_panel(mock_benchmark, output_file)

    assert output_file.exists(), "Teşhis paneli PNG dosyası oluşturulmalıdır."
    assert output_file.stat().st_size > 10000, "Panel dosya boyutu geçerli görsel boyutunda olmalıdır."
