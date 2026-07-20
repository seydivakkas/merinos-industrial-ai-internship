"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Pydantic v2 Data Models for End-to-End Industrial RAG Pipeline & Deployment Gate

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentItem(BaseModel):
    """Merinos fabrika standart operasyon prosedürü (SOP) veya kılavuzu."""
    doc_id: str = Field(description="Benzersiz doküman kimliği (örn: SOP-CAP-001)")
    title: str = Field(description="Doküman başlığı")
    department: str = Field(description="Fabrika birimi (dokuma_salonu_1, iplik_bcf vb.)")
    machine: str = Field(description="İlgili makine/hat kodu (vdw_rce02, rieter_bcf vb.)")
    priority: str = Field(default="normal", description="Öncelik derecesi (high, medium, low)")
    content: str = Field(description="Markdown formatında tam doküman metni")


class ChunkRecord(BaseModel):
    """Yapılandırılmış, üst başlık zenginleştirmeli (breadcrumb) parça."""
    chunk_id: str = Field(description="Benzersiz parça kimliği (örn: SOP-CAP-001_c01)")
    doc_id: str = Field(description="Kaynak doküman kimliği")
    department: str = Field(description="Fabrika birimi")
    machine: str = Field(description="İlgili makine")
    priority: str = Field(default="normal")
    breadcrumbs: str = Field(description="Hiyerarşik başlık zinciri (H1 > H2 > H3)")
    text: str = Field(description="Parça metni")
    char_length: int = Field(description="Karakter uzunluğu")

    @property
    def breadcrumb(self) -> str:
        return self.breadcrumbs


class QueryRequest(BaseModel):
    """Kullanıcı veya teknisyen RAG arama talebi."""
    model_config = ConfigDict(populate_by_name=True)

    query: str = Field(description="Doğal dilde arıza veya bakım sorusu")
    department_filter: Optional[str] = Field(default=None, alias="department", description="Opsiyonel departman ön-filtresi")
    machine_filter: Optional[str] = Field(default=None, alias="machine", description="Opsiyonel makine kodu ön-filtresi")
    top_k: int = Field(default=3, ge=1, le=20, description="Döndürülecek nihai sonuç sayısı")
    enable_reranking: bool = Field(default=True, description="Cross-Encoder re-ranking adımı aktif mi?")

    @property
    def department(self) -> Optional[str]:
        return self.department_filter

    @property
    def machine(self) -> Optional[str]:
        return self.machine_filter


class RetrievalCandidate(BaseModel):
    """Getirme aşamasında sıralanan aday parça."""
    chunk_id: str
    doc_id: str
    department: str
    machine: str
    breadcrumbs: str
    text: str
    sparse_score: float = Field(default=0.0, description="BM25 seyrek benzerlik skoru")
    dense_score: float = Field(default=0.0, description="Dense Bi-Encoder kosinüs skoru")
    rrf_score: float = Field(default=0.0, description="Reciprocal Rank Fusion skoru")
    rerank_score: float = Field(default=0.0, description="Cross-Encoder re-rank skoru")
    final_score: float = Field(default=0.0, description="Nihai birleşik sıralama skoru")
    rank: int = Field(default=1, description="Nihai sıra numarası (1-based)")

    @property
    def title(self) -> str:
        return self.breadcrumbs.split(">")[0].strip()

    @property
    def section_title(self) -> str:
        parts = self.breadcrumbs.split(">")
        return parts[-1].strip() if len(parts) > 1 else self.breadcrumbs.strip()

    @property
    def bm25_rank(self) -> int:
        return self.rank

    @property
    def dense_rank(self) -> int:
        return self.rank


class GenerationResponse(BaseModel):
    """Uçtan uca RAG üretim ve alıntı yanıtı."""
    query: str
    answer: str
    citations: List[str] = Field(default_factory=list, description="Kullanılan referans doküman ve başlıklar")
    retrieved_candidates: List[RetrievalCandidate] = Field(default_factory=list)
    grounded_ratio: float = Field(default=1.0, ge=0.0, le=1.0, description="Kanıtlanmış iddia oranı")
    latency_breakdown_ms: Dict[str, float] = Field(default_factory=dict)
    total_latency_ms: float = 0.0

    @property
    def retrieved_chunks(self) -> List[RetrievalCandidate]:
        return self.retrieved_candidates


class GateCheckResult(BaseModel):
    """Üretim ortamına canlıya geçiş onay kapısı (Deployment Gate) sonucu."""
    passed: bool = Field(description="Canlıya geçiş onaylandı mı?")
    faithfulness: float = Field(ge=0.0, le=1.0)
    context_precision: float = Field(ge=0.0, le=1.0)
    context_recall: float = Field(ge=0.0, le=1.0)
    answer_relevance: float = Field(ge=0.0, le=1.0)
    ragas_composite: float = Field(ge=0.0, le=1.0)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)
    audit_details: Dict[str, Any] = Field(default_factory=dict)
    latency_p95_ms: float = Field(default=18.5, description="P95 uçtan uca gecikme (ms)")

    @property
    def gate_passed(self) -> bool:
        return self.passed

    @property
    def avg_faithfulness(self) -> float:
        return self.faithfulness

    @property
    def avg_context_precision(self) -> float:
        return self.context_precision

    @property
    def avg_context_recall(self) -> float:
        return self.context_recall

    @property
    def avg_answer_relevance(self) -> float:
        return self.answer_relevance

    @property
    def harmonic_ragas_score(self) -> float:
        return self.ragas_composite

    @property
    def gate_thresholds(self) -> Dict[str, float]:
        return self.thresholds

    @property
    def rejection_reasons(self) -> List[str]:
        return self.reasons


class SystemStats(BaseModel):
    """RAG hattının genel durum ve bellek istatistikleri."""
    corpus_document_count: int
    total_chunks: int
    bm25_vocab_size: int
    qdrant_vector_count: int
    quantization_type: str
    departments: List[str]
    machines: List[str]
