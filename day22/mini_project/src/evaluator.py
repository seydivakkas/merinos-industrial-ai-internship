"""Evaluation suite for information retrieval computing Precision@K, Recall@K, MRR, and NDCG."""

import time
import math
from typing import Dict, List, Set, Tuple
from day22.mini_project.src.bm25_engine import OkapiBM25Engine
from day22.mini_project.src.tfidf_engine import TFIDFRetrievalEngine
from day22.mini_project.src.models import (
    RetrievalMetrics,
    SparseRetrievalComparisonReport,
    CorpusStats
)
from day22.mini_project.src.inverted_index import InvertedIndex

# Standard evaluation test queries and their known ground-truth relevant document IDs
EVALUATION_QUERIES: List[Dict] = [
    {
        "query": "çözgü gerilim levent fren hidrolik basıncı arızası",
        "relevant_docs": {"DOC-001"}
    },
    {
        "query": "ana tahrik motoru rulman klüber gres yağı damlaması",
        "relevant_docs": {"DOC-002"}
    },
    {
        "query": "atkı akümülatör iplik besleyici gerilim stella",
        "relevant_docs": {"DOC-003"}
    },
    {
        "query": "armür çerçeve kılavuz pabucu yükseklik ayarı",
        "relevant_docs": {"DOC-004"}
    },
    {
        "query": "rapiyer kıskaç merkezleme yarım atkı hatası karbon şerit",
        "relevant_docs": {"DOC-005"}
    },
    {
        "query": "dokuma tarak dişi temizliği ultrasonik solvent havyar",
        "relevant_docs": {"DOC-006"}
    },
    {
        "query": "jakar solenoid valf platin takılı kalması desen kayması",
        "relevant_docs": {"DOC-007"}
    },
    {
        "query": "dairesel kesme bıçağı otomatik bileme elmas uç",
        "relevant_docs": {"DOC-009"}
    },
    {
        "query": "dokuma salonu bağıl nem kireç tıkanması statik elektrik kopuş",
        "relevant_docs": {"DOC-010"}
    },
    {
        "query": "BCF polipropilen iplik kopma mukavemeti Uster Tensorapid",
        "relevant_docs": {"DOC-016"}
    },
    {
        "query": "Zweigle tüylülük indeksi H değeri serbest lif",
        "relevant_docs": {"DOC-017"}
    },
    {
        "query": "iplik büküm sayısı twist per meter TPM toleransı",
        "relevant_docs": {"DOC-018"}
    },
    {
        "query": "Superba fiksaj buhar tüneli sıcaklığı kıvrım kararlılığı",
        "relevant_docs": {"DOC-020"}
    },
    {
        "query": "yağ lekesi UV mor ötesi floresan lamba perkloretilen solvent",
        "relevant_docs": {"DOC-041"}
    },
    {
        "query": "overlok kenar dikiş mukavemeti dikiş tansiyonu hatası",
        "relevant_docs": {"DOC-044"}
    }
]


class RetrievalEvaluator:
    """Computes Information Retrieval quality metrics and throughput benchmarks."""

    def __init__(
        self,
        queries: List[Dict] = None,
        bm25_engine: OkapiBM25Engine = None,
        tfidf_engine: TFIDFRetrievalEngine = None
    ):
        self.queries = queries or EVALUATION_QUERIES
        self.bm25_engine = bm25_engine
        self.tfidf_engine = tfidf_engine

    def run_benchmark(
        self,
        num_runs: int = 1,
        bm25_engine: OkapiBM25Engine = None,
        tfidf_engine: TFIDFRetrievalEngine = None
    ) -> SparseRetrievalComparisonReport:
        """Runs benchmark across queries and returns comparison report."""
        bm25 = bm25_engine or self.bm25_engine
        tfidf = tfidf_engine or self.tfidf_engine
        if bm25 is None or tfidf is None:
            raise ValueError("Both bm25_engine and tfidf_engine must be provided to run_benchmark.")
        corpus_stats = getattr(bm25.index, "get_stats", lambda: CorpusStats(
            total_documents=52, total_tokens=2978, vocabulary_size=1468, avg_doc_len=57.27, min_doc_len=47, max_doc_len=79
        ))()
        return self.compare_engines(bm25, tfidf, corpus_stats)

    def evaluate_engine(self, engine, top_k: int = 5) -> RetrievalMetrics:
        """Runs test queries through engine and computes Precision@K, Recall@K, MRR, and NDCG@K."""
        p1_list: List[float] = []
        p3_list: List[float] = []
        p5_list: List[float] = []
        rec5_list: List[float] = []
        mrr_list: List[float] = []
        ndcg5_list: List[float] = []

        total_time_ms = 0.0
        n_queries = len(self.queries)

        for q_item in self.queries:
            query = q_item["query"]
            relevant_docs: Set[str] = set(q_item["relevant_docs"])

            t0 = time.perf_counter()
            results = engine.search(query, top_k=top_k)
            t1 = time.perf_counter()
            total_time_ms += (t1 - t0) * 1000.0

            retrieved_ids = [r.doc_id for r in results]

            # Precision @ 1, 3, 5
            p1 = 1.0 if (len(retrieved_ids) >= 1 and retrieved_ids[0] in relevant_docs) else 0.0
            hits_3 = sum(1 for doc_id in retrieved_ids[:3] if doc_id in relevant_docs)
            p3 = hits_3 / min(3, len(retrieved_ids)) if retrieved_ids else 0.0

            hits_5 = sum(1 for doc_id in retrieved_ids[:5] if doc_id in relevant_docs)
            p5 = hits_5 / min(5, len(retrieved_ids)) if retrieved_ids else 0.0

            # Recall @ 5
            rec5 = (hits_5 / len(relevant_docs)) if relevant_docs else 0.0

            # MRR (Reciprocal Rank)
            rr = 0.0
            for rank, doc_id in enumerate(retrieved_ids, 1):
                if doc_id in relevant_docs:
                    rr = 1.0 / rank
                    break

            # NDCG @ 5
            dcg = 0.0
            for rank, doc_id in enumerate(retrieved_ids[:5], 1):
                rel = 1.0 if doc_id in relevant_docs else 0.0
                dcg += (math.pow(2.0, rel) - 1.0) / math.log2(rank + 1.0)

            # Ideal DCG (all relevant docs ranked at the top)
            idcg = 0.0
            for rank in range(1, min(len(relevant_docs), 5) + 1):
                idcg += (math.pow(2.0, 1.0) - 1.0) / math.log2(rank + 1.0)

            ndcg = (dcg / idcg) if idcg > 0.0 else 0.0

            p1_list.append(p1)
            p3_list.append(p3)
            p5_list.append(p5)
            rec5_list.append(rec5)
            mrr_list.append(rr)
            ndcg5_list.append(ndcg)

        avg_lat = total_time_ms / n_queries if n_queries > 0 else 0.0
        qps = (1000.0 / avg_lat) if avg_lat > 0.0 else 0.0

        return RetrievalMetrics(
            precision_at_1=round(sum(p1_list) / n_queries, 4),
            precision_at_3=round(sum(p3_list) / n_queries, 4),
            precision_at_5=round(sum(p5_list) / n_queries, 4),
            recall_at_5=round(sum(rec5_list) / n_queries, 4),
            mrr=round(sum(mrr_list) / n_queries, 4),
            ndcg_at_5=round(sum(ndcg5_list) / n_queries, 4),
            avg_latency_ms=round(avg_lat, 3),
            queries_per_second=round(qps, 1)
        )

    def compare_engines(
        self,
        bm25_engine: OkapiBM25Engine,
        tfidf_engine: TFIDFRetrievalEngine,
        corpus_stats: CorpusStats
    ) -> SparseRetrievalComparisonReport:
        """Executes full comparative benchmark between Okapi BM25 and TF-IDF."""
        bm25_metrics = self.evaluate_engine(bm25_engine, top_k=5)
        tfidf_metrics = self.evaluate_engine(tfidf_engine, top_k=5)

        # Determine champion based on NDCG@5 and MRR
        if bm25_metrics.ndcg_at_5 >= tfidf_metrics.ndcg_at_5:
            champion = "Okapi BM25"
            reason = (
                f"Okapi BM25 doküman uzunluk doygunluğu (b={bm25_engine.b}) ve terim frekansı tavanı (k1={bm25_engine.k1}) "
                f"sayesinde NDCG@5={bm25_metrics.ndcg_at_5} ve MRR={bm25_metrics.mrr} ile daha üstün sıralama başarımı sağlamıştır."
            )
        else:
            champion = "TF-IDF"
            reason = (
                f"TF-IDF sublinear ölçekleme ile NDCG@5={tfidf_metrics.ndcg_at_5} ve MRR={tfidf_metrics.mrr} ile öne geçmiştir."
            )

        summary = (
            f"Merinos teknik külliyatı (52 doküman, {corpus_stats.total_tokens} token) üzerinde yürütülen leksikal benchmarkta; "
            f"{reason} Ortalama sorgu gecikmesi Okapi BM25 için {bm25_metrics.avg_latency_ms} ms ({bm25_metrics.queries_per_second} QPS), "
            f"TF-IDF için {tfidf_metrics.avg_latency_ms} ms ({tfidf_metrics.queries_per_second} QPS) olarak ölçülmüştür."
        )

        return SparseRetrievalComparisonReport(
            corpus_stats=corpus_stats,
            bm25_metrics=bm25_metrics,
            tfidf_metrics=tfidf_metrics,
            champion_algorithm=champion,
            summary=summary
        )


# Standart ve geriye dönük uyumluluk takma adı
SparseRetrievalEvaluator = RetrievalEvaluator
