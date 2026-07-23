"""
day03/mini_project/tests/test_pipeline.py
Çok kaynaklı veri boru hattı, parserlar, normalizer ve karantina mantığı için birim testler.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from day02.mini_project.src.models import CarpetProduct, MaterialEnum
from day03.mini_project.src.normalizer import DataNormalizer
from day03.mini_project.src.parsers import CsvDataSourceParser, JsonDataSourceParser
from day03.mini_project.src.pipeline import DataIngestionPipeline

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_csv_parser_valid():
    csv_file = FIXTURES_DIR / "raw_production_logs.csv"
    parser = CsvDataSourceParser(source_path=csv_file, required_columns=["product_id", "raw_width"])
    records = parser.parse()

    assert len(records) == 10
    assert parser.stats.valid_records_count == 10
    assert parser.stats.malformed_records_count == 0
    assert records[0]["product_id"] == "MRP-1001"
    assert records[0]["dimension_unit"] == "cm"


def test_csv_parser_missing_required_column(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("col_a,col_b\n1,2\n", encoding="utf-8")

    parser = CsvDataSourceParser(source_path=bad_csv, required_columns=["product_id"])
    with pytest.raises(ValueError, match="zorunlu sütunlar eksik"):
        parser.parse()


def test_json_parser_valid():
    json_file = FIXTURES_DIR / "raw_catalog_feed.json"
    parser = JsonDataSourceParser(source_path=json_file)
    records = parser.parse()

    assert len(records) == 10
    assert parser.stats.valid_records_count == 10
    assert records[0]["product_code"] == "MRP-1001"
    assert "palette" in records[0]


def test_normalizer_unit_conversions():
    norm = DataNormalizer()

    # inç -> cm
    assert norm.convert_dimension_to_cm(100.0, "inch") == 254.0
    # cm -> cm
    assert norm.convert_dimension_to_cm(160.0, "cm") == 160.0
    # mm -> cm
    assert norm.convert_dimension_to_cm(1200.0, "mm") == 120.0

    # Hatalı durumlar
    with pytest.raises(ValueError, match="Sayısal olmayan"):
        norm.convert_dimension_to_cm("not_a_number", "cm")

    with pytest.raises(ValueError, match="Desteklenmeyen ölçü birimi"):
        norm.convert_dimension_to_cm(100.0, "light_years")


def test_normalizer_hex_and_materials():
    norm = DataNormalizer()

    # 3 basamaklı hex genişletme (#fff -> #FFFFFF)
    assert norm.normalize_hex_color("#fff") == "#FFFFFF"
    assert norm.normalize_hex_color("2b3a42") == "#2B3A42"

    with pytest.raises(ValueError, match="Geçersiz hex"):
        norm.normalize_hex_color("INVALID_HEX")

    # Türkçe ve esnek malzeme dönüşümleri
    assert norm.normalize_material("yün") == MaterialEnum.WOOL
    assert norm.normalize_material("wool") == MaterialEnum.WOOL
    assert norm.normalize_material("akrilik") == MaterialEnum.ACRYLIC
    assert norm.normalize_material("bambu") == MaterialEnum.BAMBOO_SILK


def test_normalizer_valid_and_quarantine_record():
    norm = DataNormalizer()

    valid_rec = {
        "product_id": "MRP-1001",
        "product_name": "Prestij Klasik",
        "collection": "Prestij",
        "composition": "wool",
        "raw_width": 160.0,
        "raw_length": 230.0,
        "dimension_unit": "cm",
        "pile_height_mm": 11.0,
        "palette": ["#2B3A42", "#4F6D7A"]
    }
    product, err = norm.process_record(valid_rec)
    assert err is None
    assert isinstance(product, CarpetProduct)
    assert product.product_id == "MRP-1001"
    assert product.material == MaterialEnum.WOOL
    assert product.dimensions.width_cm == 160.0

    # Geçersiz kayıt: Negatif genişlik
    bad_rec = dict(valid_rec, raw_width=-100.0)
    product_bad, err_bad = norm.process_record(bad_rec)
    assert product_bad is None
    assert err_bad is not None
    assert "error_message" in err_bad
    assert err_bad["product_id"] == "MRP-1001"


def test_full_pipeline_execution(tmp_path):
    csv_file = FIXTURES_DIR / "raw_production_logs.csv"
    json_file = FIXTURES_DIR / "raw_catalog_feed.json"

    pipeline = DataIngestionPipeline()
    report = pipeline.run(csv_path=csv_file, json_path=json_file, output_dir=tmp_path)

    assert report["status"] == "SUCCESS"
    assert report["total_csv_records"] == 10
    assert report["total_json_records"] == 10
    assert report["valid_products_count"] == 10
    assert report["quarantine_records_count"] == 0
    assert report["data_quality_score_pct"] == 100.0

    # Çıktı dosyalarının kontrolü
    assert (tmp_path / "normalized_products.json").exists()
    assert (tmp_path / "data_quality_report.json").exists()
    assert (tmp_path / "quarantine_records.json").exists()

    saved_products = json.loads((tmp_path / "normalized_products.json").read_text(encoding="utf-8"))
    assert len(saved_products) == 10
    assert saved_products[0]["product_id"] == "MRP-1001"


def test_pipeline_quarantine_handling_with_dirty_records(tmp_path):
    dirty_csv = FIXTURES_DIR / "dirty_records.csv"
    empty_json = tmp_path / "empty_catalog.json"
    empty_json.write_text("[]", encoding="utf-8")

    pipeline = DataIngestionPipeline()
    report = pipeline.run(csv_path=dirty_csv, json_path=empty_json, output_dir=tmp_path)

    # Kirli kayıtların tamamı ya parse anında ya da normalizasyonda karantinaya düşmeli
    assert report["quarantine_records_count"] >= 5
    assert report["valid_products_count"] == 0
    assert report["data_quality_score_pct"] == 0.0

    quarantine = json.loads((tmp_path / "quarantine_records.json").read_text(encoding="utf-8"))
    assert len(quarantine) >= 5
