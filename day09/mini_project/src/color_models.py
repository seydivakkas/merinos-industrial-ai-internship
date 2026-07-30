"""
color_models.py - Pydantic Data Models for Dominant Palette & CIEDE2000 Matching Engine.
"""

from enum import Enum
from typing import Any, List, Dict
from pydantic import BaseModel, Field, field_validator


class MatchGrade(str, Enum):
    """Quality assurance grade based on CIEDE2000 color difference."""
    EXACT = "exact"               # DeltaE00 < 1.0 (Imperceptible difference)
    ACCEPTABLE = "acceptable"     # 1.0 <= DeltaE00 < 2.0 (Commercially acceptable)
    WARNING = "warning"           # 2.0 <= DeltaE00 < 4.0 (Noticeable variation, supervisor review)
    OUT_OF_SPEC = "out_of_spec"   # DeltaE00 >= 4.0 (Reject / Custom dyeing required)


class CatalogYarn(BaseModel):
    """Certified production yarn bobbin in Merinos factory inventory."""
    yarn_id: str = Field(..., description="Unique yarn identifier, e.g. MRN-YRN-001")
    name: str = Field(..., description="Descriptive commercial yarn color name")
    rgb: List[int] = Field(..., description="Reference sRGB [R, G, B] in [0, 255]")
    cielab: List[float] = Field(..., description="Reference CIE L*a*b* under D65 illuminant")
    pantone_code: str = Field(..., description="Pantone TCX / Textile reference code")
    material: str = Field(default="100% Heat-Set Polypropylene", description="Yarn fiber material")
    cost_per_kg: float = Field(..., ge=0.0, description="Unit material cost in USD/kg")
    in_stock: bool = Field(default=True, description="Inventory availability flag")

    @field_validator("rgb")
    @classmethod
    def validate_rgb(cls, v: List[int]) -> List[int]:
        if len(v) != 3:
            raise ValueError("RGB must have exactly 3 components.")
        if any(c < 0 or c > 255 for c in v):
            raise ValueError("RGB channels must be in [0, 255].")
        return v

    @field_validator("cielab")
    @classmethod
    def validate_cielab(cls, v: List[float]) -> List[float]:
        if len(v) != 3:
            raise ValueError("CIELAB must have exactly 3 components [L*, a*, b*].")
        L, a, b = v
        if not (0.0 <= L <= 100.0):
            raise ValueError("L* must be in range [0.0, 100.0].")
        if not (-128.0 <= a <= 128.0 and -128.0 <= b <= 128.0):
            raise ValueError("a* and b* must be within reasonable CIELAB bounds [-128, 128].")
        return v


class ExtractedColor(BaseModel):
    """Dominant color cluster extracted from carpet pattern image via K-Means."""
    cluster_id: int = Field(..., ge=0, description="Cluster index sorted by area dominance")
    rgb: List[int] = Field(..., description="Centroid sRGB [R, G, B] in [0, 255]")
    cielab: List[float] = Field(..., description="Centroid CIE L*a*b* [L*, a*, b*]")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Surface area coverage percentage")
    pixel_count: int = Field(..., ge=0, description="Total assigned pixel count")


class YarnMatchResult(BaseModel):
    """Evaluation result of matching an extracted color to the nearest catalog yarn bobbin."""
    extracted_color: ExtractedColor
    matched_yarn: CatalogYarn
    delta_e_00: float = Field(..., ge=0.0, description="CIEDE2000 perceptual color distance")
    delta_e_76: float = Field(..., ge=0.0, description="CIE 1976 Euclidean color distance for comparison")
    match_grade: MatchGrade
    alternative_matches: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top-3 closest alternative bobbins with their delta_e_00 values"
    )


class PaletteExtractionResult(BaseModel):
    """Output summary of K-Means palette extraction."""
    k: int = Field(..., ge=1, description="Number of clusters extracted")
    space_used: str = Field(..., description="Color space used for clustering (RGB or LAB)")
    palette: List[ExtractedColor] = Field(..., description="List of extracted colors sorted by dominance")
    inertia: float = Field(..., description="K-Means sum of squared distances to centroids")
    sample_ratio: float = Field(..., description="Subsampling ratio used for clustering acceleration")
    total_pixels: int = Field(..., ge=1, description="Total pixels in image")
    elapsed_ms: float = Field(..., ge=0.0, description="Clustering latency in milliseconds")


class CreelAllocationPlan(BaseModel):
    """Jacquard loom creel bobbin allocation manifest for production."""
    allocation_id: str
    pattern_name: str
    target_creel_size: int
    active_bobbins: List[YarnMatchResult]
    unique_yarn_count: int
    total_estimated_yarn_cost_per_m2: float
    uncatalogued_colors_count: int


class QuantizationReport(BaseModel):
    """Full-image color quantization and distortion report."""
    image_shape: List[int]
    num_colors_used: int
    mean_delta_e_00: float = Field(..., ge=0.0, description="Average perceptual distortion per pixel")
    max_delta_e_00: float = Field(..., ge=0.0, description="Maximum perceptual distortion in image")
    coverage_percentages: Dict[str, float] = Field(
        default_factory=dict,
        description="Percentage of carpet surface covered by each catalog yarn ID"
    )
