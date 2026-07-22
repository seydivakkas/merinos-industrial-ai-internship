"""
day02/mini_project/src/serializer.py
Pydantic modellerini JSON'a serileştirme ve JSON Schema dışa aktarma araçları.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from day02.mini_project.src.models import (
    CarpetDimensions,
    CarpetProduct,
    ColorSpaceEnum,
    IndustrialImageMetadata,
    InferenceRequest,
    InferenceResponse,
    MaterialEnum,
    TechnicalDocument,
)


def create_sample_models() -> Dict[str, Any]:
    """Geçerli endüstriyel örnek veri modelleri üretir."""
    img_meta = IndustrialImageMetadata(
        image_id="IMG-USAK-001",
        width_px=1024,
        height_px=1536,
        channels=3,
        color_space=ColorSpaceEnum.RGB,
        dpi=300,
        knot_density=60
    )

    dimensions = CarpetDimensions(
        width_cm=200.0,
        length_cm=300.0,
        pile_height_mm=12.0
    )

    product = CarpetProduct(
        product_id="MRP-202601",
        title="Geleneksel Uşak Madalyonlu Halı",
        collection="Anatolia Heritage",
        material=MaterialEnum.WOOL,
        dimensions=dimensions,
        palette_hex=["#8B0000", "#1E3F66", "#D4AF37", "#F5F5DC", "#2E8B57"],
        knot_count_total=360000,
        is_active=True,
        tags=["vintage", "madalyon", "usak", "el-dokuma-hissi"]
    )

    doc = TechnicalDocument(
        doc_id="DOC-STAND-042",
        title="Merinos Yün İplik Dokuma Standartları Şartnamesi",
        section="4.2 Hav Yüksekliği ve Düğüm Toleransları",
        content="Yün halı üretiminde 10 cm başına düşen düğüm sayısı en az 50x50 olmalıdır. Jakarlı dokuma tezgahlarında hav yüksekliği toleransı ±1.5 mm olarak belirlenmiştir.",
        tags=["kalite", "jakar", "tolerans", "yun"],
        author="Tekstil Ar-Ge ve Kalite Kontrol Müdürlüğü"
    )

    infer_req = InferenceRequest(
        request_id="REQ-GEN-8910",
        prompt="traditional Usak carpet motif, central ornamental medallion, symmetrical border, high knot density, 2d vector texture",
        negative_prompt="blurry, distorted, 3d furniture shadows, human, folds",
        lora_weight=0.75,
        steps=35,
        guidance_scale=7.5,
        seed=42,
        target_palette_size=8,
        enable_seamless=True
    )

    infer_res = InferenceResponse(
        request_id="REQ-GEN-8910",
        status="SUCCESS",
        execution_time_ms=1420.5,
        output_image_uri="shared/artifacts/generated_patterns/REQ-GEN-8910.png",
        extracted_palette_hex=["#8B0000", "#1E3F66", "#D4AF37", "#F5F5DC"],
        error_message=None
    )

    return {
        "image_metadata": img_meta.model_dump(),
        "carpet_product": product.model_dump(),
        "technical_document": doc.model_dump(mode="json"),
        "inference_request": infer_req.model_dump(),
        "inference_response": infer_res.model_dump()
    }


def export_json_schemas() -> Dict[str, Any]:
    """Tüm Pydantic modellerinin OpenAPI / JSON Schema tanımlarını üretir."""
    return {
        "IndustrialImageMetadata": IndustrialImageMetadata.model_json_schema(),
        "CarpetDimensions": CarpetDimensions.model_json_schema(),
        "CarpetProduct": CarpetProduct.model_json_schema(),
        "TechnicalDocument": TechnicalDocument.model_json_schema(),
        "InferenceRequest": InferenceRequest.model_json_schema(),
        "InferenceResponse": InferenceResponse.model_json_schema()
    }


def save_outputs(output_dir: Path) -> None:
    """Örnek verileri ve şemaları JSON olarak kaydeder."""
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = create_sample_models()
    with open(output_dir / "sample_models.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    schemas = export_json_schemas()
    with open(output_dir / "schemas.json", "w", encoding="utf-8") as f:
        json.dump(schemas, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "outputs"
    save_outputs(out_dir)
    print(f"Sample modeller ve JSON şemaları kaydedildi: {out_dir}")
