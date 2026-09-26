"""Tests for Day 01 Industrial Observation Catalog and Data Taxonomy."""

import pytest
from pydantic import ValidationError

from day01.mini_project.src.models import DataAsset, DataModality
from day01.mini_project.src.observation_catalog import ObservationCatalog


def test_data_asset_creation():
    """Verify valid DataAsset initialization."""
    asset = DataAsset(
        asset_id="TEST-01",
        name="test_sensor_stream",
        modality=DataModality.NUMERICAL,
        source_type="SyntheticSensor",
        estimated_size_kb=100.0,
        description="Synthetic test stream",
    )
    assert asset.asset_id == "TEST-01"
    assert asset.modality == DataModality.NUMERICAL
    assert asset.estimated_size_kb == 100.0


def test_data_asset_validation_negative_size():
    """Verify validation rejects negative file sizes."""
    with pytest.raises(ValidationError):
        DataAsset(
            asset_id="ERR-01",
            name="invalid_size_asset",
            modality=DataModality.VISUAL,
            source_type="Camera",
            estimated_size_kb=-15.0,
        )


def test_observation_catalog_operations(tmp_path):
    """Verify adding, filtering, and summary statistics of the catalog."""
    catalog = ObservationCatalog("TestCatalog")
    assert len(catalog.list_assets()) == 0

    a1 = DataAsset(
        asset_id="N-1",
        name="telemetry",
        modality=DataModality.NUMERICAL,
        source_type="SimLoom",
        estimated_size_kb=200.0,
    )
    a2 = DataAsset(
        asset_id="V-1",
        name="pattern",
        modality=DataModality.VISUAL,
        source_type="SimCamera",
        estimated_size_kb=1024.0,
    )
    a3 = DataAsset(
        asset_id="T-1",
        name="manual",
        modality=DataModality.TEXTUAL,
        source_type="SimDoc",
        estimated_size_kb=50.0,
    )

    catalog.add_asset(a1)
    catalog.add_asset(a2)
    catalog.add_asset(a3)

    assert len(catalog.list_assets()) == 3
    assert len(catalog.filter_by_modality(DataModality.NUMERICAL)) == 1
    assert len(catalog.filter_by_modality(DataModality.VISUAL)) == 1
    assert len(catalog.filter_by_modality(DataModality.TEXTUAL)) == 1

    summary = catalog.get_summary()
    assert summary["total_assets"] == 3
    assert summary["total_size_kb"] == 1274.0
    assert summary["modality_counts"]["numerical"] == 1
    assert summary["modality_counts"]["visual"] == 1
    assert summary["modality_counts"]["textual"] == 1

    # Test export
    out_file = tmp_path / "catalog.json"
    exported = catalog.export_json(out_file)
    assert exported.exists()
    assert '"total_assets": 3' in out_file.read_text(encoding="utf-8")


def test_catalog_duplicate_prevention():
    """Verify duplicate asset IDs are rejected."""
    catalog = ObservationCatalog("DupCheck")
    a = DataAsset(
        asset_id="DUP-1",
        name="first",
        modality=DataModality.NUMERICAL,
        source_type="Test",
        estimated_size_kb=10.0,
    )
    catalog.add_asset(a)
    with pytest.raises(ValueError, match="already exists"):
        catalog.add_asset(a)


def test_create_sample_catalog():
    """Verify sample catalog loads all 3 modalities."""
    cat = ObservationCatalog.create_sample_catalog()
    assert len(cat.list_assets()) == 6
    summary = cat.get_summary()
    assert summary["modality_counts"]["numerical"] == 2
    assert summary["modality_counts"]["visual"] == 2
    assert summary["modality_counts"]["textual"] == 2
