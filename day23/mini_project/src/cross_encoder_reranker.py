"""
Merinos Industrial AI Internship - Day 23
Cross-Encoder Re-Ranker Engine

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Tuple, Optional, Dict
import numpy as np

from day23.mini_project.src.models import (
    DenseSearchResultItem,
    ReRankedResultItem,
    RawDocument
)


class CrossEncoderReranker:
    """
    Çapraz Dikkat (Cross-Attention) mekanizması ile (Sorgu, Doküman) çiftlerini
    birlikte işleyip derin alaka skoru üreten Re-Ranker motoru.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-TinyBERT-L-2-v2",
        device: str = "cpu",
        apply_sigmoid: bool = True
    ):
        self.model_name = model_name
        self.device = device
        self.apply_sigmoid = apply_sigmoid

        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """CrossEncoder modelini yükler."""
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name, device=self.device)
        except Exception:
            self.model = None

    def _fallback_cross_score(self, query: str, doc_text: str) -> float:
        """
        Model yüklenemezse deterministik çapraz alaka skoru (offline güvence).
        """
        q_tokens = set(query.lower().split())
        d_tokens = set(doc_text.lower().split())
        if not q_tokens:
            return 0.0

        intersection = q_tokens.intersection(d_tokens)
        jaccard = len(intersection) / max(1, len(q_tokens.union(d_tokens)))
        overlap = len(intersection) / len(q_tokens)
        
        raw_score = 3.0 * overlap + 2.0 * jaccard
        return float(1.0 / (1.0 + np.exp(-raw_score)))

    def predict_pairs(self, pairs: List[Tuple[str, str]]) -> np.ndarray:
        """
        (Sorgu, Doküman) metin çiftlerinin alaka skorlarını hesaplar.
        """
        if not pairs:
            return np.empty((0,), dtype=np.float32)

        if self.model is not None:
            try:
                raw_scores = self.model.predict(
                    pairs,
                    batch_size=16,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                scores = np.array(raw_scores, dtype=np.float32)
                if self.apply_sigmoid:
                    scores = 1.0 / (1.0 + np.exp(-scores))
                return scores
            except Exception:
                pass

        # Fallback puanlama
        scores = np.array([self._fallback_cross_score(q, d) for q, d in pairs], dtype=np.float32)
        return scores

    def rerank(
        self,
        query: str,
        candidates: List[DenseSearchResultItem],
        doc_store: Dict[str, RawDocument],
        top_k: int = 3
    ) -> List[ReRankedResultItem]:
        """
        Bi-Encoder'dan gelen aday dokümanları Cross-Encoder ile yeniden puanlar ve sıralar.
        """
        if not candidates:
            return []

        pairs: List[Tuple[str, str]] = []
        valid_candidates: List[DenseSearchResultItem] = []

        for item in candidates:
            doc = doc_store.get(item.doc_id)
            if doc:
                text = f"{doc.title} - {doc.content}"
            else:
                text = f"{item.title} - {item.snippet}"
            pairs.append((query, text))
            valid_candidates.append(item)

        cross_scores = self.predict_pairs(pairs)

        # Cross-Encoder skoruna göre sıralama (azalan)
        sorted_indices = np.argsort(-cross_scores)

        reranked_results: List[ReRankedResultItem] = []
        rank = 1

        for idx in sorted_indices:
            candidate = valid_candidates[idx]
            ce_score = float(cross_scores[idx])

            reranked_results.append(
                ReRankedResultItem(
                    doc_id=candidate.doc_id,
                    title=candidate.title,
                    bi_encoder_score=candidate.score,
                    cross_encoder_score=ce_score,
                    rank=rank,
                    snippet=candidate.snippet,
                    category=candidate.category,
                    tags=candidate.tags
                )
            )
            rank += 1
            if len(reranked_results) >= top_k:
                break

        return reranked_results
