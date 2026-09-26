"""Day 04 - Data Models for Workstation Environment and Data Contracts.

Defines schemas for Python development workstation auditing, system resource
specifications, and re-exports industrial data contracts.
"""

from typing import List
from pydantic import BaseModel, Field

from day01.mini_project.src.models import DataAsset, DataModality
from day04.mini_project.src.data_contracts import (
    CarpetSpecificationContract,
    ContractValidationError,
    LoomTelemetryContract,
)


class SystemResourceRequirements(BaseModel):
    """Minimum hardware and Python environment requirements."""
    min_cpu_cores: int = Field(default=2, ge=1)
    min_ram_gb: float = Field(default=4.0, ge=1.0)
    required_python_version: str = Field(default="3.10")
    supported_modalities: List[DataModality] = Field(
        default_factory=lambda: [DataModality.NUMERICAL, DataModality.VISUAL, DataModality.TEXTUAL]
    )


class WorkstationAuditResult(BaseModel):
    """Result of workstation environment and capability check."""
    cpu_cores: int
    ram_gb: float
    python_version: str
    os_name: str
    is_compliant: bool
    modalities_supported: List[DataModality]
    notes: List[str]


__all__ = [
    "DataModality",
    "DataAsset",
    "SystemResourceRequirements",
    "WorkstationAuditResult",
    "CarpetSpecificationContract",
    "LoomTelemetryContract",
    "ContractValidationError",
]
