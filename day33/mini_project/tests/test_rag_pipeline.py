# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Unit & Integration Tests: RAG Generation, Context Builder, Citation Verifier, Error Separation
"""

import pytest
import json
from pathlib import Path

from day31.mini_project.src.models import ChunkRecord
from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day33.mini_project.src.models import (
    SourceChunk,
    RAGContext,
    Claim,
    RAGResponse
)
from day33.mini_project.src.context_builder import ContextBuilder
from day33.mini_project.src.citation_verifier import (
    CitationVerifier,
    split_into_claims,
    extract_technical_keywords
)
from day33.mini_project.src.rag_generator import RAGGenerator, REFUSAL_MESSAGE
from day33.mini_project.src.error_classifier import RAGErrorClassifier


# =====================================================================
# 1. Context Builder Testleri
# =====================================================================

def test_context_builder_source_id_formatting():
    builder = ContextBuilder(top_k=2, id_prefix="S")
    dummy_chunk_1 = ChunkRecord(
        chunk_id="c001",
        doc_id="doc_sop",
        title="Dokuma SOP",
        source="sop.pdf",
        page_number=1,
        section="Arıza Kodları",
        breadcrumbs="SOP > Arızalar",
        text="E-401 ana tahrik motoru aşırı ısınmasıdır.",
        char_count=45,
        token_estimate=11,
        chunk_strategy="semantic"
    )
    dummy_chunk_2 = ChunkRecord(
        chunk_id="c002",
        doc_id="doc_quality",
        title="Kalite Standardı",
        source="kalite.docx",
        page_number=1,
        section="Tansiyon",
        breadcrumbs="Kalite > İplik",
        text="İplik tansiyonu 14 bar altına düşmemelidir.",
        char_count=43,
        token_estimate=10,
        chunk_strategy="semantic"
    )
    chunk_lookup = {"c001": dummy_chunk_1, "c002": dummy_chunk_2}
    retrieved = [
        type("Item", (), {"chunk_id": "c001", "score": 0.95, "rank": 1})(),
        type("Item", (), {"chunk_id": "c002", "score": 0.88, "rank": 2})()
    ]

    ctx = builder.build_context(retrieved, chunk_lookup)

    assert len(ctx.sources) == 2
    assert ctx.sources[0].source_id == "S1"
    assert ctx.sources[0].chunk_id == "c001"
    assert ctx.sources[1].source_id == "S2"
    assert ctx.sources[1].chunk_id == "c002"
    assert "[S1] Doküman: sop.pdf" in ctx.formatted_text
    assert "[S2] Doküman: kalite.docx" in ctx.formatted_text
    assert ctx.total_tokens_estimate > 0


# =====================================================================
# 2. İddia ve Atıf Ayrıştırma (Claim Extraction) Testleri
# =====================================================================

def test_split_into_claims_and_citations():
    raw_answer = (
        "E-401 arızasında acil durdurma butonuna basılmalıdır [S1]. "
        "Motor fanı temizlenmelidir [s1]. "
        "Basınç 14 bar seviyesine ayarlanmalıdır [S2]."
    )
    claims = split_into_claims(raw_answer)

    assert len(claims) == 3
    assert claims[0].cited_source_ids == ["S1"]
    assert claims[0].is_cited is True
    assert claims[1].cited_source_ids == ["S1"]  # Küçük harf s1 büyük harf S1'e dönüştürülmeli
    assert claims[2].cited_source_ids == ["S2"]


def test_claim_without_citation():
    raw_answer = "Bu cümlenin hiçbir kaynak atfı yoktur."
    claims = split_into_claims(raw_answer)
    assert len(claims) == 1
    assert claims[0].is_cited is False
    assert claims[0].cited_source_ids == []


# =====================================================================
# 3. Citation Verifier (Faithfulness & Hallucination) Testleri
# =====================================================================

def test_citation_verifier_supported_claim():
    verifier = CitationVerifier(faithfulness_threshold=0.70)
    src_chunk = SourceChunk(
        source_id="S1",
        chunk_id="c1",
        doc_id="d1",
        title="Dokuma SOP",
        section="Arıza",
        breadcrumbs="SOP",
        text="E-401 arıza kodu ana tahrik motoru aşırı ısınması veya aşınması durumunda verilir.",
        rank=1,
        score=0.9
    )
    ctx = RAGContext(sources=[src_chunk], formatted_text=src_chunk.text)
    claim = Claim(
        claim_id=1,
        text="E-401 arıza kodu ana tahrik motoru aşırı ısınmasında aktifleşir [S1].",
        cited_source_ids=["S1"],
        is_cited=True
    )

    verifs, faith, prec, rec, hallu = verifier.verify_claims([claim], ctx)

    assert len(verifs) == 1
    assert verifs[0].status == "SUPPORTED"
    assert verifs[0].faithfulness_score >= 0.70
    assert hallu is False
    assert prec == 1.0


def test_citation_verifier_hallucination_detection():
    verifier = CitationVerifier(faithfulness_threshold=0.70)
    src_chunk = SourceChunk(
        source_id="S1",
        chunk_id="c1",
        doc_id="d1",
        title="Dokuma SOP",
        section="Arıza",
        breadcrumbs="SOP",
        text="E-401 arıza kodu ana tahrik motoru aşırı ısınması durumunda verilir.",
        rank=1,
        score=0.9
    )
    ctx = RAGContext(sources=[src_chunk], formatted_text=src_chunk.text)

    # Kasıtlı Uydurma / Halüsinasyon Cümlesi
    hallu_claim = Claim(
        claim_id=1,
        text="Operatör motor hidrolik yağını 120 santigrat derecede 50 bar basmalıdır [S1].",
        cited_source_ids=["S1"],
        is_cited=True
    )

    verifs, faith, prec, rec, hallu = verifier.verify_claims([hallu_claim], ctx)

    assert len(verifs) == 1
    assert verifs[0].status == "HALLUCINATION"
    assert verifs[0].faithfulness_score < 0.70
    assert hallu is True
    assert "hidrolik" in verifs[0].missing_keywords or "50" in verifs[0].missing_keywords


def test_citation_verifier_invalid_source_id():
    verifier = CitationVerifier(faithfulness_threshold=0.70)
    src_chunk = SourceChunk(
        source_id="S1",
        chunk_id="c1",
        doc_id="d1",
        title="SOP",
        section="A",
        breadcrumbs="B",
        text="Metin",
        rank=1,
        score=1.0
    )
    ctx = RAGContext(sources=[src_chunk], formatted_text="")
    # [S9] kaynak kimliği context'te yok
    invalid_claim = Claim(
        claim_id=1,
        text="Herhangi bir iddia [S9].",
        cited_source_ids=["S9"],
        is_cited=True
    )
    verifs, faith, prec, rec, hallu = verifier.verify_claims([invalid_claim], ctx)
    assert verifs[0].status == "INVALID_SOURCE_ID"
    assert hallu is True


# =====================================================================
# 4. Hata Sınıflandırıcı (Error Classifier) Testleri
# =====================================================================

def test_error_classifier_categories():
    classifier = RAGErrorClassifier(faithfulness_threshold=0.70)
    src_chunk = SourceChunk(
        source_id="S1",
        chunk_id="DOC_MERINOS_WEAVING_SOP_c004",
        doc_id="d1",
        title="SOP",
        section="Arıza",
        breadcrumbs="",
        text="E-401 motor",
        rank=1,
        score=1.0
    )
    ctx = RAGContext(sources=[src_chunk], formatted_text="")

    # A. Tam Başarı
    res_success = RAGResponse(
        query="E-401",
        raw_answer="E-401 motor arızası [S1].",
        cleaned_answer="E-401 motor arızası.",
        context=ctx,
        claims=[],
        is_refusal=False,
        overall_faithfulness=0.90,
        citation_precision=1.0,
        citation_recall=1.0,
        hallucination_detected=False,
        latency_ms=10.0
    )
    item_suc = classifier.classify_result("Q1", "E-401", "ERROR", "FAITHFUL_ANSWER", "DOC_MERINOS_WEAVING_SOP_c004", res_success)
    assert item_suc.error_type == "SUCCESS"

    # B. Retrieval Hatası (Hedef parça context'te yok)
    item_rf = classifier.classify_result("Q2", "Basınç", "QUALITY", "FAITHFUL_ANSWER", "TARGET_NOT_IN_CONTEXT", res_success)
    assert item_rf.error_type == "RETRIEVAL_FAILURE"

    # C. Generation / Halüsinasyon Hatası
    res_hallu = RAGResponse(
        query="E-401",
        raw_answer="Sahte cevap [S1].",
        cleaned_answer="Sahte cevap.",
        context=ctx,
        claims=[],
        is_refusal=False,
        overall_faithfulness=0.40,
        citation_precision=0.0,
        citation_recall=0.0,
        hallucination_detected=True,
        latency_ms=10.0
    )
    item_gh = classifier.classify_result("Q3", "E-401", "ERROR", "FAITHFUL_ANSWER", "DOC_MERINOS_WEAVING_SOP_c004", res_hallu)
    assert item_gh.error_type == "GENERATION_HALLUCINATION"

    # D. Doğru Reddetme (Correct Abstention)
    res_refusal = RAGResponse(
        query="yemekhane",
        raw_answer=REFUSAL_MESSAGE,
        cleaned_answer=REFUSAL_MESSAGE,
        context=ctx,
        claims=[],
        is_refusal=True,
        overall_faithfulness=1.0,
        citation_precision=1.0,
        citation_recall=1.0,
        hallucination_detected=False,
        latency_ms=5.0
    )
    item_ca = classifier.classify_result("Q4", "yemekhane", "OUT_OF_DOMAIN", "REFUSAL", None, res_refusal)
    assert item_ca.error_type == "CORRECT_ABSTENTION"


# =====================================================================
# 5. Uçtan Uca Entegrasyon Testi (Real Chunks & 15 Golden Queries)
# =====================================================================

def test_end_to_end_rag_benchmark():
    docs_dir = Path("day31/mini_project/fixtures/documents")
    queries_path = Path("day33/mini_project/fixtures/rag_evaluation_queries.json")

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
    generator = RAGGenerator(faithfulness_threshold=0.70, top_k=3)
    classifier = RAGErrorClassifier(faithfulness_threshold=0.70)

    with open(queries_path, "r", encoding="utf-8") as f:
        test_queries = json.load(f)

    assert len(test_queries) == 15

    successes = 0
    abstentions = 0

    for q in test_queries:
        qid = q["id"]
        qtext = q["query"]
        cat = q["category"]
        exp_beh = q["expected_behavior"]
        target_chunk = q.get("target_chunk_id")

        # Hibrit Arama
        ret_res = hybrid.search(qtext, method="linear", top_k=3, alpha=0.5)

        # RAG Cevaplama ve Doğrulama
        rag_res = generator.generate_answer(
            query=qtext,
            retrieved_items=ret_res.items,
            chunk_lookup=chunk_lookup
        )

        item = classifier.classify_result(
            query_id=qid,
            query=qtext,
            category=cat,
            expected_behavior=exp_beh,
            target_chunk_id=target_chunk,
            rag_response=rag_res
        )

        if item.error_type == "SUCCESS":
            successes += 1
            assert rag_res.overall_faithfulness >= 0.70
            assert not rag_res.hallucination_detected
            assert len(rag_res.claims) > 0
        elif item.error_type == "CORRECT_ABSTENTION":
            abstentions += 1
            assert rag_res.is_refusal is True

    # 14 geçerli sorgu başarıyla cevaplanmalı, 1 negatif sorgu reddedilmeli
    assert successes == 14
    assert abstentions == 1
