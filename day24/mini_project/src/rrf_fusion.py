from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from collections import defaultdict

from day24.mini_project.src.models import (
    CandidateResult,
    FusedSearchResultItem,
    RawDocument
)


class RankFusionEngine:
    """RRF (Reciprocal Rank Fusion) ile farklı arama sonuçlarını birleştiren sınıf."""

    def __init__(
        self,
        k: int = 60,
        rrf_k: Optional[int] = None,
        weight_sparse: float = 1.0,
        weight_dense: float = 1.0,
        default_alpha: float = 0.5,
        **kwargs: Any
    ):
        self.k = rrf_k if rrf_k is not None else k
        self.rrf_k = self.k
        self.weight_sparse = weight_sparse
        self.weight_dense = weight_dense
        self.default_alpha = default_alpha

    def reciprocal_rank_fusion(
        self,
        results_list: List[List[Dict[str, Any]]] = None,
        weights: Optional[List[float]] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion (RRF) algoritması ile birden fazla arama sonucunu birleştirir."""
        if "sparse_candidates" in kwargs:
            results_list = kwargs.pop("sparse_candidates")
        if "dense_candidates" in kwargs:
            weights = kwargs.pop("dense_candidates")
        doc_store = kwargs.pop("doc_store", None)
        top_k = kwargs.pop("top_k", 10)

        if not results_list:
            return []

        # İki aday listesi (sparse ve dense CandidateResult listeleri) ile çağrıldıysa
        if (
            isinstance(results_list, list)
            and len(results_list) > 0
            and not isinstance(results_list[0], list)
        ):
            sparse_candidates = results_list
            dense_candidates = weights if isinstance(weights, list) else []
            return self._fuse_sparse_and_dense_candidates(
                sparse_candidates=sparse_candidates,
                dense_candidates=dense_candidates,
                doc_store=doc_store,
                top_k=top_k
            )

        if weights is None:
            weights = [1.0] * len(results_list)

        scores = defaultdict(float)
        doc_map = {}
        for list_idx, results in enumerate(results_list):
            w = weights[list_idx] if list_idx < len(weights) else 1.0
            for rank, item in enumerate(results):
                doc_id = item.get("id") if isinstance(item, dict) else getattr(item, "doc_id", getattr(item, "id", None))
                score = w / (self.k + rank + 1)
                scores[doc_id] = scores.get(doc_id, 0.0) + score
                if doc_id and doc_id not in doc_map:
                    doc_map[doc_id] = item

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        fused_dicts = []
        for rank_idx, (doc_id, score) in enumerate(sorted_docs, start=1):
            raw = doc_map.get(doc_id, {})
            fused_dicts.append({
                "id": doc_id,
                "doc_id": doc_id,
                "fusion_score": float(score),
                "fusion_rank": rank_idx,
                "title": raw.get("title", "") if isinstance(raw, dict) else getattr(raw, "title", ""),
                "content": raw.get("content", "") if isinstance(raw, dict) else getattr(raw, "content", ""),
                "category": raw.get("category", "") if isinstance(raw, dict) else getattr(raw, "category", "")
            })
        return fused_dicts

    def _fuse_sparse_and_dense_candidates(
        self,
        sparse_candidates: List[CandidateResult],
        dense_candidates: List[CandidateResult],
        doc_store: Optional[Dict[str, RawDocument]] = None,
        top_k: int = 10
    ) -> List[FusedSearchResultItem]:
        """CandidateResult listelerini FusedSearchResultItem formatında birleştirir."""
        store = doc_store or {}
        sparse_map = {c.doc_id: (c.rank, c.score, c) for c in sparse_candidates}
        dense_map = {c.doc_id: (c.rank, c.score, c) for c in dense_candidates}

        all_doc_ids = list(dict.fromkeys(list(sparse_map.keys()) + list(dense_map.keys())))

        fused_items = []
        for doc_id in all_doc_ids:
            score = 0.0
            sparse_rank, sparse_score, sparse_c = sparse_map.get(doc_id, (None, None, None))
            dense_rank, dense_score, dense_c = dense_map.get(doc_id, (None, None, None))

            if sparse_rank is not None:
                score += self.weight_sparse / (self.rrf_k + sparse_rank)
            if dense_rank is not None:
                score += self.weight_dense / (self.rrf_k + dense_rank)

            doc = store.get(doc_id)
            ref_c = sparse_c or dense_c
            title = doc.title if doc else (ref_c.title if ref_c else "")
            category = doc.category if doc else (ref_c.category if ref_c else "")
            tags = doc.tags if doc else []
            content = doc.content if doc else (ref_c.content if ref_c else "")
            snippet = " ".join(content.split())[:160] + "..." if content else ""

            fused_items.append({
                "doc_id": doc_id,
                "title": title,
                "fused_score": float(score),
                "sparse_rank": sparse_rank,
                "dense_rank": dense_rank,
                "sparse_score": sparse_score,
                "dense_score": dense_score,
                "snippet": snippet,
                "category": category,
                "tags": tags
            })

        fused_items.sort(key=lambda x: x["fused_score"], reverse=True)

        results: List[FusedSearchResultItem] = []
        for rank, item in enumerate(fused_items[:top_k], start=1):
            results.append(
                FusedSearchResultItem(
                    doc_id=item["doc_id"],
                    title=item["title"],
                    fused_score=item["fused_score"],
                    final_rank=rank,
                    sparse_rank=item["sparse_rank"],
                    dense_rank=item["dense_rank"],
                    sparse_score=item["sparse_score"],
                    dense_score=item["dense_score"],
                    snippet=item["snippet"],
                    category=item["category"],
                    tags=item["tags"],
                    fusion_mode="rrf"
                )
            )
        return results

    def weighted_linear_fusion(
        self,
        sparse_candidates: List[CandidateResult],
        dense_candidates: List[CandidateResult],
        doc_store: Optional[Dict[str, RawDocument]] = None,
        alpha: Optional[float] = None,
        top_k: int = 10
    ) -> List[FusedSearchResultItem]:
        """
        Min-Max normalize edilmiş ağırlıklı doğrusal skor füzyonu:
        Score(d) = alpha * Norm(Sparse) + (1 - alpha) * Norm(Dense)
        """
        store = doc_store or {}
        a = alpha if alpha is not None else self.default_alpha

        norm_sparse = min_max_normalize_scores(sparse_candidates)
        norm_dense = min_max_normalize_scores(dense_candidates)

        sparse_map = {c.doc_id: (c.rank, c.score, c) for c in sparse_candidates}
        dense_map = {c.doc_id: (c.rank, c.score, c) for c in dense_candidates}

        all_doc_ids = list(dict.fromkeys(list(norm_sparse.keys()) + list(norm_dense.keys())))

        fused_items = []
        for doc_id in all_doc_ids:
            ns = norm_sparse.get(doc_id, 0.0)
            nd = norm_dense.get(doc_id, 0.0)

            score = a * ns + (1.0 - a) * nd

            sparse_rank, sparse_score, sparse_c = sparse_map.get(doc_id, (None, None, None))
            dense_rank, dense_score, dense_c = dense_map.get(doc_id, (None, None, None))

            doc = store.get(doc_id)
            ref_c = sparse_c or dense_c
            title = doc.title if doc else (ref_c.title if ref_c else "")
            category = doc.category if doc else (ref_c.category if ref_c else "")
            tags = doc.tags if doc else []
            content = doc.content if doc else (ref_c.content if ref_c else "")
            snippet = " ".join(content.split())[:160] + "..." if content else ""

            fused_items.append({
                "doc_id": doc_id,
                "title": title,
                "fused_score": float(score),
                "sparse_rank": sparse_rank,
                "dense_rank": dense_rank,
                "sparse_score": sparse_score,
                "dense_score": dense_score,
                "snippet": snippet,
                "category": category,
                "tags": tags
            })

        fused_items.sort(key=lambda x: x["fused_score"], reverse=True)

        results: List[FusedSearchResultItem] = []
        for rank, item in enumerate(fused_items[:top_k], start=1):
            results.append(
                FusedSearchResultItem(
                    doc_id=item["doc_id"],
                    title=item["title"],
                    fused_score=item["fused_score"],
                    final_rank=rank,
                    sparse_rank=item["sparse_rank"],
                    dense_rank=item["dense_rank"],
                    sparse_score=item["sparse_score"],
                    dense_score=item["dense_score"],
                    snippet=item["snippet"],
                    category=item["category"],
                    tags=item["tags"],
                    fusion_mode="weighted"
                )
            )

        return results


def min_max_normalize_scores(candidates: List[CandidateResult]) -> Dict[str, float]:
    """
    Aday arama sonuçlarının ham skorlarını [0.0, 1.0] aralığına normalize eder.
    Tüm skorlar eşitse veya tek eleman varsa 1.0 döner.
    """
    if not candidates:
        return {}
    scores = [c.score for c in candidates]
    s_min, s_max = min(scores), max(scores)
    s_range = s_max - s_min
    if s_range <= 1e-8:
        return {c.doc_id: 1.0 for c in candidates}
    return {c.doc_id: float((c.score - s_min) / s_range) for c in candidates}


def reciprocal_rank_fusion(
    sparse_candidates: List[CandidateResult],
    dense_candidates: List[CandidateResult],
    doc_store: Optional[Dict[str, RawDocument]] = None,
    k: int = 60,
    weight_sparse: float = 1.0,
    weight_dense: float = 1.0,
    top_k: int = 10
) -> List[FusedSearchResultItem]:
    """Modül seviyesi RRF yardımcı fonksiyonu."""
    engine = RankFusionEngine(rrf_k=k, weight_sparse=weight_sparse, weight_dense=weight_dense)
    return engine.reciprocal_rank_fusion(
        sparse_candidates=sparse_candidates,
        dense_candidates=dense_candidates,
        doc_store=doc_store,
        top_k=top_k
    )


def weighted_linear_score_fusion(
    sparse_candidates: List[CandidateResult],
    dense_candidates: List[CandidateResult],
    doc_store: Optional[Dict[str, RawDocument]] = None,
    alpha: float = 0.5,
    top_k: int = 10
) -> List[FusedSearchResultItem]:
    """Modül seviyesi Ağırlıklı Doğrusal Füzyon yardımcı fonksiyonu."""
    engine = RankFusionEngine(default_alpha=alpha)
    return engine.weighted_linear_fusion(sparse_candidates, dense_candidates, doc_store=doc_store, alpha=alpha, top_k=top_k)
