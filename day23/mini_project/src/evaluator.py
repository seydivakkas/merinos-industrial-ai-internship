"""
Merinos Industrial AI Internship - Day 23
Dense Retrieval & Re-ranking Benchmark Evaluator

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Tuple, Any
import numpy as np
import time

from day23.mini_project.src.models import (
    EvaluationMetrics,
    DenseRetrievalBenchmarkReport,
    RawDocument
)
from day23.mini_project.src.pipeline import TwoStageRetrievalPipeline
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.tokenizer import MerinosTextTokenizer
from day22.mini_project.src.bm25_engine import OkapiBM25Engine


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


class DenseRetrievalEvaluator:
    """
    Bi-Encoder, Two-Stage Re-ranked ve BM25 modellerini 15 kurumsal teknik
    sorguda doğruluk, sıralama ve gecikme metrikleriyle kıyaslayan motor.
    """

    def __init__(
        self,
        pipeline: TwoStageRetrievalPipeline,
        corpus: List[RawDocument]
    ):
        self.pipeline = pipeline
        self.corpus = corpus

        # Day 22 BM25 referans motorunu kur
        self.tokenizer = MerinosTextTokenizer()
        self.inverted_index = InvertedIndex(tokenizer=self.tokenizer)
        from day22.mini_project.src.models import RawDocument as D22RawDoc
        d22_docs = [D22RawDoc(**doc.model_dump()) for doc in corpus]
        self.inverted_index.build(d22_docs)
        self.bm25_engine = OkapiBM25Engine(self.inverted_index, self.tokenizer, k1=1.5, b=0.75)

    def _compute_metrics(
        self,
        retrieved_ids_list: List[List[str]],
        ground_truth_list: List[List[str]]
    ) -> EvaluationMetrics:
        """Precision@K, Recall@K, MRR ve NDCG@K metriklerini hesaplar."""
        p1_list, p3_list, p5_list = [], [], []
        r5_list = []
        rr_list = []
        ndcg5_list = []

        for retrieved, relevant in zip(retrieved_ids_list, ground_truth_list):
            rel_set = set(relevant)
            if not rel_set:
                continue

            # Precision @ K
            k1 = retrieved[:1]
            k3 = retrieved[:3]
            k5 = retrieved[:5]

            p1 = len([doc for doc in k1 if doc in rel_set]) / 1.0
            p3 = len([doc for doc in k3 if doc in rel_set]) / 3.0
            p5 = len([doc for doc in k5 if doc in rel_set]) / 5.0

            # Recall @ 5
            r5 = len([doc for doc in k5 if doc in rel_set]) / float(len(rel_set))

            # MRR (Reciprocal Rank of first relevant item)
            rr = 0.0
            for rank, doc in enumerate(retrieved, start=1):
                if doc in rel_set:
                    rr = 1.0 / rank
                    break

            # NDCG @ 5
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
            precision_at_1=float(np.mean(p1_list)),
            precision_at_3=float(np.mean(p3_list)),
            precision_at_5=float(np.mean(p5_list)),
            recall_at_5=float(np.mean(r5_list)),
            mrr=float(np.mean(rr_list)),
            ndcg_at_5=float(np.mean(ndcg5_list))
        )

    def run_benchmark(
        self,
        queries_data: Optional[List[Dict[str, Any]]] = None,
        num_runs: int = 5
    ) -> DenseRetrievalBenchmarkReport:
        """Sorgularda tüm modelleri çalıştırır ve benchmark raporu oluşturur."""
        target_data = queries_data or BENCHMARK_QUERIES
        queries = [item["query"] for item in target_data]
        ground_truths = [item["relevant_docs"] for item in target_data]

        # 1. Bi-Encoder Arama
        bi_retrieved = []
        bi_times = []
        for _ in range(num_runs):
            for q in queries:
                t0 = time.perf_counter()
                results = self.pipeline.search_first_stage(q, top_k=5, use_qdrant=True)
                t1 = time.perf_counter()
                bi_times.append((t1 - t0) * 1000.0)

        for q in queries:
            results = self.pipeline.search_first_stage(q, top_k=5, use_qdrant=True)
            bi_retrieved.append([r.doc_id for r in results])

        bi_metrics = self._compute_metrics(bi_retrieved, ground_truths)
        bi_latency_ms = float(np.mean(bi_times))
        bi_qps = float(1000.0 / bi_latency_ms) if bi_latency_ms > 0 else 0.0

        # 2. Two-Stage Re-ranked Arama
        reranked_retrieved = []
        reranked_times = []
        for _ in range(num_runs):
            for q in queries:
                t0 = time.perf_counter()
                results, _, _ = self.pipeline.search_and_rerank(
                    query=q,
                    first_stage_top_k=10,
                    final_top_k=5,
                    use_qdrant=True
                )
                t1 = time.perf_counter()
                reranked_times.append((t1 - t0) * 1000.0)

        for q in queries:
            results, _, _ = self.pipeline.search_and_rerank(
                query=q,
                first_stage_top_k=10,
                final_top_k=5,
                use_qdrant=True
            )
            reranked_retrieved.append([r.doc_id for r in results])

        reranked_metrics = self._compute_metrics(reranked_retrieved, ground_truths)
        reranked_latency_ms = float(np.mean(reranked_times))
        reranked_qps = float(1000.0 / reranked_latency_ms) if reranked_latency_ms > 0 else 0.0

        # 3. BM25 Referans Arama
        bm25_retrieved = []
        bm25_times = []
        for _ in range(num_runs):
            for q in queries:
                t0 = time.perf_counter()
                results = self.bm25_engine.search(q, top_k=5)
                t1 = time.perf_counter()
                bm25_times.append((t1 - t0) * 1000.0)

        for q in queries:
            results = self.bm25_engine.search(q, top_k=5)
            bm25_retrieved.append([r.doc_id for r in results])

        bm25_metrics = self._compute_metrics(bm25_retrieved, ground_truths)
        bm25_latency_ms = float(np.mean(bm25_times))
        bm25_qps = float(1000.0 / bm25_latency_ms) if bm25_latency_ms > 0 else 0.0

        return DenseRetrievalBenchmarkReport(
            bi_encoder_metrics=bi_metrics,
            reranked_metrics=reranked_metrics,
            bm25_metrics=bm25_metrics,
            bi_encoder_latency_ms=bi_latency_ms,
            reranked_latency_ms=reranked_latency_ms,
            bm25_latency_ms=bm25_latency_ms,
            bi_encoder_qps=bi_qps,
            reranked_qps=reranked_qps,
            bm25_qps=bm25_qps,
            total_documents=len(self.corpus),
            embedding_dimension=self.pipeline.bi_encoder.embedding_dim,
            models_info={
                "bi_encoder": self.pipeline.bi_encoder.model_name,
                "cross_encoder": self.pipeline.reranker.model_name,
                "vector_db": "Qdrant (In-Memory / HNSW)"
            }
        )
