"""
Merinos Industrial AI Internship - Day 25
Unit & Integration Tests for Document Chunking Strategies

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import pytest
import json
from pathlib import Path
import numpy as np

from day25.mini_project.src.models import (
    DocumentItem,
    ChunkItem,
    ChunkingStats,
    RetrievalMetrics,
    StrategyEvaluationResult,
    ChunkingBenchmarkReport
)
from day25.mini_project.src.fixed_chunker import FixedSizeChunker
from day25.mini_project.src.recursive_chunker import RecursiveCharacterChunker
from day25.mini_project.src.semantic_chunker import SemanticChunker
from day25.mini_project.src.markdown_chunker import MarkdownAwareChunker
from day25.mini_project.src.chunk_engine import MerinosChunkEngine
from day25.mini_project.src.evaluator import ChunkingBenchmarkEvaluator
from day25.mini_project.src.visualizer import plot_chunking_diagnostic_panel


@pytest.fixture
def sample_document() -> DocumentItem:
    """Testler için örnek çok bölümlü teknik doküman."""
    content = (
        "# SOP-099: Örnek Dokuma Bakım Kılavuzu\n\n"
        "## 1. Genel Bilgilendirme ve Güvenlik\n"
        "Bu prosedür Merinos Gaziantep tesislerindeki halı dokuma tezgâhları için hazırlanmıştır.\n"
        "Bakım öncesi ana şalter indirilerek kilitlenmeli ve etiketlenmelidir (LOTO).\n\n"
        "## 2. Mekanik Ayarlar ve Yağlama\n"
        "Tezgâh ana tahrik mili her 250 çalışma saatinde bir kontrol edilmelidir.\n"
        "Önemli Kritik Parametre: Yağlama basıncı kesinlikle 4.5 bar seviyesinde tutulmalıdır.\n\n"
        "### 2.1 Periyodik Yağlama Tablosu\n"
        "| Komponent | Yağ Tipi | Periyot |\n"
        "| Dişli Kutusu | ISO VG 220 | Aylık |\n"
        "| Rulman Grubu | NLGI 2 Gres | Haftalık |\n\n"
        "Bu tablodaki periyotlara uyulmaması durumunda garanti kapsamı devre dışı kalır."
    )
    return DocumentItem(
        doc_id="SOP-099",
        title="SOP-099: Örnek Dokuma Bakım Kılavuzu",
        category="Dokuma Bakım",
        content=content,
        metadata={"machine": "Test Tezgâhı", "rev": 1}
    )


@pytest.fixture
def sample_query() -> dict:
    return {
        "id": "Q-TEST-01",
        "query": "Yağlama basıncı kesinlikle kaç bar seviyesinde tutulmalıdır?",
        "target_doc_id": "SOP-099",
        "target_fact": "yağlama basıncı kesinlikle 4.5 bar seviyesinde tutulmalıdır"
    }


def test_fixed_size_chunker(sample_document):
    """Fixed-Size chunker'ın boyut ve örtüşme adımlarını test eder."""
    chunker = FixedSizeChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) > 1
    for c in chunks:
        assert isinstance(c, ChunkItem)
        assert c.strategy == "fixed_size"
        assert c.doc_id == sample_document.doc_id
        assert c.char_length <= 150
        assert c.char_length > 0


def test_fixed_size_invalid_params():
    """Geçersiz chunk_size veya overlap parametrelerinin hata fırlatmasını test eder."""
    with pytest.raises(ValueError):
        FixedSizeChunker(chunk_size=0, chunk_overlap=0)

    with pytest.raises(ValueError):
        FixedSizeChunker(chunk_size=100, chunk_overlap=120)


def test_recursive_character_chunker(sample_document):
    """Recursive chunker'ın hiyerarşik ayırıcılar ile paragrafları bölmesini test eder."""
    chunker = RecursiveCharacterChunker(chunk_size=200, chunk_overlap=40)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) >= 2
    for c in chunks:
        assert c.strategy == "recursive"
        assert c.char_length > 0
        assert c.token_count > 0


def test_semantic_chunker_breakpoints(sample_document):
    """Semantic chunker'ın cümle kırılma noktalarını tespit edip bölmesini test eder."""
    chunker = SemanticChunker(
        similarity_threshold_percentile=50.0,
        min_chunk_size=50,
        max_chunk_size=300
    )
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) >= 1
    for c in chunks:
        assert c.strategy == "semantic"
        assert c.char_length <= 350


def test_markdown_aware_chunker_breadcrumbs(sample_document):
    """Markdown chunker'ın H1, H2, H3 başlıklarını breadcrumb olarak eklemesini test eder."""
    chunker = MarkdownAwareChunker(max_chunk_size=250)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) >= 3
    # Başlık hiyerarşisinin yakalandığını doğrula
    has_breadcrumb = any(len(c.section_headers) >= 2 for c in chunks)
    assert has_breadcrumb, "Markdown chunker başlık hiyerarşisini (breadcrumbs) yakalayamadı"

    for c in chunks:
        assert c.strategy == "markdown_aware"
        assert "breadcrumbs" in c.metadata
        assert len(c.content) > 0


def test_merinos_chunk_engine_orchestration(sample_document):
    """Birleşik motorun 4 stratejiyi de başarıyla çalıştırmasını test eder."""
    engine = MerinosChunkEngine()

    all_results = engine.chunk_all_strategies([sample_document])
    assert set(all_results.keys()) == {"fixed_size", "recursive", "semantic", "markdown_aware"}

    for strat, chunks in all_results.items():
        assert len(chunks) >= 1
        assert chunks[0].strategy == strat

    with pytest.raises(ValueError):
        engine.chunk_document(sample_document, "invalid_strategy")


def test_chunk_stats_and_coherence(sample_document):
    """İstatistik ve parça içi tutarlılık (coherence) hesaplamalarını test eder."""
    engine = MerinosChunkEngine()
    chunks = engine.chunk_document(sample_document, "markdown_aware")

    evaluator = ChunkingBenchmarkEvaluator()
    stats = evaluator.calculate_chunk_stats("markdown_aware", chunks, len(sample_document.content))

    assert stats.strategy == "markdown_aware"
    assert stats.total_chunks == len(chunks)
    assert stats.mean_char_length > 0
    assert 0.0 <= stats.intra_chunk_coherence <= 1.0
    assert stats.redundancy_ratio >= 0.5


def test_retrieval_metrics_evaluation(sample_document, sample_query):
    """Vektör getirme değerlendirmesi ve metrik üretimini test eder."""
    engine = MerinosChunkEngine()
    chunks = engine.chunk_document(sample_document, "markdown_aware")

    evaluator = ChunkingBenchmarkEvaluator()
    metrics, idx_lat, qry_lat = evaluator.evaluate_retrieval(chunks, [sample_query])

    assert isinstance(metrics, RetrievalMetrics)
    assert 0.0 <= metrics.precision_at_1 <= 1.0
    assert 0.0 <= metrics.recall_at_5 <= 1.0
    assert 0.0 <= metrics.mrr <= 1.0
    assert 0.0 <= metrics.ndcg_at_5 <= 1.0
    assert idx_lat >= 0.0
    assert qry_lat >= 0.0


def test_end_to_end_benchmark_report(sample_document, sample_query):
    """4 stratejinin uçtan uca kıyaslanıp rapor nesnesine dönüştürülmesini test eder."""
    evaluator = ChunkingBenchmarkEvaluator()
    report = evaluator.run_benchmark([sample_document], [sample_query])

    assert isinstance(report, ChunkingBenchmarkReport)
    assert len(report.strategies) == 4
    assert report.total_documents == 1
    assert report.total_queries == 1
    assert report.best_retrieval_strategy in evaluator.engine.AVAILABLE_STRATEGIES
    assert report.best_coherence_strategy in evaluator.engine.AVAILABLE_STRATEGIES


def test_diagnostic_panel_plot_and_cli(tmp_path, sample_document, sample_query):
    """2x2 Tanı panelinin görselleştirilip dosyaya kaydedilmesini test eder."""
    evaluator = ChunkingBenchmarkEvaluator()
    report = evaluator.run_benchmark([sample_document], [sample_query])

    out_png = tmp_path / "test_chunking_panel.png"
    result_path = plot_chunking_diagnostic_panel(report, out_png)

    assert result_path.exists()
    assert result_path.stat().st_size > 10000  # En az 10 KB görsel üretilmiş olmalı
