"""Comprehensive Carpet Color Composition and Dye Lot Inspection Engine."""

from pathlib import Path
from typing import Any
import cv2
import numpy as np

from day08.mini_project.src.color_models import (
    DyeLotInspectionReport,
    QAGrade,
    YarnColor,
    YarnSegmentationResult,
)
from day08.mini_project.src.conversions import ColorConverter
from day08.mini_project.src.delta_e import DeltaECalculator
from day08.mini_project.src.thresholding import (
    HSVColorThresholder,
    MaskMorphologyCleaner,
    PerceptualDeltaEThresholder,
)


class CarpetColorAnalyzer:
    """End-to-end analyzer for yarn color composition and dye lot drift detection."""

    def __init__(self, palette: list[YarnColor] | None = None):
        self.palette = palette or self.get_default_palette()

    @classmethod
    def get_default_palette(cls) -> list[YarnColor]:
        """Provides default Merinos corporate yarn palette."""
        return [
            YarnColor(
                name="Royal Navy",
                code="YARN-NAVY-01",
                hex_code="#1A2B4C",
                rgb=(26, 43, 76),
                bgr=(76, 43, 26),
                lab=(17.7, 5.0, -22.4),
                hsv_lower=(105, 100, 20),
                hsv_upper=(125, 255, 120),
            ),
            YarnColor(
                name="Imperial Red",
                code="YARN-RED-02",
                hex_code="#8B0000",
                rgb=(139, 0, 0),
                bgr=(0, 0, 139),
                lab=(28.1, 51.0, 41.3),
                hsv_lower=(0, 140, 40),
                hsv_upper=(10, 255, 220),
                hsv_lower2=(170, 140, 40),
                hsv_upper2=(180, 255, 220),
            ),
            YarnColor(
                name="Silk Cream",
                code="YARN-CREAM-03",
                hex_code="#F5F2EB",
                rgb=(245, 242, 235),
                bgr=(235, 242, 245),
                lab=(95.4, -0.2, 3.7),
                hsv_lower=(0, 0, 180),
                hsv_upper=(180, 45, 255),
            ),
            YarnColor(
                name="Antique Gold",
                code="YARN-GOLD-04",
                hex_code="#D4AF37",
                rgb=(212, 175, 55),
                bgr=(55, 175, 212),
                lab=(72.8, 1.3, 62.9),
                hsv_lower=(20, 140, 120),
                hsv_upper=(35, 255, 255),
            ),
        ]

    def analyze_carpet(
        self,
        img_bgr: np.ndarray,
        carpet_name: str = "Carpet_Sample",
        method: str = "hsv",
        delta_e_tolerance: float = 14.0,
    ) -> tuple[DyeLotInspectionReport, dict[str, np.ndarray]]:
        """Segments all reference yarn colors, analyzes dye lot drift, and computes area ratios.

        Returns:
            (report, masks_dict): structured QA report and dictionary of binary yarn masks.
        """
        h, w = img_bgr.shape[:2]
        total_pixels = h * w
        combined_classified_mask = np.zeros((h, w), dtype=np.uint8)

        findings: list[YarnSegmentationResult] = []
        masks: dict[str, np.ndarray] = {}
        lab_img_f = ColorConverter.bgr_image_to_cielab_float(img_bgr)

        worst_delta_e = 0.0
        overall_status = QAGrade.PASS

        for yarn in self.palette:
            if method.lower() == "hsv" and yarn.hsv_lower and yarn.hsv_upper:
                raw_mask = HSVColorThresholder.create_mask(
                    img_bgr,
                    lower=yarn.hsv_lower,
                    upper=yarn.hsv_upper,
                    lower2=yarn.hsv_lower2,
                    upper2=yarn.hsv_upper2,
                )
            else:
                raw_mask, _ = PerceptualDeltaEThresholder.create_mask(
                    img_bgr,
                    target_lab=yarn.lab,
                    tolerance_delta_e=delta_e_tolerance,
                )

            # Clean mask
            clean_mask = MaskMorphologyCleaner.clean(raw_mask)
            masks[yarn.name] = clean_mask

            pixel_count = int(np.count_nonzero(clean_mask))
            area_pct = round((pixel_count / total_pixels) * 100.0, 2)
            combined_classified_mask = cv2.bitwise_or(combined_classified_mask, clean_mask)

            # Compute observed mean color
            if pixel_count > 0:
                mean_b = float(np.mean(img_bgr[:, :, 0][clean_mask > 0]))
                mean_g = float(np.mean(img_bgr[:, :, 1][clean_mask > 0]))
                mean_r = float(np.mean(img_bgr[:, :, 2][clean_mask > 0]))
                mean_rgb = (round(mean_r, 1), round(mean_g, 1), round(mean_b, 1))

                mean_l = float(np.mean(lab_img_f[:, :, 0][clean_mask > 0]))
                mean_a = float(np.mean(lab_img_f[:, :, 1][clean_mask > 0]))
                mean_b_lab = float(np.mean(lab_img_f[:, :, 2][clean_mask > 0]))
                mean_lab = (round(mean_l, 2), round(mean_a, 2), round(mean_b_lab, 2))

                diff = DeltaECalculator.calculate_delta_e_cie76(yarn.lab, mean_lab)
                yarn_delta_e = diff.delta_e
                yarn_grade = diff.grade
            else:
                mean_rgb = (0.0, 0.0, 0.0)
                mean_lab = (0.0, 0.0, 0.0)
                yarn_delta_e = 0.0
                yarn_grade = QAGrade.PASS

            if yarn_delta_e > worst_delta_e:
                worst_delta_e = yarn_delta_e

            # Overall status escalates: PASS -> WARNING -> REJECT
            if yarn_grade == QAGrade.REJECT:
                overall_status = QAGrade.REJECT
            elif yarn_grade == QAGrade.WARNING and overall_status != QAGrade.REJECT:
                overall_status = QAGrade.WARNING

            findings.append(
                YarnSegmentationResult(
                    yarn_name=yarn.name,
                    yarn_code=yarn.code,
                    pixel_count=pixel_count,
                    area_percentage=area_pct,
                    mean_rgb=mean_rgb,
                    mean_lab=mean_lab,
                    delta_e_from_target=yarn_delta_e,
                    grade=yarn_grade,
                )
            )

        unclassified_pixels = total_pixels - int(np.count_nonzero(combined_classified_mask))
        unclass_pct = max(0.0, round((unclassified_pixels / total_pixels) * 100.0, 2))

        report = DyeLotInspectionReport(
            carpet_name=carpet_name,
            total_pixels=total_pixels,
            overall_status=overall_status,
            max_delta_e=round(worst_delta_e, 3),
            yarn_findings=findings,
            unclassified_percentage=unclass_pct,
        )

        return report, masks
