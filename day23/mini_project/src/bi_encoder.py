import logging
from typing import List, Union, Dict, Any, Optional
import numpy as np
import hashlib
from sentence_transformers import SentenceTransformer

from day23.mini_project.src.models import RawDocument, DenseSearchResultItem

logger = logging.getLogger(__name__)


class BiEncoderDenseRetriever:
    """Teknik dokümanlar için Bi-Encoder tabanlı dense retriever."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_length: int = 256,
        device: str = None,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.device = device or ("cuda" if self._has_cuda() else "cpu")
        logger.info(f"Bi-Encoder modeli yükleniyor: {model_name}")
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
        except Exception as e:
            logger.warning(f"SentenceTransformer yüklenemedi: {e}, fallback kullanılacak.")
            self.model = None

        self.embedding_dim = 384
        self.normalize = True
        self.documents: List[RawDocument] = []
        self.doc_map: Dict[str, RawDocument] = {}
        self.doc_embeddings: Optional[np.ndarray] = None

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False,
    ) -> np.ndarray:
        """Verilen metin/metinleri dense vektörlere dönüştürür."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self.embedding_dim), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=show_progress,
                    normalize_embeddings=normalize,
                    convert_to_numpy=True
                )
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning(f"Model encode hatası: {e}, fallback kullanılıyor.")

        # Fallback deterministik karma tabanlı vektör üretimi
        vecs = [self._fallback_embedding(t) for t in texts]
        arr = np.array(vecs, dtype=np.float32)
        if normalize:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            arr = arr / norms
        return arr

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Deterministik semantik karma tabanlı fallback vektör üreteci."""
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % self.embedding_dim
            sign = 1.0 if (h // self.embedding_dim) % 2 == 0 else -1.0
            weight = 1.0 / (1.0 + 0.1 * i)
            vec[idx] += sign * weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def encode_query(self, query: str) -> np.ndarray:
        """Tekil sorgu metnini vektöre dönüştürür (1, D)."""
        return self.encode([query])

    def index_corpus(self, documents: List[RawDocument]) -> np.ndarray:
        """Külliyattaki tüm dokümanları vektörleştirir ve bellekte indeksler."""
        self.documents = documents
        self.doc_map = {doc.doc_id: doc for doc in documents}

        corpus_texts = [f"{doc.title} - {' '.join(doc.tags)} - {doc.content}" for doc in documents]
        self.doc_embeddings = self.encode(corpus_texts)
        return self.doc_embeddings

    def search(
        self,
        query: str,
        top_k: int = 10,
        category_filter: Optional[str] = None
    ) -> List[DenseSearchResultItem]:
        """Sorguyu vektörleştirir, külliyatla kosinüs benzerliğini hesaplar ve Top-K döndürür."""
        if self.doc_embeddings is None or len(self.documents) == 0:
            return []

        query_vec = self.encode_query(query)
        scores = np.dot(query_vec, self.doc_embeddings.T).flatten()
        sorted_indices = np.argsort(-scores)

        results: List[DenseSearchResultItem] = []
        rank = 1

        for idx in sorted_indices:
            doc = self.documents[idx]
            if category_filter and doc.category.upper() != category_filter.upper():
                continue

            score = float(scores[idx])
            snippet = self._extract_snippet(doc.content)

            results.append(
                DenseSearchResultItem(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    score=score,
                    rank=rank,
                    snippet=snippet,
                    category=doc.category,
                    tags=doc.tags
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def _extract_snippet(self, text: str, max_length: int = 160) -> str:
        """İçerikten özet snippet üretir."""
        clean = " ".join(text.split())
        if len(clean) <= max_length:
            return clean
        return clean[:max_length].rstrip() + "..."
