"""
Merinos Industrial AI Internship - Day 28
Data Models for Controlled Carpet Image Generation & Comparative Analysis.
Staj Defteri Yaprak 55 ve 56 Müfredatına Dayalı Veri Modelleri.
Copyright (c) 2026 Seydi Eryilmaz (@seydivakkas). All Rights Reserved.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ExperimentType(str, Enum):
    """Deney türü sınıflandırması (Yaprak 55 & 56)."""
    SEED_VARIATION = "SEED_VARIATION"                     # Yaprak 55: Sabit prompt, farklı seed'ler
    SINGLE_VARIABLE_MUTATION = "SINGLE_VARIABLE_MUTATION" # Yaprak 56: Sabit seed, tek bir alanın değişimi


class StructuredDesignBrief(BaseModel):
    """
    Kullanıcı tasarım isteğinin 6 temel alana ayrılmış Pydantic v2 modeli.
    Staj Defteri Yaprak 55 uyarınca: Stil, Motif, Renk, Kompozisyon, Bordür, Simetri.
    """
    brief_id: str = Field(default="BRF-01", description="Brif kimlik kodu")
    title: str = Field(default="Özel Halı Tasarımı", description="Tasarım proje başlığı")
    style: str = Field(..., min_length=2, description="Tasarım stili (Örn: Klasik Osmanlı Saray, İskandinav)")
    motif: str = Field(..., min_length=2, description="Temel bezeme öğesi (Örn: Barok Madalyon, Rumi)")
    color: str = Field(..., min_length=2, description="Baskın renk tanımları (Örn: Krem Fildişi ve Koyu Bordo)")
    composition: Optional[str] = Field(default="", description="Motiflerin yerleşimi (Örn: Merkezi madalyon)")
    border: Optional[str] = Field(default="", description="Kenar çerçevesi (Örn: Geniş su yolu bordürü)")
    symmetry: Optional[str] = Field(default="", description="Simetri beklentisi (Örn: Çift yönlü 4-çeyrek simetri)")
    seed: int = Field(default=42, ge=0, description="Rastgele gürültü tohum değeri")
    steps: int = Field(default=30, ge=5, le=100, description="Difüzyon çıkarım adım sayısı")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="CFG yönlendirme ölçeği")
    scheduler: str = Field(default="EulerDiscreteScheduler", description="Difüzyon gürültü çözücü algoritması")

    @field_validator("style", "motif", "color")
    @classmethod
    def validate_required_strings(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Bu alan boş bırakılamaz; geçerli bir metin zorunludur.")
        return v.strip()


class PromptAssemblyResult(BaseModel):
    """
    Alanların sabit sırada birleştirilmesiyle oluşturulan prompt sonucu.
    Staj Defteri Yaprak 55: Sabit sırayla birleştirme.
    """
    assembled_prompt: str = Field(description="SDXL modeline gönderilecek tam metin")
    negative_prompt: str = Field(description="Negatif filtreleme istemi")
    field_order: List[str] = Field(description="Birleştirilen alanların sıralı listesi")
    omitted_fields: List[str] = Field(default_factory=list, description="Boş bırakıldığı için eklenmeyen alanlar")
    brief_id: str


class ExperimentRunRecord(BaseModel):
    """
    Tek bir çıkarım çalıştırmasının tekrarlanabilirlik kaydı.
    Staj Defteri Yaprak 56: Prompt, seed, model, scheduler ve adımların loglanması.
    """
    run_id: str
    brief_id: str
    seed: int
    prompt_assembled: str
    negative_prompt: str
    image_path: str
    execution_time_sec: float
    model_name: str
    scheduler: str
    steps: int
    guidance_scale: float
    timestamp: str
    mutated_field: Optional[str] = None
    mutated_value: Optional[str] = None


class ComparisonResult(BaseModel):
    """
    Karşılaştırmalı deney çıktısı (Yaprak 55 veya Yaprak 56).
    """
    experiment_id: str
    experiment_type: ExperimentType
    base_brief: StructuredDesignBrief
    runs: List[ExperimentRunRecord]
    panel_image_path: Optional[str] = None
    findings: List[str] = Field(default_factory=list)


class ReproducibilityVerificationResult(BaseModel):
    """
    Aynı seed ve prompt ile iki bağımsız çalıştırmanın piksel düzeyinde denkliği (MSE = 0).
    """
    seed: int
    run_1_id: str
    run_2_id: str
    pixel_mse: float
    is_identical: bool
    verdict: str
