"""
models.py - Pydantic Data Models for Perspective Rectification & Homography Engine.
"""

from enum import Enum
from typing import List, Dict, Tuple, Any
import numpy as np
from pydantic import BaseModel, Field, field_validator


class Point2D(BaseModel):
    """2D floating-point subpixel image coordinate [x, y]."""
    x: float = Field(..., description="Horizontal pixel coordinate (column)")
    y: float = Field(..., description="Vertical pixel coordinate (row)")

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def to_int_tuple(self) -> Tuple[int, int]:
        return (int(round(self.x)), int(round(self.y)))


class QuadCorners(BaseModel):
    """Oriented 4 exterior corner coordinates of a quadrilateral in standard order:
    [Top-Left, Top-Right, Bottom-Right, Bottom-Left].
    """
    top_left: Point2D
    top_right: Point2D
    bottom_right: Point2D
    bottom_left: Point2D

    def to_numpy(self) -> np.ndarray:
        """Return corners as a (4, 2) float32 NumPy array."""
        return np.array([
            [self.top_left.x, self.top_left.y],
            [self.top_right.x, self.top_right.y],
            [self.bottom_right.x, self.bottom_right.y],
            [self.bottom_left.x, self.bottom_left.y],
        ], dtype=np.float32)

    @classmethod
    def from_numpy(cls, pts: np.ndarray) -> "QuadCorners":
        """Create QuadCorners from an ordered (4, 2) NumPy array."""
        p = pts.reshape(4, 2).astype(np.float64)
        return cls(
            top_left=Point2D(x=float(p[0, 0]), y=float(p[0, 1])),
            top_right=Point2D(x=float(p[1, 0]), y=float(p[1, 1])),
            bottom_right=Point2D(x=float(p[2, 0]), y=float(p[2, 1])),
            bottom_left=Point2D(x=float(p[3, 0]), y=float(p[3, 1])),
        )

    def edge_lengths(self) -> Dict[str, float]:
        """Compute Euclidean lengths of the four edges (top, right, bottom, left)."""
        pts = self.to_numpy()
        return {
            "top": float(np.linalg.norm(pts[1] - pts[0])),
            "right": float(np.linalg.norm(pts[2] - pts[1])),
            "bottom": float(np.linalg.norm(pts[2] - pts[3])),
            "left": float(np.linalg.norm(pts[3] - pts[0])),
        }

    def corner_angles(self) -> List[float]:
        """Compute internal corner angles in degrees [TL, TR, BR, BL]."""
        pts = self.to_numpy()
        angles = []
        for i in range(4):
            prev_pt = pts[(i - 1) % 4]
            curr_pt = pts[i]
            next_pt = pts[(i + 1) % 4]

            v1 = prev_pt - curr_pt
            v2 = next_pt - curr_pt

            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 < 1e-6 or norm2 < 1e-6:
                angles.append(0.0)
                continue

            cos_theta = np.dot(v1, v2) / (norm1 * norm2)
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            angle_deg = float(np.degrees(np.arccos(cos_theta)))
            angles.append(round(angle_deg, 2))

        return angles


class StandardCarpetRatio(str, Enum):
    """Standard physical catalog carpet dimensions manufactured by Merinos."""
    STANDARD_160_230 = "160x230"
    STANDARD_200_290 = "200x290"
    RUNNER_80_150 = "80x150"
    SQUARE_100_100 = "100x100"


class HomographyResult(BaseModel):
    """Mathematical properties of the estimated 3x3 homography perspective matrix."""
    matrix: List[List[float]] = Field(..., description="3x3 Homography projection matrix H")
    determinant: float = Field(..., description="Determinant of matrix H (det(H))")
    condition_number: float = Field(..., description="Numerical stability condition number cond(H)")
    inverse_frobenius_error: float = Field(
        ...,
        description="Residual Frobenius error ||H * H^-1 - I||_F verifying numerical invertibility"
    )

    def to_numpy(self) -> np.ndarray:
        return np.array(self.matrix, dtype=np.float64)


class QAGrade(str, Enum):
    """Quality assurance assessment of geometric rectification."""
    PASS = "pass"        # Deviation <= 1.5 deg
    WARNING = "warning"  # 1.5 deg < Deviation <= 4.0 deg
    REJECT = "reject"    # Deviation > 4.0 deg or ill-conditioned H


class RectificationReport(BaseModel):
    """End-to-end perspective rectification quality and metric report."""
    source_corners: QuadCorners
    target_dimensions: List[int] = Field(..., description="Target image resolution [width, height]")
    rectification_mode: str = Field(..., description="'adaptive' or 'standard'")
    aspect_ratio: float = Field(..., description="Output aspect ratio (width / height)")
    corner_angles: List[float] = Field(..., description="Interior angles of rectified corners in degrees")
    max_angle_deviation: float = Field(..., description="Maximum deviation from 90.0 degrees")
    homography: HomographyResult
    qa_grade: QAGrade
    message: str
