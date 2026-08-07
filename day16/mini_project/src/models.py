"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
İkili Sınıflandırma ve Lojistik Regresyon Pydantic Veri Modelleri

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from enum import IntEnum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QualityClass(IntEnum):
    """Halı ve iplik üretim kalite sınıfı."""
    STANDARD = 0   # Standart / Kusursuz Üretim
    DEFECTIVE = 1  # Kusurlu / Hatalı Parti


class ConfusionMatrixMetrics(BaseModel):
    """Karar matrisi ve türetilmiş performans metrikleri."""
    tp: int = Field(..., description="True Positive (Doğru Tespit Edilen Kusurlu)")
    fp: int = Field(..., description="False Positive (Yanlış Alarm - Tip I Hata)")
    tn: int = Field(..., description="True Negative (Doğru Kabul Edilen Standart)")
    fn: int = Field(..., description="False Negative (Kaçırılan Kusurlu - Tip II Hata)")
    accuracy: float = Field(..., description="Genel Doğruluk Oranı (Accuracy)")
    precision: float = Field(..., description="Hassasiyet (Pozitif Tahmin Değeri)")
    recall: float = Field(..., description="Duyarlılık / Anma (True Positive Rate - TPR)")
    specificity: float = Field(..., description="Özgüllük (True Negative Rate - TNR)")
    f1_score: float = Field(..., description="Harmonik Ortalama F1-Skoru")
    f2_score: float = Field(..., description="Duyarlılık Ağırlıklı F2-Skoru")


class ThresholdEvaluation(BaseModel):
    """Belirli bir karar eşiğinde hesaplanan metrikler."""
    threshold: float = Field(..., description="Uygulanan karar eşik değeri (tau)")
    precision: float = Field(..., description="Eşikteki hassasiyet")
    recall: float = Field(..., description="Eşikteki duyarlılık (TPR)")
    specificity: float = Field(..., description="Eşikteki özgüllük (1 - FPR)")
    f1_score: float = Field(..., description="Eşikteki F1 skoru")
    f2_score: float = Field(..., description="Eşikteki F2 skoru")
    fpr: float = Field(..., description="Yanlış pozitif oranı (False Positive Rate)")
    tpr: float = Field(..., description="Doğru pozitif oranı (True Positive Rate)")
    cost: float = Field(..., description="Endüstriyel maliyet fonksiyonu değeri")


class ROCAUCMetrics(BaseModel):
    """ROC ve PR eğrileri değerlendirme özeti."""
    roc_auc: float = Field(..., description="ROC Eğrisi Altındaki Alan (AUC)")
    pr_auc: float = Field(..., description="Precision-Recall Eğrisi Altındaki Alan (Average Precision)")
    brier_score: float = Field(..., description="Brier Olasılık Kalibrasyon Skoru")
    optimal_threshold_youden: float = Field(..., description="Youden's J İstatistiğini maksimize eden eşik")
    optimal_threshold_f2: float = Field(..., description="F2 Skorunu maksimize eden eşik")
    optimal_threshold_cost: float = Field(..., description="Toplam kalite maliyetini minimize eden eşik")


class FeatureWeight(BaseModel):
    """Lojistik regresyon öznitelik katsayısı ve odds oranı."""
    feature_name: str = Field(..., description="Öznitelik adı")
    weight: float = Field(..., description="Model katsayısı (beta_j)")
    odds_ratio: float = Field(..., description="Odds Oranı (exp(beta_j))")
    impact_direction: str = Field(..., description="Kusur riskine etkisi (ARTIRICI / AZALTICI)")


class ModelEvaluationSummary(BaseModel):
    """Model varyantı değerlendirme çıktısı."""
    model_type: str = Field(..., description="Model tipi ve yapılandırması")
    threshold: float = Field(..., description="Uygulanan sınıflandırma eşiği")
    metrics: ConfusionMatrixMetrics = Field(..., description="Karar matrisi metrikleri")
    cost: float = Field(..., description="Hesaplanan toplam endüstriyel hata maliyeti")


class BinaryClassificationReport(BaseModel):
    """Day 16 kurumsal ikili sınıflandırma ana raporu."""
    dataset_samples: int = Field(..., description="Toplam örneklem sayısı")
    defect_count: int = Field(..., description="Kusurlu örneklem sayısı")
    defect_ratio: float = Field(..., description="Kusurlu sınıf oranı")
    roc_auc_metrics: ROCAUCMetrics = Field(..., description="Eğri altı alan ve optimal eşik metrikleri")
    baseline_model: ModelEvaluationSummary = Field(..., description="Temel Lojistik Regresyon (tau=0.50, dengesiz)")
    balanced_model: ModelEvaluationSummary = Field(..., description="Dengeli Lojistik Regresyon (class_weight='balanced')")
    tuned_threshold_model: ModelEvaluationSummary = Field(..., description="Optimal Maliyet Eşikli Model")
    feature_weights: List[FeatureWeight] = Field(..., description="Öznitelik önem sıralaması")
