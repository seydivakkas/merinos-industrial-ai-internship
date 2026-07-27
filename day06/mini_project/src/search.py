"""
Merinos Industrial AI Internship - Day 06
search.py: Vector Similarity Search Engine & Retrieval Benchmark
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import time
import numpy as np

from day06.mini_project.src import metrics
from day06.mini_project.src.scalers import StandardScaler, MinMaxScaler, L2Normalizer
from day06.mini_project.src.curse_analyzer import CurseOfDimensionalityAnalyzer


class VectorSimilaritySearchEngine:
    """Brute-force k-NN vector search engine across multiple distance metrics and scaling methods."""

    def __init__(
        self,
        embeddings: np.ndarray,
        product_ids: List[str],
        collections: List[str],
        cov_inv: Optional[np.ndarray] = None,
    ):
        self.raw_embeddings = embeddings.astype(np.float32)
        self.product_ids = list(product_ids)
        self.collections = list(collections)
        self.n_samples, self.dim = self.raw_embeddings.shape

        # Precompute covariance inverse for Mahalanobis
        if cov_inv is not None:
            self.cov_inv = cov_inv
        else:
            cov = np.cov(self.raw_embeddings, rowvar=False)
            reg = np.eye(self.dim) * 1e-6
            self.cov_inv = np.linalg.pinv(cov + reg).astype(np.float32)

    def search(
        self,
        query_vector: np.ndarray,
        metric: str = "cosine",
        top_k: int = 5,
        scaling: str = "none",
        exclude_self_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Searches for Top-K most similar items given a query vector."""
        q = query_vector.reshape(1, -1).astype(np.float32)
        X = self.raw_embeddings

        # Apply scaling if requested
        if scaling == "standard":
            scaler = StandardScaler().fit(X)
            X = scaler.transform(X)
            q = scaler.transform(q)
        elif scaling == "min_max":
            scaler = MinMaxScaler().fit(X)
            X = scaler.transform(X)
            q = scaler.transform(q)
        elif scaling == "l2_normalized":
            X = L2Normalizer.transform(X)
            q = L2Normalizer.transform(q)

        # Compute distances from query to all items
        if metric == "euclidean":
            dists = metrics.pairwise_euclidean(q, X)[0]  # (N,)
            sims = 1.0 / (1.0 + dists)
        elif metric == "manhattan":
            dists = metrics.pairwise_manhattan(q, X)[0]
            sims = 1.0 / (1.0 + dists)
        elif metric == "cosine":
            sims = metrics.pairwise_cosine_similarity(q, X)[0]
            dists = 1.0 - sims
        elif metric == "mahalanobis":
            dists = metrics.pairwise_mahalanobis(q, X, self.cov_inv)[0]
            sims = 1.0 / (1.0 + dists)
        else:
            raise ValueError(f"Unknown metric: '{metric}'")

        # Sort indices ascending by distance
        sorted_indices = np.argsort(dists)

        results = []
        for idx in sorted_indices:
            p_id = self.product_ids[idx]
            if exclude_self_id and p_id == exclude_self_id:
                continue

            results.append({
                "product_id": p_id,
                "collection": self.collections[idx],
                "distance": round(float(dists[idx]), 4),
                "similarity": round(float(sims[idx]), 4),
            })

            if len(results) >= top_k:
                break

        return results

    def compare_metrics_for_item(self, item_index: int = 0, top_k: int = 5) -> Dict[str, Any]:
        """Compares Top-K retrieved nearest neighbors across all distance metrics for a target item."""
        target_id = self.product_ids[item_index]
        target_col = self.collections[item_index]
        query_vec = self.raw_embeddings[item_index]

        metric_names = ["cosine", "euclidean", "manhattan", "mahalanobis"]
        comparison: Dict[str, List[Dict[str, Any]]] = {}

        for m in metric_names:
            neighbors = self.search(query_vec, metric=m, top_k=top_k, exclude_self_id=target_id)
            comparison[m] = neighbors

        return {
            "query_product_id": target_id,
            "query_collection": target_col,
            "top_k": top_k,
            "comparisons": comparison,
        }


def run_benchmark_and_generate_artifacts(
    fixtures_path: Union[str, Path],
    output_dir: Union[str, Path],
) -> Dict[str, Any]:
    """Orchestrates metric benchmarking, curse of dimensionality analysis, and generates reports."""
    fixtures_path = Path(fixtures_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = np.load(fixtures_path, allow_pickle=True)
    product_ids = [str(x) for x in data["product_ids"]]
    collections = [str(x) for x in data["collections"]]
    embeds_32d = data["embeddings_32d"]
    embeds_128d = data["embeddings_128d"]

    engine = VectorSimilaritySearchEngine(
        embeddings=embeds_128d,
        product_ids=product_ids,
        collections=collections,
    )

    # 1. Benchmark Pairwise Latencies
    benchmark_timings = {}
    N = 100
    for m in ["cosine", "euclidean", "manhattan", "mahalanobis"]:
        t0 = time.perf_counter()
        for _ in range(20):
            if m == "cosine":
                _ = metrics.pairwise_cosine_similarity(embeds_128d)
            elif m == "euclidean":
                _ = metrics.pairwise_euclidean(embeds_128d)
            elif m == "manhattan":
                _ = metrics.pairwise_manhattan(embeds_128d)
            elif m == "mahalanobis":
                _ = metrics.pairwise_mahalanobis(embeds_128d, cov_inv=engine.cov_inv)
        t1 = time.perf_counter()
        avg_ms = ((t1 - t0) / 20.0) * 1000.0
        benchmark_timings[m] = {
            "pairwise_matrix_shape": f"{N}x{N}",
            "vector_dimension": 128,
            "latency_ms": round(avg_ms, 3),
            "throughput_pairs_per_sec": int((N * N) / (avg_ms / 1000.0)),
        }

    # 2. Curse of Dimensionality Analysis
    curse_report = CurseOfDimensionalityAnalyzer.run_multi_dimensional_analysis(
        dimensions=[2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
        n_samples=500,
        metric="euclidean",
    )

    # 3. Top-K Search Sample Comparison
    search_sample = engine.compare_metrics_for_item(item_index=0, top_k=5)

    # 4. Save JSON Artifacts
    bench_file = output_dir / "similarity_benchmark.json"
    with open(bench_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_timings, f, indent=2, ensure_ascii=False)

    curse_file = output_dir / "curse_of_dimensionality_report.json"
    with open(curse_file, "w", encoding="utf-8") as f:
        json.dump(curse_report, f, indent=2, ensure_ascii=False)

    search_file = output_dir / "topk_search_sample.json"
    with open(search_file, "w", encoding="utf-8") as f:
        json.dump(search_sample, f, indent=2, ensure_ascii=False)

    # 5. Generate Markdown Summary
    md_lines = [
        "# Merinos Industrial AI — Day 06: Vektör Benzerlik ve Mesafe Metrikleri Raporu",
        "",
        "> **Aşama:** Faz 1: Çevre & Veri Temelleri (Kapanış)  ",
        f"> **Tarih:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        "",
        "## 1. Çiftli (Pairwise) Mesafe Hesaplama Performansı (100x100 Matris, 128 Boyut)",
        "",
        "| Metrik | Gecikme (ms) | Throughput (Çift/sn) | Matematiksel Formül | Endüstriyel Özellik |",
        f"| **Cosine** | **`{benchmark_timings['cosine']['latency_ms']} ms`** | `{benchmark_timings['cosine']['throughput_pairs_per_sec']:,}` | S_C = (u . v) / (||u|| ||v||) | Normdan bağımsız, açısal yönelim |",
        f"| **Euclidean (L2)** | **`{benchmark_timings['euclidean']['latency_ms']} ms`** | `{benchmark_timings['euclidean']['throughput_pairs_per_sec']:,}` | d_2 = ||u - v||_2 | Geometrik mesafe, ölçeğe duyarlı |",
        f"| **Manhattan (L1)** | **`{benchmark_timings['manhattan']['latency_ms']} ms`** | `{benchmark_timings['manhattan']['throughput_pairs_per_sec']:,}` | d_1 = sum |u_i - v_i| | Aykırı değerlere (outliers) dayanıklı |",
        f"| **Mahalanobis** | **`{benchmark_timings['mahalanobis']['latency_ms']} ms`** | `{benchmark_timings['mahalanobis']['throughput_pairs_per_sec']:,}` | d_M = sqrt((u-v)^T Sigma^-1 (u-v)) | Kovaryans ve korelasyon düzeltmeli |",
        "",
        "## 2. Boyutsallık Laneti (Curse of Dimensionality / Distance Concentration)",
        "",
        f"- **İncelenen Boyut Aralığı:** D = 2 ile D = 1024",
        f"- **Kontrast Azalma Çarpanı:** **`{curse_report['contrast_decay_ratio']}x`** kayıp",
        f"- **D=2 Kontrastı:** `{curse_report['results'][0]['relative_contrast']}` -> **D=1024 Kontrastı:** `{curse_report['results'][-1]['relative_contrast']}`",
        "",
        "## 3. Top-K Arama Karşılaştırması (`MRP-1001` için İlk 3 Sonuç)",
        "",
        f"- **Sorgu:** `{search_sample['query_product_id']}` (Koleksiyon: `{search_sample['query_collection']}`)",
    ]

    for m, items in search_sample["comparisons"].items():
        top_items = ", ".join([f"`{it['product_id']}` ({it['collection']}: {it['distance']})" for it in items[:3]])
        md_lines.append(f"- **{m.title()}:** {top_items}")

    md_lines.extend([
        "",
        "## 4. Faz 1 Mühendislik Çıkarımları",
        "1. **Birim Vektörde Kosinüs-Öklid Eşitliği:** $L_2$ normalize vektörlerde $d_E^2 = 2(1 - S_C)$ olduğundan, yüksek hızlı iç çarpım (dot product) doğrudan Öklid sıralamasını verir.",
        "2. **Ölçekleme Zorunluluğu:** Fiziksel üretim metrikleri (hav: 10 mm, ilmek: 500,000) bir arada arandığında MinMaxScaler / StandardScaler uygulanmazsa mesafe tek bir sütun tarafından domine edilir.",
        "3. **Faz 2'ye Geçiş:** Faz 1 (Veri & Çevre) başarıyla mühürlenmiş; Faz 2'de (OpenCV ve Bilgisayarlı Görü) pikseller üzerinden renk uzayları, homografi ve doku analizine geçilmeye hazır olunmuştur.",
    ])

    summary_file = output_dir / "similarity_metrics_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return {
        "benchmarks": benchmark_timings,
        "curse_report": curse_report,
        "search_sample": search_sample,
        "benchmark_file": str(bench_file),
        "curse_file": str(curse_file),
        "search_file": str(search_file),
        "summary_file": str(summary_file),
    }


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    f_path = base_dir / "fixtures" / "carpet_feature_embeddings.npz"
    o_dir = base_dir / "outputs"
    print("=" * 60)
    print("Running Day 06 Vector Similarity Pipeline...")
    res = run_benchmark_and_generate_artifacts(f_path, o_dir)
    print("Execution complete!")
    print(f"Summary generated at: {res['summary_file']}")
    print("=" * 60)
