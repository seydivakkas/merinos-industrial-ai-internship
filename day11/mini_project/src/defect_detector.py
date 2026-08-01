"""
defect_detector.py - Industrial Carpet Weaving Defect Detection & Classification.
"""

import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from day11.mini_project.src.models import (
    DefectType,
    DefectSeverity,
    RollDecision,
    DefectBoundingBox,
    DetectedDefect,
    MorphologyInspectionReport,
)
from day11.mini_project.src.morphology_engine import MorphologyEngine


class CarpetDefectDetector:
    """Detects and classifies structural defects on woven carpets using mathematical morphology."""

    def __init__(
        self,
        blur_kernel: Tuple[int, int] = (3, 3),
        blur_sigma: float = 1.0,
        tophat_kernel_size: Tuple[int, int] = (11, 11),
        blackhat_kernel_size: Tuple[int, int] = (17, 17),
        tophat_thresh: float = 20.0,
        blackhat_thresh: float = 22.0,
        min_area: float = 15.0,
        max_area: float = 5000.0,
        aspect_ratio_threshold: float = 3.2,
    ):
        self.blur_kernel = blur_kernel
        self.blur_sigma = blur_sigma
        self.tophat_ksize = tophat_kernel_size
        self.blackhat_ksize = blackhat_kernel_size
        self.tophat_thresh = tophat_thresh
        self.blackhat_thresh = blackhat_thresh
        self.min_area = min_area
        self.max_area = max_area
        self.aspect_ratio_thresh = aspect_ratio_threshold

    def inspect(
        self,
        image_bgr: np.ndarray,
        image_path: str = "carpet_frame.png",
    ) -> Tuple[MorphologyInspectionReport, Dict[str, np.ndarray]]:
        """Inspect a carpet image for weaving and finishing defects.

        Args:
            image_bgr: Input BGR image (H, W, 3).
            image_path: Optional metadata file path.

        Returns:
            Tuple of (MorphologyInspectionReport, debug_masks_dict).
        """
        t_start = time.perf_counter()
        h, w = image_bgr.shape[:2]

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, self.blur_sigma)

        # 1. Multi-scale White Top-Hat for bright anomalies (slub knots)
        engine_top_med = MorphologyEngine(kernel_size=15)
        engine_top_large = MorphologyEngine(kernel_size=29)
        wth = np.maximum(
            engine_top_med.white_tophat(blurred),
            engine_top_large.white_tophat(blurred),
        )

        # 2. Multi-scale Black Top-Hat for dark anomalies (small punctures, large holes, oil spots)
        engine_black_med = MorphologyEngine(kernel_size=17)
        engine_black_large = MorphologyEngine(kernel_size=37)
        bth_med = engine_black_med.black_tophat(blurred)
        bth_large = engine_black_large.black_tophat(blurred)
        bth = np.maximum(bth_med, bth_large)

        # 3. Directional structuring elements for thin breaks:
        k_bridge_weft = MorphologyEngine.get_directional_kernel("vertical", length=19, thickness=1)
        k_bridge_warp = MorphologyEngine.get_directional_kernel("horizontal", length=19, thickness=1)

        bth_weft = cv2.morphologyEx(blurred, cv2.MORPH_BLACKHAT, k_bridge_weft)
        bth_warp = cv2.morphologyEx(blurred, cv2.MORPH_BLACKHAT, k_bridge_warp)

        # Thresholding
        _, mask_wth = cv2.threshold(wth, self.tophat_thresh, 255, cv2.THRESH_BINARY)
        _, mask_bth = cv2.threshold(bth, self.blackhat_thresh, 255, cv2.THRESH_BINARY)
        _, mask_weft = cv2.threshold(bth_weft, self.blackhat_thresh, 255, cv2.THRESH_BINARY)
        _, mask_warp = cv2.threshold(bth_warp, self.blackhat_thresh, 255, cv2.THRESH_BINARY)

        # Morphological noise cleanup (small opening to eliminate 1-px texture ripples)
        clean_engine = MorphologyEngine(kernel_size=3)
        mask_wth = clean_engine.opening(mask_wth)
        mask_bth = clean_engine.opening(mask_bth)
        mask_weft = clean_engine.opening(mask_weft)
        mask_warp = clean_engine.opening(mask_warp)

        # Unified dark defects mask
        mask_dark = cv2.bitwise_or(mask_bth, cv2.bitwise_or(mask_weft, mask_warp))

        detected_defects: List[DetectedDefect] = []

        # Helper to process binary mask contours
        def _extract_contours(mask: np.ndarray, is_bright: bool):
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts:
                area = cv2.contourArea(cnt)
                if area < self.min_area or area > self.max_area:
                    continue

                x, y, bw, bh = cv2.boundingRect(cnt)
                peri = cv2.arcLength(cnt, True)
                circularity = (4.0 * np.pi * area) / (peri * peri) if peri > 0 else 0.0
                aspect_ratio = max(bw, bh) / max(1.0, float(min(bw, bh)))

                # Moments for centroid
                m = cv2.moments(cnt)
                if m["m00"] > 0:
                    cx = float(m["m10"] / m["m00"])
                    cy = float(m["m01"] / m["m00"])
                else:
                    cx = float(x + bw / 2.0)
                    cy = float(y + bh / 2.0)

                # Contrast difference
                roi = gray[y : y + bh, x : x + bw]
                local_bg = float(np.median(gray[max(0, y - 5) : min(h, y + bh + 5), max(0, x - 5) : min(w, x + bw + 5)]))
                mean_contrast = abs(float(np.mean(roi)) - local_bg)

                bbox = DefectBoundingBox(
                    x=int(x),
                    y=int(y),
                    width=int(bw),
                    height=int(bh),
                    area=float(area),
                    aspect_ratio=float(round(aspect_ratio, 2)),
                    centroid=(round(cx, 2), round(cy, 2)),
                )

                # Geometric & Contrast Classification
                if is_bright:
                    dtype = DefectType.SLUB_KNOT
                    severity = DefectSeverity.MAJOR if area > 80.0 else DefectSeverity.MINOR
                else:
                    # Dark defect: check elongation for yarn break vs puncture/stain
                    if aspect_ratio >= self.aspect_ratio_thresh:
                        if bw > bh:
                            dtype = DefectType.YARN_BREAK_WEFT
                            severity = DefectSeverity.CRITICAL if bw > 75.0 else DefectSeverity.MAJOR
                        else:
                            dtype = DefectType.YARN_BREAK_WARP
                            severity = DefectSeverity.CRITICAL if bh > 75.0 else DefectSeverity.MAJOR
                    else:
                        # Compact or blob dark defect
                        if area >= 220.0 or circularity < 0.35:
                            dtype = DefectType.OIL_STAIN
                            severity = DefectSeverity.CRITICAL if area > 350.0 else DefectSeverity.MAJOR
                        else:
                            dtype = DefectType.HOLE
                            severity = DefectSeverity.CRITICAL if area > 120.0 else DefectSeverity.MAJOR

                conf = min(0.99, max(0.65, 0.70 + (mean_contrast / 100.0) * 0.25))

                detected_defects.append(
                    DetectedDefect(
                        defect_type=dtype,
                        severity=severity,
                        confidence=float(round(conf, 3)),
                        bbox=bbox,
                        mean_contrast=float(round(mean_contrast, 2)),
                    )
                )

        # Run extraction across bright and dark channels
        _extract_contours(mask_wth, is_bright=True)
        _extract_contours(mask_dark, is_bright=False)

        # Roll Decision Logic
        has_critical = any(d.severity == DefectSeverity.CRITICAL for d in detected_defects)
        major_count = sum(1 for d in detected_defects if d.severity == DefectSeverity.MAJOR)

        if has_critical:
            decision = RollDecision.REJECT
        elif major_count > 2:
            decision = RollDecision.REPAIR
        else:
            decision = RollDecision.PASS

        # Aggregate counts
        counts: Dict[str, int] = {}
        for d in detected_defects:
            counts[d.defect_type.value] = counts.get(d.defect_type.value, 0) + 1

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        report = MorphologyInspectionReport(
            image_path=str(image_path),
            resolution=(w, h),
            total_defects=len(detected_defects),
            defect_counts=counts,
            roll_decision=decision,
            processing_time_ms=float(round(elapsed_ms, 2)),
            defects=detected_defects,
        )

        masks = {
            "white_tophat": wth,
            "black_tophat": bth,
            "mask_tophat": mask_wth,
            "mask_blackhat": mask_bth,
            "mask_weft": mask_weft,
            "mask_warp": mask_warp,
        }

        return report, masks

    @staticmethod
    def annotate_defects(
        image_bgr: np.ndarray,
        defects: List[DetectedDefect],
    ) -> np.ndarray:
        """Annotate detected defects on carpet image with color-coded bounding boxes and labels."""
        overlay = image_bgr.copy()

        # Color mapping (BGR)
        color_map = {
            DefectType.HOLE: (0, 0, 230),               # Crimson Red
            DefectType.YARN_BREAK_WEFT: (0, 140, 255),   # Deep Amber
            DefectType.YARN_BREAK_WARP: (0, 200, 255),   # Golden Orange
            DefectType.SLUB_KNOT: (255, 230, 0),         # Bright Cyan
            DefectType.OIL_STAIN: (200, 0, 200),         # Deep Magenta
        }

        for d in defects:
            box = d.bbox
            col = color_map.get(d.defect_type, (0, 255, 0))

            # Semi-transparent rectangle
            cv2.rectangle(overlay, (box.x, box.y), (box.x + box.width, box.y + box.height), col, 2)

            # Label text
            label = f"{d.defect_type.value} [{d.severity.value[:3]}] {d.confidence*100:.0f}%"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)

            y_text = max(th + 4, box.y - 4)
            cv2.rectangle(overlay, (box.x, y_text - th - 3), (box.x + tw + 4, y_text + 2), col, -1)
            cv2.putText(
                overlay,
                label,
                (box.x + 2, y_text - 1),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        return overlay
