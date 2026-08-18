"""
Merinos Industrial AI Internship - Day 25
Document Chunking Benchmark & Retrieval Evaluator

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import time
import math
import re
from pathlib import Path
import numpy as np
import hashlib

from day25.mini_project.src.models import (
    DocumentItem,
    ChunkItem,
    ChunkingStats,
    RetrievalMetrics,
    StrategyEvaluationResult,
    ChunkingBenchmarkReport
)
from day25.mini_project.src.chunk_engine import MerinosChunkEngine


class ChunkingBenchmarkEvaluator:
    """
    4 farklı metin parçalama stratejisinin (Fixed, Recursive, Semantic, Markdown-Aware)
    geometrik istatistiklerini, anlamsal tutarlılığını (intra-chunk coherence) ve
    bilgi getirme (P@1, Recall@5, MRR, NDCG@5, Needle hit rate) başarımını kıyaslayan değerlendirici.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        self.config = config or {}
        self.model_name = self.config.get("evaluation", {}).get("dense_model_name", model_name)
        self.top_k = self.config.get("evaluation", {}).get("top_k", 5)
        self.device = device
        self.engine = MerinosChunkEngine(self.config)

        self.model = None
        self._load_dense_model()

    def _load_dense_model(self) -> None:
        """SentenceTransformer modelini yükler veya deterministik fallback hazırlar."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception:
            self.model = None

    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        """Metin listesini normalize edilmiş yoğun vektörlere dönüştürür."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
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
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            words = text.lower().split()
            for i, w in enumerate(words):
                h = int(hashlib.sha256(w.encode("utf-8")).hexdigest()[:8], 16)
                idx = h % dim
                sign = 1.0 if (h // dim) % 2 == 0 else -1.0
                vec[idx] += sign * (1.0 / (1.0 + 0.05 * (i % 20)))
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)

    def compute_intra_chunk_coherence(self, chunks: List[ChunkItem], sample_limit: int = 60) -> float:
        """
        Parça içi ardışık cümlelerin kosinüs benzerliğini hesaplayarak
        anlamsal tutarlılık (intra-chunk coherence) skorunu üretir.
        """
        if not chunks:
            return 0.0

        sample_chunks = chunks[:sample_limit]
        coherence_scores: List[float] = []

        for chk in sample_chunks:
            # Cümlelere böl
            sentences = [s.strip() for s in re.split(r"(?<=[.?!])\s+", chk.content) if len(s.strip()) > 10]
            if len(sentences) < 2:
                # Tek cümle veya çok kısa parça, kendi içinde tutarlıdır
                coherence_scores.append(0.85)
                continue

            # Cümleleri encode et
            emb = self._encode_texts(sentences)
            sims = []
            for i in range(len(emb) - 1):
                sim = float(np.dot(emb[i], emb[i + 1]))
                # -1 ile 1 arasından [0, 1] aralığına normalize et
                sim_norm = max(0.0, min(1.0, (sim + 1.0) / 2.0))
                sims.append(sim_norm)

            if sims:
                coherence_scores.append(float(np.mean(sims)))
            else:
                coherence_scores.append(0.80)

        return float(np.mean(coherence_scores)) if coherence_scores else 0.0

    def calculate_chunk_stats(
        self,
        strategy: str,
        chunks: List[ChunkItem],
        raw_corpus_char_len: int
    ) -> ChunkingStats:
        """Parçaların geometrik boyut ve dağılım istatistiklerini hesaplar."""
        if not chunks:
            return ChunkingStats(
                strategy=strategy,
                total_chunks=0,
                mean_char_length=0.0,
                median_char_length=0.0,
                min_char_length=0,
                max_char_length=0,
                std_char_length=0.0,
                mean_token_count=0.0,
                intra_chunk_coherence=0.0,
                breadcrumb_coverage_ratio=0.0,
                redundancy_ratio=1.0
            )

        lengths = [c.char_length for c in chunks]
        tokens = [c.token_count for c in chunks]

        # Breadcrumb kapsama oranı (1'den fazla seviye başlık içeren veya başlık yolu olan parçalar)
        breadcrumb_count = sum(1 for c in chunks if len(c.section_headers) > 1 or c.metadata.get("breadcrumbs"))
        coverage_ratio = float(breadcrumb_count / len(chunks))

        # Redundancy oranı (toplam parça karakteri / orijinal metin karakteri)
        total_chunk_chars = sum(lengths)
        redundancy = float(total_chunk_chars / raw_corpus_char_len) if raw_corpus_char_len > 0 else 1.0

        # Anlamsal tutarlılık
        coherence = self.compute_intra_chunk_coherence(chunks)

        return ChunkingStats(
            strategy=strategy,
            total_chunks=len(chunks),
            mean_char_length=float(np.mean(lengths)),
            median_char_length=float(np.median(lengths)),
            min_char_length=int(np.min(lengths)),
            max_char_length=int(np.max(lengths)),
            std_char_length=float(np.std(lengths)),
            mean_token_count=float(np.mean(tokens)),
            intra_chunk_coherence=coherence,
            breadcrumb_coverage_ratio=coverage_ratio,
            redundancy_ratio=redundancy
        )

    def evaluate_retrieval(
        self,
        chunks: List[ChunkItem],
        queries: List[Dict[str, Any]]
    ) -> Tuple[RetrievalMetrics, float, float]:
        """
        Verilen parçalar üzerinde vektör indeksi kurar ve test sorguları ile
        P@1, Recall@5, MRR, NDCG@5 ve Needle hit rate metriklerini hesaplar.
        """
        if not chunks or not queries:
            return (
                RetrievalMetrics(
                    precision_at_1=0.0,
                    recall_at_5=0.0,
                    mrr=0.0,
                    ndcg_at_5=0.0,
                    needle_hit_rate_at_1=0.0,
                    needle_hit_rate_at_5=0.0
                ),
                0.0,
                0.0
            )

        # 1. İndeksleme aşaması
        t0_idx = time.perf_counter()
        # Arama için zenginleştirilmiş metin: Başlık yolu + Parça içeriği
        indexing_texts = [
            f"{c.breadcrumb_str}\n{c.content}" if c.breadcrumb_str != c.title else c.content
            for c in chunks
        ]
        chunk_embeddings = self._encode_texts(indexing_texts)
        indexing_latency_ms = (time.perf_counter() - t0_idx) * 1000.0

        # 2. Sorgu aşaması
        t0_qry = time.perf_counter()
        query_texts = [q["query"] for q in queries]
        query_embeddings = self._encode_texts(query_texts)

        p1_list: List[float] = []
        r5_list: List[float] = []
        mrr_list: List[float] = []
        ndcg_list: List[float] = []
        needle_hit1_list: List[float] = []
        needle_hit5_list: List[float] = []

        for q_idx, q_item in enumerate(queries):
            target_doc_id = q_item["target_doc_id"]
            target_fact = q_item.get("target_fact", "").strip().lower()

            q_vec = query_embeddings[q_idx]
            # Kosinüs benzerliği
            scores = np.dot(chunk_embeddings, q_vec)
            top_k_indices = np.argsort(-scores)[:self.top_k]

            retrieved_chunks = [chunks[i] for i in top_k_indices]
            retrieved_doc_ids = [c.doc_id for c in retrieved_chunks]

            # Precision@1
            p1 = 1.0 if (retrieved_doc_ids and retrieved_doc_ids[0] == target_doc_id) else 0.0
            p1_list.append(p1)

            # Recall@5
            r5 = 1.0 if target_doc_id in retrieved_doc_ids else 0.0
            r5_list.append(r5)

            # MRR
            mrr = 0.0
            for rank, d_id in enumerate(retrieved_doc_ids, start=1):
                if d_id == target_doc_id:
                    mrr = 1.0 / rank
                    break
            mrr_list.append(mrr)

            # NDCG@5 (İkili ilgi düzeyi: 1 if doc_id == target else 0)
            dcg = 0.0
            for rank, d_id in enumerate(retrieved_doc_ids, start=1):
                rel = 1.0 if d_id == target_doc_id else 0.0
                dcg += rel / math.log2(rank + 1)
            
            # İdeal DCG: Korpus içindeki hedef dokümana ait toplam parça sayısı veya top-k kadar 1.0
            total_relevant = sum(1 for c in chunks if c.doc_id == target_doc_id)
            ideal_hits = min(total_relevant, self.top_k)
            if ideal_hits > 0:
                idcg = sum(1.0 / math.log2(r + 1) for r in range(1, ideal_hits + 1))
                ndcg = min(1.0, dcg / idcg)
            else:
                ndcg = 0.0
            ndcg_list.append(ndcg)

            # Needle-in-a-haystack fact hit
            hit1 = 0.0
            hit5 = 0.0
            if target_fact:
                # Top 1 parça hedef bilgiyi barındırıyor mu?
                if retrieved_chunks and target_fact in retrieved_chunks[0].content.lower():
                    hit1 = 1.0
                # Top 5 parçadan en az biri barındırıyor mu?
                for c in retrieved_chunks:
                    if target_fact in c.content.lower():
                        hit5 = 1.0
                        break
            needle_hit1_list.append(hit1)
            needle_hit5_list.append(hit5)

        total_query_latency_ms = (time.perf_counter() - t0_qry) * 1000.0
        avg_query_latency_ms = total_query_latency_ms / len(queries) if queries else 0.0

        metrics = RetrievalMetrics(
            precision_at_1=float(np.mean(p1_list)),
            recall_at_5=float(np.mean(r5_list)),
            mrr=float(np.mean(mrr_list)),
            ndcg_at_5=float(np.mean(ndcg_list)),
            needle_hit_rate_at_1=float(np.mean(needle_hit1_list)),
            needle_hit_rate_at_5=float(np.mean(needle_hit5_list))
        )

        return metrics, indexing_latency_ms, avg_query_latency_ms

    def evaluate_strategy(
        self,
        strategy: str,
        corpus: List[DocumentItem],
        queries: List[Dict[str, Any]]
    ) -> StrategyEvaluationResult:
        """Tek bir parçalama stratejisinin uçtan uca değerlendirmesini yapar."""
        raw_corpus_chars = sum(len(d.content) for d in corpus)

        # 1. Parçalama
        chunks = self.engine.chunk_corpus(corpus, strategy)

        # 2. Geometrik İstatistikler & Coherence
        stats = self.calculate_chunk_stats(strategy, chunks, raw_corpus_chars)

        # 3. Retrieval Değerlendirmesi
        retrieval, idx_lat, qry_lat = self.evaluate_retrieval(chunks, queries)

        return StrategyEvaluationResult(
            strategy_name=strategy,
            stats=stats,
            retrieval=retrieval,
            indexing_latency_ms=idx_lat,
            query_latency_ms=qry_lat
        )

    def run_benchmark(
        self,
        corpus: List[DocumentItem],
        queries: List[Dict[str, Any]]
    ) -> ChunkingBenchmarkReport:
        """4 parçalama stratejisinin tamamı için büyük kıyaslamayı çalıştırır."""
        results: Dict[str, StrategyEvaluationResult] = {}

        for strat in self.engine.AVAILABLE_STRATEGIES:
            res = self.evaluate_strategy(strat, corpus, queries)
            results[strat] = res

        # En başarılı stratejilerin tespiti
        best_retrieval = max(results.keys(), key=lambda s: results[s].retrieval.ndcg_at_5)
        best_coherence = max(results.keys(), key=lambda s: results[s].stats.intra_chunk_coherence)

        report = ChunkingBenchmarkReport(
            strategies=results,
            total_documents=len(corpus),
            total_queries=len(queries),
            best_retrieval_strategy=best_retrieval,
            best_coherence_strategy=best_coherence,
            config_summary=self.config
        )

        return report
