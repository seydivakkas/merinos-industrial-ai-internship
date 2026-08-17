"""
Merinos Industrial AI Internship - Day 24
Hybrid Retrieval & Rank Fusion Benchmark Evaluator

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
import json
import numpy as np
import time

from day24.mini_project.src.models import (
    EvaluationMetrics,
    HybridRetrievalBenchmarkReport,
    RawDocument
)
from day24.mini_project.src.pipeline import ThreeStageHybridPipeline
from day24.mini_project.src.hybrid_engine import MerinosHybridSearchEngine
from day23.mini_project.src.cross_encoder_reranker import CrossEncoderReranker


BENCHMARK_QUERIES = [
    {
        "query": "çözgü gerilim levent fren hidrolik basıncı arızası",
        "relevant_docs": ["DOC-001"]
    },
    {
        "query": "ana tahrik motoru rulman klüber gres yağı damlaması",
        "relevant_docs": ["DOC-002"]
    },
    {
        "query": "atkı akümülatör iplik besleyici gerilim stella",
        "relevant_docs": ["DOC-003"]
    },
    {
        "query": "armür çerçeve kılavuz pabucu yükseklik ayarı",
        "relevant_docs": ["DOC-004"]
    },
    {
        "query": "rapiyer kıskaç merkezleme yarım atkı hatası karbon şerit",
        "relevant_docs": ["DOC-005"]
    },
    {
        "query": "dokuma tarak dişi temizliği ultrasonik solvent havyar",
        "relevant_docs": ["DOC-006"]
    },
    {
        "query": "jakar solenoid valf platin takılı kalması desen kayması",
        "relevant_docs": ["DOC-007"]
    },
    {
        "query": "dairesel kesme bıçağı otomatik bileme elmas uç",
        "relevant_docs": ["DOC-009"]
    },
    {
        "query": "dokuma salonu bağıl nem kireç tıkanması statik elektrik kopuş",
        "relevant_docs": ["DOC-010"]
    },
    {
        "query": "BCF polipropilen iplik kopma mukavemeti Uster Tensorapid",
        "relevant_docs": ["DOC-016"]
    },
    {
        "query": "Zweigle tüylülük indeksi H değeri serbest lif",
        "relevant_docs": ["DOC-017"]
    },
    {
        "query": "iplik büküm sayısı twist per meter TPM toleransı",
        "relevant_docs": ["DOC-018"]
    },
    {
        "query": "Superba fiksaj buhar tüneli sıcaklığı kıvrım kararlılığı",
        "relevant_docs": ["DOC-020"]
    },
    {
        "query": "yağ lekesi UV mor ötesi floresan lamba perkloretilen solvent",
        "relevant_docs": ["DOC-041"]
    },
    {
        "query": "overlok kenar dikiş mukavemeti dikiş tansiyonu hatası",
        "relevant_docs": ["DOC-044"]
    }
]


class HybridRetrievalEvaluator:
    """
    BM25, Dense, RRF Hybrid, Weighted Hybrid ve Three-Stage Re-ranked modellerini
    15 kurumsal teknik sorguda karşılaştıran benchmark motoru.
    """

    def __init__(
        self,
        pipeline: Optional[ThreeStageHybridPipeline] = None,
        corpus: Optional[List[RawDocument]] = None,
        corpus_path: Optional[Union[Path, str]] = None
    ):
        self.pipeline = pipeline
        self.corpus: List[RawDocument] = corpus or []
        self.corpus_path = Path(corpus_path) if corpus_path else None

    def initialize(self) -> None:
        """Külliyatı yükler ve pipeline motorlarını hazır hale getirir."""
        if self.corpus_path and not self.corpus:
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.corpus = [
                RawDocument(
                    doc_id=item.get("id") or item.get("doc_id"),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    category=item.get("category", ""),
                    tags=item.get("tags") or item.get("keywords") or [],
                    metadata=item.get("metadata", {}),
                )
                for item in data
            ]

        if self.pipeline is None:
            self.pipeline = ThreeStageHybridPipeline()

        if self.corpus:
            self.pipeline.index_corpus(self.corpus)

    def _compute_metrics(
        self,
        retrieved_ids_list: List[List[str]],
        ground_truth_list: List[List[str]]
    ) -> EvaluationMetrics:
        """P@1, P@3, P@5, Recall@5, MRR ve NDCG@5 hesaplar."""
        p1_list, p3_list, p5_list = [], [], []
        r5_list = []
        rr_list = []
        ndcg5_list = []

        for retrieved, relevant in zip(retrieved_ids_list, ground_truth_list):
            rel_set = set(relevant)
            if not rel_set:
                continue

            k1 = retrieved[:1]
            k3 = retrieved[:3]
            k5 = retrieved[:5]

            p1 = len([d for d in k1 if d in rel_set]) / 1.0
            p3 = len([d for d in k3 if d in rel_set]) / 3.0
            p5 = len([d for d in k5 if d in rel_set]) / 5.0
            r5 = len([d for d in k5 if d in rel_set]) / float(len(rel_set))

            rr = 0.0
            for rank, doc in enumerate(retrieved, start=1):
                if doc in rel_set:
                    rr = 1.0 / rank
                    break

            dcg5 = 0.0
            for rank, doc in enumerate(k5, start=1):
                rel = 1.0 if doc in rel_set else 0.0
                dcg5 += rel / np.log2(rank + 1)

            idcg5 = sum([1.0 / np.log2(r + 1) for r in range(1, min(len(rel_set), 5) + 1)])
            ndcg5 = (dcg5 / idcg5) if idcg5 > 0 else 0.0

            p1_list.append(p1)
            p3_list.append(p3)
            p5_list.append(p5)
            r5_list.append(r5)
            rr_list.append(rr)
            ndcg5_list.append(ndcg5)

        return EvaluationMetrics(
            precision_at_1=float(np.mean(p1_list)) if p1_list else 0.0,
            precision_at_3=float(np.mean(p3_list)) if p3_list else 0.0,
            precision_at_5=float(np.mean(p5_list)) if p5_list else 0.0,
            recall_at_5=float(np.mean(r5_list)) if r5_list else 0.0,
            mrr=float(np.mean(rr_list)) if rr_list else 0.0,
            ndcg_at_5=float(np.mean(ndcg5_list)) if ndcg5_list else 0.0
        )

    def tune_alpha(
        self,
        alphas: Optional[List[float]] = None,
        queries_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[float, float]:
        """Farklı alpha değerleri için MRR skorlarını hesaplar ve döndürür."""
        alpha_grid = alphas if alphas is not None else [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
        target_data = queries_data or BENCHMARK_QUERIES
        queries = [item["query"] for item in target_data]
        ground_truths = [item["relevant_docs"] for item in target_data]

        results = {}
        for a in alpha_grid:
            retrieved = []
            for q in queries:
                fused, _, _, _ = self.pipeline.hybrid_engine.search_hybrid_weighted(
                    query=q,
                    alpha=a,
                    top_k=5
                )
                retrieved.append([r.doc_id for r in fused])
            m = self._compute_metrics(retrieved, ground_truths)
            results[a] = m.mrr

        return results

    def tune_alpha_grid(
        self,
        top_k: int = 5,
        alpha_steps: Optional[List[float]] = None,
        queries_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Alpha optimizasyonu grid search sonuçlarını detaylı metriklerle döndürür."""
        alphas = alpha_steps or [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        target_data = queries_data or BENCHMARK_QUERIES
        queries = [item["query"] for item in target_data]
        ground_truths = [item["relevant_docs"] for item in target_data]

        grid_results = []
        for a in alphas:
            retrieved = []
            for q in queries:
                fused, _, _, _ = self.pipeline.hybrid_engine.search_hybrid_weighted(
                    query=q,
                    alpha=a,
                    top_k=top_k
                )
                retrieved.append([r.doc_id for r in fused])
            m = self._compute_metrics(retrieved, ground_truths)
            grid_results.append({
                "alpha": float(a),
                "ndcg_at_5": m.ndcg_at_5,
                "mrr_at_5": m.mrr,
                "hit_rate_at_5": m.recall_at_5,
            })
        return grid_results

    def run_benchmark(
        self,
        queries_data: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 5,
        rrf_k: int = 60,
        alpha: float = 0.5,
        num_runs: int = 1
    ) -> HybridRetrievalBenchmarkReport:
        """5 modelin karşılaştırmalı benchmark raporunu oluşturur."""
        target_data = queries_data or BENCHMARK_QUERIES
        queries = [item["query"] for item in target_data]
        ground_truths = [item["relevant_docs"] for item in target_data]

        # 1. BM25
        bm25_retrieved, bm25_times = [], []
        for q in queries:
            t0 = time.perf_counter()
            hits = self.pipeline.hybrid_engine.search_sparse(q, top_k=top_k)
            t1 = time.perf_counter()
            bm25_times.append((t1 - t0) * 1000.0)
            bm25_retrieved.append([h.doc_id for h in hits])
        bm25_metrics = self._compute_metrics(bm25_retrieved, ground_truths)
        bm25_latency = float(np.mean(bm25_times)) if bm25_times else 1.0

        # 2. Dense Qdrant
        dense_retrieved, dense_times = [], []
        for q in queries:
            t0 = time.perf_counter()
            hits = self.pipeline.hybrid_engine.search_dense(q, top_k=top_k)
            t1 = time.perf_counter()
            dense_times.append((t1 - t0) * 1000.0)
            dense_retrieved.append([h.doc_id for h in hits])
        dense_metrics = self._compute_metrics(dense_retrieved, ground_truths)
        dense_latency = float(np.mean(dense_times)) if dense_times else 1.0

        # 3. RRF Hybrid
        rrf_retrieved, rrf_times = [], []
        for q in queries:
            t0 = time.perf_counter()
            fused, _, _, _ = self.pipeline.hybrid_engine.search_hybrid_rrf(q, top_k=top_k)
            t1 = time.perf_counter()
            rrf_times.append((t1 - t0) * 1000.0)
            rrf_retrieved.append([f.doc_id for f in fused])
        rrf_metrics = self._compute_metrics(rrf_retrieved, ground_truths)
        rrf_latency = float(np.mean(rrf_times)) if rrf_times else 1.0

        # 4. Weighted Linear Hybrid (alpha)
        weighted_retrieved, weighted_times = [], []
        for q in queries:
            t0 = time.perf_counter()
            fused, _, _, _ = self.pipeline.hybrid_engine.search_hybrid_weighted(q, alpha=alpha, top_k=top_k)
            t1 = time.perf_counter()
            weighted_times.append((t1 - t0) * 1000.0)
            weighted_retrieved.append([f.doc_id for f in fused])
        weighted_metrics = self._compute_metrics(weighted_retrieved, ground_truths)
        weighted_latency = float(np.mean(weighted_times)) if weighted_times else 1.0

        # 5. Three-Stage Re-ranked Hybrid
        reranked_retrieved, reranked_times = [], []
        for q in queries:
            t0 = time.perf_counter()
            res, _, _, _ = self.pipeline.search_and_rerank(
                query=q,
                first_stage_pool_size=15,
                fused_top_k=10,
                final_top_k=top_k,
                use_rrf=True
            )
            t1 = time.perf_counter()
            reranked_times.append((t1 - t0) * 1000.0)
            reranked_retrieved.append([r.doc_id for r in res])
        reranked_metrics = self._compute_metrics(reranked_retrieved, ground_truths)
        reranked_latency = float(np.mean(reranked_times)) if reranked_times else 1.0

        # Alpha grid tuning
        alpha_scores = self.tune_alpha(queries_data=target_data)
        best_alpha = max(alpha_scores.items(), key=lambda x: x[1])[0]

        return HybridRetrievalBenchmarkReport(
            bm25_metrics=bm25_metrics,
            dense_metrics=dense_metrics,
            rrf_hybrid_metrics=rrf_metrics,
            weighted_hybrid_metrics=weighted_metrics,
            reranked_hybrid_metrics=reranked_metrics,
            bm25_latency_ms=bm25_latency,
            dense_latency_ms=dense_latency,
            rrf_latency_ms=rrf_latency,
            weighted_latency_ms=weighted_latency,
            reranked_latency_ms=reranked_latency,
            bm25_qps=float(1000.0 / bm25_latency) if bm25_latency > 0 else 0.0,
            dense_qps=float(1000.0 / dense_latency) if dense_latency > 0 else 0.0,
            rrf_qps=float(1000.0 / rrf_latency) if rrf_latency > 0 else 0.0,
            weighted_qps=float(1000.0 / weighted_latency) if weighted_latency > 0 else 0.0,
            reranked_qps=float(1000.0 / reranked_latency) if reranked_latency > 0 else 0.0,
            total_documents=len(self.corpus),
            rrf_k=rrf_k,
            best_alpha=best_alpha,
            models_info={
                "sparse_engine": "Okapi BM25 (k1=1.5, b=0.75)",
                "dense_engine": "Qdrant Bi-Encoder (all-MiniLM-L6-v2, 384-d)",
                "fusion": f"Reciprocal Rank Fusion (k={rrf_k})",
                "reranker": "Cross-Encoder (ms-marco-TinyBERT-L-2-v2)"
            }
        )

    def evaluate_all(
        self,
        top_k: int = 5,
        rrf_k: int = 60,
        alpha: float = 0.5
    ) -> HybridRetrievalBenchmarkReport:
        """evaluate_all takma adı."""
        return self.run_benchmark(top_k=top_k, rrf_k=rrf_k, alpha=alpha)

    def save_benchmark_report(
        self,
        report: HybridRetrievalBenchmarkReport,
        output_path: Union[Path, str]
    ) -> Dict[str, Any]:
        """Raporu JSON formatında kaydeder ve sözlük olarak döndürür."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        report_data = report.model_dump()
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        return report_data
