# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
Retrieval Evaluator: Standart IR Metrikleri Değerlendirme Motoru
(Hit@K, MRR, Precision@K, Recall@K, NDCG@K ve Alpha Parametre Taraması)
"""

import math
from typing import List, Dict, Any, Optional, Callable
from day32.mini_project.src.models import (
    GoldenQuery,
    MetricScore,
    QueryEvaluationResult,
    SystemEvaluationReport,
    AlphaSweepPoint
)
from day32.mini_project.src.hybrid_retriever import HybridRetriever


def compute_dcg(ranks: List[int], k: int) -> float:
    """
    Binary relevance için DCG@K hesabı:
    DCG@K = sum_{i=1}^K rel_i / log2(i + 1)
    """
    dcg = 0.0
    for r in ranks:
        if 1 <= r <= k:
            dcg += 1.0 / math.log2(r + 1.0)
    return dcg


def compute_idcg(num_relevant: int, k: int) -> float:
    """İdeal DCG (IDCG@K) hesabı."""
    if num_relevant <= 0:
        return 0.0
    idcg = 0.0
    for i in range(1, min(num_relevant, k) + 1):
        idcg += 1.0 / math.log2(i + 1.0)
    return idcg


class RetrievalEvaluator:
    """
    Altın kıyaslama veri seti üzerinde farklı retrieval motorlarını
    standart IR metrikleriyle (Hit@K, MRR, NDCG@K) objektif olarak ölçen değerlendirici.
    """

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        k_values: Optional[List[int]] = None,
        eval_depth: int = 10
    ):
        self.retriever = hybrid_retriever
        self.k_values = k_values or [1, 3, 5, 10]
        self.eval_depth = eval_depth

    def evaluate_query(
        self,
        query: GoldenQuery,
        retrieved_chunk_ids: List[str],
        retrieved_doc_ids: List[str]
    ) -> QueryEvaluationResult:
        """Tek bir sorgu için getirme başarı derecesini ve metriklerini hesaplar."""
        # Negatif kontrol (OUT_OF_DOMAIN) sorgusu ise
        if query.target_chunk_id is None and query.target_doc_id is None:
            # Dış alan sorgusu için hiçbir parça getirilmemesi idealdir,
            # Ancak standart retrieval'da her zaman top-k döneceğinden rank None olarak işaretlenir.
            return QueryResult_Out(query)

        # Hedef parça veya doküman indeksini bul
        found_rank: Optional[int] = None
        for rank, cid in enumerate(retrieved_chunk_ids, start=1):
            if cid == query.target_chunk_id:
                found_rank = rank
                break

        # Parça bazında bulunamadıysa doküman eşleşmesine bak (fallback)
        if found_rank is None and query.target_doc_id:
            for rank, did in enumerate(retrieved_doc_ids, start=1):
                if did == query.target_doc_id:
                    found_rank = rank
                    break

        hit_at_k: Dict[int, bool] = {}
        for k in self.k_values:
            hit_at_k[k] = (found_rank is not None and found_rank <= k)

        rr = (1.0 / found_rank) if found_rank is not None else 0.0
        top1_id = retrieved_chunk_ids[0] if retrieved_chunk_ids else None
        top1_corr = (found_rank == 1)

        return QueryEvaluationResult(
            query_id=query.id,
            query=query.query,
            category=query.category,
            target_chunk_id=query.target_chunk_id,
            target_doc_id=query.target_doc_id,
            found_rank=found_rank,
            hit_at_k=hit_at_k,
            reciprocal_rank=round(rr, 4),
            top1_retrieved_chunk_id=top1_id,
            top1_correct=top1_corr
        )

    def evaluate_system(
        self,
        system_name: str,
        search_fn: Callable[[str, int], List[Any]],
        queries: List[GoldenQuery]
    ) -> SystemEvaluationReport:
        """Verilen bir arama fonksiyonu için tüm altın veri seti üzerinden tam rapor üretir."""
        query_results: List[QueryEvaluationResult] = []
        valid_queries = [q for q in queries if q.target_chunk_id is not None or q.target_doc_id is not None]

        for q in queries:
            raw_results = search_fn(q.query, self.eval_depth)
            retrieved_chunk_ids = [getattr(r, "chunk_id", None) for r in raw_results]
            retrieved_doc_ids = [getattr(r, "doc_id", None) for r in raw_results]

            res = self.evaluate_query(q, retrieved_chunk_ids, retrieved_doc_ids)
            query_results.append(res)

        # Metrikleri hesapla (sadece hedefi olan geçerli sorgular üzerinden)
        valid_eval_results = [r for r in query_results if r.category != "OUT_OF_DOMAIN"]
        num_valid = len(valid_eval_results)

        hit_at_k: Dict[int, float] = {}
        precision_at_k: Dict[int, float] = {}
        recall_at_k: Dict[int, float] = {}
        ndcg_at_k: Dict[int, float] = {}

        if num_valid > 0:
            for k in self.k_values:
                hits = sum(1 for r in valid_eval_results if r.hit_at_k.get(k, False))
                hit_at_k[k] = round(hits / num_valid, 4)
                precision_at_k[k] = round(hits / (num_valid * k), 4)
                recall_at_k[k] = round(hits / num_valid, 4)

                # NDCG hesabı
                total_ndcg = 0.0
                idcg = compute_idcg(1, k)  # 1 hedef parça
                for r in valid_eval_results:
                    if r.found_rank and r.found_rank <= k:
                        dcg = compute_dcg([r.found_rank], k)
                        total_ndcg += (dcg / idcg) if idcg > 0 else 0.0
                ndcg_at_k[k] = round(total_ndcg / num_valid, 4)

            mean_rr = round(sum(r.reciprocal_rank for r in valid_eval_results) / num_valid, 4)
        else:
            hit_at_k = {k: 0.0 for k in self.k_values}
            precision_at_k = {k: 0.0 for k in self.k_values}
            recall_at_k = {k: 0.0 for k in self.k_values}
            ndcg_at_k = {k: 0.0 for k in self.k_values}
            mean_rr = 0.0

        overall_metrics = MetricScore(
            hit_at_k=hit_at_k,
            mrr=mean_rr,
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            ndcg_at_k=ndcg_at_k
        )

        # Kategori bazlı ayrım
        categories = sorted(list(set(r.category for r in valid_eval_results)))
        category_breakdown: Dict[str, Dict[str, float]] = {}
        for cat in categories:
            cat_results = [r for r in valid_eval_results if r.category == cat]
            c_len = len(cat_results)
            if c_len > 0:
                c_hit1 = round(sum(1 for r in cat_results if r.hit_at_k.get(1, False)) / c_len, 4)
                c_hit3 = round(sum(1 for r in cat_results if r.hit_at_k.get(3, False)) / c_len, 4)
                c_mrr = round(sum(r.reciprocal_rank for r in cat_results) / c_len, 4)
                category_breakdown[cat] = {
                    "count": c_len,
                    "hit@1": c_hit1,
                    "hit@3": c_hit3,
                    "mrr": c_mrr
                }

        return SystemEvaluationReport(
            system_name=system_name,
            overall_metrics=overall_metrics,
            category_breakdown=category_breakdown,
            total_queries=len(queries),
            valid_queries=num_valid,
            results=query_results
        )

    def evaluate_all_standard_systems(self, queries: List[GoldenQuery]) -> Dict[str, SystemEvaluationReport]:
        """Dört ana getirme mimarisini (BM25, Dense, Linear_0.5, RRF_k60) aynı veri setiyle test eder."""
        reports: Dict[str, SystemEvaluationReport] = {}

        # 1. BM25
        reports["BM25"] = self.evaluate_system(
            "BM25",
            lambda q, k: self.retriever.bm25.search(q, top_k=k).items,
            queries
        )

        # 2. Dense
        reports["Dense"] = self.evaluate_system(
            "Dense",
            lambda q, k: self.retriever.dense.search(q, top_k=k).items,
            queries
        )

        # 3. Linear (alpha=0.5)
        reports["Linear_0.5"] = self.evaluate_system(
            "Linear_0.5",
            lambda q, k: self.retriever.search_linear(q, top_k=k, alpha=0.5).items,
            queries
        )

        # 4. RRF (k=60)
        reports["RRF_k60"] = self.evaluate_system(
            "RRF_k60",
            lambda q, k: self.retriever.search_rrf(q, top_k=k, k=60).items,
            queries
        )

        return reports

    def sweep_alpha(
        self,
        queries: List[GoldenQuery],
        alphas: Optional[List[float]] = None
    ) -> List[AlphaSweepPoint]:
        """Alpha parametresi (0.0 ile 1.0 arası) için hassasiyet taraması yapar."""
        test_alphas = alphas or [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        sweep_results: List[AlphaSweepPoint] = []

        for a in test_alphas:
            rep = self.evaluate_system(
                f"Linear_alpha_{a:.1f}",
                lambda q, k, cur_a=a: self.retriever.search_linear(q, top_k=k, alpha=cur_a).items,
                queries
            )
            m = rep.overall_metrics
            sweep_results.append(AlphaSweepPoint(
                alpha=round(a, 2),
                hit_at_1=m.hit_at_k.get(1, 0.0),
                hit_at_3=m.hit_at_k.get(3, 0.0),
                hit_at_5=m.hit_at_k.get(5, 0.0),
                mrr=m.mrr,
                ndcg_at_5=m.ndcg_at_k.get(5, 0.0)
            ))

        return sweep_results


def QueryResult_Out(query: GoldenQuery) -> QueryEvaluationResult:
    """Negatif kontrol (alan dışı) sorguları için yardımcı nesne oluşturur."""
    return QueryEvaluationResult(
        query_id=query.id,
        query=query.query,
        category=query.category,
        target_chunk_id=None,
        target_doc_id=None,
        found_rank=None,
        hit_at_k={1: False, 3: False, 5: False, 10: False},
        reciprocal_rank=0.0,
        top1_retrieved_chunk_id=None,
        top1_correct=False
    )
