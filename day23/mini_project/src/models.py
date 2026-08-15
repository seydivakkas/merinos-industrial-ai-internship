"""
Merinos Industrial AI Internship - Day 23
Dense Retrieval & Re-ranking Data Models (Pydantic v2)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RawDocument(BaseModel):
    """Külliyattaki ham Merinos teknik bakım ve arıza dokümanı şeması."""
    doc_id: str = Field(description="Tekil doküman tanımlayıcısı (örn: DOC-001)")
    title: str = Field(description="Doküman başlığı")
    content: str = Field(description="Teknik servis metni veya onarım adımları")
    category: str = Field(description="Kategori: WEAVING, JACQUARD, YARN, DYEING_FINISHING")
    tags: List[str] = Field(default_factory=list, description="İlişkili etiketler ve arıza kodları")


class EmbeddedDocument(BaseModel):
    """Vektörleştirilmiş doküman şeması."""
    doc_id: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DenseSearchResultItem(BaseModel):
    """Bi-Encoder veya Qdrant arama sonuç kalemi."""
    doc_id: str
    title: str
    score: float
    rank: int
    snippet: str
    category: str
    tags: List[str] = Field(default_factory=list)


class ReRankedResultItem(BaseModel):
    """Cross-Encoder re-ranking sonrası sonuç kalemi."""
    doc_id: str
    title: str
    bi_encoder_score: float
    cross_encoder_score: float
    rank: int
    snippet: str
    category: str
    tags: List[str] = Field(default_factory=list)


class EvaluationMetrics(BaseModel):
    """Bilgi getirme başarı metrikleri."""
    precision_at_1: float
    precision_at_3: float
    precision_at_5: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float


class DenseRetrievalBenchmarkReport(BaseModel):
    """Bi-Encoder, Re-ranker ve BM25 karşılaştırmalı değerlendirme raporu."""
    bi_encoder_metrics: EvaluationMetrics
    reranked_metrics: EvaluationMetrics
    bm25_metrics: EvaluationMetrics
    bi_encoder_latency_ms: float
    reranked_latency_ms: float
    bm25_latency_ms: float
    bi_encoder_qps: float
    reranked_qps: float
    bm25_qps: float
    total_documents: int
    embedding_dimension: int
    models_info: Dict[str, str]
