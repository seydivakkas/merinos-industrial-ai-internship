"""Unit tests for Day 01 Environment Profiler and Data Asset Taxonomy."""

import json
from pathlib import Path
import pytest

from day04.mini_project.src.models import (
    DataAsset,
    DataModality,
    SystemResourceRequirements,
)
from day04.mini_project.src.environment_profiler import EnvironmentProfiler


@pytest.fixture
def requirements() -> SystemResourceRequirements:
    return SystemResourceRequirements(
        min_cpu_cores=1,
        min_ram_gb=1.0,
        required_python_version="3.10",
        supported_modalities=[
            DataModality.NUMERICAL,
            DataModality.VISUAL,
            DataModality.TEXTUAL,
        ],
    )


@pytest.fixture
def profiler(requirements: SystemResourceRequirements) -> EnvironmentProfiler:
    return EnvironmentProfiler(requirements)


def test_workstation_audit(profiler: EnvironmentProfiler):
    """Verifies that workstation resources are audited correctly."""
    result = profiler.audit_workstation()
    assert result.cpu_cores >= 1
    assert result.ram_gb > 0.0
    assert result.is_compliant is True
    assert len(result.modalities_supported) == 3


def test_data_asset_registration_and_distribution(profiler: EnvironmentProfiler, tmp_path: Path):
    """Verifies data asset classification across numerical, visual, and textual modalities."""
    a1 = DataAsset(
        asset_id="ASSET-NUM-01",
        name="Loom Telemetry Log",
        modality=DataModality.NUMERICAL,
        source_type="LoomSensor",
        estimated_size_kb=150.0,
    )
    a2 = DataAsset(
        asset_id="ASSET-VIS-01",
        name="Carpet Surface Sample",
        modality=DataModality.VISUAL,
        source_type="InspectionCamera",
        estimated_size_kb=2400.0,
    )
    a3 = DataAsset(
        asset_id="ASSET-TXT-01",
        name="Weaving Machine Manual",
        modality=DataModality.TEXTUAL,
        source_type="TechManual",
        estimated_size_kb=512.0,
    )

    profiler.register_asset(a1)
    profiler.register_asset(a2)
    profiler.register_asset(a3)

    dist = profiler.get_modality_distribution()
    assert dist["numerical"] == 1
    assert dist["visual"] == 1
    assert dist["textual"] == 1

    out_file = tmp_path / "inventory.json"
    profiler.export_inventory_json(out_file)
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data["assets"]) == 3
