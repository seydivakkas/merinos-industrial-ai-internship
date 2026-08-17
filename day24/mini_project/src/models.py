"""
Merinos Industrial AI Internship - Day 24
Hybrid Retrieval & Rank Fusion Data Models (Pydantic v2)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, computed_field


class RawDocument(BaseModel):
    """Külliyattaki Merinos teknik arıza ve bakım dokümanı şeması."""
    doc_id: str = Field(description="Tekil doküman tanımlayıcısı (örn: DOC-001)")
    title: str = Field(description="Doküman başlığı")
    content: str = Field(description="Teknik bakım metni veya onarım protokolü")
    category: str = Field(description="Kategori: DOKUMA_TEZGAHI_BAKIM, DESEN_VE_JAKAR_YONETIMI, IPLIK_LABORATUVAR_STANDARTLARI, KALITE_GUVENCE_VE_HATA_TRIAJ")
    tags: List[str] = Field(default_factory=list, description="İlişkili etiketler ve arıza kodları")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Ek makine ve revizyon bilgisi")


class CandidateResult(BaseModel):
    """Tekil arama motorundan (BM25 veya Dense) dönen aday sonuç."""
    doc_id: str
    score: float
    rank: int
    title: str = ""
    content: str = ""
    category: str = ""
    channel: str = ""


class FusedSearchResultItem(BaseModel):
    """RRF veya Weighted Fusion sonucu birleştirilmiş arama kalemi."""
    doc_id: str
    title: str
    fused_score: float
    final_rank: int
    sparse_rank: Optional[int] = None
    dense_rank: Optional[int] = None
    sparse_score: Optional[float] = None
    dense_score: Optional[float] = None
    snippet: str = ""
    category: str = ""
    tags: List[str] = Field(default_factory=list)
    fusion_mode: str = "rrf"

    @property
    def fusion_rank(self) -> int:
        return self.final_rank

    @property
    def fusion_score(self) -> float:
        return self.fused_score

    @property
    def bm25_rank(self) -> Optional[int]:
        return self.sparse_rank


class ReRankedHybridResultItem(BaseModel):
    """Füzyon sonrası Cross-Encoder ile yeniden sıralanmış nihai sonuç kalemi."""
    doc_id: str
    title: str
    fused_score: float
    cross_encoder_score: float
    rank: int
    snippet: str = ""
    category: str = ""
    tags: List[str] = Field(default_factory=list)
    pre_rerank_rank: int = 1

    @property
    def final_score(self) -> float:
        return self.cross_encoder_score


class EvaluationMetrics(BaseModel):
    """Bilgi getirme başarı metrikleri."""
    precision_at_1: float
    precision_at_3: float
    precision_at_5: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float

    @computed_field
    @property
    def mrr_at_5(self) -> float:
        return self.mrr

    @computed_field
    @property
    def hit_rate_at_1(self) -> float:
        return self.precision_at_1

    @computed_field
    @property
    def hit_rate_at_3(self) -> float:
        return min(1.0, self.precision_at_3 * 3.0)

    @computed_field
    @property
    def hit_rate_at_5(self) -> float:
        return self.recall_at_5


class HybridRetrievalBenchmarkReport(BaseModel):
    """5 farklı getirme modelinin karşılaştırmalı performans raporu."""
    bm25_metrics: EvaluationMetrics
    dense_metrics: EvaluationMetrics
    rrf_hybrid_metrics: EvaluationMetrics
    weighted_hybrid_metrics: EvaluationMetrics
    reranked_hybrid_metrics: EvaluationMetrics
    bm25_latency_ms: float
    dense_latency_ms: float
    rrf_latency_ms: float
    weighted_latency_ms: float
    reranked_latency_ms: float
    bm25_qps: float
    dense_qps: float
    rrf_qps: float
    weighted_qps: float
    reranked_qps: float
    total_documents: int
    rrf_k: int
    best_alpha: float
    models_info: Dict[str, str]

    @computed_field
    @property
    def models(self) -> Dict[str, EvaluationMetrics]:
        return {
            "BM25_Sparse_Baseline": self.bm25_metrics,
            "Qdrant_Dense_Baseline": self.dense_metrics,
            "Hybrid_RRF_Fusion": self.rrf_hybrid_metrics,
            "Hybrid_Weighted_Fusion": self.weighted_hybrid_metrics,
            "Hybrid_RRF_CrossEncoder": self.reranked_hybrid_metrics,
        }
