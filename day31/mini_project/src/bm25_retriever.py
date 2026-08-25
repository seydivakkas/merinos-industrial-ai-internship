# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
BM25 Retriever: Okapi BM25 Leksikal Arama Motoru ve Ters İndeksleme
"""

import re
import math
import time
from typing import List, Dict, Tuple, Optional

from day31.mini_project.src.models import ChunkRecord, RetrievalItem, QueryResult


def tokenize_technical(text: str) -> List[str]:
    """
    Türkçe karakterleri, teknik kodları (örn: 'E-401', '80x80', '14bar')
    koruyarak ayrıştıran endüstriyel tokenizasyon fonksiyonu.
    """
    cleaned = text.lower().replace("’", "'")
    # Teknik kodlar ve alfanümerik kelimeleri eşle
    tokens = re.findall(r"[a-zçğıöşü0-9]+(?:[-/.][a-zçğıöşü0-9]+)*", cleaned)
    return [t for t in tokens if len(t) >= 2]


class BM25Retriever:
    """Okapi BM25 Seyrek (Sparse) Leksikal Arama Motoru."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[ChunkRecord] = []
        self.corpus_size: int = 0
        self.avg_doc_len: float = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.inverted_index: Dict[str, List[Tuple[int, int]]] = {}  # term -> [(chunk_idx, tf)]

    def index(self, chunks: List[ChunkRecord]) -> None:
        """Parça koleksiyonunu indeksler ve ters indeks tablosunu oluşturur."""
        self.chunks = chunks
        self.corpus_size = len(chunks)
        self.doc_lengths = []
        self.doc_freqs = {}
        self.inverted_index = {}

        if self.corpus_size == 0:
            return

        total_tokens = 0
        for doc_idx, chunk in enumerate(chunks):
            # Breadcrumbs ve metni birlikte indeksle
            full_text = f"{chunk.breadcrumbs} {chunk.text}"
            tokens = tokenize_technical(full_text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_tokens += doc_len

            # Terim frekansı (TF)
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for term, count in tf_map.items():
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((doc_idx, count))

        self.avg_doc_len = total_tokens / self.corpus_size if self.corpus_size > 0 else 0.0

    def score_document(self, query_tokens: List[str], doc_idx: int) -> float:
        """Tek bir doküman için BM25 skorunu hesaplar."""
        score = 0.0
        doc_len = self.doc_lengths[doc_idx]

        for term in query_tokens:
            if term not in self.doc_freqs:
                continue

            df = self.doc_freqs[term]
            # IDF hesabı (Robertson-Spärck Jones)
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            # Dokümandaki TF
            tf = 0
            for d_id, count in self.inverted_index.get(term, []):
                if d_id == doc_idx:
                    tf = count
                    break

            if tf == 0:
                continue

            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
            score += idf * (numerator / denominator)

        return float(score)

    def search(self, query: str, top_k: int = 5, query_type: str = "exact") -> QueryResult:
        """Sorguyu çalıştırır ve en yüksek skorlu Top-K parçayı döner."""
        t_start = time.perf_counter()
        q_tokens = tokenize_technical(query)

        if not q_tokens or self.corpus_size == 0:
            return QueryResult(
                query=query,
                query_type=query_type,
                method="bm25",
                items=[],
                latency_ms=round((time.perf_counter() - t_start) * 1000, 3)
            )

        scored_docs: List[Tuple[int, float]] = []
        for idx in range(self.corpus_size):
            s = self.score_document(q_tokens, idx)
            if s > 0.0:
                scored_docs.append((idx, s))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_docs[:top_k]

        items: List[RetrievalItem] = []
        for rank, (doc_idx, sc) in enumerate(top_candidates, start=1):
            chunk = self.chunks[doc_idx]
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
            method="bm25",
            items=items,
            latency_ms=latency
        )
