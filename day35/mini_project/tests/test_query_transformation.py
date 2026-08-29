# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Birim ve Entegrasyon Testleri: Query Transformation, HyDE ve Çoklu Sorgu Genişletmesi
"""

import json
from pathlib import Path
import pytest

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day35.mini_project.src.models import (
    TransformedQuery,
    MethodResult,
    QueryTransformBenchmarkItem,
    QueryTransformBenchmarkReport
)
from day35.mini_project.src.query_rewriter import QueryRewriter
from day35.mini_project.src.multi_query_expander import MultiQueryExpander
from day35.mini_project.src.hyde_generator import HyDEGenerator
from day35.mini_project.src.transformed_retriever import TransformedRetriever


# =====================================================================
# 1. Veri Modelleri Doğrulama Testi
# =====================================================================

def test_models_instantiation_and_serialization():
    tq = TransformedQuery(
        raw_query="motor cok sıcak durdu napcam",
        rewritten_query="Ana tahrik motoru aşırı ısınması acil müdahale talimatı",
        sub_queries=["motor sıcaklık arızası", "E-401 hata kodu", "soğutma fanı kontrolü"],
        hypothetical_doc="MERİNOS SOP: Motor aşırı ısındığında soğutma fanı ve filtre kontrol edilmelidir."
    )
    assert tq.raw_query.startswith("motor")
    assert len(tq.sub_queries) == 3

    m_res = MethodResult(
        method_name="HYDE",
        retrieved_chunk_ids=["c001", "c002"],
        latency_ms=12.4
    )
    assert m_res.method_name == "HYDE"
    assert len(m_res.retrieved_chunk_ids) == 2

    item = QueryTransformBenchmarkItem(
        query_id="Q01",
        noisy_query="motor sıcak",
        category="MAINTENANCE_SOP",
        target_chunk_id="c001",
        raw_rank=4,
        rewrite_rank=2,
        multi_query_rank=2,
        hyde_rank=1,
        fused_rank=1,
        rank_improved=True,
        best_method="HYDE"
    )
    assert item.rank_improved is True
    assert item.best_method == "HYDE"

    rep = QueryTransformBenchmarkReport(
        timestamp="2026-09-06T10:00:00",
        total_queries=1,
        valid_domain_queries=1,
        raw_hit1_rate=0.0,
        rewrite_hit1_rate=0.0,
        multi_query_hit1_rate=0.0,
        hyde_hit1_rate=1.0,
        fused_hit1_rate=1.0,
        raw_mrr=0.25,
        rewrite_mrr=0.5,
        multi_query_mrr=0.5,
        hyde_mrr=1.0,
        fused_mrr=1.0,
        mrr_gain_hyde=0.75,
        mrr_gain_fused=0.75,
        avg_raw_latency_ms=8.5,
        avg_fused_latency_ms=35.2,
        items=[item]
    )
    data = json.loads(rep.model_dump_json())
    assert data["hyde_mrr"] == 1.0


# =====================================================================
# 2. Query Rewriter: Argo & İmla Düzeltme Testi
# =====================================================================

def test_query_rewriter_slang_normalization():
    rewriter = QueryRewriter()

    noisy_q1 = "motor cok sıcak durdu napcam"
    rewritten_q1 = rewriter.rewrite(noisy_q1)
    assert "tahrik motoru" in rewritten_q1 or "aşırı ısınma" in rewritten_q1 or "operatör müdahale" in rewritten_q1

    noisy_q2 = "cerceve kilit basinc dustu durdu kod ne"
    rewritten_q2 = rewriter.rewrite(noisy_q2)
    assert "çerçeve kilit basıncı" in rewritten_q2 or "E-256" in rewritten_q2

    noisy_q3 = "sarı lamba yanıyo tezgah yavasladı neden"
    rewritten_q3 = rewriter.rewrite(noisy_q3)
    assert "sarı ikaz lambası" in rewritten_q3 or "tarak boşluğu" in rewritten_q3


# =====================================================================
# 3. Multi-Query Expander: Farklı Mühendislik Boyutları Testi
# =====================================================================

def test_multi_query_expander_perspectives():
    expander = MultiQueryExpander()

    sub_queries = expander.expand("iplik koptu hangi vana basınç kaçtı")
    assert len(sub_queries) >= 2
    combined_text = " ".join(sub_queries).lower()
    assert "tansiyon" in combined_text or "basınç" in combined_text or "kopuş" in combined_text


# =====================================================================
# 4. HyDE Generator: Doküman Tipi Varsayımsal Üretim Testi
# =====================================================================

def test_hyde_generator_sop_format():
    hyde = HyDEGenerator()

    hypo_doc = hyde.generate_hypothetical_document("mekik iplik rezerv bos arıza kodu")
    assert "MERİNOS" in hypo_doc or "SOP" in hypo_doc or "STANDART İŞLETİM PROSEDÜRÜ" in hypo_doc
    assert "E-108" in hypo_doc or "rezerv" in hypo_doc or "sensör" in hypo_doc
    assert len(hypo_doc) > 80


# =====================================================================
# 5. Transformed Retriever Orkestrasyonu Testi
# =====================================================================

@pytest.fixture(scope="module")
def transformed_retriever_instance():
    docs_dir = "day31/mini_project/fixtures/documents"
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )
    chunk_lookup = {c.chunk_id: c for c in km.chunks}

    return TransformedRetriever(
        hybrid_retriever=hybrid,
        chunk_lookup=chunk_lookup,
        rewriter=QueryRewriter(),
        expander=MultiQueryExpander(),
        hyde=HyDEGenerator(),
        rrf_k=60
    )


def test_transformed_retriever_methods(transformed_retriever_instance):
    tr = transformed_retriever_instance
    query = "motor cok sıcak durdu napcam"

    # 1. Transform Query object check
    tq = tr.transform_query(query)
    assert tq.raw_query == query
    assert len(tq.sub_queries) >= 2
    assert len(tq.hypothetical_doc) > 50

    # 2. Search methods return valid results
    res_raw = tr.search_raw(query, top_k=5)
    assert res_raw.method_name == "RAW"
    assert len(res_raw.retrieved_chunk_ids) > 0
    assert res_raw.latency_ms >= 0

    res_rewr = tr.search_rewritten(query, top_k=5)
    assert res_rewr.method_name == "REWRITE"
    assert len(res_rewr.retrieved_chunk_ids) > 0

    res_multi = tr.search_multi_query(query, top_k=5)
    assert res_multi.method_name == "MULTI_QUERY"
    assert len(res_multi.retrieved_chunk_ids) > 0

    res_hyde = tr.search_hyde(query, top_k=5)
    assert res_hyde.method_name == "HYDE"
    assert len(res_hyde.retrieved_chunk_ids) > 0

    res_fused = tr.search_fused(query, top_k=5)
    assert res_fused.method_name == "RRF_FUSED"
    assert len(res_fused.retrieved_chunk_ids) > 0


# =====================================================================
# 6. End-to-End Benchmark Doğrulaması: HyDE / Fused Başarımı
# =====================================================================

def test_end_to_end_noisy_benchmark(transformed_retriever_instance):
    tr = transformed_retriever_instance
    fixtures_path = Path("day35/mini_project/fixtures/noisy_operator_queries.json")
    assert fixtures_path.exists()

    with open(fixtures_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    assert len(queries) >= 10

    # Test top 5 queries to verify ranking
    for q in queries[:5]:
        qtext = q["noisy_query"]
        target = q["target_chunk_id"]

        m_fused = tr.search_fused(qtext, top_k=5)
        # Verify the retriever returns non-empty result
        assert len(m_fused.retrieved_chunk_ids) > 0
        # Check target chunk retrieved within top 5
        assert target in m_fused.retrieved_chunk_ids, f"Target {target} not found in top 5 for query '{qtext}'"
