"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Kusur Sınıflandırması Pydantic Veri Modelleri

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from enum import IntEnum
from typing import Dict, List
from pydantic import BaseModel, Field


class DefectClass(IntEnum):
    """Merinos endüstriyel halı ve iplik kusur kategorileri."""
    YARN_BREAKAGE = 0           # İplik Kopması (Çözgü/Atkı Kopuşu)
    OIL_STAIN = 1               # Yağ Lekesi (Mekanik Rulman Sızıntısı)
    JACQUARD_PATTERN_SHIFT = 2  # Jakar Desen Kayması (Senkronizasyon Hatası)
    BORDER_SEWING_DEFECT = 3    # Kenar Dikiş / Overlok Hatası


class PerClassMetrics(BaseModel):
    """Sınıf bazlı duyarlılık, hassasiyet ve F1 başarım metrikleri."""
    class_id: int = Field(..., description="Sınıf nümerik kimliği")
    class_name: str = Field(..., description="Sınıf adı")
    tp: int = Field(..., description="Doğru pozitif sayısı")
    fp: int = Field(..., description="Yanlış pozitif sayısı")
    fn: int = Field(..., description="Yanlış negatif sayısı")
    precision: float = Field(..., description="Sınıf hassasiyeti (Precision)")
    recall: float = Field(..., description="Sınıf duyarlılığı (Recall / Sensitivity)")
    f1_score: float = Field(..., description="Sınıf F1-Skoru")
    support: int = Field(..., description="Test kümesindeki gerçek örneklem sayısı")


class MulticlassMetrics(BaseModel):
    """Çok sınıflı genel ve ortalama model performans metrikleri."""
    accuracy: float = Field(..., description="Genel Doğruluk Oranı (Accuracy)")
    macro_precision: float = Field(..., description="Sınıflara eşit ağırlıklı Makro Hassasiyet")
    macro_recall: float = Field(..., description="Sınıflara eşit ağırlıklı Makro Duyarlılık")
    macro_f1: float = Field(..., description="Sınıflara eşit ağırlıklı Makro F1-Skoru")
    micro_f1: float = Field(..., description="Global TP/FP/FN üzerinden Mikro F1-Skoru")
    weighted_f1: float = Field(..., description="Sınıf frekanslarıyla ağırlıklandırılmış F1-Skoru")
    cohen_kappa: float = Field(..., description="Şans faktöründen arındırılmış Cohen Kappa katsayısı")
    log_loss: float = Field(..., description="Çok sınıflı çapraz entropi (Categorical Cross-Entropy)")
    roc_auc_ovr_macro: float = Field(..., description="One-vs-Rest çok sınıflı Makro ROC-AUC")


class ModelComparisonSummary(BaseModel):
    """Tekil model mimarisinin (Multinomial Softmax veya OvR) performans özeti."""
    strategy_name: str = Field(..., description="Strateji adı (Multinomial Softmax veya One-vs-Rest)")
    training_time_ms: float = Field(..., description="Eğitim süresi (milisaniye)")
    inference_latency_ms: float = Field(..., description="Tekil örneklem çıkarım gecikmesi (ms)")
    throughput_fps: float = Field(..., description="Saniyedeki çıkarım kapasitesi (Samples/sec)")
    metrics: MulticlassMetrics = Field(..., description="Çok sınıflı başarım metrikleri")
    per_class: List[PerClassMetrics] = Field(..., description="4 sınıf için ayrıntılı karneler")


class ClassTopFeatures(BaseModel):
    """Bir sınıf için en ayırt edici katsayılar (Feature Importance)."""
    class_name: str = Field(..., description="Kusur sınıfı adı")
    top_positive_features: List[Dict[str, float]] = Field(..., description="Riski en çok artıran öznitelikler")
    top_negative_features: List[Dict[str, float]] = Field(..., description="Riski en çok azaltan öznitelikler")


class MulticlassEvaluationReport(BaseModel):
    """Day 17 kurumsal çok sınıflı karşılaştırmalı master raporu."""
    dataset_samples: int = Field(..., description="Toplam değerlendirilen test örneklem sayısı")
    class_distribution: Dict[str, int] = Field(..., description="Test kümesindeki sınıf dağılımı")
    multinomial_model: ModelComparisonSummary = Field(..., description="Softmax Multinomial Lojistik Regresyon")
    ovr_model: ModelComparisonSummary = Field(..., description="One-vs-Rest (OvR) Lojistik Regresyon")
    feature_importance: List[ClassTopFeatures] = Field(..., description="Sınıf bazlı öznitelik ağırlıkları")


class MulticlassPredictionResult(BaseModel):
    """Canlı partide yapılan çok sınıflı tahmin çıktısı."""
    predicted_class_id: int = Field(..., description="Tahmin edilen sınıf kimliği")
    predicted_class_name: str = Field(..., description="Tahmin edilen sınıf adı")
    confidence: float = Field(..., description="En yüksek sınıf olasılığı (Güven Skoru)")
    probabilities: Dict[str, float] = Field(..., description="Her 4 sınıf için öngörülen olasılıklar")
