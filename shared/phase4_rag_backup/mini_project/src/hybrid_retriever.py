"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Unified Hybrid Retriever: Pre-filtering, BM25 + Qdrant HNSW Fusion (RRF k=60) and Cross-Encoder Re-Ranking

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import time
from typing import List, Dict, Any, Optional
from qdrant_client import models as qm

from day28.mini_project.src.models import QueryRequest, RetrievalCandidate, ChunkRecord
from day28.mini_project.src.document_indexer import DocumentIndexer


class HybridRetriever:
    """Merinos Uçtan Uca Hibrit Getirme Motoru."""

    def __init__(
        self,
        indexer: DocumentIndexer,
        rrf_k: int = 60,
        sparse_weight: float = 0.4,
        dense_weight: float = 0.6
    ):
        self.indexer = indexer
        self.rrf_k = rrf_k
        self.sparse_weight = sparse_weight
        self.dense_weight = dense_weight
        self._cross_encoder = None

    def _get_cross_encoder_score(self, query: str, candidate_text: str) -> float:
        """Cross-Encoder veya anlamsal terim örtüşmesi ile nihai sıra skoru üretir."""
        if self._cross_encoder is None:
            try:
                from sentence_transformers import CrossEncoder
                self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception:
                self._cross_encoder = False

        if self._cross_encoder:
            score = self._cross_encoder.predict([(query, candidate_text)])[0]
            # Sigmoid ile normalize et
            return float(1.0 / (1.0 + 2.71828 ** (-score)))

        # Offline / Hızlı Deterministik Heuristic Skoru
        q_words = set(query.lower().split())
        c_words = set(candidate_text.lower().split())
        overlap = len(q_words.intersection(c_words)) / max(1, len(q_words))
        return float(min(1.0, overlap * 1.5))

    def retrieve(self, request: QueryRequest) -> (List[RetrievalCandidate], Dict[str, float]):
        """Sorgu için filtreleme, seyrek arama, yoğun arama, RRF ve re-ranking adımlarını yürütür."""
        latencies: Dict[str, float] = {}

        # 1. Filtreleme ve Aday Belirleme
        t0 = time.perf_counter()
        valid_chunk_indices = []
        for idx, ch in enumerate(self.indexer.chunks):
            if request.department_filter and ch.department != request.department_filter:
                continue
            if request.machine_filter and ch.machine != request.machine_filter:
                continue
            valid_chunk_indices.append(idx)
        latencies["filter_ms"] = round((time.perf_counter() - t0) * 1000, 3)

        if not valid_chunk_indices:
            return [], latencies

        # 2. BM25 Seyrek Arama
        t1 = time.perf_counter()
        sparse_scores: List[tuple[int, float]] = []
        for idx in valid_chunk_indices:
            s = self.indexer.bm25_index.score(request.query, idx)
            sparse_scores.append((idx, s))

        # En yüksek skordan düşüğe sırala
        sparse_scores.sort(key=lambda x: x[1], reverse=True)
        sparse_rank_map = {idx: rank + 1 for rank, (idx, _) in enumerate(sparse_scores)}
        sparse_score_map = {idx: s for idx, s in sparse_scores}
        latencies["sparse_search_ms"] = round((time.perf_counter() - t1) * 1000, 3)

        # 3. Qdrant Yoğun Vektör Araması (Pre-filtered)
        t2 = time.perf_counter()
        q_vec = self.indexer._get_embedding(request.query)

        filter_conditions = []
        if request.department_filter:
            filter_conditions.append(
                qm.FieldCondition(
                    key="department",
                    match=qm.MatchValue(value=request.department_filter)
                )
            )
        if request.machine_filter:
            filter_conditions.append(
                qm.FieldCondition(
                    key="machine",
                    match=qm.MatchValue(value=request.machine_filter)
                )
            )

        qdrant_filter = qm.Filter(must=filter_conditions) if filter_conditions else None

        dense_response = self.indexer.qdrant_client.query_points(
            collection_name=self.indexer.collection_name,
            query=q_vec,
            query_filter=qdrant_filter,
            limit=len(valid_chunk_indices)
        )

        dense_rank_map: Dict[int, int] = {}
        dense_score_map: Dict[int, float] = {}
        for rank, p in enumerate(dense_response.points):
            chunk_idx = p.id - 1  # 1-based point ID
            dense_rank_map[chunk_idx] = rank + 1
            dense_score_map[chunk_idx] = float(p.score)

        latencies["dense_search_ms"] = round((time.perf_counter() - t2) * 1000, 3)

        # 4. Karşılıklı Sıra Füzyonu (Reciprocal Rank Fusion - RRF k=60)
        t3 = time.perf_counter()
        rrf_results: List[tuple[int, float]] = []
        for idx in valid_chunk_indices:
            r_sparse = sparse_rank_map.get(idx, len(valid_chunk_indices) + 10)
            r_dense = dense_rank_map.get(idx, len(valid_chunk_indices) + 10)

            score_sparse = self.sparse_weight / (self.rrf_k + r_sparse)
            score_dense = self.dense_weight / (self.rrf_k + r_dense)
            total_rrf = score_sparse + score_dense
            rrf_results.append((idx, total_rrf))

        rrf_results.sort(key=lambda x: x[1], reverse=True)
        top_candidates = rrf_results[:max(request.top_k * 2, 8)]
        latencies["rrf_fusion_ms"] = round((time.perf_counter() - t3) * 1000, 3)

        # 5. Cross-Encoder Re-Ranking
        t4 = time.perf_counter()
        final_candidates: List[RetrievalCandidate] = []

        for idx, rrf_score in top_candidates:
            ch = self.indexer.chunks[idx]
            cand_text = f"{ch.breadcrumbs}\n{ch.text}"

            if request.enable_reranking:
                rerank_score = self._get_cross_encoder_score(request.query, cand_text)
                final_score = 0.5 * rrf_score * 100 + 0.5 * rerank_score
            else:
                rerank_score = 0.0
                final_score = rrf_score

            final_candidates.append(
                RetrievalCandidate(
                    chunk_id=ch.chunk_id,
                    doc_id=ch.doc_id,
                    department=ch.department,
                    machine=ch.machine,
                    breadcrumbs=ch.breadcrumbs,
                    text=ch.text,
                    sparse_score=round(sparse_score_map.get(idx, 0.0), 4),
                    dense_score=round(dense_score_map.get(idx, 0.0), 4),
                    rrf_score=round(rrf_score, 6),
                    rerank_score=round(rerank_score, 4),
                    final_score=round(final_score, 4)
                )
            )

        # Nihai skora göre sırala ve top_k kes
        final_candidates.sort(key=lambda x: x.final_score, reverse=True)
        sliced_candidates = final_candidates[:request.top_k]
        for r, c in enumerate(sliced_candidates, start=1):
            c.rank = r

        latencies["reranking_ms"] = round((time.perf_counter() - t4) * 1000, 3)
        return sliced_candidates, latencies
