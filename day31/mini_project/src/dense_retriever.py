# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Dense Retriever: SentenceTransformers (384-D) Anlamsal Vektörel Arama Motoru
"""

import time
import hashlib
import numpy as np
from typing import List, Tuple, Optional

from day31.mini_project.src.models import ChunkRecord, RetrievalItem, QueryResult


class DenseRetriever:
    """Yoğun (Dense) Vektörel Anlamsal Arama Motoru (Cosine Similarity)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", vector_dim: int = 384):
        self.model_name = model_name
        self.vector_dim = vector_dim
        self.chunks: List[ChunkRecord] = []
        self.embeddings: Optional[np.ndarray] = None  # shape: (N, vector_dim)
        self._model = None
        self._use_fallback = False

    def _load_model(self):
        """SentenceTransformer modelini tembel yükleme (lazy loading) ile hazırlar."""
        if self._model is None and not self._use_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Bilgi: SentenceTransformer yüklenemedi ({e}), deterministik vektör motoru devrede.")
                self._use_fallback = True

    def _encode_text(self, text: str) -> np.ndarray:
        """Metin için L2-normalize 384-D embedding vektörü üretir."""
        self._load_model()
        if self._model is not None and not self._use_fallback:
            try:
                vec = self._model.encode(text, normalize_embeddings=True)
                return np.array(vec, dtype=np.float32)
            except Exception:
                self._use_fallback = True

        # Deterministik L2-normalize n-gram hashing fallback
        vec = np.zeros(self.vector_dim, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            # Kelime bazlı hash
            h1 = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            pos1 = h1 % self.vector_dim
            vec[pos1] += 1.0 / (idx + 1.0)
            # İkili n-gram hash (ardışık kelimelerin anlamını yakalamak için)
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                h2 = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest()[:8], 16)
                pos2 = h2 % self.vector_dim
                vec[pos2] += 1.5 / (idx + 1.0)

        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        return vec

    def index(self, chunks: List[ChunkRecord]) -> None:
        """Tüm parçaların embedding'lerini hesaplar ve matris belleğinde saklar."""
        self.chunks = chunks
        if not chunks:
            self.embeddings = np.empty((0, self.vector_dim), dtype=np.float32)
            return

        vectors: List[np.ndarray] = []
        for chunk in chunks:
            full_text = f"{chunk.breadcrumbs} {chunk.text}"
            v = self._encode_text(full_text)
            vectors.append(v)

        self.embeddings = np.array(vectors, dtype=np.float32)

    def search(self, query: str, top_k: int = 5, query_type: str = "semantic") -> QueryResult:
        """Sorgu vektörü ile doküman vektörleri arasındaki Cosine Similarity'yi hesaplar."""
        t_start = time.perf_counter()

        if self.embeddings is None or len(self.chunks) == 0:
            return QueryResult(
                query=query,
                query_type=query_type,
                method="dense",
                items=[],
                latency_ms=round((time.perf_counter() - t_start) * 1000, 3)
            )

        q_vec = self._encode_text(query)  # shape: (vector_dim,)
        # Normalize vektörlerde Cosine Similarity = Dot Product: (N, D) @ (D,) -> (N,)
        sim_scores = np.dot(self.embeddings, q_vec)

        # En yüksek skorlu Top-K indeksleri seç
        top_indices = np.argsort(sim_scores)[::-1][:top_k]

        items: List[RetrievalItem] = []
        for rank, idx in enumerate(top_indices, start=1):
            sc = float(sim_scores[idx])
            chunk = self.chunks[idx]
            items.append(RetrievalItem(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                score=round(sc, 4),
                rank=rank,
                source=chunk.source,
                page_number=chunk.page_number,
                section=chunk.section,
                breadcrumbs=chunk.breadcrumbs,
                text_snippet=chunk.text[:160].replace("\n", " ") + "..."
            ))

        latency = round((time.perf_counter() - t_start) * 1000, 3)
        return QueryResult(
            query=query,
            query_type=query_type,
            method="dense",
            items=items,
            latency_ms=latency
        )
