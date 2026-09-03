# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Pydantic DTO ve Veri Modelleri: Profilleme, Kuantizasyon ve Edge Çıkarım Yapıları
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LatencyDistribution(BaseModel):
    """Gecikme İstatistikleri (ms)."""
    p50_ms: float = Field(..., description="Medyan gecikme (50. persentil)")
    p95_ms: float = Field(..., description="95. persentil kuyruk gecikmesi")
    p99_ms: float = Field(..., description="99. persentil kuyruk gecikmesi")
    mean_ms: float = Field(..., description="Ortalama gecikme")
    std_ms: float = Field(..., description="Standart sapma")
    min_ms: float = Field(..., description="Minimum gecikme")
    max_ms: float = Field(..., description="Maksimum gecikme")


class ModelSizeReport(BaseModel):
    """Model Dosya Boyutu ve Sıkıştırma Karnesi."""
    original_bytes: int = Field(..., description="FP32 orijinal bayt boyutu")
    original_mb: float = Field(..., description="FP32 megabayt boyutu")
    quantized_bytes: int = Field(..., description="INT8 kuantize bayt boyutu")
    quantized_mb: float = Field(..., description="INT8 megabayt boyutu")
    reduction_percentage: float = Field(..., description="Boyut küçülme yüzdesi (% reduction)")
    compression_ratio: float = Field(..., description="Sıkıştırma oranı (ör: 3.9x)")


class AccuracyPreservation(BaseModel):
    """FP32 vs INT8 Çıktı Sadakati ve Hassasiyet Korunumu."""
    cosine_similarity: float = Field(..., description="Ortalama kosinüs benzerliği")
    mean_absolute_error: float = Field(..., description="Ortalama mutlak hata (MAE)")
    max_absolute_error: float = Field(..., description="Maksimum mutlak hata")
    is_tolerable: bool = Field(..., description="Endüstriyel tolerans sınırları içinde mi?")


class HardwareProfiling(BaseModel):
    """Donanım ve Yürütme Parametreleri."""
    thread_count: int = Field(..., description="Kullanılan CPU iş parçacığı sayısı")
    cpu_architecture: str = Field("x86_64", description="CPU mimarisi")
    memory_rss_mb: float = Field(..., description="İşlem yerleşik bellek tüketimi (RSS MB)")
    throughput_qps: float = Field(..., description="Saniyedeki sorgu sayısı (Queries Per Second)")


class EngineBenchmarkItem(BaseModel):
    """Tekil Çıkarım Motoru Kıyaslama Kaydı."""
    model_name: str = Field(..., description="Model adı (Bi-Encoder / Cross-Encoder)")
    engine_type: str = Field(..., description="Motor türü: PyTorch_FP32, ONNX_FP32, ONNX_INT8")
    latency: LatencyDistribution = Field(..., description="Gecikme dağılımı")
    accuracy: Optional[AccuracyPreservation] = Field(None, description="Hassasiyet korunumu")
    hardware: HardwareProfiling = Field(..., description="Donanım profili")


class EdgeQueryResult(BaseModel):
    """Tezgâh Başı Yerel Arama ve Sıralama Sonucu."""
    query: str = Field(..., description="Operatörün sorduğu soru")
    loom_id: str = Field("TEZGAH-01", description="Tezgâh kodu")
    retrieved_doc_ids: List[str] = Field(default_factory=list, description="Getirilen doküman kimlikleri")
    scores: List[float] = Field(default_factory=list, description="Relevance / Cosine benzerlik skorları")
    execution_time_ms: float = Field(..., description="Toplam uçtan uca çıkarım süresi (ms)")
    engine_used: str = Field("ONNX_INT8", description="Kullanılan çıkarım motoru")


class ThreadScalingItem(BaseModel):
    """İş Parçacığı Ölçekleme Analizi."""
    thread_count: int
    mean_latency_ms: float
    throughput_qps: float


class EdgeBenchmarkReport(BaseModel):
    """GÜN 39 Kapsamlı Model Sıkıştırma ve Edge Dağıtım Raporu."""
    timestamp: str = Field(..., description="Rapor üretim zamanı")
    factory_site: str = Field("Merinos Gaziantep Halı Fabrikası", description="Fabrika lokasyonu")
    bi_encoder_size: ModelSizeReport = Field(..., description="Bi-Encoder boyut raporu")
    cross_encoder_size: ModelSizeReport = Field(..., description="Cross-Encoder boyut raporu")
    benchmark_items: List[EngineBenchmarkItem] = Field(default_factory=list, description="Kıyaslama sonuçları")
    thread_scaling: List[ThreadScalingItem] = Field(default_factory=list, description="Thread ölçekleme karnesi")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Yönetici özeti ve çıkarımlar")
