"""Unit tests for Day 02 Data Modeling and Schema Transformation."""

from pathlib import Path
import pytest

from day02.mini_project.src.models import (
    ProductCompositeCatalog,
    ProductTabularRecord,
    VisualAssetMetadata,
)
from day02.mini_project.src.schema_transformer import SchemaTransformer


@pytest.fixture
def transformer() -> SchemaTransformer:
    t = SchemaTransformer()
    p1 = ProductTabularRecord(
        product_id="PRD-101",
        title="Anatolian Classic Medallion",
        collection="Heritage",
        width_cm=160,
        length_cm=230,
        primary_color="Navy Blue",
    )
    p2 = ProductTabularRecord(
        product_id="PRD-102",
        title="Modern Geometrics Minimalist",
        collection="Contemporary",
        width_cm=200,
        length_cm=290,
        primary_color="Anthracite Grey",
    )
    t.add_product(p1)
    t.add_product(p2)

    img1 = VisualAssetMetadata(image_id="IMG-01", file_name="anatolian_top.jpg", angle_or_view="top_down", resolution="1920x1080")
    img2 = VisualAssetMetadata(image_id="IMG-02", file_name="anatolian_pile.jpg", angle_or_view="pile_detail", resolution="1920x1080")
    t.add_asset(img1)
    t.add_asset(img2)

    t.link_product_to_images("PRD-101", ["IMG-01", "IMG-02"])
    return t


def test_referential_integrity_success(transformer: SchemaTransformer):
    is_valid, errors = transformer.validate_referential_integrity()
    assert is_valid is True
    assert len(errors) == 0


def test_referential_integrity_missing_asset(transformer: SchemaTransformer):
    transformer.link_product_to_images("PRD-102", ["NON_EXISTENT_IMG"])
    is_valid, errors = transformer.validate_referential_integrity()
    assert is_valid is False
    assert any("NON_EXISTENT_IMG" in e for e in errors)


def test_build_composite_catalog(transformer: SchemaTransformer, tmp_path: Path):
    comp = transformer.build_composite_catalog("PRD-101")
    assert isinstance(comp, ProductCompositeCatalog)
    assert comp.product_id == "PRD-101"
    assert len(comp.visual_assets) == 2
    assert comp.dimensions["width_cm"] == 160

    out_file = tmp_path / "composite.json"
    transformer.export_all_to_json(out_file)
    assert out_file.exists()
