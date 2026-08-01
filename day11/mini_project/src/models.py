"""
models.py - Pydantic v2 Models for Day 11 Morphological Defect Detection.
"""

from enum import Enum
from typing import Dict, List, Tuple
from pydantic import BaseModel, Field


class DefectType(str, Enum):
    """Types of physical weaving and finishing defects encountered on carpets."""
    HOLE = "HOLE"
    YARN_BREAK_WEFT = "YARN_BREAK_WEFT"
    YARN_BREAK_WARP = "YARN_BREAK_WARP"
    SLUB_KNOT = "SLUB_KNOT"
    OIL_STAIN = "OIL_STAIN"


class DefectSeverity(str, Enum):
    """Severity tier for defect grading and intervention."""
    CRITICAL = "CRITICAL"      # Requires cutting or immediate line stop
    MAJOR = "MAJOR"            # Requires manual mending / repair
    MINOR = "MINOR"            # Cosmetic flaw within allowable discount grade
    ACCEPTABLE = "ACCEPTABLE"  # Negligible micro-imperfection


class RollDecision(str, Enum):
    """Quality decision for inspected carpet roll section."""
    PASS = "PASS"      # 1st quality certified
    REPAIR = "REPAIR"  # Forwarded to manual mending station
    REJECT = "REJECT"  # Scrap / 2nd quality downgraded


class DefectBoundingBox(BaseModel):
    """2D Bounding box of detected defect in image pixel coordinates."""
    x: int = Field(ge=0, description="Top-left X pixel coordinate")
    y: int = Field(ge=0, description="Top-left Y pixel coordinate")
    width: int = Field(gt=0, description="Bounding box width in pixels")
    height: int = Field(gt=0, description="Bounding box height in pixels")
    area: float = Field(gt=0, description="Contour pixel area")
    aspect_ratio: float = Field(gt=0, description="Aspect ratio (max(w,h) / min(w,h))")
    centroid: Tuple[float, float] = Field(description="Center of mass (cx, cy)")


class DetectedDefect(BaseModel):
    """Single detected defect occurrence with classification and geometry."""
    defect_type: DefectType
    severity: DefectSeverity
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")
    bbox: DefectBoundingBox
    mean_contrast: float = Field(description="Mean absolute intensity difference from local background")


class MorphologyInspectionReport(BaseModel):
    """Comprehensive inspection report for a carpet image section."""
    image_path: str
    resolution: Tuple[int, int] = Field(description="(width, height) in pixels")
    total_defects: int = Field(ge=0)
    defect_counts: Dict[str, int] = Field(default_factory=dict)
    roll_decision: RollDecision
    processing_time_ms: float = Field(ge=0.0)
    defects: List[DetectedDefect] = Field(default_factory=list)
