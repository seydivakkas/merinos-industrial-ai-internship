"""
Merinos Industrial AI Internship - Day 26
Unit & Integration Tests for Vector Indexing & Optimization Suite

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import pytest
import json
from pathlib import Path
import numpy as np

from day26.mini_project.src.models import (
    VectorPoint,
    FilterCondition,
    PayloadFilter,
    SearchResult,
    IndexBenchmarkMetrics,
    VectorIndexReport
)
from day26.mini_project.src.quantization import ScalarQuantizer, ProductQuantizer
from day26.mini_project.src.ivf_index import InvertedFileIndex
from day26.mini_project.src.hnsw_index import HNSWVectorIndex
from day26.mini_project.src.qdrant_manager import QdrantVectorStore
from day26.mini_project.src.benchmarker import VectorIndexBenchmarker, ExactFlatSearcher
from day26.mini_project.src.visualizer import plot_vector_index_diagnostic_panel


@pytest.fixture
def sample_points() -> list[VectorPoint]:
    """Testler için 20 adet sentetik vektör noktası üretir."""
    np.random.seed(42)
    dim = 64
    points = []
    departments = ["DOKUMA_TEZGAHI_BAKIM", "IPLIK_LABORATUVAR_STANDARTLARI", "KALITE_GUVENCE_VE_HATA_TRIAJ"]
    machines = ["Van de Wiele RCE02", "Neumag S+ BCF", "Schönherr Alpha 500"]

    for i in range(1, 21):
        vec = np.random.randn(dim).astype(np.float32)
        vec = (vec / np.linalg.norm(vec)).tolist()
        dept = departments[i % len(departments)]
        mach = machines[i % len(machines)]
        points.append(
            VectorPoint(
                point_id=i,
                chunk_id=f"chk_{i:03d}",
                doc_id=f"SOP-{i:03d}",
                title=f"Test SOP {i}",
                breadcrumbs=f"Test > Makine {mach}",
                content=f"Örnek içerik metni {i} için bakım talimatı.",
                machine=mach,
                department=dept,
                component="Rulman",
                priority="CRITICAL" if i % 2 == 0 else "NORMAL",
                char_length=150,
                token_count=25,
                vector=vec
            )
        )
    return points


@pytest.fixture
def sample_query(sample_points) -> dict:
    """Testler için ilk noktanın vektörüne yakın bir sorgu üretir."""
    q_vec = list(sample_points[0].vector)
    return {
        "query_id": "Q-TEST-01",
        "query": "Van de Wiele RCE02 bakım prosedürü",
        "filter": {"department": "DOKUMA_TEZGAHI_BAKIM"},
        "vector": q_vec
    }


def test_scalar_quantizer_compression_and_error(sample_points):
    """Skaler kuantizasyonun boyut küçültmesini ve kosinüs rekonstrüksiyon doğruluğunu test eder."""
    mat = np.array([p.vector for p in sample_points], dtype=np.float32)
    quantizer = ScalarQuantizer()
    quantizer.fit(mat)

    quantized, scales, offsets = quantizer.quantize(mat)

    # 1. Veri tipi uint8 olmalı (1 bayt)
    assert quantized.dtype == np.uint8
    assert quantized.shape == mat.shape

    # 2. Rekonstrüksiyon doğruluğu
    reconstructed = quantizer.dequantize(quantized, scales, offsets)
    # Cosine fidelity
    sims = np.sum(mat * reconstructed, axis=1)
    mean_sim = float(np.mean(sims))
    assert mean_sim > 0.95, f"Kuantizasyon kosinüs benzerliği çok düşük: {mean_sim}"


def test_product_quantizer_encoding(sample_points):
    """Ürün kuantizasyonunun (PQ) alt-vektör kodlamasını test eder."""
    mat = np.array([p.vector for p in sample_points], dtype=np.float32)
    num_subvectors = 4
    pq = ProductQuantizer(num_subvectors=num_subvectors, num_clusters=4)
    pq.fit(mat)

    codes = pq.encode(mat)
    assert codes.shape == (len(sample_points), num_subvectors)
    assert codes.dtype == np.uint8
    assert len(pq.codebooks) == num_subvectors


def test_ivf_index_construction_and_search(sample_points, sample_query):
    """IVF indeksinin Voronoi hücre inşasını ve arama kabiliyetini test eder."""
    ivf = InvertedFileIndex(nlist=4, nprobe=2)
    ivf.build_index(sample_points)

    assert ivf.is_built
    assert len(ivf.inverted_lists) == 4

    q_vec = np.array(sample_query["vector"], dtype=np.float32)
    results = ivf.search(q_vec, top_k=3)

    assert len(results) == 3
    assert all(isinstance(r, SearchResult) for r in results)
    assert results[0].score >= results[1].score >= results[2].score


def test_hnsw_graph_construction_and_search(sample_points, sample_query):
    """HNSW grafının çok katmanlı yapısını ve logaritmik aramasını test eder."""
    hnsw = HNSWVectorIndex(m=8, ef_construct=16, ef_search=16)
    hnsw.build_index(sample_points)

    assert hnsw.entry_point is not None
    assert len(hnsw.graphs) >= 1

    q_vec = np.array(sample_query["vector"], dtype=np.float32)
    results = hnsw.search(q_vec, top_k=3)

    assert len(results) == 3
    assert results[0].score <= 1.0


def test_payload_pre_filtering_and_selectivity(sample_points, sample_query):
    """Payload filtrelemenin ilgisiz departmanları kesinlikle dışlamasını test eder."""
    flat = ExactFlatSearcher(sample_points)
    target_dept = "DOKUMA_TEZGAHI_BAKIM"
    p_filter = PayloadFilter.from_dict({"department": target_dept})

    q_vec = np.array(sample_query["vector"], dtype=np.float32)
    results = flat.search(q_vec, top_k=5, payload_filter=p_filter)

    assert len(results) > 0
    for r in results:
        assert r.payload["department"] == target_dept


def test_qdrant_manager_in_memory_hnsw(sample_points, sample_query):
    """Qdrant in-memory istemcisinin HNSW koleksiyonu kurup arama yapmasını test eder."""
    store = QdrantVectorStore(collection_name="test_qdrant_hnsw", dimension=64)
    store.create_collection(m=8, ef_construct=16, use_quantization=False)
    store.upsert_points(sample_points)

    assert store.count_points() == len(sample_points)

    results = store.search(sample_query["vector"], top_k=3)
    assert len(results) == 3
    assert results[0].score > 0.5


def test_qdrant_scalar_quantization(sample_points, sample_query):
    """Qdrant in-memory istemcisinin Int8 Skaler Kuantizasyon ile çalışmasını test eder."""
    store = QdrantVectorStore(collection_name="test_qdrant_sq", dimension=64)
    store.create_collection(m=8, ef_construct=16, use_quantization=True)
    store.upsert_points(sample_points)

    results = store.search(sample_query["vector"], top_k=3)
    assert len(results) == 3
    assert results[0].score > 0.5


def test_qdrant_payload_filtered_search(sample_points, sample_query):
    """Qdrant üzerinde FieldCondition tabanlı filtrelenmiş aramayı test eder."""
    store = QdrantVectorStore(collection_name="test_qdrant_filtered", dimension=64)
    store.create_collection(m=8, ef_construct=16, use_quantization=False)
    store.upsert_points(sample_points)

    p_filter = PayloadFilter.from_dict({"priority": "CRITICAL"})
    results = store.search(sample_query["vector"], top_k=5, payload_filter=p_filter)

    assert len(results) > 0
    for r in results:
        assert r.payload.get("priority") == "CRITICAL"


def test_benchmark_runner_and_report(sample_points, sample_query):
    """4 indeks mimarisinin (Flat, IVF, HNSW, Quantized HNSW) kıyaslama raporunu test eder."""
    benchmarker = VectorIndexBenchmarker()
    report = benchmarker.run_benchmark(sample_points, [sample_query])

    assert isinstance(report, VectorIndexReport)
    assert set(report.indices.keys()) == {"exact_flat", "ivf", "hnsw", "quantized_hnsw"}

    for k, m in report.indices.items():
        assert m.indexing_time_ms >= 0.0
        assert m.query_latency_ms >= 0.0
        assert 0.0 <= m.recall_at_5 <= 1.0
        assert m.memory_kb > 0.0


def test_diagnostic_panel_plot(tmp_path, sample_points, sample_query):
    """2x2 Master Tanı Panelinin çizdirilip PNG olarak kaydedilmesini test eder."""
    benchmarker = VectorIndexBenchmarker()
    report = benchmarker.run_benchmark(sample_points, [sample_query])

    out_file = tmp_path / "test_vector_index_panel.png"
    result_path = plot_vector_index_diagnostic_panel(report, out_file)

    assert result_path.exists()
    assert result_path.stat().st_size > 10000
