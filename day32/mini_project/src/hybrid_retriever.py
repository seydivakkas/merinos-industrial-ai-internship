# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
Hybrid Retriever: BM25 (lexical) ve anlamsal (dense) aramayı birleştiren hibrit arama sınıfı.
Şekil 63 ile %100 birebir hizalı sınıf yapısı, metodlar ve füzyon algoritmaları
"""

import time
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union

from day31.mini_project.src.models import ChunkRecord, RetrievalItem, QueryResult
from day31.mini_project.src.bm25_retriever import BM25Retriever
from day31.mini_project.src.dense_retriever import DenseRetriever
from day32.mini_project.src.models import FusedItem, HybridQueryResult

# Şekil 63 Tip Alias Uyumu
Document = ChunkRecord


def min_max_normalize(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Verilen parça skoru sözlüğünü [0.0, 1.0] kapalı aralığına normalize eder.
    Aykırı değerler veya min==max durumunda sıfıra bölme hatasını önler.
    """
    if not scores:
        return {}

    values = list(scores.values())
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return {k: 1.0 if max_val > 0.0 else 0.0 for k in scores}

    spread = max_val - min_val
    return {k: (v - min_val) / spread for k, v in scores.items()}


def compute_rrf_score(rank: int, k: int = 60) -> float:
    """
    Tekil bir sistemdeki sıra derecesi (1-indexed) için RRF terimini hesaplar:
    1 / (k + rank)
    """
    if rank < 1:
        raise ValueError(f"Sıralama 1 veya daha büyük olmalıdır: {rank}")
    return 1.0 / (k + rank)


class HybridRetriever:
    """
    BM25 (lexical) ve anlamsal (dense) aramayı birleştiren hibrit arama sınıfı.
    Şekil 63: Doğrusal Birleştirme (Linear Fusion) ve Reciprocal Rank Fusion (RRF) algoritmalarını içerir.
    """

    def __init__(
        self,
        bm25_retriever: Optional[BM25Retriever] = None,
        dense_retriever: Optional[DenseRetriever] = None,
        alpha: float = 0.5,
        rrf_k: int = 60,
        chunks: Optional[List[ChunkRecord]] = None,
        candidate_depth: int = 20,
        **kwargs
    ):
        # Şekil 63 ve geriye dönük uyumluluk: bm25/dense alternatif isimleri
        self.bm25 = bm25_retriever or kwargs.get("bm25") or BM25Retriever()
        self.dense = dense_retriever or kwargs.get("dense") or DenseRetriever()
        self.alpha = alpha if alpha is not None else kwargs.get("default_alpha", 0.5)
        self.rrf_k = rrf_k if rrf_k is not None else kwargs.get("default_k_rrf", 60)
        self.default_alpha = self.alpha
        self.default_k_rrf = self.rrf_k
        self.candidate_depth = candidate_depth
        self.chunks: List[ChunkRecord] = chunks or []
        self._chunk_map: Dict[str, ChunkRecord] = {}

        if self.chunks:
            self._update_chunk_map()

    def index(self, chunks: List[ChunkRecord]) -> None:
        """Her iki alt arama motoruna parçaları indeksletir ve dahili önbelleği kurar."""
        self.chunks = chunks
        self._update_chunk_map()
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def _update_chunk_map(self) -> None:
        self._chunk_map = {c.chunk_id: c for c in self.chunks}

    def search_linear(
        self,
        query: str,
        top_k: int = 5,
        alpha: Optional[float] = None
    ) -> HybridQueryResult:
        """
        BM25 ve anlamsal arama skorlarını doğrusal birleştirme (linear fusion) ile birleştirir.
        Şekil 63:
        1. Her iki retriever'dan sonuçları al (top_k * 2)
        2. Skorları birleştir (min-max normalizasyon + ağırlıklı toplam)
        """
        t_start = time.perf_counter()
        eff_alpha = self.alpha if alpha is None else alpha
        if not (0.0 <= eff_alpha <= 1.0):
            raise ValueError(f"Alpha parametresi [0.0, 1.0] aralığında olmalıdır, girilen: {eff_alpha}")

        # Her iki retriever'dan sonuçları al
        pool_size = max(top_k * 2, min(len(self.chunks), self.candidate_depth)) if self.chunks else top_k * 2
        bm25_results = self.bm25.search(query, top_k=pool_size)
        dense_results = self.dense.search(query, top_k=pool_size)

        bm25_raw: Dict[str, float] = {item.chunk_id: item.score for item in bm25_results.items}
        dense_raw: Dict[str, float] = {item.chunk_id: item.score for item in dense_results.items}

        bm25_ranks: Dict[str, int] = {item.chunk_id: item.rank for item in bm25_results.items}
        dense_ranks: Dict[str, int] = {item.chunk_id: item.rank for item in dense_results.items}

        # Skorları birleştir (min-max normalizasyon + ağırlıklı toplam)
        bm25_norm = min_max_normalize(bm25_raw)
        dense_norm = min_max_normalize(dense_raw)

        all_candidates = set(bm25_norm.keys()) | set(dense_norm.keys())
        merged_scores: Dict[str, float] = {}

        for cid in all_candidates:
            s_bm25 = bm25_norm.get(cid, 0.0)
            s_dense = dense_norm.get(cid, 0.0)
            merged_scores[cid] = eff_alpha * s_bm25 + (1.0 - eff_alpha) * s_dense

        # Sırala ve top_k seç
        sorted_candidates = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        items: List[FusedItem] = []
        for rank, (cid, score) in enumerate(sorted_candidates, start=1):
            chunk = self._chunk_map.get(cid)
            source = chunk.source if chunk else ""
            doc_id = chunk.doc_id if chunk else ""
            section = chunk.section if chunk else ""
            breadcrumbs = chunk.breadcrumbs if chunk else ""
            text_snippet = (chunk.text[:160].replace("\n", " ") + "...") if chunk else ""

            items.append(FusedItem(
                chunk_id=cid,
                doc_id=doc_id,
                final_score=round(score, 5),
                rank=rank,
                bm25_rank=bm25_ranks.get(cid),
                bm25_score=round(bm25_raw[cid], 4) if cid in bm25_raw else None,
                dense_rank=dense_ranks.get(cid),
                dense_score=round(dense_raw[cid], 4) if cid in dense_raw else None,
                source=source,
                section=section,
                breadcrumbs=breadcrumbs,
                text_snippet=text_snippet
            ))

        latency = round((time.perf_counter() - t_start) * 1000, 2)
        return HybridQueryResult(
            query=query,
            fusion_method="linear",
            alpha=round(eff_alpha, 3),
            k_rrf=None,
            items=items,
            latency_ms=latency
        )

    def search_rrf(
        self,
        query: str,
        top_k: int = 5,
        k: Optional[int] = None
    ) -> HybridQueryResult:
        """
        Reciprocal Rank Fusion (RRF) ile sonuçları birleştirir.
        Şekil 63:
        1. Her iki retriever'dan sonuçları al (top_k * 2)
        2. RRF puanlarını hesapla (1 / (k + rank))
        """
        t_start = time.perf_counter()
        eff_k = self.rrf_k if k is None else k
        if eff_k <= 0:
            raise ValueError(f"RRF k sabiti pozitif tam sayı olmalıdır: {eff_k}")

        pool_size = max(top_k * 2, min(len(self.chunks), self.candidate_depth)) if self.chunks else top_k * 2
        bm25_results = self.bm25.search(query, top_k=pool_size)
        dense_results = self.dense.search(query, top_k=pool_size)

        bm25_raw: Dict[str, float] = {item.chunk_id: item.score for item in bm25_results.items}
        dense_raw: Dict[str, float] = {item.chunk_id: item.score for item in dense_results.items}

        bm25_ranks: Dict[str, int] = {item.chunk_id: item.rank for item in bm25_results.items}
        dense_ranks: Dict[str, int] = {item.chunk_id: item.rank for item in dense_results.items}

        all_candidates = set(bm25_ranks.keys()) | set(dense_ranks.keys())
        merged_scores: Dict[str, float] = {}

        for cid in all_candidates:
            rrf_score = 0.0
            if cid in bm25_ranks:
                rrf_score += compute_rrf_score(bm25_ranks[cid], k=eff_k)
            if cid in dense_ranks:
                rrf_score += compute_rrf_score(dense_ranks[cid], k=eff_k)
            merged_scores[cid] = rrf_score

        sorted_candidates = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        items: List[FusedItem] = []
        for rank, (cid, score) in enumerate(sorted_candidates, start=1):
            chunk = self._chunk_map.get(cid)
            source = chunk.source if chunk else ""
            doc_id = chunk.doc_id if chunk else ""
            section = chunk.section if chunk else ""
            breadcrumbs = chunk.breadcrumbs if chunk else ""
            text_snippet = (chunk.text[:160].replace("\n", " ") + "...") if chunk else ""

            items.append(FusedItem(
                chunk_id=cid,
                doc_id=doc_id,
                final_score=round(score, 6),
                rank=rank,
                bm25_rank=bm25_ranks.get(cid),
                bm25_score=round(bm25_raw[cid], 4) if cid in bm25_raw else None,
                dense_rank=dense_ranks.get(cid),
                dense_score=round(dense_raw[cid], 4) if cid in dense_raw else None,
                source=source,
                section=section,
                breadcrumbs=breadcrumbs,
                text_snippet=text_snippet
            ))

        latency = round((time.perf_counter() - t_start) * 1000, 2)
        return HybridQueryResult(
            query=query,
            fusion_method="rrf",
            alpha=None,
            k_rrf=eff_k,
            items=items,
            latency_ms=latency
        )

    def search(
        self,
        query: str,
        method: str = "rrf",
        top_k: int = 5,
        alpha: Optional[float] = None,
        k_rrf: Optional[int] = None
    ) -> HybridQueryResult:
        """Genel arama yönlendiricisi."""
        clean_method = method.lower().strip()
        if clean_method == "linear":
            return self.search_linear(query, top_k=top_k, alpha=alpha)
        elif clean_method == "rrf":
            return self.search_rrf(query, top_k=top_k, k=k_rrf)
        else:
            raise ValueError(f"Bilinmeyen hibrit füzyon metodu: {method}. 'linear' veya 'rrf' kullanın.")
