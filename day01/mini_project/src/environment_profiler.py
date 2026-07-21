"""Day 01 - Environment Profiler and Data Asset Inventory Manager.

Performs local system hardware audits and manages classification of
textile enterprise data assets (numerical, visual, textual).
"""

import json
import logging
import os
import platform
import sys
from pathlib import Path
from typing import Dict, List

import psutil

from day01.mini_project.src.models import (
    DataAsset,
    DataModality,
    SystemResourceRequirements,
    WorkstationAuditResult,
)

logger = logging.getLogger("Day01_EnvironmentProfiler")


class EnvironmentProfiler:
    """Audits local development workstation and inventories enterprise data assets."""

    def __init__(self, requirements: SystemResourceRequirements) -> None:
        self.requirements = requirements
        self.assets: List[DataAsset] = []

    def audit_workstation(self) -> WorkstationAuditResult:
        """Audits current host system resources against baseline requirements."""
        cpu_cores = os.cpu_count() or 1
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        os_name = f"{platform.system()} {platform.release()}"

        notes: List[str] = []
        is_compliant = True

        if cpu_cores < self.requirements.min_cpu_cores:
            is_compliant = False
            notes.append(f"CPU count ({cpu_cores}) is below required minimum ({self.requirements.min_cpu_cores})")
        else:
            notes.append(f"CPU cores sufficient: {cpu_cores}")

        if ram_gb < self.requirements.min_ram_gb:
            is_compliant = False
            notes.append(f"RAM ({ram_gb} GB) is below required minimum ({self.requirements.min_ram_gb} GB)")
        else:
            notes.append(f"RAM sufficient: {ram_gb} GB")

        notes.append(f"Python runtime: {python_ver} on {os_name}")

        result = WorkstationAuditResult(
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            python_version=python_ver,
            os_name=os_name,
            is_compliant=is_compliant,
            modalities_supported=self.requirements.supported_modalities,
            notes=notes,
        )
        logger.info(f"Audit completed: Compliant={is_compliant}")
        return result

    def register_asset(self, asset: DataAsset) -> None:
        """Registers a sample data asset in the inventory."""
        self.assets.append(asset)
        logger.info(f"Registered asset: {asset.asset_id} ({asset.modality.value})")

    def get_modality_distribution(self) -> Dict[str, int]:
        """Calculates distribution of registered assets across modalities."""
        distribution: Dict[str, int] = {m.value: 0 for m in DataModality}
        for asset in self.assets:
            distribution[asset.modality.value] += 1
        return distribution

    def export_inventory_json(self, output_path: Path) -> None:
        """Exports the asset inventory and system profile to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "requirements": self.requirements.model_dump(),
            "assets": [a.model_dump() for a in self.assets],
            "distribution": self.get_modality_distribution(),
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Exported inventory to {output_path}")
