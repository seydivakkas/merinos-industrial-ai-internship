# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 36
Veri Modelleri: Yapılandırılmış Çıktı (GeneratedAnswer / StructuredAnswer), Alıntı ve Groundedness Modelleri
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    """Doküman alıntı ve kaynak referans nesnesi."""
    chunk_id: str = Field(..., description="Parça kimliği (Örn: DOC_MERINOS_WEAVING_SOP_c004)")
    source_id: str = Field(default="", description="Kılavuz doküman adı")
    source: Optional[str] = Field(default=None, description="Kaynak dosya adı")
    section: str = Field(default="", description="Bölüm başlığı ve açıklaması")
    quote: Optional[str] = Field(default=None, description="Dokümandan alınan doğrudan alıntı cümlesi")
    verified: bool = Field(default=True, description="Alıntının metinde yer aldığı doğrulandı mı?")

    def model_post_init(self, __context: Any) -> None:
        if not self.source_id and self.source:
            self.source_id = self.source
        elif not self.source and self.source_id:
            self.source = self.source_id


class GeneratedAnswer(BaseModel):
    """
    SCADA paneline, PLC arıza loguna ve mobil operatör tabletine
    aktarılabilir endüstriyel yapılandırılmış yanıt şeması.
    """
    query: str = Field(..., description="Operatörün sorduğu orijinal soru")
    answer: str = Field(default="", description="Net, doğrudan teknik teşhis ve cevap")
    direct_answer: Optional[str] = Field(default=None, description="Doğrudan teşhis ve cevap (uyumluluk alanı)")
    steps: List[str] = Field(default_factory=list, description="Operatörün izleyeceği önerilen adımlar")
    action_steps: Optional[List[str]] = Field(default=None, description="Eylem adımları (uyumluluk alanı)")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Çıkarılan teknik parametreler")
    technical_parameters: Optional[Dict[str, str]] = Field(default=None, description="Teknik parametreler (uyumluluk alanı)")
    citations: List[SourceCitation] = Field(default_factory=list, description="Kullanılan doküman alıntıları")
    safety_alert: Optional[str] = Field(default=None, description="Acil durdurma veya yüksek tehlike güvenlik uyarısı")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Modelin yanıt güvenilirlik puanı")
    fallback_triggered: bool = Field(default=False, description="Güvenli ret devreye girdi mi?")

    def model_post_init(self, __context: Any) -> None:
        if not self.answer and self.direct_answer:
            self.answer = self.direct_answer
        elif not self.direct_answer and self.answer:
            self.direct_answer = self.answer

        if not self.steps and self.action_steps:
            self.steps = self.action_steps
        elif not self.action_steps and self.steps:
            self.action_steps = self.steps

        if not self.parameters and self.technical_parameters:
            self.parameters = self.technical_parameters
        elif not self.technical_parameters and self.parameters:
            self.technical_parameters = self.parameters


# Geriye dönük uyumluluk takma adları (Aliases)
CitationItem = SourceCitation
StructuredAnswer = GeneratedAnswer


class ClaimVerificationResult(BaseModel):
    """Yanıt içindeki tek bir atomik iddianın bağlamla NLI çıkarım sonucu."""
    claim_text: str = Field(..., description="Doğrulanan atomik iddia cümlesi")
    cited_chunk_id: Optional[str] = Field(None, description="İddianın atıfta bulunduğu parça kimliği")
    is_supported: bool = Field(..., description="İddia bağlamdaki kanıtlarla doğrulanabildi mi?")
    similarity_score: float = Field(..., description="Semantik veya leksikal örtüşme puanı (0.0 - 1.0)")
    verdict: str = Field(..., description="FAITHFUL, UNSUPPORTED veya CONTRADICTION")


class GroundednessMetric(BaseModel):
    """Bir yanıtın veya senaryonun özet doğruluk ve alıntı metrikleri."""
    total_claims: int = Field(..., description="Yanıttan çıkarılan toplam atomik iddia sayısı")
    supported_claims: int = Field(..., description="Bağlam tarafından doğrulanan iddia sayısı")
    faithfulness_rate: float = Field(..., description="Desteklenen İddia / Toplam İddia oranı")
    citation_precision: float = Field(..., description="Doğru Alıntılar / Toplam Alıntılar")
    citation_recall: float = Field(..., description="Alıntı ile Desteklenen İddia / Toplam İddia")


class GenerationBenchmarkItem(BaseModel):
    """Benchmark veri setindeki tek bir sorgunun değerlendirme sonucu."""
    scenario_id: str
    query: str
    category: str
    is_adversarial: bool
    fallback_triggered: bool
    fallback_correct: bool
    faithfulness_rate: float
    citation_precision: float
    citation_recall: float
    has_safety_alert: bool
    latency_ms: float
    answer: GeneratedAnswer


class GenerationBenchmarkReport(BaseModel):
    """15 altın soru üzerinden derlenen üretim ve alıntı kalite raporu."""
    timestamp: str
    total_scenarios: int
    valid_domain_scenarios: int
    adversarial_scenarios: int
    mean_faithfulness_rate: float
    mean_citation_precision: float
    mean_citation_recall: float
    adversarial_fallback_accuracy: float
    avg_latency_ms: float
    items: List[GenerationBenchmarkItem]
