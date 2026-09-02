# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
Veri Modelleri: FastAPI İstek/Yanıt Şemaları ve Sistem DTO'ları
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class OperatorQuery(BaseModel):
    """
    Şekil 75 uyumlu operatör sorgu DTO şeması.
    FastAPI /api/v1/process-operator-query uç noktası için girdi modeli.
    """
    query: str = Field(..., description="Operatörün sorduğu teknik soru")
    loom_id: Optional[str] = Field(default="TEZGAH-01", description="Tezgâh kodu")
    shift: Optional[str] = Field(default="VARDIYA-1", description="Vardiya kodu")
    operator_id: Optional[str] = Field(default="OP-104", description="Operatör kimlik no")
    top_k: int = Field(default=5, description="Getirilecek benzer doküman sayısı")


class OperatorQueryRequest(BaseModel):
    """Dokuma salonu operatörünün API'ye gönderdiği arıza / bilgi sorgusu."""
    query: str = Field(..., min_length=3, description="Operatörün sorduğu teknik soru veya arıza semptomu")
    loom_id: str = Field(default="TEZGAH-01", description="Sorgunun geldiği jakarlı dokuma tezgâhı kodu")
    shift_id: str = Field(default="VARDIYA-1", description="Aktif vardiya kodu (VARDIYA-1, VARDIYA-2, VARDIYA-3)")
    operator_id: str = Field(default="OP-104", description="Operatör sicil / kimlik numarası")
    include_metrics: bool = Field(default=True, description="Ragas Triad kalite metriklerinin hesaplanıp dönülmesi")
    top_k: int = Field(default=5, description="Getirilecek benzer doküman sayısı")


class CitationDto(BaseModel):
    """Nihai yanıtta yer alan teknik doküman alıntısı."""
    source_id: str = Field(..., description="Referans alınan doküman veya PDF adı")
    chunk_id: str = Field(default="", description="Bilgi tabanındaki parça kimliği")
    quote: str = Field(..., description="Metinden doğrudan yapılan alıntı")
    title: Optional[str] = Field(default=None, description="Doküman başlığı")
    document: Optional[str] = Field(default=None, description="Dosya adı")
    similarity: Optional[str] = Field(default=None, description="Benzerlik yüzdesi")
    score: Optional[float] = Field(default=None, description="Benzerlik skoru")
    badge: Optional[str] = Field(default="Teknik", description="Doküman kategorisi")
    page_number: Optional[int] = Field(None, description="Alıntının bulunduğu sayfa")
    section: Optional[str] = Field(None, description="Doküman bölüm başlığı")
    verified: bool = Field(default=True, description="Alıntının NLI doğrulanma durumu")


class GuardrailStatusDto(BaseModel):
    """Güvenlik korkuluğu (Guardrail) denetim kararı ve durumu."""
    action: str = Field(..., description="ALLOW, BLOCK veya MODIFY")
    reason: str = Field(..., description="Kararın gerekçesi ve İSG kuralı açıklaması")
    violation_category: Optional[str] = Field(None, description="ISG_VIOLATION, PARAMETER_OUT_OF_BOUNDS vb.")
    is_blocked: bool = Field(default=False, description="Yanıtın engellenip engellenmediği")
    sanitized_content: Optional[str] = Field(None, description="Engellenme durumunda dönülen standart ikaz metni")
    status: Optional[str] = Field(default="Güvenli", description="Arayüz için okunabilir durum etiketi")


class RagasMetricsDto(BaseModel):
    """Getirme ve üretim kalitesini ölçen Ragas Triad metrikleri."""
    context_precision: float = Field(..., ge=0.0, le=1.0, description="Getirilen parçaların alaka ve sıralama başarısı")
    context_recall: float = Field(..., ge=0.0, le=1.0, description="Dokümandaki teknik iddiaların kapsanma oranı")
    faithfulness: float = Field(..., ge=0.0, le=1.0, description="Bağlama sadakat (1 - Halüsinasyon)")
    answer_relevance: float = Field(..., ge=0.0, le=1.0, description="Sorulan teknik soruyla anlamsal örtüşme")
    rag_triad_score: float = Field(..., ge=0.0, le=1.0, description="Harmonik kalite skoru")
    found_documents: Optional[int] = Field(default=5, description="Bulunan doküman sayısı")
    latency_sec: Optional[float] = Field(default=1.38, description="Yanıt süresi (saniye)")
    similarity_score: Optional[str] = Field(default="%87", description="En yüksek benzerlik skoru")
    model: Optional[str] = Field(default="local-rag", description="Kullanılan RAG modeli")


class OperatorQueryResponse(BaseModel):
    """FastAPI tarafından operatöre veya SCADA paneline dönülen yapılandırılmış yanıt."""
    request_id: str = Field(..., description="İsteğe atanan benzersiz takip kimliği")
    query: str = Field(..., description="İşlenen operatör sorusu")
    loom_id: str = Field(..., description="Hedef tezgâh kodu")
    shift_id: str = Field(..., description="Vardiya kodu")
    direct_answer: str = Field(..., description="Doğrudan teknik teşhis veya standart ikaz")
    answer: Optional[str] = Field(default=None, description="Arayüz ve Şekil 75 uyumlu cevap alanı")
    technical_steps: List[str] = Field(default_factory=list, description="Adım adım operatör müdahale kılavuzu")
    action_steps: List[str] = Field(default_factory=list, description="Arayüz ve Şekil 76 uyumlu aksiyon adımları")
    key_parameters: Dict[str, str] = Field(default_factory=dict, description="Önemli fiziksel parametreler")
    citations: List[CitationDto] = Field(default_factory=list, description="Doğrulanmış doküman alıntıları")
    safety_status: GuardrailStatusDto = Field(..., description="İSG ve halüsinasyon güvenlik durumu")
    metrics: Optional[RagasMetricsDto] = Field(None, description="Hesaplanan Ragas Triad metrikleri")
    latency_ms: float = Field(..., description="Toplam uçtan uca yanıt süresi (milisaniye)")
    timestamp: str = Field(..., description="İşlem zaman damgası")


class GuardrailCheckRequest(BaseModel):
    """Yalnızca güvenlik ve İSG kontrolü yapmak için kullanılan hızlı istek şeması."""
    text: str = Field(..., min_length=3, description="Kontrol edilecek metin veya operatör komutu")
    check_type: str = Field(default="INPUT", description="INPUT (girdi) veya OUTPUT (çıktı)")


class LoomItemDto(BaseModel):
    """Fabrika tezgâh kaydı DTO."""
    id: str
    model: str
    series: str
    status: str


class LoomListResponse(BaseModel):
    """Fabrika tezgâhları listesi yanıtı."""
    total_looms: int
    looms: List[LoomItemDto]


class HealthResponse(BaseModel):
    """API ve alt sistemlerin canlılık ve sağlık durumu."""
    status: str = Field(default="HEALTHY")
    version: str = Field(default="1.0.0")
    facility: str
    weaving_hall: str
    knowledge_base_chunks: int
    retriever_status: str
    guardrail_status: str
    uptime_seconds: float


class SystemMetricsResponse(BaseModel):
    """API servisinin çalışma süresince topladığı istatistikler ve sayaçlar."""
    total_queries: int
    blocked_queries: int
    allowed_queries: int
    interception_rate: float
    avg_latency_ms: float
    loom_query_counts: Dict[str, int]
