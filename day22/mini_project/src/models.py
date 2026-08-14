"""Pydantic v2 data models for Day 22 Sparse Retrieval Engine."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RawDocument(BaseModel):
    """Raw industrial technical document from Merinos corpus."""
    doc_id: str = Field(..., description="Tekil doküman kimliği (örn. DOC-001)")
    title: str = Field(..., description="Doküman başlığı")
    category: str = Field(..., description="Teknik kategori")
    content: str = Field(..., description="Dokümanın tam metin içeriği")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Ek meta veriler")


class TokenizedDocument(BaseModel):
    """Tokenized and frequency-mapped document representation."""
    doc_id: str
    tokens: List[str]
    doc_len: int
    term_frequencies: Dict[str, int]


class SearchResultItem(BaseModel):
    """Single search result item returned by retrieval engines."""
    doc_id: str
    title: str
    category: str
    score: float
    rank: int
    snippet: str


class RetrievalMetrics(BaseModel):
    """Standard Information Retrieval (IR) evaluation metrics."""
    precision_at_1: float
    precision_at_3: float
    precision_at_5: float
    recall_at_5: float
    mrr: float = Field(..., description="Mean Reciprocal Rank")
    ndcg_at_5: float = Field(..., description="Normalized Discounted Cumulative Gain @ 5")
    avg_latency_ms: float
    queries_per_second: float


class CorpusStats(BaseModel):
    """Corpus level descriptive statistics."""
    total_documents: int
    total_tokens: int
    vocabulary_size: int
    avg_doc_len: float
    min_doc_len: int
    max_doc_len: int

    @property
    def unique_terms(self) -> int:
        return self.vocabulary_size

    @property
    def avg_doc_length(self) -> float:
        return self.avg_doc_len


class SparseRetrievalComparisonReport(BaseModel):
    """Comprehensive benchmark comparison report between TF-IDF and Okapi BM25."""
    corpus_stats: CorpusStats
    bm25_metrics: RetrievalMetrics
    tfidf_metrics: RetrievalMetrics
    champion_algorithm: str
    summary: str

    @property
    def bm25_latency_ms(self) -> float:
        return self.bm25_metrics.avg_latency_ms

    @property
    def bm25_qps(self) -> float:
        return self.bm25_metrics.queries_per_second

    @property
    def tfidf_latency_ms(self) -> float:
        return self.tfidf_metrics.avg_latency_ms

    @property
    def tfidf_qps(self) -> float:
        return self.tfidf_metrics.queries_per_second
