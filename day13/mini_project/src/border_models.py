"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Kenar ve Çizgi Tespiti & Jakarlı Halı Bordür Paralellik Analizi Veri Modelleri

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class EdgeOperatorType(str, Enum):
    """Desteklenen kenar operatörü türleri."""
    SOBEL = "SOBEL"
    SCHARR = "SCHARR"
    LAPLACIAN = "LAPLACIAN"
    CANNY = "CANNY"


class BorderSide(str, Enum):
    """Halı bordür kenarı yönü."""
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class QualityDecision(str, Enum):
    """Üretim kalite güvence kabul/red kararı."""
    ACCEPT = "ACCEPT"
    WARNING = "WARNING"
    REJECT = "REJECT"


class LineSegment(BaseModel):
    """PPHT ile tespit edilen tekil çizgi parçası modeli."""
    x1: float = Field(..., description="Başlangıç x koordinatı")
    y1: float = Field(..., description="Başlangıç y koordinatı")
    x2: float = Field(..., description="Bitiş x koordinatı")
    y2: float = Field(..., description="Bitiş y koordinatı")
    length: float = Field(..., ge=0.0, description="Çizgi parçasının Öklid uzunluğu (px)")
    angle_deg: float = Field(..., description="Yatay eksene göre açısı [-90, +90] derece")
    slope: Optional[float] = Field(None, description="Doğru eğimi (dy / dx, dikey ise None)")
    intercept: Optional[float] = Field(None, description="Y-kesişim değeri (y = m*x + b)")


class BorderEdge(BaseModel):
    """Halı kenarını temsil eden nihai bordür doğrusu."""
    side: BorderSide = Field(..., description="Bordür yönü (TOP, BOTTOM, LEFT, RIGHT)")
    x1: float = Field(..., description="Temsilci doğru başlangıç x")
    y1: float = Field(..., description="Temsilci doğru başlangıç y")
    x2: float = Field(..., description="Temsilci doğru bitiş x")
    y2: float = Field(..., description="Temsilci doğru bitiş y")
    angle_deg: float = Field(..., description="Bordürün yatay/dikey eksene göre açısı (derece)")
    segment_count: int = Field(..., ge=0, description="Bordürü oluşturan destekleyici Hough segmenti sayısı")
    straightness_rms: float = Field(..., ge=0.0, description="Doğrudan sapma karekök ortalama hatası (RMS, px)")
    mean_coordinate: float = Field(..., description="Kenarın ortalama konumu (yatay için y, dikey için x)")


class ParallelismMetric(BaseModel):
    """Karşılıklı iki bordür arasındaki paralellik ve mesafe metrikleri."""
    pair_name: str = Field(..., description="Bordür çifti adı (örn. 'TOP-BOTTOM' veya 'LEFT-RIGHT')")
    angle_difference_deg: float = Field(..., ge=0.0, description="İki kenar arasındaki açısal fark (derece)")
    is_parallel: bool = Field(..., description="Tolerans dahilinde paralel mi?")
    distance_min_px: float = Field(..., ge=0.0, description="Kenarlar arası minimum dik mesafe (px)")
    distance_max_px: float = Field(..., ge=0.0, description="Kenarlar arası maksimum dik mesafe (px)")
    distance_mean_px: float = Field(..., ge=0.0, description="Kenarlar arası ortalama dik mesafe (px)")
    distance_std_px: float = Field(..., ge=0.0, description="Kenarlar arası mesafe standart sapması (px)")


class BorderParallelismReport(BaseModel):
    """Uçtan uca halı bordür analizi ve kalite değerlendirme raporu."""
    image_shape: Tuple[int, int] = Field(..., description="Görüntü boyutları (Yükseklik, Genişlik)")
    total_lines_detected: int = Field(..., ge=0, description="Hough dönüşümüyle bulunan toplam çizgi sayısı")
    borders: Dict[str, Optional[BorderEdge]] = Field(..., description="Tespit edilen 4 bordür kenarı")
    horizontal_parallelism: Optional[ParallelismMetric] = Field(None, description="Üst ve Alt bordür paralellik analizi")
    vertical_parallelism: Optional[ParallelismMetric] = Field(None, description="Sol ve Sağ bordür paralellik analizi")
    orthogonality_angle_deg: Optional[float] = Field(None, description="Yatay ve dikey bordürler arasındaki köşe açısı (90° olmalı)")
    orthogonality_deviation_deg: Optional[float] = Field(None, description="90 dereceden sapma mutlak değeri")
    decision: QualityDecision = Field(..., description="Genel rulo kalite kararı")
    decision_notes: List[str] = Field(default_factory=list, description="Karar gerekçeleri ve açıklamaları")
    processing_time_ms: float = Field(..., ge=0.0, description="Analiz toplam işlem süresi (ms)")
