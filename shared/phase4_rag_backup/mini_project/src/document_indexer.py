"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Document Indexer: Markdown-Aware Chunking & Dual Indexing (BM25 + Qdrant In-Memory HNSW with Int8 SQ)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import re
import math
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models as qm

from day28.mini_project.src.models import DocumentItem, ChunkRecord


def _tokenize(text: str) -> List[str]:
    """Türkçe ve teknik endüstriyel terimleri destekleyen kelime ayrıştırıcı."""
    cleaned = re.sub(r"[^\w\s\d.,±°%/-]", " ", text.lower())
    return [w for w in cleaned.split() if len(w) >= 2]


class BM25Index:
    """Okapi BM25 Seyrek İndeks ve Skorlayıcı Motoru."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.inverted_index: Dict[str, List[tuple[int, int]]] = {}  # term -> [(doc_idx, tf)]
        self.chunks: List[ChunkRecord] = []

    def fit(self, chunks: List[ChunkRecord]) -> None:
        self.chunks = chunks
        self.corpus_size = len(chunks)
        self.doc_lengths = []
        self.doc_freqs = {}
        self.inverted_index = {}

        if self.corpus_size == 0:
            return

        total_len = 0
        for doc_idx, chunk in enumerate(chunks):
            # Breadcrumbs ve metni birlikte indeksle
            full_text = f"{chunk.breadcrumbs} {chunk.text}"
            tokens = _tokenize(full_text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len

            # TF hesabı
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for term, count in tf_map.items():
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((doc_idx, count))

        self.avg_doc_len = total_len / self.corpus_size

    def score(self, query: str, doc_idx: Optional[int] = None) -> Any:
        """Belirli bir doküman veya tüm korpus için BM25 skorunu hesaplar."""
        if doc_idx is None:
            return [self.score(query, i) for i in range(self.corpus_size)]

        q_tokens = _tokenize(query)
        score = 0.0
        doc_len = self.doc_lengths[doc_idx]

        for term in q_tokens:
            if term not in self.doc_freqs:
                continue
            df = self.doc_freqs[term]
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            # Doc TF
            postings = self.inverted_index.get(term, [])
            tf = 0
            for d_id, count in postings:
                if d_id == doc_idx:
                    tf = count
                    break
            if tf == 0:
                continue

            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
            score += idf * (numerator / denominator)

        return float(score)

    def score_all(self, query: str) -> List[float]:
        """Korpus içerisindeki tüm dokümanlar için BM25 skorlarını döner."""
        return [float(self.score(query, i)) for i in range(self.corpus_size)]


class DocumentIndexer:
    """Markdown Doküman Parçalayıcı ve Çift Yollu İndeksleyici."""

    def __init__(
        self,
        collection_name: str = "merinos_capstone_kb",
        vector_size: int = 384,
        max_chunk_size: int = 450,
        chunk_overlap: int = 50
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

        self.chunks: List[ChunkRecord] = []
        self.bm25_index = BM25Index()

        # In-Memory Qdrant İstemcisi
        self.qdrant_client = QdrantClient(":memory:")
        self._embed_model = None

    def _get_embedding(self, text: str) -> List[float]:
        """Metin için 384-D yoğun embedding vektörü üretir."""
        if self._embed_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self._embed_model = False

        if self._embed_model:
            vec = self._embed_model.encode(text, normalize_embeddings=True)
            return vec.tolist()

        # Deterministik SHA-256 Fallback
        vec = np.zeros(self.vector_size, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            pos = h % self.vector_size
            vec[pos] += 1.0 / (idx + 1.0)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def chunk_markdown(self, doc: DocumentItem) -> List[ChunkRecord]:
        """Markdown başlık hiyerarşisini (H1, H2) koruyarak dokümanı parçalar."""
        lines = doc.content.split("\n")
        chunks: List[ChunkRecord] = []
        
        current_h1 = doc.title
        current_h2 = ""
        current_buffer: List[str] = []
        chunk_counter = 1

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# "):
                current_h1 = line_str[2:].strip()
                continue
            elif line_str.startswith("## "):
                # Yeni bir H2 alt başlığına geçildi, önceki tamponu parça yap
                if current_buffer:
                    b_text = "\n".join(current_buffer).strip()
                    if len(b_text) > 30:
                        bc = f"{current_h1} > {current_h2}" if current_h2 else current_h1
                        chunks.append(
                            ChunkRecord(
                                chunk_id=f"{doc.doc_id}_c{chunk_counter:02d}",
                                doc_id=doc.doc_id,
                                department=doc.department,
                                machine=doc.machine,
                                priority=doc.priority,
                                breadcrumbs=bc,
                                text=b_text,
                                char_length=len(b_text)
                            )
                        )
                        chunk_counter += 1
                        current_buffer = []
                current_h2 = line_str[3:].strip()
            else:
                if line_str:
                    current_buffer.append(line_str)

        # Kalan tamponu parça olarak ekle
        if current_buffer:
            b_text = "\n".join(current_buffer).strip()
            if len(b_text) > 30:
                bc = f"{current_h1} > {current_h2}" if current_h2 else current_h1
                chunks.append(
                    ChunkRecord(
                        chunk_id=f"{doc.doc_id}_c{chunk_counter:02d}",
                        doc_id=doc.doc_id,
                        department=doc.department,
                        machine=doc.machine,
                        priority=doc.priority,
                        breadcrumbs=bc,
                        text=b_text,
                        char_length=len(b_text)
                    )
                )

        return chunks

    def chunk_documents(self, documents: List[DocumentItem]) -> List[ChunkRecord]:
        """Tüm doküman listesini Markdown başlık hiyerarşisine göre parçalar."""
        all_chunks: List[ChunkRecord] = []
        for doc in documents:
            all_chunks.extend(self.chunk_markdown(doc))
        return all_chunks

    def build_indexes(self, documents: List[DocumentItem]) -> None:
        """Tüm dokümanları parçalar, BM25 ve Qdrant HNSW indekslerini inşa eder."""
        all_chunks: List[ChunkRecord] = []
        for doc in documents:
            doc_chunks = self.chunk_markdown(doc)
            all_chunks.extend(doc_chunks)

        self.chunks = all_chunks

        # 1. BM25 İndeksi
        self.bm25_index.fit(all_chunks)

        # 2. Qdrant HNSW + Int8 Scalar Quantization Koleksiyonu
        if self.qdrant_client.collection_exists(self.collection_name):
            self.qdrant_client.delete_collection(self.collection_name)

        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qm.VectorParams(
                size=self.vector_size,
                distance=qm.Distance.COSINE
            ),
            hnsw_config=qm.HnswConfigDiff(m=16, ef_construct=64),
            quantization_config=qm.ScalarQuantization(
                scalar=qm.ScalarQuantizationConfig(
                    type=qm.ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True
                )
            )
        )

        # Payload şema indeksleri
        self.qdrant_client.create_payload_index(
            collection_name=self.collection_name,
            field_name="department",
            field_schema=qm.PayloadSchemaType.KEYWORD
        )
        self.qdrant_client.create_payload_index(
            collection_name=self.collection_name,
            field_name="machine",
            field_schema=qm.PayloadSchemaType.KEYWORD
        )

        # Vektörleri yükle
        points = []
        for idx, ch in enumerate(all_chunks):
            embed_text = f"{ch.breadcrumbs}\n{ch.text}"
            vec = self._get_embedding(embed_text)
            points.append(
                qm.PointStruct(
                    id=idx + 1,
                    vector=vec,
                    payload={
                        "chunk_id": ch.chunk_id,
                        "doc_id": ch.doc_id,
                        "department": ch.department,
                        "machine": ch.machine,
                        "priority": ch.priority,
                        "breadcrumbs": ch.breadcrumbs,
                        "text": ch.text,
                        "char_length": ch.char_length
                    }
                )
            )

        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
