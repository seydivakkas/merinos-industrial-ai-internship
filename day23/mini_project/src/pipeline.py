"""
Merinos Industrial AI Internship - Day 23
Two-Stage Dense Retrieval & Re-ranking Pipeline

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Optional, Tuple
import time

from day23.mini_project.src.models import (
    RawDocument,
    DenseSearchResultItem,
    ReRankedResultItem
)
from day23.mini_project.src.bi_encoder import BiEncoderDenseRetriever
from day23.mini_project.src.vector_store import QdrantVectorStore
from day23.mini_project.src.cross_encoder_reranker import CrossEncoderReranker


class TwoStageRetrievalPipeline:
    """
    1. Aşama: Bi-Encoder + Qdrant ile hızlı anlamsal aday getirme (First Stage).
    2. Aşama: Cross-Encoder ile derin alaka yeniden sıralaması (Re-ranking).
    """

    def __init__(
        self,
        bi_encoder: BiEncoderDenseRetriever,
        reranker: CrossEncoderReranker,
        vector_store: Optional[QdrantVectorStore] = None
    ):
        self.bi_encoder = bi_encoder
        self.reranker = reranker
        self.vector_store = vector_store

        self.documents: List[RawDocument] = []
        self.doc_map: Dict[str, RawDocument] = {}

    def index_corpus(self, documents: List[RawDocument]) -> None:
        """Külliyatı hem Bi-Encoder'a hem de Qdrant'a indeksler."""
        self.documents = documents
        self.doc_map = {doc.doc_id: doc for doc in documents}

        # Bi-Encoder ile gömme üretimi
        embeddings = self.bi_encoder.index_corpus(documents)

        # Qdrant'a yükleme
        if self.vector_store is not None:
            self.vector_store.upsert_documents(documents, embeddings)

    def search_first_stage(
        self,
        query: str,
        top_k: int = 10,
        category_filter: Optional[str] = None,
        use_qdrant: bool = True
    ) -> List[DenseSearchResultItem]:
        """Yalnızca 1. Aşama Bi-Encoder/Qdrant aramasını koşturur."""
        if use_qdrant and self.vector_store is not None:
            query_vec = self.bi_encoder.encode_query(query)
            return self.vector_store.search(
                query_vector=query_vec,
                top_k=top_k,
                category_filter=category_filter
            )
        else:
            return self.bi_encoder.search(
                query=query,
                top_k=top_k,
                category_filter=category_filter
            )

    def search_and_rerank(
        self,
        query: str,
        first_stage_top_k: int = 10,
        final_top_k: int = 3,
        category_filter: Optional[str] = None,
        use_qdrant: bool = True
    ) -> Tuple[List[ReRankedResultItem], float, float]:
        """
        İki aşamalı getirme ve yeniden sıralama hattını koşturur.
        Dönüş: (Sonuçlar, Bi-Encoder Süresi ms, Cross-Encoder Süresi ms)
        """
        # 1. Aşama
        t0 = time.perf_counter()
        candidates = self.search_first_stage(
            query=query,
            top_k=first_stage_top_k,
            category_filter=category_filter,
            use_qdrant=use_qdrant
        )
        t1 = time.perf_counter()
        bi_encoder_time_ms = (t1 - t0) * 1000.0

        # 2. Aşama
        t2 = time.perf_counter()
        reranked = self.reranker.rerank(
            query=query,
            candidates=candidates,
            doc_store=self.doc_map,
            top_k=final_top_k
        )
        t3 = time.perf_counter()
        cross_encoder_time_ms = (t3 - t2) * 1000.0

        return reranked, bi_encoder_time_ms, cross_encoder_time_ms
