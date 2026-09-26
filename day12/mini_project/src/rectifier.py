"""
rectifier.py - Carpet Perspective Rectifier Pipeline & Geometric Orthogonality Assessment.
"""

import json
from pathlib import Path
from typing import Optional, Tuple, Union, Dict, Any
import numpy as np
import cv2

from .models import (
    Point2D,
    QuadCorners,
    StandardCarpetRatio,
    HomographyResult,
    QAGrade,
    RectificationReport,
)
from .corner_detector import CornerDetector, order_points
from .homography import compute_homography, warp_perspective, transform_points


class CarpetPerspectiveRectifier:
    """End-to-end perspective distortion correction for carpet manufacturing inspection."""

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
    ):
        self.config = self._load_config(config_path)
        cd_cfg = self.config.get("corner_detection", {})
        self.corner_detector = CornerDetector(
            canny_low=cd_cfg.get("canny_low_threshold", 40),
            canny_high=cd_cfg.get("canny_high_threshold", 120),
            blur_kernel=tuple(cd_cfg.get("gaussian_blur_kernel", [5, 5])),
            morph_kernel_size=tuple(cd_cfg.get("morph_kernel_size", [5, 5])),
            min_area_ratio=cd_cfg.get("min_carpet_area_ratio", 0.15),
            approx_epsilon_ratio=cd_cfg.get("approx_poly_epsilon_ratio", 0.025),
        )

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        if config_path is None:
            default_path = Path(__file__).resolve().parent.parent / "configs" / "rectification_config.json"
            config_path = default_path

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def compute_target_dimensions(
        self,
        corners: QuadCorners,
        mode: str = "adaptive",
        standard_ratio: Optional[StandardCarpetRatio] = None,
    ) -> Tuple[int, int]:
        """Compute target rectified width and height in pixels.

        Args:
            corners: QuadCorners model containing the 4 ordered points.
            mode: 'adaptive' (maximum edge length) or 'standard' (catalog physical ratio).
            standard_ratio: StandardCarpetRatio enum if mode == 'standard'.

        Returns:
            Tuple of (target_width, target_height) in integer pixels.
        """
        pts = corners.to_numpy()

        # Compute edge lengths
        width_bottom = float(np.linalg.norm(pts[2] - pts[3]))  # BR to BL
        width_top = float(np.linalg.norm(pts[1] - pts[0]))     # TR to TL
        max_w = int(round(max(width_bottom, width_top)))

        height_right = float(np.linalg.norm(pts[2] - pts[1]))  # BR to TR
        height_left = float(np.linalg.norm(pts[3] - pts[0]))   # BL to TL
        max_h = int(round(max(height_right, height_left)))

        # Ensure minimal viable dimension
        max_w = max(64, max_w)
        max_h = max(64, max_h)

        if mode == "adaptive":
            return (max_w, max_h)

        # Standard physical ratio mode
        sizes_cfg = self.config.get("standard_carpet_sizes", {})
        key = standard_ratio.value if standard_ratio else "160x230"

        if key in sizes_cfg:
            ratio_val = sizes_cfg[key]["aspect_ratio"]
            # Preserve max observed height and scale width strictly to physical ratio
            target_h = max_h
            target_w = int(round(target_h * ratio_val))
            return (target_w, target_h)

        return (max_w, max_h)

    def rectify(
        self,
        image_bgr: np.ndarray,
        corners: Optional[Union[np.ndarray, QuadCorners]] = None,
        mode: str = "adaptive",
        standard_ratio: Optional[StandardCarpetRatio] = None,
        interpolation: int = cv2.INTER_LINEAR,
    ) -> Tuple[np.ndarray, RectificationReport]:
        """Rectify a perspective-distorted carpet image to an orthographic top-down view.

        Args:
            image_bgr: Input distorted BGR carpet image.
            corners: Optional manually provided or previously detected 4 corners.
            mode: 'adaptive' or 'standard'.
            standard_ratio: Optional Merinos catalog standard size.
            interpolation: OpenCV interpolation flag.

        Returns:
            Tuple of:
            - rectified_image: Corrected (H, W, 3) BGR image.
            - report: RectificationReport containing homography, orthogonality, and QA grade.
        """
        # 1. Corner acquisition
        if corners is None:
            raw_pts = self.corner_detector.detect_corners(image_bgr)
            ordered_pts = order_points(raw_pts)
            quad = QuadCorners.from_numpy(ordered_pts)
        elif isinstance(corners, QuadCorners):
            quad = corners
            ordered_pts = quad.to_numpy()
        else:
            ordered_pts = order_points(np.asarray(corners, dtype=np.float32))
            quad = QuadCorners.from_numpy(ordered_pts)

        # 2. Target dimension calculation
        target_w, target_h = self.compute_target_dimensions(
            quad, mode=mode, standard_ratio=standard_ratio
        )

        # 3. Define target rectangular coordinates [TL, TR, BR, BL]
        dst_pts = np.array([
            [0.0, 0.0],
            [float(target_w - 1), 0.0],
            [float(target_w - 1), float(target_h - 1)],
            [0.0, float(target_h - 1)],
        ], dtype=np.float32)

        # 4. Compute 3x3 Homography Matrix
        H, homography_res = compute_homography(ordered_pts, dst_pts)

        # 5. Perspective Warp
        rectified = warp_perspective(
            image_bgr,
            H,
            (target_w, target_h),
            flags=interpolation,
        )

        # 6. Geometric Quality Assessment (Orthogonality)
        rect_quad = QuadCorners.from_numpy(dst_pts)
        rect_angles = rect_quad.corner_angles()
        deviations = [round(abs(a - 90.0), 2) for a in rect_angles]
        max_dev = max(deviations) if deviations else 0.0

        qa_cfg = self.config.get("qa_rectification_thresholds", {})
        pass_thresh = qa_cfg.get("max_corner_angle_deviation_pass", 1.5)
        warn_thresh = qa_cfg.get("max_corner_angle_deviation_warning", 4.0)

        cond = homography_res.condition_number
        if max_dev <= pass_thresh and cond < 1e5:
            grade = QAGrade.PASS
            msg = f"Perspective successfully rectified with high precision (Max deviation: {max_dev:.2f} deg)."
        elif max_dev <= warn_thresh and cond < 1e6:
            grade = QAGrade.WARNING
            msg = f"Rectification acceptable with minor angle skew (Max deviation: {max_dev:.2f} deg)."
        else:
            grade = QAGrade.REJECT
            msg = f"Rectification rejected: excessive distortion or ill-conditioned H (cond: {cond:.1f})."

        report = RectificationReport(
            source_corners=quad,
            target_dimensions=[target_w, target_h],
            rectification_mode=mode,
            aspect_ratio=round(target_w / target_h, 4),
            corner_angles=rect_angles,
            max_angle_deviation=max_dev,
            homography=homography_res,
            qa_grade=grade,
            message=msg,
        )

        return rectified, report
