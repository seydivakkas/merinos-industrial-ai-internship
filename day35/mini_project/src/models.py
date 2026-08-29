# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Veri Modelleri: Query Transformation, HyDE ve Çoklu Sorgu Genişletmesi
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TransformedQuery(BaseModel):
    """Operatörün ham sorgusunun farklı teknik temsillere dönüştürülmüş hali."""
    model_config = ConfigDict(frozen=True)

    raw_query: str = Field(description="Operatörün yazdığı ham/gürültülü sorgu")
    rewritten_query: str = Field(description="Resmi mühendislik diline normalize edilmiş sorgu")
    sub_queries: List[str] = Field(default_factory=list, description="Çoklu perspektif alt sorguları (Multi-Query)")
    hypothetical_doc: str = Field(description="HyDE ile üretilmiş varsayımsal fabrika SOP dokümanı")


class MethodResult(BaseModel):
    """Belirli bir arama/dönüştürme yönteminin tekil getirme çıktısı."""
    model_config = ConfigDict(frozen=True)

    method_name: str = Field(description="RAW, REWRITE, MULTI_QUERY, HYDE veya RRF_FUSED")
    retrieved_chunk_ids: List[str] = Field(default_factory=list, description="Getirilen parça kimlikleri sıralı listesi")
    target_rank: Optional[int] = Field(default=None, description="Hedef parçanın bu yöntemdeki sıralaması (1, 2, ...)")
    hit_at_1: bool = Field(default=False, description="Hedef parça 1. sırada mı?")
    hit_at_3: bool = Field(default=False, description="Hedef parça Top-3'te mi?")
    reciprocal_rank: float = Field(default=0.0, description="1 / target_rank skoru")
    latency_ms: float = Field(default=0.0, description="Yöntemin toplam yanıt süresi (ms)")


class QueryTransformBenchmarkItem(BaseModel):
    """Tekil bir test sorgusunun tüm yöntemler bazındaki karşılaştırma kaydı."""
    model_config = ConfigDict(frozen=True)

    query_id: str = Field(description="Sorgu ID")
    noisy_query: str = Field(description="Ham operatör sorgusu")
    category: str = Field(description="Sorgu kategorisi")
    target_chunk_id: Optional[str] = Field(default=None, description="Doğru hedef parça ID")

    raw_rank: Optional[int] = Field(default=None, description="Ham sorgu sıralaması")
    rewrite_rank: Optional[int] = Field(default=None, description="Query Rewriting sıralaması")
    multi_query_rank: Optional[int] = Field(default=None, description="Multi-Query sıralaması")
    hyde_rank: Optional[int] = Field(default=None, description="HyDE sıralaması")
    fused_rank: Optional[int] = Field(default=None, description="RRF Birleşik sıralama")

    rank_improved: bool = Field(default=False, description="Ham sorguya göre iyileşme sağlandı mı?")
    best_method: str = Field(default="RAW", description="Bu sorguyu en iyi getiren yöntem")


class QueryTransformBenchmarkReport(BaseModel):
    """15 gürültülü sorgu üzerinde yöntemlerin toplu başarım raporu."""
    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(description="Test zaman damgası")
    total_queries: int = Field(description="Toplam test sorgusu")
    valid_domain_queries: int = Field(description="Geçerli fabrika içi sorgu adedi")

    raw_hit1_rate: float = Field(description="Ham sorgu Hit@1 başarı yüzdesi")
    rewrite_hit1_rate: float = Field(description="Rewriting Hit@1 başarı yüzdesi")
    multi_query_hit1_rate: float = Field(description="Multi-Query Hit@1 başarı yüzdesi")
    hyde_hit1_rate: float = Field(description="HyDE Hit@1 başarı yüzdesi")
    fused_hit1_rate: float = Field(description="RRF Fused Hit@1 başarı yüzdesi")

    raw_mrr: float = Field(description="Ham sorgu MRR skoru")
    rewrite_mrr: float = Field(description="Rewriting MRR skoru")
    multi_query_mrr: float = Field(description="Multi-Query MRR skoru")
    hyde_mrr: float = Field(description="HyDE MRR skoru")
    fused_mrr: float = Field(description="RRF Fused MRR skoru")

    mrr_gain_hyde: float = Field(description="HyDE MRR kazancı (hyde_mrr - raw_mrr)")
    mrr_gain_fused: float = Field(description="Birleşik RRF MRR kazancı (fused_mrr - raw_mrr)")

    avg_raw_latency_ms: float = Field(description="Ham getirme ortalama gecikmesi (ms)")
    avg_fused_latency_ms: float = Field(description="Birleşik getirme ortalama gecikmesi (ms)")

    items: List[QueryTransformBenchmarkItem] = Field(default_factory=list, description="Sorgu bazlı detay kayıtları")
