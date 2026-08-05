"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Geleneksel Öznitelik Çıkarımı ve Desen Sınıflandırma Pydantic Modelleri

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class PatternClass(str, Enum):
    """Merinos jakarlı halı desen kategorileri."""
    MEDALLION_CLASSIC = "MEDALLION_CLASSIC"
    GEOMETRIC_MODERN = "GEOMETRIC_MODERN"
    FLORAL_TRADITIONAL = "FLORAL_TRADITIONAL"
    VINTAGE_DISTRESSED = "VINTAGE_DISTRESSED"


class KeypointDescriptorType(str, Enum):
    """Kullanılan yerel anahtar nokta algoritması."""
    ORB = "ORB"
    SIFT = "SIFT"


class KeypointStats(BaseModel):
    """Anahtar nokta yoğunluğu ve uzamsal dağılım istatistikleri."""
    count: int = Field(..., description="Tespit edilen toplam anahtar nokta sayısı")
    mean_response: float = Field(..., description="Ortalama köşe/gradyan tepki değeri")
    mean_size: float = Field(..., description="Ortalama ölçek/boyut (piksel)")
    angle_entropy: float = Field(..., description="Anahtar nokta yönelim açılarının entropisi (rotasyon çeşitliliği)")


class GLCMFeatures(BaseModel):
    """Haralick gri seviye eş-oluşum matrisi doku öznitelikleri."""
    contrast: float = Field(..., description="Yerel gri seviye varyasyonu ve iplik sıklığı")
    dissimilarity: float = Field(..., description="Komşu pikseller arası ortalama gri seviye farkı")
    homogeneity: float = Field(..., description="Yerel pürüzsüzlük ve doku düzeni")
    energy: float = Field(..., description="Açısal ikinci moment (ASM), doku periyodikliği")
    correlation: float = Field(..., description="Doğrusal bağımlılık ve doku yönelimi")
    entropy: float = Field(..., description="Doku rastgeleliği ve karmaşıklığı")
    direction_variance: float = Field(..., description="Farklı açılardaki (0, 45, 90, 135) özellik varyansı")


class ColorHistogramFeatures(BaseModel):
    """Çok kanallı normalize 3D renk histogramı öznitelikleri."""
    dimension: int = Field(..., description="Histogram toplam bin sayısı (örn. 16x8x8 = 1024)")
    top_bins: List[Tuple[int, float]] = Field(..., description="En baskın ilk 5 bin indeksi ve oranları")
    entropy: float = Field(..., description="Renk dağılımı Shannon entropisi")
    peak_bin_value: float = Field(..., description="En baskın rengin oransal ağırlığı")


class CarpetFeatureVector(BaseModel):
    """Birleştirilmiş (Fused) normalize halı öznitelik vektörü."""
    image_name: str = Field(..., description="Halı görseli adı veya dosya yolu")
    total_dimension: int = Field(..., description="Toplam birleştirilmiş vektör boyutu")
    glcm_dim: int = Field(..., description="GLCM doku öznitelik boyutu")
    color_hist_dim: int = Field(..., description="Renk histogramı öznitelik boyutu")
    keypoint_dim: int = Field(..., description="Anahtar nokta istatistik vektör boyutu")
    vector: List[float] = Field(..., description="L2 normalize birleşik öznitelik vektörü")
    pattern_class: Optional[PatternClass] = Field(None, description="Etiketli desen sınıfı (varsa)")


class PatternMatchResult(BaseModel):
    """Desen benzerlik sorgusu ve eşleşme sonucu."""
    query_name: str = Field(..., description="Sorgu görselinin adı")
    catalog_name: str = Field(..., description="Katalogdaki eşleşen görselin adı")
    predicted_class: PatternClass = Field(..., description="Tahmin edilen desen sınıfı")
    similarity_score: float = Field(..., description="Kosinüs benzerlik skoru (%0-100)")
    distance: float = Field(..., description="Öklid veya Kosinüs mesafesi")
    good_matches_count: Optional[int] = Field(None, description="Lowe ratio testinden geçen anahtar nokta sayısı")
    inlier_ratio: Optional[float] = Field(None, description="RANSAC homografi uyumlu inlier oranı")


class FeatureBenchmarkReport(BaseModel):
    """Öznitelik çıkarımı ve görsel arama hız/başarı raporu."""
    orb_latency_ms: float = Field(..., description="ORB ortalama çıkarım süresi (ms)")
    orb_fps: float = Field(..., description="ORB Throughput (FPS)")
    sift_latency_ms: float = Field(..., description="SIFT ortalama çıkarım süresi (ms)")
    sift_fps: float = Field(..., description="SIFT Throughput (FPS)")
    glcm_latency_ms: float = Field(..., description="GLCM ortalama çıkarım süresi (ms)")
    glcm_fps: float = Field(..., description="GLCM Throughput (FPS)")
    retrieval_latency_ms: float = Field(..., description="Katalogda Top-K arama süresi (ms)")
    classification_accuracy: float = Field(..., description="4 sınıflı desen sınıflandırma başarısı (%0-100)")
    industrial_recommendations: List[str] = Field(..., description="Üretim hattı ve laboratuvar önerileri")
