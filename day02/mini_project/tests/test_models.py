"""
day02/mini_project/tests/test_models.py
Endüstriyel Pydantic modellerinin doğrulama, sınır ve hata senaryoları testleri.
"""

import pytest
from pydantic import ValidationError

from day02.mini_project.src.models import (
    CarpetDimensions,
    CarpetProduct,
    ColorSpaceEnum,
    IndustrialImageMetadata,
    InferenceRequest,
    InferenceResponse,
    InvalidDimensionsError,
    MaterialEnum,
    TechnicalDocument,
)
from day02.mini_project.src.serializer import create_sample_models, export_json_schemas


def test_valid_image_metadata():
    meta = IndustrialImageMetadata(
        image_id="IMG-TEST-001",
        width_px=1920,
        height_px=1080,
        channels=3,
        color_space=ColorSpaceEnum.RGB,
        dpi=300,
        knot_density=50
    )
    assert meta.width_px == 1920
    assert meta.aspect_ratio == round(1920 / 1080, 4)
    assert meta.total_megapixels == 2.07


def test_invalid_image_metadata_channels_and_resolution():
    # Geçersiz kanal sayısı (2 kanal olamaz)
    with pytest.raises(ValidationError) as exc_info:
        IndustrialImageMetadata(
            image_id="IMG-ERR",
            width_px=1000,
            height_px=1000,
            channels=2
        )
    assert "Desteklenmeyen kanal sayısı" in str(exc_info.value)

    # Geçersiz çözünürlük (alt sınır ihlali: < 64px)
    with pytest.raises(ValidationError):
        IndustrialImageMetadata(
            image_id="IMG-ERR2",
            width_px=32,
            height_px=1000
        )


def test_carpet_dimensions_and_aspect_sanity():
    # Geçerli boyutlar
    dims = CarpetDimensions(width_cm=160.0, length_cm=230.0, pile_height_mm=10.0)
    assert dims.area_square_meters == 3.68

    # Aşırı en-boy oranı (1:11 oranı dokuma tezgahı kısıtını aşar)
    with pytest.raises(InvalidDimensionsError):
        CarpetDimensions(width_cm=100.0, length_cm=1100.0, pile_height_mm=10.0)


def test_valid_carpet_product():
    dims = CarpetDimensions(width_cm=200.0, length_cm=290.0)
    prod = CarpetProduct(
        product_id="MRP-894721",
        title="Modern Geometrik İskandinav Halı",
        collection="Nordic Pure",
        material=MaterialEnum.ACRYLIC,
        dimensions=dims,
        palette_hex=["#FFFFFF", "#000000", "#7D7D7D"],
        is_active=True
    )
    assert prod.product_id == "MRP-894721"
    assert len(prod.palette_hex) == 3


def test_invalid_carpet_product_id_and_hex_palette():
    dims = CarpetDimensions(width_cm=200.0, length_cm=200.0)

    # Geçersiz ürün kodu formatı
    with pytest.raises(ValidationError) as exc:
        CarpetProduct(
            product_id="INVALID-123",
            title="Hatalı Kodlu Halı",
            collection="Col",
            material=MaterialEnum.WOOL,
            dimensions=dims,
            palette_hex=["#FFFFFF"]
        )
    assert "Geçersiz ürün kodu" in str(exc.value)

    # Geçersiz hex renk kodu
    with pytest.raises(ValidationError) as exc_hex:
        CarpetProduct(
            product_id="MRP-12345",
            title="Hatalı Renkli Halı",
            collection="Col",
            material=MaterialEnum.WOOL,
            dimensions=dims,
            palette_hex=["#FFF", "MaviRenk", "#123456"]
        )
    assert "Geçersiz hex renk kodu" in str(exc_hex.value)


def test_technical_document_immutability():
    doc = TechnicalDocument(
        doc_id="DOC-001",
        title="Hereke Düğüm Standartları",
        section="1.1 Düğüm Yapısı",
        content="Hereke tipi halılarda çift düğüm (Gördes düğümü) tekniği esastır.",
        tags=["hereke", "gordes"]
    )
    assert doc.doc_id == "DOC-001"
    
    # Frozen model değiştirilemez
    with pytest.raises(ValidationError):
        doc.title = "Yeni Başlık"


def test_inference_request_validation():
    # Geçerli istek
    req = InferenceRequest(
        request_id="REQ-001",
        prompt="traditional usak carpet pattern",
        steps=30,
        lora_weight=0.8
    )
    assert req.steps == 30

    # Adım sayısı alt sınır ihlali (< 10)
    with pytest.raises(ValidationError):
        InferenceRequest(
            request_id="REQ-002",
            prompt="pattern",
            steps=5
        )

    # LoRA ağırlığı sınır ihlali (> 1.0)
    with pytest.raises(ValidationError):
        InferenceRequest(
            request_id="REQ-003",
            prompt="pattern",
            lora_weight=1.5
        )


def test_sample_models_and_json_schemas():
    samples = create_sample_models()
    assert "image_metadata" in samples
    assert "carpet_product" in samples
    assert "inference_request" in samples

    schemas = export_json_schemas()
    assert "IndustrialImageMetadata" in schemas
    assert "CarpetProduct" in schemas
    assert "InferenceRequest" in schemas
