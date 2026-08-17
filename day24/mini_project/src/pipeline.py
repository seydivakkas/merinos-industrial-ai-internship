"""
Merinos Industrial AI Internship - Day 24
Three-Stage Hybrid Retrieval & Cross-Encoder Re-ranking Pipeline

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path
import json
import time

from day24.mini_project.src.models import (
    RawDocument,
    FusedSearchResultItem,
    ReRankedHybridResultItem
)
from day24.mini_project.src.hybrid_engine import MerinosHybridSearchEngine
from day23.mini_project.src.cross_encoder_reranker import CrossEncoderReranker


class ThreeStageHybridPipeline:
    """
    1. Aşama: BM25 (Seyrek) + Qdrant (Yoğun) Aday Getirme (Retrieval)
    2. Aşama: Reciprocal Rank Fusion (RRF k=60) veya Ağırlıklı Doğrusal Füzyon (Fusion)
    3. Aşama: Cross-Encoder ile Derin Alaka Sıralaması (Re-ranking)
    """

    def __init__(
        self,
        hybrid_engine: Optional[MerinosHybridSearchEngine] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        rrf_k: int = 60,
        default_alpha: float = 0.5,
        collection_name: str = "merinos_hybrid_docs",
        use_cross_encoder: bool = True,
        cross_encoder_top_n: int = 10,
    ):
        self.rrf_k = rrf_k
        self.default_alpha = default_alpha
        self.use_cross_encoder = use_cross_encoder
        self.cross_encoder_top_n = cross_encoder_top_n

        if hybrid_engine is not None:
            self.hybrid_engine = hybrid_engine
        else:
            self.hybrid_engine = MerinosHybridSearchEngine(
                rrf_k=rrf_k,
                default_alpha=default_alpha
            )

        if reranker is not None:
            self.reranker = reranker
        else:
            self.reranker = CrossEncoderReranker()

    def index_corpus(self, corpus: Union[List[RawDocument], Path, str]) -> List[RawDocument]:
        """Külliyatı yükler ve hem BM25 hem Qdrant vektör tabanına indeksler."""
        if isinstance(corpus, (Path, str)):
            corpus_path = Path(corpus)
            with open(corpus_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            docs = []
            for item in data:
                docs.append(
                    RawDocument(
                        doc_id=item.get("id") or item.get("doc_id"),
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        category=item.get("category", ""),
                        tags=item.get("tags") or item.get("keywords") or [],
                        metadata=item.get("metadata", {}),
                    )
                )
        else:
            docs = corpus

        self.hybrid_engine.index_corpus(docs)
        return docs

    def search(
        self,
        query: str,
        mode: str = "rrf",
        category_filter: Optional[str] = None,
        top_k: int = 5,
        rerank: bool = False,
        alpha: Optional[float] = None,
    ) -> List[Union[FusedSearchResultItem, ReRankedHybridResultItem]]:
        """
        Esnek arama arayüzü: Doğrudan füzyon veya Cross-Encoder ile yeniden sıralama.
        """
        if rerank:
            results, _, _, _ = self.search_and_rerank(
                query=query,
                first_stage_pool_size=max(top_k * 3, self.cross_encoder_top_n),
                fused_top_k=self.cross_encoder_top_n,
                final_top_k=top_k,
                use_rrf=(mode.lower() == "rrf"),
                alpha=alpha,
                category_filter=category_filter
            )
            return results

        if mode.lower() == "rrf":
            fused, _, _, _ = self.hybrid_engine.search_hybrid_rrf(
                query=query,
                top_k=top_k,
                candidate_pool_size=max(top_k * 3, 15),
                category_filter=category_filter
            )
        else:
            fused, _, _, _ = self.hybrid_engine.search_hybrid_weighted(
                query=query,
                alpha=alpha if alpha is not None else self.default_alpha,
                top_k=top_k,
                candidate_pool_size=max(top_k * 3, 15),
                category_filter=category_filter
            )
        return fused

    def search_and_rerank(
        self,
        query: str,
        first_stage_pool_size: int = 15,
        fused_top_k: int = 10,
        final_top_k: int = 3,
        use_rrf: bool = True,
        alpha: Optional[float] = None,
        category_filter: Optional[str] = None
    ) -> Tuple[List[ReRankedHybridResultItem], float, float, float]:
        """
        3 Aşamalı hibrit getirme ve yeniden sıralama hattı:
        Dönüş: (Sonuçlar, Aday Getirme Süresi ms, Füzyon Süresi ms, Re-ranking Süresi ms)
        """
        if use_rrf:
            fused_candidates, bm25_ms, dense_ms, fusion_ms = self.hybrid_engine.search_hybrid_rrf(
                query=query,
                top_k=fused_top_k,
                candidate_pool_size=first_stage_pool_size,
                category_filter=category_filter
            )
        else:
            fused_candidates, bm25_ms, dense_ms, fusion_ms = self.hybrid_engine.search_hybrid_weighted(
                query=query,
                alpha=alpha,
                top_k=fused_top_k,
                candidate_pool_size=first_stage_pool_size,
                category_filter=category_filter
            )
        retrieval_ms = bm25_ms + dense_ms

        # 3. Aşama: Cross-Encoder Re-ranking
        t_re_start = time.perf_counter()
        pairs = []
        for c in fused_candidates:
            doc = self.hybrid_engine.doc_map.get(c.doc_id)
            if doc:
                text = f"{doc.title} - {doc.content}"
            else:
                text = f"{c.title} - {c.snippet}"
            pairs.append((query, text))

        if pairs:
            ce_scores = self.reranker.predict_pairs(pairs)
            sorted_indices = sorted(range(len(fused_candidates)), key=lambda i: ce_scores[i], reverse=True)
        else:
            ce_scores = []
            sorted_indices = []

        t_re_end = time.perf_counter()
        rerank_ms = (t_re_end - t_re_start) * 1000.0

        reranked_results: List[ReRankedHybridResultItem] = []
        for rank, idx in enumerate(sorted_indices[:final_top_k], start=1):
            c = fused_candidates[idx]
            reranked_results.append(
                ReRankedHybridResultItem(
                    doc_id=c.doc_id,
                    title=c.title,
                    fused_score=c.fused_score,
                    cross_encoder_score=float(ce_scores[idx]),
                    rank=rank,
                    snippet=c.snippet,
                    category=c.category,
                    tags=c.tags
                )
            )

        return reranked_results, retrieval_ms, fusion_ms, rerank_ms
