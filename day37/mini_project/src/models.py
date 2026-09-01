# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 37
Veri Modelleri: Ragas Metrikleri, Guardrail Güvenlik Kararları ve Benchmark Raporları
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class RagasMetrics(BaseModel):
    """Bütüncül RAG Triad metrikleri ve genel harmonik skor."""
    context_precision: float = Field(..., ge=0.0, le=1.0, description="Getirilen parçaların alaka ve sıralama kalitesi")
    context_recall: float = Field(..., ge=0.0, le=1.0, description="Altın referans bilginin getirilme kapsayıcılığı")
    faithfulness: float = Field(..., ge=0.0, le=1.0, description="Üretilen yanıtın bağlama sadakati (1 - Halüsinasyon)")
    answer_relevance: float = Field(..., ge=0.0, le=1.0, description="Üretilen yanıtın soruyla semantik örtüşmesi")
    rag_triad_score: float = Field(..., ge=0.0, le=1.0, description="Harmonik RAG kalite skoru")


class GuardrailDecision(BaseModel):
    """Girdi veya çıktı güvenlik korkuluğunun (Guardrail) verdiği karar."""
    action: str = Field(..., description="ALLOW, BLOCK veya MODIFY")
    reason: str = Field(..., description="Kararın gerekçesi ve kural açıklaması")
    violation_category: Optional[str] = Field(None, description="ISG_VIOLATION, PARAMETER_OUT_OF_BOUNDS, HALLUCINATION vb.")
    sanitized_content: Optional[str] = Field(None, description="Gerekiyorsa sansürlenmiş veya standart ret metni")


class EvaluationScenarioResult(BaseModel):
    """Tek bir değerlendirme senaryosunun test sonucu."""
    scenario_id: str
    query: str
    category: str
    input_guardrail: GuardrailDecision
    output_guardrail: GuardrailDecision
    metrics: RagasMetrics
    final_answer: str
    is_blocked: bool
    latency_ms: float


class RagasBenchmarkReport(BaseModel):
    """15 altın senaryo üzerinden derlenen kalite, güvenlik ve halüsinasyon karnesi."""
    timestamp: str
    total_scenarios: int
    mean_context_precision: float
    mean_context_recall: float
    mean_faithfulness: float
    mean_answer_relevance: float
    mean_rag_triad_score: float
    guardrail_interception_rate: float
    avg_latency_ms: float
    items: List[EvaluationScenarioResult]
