"""Data Models and Schema Definitions for Industrial Color Analysis."""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class QAGrade(str, Enum):
    """Quality assurance classification based on perceptual Delta E."""

    PASS = "PASS"
    WARNING = "WARNING"
    REJECT = "REJECT"


@dataclass
class YarnColor:
    """Standard industrial yarn color specification."""

    name: str
    code: str
    hex_code: str
    rgb: tuple[int, int, int]
    bgr: tuple[int, int, int]
    lab: tuple[float, float, float]
    hsv_lower: tuple[int, int, int] | None = None
    hsv_upper: tuple[int, int, int] | None = None
    # For colors that wrap around hue=180 (like red)
    hsv_lower2: tuple[int, int, int] | None = None
    hsv_upper2: tuple[int, int, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ColorDifferenceResult:
    """Perceptual color distance result calculated via CIE 1976 Delta E."""

    delta_e: float
    delta_l: float
    delta_a: float
    delta_b: float
    grade: QAGrade
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        res = asdict(self)
        res["grade"] = self.grade.value
        return res


@dataclass
class YarnSegmentationResult:
    """Statistical summary of a segmented yarn color region in carpet scan."""

    yarn_name: str
    yarn_code: str
    pixel_count: int
    area_percentage: float
    mean_rgb: tuple[float, float, float]
    mean_lab: tuple[float, float, float]
    delta_e_from_target: float
    grade: QAGrade

    def to_dict(self) -> dict[str, Any]:
        res = asdict(self)
        res["grade"] = self.grade.value
        return res


@dataclass
class DyeLotInspectionReport:
    """Comprehensive dye lot inspection and yarn composition QA report."""

    carpet_name: str
    total_pixels: int
    overall_status: QAGrade
    max_delta_e: float
    yarn_findings: list[YarnSegmentationResult]
    unclassified_percentage: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "carpet_name": self.carpet_name,
            "total_pixels": self.total_pixels,
            "overall_status": self.overall_status.value,
            "max_delta_e": self.max_delta_e,
            "yarn_findings": [f.to_dict() for f in self.yarn_findings],
            "unclassified_percentage": self.unclassified_percentage,
        }
