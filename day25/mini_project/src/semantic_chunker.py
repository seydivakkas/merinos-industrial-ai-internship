"""
Merinos Industrial AI Internship - Day 25
Semantic Document Chunker via Sentence Embedding Distance Breakpoints

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Optional, Tuple, Dict, Any
import re
import numpy as np
import hashlib

from day25.mini_project.src.models import DocumentItem, ChunkItem


class SemanticChunker:
    """
    Cümle embedding'leri arasındaki anlamsal kosinüs mesafesini (cosine distance)
    hesaplayarak, konu değişiminin gerçekleştiği kırılma noktalarından (breakpoints)
    metni parçalayan anlamsal bölücü.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold_percentile: float = 85.0,
        min_chunk_size: int = 120,
        max_chunk_size: int = 600,
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.similarity_threshold_percentile = similarity_threshold_percentile
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.device = device

        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """SentenceTransformer modelini yükler veya deterministik fallback hazırlar."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception:
            self.model = None

    def _encode_sentences(self, sentences: List[str]) -> np.ndarray:
        """Cümleleri normalize edilmiş yoğun vektörlere dönüştürür."""
        if not sentences:
            return np.empty((0, 384), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    sentences,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    batch_size=32,
                    show_progress_bar=False
                )
                return embeddings
            except Exception:
                pass

        # Deterministik offline fallback vektörleri
        embeddings = []
        dim = 384
        for sent in sentences:
            vec = np.zeros(dim, dtype=np.float32)
            words = sent.lower().split()
            for i, w in enumerate(words):
                h = int(hashlib.sha256(w.encode("utf-8")).hexdigest()[:8], 16)
                idx = h % dim
                sign = 1.0 if (h // dim) % 2 == 0 else -1.0
                vec[idx] += sign * (1.0 / (1.0 + 0.1 * i))
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Metni noktalama işaretleri ve satır başlarını koruyarak cümlelere böler."""
        # Başlıkları ve maddeleri ayrı cümle gibi koru
        raw_lines = text.split("\n")
        sentences = []
        for line in raw_lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Başlık ise tek parça tut
            if line_str.startswith("#") or line_str.startswith("|"):
                sentences.append(line_str)
                continue
            # Nokta, soru işareti veya ünlem sonrası böl
            splits = re.split(r"(?<=[.?!])\s+", line_str)
            for s in splits:
                s_clean = s.strip()
                if s_clean:
                    sentences.append(s_clean)
        return sentences

    def chunk_document(self, doc: DocumentItem) -> List[ChunkItem]:
        """Dokümanı anlamsal benzerlik kırılma noktalarına göre parçalar."""
        text = doc.content.strip()
        if not text:
            return []

        sentences = self._split_into_sentences(text)
        if len(sentences) <= 2:
            return [
                ChunkItem(
                    chunk_id=f"{doc.doc_id}_chunk_001",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    category=doc.category,
                    content=text,
                    strategy="semantic",
                    chunk_index=1,
                    total_chunks_in_doc=1,
                    char_start=0,
                    char_end=len(text),
                    char_length=len(text),
                    token_count=len(text.split()),
                    section_headers=[doc.title],
                    metadata=doc.metadata
                )
            ]

        # 1. Cümle vektörleri ve ardışık kosinüs mesafesi
        embeddings = self._encode_sentences(sentences)
        # Cosine distance = 1.0 - Cosine similarity (normalize vektörlerde dot product)
        distances = []
        for i in range(len(embeddings) - 1):
            sim = float(np.dot(embeddings[i], embeddings[i + 1]))
            dist = 1.0 - sim
            distances.append(dist)

        # 2. Eşik hesaplama (Percentile threshold)
        if distances:
            threshold = float(np.percentile(distances, self.similarity_threshold_percentile))
        else:
            threshold = 0.5

        # 3. Kırılma noktalarının tespiti ve boyut sınırlarının uygulanması
        chunks_sentences: List[List[str]] = []
        current_chunk: List[str] = [sentences[0]]
        current_len = len(sentences[0])

        for i in range(len(distances)):
            next_sent = sentences[i + 1]
            dist = distances[i]

            # Koşul 1: Mesafe eşiği aşıldı mı?
            is_semantic_break = dist >= threshold
            # Koşul 2: Min chunk size sağlandı mı?
            meets_min_size = current_len >= self.min_chunk_size
            # Koşul 3: Max chunk size aşılıyor mu?
            exceeds_max_size = (current_len + len(next_sent)) > self.max_chunk_size

            if (is_semantic_break and meets_min_size) or exceeds_max_size:
                chunks_sentences.append(current_chunk)
                current_chunk = [next_sent]
                current_len = len(next_sent)
            else:
                current_chunk.append(next_sent)
                current_len += len(next_sent) + 1

        if current_chunk:
            chunks_sentences.append(current_chunk)

        total_chunks = len(chunks_sentences)
        items: List[ChunkItem] = []
        search_start = 0

        for idx, s_list in enumerate(chunks_sentences, start=1):
            chunk_text = "\n".join(s_list).strip()
            found_pos = text.find(s_list[0], search_start)
            if found_pos != -1:
                char_start = found_pos
                char_end = found_pos + len(chunk_text)
                search_start = char_start + 1
            else:
                char_start = 0
                char_end = len(chunk_text)

            items.append(
                ChunkItem(
                    chunk_id=f"{doc.doc_id}_chunk_{idx:03d}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    category=doc.category,
                    content=chunk_text,
                    strategy="semantic",
                    chunk_index=idx,
                    total_chunks_in_doc=total_chunks,
                    char_start=char_start,
                    char_end=char_end,
                    char_length=len(chunk_text),
                    token_count=len(chunk_text.split()),
                    section_headers=[doc.title],
                    metadata=doc.metadata
                )
            )

        return items
