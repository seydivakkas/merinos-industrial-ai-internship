# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
Domain Models: Yapılandırılmış Halı Brifi, İstem Montajı ve Tümleşik Analiz Raporu
Staj Defteri Yaprak 59 ve 60 ile %100 Uyumlu.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class SymmetryMode(str, Enum):
    """Halı simetri ekseni seçenekleri."""
    BILATERAL = "BILATERAL"                            # Yalnızca dikey ayna (sol-sağ)
    VERTICAL = "VERTICAL"                              # Yalnızca yatay ayna (üst-alt)
    BILATERAL_AND_VERTICAL = "BILATERAL_AND_VERTICAL"    # Çift yönlü 4-çeyrek simetri (Klasik saray halısı)
    RADIAL = "RADIAL"                                  # Merkezi dairesel simetri
    ASYMMETRIC = "ASYMMETRIC"                          # Asimetrik serbest modern tasarım


class CarpetDesignInput(BaseModel):
    """
    Kullanıcıdan ve desinatörden alınan yapılandırılmış tasarım brif modeli.
    Staj Defteri Yaprak 59: Stil, motif, renk, kompozisyon, bordür ve simetri alanlarını içerir.
    Zorunlu alanlar: style, motif, primary_color.
    İsteğe bağlı alanlar: secondary_color, composition, border_type.
    """
    brief_id: str = Field(default="BRF-001", description="Tasarım brif kimliği")
    title: str = Field(default="Merinos Özel Tasarım Halı", description="Tasarım proje başlığı")
    style: str = Field(..., min_length=2, description="Tasarım stili (Örn: Klasik Osmanlı, Modern Minimalist, İskandinav)")
    motif: str = Field(..., min_length=2, description="Ana motif öğesi (Örn: Barok Madalyon, Geometrik Prizma, Rumi Dalları)")
    primary_color: str = Field(..., min_length=2, description="Ana zemin rengi (Örn: Krem, Lacivert, Taş Grisi)")
    secondary_color: Optional[str] = Field(default="", description="İkincil / vurgulu desen rengi (İsteğe bağlı)")
    composition: Optional[str] = Field(default="", description="Yerleşim kompozisyonu (İsteğe bağlı)")
    border_type: Optional[str] = Field(default="", description="Bordür çerçeve cinsi (İsteğe bağlı)")
    symmetry_mode: SymmetryMode = Field(default=SymmetryMode.BILATERAL_AND_VERTICAL, description="Simetri modu")
    seed: int = Field(default=42, ge=0, description="Deterministik desen tohum değeri")

    @field_validator("style", "motif", "primary_color")
    @classmethod
    def validate_non_empty_required_fields(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Bu alan zorunludur ve boş bırakılamaz.")
        return v.strip()


class PromptAssemblyResult(BaseModel):
    """
    Yaprak 59: Alanların sabit sırada birleştirilmesi ve boş bırakılan alanların elenmesi sonucu.
    """
    assembled_prompt: str = Field(description="Sabit sırada birleştirilmiş SDXL prompt metni")
    negative_prompt: str = Field(description="İstenmeyen doku ve artefaktları engelleyen negatif prompt")
    included_fields: Dict[str, str] = Field(default_factory=dict, description="Prompt'a dahil edilen dolu alanlar")
    omitted_fields: List[str] = Field(default_factory=list, description="Boş bırakıldığı için prompt'a katılmayan alanlar")


class TechnicalLimitationsReport(BaseModel):
    """
    Staj Defteri Yaprak 60: Çalışmanın 4 Temel Teknik Sınırının Analizi.
    """
    manufacturability: Dict[str, Any] = Field(
        description="Sınır 1: Gerçek üretilebilirlik kararı vermemesi (iplik sıklığı, tarak-atkı sınırını bilmeme)"
    )
    aesthetic_subjectivity: Dict[str, Any] = Field(
        description="Sınır 2: Estetik kalitenin kesin ölçülememesi (insan beğenisinin sübjektifliği)"
    )
    copyright_originality: Dict[str, Any] = Field(
        description="Sınır 3: Telif veya özgünlük değerlendirmesi yapmaması (geleneksel motif koruması)"
    )
    metric_independence: Dict[str, Any] = Field(
        description="Sınır 4: Analiz metriklerinin tek başına başarılı tasarım anlamına gelmemesi"
    )
    summary_verdict: str = Field(description="Teknik değerlendirme özeti")


class IntegratedPipelineOutput(BaseModel):
    """
    Staj Defteri Yaprak 59 & 60: Tümleşik Boru Hattı Nihai Çıktı Modeli.
    Görüntü üretimi + renk analizi + simetri + seam + benzerlik arama tek bir pakette toplanır.
    """
    brief: CarpetDesignInput
    prompt_result: PromptAssemblyResult
    generated_image_path: str
    color_analysis: Dict[str, Any] = Field(description="K-Means renk kümeleme ve CIEDE2000 bobin eşleşmeleri")
    symmetry_analysis: Dict[str, Any] = Field(description="Yatay, dikey simetri skorları ve periyodik tekrar")
    seam_analysis: Dict[str, Any] = Field(description="Kenar sürekliliği ve dikiş sıçrama gradyanı")
    similar_carpets: List[Dict[str, Any]] = Field(description="CNN embedding ile bulunan Top-K benzer referanslar")
    limitations_report: TechnicalLimitationsReport
    execution_time_ms: Dict[str, float] = Field(default_factory=dict, description="Adım adım çalışma süreleri")
    total_latency_ms: float = Field(default=0.0, description="Toplam uçtan uca gecikme")
    success: bool = Field(default=True)


# Şekil 59 İsim Uyumluluğu
CarpetDesign = CarpetDesignInput


class GenerationConfig(BaseModel):
    """SDXL generation configuration model (Şekil 59)."""
    model: str = Field(default="sdxl")
    steps: int = Field(default=30)
    guidance_scale: float = Field(default=7.5)
