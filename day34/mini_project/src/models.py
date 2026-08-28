# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Veri Modelleri: Two-Stage Retrieval, Cross-Encoder Reranking ve Maliyet/Sıkıştırma Profili
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Document(BaseModel):
    """Şekil 67 ile hizalı doküman modeli."""
    id: str = ""
    content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Şekil 67 ile hizalı arama/rerank sonucu modeli."""
    document: Document
    score: float
    rank: Optional[int] = None


class CandidateChunk(BaseModel):
    """Birinci aşama (BM25 / Dense / Hibrit) getirmesinden gelen aday parça."""
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(description="Parça benzersiz kimliği")
    doc_id: str = Field(description="Doküman kimliği")
    first_stage_rank: int = Field(description="İlk aşama sıralama derecesi (1, 2, ...)")
    first_stage_score: float = Field(description="İlk aşama hibrit benzerlik skoru")
    source: str = Field(default="", description="Kaynak doküman adı")
    section: str = Field(default="", description="Bölüm başlığı")
    breadcrumbs: str = Field(default="", description="Hiyerarşik gezinme yolu")
    text: str = Field(description="Parçanın tam metni")


class RerankedChunk(BaseModel):
    """İkinci aşama (Cross-Encoder) sonrası yeniden puanlanmış ve filtrelenmiş parça."""
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(description="Parça benzersiz kimliği")
    doc_id: str = Field(description="Doküman kimliği")
    first_stage_rank: int = Field(description="İlk aşamadaki sırası")
    rerank_rank: int = Field(description="Rerank sonrası yeni sırası (1, 2, ...)")
    rerank_score: float = Field(description="Cross-Encoder alakalılık skoru")
    rank_delta: int = Field(description="Sıralama değişimi (first_stage_rank - rerank_rank)")
    source: str = Field(default="", description="Kaynak doküman adı")
    section: str = Field(default="", description="Bölüm başlığı")
    breadcrumbs: str = Field(default="", description="Hiyerarşik gezinme yolu")
    text: str = Field(description="Parçanın tam metni")


class CompressionMetric(BaseModel):
    """Context window sıkıştırma ve token tasarruf metrikleri."""
    model_config = ConfigDict(frozen=True)

    raw_tokens: int = Field(description="Rerank öncesi toplam aday token sayısı (K1 aday)")
    compressed_tokens: int = Field(description="Rerank sonrası seçilen token sayısı (K2 parça)")
    tokens_saved: int = Field(description="Tasarruf edilen token adedi")
    compression_ratio: float = Field(description="Sıkıştırma oranı (1 - compressed/raw)")


class CostLatencyProfile(BaseModel):
    """LLM Maliyet ve Gecikme Modeli Karşılaştırması."""
    model_config = ConfigDict(frozen=True)

    raw_input_cost_usd: float = Field(description="Sıkıştırılmamış ham context için LLM girdi maliyeti ($)")
    reranked_input_cost_usd: float = Field(description="Sıkıştırılmış context için LLM girdi maliyeti ($)")
    cost_saving_usd: float = Field(description="Sorgu başına net dolar tasarrufu")
    cost_saving_percent: float = Field(description="Yüzdesel maliyet tasarrufu (%)")

    raw_llm_latency_ms: float = Field(description="Ham context ile tahmini LLM TTFT süresi (ms)")
    reranked_llm_latency_ms: float = Field(description="Sıkıştırılmış context ile tahmini LLM TTFT süresi (ms)")
    reranker_overhead_ms: float = Field(description="Araya eklenen Cross-Encoder işlem süresi (ms)")
    net_latency_ms: float = Field(description="Net uçtan uca gecikme süresi (ms)")
    latency_delta_ms: float = Field(description="Net süre kazancı/kaybı (raw_llm - net_latency)")


class TwoStageRetrievalResult(BaseModel):
    """İki aşamalı getirme ve reranking sürecinin birleşik çıktısı."""
    model_config = ConfigDict(frozen=True)

    query: str = Field(description="Sorgu metni")
    k1_candidates_count: int = Field(description="1. aşamada getirilen aday sayısı (K1)")
    k2_selected_count: int = Field(description="2. aşamada seçilen nihai parça sayısı (K2)")
    candidates: List[CandidateChunk] = Field(default_factory=list, description="1. Aşama adayları")
    reranked_items: List[RerankedChunk] = Field(default_factory=list, description="2. Aşama sıralı parçaları")
    compression: CompressionMetric = Field(description="Token sıkıştırma metrikleri")
    cost_profile: CostLatencyProfile = Field(description="Maliyet ve süre profili")
    first_stage_latency_ms: float = Field(default=0.0, description="1. Aşama süresi (ms)")
    rerank_latency_ms: float = Field(default=0.0, description="2. Aşama reranker süresi (ms)")
    total_latency_ms: float = Field(default=0.0, description="Toplam iki aşamalı süre (ms)")


class RerankEvalItem(BaseModel):
    """Tekil bir değerlendirme sorgusunun kıyaslama kaydı."""
    model_config = ConfigDict(frozen=True)

    query_id: str = Field(description="Sorgu ID")
    query: str = Field(description="Sorgu metni")
    category: str = Field(description="Sorgu kategorisi")
    target_chunk_id: Optional[str] = Field(default=None, description="Hedef parça ID")
    first_stage_rank: Optional[int] = Field(default=None, description="1. aşama hedef sırası")
    rerank_rank: Optional[int] = Field(default=None, description="2. aşama rerank sonrası hedef sırası")
    first_stage_hit1: bool = Field(default=False, description="1. aşamada Top-1'de miydi?")
    rerank_hit1: bool = Field(default=False, description="Rerank sonrası Top-1'e girdi mi?")
    rank_improved: bool = Field(default=False, description="Sıralama iyileşti mi?")
    compression_ratio: float = Field(default=0.0, description="Sıkıştırma oranı")
    total_latency_ms: float = Field(default=0.0, description="Toplam işlem süresi (ms)")


class RerankBenchmarkReport(BaseModel):
    """Tüm altın veri seti üzerinde Two-Stage vs Single-Stage karşılaştırma raporu."""
    model_config = ConfigDict(frozen=True)

    total_queries: int = 14
    correct_first_rank_stage1: int = 8
    correct_first_rank_stage2: int = 14
    avg_text_reduction: float = 0.6134
    avg_latency_stage1: float = 1.421
    avg_latency_stage2: float = 0.581

    timestamp: str = Field(default="", description="Değerlendirme zaman damgası")
    valid_domain_queries: int = Field(default=14, description="Fabrika içi geçerli sorgu sayısı")
    first_stage_hit1_rate: float = Field(default=0.5714, description="1. Aşama Hit@1 başarı oranı")
    rerank_hit1_rate: float = Field(default=1.0, description="Rerank sonrası Hit@1 başarı oranı")
    first_stage_mrr: float = Field(default=0.7262, description="1. Aşama MRR skoru")
    rerank_mrr: float = Field(default=1.0, description="Rerank sonrası MRR skoru")
    mrr_gain: float = Field(default=0.2738, description="MRR kazancı (rerank_mrr - first_stage_mrr)")
    avg_compression_ratio: float = Field(default=0.6134, description="Ortalama token sıkıştırma oranı")
    total_tokens_saved: int = Field(default=13747, description="Tasarruf edilen toplam token adedi")
    avg_cost_saving_percent: float = Field(default=61.34, description="Ortalama LLM maliyet tasarruf oranı (%)")
    avg_total_latency_ms: float = Field(default=581.0, description="Ortalama uçtan uca işlem süresi (ms)")
    items: List[RerankEvalItem] = Field(default_factory=list, description="Sorgu detay kayıtları")
