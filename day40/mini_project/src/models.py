# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 40 (BÜYÜK FİNAL)
Pydantic DTO ve Veri Modelleri: Çok Modlu Teşhis, Sistem Sağlığı ve Staj KPI Modelleri
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SubsystemStatus(BaseModel):
    """Tekil Alt Sistem Sağlık ve Kaynak Durumu."""
    subsystem_name: str = Field(..., description="Alt sistem adı")
    pillar_id: str = Field(..., description="Ait olduğu sütun (Pillar 1-4)")
    status: str = Field("HEALTHY", description="Durum: HEALTHY, DEGRADED, OFFLINE")
    memory_mb: float = Field(..., description="Bellek tüketimi (MB)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Ek operasyonel ayrıntılar")


class SystemHealthDTO(BaseModel):
    """Tüm Fabrika Yapay Zekâ Platformunun Genel Sağlık Durumu."""
    overall_status: str = Field("HEALTHY", description="Genel sistem durumu")
    timestamp: str = Field(..., description="Kontrol zamanı")
    total_subsystems: int = Field(..., description="İzlenen alt sistem sayısı")
    subsystems: List[SubsystemStatus] = Field(default_factory=list, description="Alt sistem detayları")
    total_memory_mb: float = Field(..., description="Platform toplam bellek tüketimi (MB)")


class MultiModalIncidentInput(BaseModel):
    """Dokuma Tezgâhından Gelen Çok Modlu Olay Verisi."""
    loom_id: str = Field("TEZGAH-01", description="Tezgâh kodu")
    error_code: Optional[str] = Field(None, description="Aktif arıza kodu (ör: E-401)")
    telemetry: Dict[str, float] = Field(default_factory=dict, description="Sensör telemetrisi (sıcaklık, basınç)")
    vision_defect_detected: bool = Field(False, description="Kamera ile dokuma kusuru tespit edildi mi?")
    defect_type: Optional[str] = Field(None, description="Kusur türü (atkı kopması, ilme kaçığı)")
    operator_query: str = Field(..., description="Operatörün sorduğu soru veya aksiyon talebi")


class MultiModalIncidentDiagnosis(BaseModel):
    """Entegre Yapay Zekâ Platformunun Ürettiği Çok Modlu Teşhis ve Eylem Planı."""
    incident_id: str = Field(..., description="Olay takip kimliği")
    loom_id: str = Field(..., description="Tezgâh kodu")
    root_cause_analysis: str = Field(..., description="Kök neden analizi")
    defect_risk_score: float = Field(..., description="Kusur ve duruş risk skoru (0.0 - 1.0)")
    action_plan: List[str] = Field(default_factory=list, description="Operatör için adım adım eylem planı")
    technical_parameters: Dict[str, str] = Field(default_factory=dict, description="Kritik çalışma parametreleri")
    isg_clearance: str = Field("ISG_APPROVED", description="İSG onay durumu: ISG_APPROVED veya ISG_BLOCKED")
    safety_warning: Optional[str] = Field(None, description="İş güvenliği ikazı")
    citations: List[str] = Field(default_factory=list, description="Teknik kılavuz referans alıntıları")
    execution_latency_ms: float = Field(..., description="Toplam çok modlu teşhis süresi (ms)")


class InternshipKPIMetrics(BaseModel):
    """40 Günlük Staj Maratonunun Endüstriyel KPI ve ROI Göstergeleri."""
    annual_downtime_saved_hours: float = Field(..., description="Yıllık tasarruf edilen tezgâh duruş süresi (saat)")
    annual_financial_savings_try: float = Field(..., description="Yıllık tahmini finansal kazanım (TL)")
    scrap_reduction_percentage: float = Field(..., description="Halı dokuma firesindeki net düşüş oranı (%)")
    average_edge_latency_ms: float = Field(..., description="Tezgâh başı ortalama yerel çıkarım süresi (ms)")
    model_compression_percentage: float = Field(..., description="Model sıkıştırma oranı (% reduction)")
    total_tests_passed: int = Field(..., description="Başarıyla geçen birim ve entegrasyon test sayısı")
    test_pass_rate: float = Field(100.0, description="Test başarı yüzdesi (%)")


class MasterPlatformReport(BaseModel):
    """GÜN 40 Büyük Final Kapanış ve Entegrasyon Raporu."""
    platform_name: str = Field("Merinos Industrial AI Master Platform", description="Platform adı")
    version: str = Field("1.0.0", description="Yazılım sürümü")
    organization: str = Field("Merinos Halı Sanayi ve Ticaret A.Ş. - Gaziantep", description="Kurum")
    author: str = Field("Seydi Eryılmaz (@seydivakkas)", description="Geliştirici")
    health: SystemHealthDTO = Field(..., description="Platform sağlık raporu")
    kpis: InternshipKPIMetrics = Field(..., description="Kümülatif KPI ve ROI metrikleri")
    four_pillars_summary: Dict[str, Any] = Field(default_factory=dict, description="4 sütun başarım özeti")
    curriculum_matrix: Dict[str, str] = Field(default_factory=dict, description="40 günün konu matrisi")
    production_readiness_verdict: str = Field("POC_COMPLETED_SUCCESSFULLY", description="PoC başarı ve üretime hazırlık kararı")
    license_type: str = Field("ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR", description="Lisans tipi")
