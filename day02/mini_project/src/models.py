"""
day02/mini_project/src/models.py
Endüstriyel Yapay Zeka platformu için Pydantic v2 veri modelleri.
Görsel metadata, halı ürün bilgisi, teknik doküman ve çıkarım istek/yanıt şemaları.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ModelValidationError(Exception):
    """Genel endüstriyel model doğrulama hatası."""
    pass


class InvalidDimensionsError(ModelValidationError):
    """Fiziksel boyut kısıtları ihlal edildiğinde fırlatılır."""
    pass


class ColorSpaceEnum(str, Enum):
    RGB = "RGB"
    BGR = "BGR"
    HSV = "HSV"
    LAB = "LAB"
    GRAY = "GRAY"


class MaterialEnum(str, Enum):
    WOOL = "wool"
    SILK = "silk"
    ACRYLIC = "acrylic"
    POLYESTER = "polyester"
    COTTON = "cotton"
    BAMBOO_SILK = "bamboo_silk"


class IndustrialImageMetadata(BaseModel):
    """
    Kamera, tarayıcı veya CAD kaynaklı endüstriyel halı görseli metadata modeli.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    image_id: str = Field(..., min_length=3, max_length=64, description="Benzersiz görsel kimliği")
    width_px: int = Field(..., ge=64, le=8192, description="Piksel cinsinden genişlik")
    height_px: int = Field(..., ge=64, le=8192, description="Piksel cinsinden yükseklik")
    channels: int = Field(default=3, description="Kanal sayısı (1: Grayscale, 3: RGB/LAB, 4: RGBA)")
    color_space: ColorSpaceEnum = Field(default=ColorSpaceEnum.RGB, description="Görselin renk uzayı")
    dpi: int = Field(default=300, ge=72, le=2400, description="Baskı/tarama çözünürlüğü (DPI)")
    knot_density: Optional[int] = Field(None, ge=10, le=120, description="10 cm başına düşen düğüm sıklığı")

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: int) -> int:
        if v not in (1, 3, 4):
            raise ValueError(f"Desteklenmeyen kanal sayısı: {v}. Yalnızca 1, 3 veya 4 olabilir.")
        return v

    @property
    def aspect_ratio(self) -> float:
        """Genişlik/Yükseklik en-boy oranı."""
        return round(self.width_px / self.height_px, 4)

    @property
    def total_megapixels(self) -> float:
        """Toplam piksel çözünürlüğü (Milyon piksel)."""
        return round((self.width_px * self.height_px) / 1_000_000, 2)


class CarpetDimensions(BaseModel):
    """
    Halı ürününün fiziksel üretim ölçüleri.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    width_cm: float = Field(..., ge=20.0, le=1500.0, description="Genişlik (cm)")
    length_cm: float = Field(..., ge=20.0, le=1500.0, description="Uzunluk (cm)")
    pile_height_mm: float = Field(default=10.0, ge=1.0, le=50.0, description="Hav yüksekliği (mm)")

    @model_validator(mode="after")
    def validate_aspect_sanity(self) -> CarpetDimensions:
        # En ve boy oranı fiziksel dokuma tezgahı toleranslarını aşmamalıdır (maks 1:10 oranı)
        ratio = max(self.width_cm, self.length_cm) / min(self.width_cm, self.length_cm)
        if ratio > 10.0:
            raise InvalidDimensionsError(
                f"Fiziksel boyut oranı tezgah kısıtını aşıyor ({ratio:.1f}:1). Maksimum izin verilen oran 10:1'dir."
            )
        return self

    @property
    def area_square_meters(self) -> float:
        """Metrekare cinsinden toplam alan."""
        return round((self.width_cm * self.length_cm) / 10_000.0, 3)


class CarpetProduct(BaseModel):
    """
    Katalog, ERP ve üretim hattı için kanonik halı ürün modeli.
    """
    model_config = ConfigDict(validate_assignment=True)

    product_id: str = Field(..., description="Ürün kodu (Örn: MRP-104928)")
    title: str = Field(..., min_length=3, max_length=150, description="Ürün ticari başlığı")
    collection: str = Field(..., min_length=2, max_length=50, description="Koleksiyon adı")
    material: MaterialEnum = Field(..., description="Ana iplik materyali")
    dimensions: CarpetDimensions = Field(..., description="Fiziksel boyutlar")
    palette_hex: List[str] = Field(..., min_length=1, max_length=16, description="Hedef iplik paleti (Hex)")
    knot_count_total: Optional[int] = Field(None, ge=1000, description="Tahmini toplam düğüm adedi")
    is_active: bool = Field(default=True, description="Üretim durumu aktif mi?")
    tags: List[str] = Field(default_factory=list, description="Stil ve arama etiketleri")

    @field_validator("product_id")
    @classmethod
    def validate_product_id_format(cls, v: str) -> str:
        pattern = r"^MRP-\d{4,8}$"
        if not re.match(pattern, v):
            raise ValueError(f"Geçersiz ürün kodu: '{v}'. Format 'MRP-XXXXXX' biçiminde olmalıdır.")
        return v

    @field_validator("palette_hex")
    @classmethod
    def validate_hex_colors(cls, v: List[str]) -> List[str]:
        hex_pattern = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
        cleaned = []
        for color in v:
            c = color.strip()
            if not re.match(hex_pattern, c):
                raise ValueError(f"Geçersiz hex renk kodu: '{color}'. Örnek: '#FFFFFF' veya '#E5A93B'")
            cleaned.append(c.upper())
        return cleaned


class TechnicalDocument(BaseModel):
    """
    RAG sistemi için teknik tekstil şartnamesi veya kalite dokümanı chunk modeli.
    """
    model_config = ConfigDict(frozen=True)

    doc_id: str = Field(..., min_length=3, max_length=64, description="Doküman/Chunk kimliği (Örn: DOC-TEX-001)")
    title: str = Field(..., min_length=5, max_length=200, description="Doküman başlığı")
    section: str = Field(..., min_length=2, max_length=100, description="Bölüm başlığı")
    content: str = Field(..., min_length=10, max_length=10000, description="Metinsel içerik")
    tags: List[str] = Field(default_factory=list, description="Kategori etiketleri")
    author: str = Field(default="Sistem Mühendisliği", description="Dokümanı hazırlayan birim")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Oluşturulma zamanı")


class InferenceRequest(BaseModel):
    """
    Üretken AI desen üretim motoru için tip denetimli servis istek modeli.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., min_length=4, max_length=64, description="İstek takip kimliği")
    prompt: str = Field(..., min_length=5, max_length=1000, description="Pozitif tasarım yönlendirmesi")
    negative_prompt: Optional[str] = Field(
        default="blurry, distorted, low resolution, 3d shadows, folds, wrinkles",
        max_length=1000,
        description="Negatif prompt"
    )
    lora_weight: float = Field(default=0.75, ge=0.0, le=1.0, description="Tekstil LoRA adaptör ağırlığı")
    steps: int = Field(default=35, ge=10, le=100, description="Difüzyon çıkarım adım sayısı")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Classifier-Free Guidance (CFG) ölçeği")
    seed: int = Field(default=42, ge=0, le=2**32 - 1, description="Deterministik rastgelelik çekirdeği")
    target_palette_size: int = Field(default=8, ge=2, le=16, description="Dokuma tezgahı iplik bobin sayısı")
    enable_seamless: bool = Field(default=False, description="Dikişsiz desen için dairesel dolgu (circular padding)")


class InferenceResponse(BaseModel):
    """
    Desen üretim hattının istemciye döndürdüğü yapısal yanıt modeli.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., description="İstek takip kimliği")
    status: str = Field(..., description="Görev durumu (SUCCESS, FAILED, PROCESSING)")
    execution_time_ms: Optional[float] = Field(None, ge=0.0, description="Toplam işlem süresi (ms)")
    output_image_uri: Optional[str] = Field(None, description="Üretilen görselin depolama yolu/URI")
    extracted_palette_hex: List[str] = Field(default_factory=list, description="Kuantize edilmiş iplik paleti")
    error_message: Optional[str] = Field(None, description="Hata detayı")


class StructureType(str, Enum):
    """Categorization of data structures."""
    STRUCTURED_TABULAR = "structured_tabular"
    SEMI_STRUCTURED_JSON = "semi_structured_json"
    UNSTRUCTURED_MEDIA = "unstructured_media"


class ProductTabularRecord(BaseModel):
    """Represents a flat structured row in an industrial carpet catalog (CSV)."""
    product_id: str = Field(..., description="Unique product SKU")
    title: str = Field(..., description="Commercial carpet design name")
    collection: str = Field(..., description="Collection/Line name")
    width_cm: int = Field(..., gt=0, description="Carpet width in cm")
    length_cm: int = Field(..., gt=0, description="Carpet length in cm")
    primary_color: str = Field(..., description="Primary weave color code/name")


class VisualAssetMetadata(BaseModel):
    """Metadata for an unstructured carpet photograph or technical drawing."""
    image_id: str = Field(..., description="Unique image identifier")
    file_name: str = Field(..., description="File name on disk")
    angle_or_view: str = Field(..., description="View type (e.g. top_down, pile_detail, border)")
    resolution: str = Field(..., description="Resolution string (e.g. 1920x1080)")


class ProductVisualRelationship(BaseModel):
    """Relational mapping linking a product to its one or more visual assets."""
    product_id: str
    image_ids: List[str] = Field(default_factory=list)


class ProductCompositeCatalog(BaseModel):
    """Semi-structured hierarchical document representation (JSON)."""
    product_id: str
    title: str
    collection: str
    dimensions: Dict[str, int]
    primary_color: str
    visual_assets: List[VisualAssetMetadata] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

