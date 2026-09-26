"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Klasik Segmentasyon Kıyaslaması Veri Modelleri (Otsu, Watershed, GrabCut)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class SegmentationMethod(str, Enum):
    """Desteklenen klasik segmentasyon yöntemleri."""
    OTSU = "OTSU"
    MULTI_OTSU = "MULTI_OTSU"
    WATERSHED = "WATERSHED"
    GRABCUT = "GRABCUT"


class SegmentationClass(int, Enum):
    """Halı segmentasyon sınıf etiketleri."""
    BACKGROUND = 0
    GROUND_FABRIC = 1
    MOTIF = 2
    BORDER = 3


class EvaluationMetrics(BaseModel):
    """İki segmentasyon maskesi arasındaki örtüşme ve kalite metrikleri."""
    iou: float = Field(..., ge=0.0, le=1.0, description="Intersection over Union (Jaccard İndeksi)")
    dice: float = Field(..., ge=0.0, le=1.0, description="Dice Katsayısı (F1 Skoru)")
    pixel_accuracy: float = Field(..., ge=0.0, le=1.0, description="Piksel doğruluğu (TP+TN)/(Total)")
    precision: float = Field(..., ge=0.0, le=1.0, description="Hassasiyet (TP / (TP + FP))")
    recall: float = Field(..., ge=0.0, le=1.0, description="Duyarlılık / Yakalama oranı (TP / (TP + FN))")
    boundary_f1: Optional[float] = Field(None, ge=0.0, le=1.0, description="Sınır kontur örtüşme F1 skoru (BF-Score)")


class AlgorithmBenchmarkResult(BaseModel):
    """Bir segmentasyon algoritmasının hız ve doğruluk benchmark sonucu."""
    method: SegmentationMethod = Field(..., description="Algoritma adı")
    latency_ms: float = Field(..., ge=0.0, description="Ortalama işlem süresi (ms)")
    fps: float = Field(..., ge=0.0, description="Saniyedeki kare sayısı (Frames Per Second)")
    metrics: Optional[EvaluationMetrics] = Field(None, description="Ground Truth maskesine göre doğruluk metrikleri")
    foreground_coverage_pct: float = Field(..., ge=0.0, le=100.0, description="Ön plan motif kaplama yüzdesi (%)")


class CarpetSegmentationReport(BaseModel):
    """Uçtan uca halı segmentasyon kıyaslama ve kalite raporu."""
    image_shape: Tuple[int, int] = Field(..., description="Görüntü boyutları (Yükseklik, Genişlik)")
    evaluated_methods: List[SegmentationMethod] = Field(..., description="Değerlendirilen yöntemlerin listesi")
    results: Dict[str, AlgorithmBenchmarkResult] = Field(..., description="Yöntem bazlı benchmark sonuçları")
    recommended_online_method: SegmentationMethod = Field(..., description="Canlı üretim hattı için önerilen yöntem")
    recommended_offline_method: SegmentationMethod = Field(..., description="Offline kalite laboratuvarı için önerilen yöntem")
    industrial_notes: List[str] = Field(default_factory=list, description="Endüstriyel çıkarımlar ve tavsiyeler")
