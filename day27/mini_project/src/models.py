"""
Merinos Industrial AI Internship - Day 27
Pydantic v2 Data Models for RAG Retrieval & Generation Evaluation (Ragas Framework)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class EvalSample(BaseModel):
    """Tek bir RAG değerlendirme sorgu/cevap veri noktası."""
    question_id: str = Field(description="Benzersiz soru kimliği (örn: Q01)")
    question: str = Field(description="Kullanıcı veya teknisyen sorusu")
    department: str = Field(description="İlgili fabrika departmanı")
    machine: str = Field(description="İlgili makine/hat kodu")
    ground_truth: str = Field(description="Uzman mühendis altın standart referans cevabı")
    contexts: List[str] = Field(default_factory=list, description="Getirilen bağlam parçaları (kademeli sıralı)")
    answer: str = Field(description="RAG modeli tarafından üretilen cevap")
    pipeline_id: str = Field(default="pipeline", description="Değerlendirilen RAG pipeline kimliği")

    @field_validator("contexts")
    @classmethod
    def validate_contexts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("En az bir adet bağlam parçası (context chunk) sağlanmalıdır.")
        return v


class ClaimItem(BaseModel):
    """Metinden çıkarılan atomik iddia ve bağlam doğrulama durumu."""
    claim_text: str = Field(description="Atomik iddia/önerme metni")
    supported: bool = Field(default=False, description="Bağlam tarafından doğrulanıp doğrulanmadığı")
    evidence_context_idx: Optional[int] = Field(default=None, description="Destekleyen bağlam indeksi (0-based)")
    similarity_score: float = Field(default=0.0, description="En yüksek anlamsal benzerlik skoru")


class MetricScore(BaseModel):
    """Tek bir Ragas metriğinin skoru ve hesaplama detayları."""
    metric_name: str = Field(description="Metrik adı (faithfulness, context_precision, context_recall, answer_relevance)")
    score: float = Field(ge=0.0, le=1.0, description="0.0 ile 1.0 arasında normalize edilmiş metrik skoru")
    details: Dict[str, Any] = Field(default_factory=dict, description="Ayrıştırılmış iddialar ve ara hesaplamalar")


class SampleEvaluation(BaseModel):
    """Tek bir örneğin 4 temel Ragas metriği ve bileşik harmonik skoru."""
    question_id: str
    pipeline_id: str
    department: str
    machine: str
    faithfulness: float = Field(ge=0.0, le=1.0)
    context_precision: float = Field(ge=0.0, le=1.0)
    context_recall: float = Field(ge=0.0, le=1.0)
    answer_relevance: float = Field(ge=0.0, le=1.0)
    ragas_composite_score: float = Field(ge=0.0, le=1.0)
    claims: List[ClaimItem] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class PipelineSummary(BaseModel):
    """Bir RAG pipeline'ının korpus genelindeki ortalama performans özeti."""
    pipeline_id: str
    pipeline_name: str
    num_samples: int
    avg_faithfulness: float
    avg_context_precision: float
    avg_context_recall: float
    avg_answer_relevance: float
    avg_ragas_composite: float
    per_department_scores: Dict[str, Dict[str, float]] = Field(default_factory=dict)


class RagasBenchmarkReport(BaseModel):
    """Tüm RAG mimarilerini kapsayan kurumsal kıyaslama raporu."""
    benchmark_name: str
    timestamp: str
    sample_count: int
    pipelines: List[PipelineSummary]
    sample_evaluations: List[SampleEvaluation]
    best_pipeline_id: str
    best_ragas_score: float
    threshold_compliance: Dict[str, bool] = Field(default_factory=dict)
