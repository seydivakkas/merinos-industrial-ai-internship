"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Perspektif Düzeltme ve Homografi Matrisi Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from .corner_detector import CornerDetector, order_points
from .homography import compute_homography, transform_points, warp_perspective
from .homography_rectifier import HomographyRectifier, order_four_points
from .rectifier import CarpetPerspectiveRectifier
from .generator import (
    create_flat_carpet_patch,
    apply_synthetic_homography,
    generate_all_synthetic_rectification_fixtures,
    _safe_imwrite,
)
from .models import (
    Point2D,
    QuadCorners,
    StandardCarpetRatio,
    HomographyResult,
    QAGrade,
    RectificationReport,
)

__all__ = [
    "CornerDetector",
    "order_points",
    "compute_homography",
    "transform_points",
    "warp_perspective",
    "HomographyRectifier",
    "order_four_points",
    "CarpetPerspectiveRectifier",
    "create_flat_carpet_patch",
    "apply_synthetic_homography",
    "generate_all_synthetic_rectification_fixtures",
    "_safe_imwrite",
    "Point2D",
    "QuadCorners",
    "StandardCarpetRatio",
    "HomographyResult",
    "QAGrade",
    "RectificationReport",
]
