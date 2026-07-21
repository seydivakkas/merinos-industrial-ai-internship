"""Day 01 - Data Models for Environment Profiling and Data Taxonomy.

Defines Pydantic v2 schemas for workstation environment profiling,
computational resources inventory, and industrial data type classification.
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class DataModality(str, Enum):
    """Core industrial data modalities identified in the textile enterprise."""
    NUMERICAL = "numerical"   # Telemetry, sensor readings, dimensions, warp tension
    VISUAL = "visual"         # Carpet surface photographs, inspection camera frames
    TEXTUAL = "textual"       # Technical manuals, incident logs, standard operating procedures


class DataAsset(BaseModel):
    """Represents an industrial data sample or file asset."""
    asset_id: str = Field(..., description="Unique asset identifier")
    name: str = Field(..., description="Human-readable asset title")
    modality: DataModality = Field(..., description="Data modality category")
    source_type: str = Field(..., description="Source system (e.g. LoomSensor, InspectionCamera, TechManual)")
    estimated_size_kb: float = Field(..., ge=0.0, description="Estimated size in kilobytes")
    description: Optional[str] = Field(default=None, description="Technical context and notes")


class SystemResourceRequirements(BaseModel):
    """Minimum hardware profile for local PoC execution."""
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
