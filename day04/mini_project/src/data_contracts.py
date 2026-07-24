"""Day 04 - Python Development Environment and Pydantic v2 Data Contracts.

Defines formal data contracts for carpet specifications, loom telemetry,
and quality inspection records with strict type constraints and validators.
"""

from datetime import datetime, timezone
import re
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ContractValidationError(Exception):
    """Raised when data contracts fail validation."""
    pass


class CarpetSpecificationContract(BaseModel):
    """Data contract for physical carpet product specification."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    product_id: str = Field(..., description="Unique product SKU (e.g. CRP-001)")
    title: str = Field(..., min_length=3, max_length=100)
    collection: str = Field(..., min_length=2, max_length=50)
    width_cm: float = Field(..., ge=20.0, le=1200.0, description="Width in cm [20, 1200]")
    length_cm: float = Field(..., ge=20.0, le=1200.0, description="Length in cm [20, 1200]")
    pile_height_mm: float = Field(default=10.0, ge=1.0, le=50.0, description="Pile height in mm [1, 50]")
    palette_hex: List[str] = Field(..., min_length=1, max_length=16)

    @field_validator("palette_hex")
    @classmethod
    def validate_hex_palette(cls, v: List[str]) -> List[str]:
        pattern = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
        cleaned = []
        for hex_code in v:
            c = hex_code.strip()
            if not re.match(pattern, c):
                raise ValueError(f"Invalid Hex color code: {hex_code}")
            cleaned.append(c.upper())
        return cleaned

    @model_validator(mode="after")
    def validate_aspect_ratio(self) -> "CarpetSpecificationContract":
        ratio = max(self.width_cm, self.length_cm) / min(self.width_cm, self.length_cm)
        if ratio > 6.0:
            raise ValueError(f"Carpet aspect ratio exceeds loom mechanical limit (ratio={ratio:.1f}:1, max=6:1).")
        return self


class LoomTelemetryContract(BaseModel):
    """Data contract for weaving loom telemetry sensors."""
    model_config = ConfigDict(extra="forbid")

    loom_id: str = Field(..., description="Identifier of the loom (e.g. LOOM-01)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    motor_temperature_c: float = Field(..., ge=10.0, le=120.0)
    pneumatic_pressure_bar: float = Field(..., ge=5.0, le=25.0)
    warp_tension_cn: float = Field(..., ge=100.0, le=1000.0)
    rpm: int = Field(..., ge=0, le=1200)
    error_code: Optional[str] = Field(default=None)
