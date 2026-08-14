"""Unit and integration test suite for Day 22 Sparse Retrieval Engine (TF-IDF & BM25)."""

import json
from pathlib import Path
import pytest

from day22.mini_project.src.models import (
    RawDocument,
    CorpusStats,
    RetrievalMetrics,
    SparseRetrievalComparisonReport
)
from day22.mini_project.src.tokenizer import MerinosTextTokenizer
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.tfidf_engine import TFIDFRetrievalEngine
from day22.mini_project.src.bm25_engine import OkapiBM25Engine
from day22.mini_project.src.evaluator import RetrievalEvaluator, EVALUATION_QUERIES
from day22.mini_project.src.visualizer import SparseRetrievalVisualizer


@pytest.fixture(scope="module")
def sample_corpus():
    """Provides a small focused technical corpus for rapid deterministic unit tests."""
    return [
        RawDocument(
            doc_id="TEST-001",
            title="Van de Wiele Çözgü Gerilim Ayarı",
            category="DOKUMA",
            content="Van de Wiele tezgâhlarında çözgü gerilim dalgalanması 15 ile 25 cN arasında tutulmalıdır. Levent fren balataları aşındığında iplik kopması arızası meydana gelir."
        ),
        RawDocument(
            doc_id="TEST-002",
            title="Ana Tahrik Motoru Rulman Gres Yağlama",
            category="BAKIM",
            content="Ana tahrik motoru rulmanları Klüber Isoflex sentetik gres yağı ile yağlanmalıdır. Fazla gres basılması eriyen yağın kumaşa damlamasına ve yağ lekesi kusuruna sebep olur."
        ),
        RawDocument(
            doc_id="TEST-003",
            title="BCF Polipropilen İplik Mukavemet Testi",
            category="LABORATUVAR",
            content="2200 dtex BCF polipropilen halı ipliklerinin kopma mukavemeti Uster Tensorapid cihazında test edilir. Minimum kopma mukavemeti 24 cN/tex olmalıdır."
        ),
        RawDocument(
            doc_id="TEST-004",
            title="Elektronik Jakar Solenoid Valf Platin Senkronizasyonu",
            category="JAKAR",
            content="Jakar başlığındaki solenoid valflerin tepki süresi 4.5 ms altında kalmalıdır. Yapışan valfler platin kancalarının takılı kalmasına ve jakar desen kayması hatasına yol açar."
        )
    ]


@pytest.fixture(scope="module")
def sample_tokenizer():
    stopwords = {"ve", "ile", "için", "bir", "bu", "da", "de"}
    return MerinosTextTokenizer(stopwords=stopwords, min_token_len=2)


@pytest.fixture(scope="module")
def built_index(sample_corpus, sample_tokenizer):
    index = InvertedIndex(sample_tokenizer)
    index.build(sample_corpus)
    return index


def test_tokenizer_turkish_casing_and_punctuation(sample_tokenizer):
    """1. Tests Turkish letter normalization, punctuation removal, and stopwords filtering."""
    raw_text = "İPLİK Kopması ve IRO Stella! (2200 dtex, 15 cN/tex) için levent freni."
    tokens = sample_tokenizer.tokenize(raw_text)

    assert "iplik" in tokens # İ -> i
    assert "kopması" in tokens
    assert "ıro" in tokens # I -> ı
    assert "stella" in tokens
    assert "2200" in tokens
    assert "dtex" in tokens
    assert "levent" in tokens
    assert "freni" in tokens

    # Stopwords should be removed
    assert "ve" not in tokens
    assert "için" not in tokens


def test_tokenizer_term_frequencies_and_bigrams():
    """2. Tests term frequency counting and optional bigram generation."""
    tokenizer = MerinosTextTokenizer(min_token_len=2, use_bigrams=True)
    tokens = tokenizer.tokenize("jakar desen kayması jakar")

    freqs = tokenizer.get_term_frequencies(tokens)
    assert freqs["jakar"] == 2
    assert freqs["desen"] == 1
    assert freqs["kayması"] == 1

    # Check bigrams
    assert "jakar_desen" in tokens
    assert "desen_kayması" in tokens
    assert "kayması_jakar" in tokens


def test_inverted_index_construction(built_index):
    """3. Tests inverted index postings, document lengths, and corpus statistics."""
    assert built_index.doc_count == 4
    assert built_index.avg_doc_len > 10.0
    assert len(built_index.raw_documents) == 4

    # Check postings for 'gerilim'
    postings_gerilim = built_index.get_postings("gerilim")
    assert len(postings_gerilim) >= 1
    doc_ids = [p[0] for p in postings_gerilim]
    assert "TEST-001" in doc_ids

    # Document frequency
    assert built_index.get_df("gerilim") >= 1
    assert built_index.get_df("olmayan_terim_xyz") == 0


def test_inverted_index_serialization(built_index, tmp_path):
    """4. Tests inverted index serialization to JSON and subsequent deserialization."""
    out_file = tmp_path / "test_inverted_index.json"
    built_index.save_index(out_file)
    assert out_file.exists()

    loaded_index = InvertedIndex(built_index.tokenizer)
    loaded_index.load_index(out_file)

    assert loaded_index.doc_count == built_index.doc_count
    assert loaded_index.avg_doc_len == built_index.avg_doc_len
    assert set(loaded_index.raw_documents.keys()) == set(built_index.raw_documents.keys())
    assert loaded_index.get_postings("yağ") == built_index.get_postings("yağ")


def test_tfidf_engine_cosine_scoring(built_index, sample_tokenizer):
    """5. Tests TF-IDF cosine similarity scoring, ranking, and snippet generation."""
    engine = TFIDFRetrievalEngine(built_index, sample_tokenizer)
    results = engine.search("rulman klüber gres yağı damlaması", top_k=3)

    assert len(results) > 0
    top_result = results[0]
    assert top_result.doc_id == "TEST-002" # Gres yağlama dokümanı
    assert 0.0 < top_result.score <= 1.0 # Cosine similarity bounded by 1.0
    assert len(top_result.snippet) > 10
    assert top_result.rank == 1


def test_bm25_engine_probabilistic_scoring(built_index, sample_tokenizer):
    """6. Tests Okapi BM25 ranking, non-negative scores, and top-1 relevance."""
    engine = OkapiBM25Engine(built_index, sample_tokenizer, k1=1.5, b=0.75)
    results = engine.search("jakar platin solenoid valf desen kayması", top_k=3)

    assert len(results) > 0
    top_result = results[0]
    assert top_result.doc_id == "TEST-004" # Jakar dokümanı
    assert top_result.score > 0.0
    assert top_result.rank == 1
    assert "solenoid" in top_result.snippet.lower() or "jakar" in top_result.snippet.lower()


def test_bm25_length_normalization_penalty(sample_tokenizer):
    """7. Tests that BM25 penalizes bloated long documents in favor of concise dense documents (b parameter)."""
    # Create two documents: one short, one padded with repetitive words
    docs = [
        RawDocument(
            doc_id="SHORT",
            title="İplik Mukavemeti",
            category="TEST",
            content="İplik kopma mukavemeti Uster cihazında test edilir."
        ),
        RawDocument(
            doc_id="LONG_BLOATED",
            title="İplik Mukavemeti Genel Rapor",
            category="TEST",
            content="İplik kopma mukavemeti Uster cihazında test edilir. " + " ".join(["genel dokuma raporu standardı"] * 30)
        )
    ]
    index = InvertedIndex(sample_tokenizer).build(docs)
    engine = OkapiBM25Engine(index, sample_tokenizer, k1=1.5, b=0.75)

    results = engine.search("iplik kopma mukavemeti", top_k=2)
    assert len(results) == 2
    # Short dense document should score higher than bloated document
    assert results[0].doc_id == "SHORT"
    assert results[0].score > results[1].score


def test_retrieval_evaluator_metrics(built_index, sample_tokenizer):
    """8. Tests evaluation metrics calculation: P@K, Recall@K, MRR, and NDCG@K."""
    bm25 = OkapiBM25Engine(built_index, sample_tokenizer)
    test_queries = [
        {"query": "çözgü gerilim levent fren", "relevant_docs": {"TEST-001"}},
        {"query": "motor rulman gres yağı lekesi", "relevant_docs": {"TEST-002"}},
        {"query": "BCF polipropilen Uster mukavemet", "relevant_docs": {"TEST-003"}},
        {"query": "jakar solenoid valf platin", "relevant_docs": {"TEST-004"}}
    ]
    evaluator = RetrievalEvaluator(queries=test_queries)
    metrics = evaluator.evaluate_engine(bm25, top_k=3)

    assert isinstance(metrics, RetrievalMetrics)
    assert metrics.precision_at_1 == 1.0
    assert metrics.recall_at_5 == 1.0
    assert metrics.mrr == 1.0
    assert metrics.ndcg_at_5 == 1.0
    assert metrics.avg_latency_ms >= 0.0
    assert metrics.queries_per_second > 0.0


def test_visualizer_panel_generation(sample_corpus, sample_tokenizer, tmp_path):
    """9. Tests 2x2 diagnostic figure rendering and file generation."""
    index = InvertedIndex(sample_tokenizer).build(sample_corpus)
    bm25 = OkapiBM25Engine(index, sample_tokenizer)
    tfidf = TFIDFRetrievalEngine(index, sample_tokenizer)

    evaluator = RetrievalEvaluator()
    report = evaluator.compare_engines(bm25, tfidf, index.get_stats())

    out_file = tmp_path / "test_sparse_retrieval_panel.png"
    vis = SparseRetrievalVisualizer()
    saved_path = vis.plot_diagnostic_panel(report, str(out_file))

    assert Path(saved_path).exists()
    assert Path(saved_path).stat().st_size > 25_000


def test_models_serialization(sample_corpus, sample_tokenizer):
    """10. Tests Pydantic v2 JSON serialization of Sparse Retrieval Report."""
    index = InvertedIndex(sample_tokenizer).build(sample_corpus)
    bm25 = OkapiBM25Engine(index, sample_tokenizer)
    tfidf = TFIDFRetrievalEngine(index, sample_tokenizer)

    evaluator = RetrievalEvaluator()
    report = evaluator.compare_engines(bm25, tfidf, index.get_stats())

    json_str = report.model_dump_json(indent=2)
    parsed = json.loads(json_str)

    assert "corpus_stats" in parsed
    assert "bm25_metrics" in parsed
    assert "tfidf_metrics" in parsed
    assert "champion_algorithm" in parsed
    assert parsed["corpus_stats"]["total_documents"] == 4
