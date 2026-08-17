"""
Merinos Industrial AI Internship - Day 24
Merinos Hybrid Search Engine (BM25 + Qdrant Dense Fusion)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path
import json
import time
import numpy as np
from loguru import logger

from day24.mini_project.src.models import (
    RawDocument,
    CandidateResult,
    FusedSearchResultItem
)
from day24.mini_project.src.rrf_fusion import RankFusionEngine

from day22.mini_project.src.tokenizer import MerinosTextTokenizer
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.bm25_engine import OkapiBM25Engine
from day22.mini_project.src.models import RawDocument as D22RawDoc

from day23.mini_project.src.bi_encoder import BiEncoderDenseRetriever
from day23.mini_project.src.vector_store import QdrantVectorStore
from day23.mini_project.src.models import RawDocument as D23RawDoc


class MerinosHybridSearchEngine:
    """BM25 (sparse) ve Qdrant (dense) aramalarını birleştiren hibrit arama motoru."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        rrf_k: int = 60,
        default_alpha: float = 0.5,
        sparse_k1: float = 1.5,
        sparse_b: float = 0.75,
        dense_model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "merinos_hybrid_docs",
        **kwargs: Any
    ):
        self.config = config or {}
        self.bm25 = None
        self.dense_model = None
        self.qdrant_client = None
        self._initialize_components()

        # Engine parameters
        self.rrf_k = self.config.get("rrf_k", rrf_k)
        self.default_alpha = self.config.get("default_alpha", default_alpha)
        self.sparse_k1 = self.config.get("sparse_k1", sparse_k1)
        self.sparse_b = self.config.get("sparse_b", sparse_b)
        self.collection_name = self.config.get("collection_name", collection_name)
        self.dense_model_name = self.config.get("dense_model", dense_model_name)

        # 1. Seyrek Motor (BM25)
        self.tokenizer = MerinosTextTokenizer()
        self.inverted_index = InvertedIndex(tokenizer=self.tokenizer)
        self.bm25_engine: Optional[OkapiBM25Engine] = None

        # 2. Yoğun Motor (Qdrant Bi-Encoder)
        self.bi_encoder = BiEncoderDenseRetriever(model_name=self.dense_model_name)
        self.vector_store = QdrantVectorStore(collection_name=self.collection_name, in_memory=True)
        if hasattr(self.vector_store, "client"):
            self.qdrant_client = self.vector_store.client

        # 3. Füzyon Motoru
        self.fusion_engine = RankFusionEngine(rrf_k=self.rrf_k, default_alpha=self.default_alpha)

        self.documents: List[RawDocument] = []
        self.doc_map: Dict[str, RawDocument] = {}

    def _initialize_components(self):
        """BM25 ve dense model bileşenlerini başlatır."""
        try:
            from sentence_transformers import SentenceTransformer
            model_name = self.config.get(
                "dense_model",
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.dense_model = SentenceTransformer(model_name)
            logger.info(f"Dense model yüklendi: {model_name}")
        except Exception as e:
            logger.warning(f"Dense model yüklenemedi, fallback kullanılıyor: {e}")
            self.dense_model = None  # Basit embedding fallback

    def sparse_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """BM25 ile anahtar kelime tabanlı arama yapar."""
        if self.bm25 is None and self.bm25_engine is None:
            logger.warning("BM25 index henüz yüklenmemiş")
            return []
        candidates = self.search_sparse(query, top_k=top_k)
        return [c.model_dump() for c in candidates]

    def index_corpus(self, documents: Union[List[RawDocument], Path, str]) -> List[RawDocument]:
        """Külliyatı hem BM25 ters indeksine hem de Qdrant vektör tabanına indeksler."""
        if isinstance(documents, (Path, str)):
            corpus_path = Path(documents)
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
            docs = documents

        self.documents = docs
        self.doc_map = {d.doc_id: d for d in docs}

        # BM25 İndeksleme
        d22_docs = [D22RawDoc(**d.model_dump()) for d in docs]
        self.inverted_index.build(d22_docs)
        self.bm25_engine = OkapiBM25Engine(
            self.inverted_index,
            self.tokenizer,
            k1=self.sparse_k1,
            b=self.sparse_b
        )
        self.bm25 = self.bm25_engine

        # Qdrant İndeksleme
        d23_docs = [D23RawDoc(**d.model_dump()) for d in docs]
        embeddings = self.bi_encoder.index_corpus(d23_docs)
        self.vector_store.upsert_documents(d23_docs, embeddings)
        return docs

    def search_sparse(
        self,
        query: str,
        top_k: int = 15,
        category_filter: Optional[str] = None
    ) -> List[CandidateResult]:
        """BM25 ile seyrek aday arama."""
        if self.bm25_engine is None:
            return []

        bm25_hits = self.bm25_engine.search(query, top_k=top_k * 2)
        candidates: List[CandidateResult] = []
        rank = 1
        for hit in bm25_hits:
            doc = self.doc_map.get(hit.doc_id)
            if category_filter and doc and doc.category.upper() != category_filter.upper():
                continue
            candidates.append(
                CandidateResult(
                    doc_id=hit.doc_id,
                    score=float(hit.score),
                    rank=rank,
                    title=doc.title if doc else "",
                    content=doc.content if doc else "",
                    category=doc.category if doc else "",
                    channel="bm25"
                )
            )
            rank += 1
            if len(candidates) >= top_k:
                break
        return candidates

    def search_dense(
        self,
        query: str,
        top_k: int = 15,
        category_filter: Optional[str] = None
    ) -> List[CandidateResult]:
        """Qdrant Bi-Encoder ile yoğun aday arama."""
        query_vec = self.bi_encoder.encode_query(query)
        dense_hits = self.vector_store.search(
            query_vector=query_vec,
            top_k=top_k,
            category_filter=category_filter
        )
        candidates = []
        for hit in dense_hits:
            doc = self.doc_map.get(hit.doc_id)
            candidates.append(
                CandidateResult(
                    doc_id=hit.doc_id,
                    score=float(hit.score),
                    rank=hit.rank,
                    title=doc.title if doc else hit.title,
                    content=doc.content if doc else "",
                    category=doc.category if doc else hit.category,
                    channel="dense"
                )
            )
        return candidates

    def search(
        self,
        query: str,
        top_k: int = 15,
        category_filter: Optional[str] = None
    ) -> Tuple[List[CandidateResult], List[CandidateResult]]:
        """Hem BM25 hem Dense sonuçlarını birlikte döndürür."""
        sparse = self.search_sparse(query, top_k=top_k, category_filter=category_filter)
        dense = self.search_dense(query, top_k=top_k, category_filter=category_filter)
        return sparse, dense

    def search_hybrid_rrf(
        self,
        query: str,
        top_k: int = 10,
        candidate_pool_size: int = 15,
        category_filter: Optional[str] = None
    ) -> Tuple[List[FusedSearchResultItem], float, float, float]:
        """
        RRF tabanlı hibrit arama:
        Dönüş: (Sonuçlar, BM25 Süresi ms, Dense Süresi ms, Füzyon Süresi ms)
        """
        t0 = time.perf_counter()
        sparse_candidates = self.search_sparse(query, top_k=candidate_pool_size, category_filter=category_filter)
        t1 = time.perf_counter()
        dense_candidates = self.search_dense(query, top_k=candidate_pool_size, category_filter=category_filter)
        t2 = time.perf_counter()

        fused_results = self.fusion_engine.reciprocal_rank_fusion(
            sparse_candidates=sparse_candidates,
            dense_candidates=dense_candidates,
            doc_store=self.doc_map,
            top_k=top_k
        )
        t3 = time.perf_counter()

        return (
            fused_results,
            (t1 - t0) * 1000.0,
            (t2 - t1) * 1000.0,
            (t3 - t2) * 1000.0
        )

    def search_hybrid_weighted(
        self,
        query: str,
        alpha: Optional[float] = None,
        top_k: int = 10,
        candidate_pool_size: int = 15,
        category_filter: Optional[str] = None
    ) -> Tuple[List[FusedSearchResultItem], float, float, float]:
        """
        Normalize Ağırlıklı Doğrusal Skor Füzyonu ile hibrit arama:
        Dönüş: (Sonuçlar, BM25 Süresi ms, Dense Süresi ms, Füzyon Süresi ms)
        """
        t0 = time.perf_counter()
        sparse_candidates = self.search_sparse(query, top_k=candidate_pool_size, category_filter=category_filter)
        t1 = time.perf_counter()
        dense_candidates = self.search_dense(query, top_k=candidate_pool_size, category_filter=category_filter)
        t2 = time.perf_counter()

        fused_results = self.fusion_engine.weighted_linear_fusion(
            sparse_candidates=sparse_candidates,
            dense_candidates=dense_candidates,
            doc_store=self.doc_map,
            alpha=alpha,
            top_k=top_k
        )
        t3 = time.perf_counter()

        return (
            fused_results,
            (t1 - t0) * 1000.0,
            (t2 - t1) * 1000.0,
            (t3 - t2) * 1000.0
        )
