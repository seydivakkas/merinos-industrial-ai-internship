"""
Merinos Industrial AI Internship - Day 26
Vector Index & Quantization Performance Benchmarker

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Tuple, Optional
import time
import math
import numpy as np

from day26.mini_project.src.models import (
    VectorPoint,
    SearchResult,
    PayloadFilter,
    IndexBenchmarkMetrics,
    VectorIndexReport
)
from day26.mini_project.src.ivf_index import InvertedFileIndex
from day26.mini_project.src.hnsw_index import HNSWVectorIndex
from day26.mini_project.src.qdrant_manager import QdrantVectorStore


class ExactFlatSearcher:
    """Tam Kosinüs Kaba Kuvvet (Brute-Force) Referans Arayıcısı (Ground Truth)."""

    def __init__(self, points: List[VectorPoint]):
        self.points = list(points)
        raw_vecs = np.array([p.vector for p in points], dtype=np.float32)
        norms = np.linalg.norm(raw_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vectors = raw_vecs / norms

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        payload_filter: Optional[PayloadFilter] = None
    ) -> List[SearchResult]:
        q = query_vector.astype(np.float32)
        q_len = np.linalg.norm(q)
        if q_len > 0:
            q = q / q_len

        # Filtre uygula
        valid_indices = []
        if payload_filter is not None:
            for idx, p in enumerate(self.points):
                if payload_filter.evaluate(p.payload):
                    valid_indices.append(idx)
        else:
            valid_indices = list(range(len(self.points)))

        if not valid_indices:
            return []

        sub_vecs = self.vectors[valid_indices]
        scores = np.dot(sub_vecs, q)
        sorted_pos = np.argsort(-scores)[:top_k]

        results = []
        for rank, pos in enumerate(sorted_pos, start=1):
            p_idx = valid_indices[pos]
            pt = self.points[p_idx]
            results.append(
                SearchResult(
                    point_id=pt.point_id,
                    score=float(scores[pos]),
                    payload=pt.payload,
                    content=pt.content,
                    rank=rank
                )
            )
        return results

    def estimate_memory_bytes(self) -> int:
        return self.vectors.nbytes


class VectorIndexBenchmarker:
    """
    Flat (Ground Truth), IVF, HNSW ve Kuantize HNSW indekslerini
    hız (QPS), gecikme (ms), bellek (RAM) ve arama doğruluğu (Recall@K)
    açısından kıyaslayan büyük test motoru.
    """

    def __init__(
        self,
        points: Optional[List[VectorPoint]] = None,
        queries: Optional[List[Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        if isinstance(points, dict) and config is None:
            config = points
            points = None

        self.points = points or []
        self.queries = queries or []
        self.config = config or {}
        self.top_k = self.config.get("evaluation", {}).get("top_k", 5)
        self.runs = self.config.get("evaluation", {}).get("runs_per_query", 3)

    def run_full_benchmark(self, top_k: int = 5) -> VectorIndexReport:
        """Kayıtlı noktalar ve sorgular üzerinde tam kıyaslama çalıştırır."""
        self.top_k = top_k
        return self.run_benchmark(self.points, self.queries)

    def _calc_recall_and_ndcg(
        self,
        actual_results: List[SearchResult],
        ground_truth_results: List[SearchResult]
    ) -> Tuple[float, float, float]:
        """Ground truth sonuçlarına göre Recall@K, Precision@1 ve NDCG@K hesaplar."""
        if not ground_truth_results:
            return 1.0, 1.0, 1.0

        gt_ids = set(r.point_id for r in ground_truth_results)
        actual_ids = [r.point_id for r in actual_results]

        # Recall@K
        hits = sum(1 for pid in actual_ids if pid in gt_ids)
        recall = float(hits / len(gt_ids))

        # Precision@1
        p1 = 1.0 if (actual_ids and actual_ids[0] in gt_ids) else 0.0

        # NDCG@K (GT sıralamasına göre derecelendirilmiş ilgi düzeyi)
        gt_ranking = {r.point_id: 1.0 / (rank + 1) for rank, r in enumerate(ground_truth_results)}
        dcg = 0.0
        for rank, pid in enumerate(actual_ids, start=1):
            rel = gt_ranking.get(pid, 0.0)
            dcg += rel / math.log2(rank + 1)

        idcg = sum((1.0 / (r + 1)) / math.log2(r + 1) for r in range(1, len(gt_ids) + 1))
        ndcg = min(1.0, dcg / idcg) if idcg > 0 else 1.0

        return recall, p1, ndcg

    def run_benchmark(
        self,
        points: List[VectorPoint],
        queries: List[Dict[str, Any]]
    ) -> VectorIndexReport:
        """Tüm indeksler üzerinde büyük kıyaslama çalıştırır."""
        n_points = len(points)
        dim = len(points[0].vector) if points else 384

        # 1. Exact Flat Ground Truth Arayıcısı
        t0_flat = time.perf_counter()
        flat_searcher = ExactFlatSearcher(points)
        flat_idx_time = (time.perf_counter() - t0_flat) * 1000.0

        # Ground truth sonuçlarını önceden üret
        gt_unfiltered: List[List[SearchResult]] = []
        gt_filtered: List[List[SearchResult]] = []
        flat_latencies = []

        for q in queries:
            q_vec = np.array(q["vector"], dtype=np.float32)
            t_start = time.perf_counter()
            res = flat_searcher.search(q_vec, top_k=self.top_k)
            flat_latencies.append((time.perf_counter() - t_start) * 1000.0)
            gt_unfiltered.append(res)

            # Filtreli ground truth
            p_filter = PayloadFilter.from_dict(q.get("filter", {}))
            res_f = flat_searcher.search(q_vec, top_k=self.top_k, payload_filter=p_filter)
            gt_filtered.append(res_f)

        flat_avg_lat = float(np.mean(flat_latencies))
        flat_metrics = IndexBenchmarkMetrics(
            index_type="exact_flat",
            total_vectors=n_points,
            dimension=dim,
            indexing_time_ms=flat_idx_time,
            query_latency_ms=flat_avg_lat,
            qps=1000.0 / flat_avg_lat if flat_avg_lat > 0 else 0.0,
            memory_bytes=flat_searcher.estimate_memory_bytes(),
            memory_kb=float(flat_searcher.estimate_memory_bytes() / 1024.0),
            recall_at_5=1.0,
            precision_at_1=1.0,
            ndcg_at_5=1.0,
            filtered_recall_at_5=1.0
        )

        results: Dict[str, IndexBenchmarkMetrics] = {"exact_flat": flat_metrics}

        # 2. IVF İndeksi
        t0_ivf = time.perf_counter()
        ivf = InvertedFileIndex(nlist=8, nprobe=3)
        ivf.build_index(points)
        ivf_idx_time = (time.perf_counter() - t0_ivf) * 1000.0

        ivf_latencies, ivf_recalls, ivf_p1s, ivf_ndcgs, ivf_filt_recalls = [], [], [], [], []
        for idx, q in enumerate(queries):
            q_vec = np.array(q["vector"], dtype=np.float32)
            t_start = time.perf_counter()
            actual = ivf.search(q_vec, top_k=self.top_k)
            ivf_latencies.append((time.perf_counter() - t_start) * 1000.0)

            rec, p1, ndcg = self._calc_recall_and_ndcg(actual, gt_unfiltered[idx])
            ivf_recalls.append(rec)
            ivf_p1s.append(p1)
            ivf_ndcgs.append(ndcg)

            # Filtreli
            p_filter = PayloadFilter.from_dict(q.get("filter", {}))
            actual_f = ivf.search(q_vec, top_k=self.top_k, payload_filter=p_filter)
            f_rec, _, _ = self._calc_recall_and_ndcg(actual_f, gt_filtered[idx])
            ivf_filt_recalls.append(f_rec)

        ivf_avg_lat = float(np.mean(ivf_latencies))
        results["ivf"] = IndexBenchmarkMetrics(
            index_type="ivf",
            total_vectors=n_points,
            dimension=dim,
            indexing_time_ms=ivf_idx_time,
            query_latency_ms=ivf_avg_lat,
            qps=1000.0 / ivf_avg_lat if ivf_avg_lat > 0 else 0.0,
            memory_bytes=ivf.estimate_memory_bytes(),
            memory_kb=float(ivf.estimate_memory_bytes() / 1024.0),
            recall_at_5=float(np.mean(ivf_recalls)),
            precision_at_1=float(np.mean(ivf_p1s)),
            ndcg_at_5=float(np.mean(ivf_ndcgs)),
            filtered_recall_at_5=float(np.mean(ivf_filt_recalls))
        )

        # 3. HNSW İndeksi
        t0_hnsw = time.perf_counter()
        hnsw = HNSWVectorIndex(m=16, ef_construct=64, ef_search=32, use_quantization=False)
        hnsw.build_index(points)
        hnsw_idx_time = (time.perf_counter() - t0_hnsw) * 1000.0

        hnsw_latencies, hnsw_recalls, hnsw_p1s, hnsw_ndcgs, hnsw_filt_recalls = [], [], [], [], []
        for idx, q in enumerate(queries):
            q_vec = np.array(q["vector"], dtype=np.float32)
            t_start = time.perf_counter()
            actual = hnsw.search(q_vec, top_k=self.top_k)
            hnsw_latencies.append((time.perf_counter() - t_start) * 1000.0)

            rec, p1, ndcg = self._calc_recall_and_ndcg(actual, gt_unfiltered[idx])
            hnsw_recalls.append(rec)
            hnsw_p1s.append(p1)
            hnsw_ndcgs.append(ndcg)

            # Filtreli
            p_filter = PayloadFilter.from_dict(q.get("filter", {}))
            actual_f = hnsw.search(q_vec, top_k=self.top_k, payload_filter=p_filter)
            f_rec, _, _ = self._calc_recall_and_ndcg(actual_f, gt_filtered[idx])
            hnsw_filt_recalls.append(f_rec)

        hnsw_avg_lat = float(np.mean(hnsw_latencies))
        results["hnsw"] = IndexBenchmarkMetrics(
            index_type="hnsw",
            total_vectors=n_points,
            dimension=dim,
            indexing_time_ms=hnsw_idx_time,
            query_latency_ms=hnsw_avg_lat,
            qps=1000.0 / hnsw_avg_lat if hnsw_avg_lat > 0 else 0.0,
            memory_bytes=hnsw.estimate_memory_bytes(),
            memory_kb=float(hnsw.estimate_memory_bytes() / 1024.0),
            recall_at_5=float(np.mean(hnsw_recalls)),
            precision_at_1=float(np.mean(hnsw_p1s)),
            ndcg_at_5=float(np.mean(hnsw_ndcgs)),
            filtered_recall_at_5=float(np.mean(hnsw_filt_recalls))
        )

        # 4. Kuantize HNSW (SQ8 - Int8)
        t0_qhnsw = time.perf_counter()
        qhnsw = HNSWVectorIndex(m=16, ef_construct=64, ef_search=32, use_quantization=True)
        qhnsw.build_index(points)
        qhnsw_idx_time = (time.perf_counter() - t0_qhnsw) * 1000.0

        qhnsw_latencies, qhnsw_recalls, qhnsw_p1s, qhnsw_ndcgs, qhnsw_filt_recalls = [], [], [], [], []
        for idx, q in enumerate(queries):
            q_vec = np.array(q["vector"], dtype=np.float32)
            t_start = time.perf_counter()
            actual = qhnsw.search(q_vec, top_k=self.top_k)
            qhnsw_latencies.append((time.perf_counter() - t_start) * 1000.0)

            rec, p1, ndcg = self._calc_recall_and_ndcg(actual, gt_unfiltered[idx])
            qhnsw_recalls.append(rec)
            qhnsw_p1s.append(p1)
            qhnsw_ndcgs.append(ndcg)

            # Filtreli
            p_filter = PayloadFilter.from_dict(q.get("filter", {}))
            actual_f = qhnsw.search(q_vec, top_k=self.top_k, payload_filter=p_filter)
            f_rec, _, _ = self._calc_recall_and_ndcg(actual_f, gt_filtered[idx])
            qhnsw_filt_recalls.append(f_rec)

        qhnsw_avg_lat = float(np.mean(qhnsw_latencies))
        results["quantized_hnsw"] = IndexBenchmarkMetrics(
            index_type="quantized_hnsw",
            total_vectors=n_points,
            dimension=dim,
            indexing_time_ms=qhnsw_idx_time,
            query_latency_ms=qhnsw_avg_lat,
            qps=1000.0 / qhnsw_avg_lat if qhnsw_avg_lat > 0 else 0.0,
            memory_bytes=qhnsw.estimate_memory_bytes(),
            memory_kb=float(qhnsw.estimate_memory_bytes() / 1024.0),
            recall_at_5=float(np.mean(qhnsw_recalls)),
            precision_at_1=float(np.mean(qhnsw_p1s)),
            ndcg_at_5=float(np.mean(qhnsw_ndcgs)),
            filtered_recall_at_5=float(np.mean(qhnsw_filt_recalls))
        )

        # En başarılı indekslerin seçimi
        ann_keys = ["ivf", "hnsw", "quantized_hnsw"]
        best_qps = max(ann_keys, key=lambda k: results[k].qps)
        best_recall = max(ann_keys, key=lambda k: results[k].recall_at_5)
        most_memory_efficient = min(ann_keys, key=lambda k: results[k].memory_bytes)

        report = VectorIndexReport(
            indices=results,
            total_vectors=n_points,
            dimension=dim,
            total_queries=len(queries),
            best_qps_index=best_qps,
            best_recall_index=best_recall,
            most_memory_efficient_index=most_memory_efficient,
            config_summary=self.config
        )

        return report
