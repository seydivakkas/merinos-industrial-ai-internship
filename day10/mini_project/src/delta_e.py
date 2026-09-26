"""CIE 1976 Delta E Perceptual Color Difference Engine.

Implements the standard CIE76 Euclidean distance in CIELAB color space,
providing industrial tolerance grading (PASS, WARNING, REJECT) for Merinos yarn dyeing.
"""

from typing import Sequence
import numpy as np

from day10.mini_project.src.color_models import ColorDifferenceResult, QAGrade


class DeltaECalculator:
    """Calculates perceptual color differences and QA compliance grades."""

    # Default industry thresholds for textile yarn dyeing
    PASS_THRESHOLD = 2.0
    WARNING_THRESHOLD = 5.0

    @classmethod
    def calculate_delta_e_cie76(
        cls,
        lab1: Sequence[float],
        lab2: Sequence[float],
        pass_thresh: float = PASS_THRESHOLD,
        warn_thresh: float = WARNING_THRESHOLD,
    ) -> ColorDifferenceResult:
        """Calculates scalar CIE 1976 Delta E between two CIELAB triplets.

        Delta E = sqrt((Delta L*)^2 + (Delta a*)^2 + (Delta b*)^2)
        """
        l1, a1, b1 = float(lab1[0]), float(lab1[1]), float(lab1[2])
        l2, a2, b2 = float(lab2[0]), float(lab2[1]), float(lab2[2])

        dl = l2 - l1
        da = a2 - a1
        db = b2 - b1

        delta_e = float(np.sqrt(dl**2 + da**2 + db**2))

        # Determine QA Grade
        if delta_e < pass_thresh:
            grade = QAGrade.PASS
            interpretation = "İnsan gözüyle algılanamaz / Mükemmel endüstriyel parti uyumu."
        elif delta_e < warn_thresh:
            grade = QAGrade.WARNING
            interpretation = "Gözle fark edilebilir ton kayması; tezgâh veya boya banyosu uyarısı."
        else:
            grade = QAGrade.REJECT
            interpretation = "Kabul edilemez ton farkı; iplik boyama partisi reddedildi."

        return ColorDifferenceResult(
            delta_e=round(delta_e, 3),
            delta_l=round(dl, 3),
            delta_a=round(da, 3),
            delta_b=round(db, 3),
            grade=grade,
            interpretation=interpretation,
        )

    @classmethod
    def pairwise_delta_e_image(
        cls,
        lab_image: np.ndarray,
        target_lab: Sequence[float],
    ) -> np.ndarray:
        """Computes a 2D map of Delta E values across an entire image array against a target LAB color.

        Args:
            lab_image: float32 CIELAB image array of shape (H, W, 3).
            target_lab: triplet [L*, a*, b*].

        Returns:
            delta_e_map: 2D float32 array of shape (H, W).
        """
        target = np.array(target_lab, dtype=np.float32).reshape(1, 1, 3)
        diff = lab_image - target
        delta_e_map = np.sqrt(np.sum(diff**2, axis=-1))
        return delta_e_map.astype(np.float32)
