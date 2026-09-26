"""Day 01 - Industrial Observation Catalog.

Implements an observation and cataloging system for heterogeneous industrial
data assets (numerical telemetry, visual surface imagery, textual documentation)
observed within an industrial carpet manufacturing environment.
Strictly uses synthetic metadata and local data taxonomy models.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from day01.mini_project.src.models import DataAsset, DataModality


class ObservationCatalog:
    """Manages an inventory of industrial data assets categorized by modality and domain."""

    def __init__(self, name: str = "Merinos_Observation_Catalog"):
        self.name = name
        self._assets: Dict[str, DataAsset] = {}

    def add_asset(self, asset: DataAsset) -> None:
        """Register a new data asset into the observation catalog."""
        if asset.asset_id in self._assets:
            raise ValueError(f"Asset with ID '{asset.asset_id}' already exists in catalog.")
        self._assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Optional[DataAsset]:
        """Retrieve an asset by its unique identifier."""
        return self._assets.get(asset_id)

    def list_assets(self) -> List[DataAsset]:
        """Return all registered assets."""
        return list(self._assets.values())

    def filter_by_modality(self, modality: DataModality) -> List[DataAsset]:
        """Return all assets belonging to a specific modality."""
        return [asset for asset in self._assets.values() if asset.modality == modality]

    def get_summary(self) -> Dict[str, Any]:
        """Compute summary statistics of registered data modalities."""
        total_assets = len(self._assets)
        total_kb = sum(a.estimated_size_kb for a in self._assets.values())
        modality_counts = {mod.value: 0 for mod in DataModality}
        modality_size_kb = {mod.value: 0.0 for mod in DataModality}

        for asset in self._assets.values():
            modality_counts[asset.modality.value] += 1
            modality_size_kb[asset.modality.value] += asset.estimated_size_kb

        return {
            "catalog_name": self.name,
            "total_assets": total_assets,
            "total_size_kb": round(total_kb, 2),
            "modality_counts": modality_counts,
            "modality_size_kb": {k: round(v, 2) for k, v in modality_size_kb.items()},
        }

    def export_json(self, output_path: Path) -> Path:
        """Export the catalog to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "catalog_name": self.name,
            "assets": [a.model_dump() for a in self._assets.values()],
            "summary": self.get_summary(),
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

    @classmethod
    def create_sample_catalog(cls) -> ObservationCatalog:
        """Create a catalog pre-populated with synthetic industrial textile examples."""
        catalog = cls(name="Sample_Industrial_Textile_Catalog")
        samples = [
            DataAsset(
                asset_id="NUM-001",
                name="synthetic_loom_warp_tension_log",
                modality=DataModality.NUMERICAL,
                source_type="SyntheticLoomTelemetry",
                estimated_size_kb=450.5,
                description="Simulated 1000-point time-series of yarn tension and machine RPM.",
            ),
            DataAsset(
                asset_id="NUM-002",
                name="synthetic_heat_setting_temperature_log",
                modality=DataModality.NUMERICAL,
                source_type="SyntheticChamberTelemetry",
                estimated_size_kb=128.0,
                description="Synthetic temperature readings across 4 heating zones.",
            ),
            DataAsset(
                asset_id="VIS-001",
                name="synthetic_carpet_surface_scan",
                modality=DataModality.VISUAL,
                source_type="SyntheticCameraFrame",
                estimated_size_kb=2048.0,
                description="Synthetic 1024x1024 RGB image showing woven pattern sample.",
            ),
            DataAsset(
                asset_id="VIS-002",
                name="synthetic_weft_defect_patch",
                modality=DataModality.VISUAL,
                source_type="SyntheticCameraFrame",
                estimated_size_kb=512.0,
                description="Synthetic crop containing simulated warp breakage artifact.",
            ),
            DataAsset(
                asset_id="TXT-001",
                name="synthetic_loom_maintenance_manual",
                modality=DataModality.TEXTUAL,
                source_type="SyntheticTechnicalDocumentation",
                estimated_size_kb=85.0,
                description="Synthetic SOP detailing lubrication and reed cleaning procedures.",
            ),
            DataAsset(
                asset_id="TXT-002",
                name="synthetic_yarn_quality_standard",
                modality=DataModality.TEXTUAL,
                source_type="SyntheticStandardDocument",
                estimated_size_kb=42.0,
                description="Synthetic specifications for tensile strength and twist tolerances.",
            ),
        ]
        for sample in samples:
            catalog.add_asset(sample)
        return catalog
