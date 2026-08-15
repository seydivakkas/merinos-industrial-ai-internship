"""
Merinos Industrial AI Internship - Day 23
Dense Retrieval & Re-ranking Unit and Integration Tests

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import pytest
import numpy as np
from pathlib import Path
import json

from day23.mini_project.src.models import (
    RawDocument,
    DenseSearchResultItem,
    ReRankedResultItem,
    EvaluationMetrics,
    DenseRetrievalBenchmarkReport
)
from day23.mini_project.src.bi_encoder import BiEncoderDenseRetriever
from day23.mini_project.src.vector_store import QdrantVectorStore
from day23.mini_project.src.cross_encoder_reranker import CrossEncoderReranker
from day23.mini_project.src.pipeline import TwoStageRetrievalPipeline
from day23.mini_project.src.evaluator import DenseRetrievalEvaluator
from day23.mini_project.src.visualizer import plot_dense_retrieval_panel


@pytest.fixture
def sample_documents() -> list[RawDocument]:
    return [
        RawDocument(
            doc_id="DOC-001",
            title="Van de Wiele Tezgâhı Atkı İpliği Kopması ve IRO Stella Arıza Protokolü",
            content="Van de Wiele jakarlı halı dokuma tezgâhlarında atkı ipliği koptuğunda IRO Stella besleyicisindeki optik sensör tetiklenir ve tezgâh ERR-W-204 hatası verir.",
            category="WEAVING",
            tags=["atkı", "iro stella", "kopma", "ERR-W-204"]
        ),
        RawDocument(
            doc_id="DOC-016",
            title="Bonas Jakar Tezgâhında Desen Kayması ve Enkoder Senkronizasyonu",
            content="Jakar kafası desen kayması optik mil enkoderinin ana krank miliyle faz farkı oluşturmasından kaynaklanır. ERR-J-108 arızasında kaplin kontrol edilir.",
            category="JACQUARD",
            tags=["jakar", "desen kayması", "enkoder", "ERR-J-108"]
        ),
        RawDocument(
            doc_id="DOC-027",
            title="BCF Polipropilen İplik Ekstrüzyon Hattında Sıcaklık Dalgalanması",
            content="BCF polipropilen iplik çekim hattında vida kovanı ısıtıcı rezistanslarının arızalanması sonucu ekstrüder sıcaklığı dalgalanır. ERR-Y-501 eriyik viskozitesi bozulur.",
            category="YARN",
            tags=["ekstrüzyon", "sıcaklık", "BCF", "ERR-Y-501"]
        ),
        RawDocument(
            doc_id="DOC-039",
            title="Buharlama Fikse Fırınında Basınç Kaybı ve Vana Sızdırmazlığı",
            content="Sürekli buharlama fikse fırınında pnömatik basınç düşüşü yaşandığında fikse odası sıcaklığı homojenliğini kaybeder. ERR-D-701 oransal buhar vanası contası kontrol edilir.",
            category="DYEING_FINISHING",
            tags=["fikse", "buharlama", "basınç", "ERR-D-701"]
        )
    ]


def test_bi_encoder_embedding_generation_and_norm(sample_documents):
    """Bi-Encoder vektör boyutu (384) ve L2 normalizasyonu testi."""
    retriever = BiEncoderDenseRetriever()
    texts = [f"{d.title} {d.content}" for d in sample_documents]
    embeddings = retriever.encode(texts)

    assert embeddings.shape == (len(sample_documents), 384)
    norms = np.linalg.norm(embeddings, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-3)


def test_bi_encoder_search_exact_and_semantic(sample_documents):
    """Bi-Encoder ile semantik benzerlik ve sıralama testi."""
    retriever = BiEncoderDenseRetriever()
    retriever.index_corpus(sample_documents)

    results = retriever.search("Bonas Jakar Tezgâhında Desen Kayması ve Enkoder", top_k=2)
    assert len(results) == 2
    assert results[0].doc_id == "DOC-016"
    assert results[0].score > 0.0
    assert "ERR-J-108" in results[0].snippet or "Jakar" in results[0].snippet


def test_qdrant_vector_store_initialization_and_upsert(sample_documents):
    """Qdrant in-memory koleksiyonu oluşturma ve doküman yükleme testi."""
    store = QdrantVectorStore(in_memory=True)
    retriever = BiEncoderDenseRetriever()
    embeddings = retriever.index_corpus(sample_documents)

    count = store.upsert_documents(sample_documents, embeddings)
    assert count == len(sample_documents)
    assert store.count() == len(sample_documents)


def test_qdrant_search_and_category_filtering(sample_documents):
    """Qdrant kategori filtresi (WEAVING vs JACQUARD) denetimi."""
    store = QdrantVectorStore(in_memory=True)
    retriever = BiEncoderDenseRetriever()
    embeddings = retriever.index_corpus(sample_documents)
    store.upsert_documents(sample_documents, embeddings)

    query_vec = retriever.encode_query("arıza ve bakım kılavuzu")
    # Filtresiz arama
    all_res = store.search(query_vec, top_k=4)
    assert len(all_res) == 4

    # Yalnızca JACQUARD kategorisi
    jacquard_res = store.search(query_vec, top_k=4, category_filter="JACQUARD")
    assert len(jacquard_res) == 1
    assert jacquard_res[0].doc_id == "DOC-016"
    assert jacquard_res[0].category == "JACQUARD"


def test_cross_encoder_predict_pairs_and_sigmoid():
    """Cross-Encoder metin çifti puanlaması ve sigmoid kalibrasyonu testi."""
    reranker = CrossEncoderReranker(apply_sigmoid=True)
    pairs = [
        ("atkı ipliği kopması", "Van de Wiele atkı ipliği koptuğunda IRO Stella alarm verir"),
        ("atkı ipliği kopması", "Buharlama fırınında buhar vanası basınç contası kontrol edilir")
    ]
    scores = reranker.predict_pairs(pairs)
    assert len(scores) == 2
    assert np.all(scores >= 0.0) and np.all(scores <= 1.0)
    # Alakalı cümlenin skoru alakasızdan yüksek olmalıdır
    assert scores[0] > scores[1]


def test_cross_encoder_rerank_candidates(sample_documents):
    """Cross-Encoder'ın Bi-Encoder adaylarını başarıyla yeniden puanlaması testi."""
    reranker = CrossEncoderReranker(apply_sigmoid=True)
    candidates = [
        DenseSearchResultItem(
            doc_id="DOC-039",
            title="Buharlama Fikse Fırınında Basınç Kaybı",
            score=0.45,
            rank=1,
            snippet="Buharlama fırını...",
            category="DYEING_FINISHING"
        ),
        DenseSearchResultItem(
            doc_id="DOC-001",
            title="Van de Wiele Tezgâhı Atkı İpliği Kopması",
            score=0.42,
            rank=2,
            snippet="Atkı ipliği kopması...",
            category="WEAVING"
        )
    ]
    doc_dict = {d.doc_id: d for d in sample_documents}
    reranked = reranker.rerank(
        query="atkı ipliği kopması IRO Stella",
        candidates=candidates,
        doc_store=doc_dict,
        top_k=2
    )

    assert len(reranked) == 2
    # Re-ranking sonrası DOC-001 ilk sıraya yükselmelidir
    assert reranked[0].doc_id == "DOC-001"
    assert reranked[0].rank == 1
    assert reranked[0].cross_encoder_score > reranked[1].cross_encoder_score


def test_two_stage_pipeline_end_to_end(sample_documents):
    """İki aşamalı getirme hattının (Retrieve + Re-rank) uçtan uca çalışması testi."""
    retriever = BiEncoderDenseRetriever()
    reranker = CrossEncoderReranker(apply_sigmoid=True)
    store = QdrantVectorStore(in_memory=True)

    pipeline = TwoStageRetrievalPipeline(bi_encoder=retriever, reranker=reranker, vector_store=store)
    pipeline.index_corpus(sample_documents)

    results, bi_time, ce_time = pipeline.search_and_rerank(
        query="jakar desen kayması ve enkoder hatası",
        first_stage_top_k=3,
        final_top_k=1,
        use_qdrant=True
    )

    assert len(results) == 1
    assert results[0].doc_id == "DOC-016"
    assert bi_time >= 0.0
    assert ce_time >= 0.0


def test_evaluator_metrics_calculation(sample_documents):
    """Değerlendirme metriklerinin (P@K, Recall@K, MRR, NDCG@K) matematiksel doğruluğu."""
    retriever = BiEncoderDenseRetriever()
    reranker = CrossEncoderReranker()
    pipeline = TwoStageRetrievalPipeline(bi_encoder=retriever, reranker=reranker)
    pipeline.index_corpus(sample_documents)

    evaluator = DenseRetrievalEvaluator(pipeline=pipeline, corpus=sample_documents)

    retrieved = [["DOC-001", "DOC-016", "DOC-027"]]
    ground_truth = [["DOC-001"]]

    metrics = evaluator._compute_metrics(retrieved, ground_truth)
    assert metrics.precision_at_1 == 1.0
    assert metrics.mrr == 1.0
    assert metrics.recall_at_5 == 1.0
    assert metrics.ndcg_at_5 == 1.0


def test_cli_commands_execution(tmp_path):
    """CLI uç noktalarının argparse üzerinden test edilmesi."""
    from day23.mini_project.src import cli
    corpus_file, output_dir = cli.get_default_paths()
    assert Path(corpus_file).exists()

    corpus = cli.load_corpus(corpus_file)
    assert len(corpus) >= 4


def test_dense_retrieval_benchmark_and_panel_generation(sample_documents, tmp_path):
    """Benchmark raporu ve 2x2 master panel PNG üretim entegrasyonu."""
    retriever = BiEncoderDenseRetriever()
    reranker = CrossEncoderReranker()
    store = QdrantVectorStore(in_memory=True)
    pipeline = TwoStageRetrievalPipeline(bi_encoder=retriever, reranker=reranker, vector_store=store)
    pipeline.index_corpus(sample_documents)

    evaluator = DenseRetrievalEvaluator(pipeline=pipeline, corpus=sample_documents)
    sample_queries = [
        {"query": "Bonas Jakar Tezgâhında Desen Kayması", "relevant_docs": ["DOC-016"]},
        {"query": "BCF Polipropilen İplik Ekstrüzyon Hattında Sıcaklık", "relevant_docs": ["DOC-027"]},
        {"query": "Buharlama Fikse Fırınında Basınç Kaybı", "relevant_docs": ["DOC-039"]}
    ]
    report = evaluator.run_benchmark(queries_data=sample_queries, num_runs=1)

    assert report.total_documents == len(sample_documents)
    assert report.embedding_dimension == 384
    assert report.reranked_metrics.precision_at_1 >= 0.8

    png_path = tmp_path / "test_panel.png"
    out_file = plot_dense_retrieval_panel(
        report=report,
        bi_encoder=retriever,
        reranker=reranker,
        corpus=sample_documents,
        output_path=str(png_path)
    )

    assert Path(out_file).exists()
    assert Path(out_file).stat().st_size > 10000
