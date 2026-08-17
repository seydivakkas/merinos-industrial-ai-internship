"""Unit and Integration Tests for Day 24 Hybrid Retrieval (BM25 + Qdrant Dense via RRF).

Merinos Halı Sanayi ve Ticaret A.Ş. - Faz 4: Retrieval & Hibrit Arama
Day 24: Hibrit Arama ve Karşılıklı Sıra Füzyonu (Reciprocal Rank Fusion - RRF)
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from day24.mini_project.src.models import CandidateResult, RawDocument
from day24.mini_project.src.rrf_fusion import (
    min_max_normalize_scores,
    reciprocal_rank_fusion,
    weighted_linear_score_fusion,
)
from day24.mini_project.src.hybrid_engine import MerinosHybridSearchEngine
from day24.mini_project.src.pipeline import ThreeStageHybridPipeline
from day24.mini_project.src.evaluator import HybridRetrievalEvaluator
from day24.mini_project.src.visualizer import plot_hybrid_retrieval_panel
from day24.mini_project.src.cli import build_parser


@pytest.fixture
def sample_candidates() -> tuple[list[CandidateResult], list[CandidateResult]]:
    """Generates mock BM25 and Dense candidate lists for fusion testing."""
    bm25_list = [
        CandidateResult(
            doc_id="DOC-001",
            score=18.5,
            rank=1,
            title="Rapierli Dokuma Tezgâhı Yağlama Döngüleri",
            content="Rapierli tezgahlarda tahrik dişlileri ve rapier kafası 250 saatte bir ISO VG 220 ile yağlanmalıdır.",
            category="DOKUMA_TEZGAHI_BAKIM",
            channel="bm25",
        ),
        CandidateResult(
            doc_id="DOC-002",
            score=12.2,
            rank=2,
            title="Jakarlı Halı Dokuma Tarak Ayarı ve Hata Önleme",
            content="Tarak diş aralığı kalibre edilmezse atkı düzgünsüzlüğü oluşur.",
            category="DOKUMA_TEZGAHI_BAKIM",
            channel="bm25",
        ),
        CandidateResult(
            doc_id="DOC-003",
            score=8.1,
            rank=3,
            title="BCF Polipropilen İplik Büküm ve Mukavemet",
            content="BCF iplik mukavemet testi cN/dtex cinsinden ölçülür.",
            category="IPLIK_LABORATUVAR_STANDARTLARI",
            channel="bm25",
        ),
    ]

    dense_list = [
        CandidateResult(
            doc_id="DOC-002",
            score=0.88,
            rank=1,
            title="Jakarlı Halı Dokuma Tarak Ayarı ve Hata Önleme",
            content="Tarak diş aralığı kalibre edilmezse atkı düzgünsüzlüğü oluşur.",
            category="DOKUMA_TEZGAHI_BAKIM",
            channel="dense",
        ),
        CandidateResult(
            doc_id="DOC-001",
            score=0.82,
            rank=2,
            title="Rapierli Dokuma Tezgâhı Yağlama Döngüleri",
            content="Rapierli tezgahlarda tahrik dişlileri ve rapier kafası 250 saatte bir ISO VG 220 ile yağlanmalıdır.",
            category="DOKUMA_TEZGAHI_BAKIM",
            channel="dense",
        ),
        CandidateResult(
            doc_id="DOC-004",
            score=0.75,
            rank=3,
            title="Halı Kenar Overlok Dikiş Gerginliği",
            content="Overlok dikişinde iplik gerginlik sensörleri periyodik ayarlanmalıdır.",
            category="KALITE_GUVENCE_VE_HATA_TRIAJ",
            channel="dense",
        ),
    ]
    return bm25_list, dense_list


@pytest.fixture
def mini_corpus_file(tmp_path: Path) -> Path:
    """Creates a temporary miniature JSON corpus for isolated pipeline testing."""
    docs = [
        {
            "id": "DOC-001",
            "title": "Rapierli Dokuma Tezgâhı Yağlama Döngüleri",
            "category": "DOKUMA_TEZGAHI_BAKIM",
            "content": "Rapierli tezgahlarda tahrik dişlileri ve rapier kafası 250 saatte bir ISO VG 220 sentetik yağ ile yağlanmalıdır. Yetersiz yağlama atkı kaçırmasına yol açar.",
            "keywords": ["yağlama", "rapier", "bakım"],
        },
        {
            "id": "DOC-002",
            "title": "Jakarlı Halı Dokuma Tarak Ayarı ve Atkı Hatası",
            "category": "DOKUMA_TEZGAHI_BAKIM",
            "content": "Tarak diş aralığı mikrometrik olarak kalibre edilmezse jakar dokumada atkı sıklığı bozulur ve çift atkı hatası oluşur.",
            "keywords": ["jakar", "tarak", "atkı hatası"],
        },
        {
            "id": "DOC-003",
            "title": "BCF Polipropilen İplik Büküm ve Mukavemet",
            "category": "IPLIK_LABORATUVAR_STANDARTLARI",
            "content": "BCF polipropilen iplik büküm düzgünsüzlüğü hav dökülmesine ve kopmaya yol açar. Tenasite değeri 3.2 cN/dtex üzerinde tutulmalıdır.",
            "keywords": ["bcf", "iplik", "büküm", "mukavemet"],
        },
        {
            "id": "DOC-004",
            "title": "Halı Hav Yüksekliği ve Doku Hataları Triyajı",
            "category": "KALITE_GUVENCE_VE_HATA_TRIAJ",
            "content": "Optik profilometre ile halı hav yüksekliği ve yüzey abrajı taranarak kalite sınıflandırması yapılır. 1. kalite halılarda hav sapması 0.5 mm altında kalmalıdır.",
            "keywords": ["hav yüksekliği", "abraj", "triyaj", "kalite"],
        },
    ]
    corpus_path = tmp_path / "test_corpus.json"
    corpus_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    return corpus_path


def test_rrf_scoring_math(sample_candidates):
    """Test 1: Reciprocal Rank Fusion calculation formula and ordering."""
    bm25_list, dense_list = sample_candidates
    k = 60

    fused = reciprocal_rank_fusion(bm25_list, dense_list, k=k, top_k=5)

    assert len(fused) == 4
    # DOC-001 is rank 1 in BM25, rank 2 in Dense -> 1/(60+1) + 1/(60+2) = 1/61 + 1/62 = 0.016393 + 0.016129 = 0.032522
    # DOC-002 is rank 2 in BM25, rank 1 in Dense -> 1/(60+2) + 1/(60+1) = 0.032522
    # Both DOC-001 and DOC-002 appear in top 2
    top2_ids = {fused[0].doc_id, fused[1].doc_id}
    assert top2_ids == {"DOC-001", "DOC-002"}

    # DOC-003 (BM25 only, rank 3) vs DOC-004 (Dense only, rank 3) -> each 1/(60+3) = 1/63 = 0.015873
    assert fused[2].fusion_score == pytest.approx(1.0 / 63, rel=1e-3)
    assert fused[3].fusion_score == pytest.approx(1.0 / 63, rel=1e-3)

    # Verification of field assignments
    for item in fused:
        assert item.fusion_mode == "rrf"
        assert item.fusion_rank >= 1


def test_weighted_fusion_score(sample_candidates):
    """Test 2: Min-Max normalization and weighted linear score fusion."""
    bm25_list, dense_list = sample_candidates

    # Check normalization directly
    norm_bm25 = min_max_normalize_scores(bm25_list)
    assert norm_bm25["DOC-001"] == pytest.approx(1.0)
    assert norm_bm25["DOC-003"] == pytest.approx(0.0)

    # Fusion with alpha = 0.5
    fused_weighted = weighted_linear_score_fusion(bm25_list, dense_list, alpha=0.5, top_k=5)
    assert len(fused_weighted) == 4

    for item in fused_weighted:
        assert item.fusion_mode == "weighted"
        assert 0.0 <= item.fusion_score <= 1.0

    # Test alpha = 1.0 (pure BM25)
    pure_bm25 = weighted_linear_score_fusion(bm25_list, dense_list, alpha=1.0, top_k=5)
    assert pure_bm25[0].doc_id == "DOC-001"

    # Test alpha = 0.0 (pure Dense)
    pure_dense = weighted_linear_score_fusion(bm25_list, dense_list, alpha=0.0, top_k=5)
    assert pure_dense[0].doc_id == "DOC-002"


def test_hybrid_engine_sparse_dense(mini_corpus_file):
    """Test 3: MerinosHybridSearchEngine indexing and separate BM25/Dense retrieval."""
    engine = MerinosHybridSearchEngine(collection_name="test_merinos_hybrid")
    docs = engine.index_corpus(mini_corpus_file)
    assert len(docs) == 4

    bm25_res, dense_res = engine.search(
        query="rapierli tezgah dişli yağlama döngüsü",
        top_k=3,
        category_filter=None,
    )

    assert len(bm25_res) > 0
    assert len(dense_res) > 0

    # Both channels should find DOC-001 as top result
    assert bm25_res[0].doc_id == "DOC-001"
    assert dense_res[0].doc_id == "DOC-001"


def test_hybrid_engine_category_filtering(mini_corpus_file):
    """Test 4: Metadata filtering by category in hybrid search."""
    engine = MerinosHybridSearchEngine(collection_name="test_filter_engine")
    engine.index_corpus(mini_corpus_file)

    bm25_res, dense_res = engine.search(
        query="iplik ve kalite kontrol",
        top_k=5,
        category_filter="IPLIK_LABORATUVAR_STANDARTLARI",
    )

    for item in bm25_res:
        assert item.category == "IPLIK_LABORATUVAR_STANDARTLARI"
    for item in dense_res:
        assert item.category == "IPLIK_LABORATUVAR_STANDARTLARI"


def test_three_stage_pipeline_rrf_search(mini_corpus_file):
    """Test 5: ThreeStageHybridPipeline executing RRF search without re-ranking."""
    pipeline = ThreeStageHybridPipeline(
        collection_name="test_rrf_pipeline",
        use_cross_encoder=False,
        rrf_k=60,
    )
    pipeline.index_corpus(mini_corpus_file)

    results = pipeline.search(
        query="tarak ayarı ve jakar atkı hatası",
        mode="rrf",
        top_k=3,
        rerank=False,
    )

    assert len(results) > 0
    assert results[0].doc_id == "DOC-002"
    assert results[0].fusion_mode == "rrf"
    assert results[0].fusion_rank == 1


def test_three_stage_pipeline_cross_encoder_rerank(mini_corpus_file):
    """Test 6: ThreeStageHybridPipeline executing Cross-Encoder re-ranking."""
    pipeline = ThreeStageHybridPipeline(
        collection_name="test_rerank_pipeline",
        use_cross_encoder=True,
        cross_encoder_top_n=4,
    )
    pipeline.index_corpus(mini_corpus_file)

    results = pipeline.search(
        query="BCF polipropilen tenasite mukavemet kopma",
        mode="rrf",
        top_k=3,
        rerank=True,
    )

    assert len(results) > 0
    top_hit = results[0]
    # Check that re-ranking output attributes exist
    assert hasattr(top_hit, "cross_encoder_score")
    assert hasattr(top_hit, "pre_rerank_rank")
    assert top_hit.doc_id == "DOC-003"
    assert top_hit.final_score is not None


def test_alpha_tuning_grid(mini_corpus_file):
    """Test 7: Evaluator grid search across alpha values [0.0 - 1.0]."""
    evaluator = HybridRetrievalEvaluator(corpus_path=mini_corpus_file)
    evaluator.initialize()

    # Run tuning on mini corpus with a subset of queries
    grid = evaluator.tune_alpha_grid(top_k=3, alpha_steps=[0.0, 0.5, 1.0])
    assert len(grid) == 3

    for item in grid:
        assert "alpha" in item
        assert "ndcg_at_5" in item
        assert "mrr_at_5" in item
        assert "hit_rate_at_5" in item
        assert 0.0 <= item["ndcg_at_5"] <= 1.0
        assert 0.0 <= item["mrr_at_5"] <= 1.0


def test_benchmark_evaluator_metrics():
    """Test 8: Evaluator running benchmark on real fixture corpus for 5 models."""
    fixtures_path = Path(__file__).resolve().parent.parent / "fixtures" / "merinos_technical_corpus.json"
    evaluator = HybridRetrievalEvaluator(corpus_path=fixtures_path)
    evaluator.initialize()

    report = evaluator.evaluate_all(top_k=5, rrf_k=60, alpha=0.5)

    expected_models = [
        "BM25_Sparse_Baseline",
        "Qdrant_Dense_Baseline",
        "Hybrid_RRF_Fusion",
        "Hybrid_Weighted_Fusion",
        "Hybrid_RRF_CrossEncoder",
    ]
    for m in expected_models:
        assert m in report.models
        met = report.models[m]
        assert 0.0 <= met.mrr_at_5 <= 1.0
        assert 0.0 <= met.ndcg_at_5 <= 1.0
        assert 0.0 <= met.hit_rate_at_1 <= 1.0
        assert 0.0 <= met.hit_rate_at_5 <= 1.0

    # Hybrid models or Cross-Encoder should achieve strong HitRate@5 (>= 0.80)
    assert report.models["Hybrid_RRF_Fusion"].hit_rate_at_5 >= 0.80


def test_visualizer_panel_generation(tmp_path: Path):
    """Test 9: Visualizer generating the 2x2 master diagnostic panel."""
    fixtures_path = Path(__file__).resolve().parent.parent / "fixtures" / "merinos_technical_corpus.json"
    evaluator = HybridRetrievalEvaluator(corpus_path=fixtures_path)
    evaluator.initialize()
    report = evaluator.evaluate_all(top_k=5, rrf_k=60, alpha=0.5)

    benchmark_json = tmp_path / "benchmark.json"
    report_dict = evaluator.save_benchmark_report(report, benchmark_json)

    out_png = tmp_path / "test_panel.png"
    result_path = plot_hybrid_retrieval_panel(report_dict, out_png)

    assert result_path.exists()
    assert result_path.stat().st_size > 5000  # valid image file


def test_cli_smoke_execution():
    """Test 10: CLI argument parser smoke testing for all subcommands."""
    parser = build_parser()

    # search-hybrid test
    args1 = parser.parse_args(["search-hybrid", "-q", "rapier", "-m", "rrf", "-k", "3"])
    assert args1.command == "search-hybrid"
    assert args1.query == "rapier"
    assert args1.mode == "rrf"
    assert args1.top_k == 3

    # benchmark test
    args2 = parser.parse_args(["benchmark", "-k", "5", "--rrf-k", "60"])
    assert args2.command == "benchmark"
    assert args2.top_k == 5
    assert args2.rrf_k == 60

    # tune-alpha test
    args3 = parser.parse_args(["tune-alpha", "-k", "5"])
    assert args3.command == "tune-alpha"

    # plot test
    args4 = parser.parse_args(["plot"])
    assert args4.command == "plot"
