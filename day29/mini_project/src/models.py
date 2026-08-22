"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Üretilen Halı Görsellerinin Çok Boyutlu Analizi
Staj Defteri Yaprak 57 ve 58 Veri Modelleri
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


class DominantColor(BaseModel):
    """K-Means ile çıkarılan tekil baskın renk modeli."""
    cluster_index: int = Field(..., description="K-Means küme indeksi")
    rgb: Tuple[int, int, int] = Field(..., description="RGB renk değerleri (0-255)")
    hex_code: str = Field(..., description="Hex renk kodu (#RRGGBB)")
    lab: Tuple[float, float, float] = Field(..., description="CIELAB (L*, a*, b*) renk koordinatları")
    percentage: float = Field(..., description="Görsel içindeki piksel kapsama yüzdesi (%)")
    nearest_yarn_name: Optional[str] = Field(None, description="En yakın Merinos kurumsal iplik bobin rengi")
    delta_e_to_target: Optional[float] = Field(None, description="En yakın hedef renge olan Delta E mesafesi")


class ColorAnalysisResult(BaseModel):
    """Yaprak 57: K-Means Renk Paleti ve CIELAB Delta E* Analiz Sonuçları."""
    num_clusters: int = Field(5, description="K-Means küme sayısı")
    dominant_colors: List[DominantColor] = Field(default_factory=list, description="Baskın renkler listesi")
    target_palette_name: Optional[str] = Field(None, description="Karşılaştırılan Merinos hedef paleti adı")
    mean_delta_e: float = Field(0.0, description="Hedef renklerle ortalama Delta E sapması")
    min_delta_e: float = Field(0.0, description="En yakın renk eşleşmesindeki Delta E")
    verdict: str = Field(..., description="Mühendislik renk yakınlığı ve algısal değerlendirme yorumu")


class SymmetryAnalysisResult(BaseModel):
    """Yaprak 57: Simetri ve Tekrar Yapısının İncelenmesi Sonuçları."""
    horizontal_symmetry: float = Field(..., ge=0.0, le=1.0, description="Yatay ayna simetri skoru (0: asimetrik, 1: kusursuz ayna)")
    vertical_symmetry: float = Field(..., ge=0.0, le=1.0, description="Dikey ayna simetri skoru (0: asimetrik, 1: kusursuz)")
    four_way_symmetry: float = Field(..., ge=0.0, le=1.0, description="4-çeyrek saray halısı simetri skoru")
    repeat_autocorrelation_score: float = Field(..., ge=0.0, le=1.0, description="Otokorelasyon tabanlı periyodik desen tekrar hissi skoru")
    verdict: str = Field(..., description="Yapısal düzen ve simetri mühendislik değerlendirmesi")


class SeamContinuityResult(BaseModel):
    """Yaprak 58: Kenar ve Dikiş Sürekliliği (Tileability) Analiz Sonuçları."""
    strip_width_pixels: int = Field(8, description="İncelenen kenar şeridi genişliği (piksel)")
    left_right_mse: float = Field(..., ge=0.0, description="Sol ve sağ kenar arasındaki piksel MSE farkı")
    top_bottom_mse: float = Field(..., ge=0.0, description="Üst ve alt kenar arasındaki piksel MSE farkı")
    continuity_score: float = Field(..., ge=0.0, le=1.0, description="Birleşik dikiş süreklilik skoru (1.0 = kusursuz uç uca döşenebilir)")
    has_seam_discontinuity: bool = Field(..., description="Kenarlarda ani kopukluk veya motif kırılması var mı?")
    verdict: str = Field(..., description="Dikiş ve kenar sürekliliği teknik değerlendirmesi")


class CarpetMatch(BaseModel):
    """CNN Embedding ile Top-K benzerlik eşleşmesi."""
    rank: int = Field(..., description="Benzerlik sıralaması (1, 2, ...)")
    carpet_id: str = Field(..., description="Referans halı kimliği")
    title: str = Field(..., description="Referans halı ürün adı")
    style: str = Field(..., description="Halı deseni stili")
    similarity_score: float = Field(..., ge=-1.0, le=1.0, description="Cosine Similarity skoru (0.0 - 1.0)")
    primary_colors: List[str] = Field(default_factory=list, description="Katalogdaki ana renkler")


class CNNEmbeddingResult(BaseModel):
    """Yaprak 58: Pretrained CNN Embedding ve Top-K Benzerlik Sonuçları."""
    backbone: str = Field("ResNet18", description="Kullanılan CNN omurgası")
    embedding_dim: int = Field(512, description="Latent görsel öznitelik vektör boyutu")
    l2_norm: float = Field(1.0, description="Embedding L2 normu (normalize edilmiş)")
    top_matches: List[CarpetMatch] = Field(default_factory=list, description="En çok benzeyen Top-K referans halılar")
    verdict: str = Field(..., description="Embedding benzerliği ve görsel yakınlık mühendislik yorumu")


class ComprehensiveVisualReport(BaseModel):
    """Yaprak 57 ve 58 Tümleşik Görsel Analiz Raporu."""
    report_id: str = Field(..., description="Rapor tekil kimliği")
    image_path: str = Field(..., description="İncelenen halı görsel dosya yolu")
    color_analysis: ColorAnalysisResult = Field(..., description="K-Means & CIELAB renk analizi")
    symmetry_analysis: SymmetryAnalysisResult = Field(..., description="Yatay/Dikey simetri ve tekrar analizi")
    seam_continuity: SeamContinuityResult = Field(..., description="Kenar dikiş sürekliliği analizi")
    cnn_embedding: CNNEmbeddingResult = Field(..., description="CNN embedding ve Top-K benzerlik")
    synthesis_verdict: str = Field(..., description="Mühendislik sentez ve genel değerlendirme")
    technical_limitations: List[str] = Field(
        default_factory=lambda: [
            "1. Gerçek Üretilebilirlik Kararı Vermez: Jakar armür kartı, atkı/çözgü sıklığı, cağlık bobin limitlerini doğrulamaz.",
            "2. Estetik Kaliteyi Kesin Olarak Ölçmez: Yalnızca renk mesafesi ve matematiksel ayna simetrisini sayısallaştırır.",
            "3. Telif veya Özgünlük Teyidi Sağlamaz: Yüksek CNN benzerliği sadece genel görsel doku yakınlığını ifade eder.",
            "4. Analiz Değerleri Tek Başına 'İyi Tasarım' Anlamına Gelmez: Tasarımın pazar veya dokuma uygunluğu uzman desinatör onayı gerektirir."
        ],
        description="Yaprak 58 ve 60'ta belirtilen 4 temel teknik çalışma sınırı"
    )
    diagnostic_panel_path: Optional[str] = Field(None, description="300 DPI Teşhis paneli görsel dosya yolu")
    execution_time_sec: float = Field(0.0, description="Analiz toplam işlem süresi (saniye)")
