# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Transformed Retriever: Raw, Rewritten, Multi-Query ve HyDE Yöntemlerini Yöneten Birleşik Getirici
"""

import time
from typing import List, Dict, Tuple, Optional, Any
from day31.mini_project.src.models import ChunkRecord
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day35.mini_project.src.models import (
    TransformedQuery,
    MethodResult
)
from day35.mini_project.src.query_rewriter import QueryRewriter
from day35.mini_project.src.multi_query_expander import MultiQueryExpander
from day35.mini_project.src.hyde_generator import HyDEGenerator


class TransformedRetriever:
    """
    Operatör sorgularını farklı dönüşümlerle zenginleştirip
    arama başarımını karşılaştıran ve RRF ile birleştiren orkestratör.
    """

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        chunk_lookup: Dict[str, ChunkRecord],
        rewriter: Optional[QueryRewriter] = None,
        expander: Optional[MultiQueryExpander] = None,
        hyde: Optional[HyDEGenerator] = None,
        rrf_k: int = 60
    ):
        self.hybrid_retriever = hybrid_retriever
        self.chunk_lookup = chunk_lookup
        self.rewriter = rewriter or QueryRewriter()
        self.expander = expander or MultiQueryExpander()
        self.hyde = hyde or HyDEGenerator()
        self.rrf_k = rrf_k

    def transform_query(self, query: str) -> TransformedQuery:
        """Sorgunun tüm dönüştürülmüş temsillerini hazırlar."""
        rewritten = self.rewriter.rewrite(query)
        sub_queries = self.expander.expand(query)
        hypothetical = self.hyde.generate_hypothetical_document(query)

        return TransformedQuery(
            raw_query=query,
            rewritten_query=rewritten,
            sub_queries=sub_queries,
            hypothetical_doc=hypothetical
        )

    def search_raw(self, query: str, top_k: int = 5) -> MethodResult:
        """Ham sorgu ile doğrudan hibrit arama."""
        t0 = time.perf_counter()
        res = self.hybrid_retriever.search(query, method="linear", top_k=top_k, alpha=0.5)
        dt = (time.perf_counter() - t0) * 1000.0
        chunk_ids = [it.chunk_id for it in res.items]
        return MethodResult(method_name="RAW", retrieved_chunk_ids=chunk_ids, latency_ms=round(dt, 2))

    def search_rewritten(self, query: str, top_k: int = 5) -> MethodResult:
        """Yeniden yazılmış resmi sorgu ile hibrit arama."""
        t0 = time.perf_counter()
        rewritten = self.rewriter.rewrite(query)
        res = self.hybrid_retriever.search(rewritten, method="linear", top_k=top_k, alpha=0.5)
        dt = (time.perf_counter() - t0) * 1000.0
        chunk_ids = [it.chunk_id for it in res.items]
        return MethodResult(method_name="REWRITE", retrieved_chunk_ids=chunk_ids, latency_ms=round(dt, 2))

    def search_multi_query(self, query: str, top_k: int = 5) -> MethodResult:
        """Çoklu perspektif sorguları bağımsız aratıp RRF ile birleştirir."""
        t0 = time.perf_counter()
        sub_queries = self.expander.expand(query)

        rrf_scores: Dict[str, float] = {}
        for sub_q in sub_queries:
            res = self.hybrid_retriever.search(sub_q, method="linear", top_k=top_k * 2, alpha=0.5)
            for it in res.items:
                rrf_scores[it.chunk_id] = rrf_scores.get(it.chunk_id, 0.0) + (1.0 / (self.rrf_k + it.rank))

        sorted_chunks = sorted(rrf_scores.keys(), key=lambda c: rrf_scores[c], reverse=True)[:top_k]
        dt = (time.perf_counter() - t0) * 1000.0
        return MethodResult(method_name="MULTI_QUERY", retrieved_chunk_ids=sorted_chunks, latency_ms=round(dt, 2))

    def search_hyde(self, query: str, top_k: int = 5) -> MethodResult:
        """Hipotetik SOP dokümanı ile doküman uzayında simetrik arama."""
        t0 = time.perf_counter()
        hypo_doc = self.hyde.generate_hypothetical_document(query)
        res = self.hybrid_retriever.search(hypo_doc, method="linear", top_k=top_k, alpha=0.5)
        dt = (time.perf_counter() - t0) * 1000.0
        chunk_ids = [it.chunk_id for it in res.items]
        return MethodResult(method_name="HYDE", retrieved_chunk_ids=chunk_ids, latency_ms=round(dt, 2))

    def search_fused(self, query: str, top_k: int = 5) -> MethodResult:
        """Tüm yöntemlerin (Raw, Rewrite, MultiQuery, HyDE) çıktılarını RRF ile birleştirir."""
        t0 = time.perf_counter()

        m_raw = self.search_raw(query, top_k=top_k * 2)
        m_rewrite = self.search_rewritten(query, top_k=top_k * 2)
        m_multi = self.search_multi_query(query, top_k=top_k * 2)
        m_hyde = self.search_hyde(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        for method_res in [m_raw, m_rewrite, m_multi, m_hyde]:
            for rank_idx, chunk_id in enumerate(method_res.retrieved_chunk_ids, start=1):
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank_idx))

        sorted_chunks = sorted(rrf_scores.keys(), key=lambda c: rrf_scores[c], reverse=True)[:top_k]
        dt = (time.perf_counter() - t0) * 1000.0
        return MethodResult(method_name="RRF_FUSED", retrieved_chunk_ids=sorted_chunks, latency_ms=round(dt, 2))
