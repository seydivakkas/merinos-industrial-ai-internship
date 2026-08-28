# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Two-Stage Pipeline: Hibrit Getirme (First-Stage) ve Cross-Encoder Reranking (Second-Stage) Birleşik Hattı
Şekil 67 ile %100 birebir hizalı sınıf yapısı, constructor ve retrieve metodu
"""

import time
from typing import List, Dict, Any, Optional
from day31.mini_project.src.models import ChunkRecord
from day34.mini_project.src.models import (
    Document,
    SearchResult,
    CandidateChunk,
    RerankedChunk,
    TwoStageRetrievalResult
)
from day34.mini_project.src.cross_encoder_reranker import CrossEncoderReranker
from day34.mini_project.src.cost_latency_analyzer import CostLatencyAnalyzer


class TwoStageRetriever:
    """
    İki aşamalı arama:
    1. İlk aşama: vektör tabanlı retrieval (k1)
    2. İkinci aşama: cross-encoder ile yeniden sıralama (k2)
    """

    def __init__(
        self,
        retriever=None,
        reranker: Optional[CrossEncoderReranker] = None,
        k1: int = 10,
        k2: int = 3,
        hybrid_retriever=None,
        chunk_lookup: Optional[Dict[str, ChunkRecord]] = None,
        analyzer: Optional[CostLatencyAnalyzer] = None,
        default_k1: Optional[int] = None,
        default_k2: Optional[int] = None
    ):
        self.retriever = retriever or hybrid_retriever
        self.hybrid_retriever = self.retriever
        self.reranker = reranker or CrossEncoderReranker()
        self.k1 = default_k1 if default_k1 is not None else k1
        self.k2 = default_k2 if default_k2 is not None else k2
        self.default_k1 = self.k1
        self.default_k2 = self.k2
        self.chunk_lookup = chunk_lookup or {}
        self.analyzer = analyzer or CostLatencyAnalyzer()

    def retrieve(
        self,
        query: str,
        k1: Optional[int] = None,
        k2: Optional[int] = None,
        method: str = "linear",
        alpha: float = 0.5
    ) -> Any:
        """
        İki aşamalı arama işlemini gerçekleştirir.
        1. aşama: vektör/hibrit arama ile adayları getir
        2. aşama: cross-encoder ile yeniden sırala
        """
        target_k1 = k1 or self.k1
        target_k2 = k2 or self.k2

        # 1. Aşama: Vektör / Hibrit Arama (Adayları Getir)
        start_first_stage = time.perf_counter()

        candidates: List[CandidateChunk] = []

        if hasattr(self.retriever, "search"):
            # Hibrit Retriever arayüzü
            hybrid_res = self.retriever.search(
                query=query,
                method=method,
                top_k=target_k1,
                alpha=alpha
            )
            first_stage_latency_ms = round((time.perf_counter() - start_first_stage) * 1000.0, 2)

            for it in hybrid_res.items:
                chunk_obj = self.chunk_lookup.get(it.chunk_id)
                full_text = chunk_obj.text if chunk_obj else it.text_snippet
                source = chunk_obj.source if chunk_obj else it.source
                section = chunk_obj.section if chunk_obj else it.section
                breadcrumbs = chunk_obj.breadcrumbs if chunk_obj else it.breadcrumbs

                candidates.append(
                    CandidateChunk(
                        chunk_id=it.chunk_id,
                        doc_id=it.doc_id,
                        first_stage_rank=it.rank,
                        first_stage_score=round(it.final_score, 4),
                        source=source,
                        section=section,
                        breadcrumbs=breadcrumbs,
                        text=full_text
                    )
                )
        elif hasattr(self.retriever, "retrieve"):
            # Basit vektör arama arayüzü (Şekil 67: candidate_docs = self.retriever.retrieve(query, top_k=self.k1))
            cand_docs = self.retriever.retrieve(query, top_k=target_k1)
            first_stage_latency_ms = round((time.perf_counter() - start_first_stage) * 1000.0, 2)
            for idx, d in enumerate(cand_docs, start=1):
                candidates.append(
                    CandidateChunk(
                        chunk_id=getattr(d, "id", f"c_{idx}"),
                        doc_id=getattr(d, "id", f"d_{idx}"),
                        first_stage_rank=idx,
                        first_stage_score=0.9 - (idx * 0.05),
                        text=getattr(d, "content", str(d))
                    )
                )
        else:
            first_stage_latency_ms = 0.0

        # 2. Aşama: Cross-Encoder ile Yeniden Sıralama (k2)
        rerank_res = self.reranker.rerank(
            query=query,
            documents=candidates,
            top_k=target_k2
        )

        if isinstance(rerank_res, tuple):
            reranked_items, rerank_latency_ms = rerank_res
        else:
            reranked_items = rerank_res
            rerank_latency_ms = 10.0

        total_latency_ms = round(first_stage_latency_ms + rerank_latency_ms, 2)

        # Context Sıkıştırma ve Maliyet Analizi
        compression = self.analyzer.analyze_compression(candidates, reranked_items)
        cost_profile = self.analyzer.analyze_cost_and_latency(
            compression=compression,
            reranker_overhead_ms=rerank_latency_ms
        )

        return TwoStageRetrievalResult(
            query=query,
            k1_candidates_count=len(candidates),
            k2_selected_count=len(reranked_items),
            candidates=candidates,
            reranked_items=reranked_items,
            compression=compression,
            cost_profile=cost_profile,
            first_stage_latency_ms=first_stage_latency_ms,
            rerank_latency_ms=rerank_latency_ms,
            total_latency_ms=total_latency_ms
        )
