"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Segmentasyon Doğrulama ve Metrik Değerlendirme Motoru (SegmentationEvaluator)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Tuple
import cv2
import numpy as np

from .models import EvaluationMetrics


class SegmentationEvaluator:
    """İki segmentasyon maskesi arasındaki piksel ve sınır örtüşme metriklerini hesaplayan değerlendirici."""

    @staticmethod
    def compute_iou(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
        """Intersection over Union (Jaccard İndeksi) hesaplar."""
        p_bool = pred_mask > 0
        g_bool = gt_mask > 0

        intersection = np.logical_and(p_bool, g_bool).sum()
        union = np.logical_or(p_bool, g_bool).sum()

        if union == 0:
            return 1.0 if intersection == 0 else 0.0

        return float(intersection / union)

    @staticmethod
    def compute_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
        """Dice Katsayısı (F1 Skoru) hesaplar."""
        p_bool = pred_mask > 0
        g_bool = gt_mask > 0

        intersection = np.logical_and(p_bool, g_bool).sum()
        total_positives = p_bool.sum() + g_bool.sum()

        if total_positives == 0:
            return 1.0

        return float(2.0 * intersection / total_positives)

    @staticmethod
    def compute_pixel_accuracy(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
        """Tüm görüntü üzerinde piksel doğruluk oranını ((TP+TN)/Total) hesaplar."""
        p_bool = pred_mask > 0
        g_bool = gt_mask > 0
        correct = np.equal(p_bool, g_bool).sum()
        return float(correct / p_bool.size)

    @staticmethod
    def compute_precision_recall(pred_mask: np.ndarray, gt_mask: np.ndarray) -> Tuple[float, float]:
        """Ön plan sınıfı için Precision ve Recall metriklerini hesaplar."""
        p_bool = pred_mask > 0
        g_bool = gt_mask > 0

        tp = np.logical_and(p_bool, g_bool).sum()
        fp = np.logical_and(p_bool, ~g_bool).sum()
        fn = np.logical_and(~p_bool, g_bool).sum()

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 1.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 1.0

        return precision, recall

    @staticmethod
    def compute_boundary_f1(
        pred_mask: np.ndarray,
        gt_mask: np.ndarray,
        tolerance_px: int = 2,
    ) -> float:
        """Sınır kontur örtüşme F1 skorunu (Boundary F1 / BF-Score) hesaplar."""
        p_bin = (pred_mask > 0).astype(np.uint8) * 255
        g_bin = (gt_mask > 0).astype(np.uint8) * 255

        # Morfolojik gradyan ile 1 piksel kalınlığında kontur sınırları
        k_bound = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        p_bound = cv2.morphologyEx(p_bin, cv2.MORPH_GRADIENT, k_bound) > 0
        g_bound = cv2.morphologyEx(g_bin, cv2.MORPH_GRADIENT, k_bound) > 0

        p_count = p_bound.sum()
        g_count = g_bound.sum()

        if p_count == 0 and g_count == 0:
            return 1.0
        if p_count == 0 or g_count == 0:
            return 0.0

        # Tolerans genişletmesi
        k_tol = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * tolerance_px + 1, 2 * tolerance_px + 1))
        p_bound_dilated = cv2.dilate(p_bound.astype(np.uint8), k_tol) > 0
        g_bound_dilated = cv2.dilate(g_bound.astype(np.uint8), k_tol) > 0

        # Hassasiyet: Tahmin sınırının GT tolerans havuzuna düşme oranı
        prec_b = float(np.logical_and(p_bound, g_bound_dilated).sum() / p_count)
        # Duyarlılık: GT sınırının tahmin tolerans havuzuna düşme oranı
        rec_b = float(np.logical_and(g_bound, p_bound_dilated).sum() / g_count)

        if (prec_b + rec_b) <= 1e-6:
            return 0.0

        bf_score = float(2.0 * prec_b * rec_b / (prec_b + rec_b))
        return bf_score

    def evaluate_all(
        self,
        pred_mask: np.ndarray,
        gt_mask: np.ndarray,
        tolerance_px: int = 2,
    ) -> EvaluationMetrics:
        """Tüm doğruluk metriklerini hesaplar ve Pydantic modeli döndürür."""
        iou = self.compute_iou(pred_mask, gt_mask)
        dice = self.compute_dice(pred_mask, gt_mask)
        acc = self.compute_pixel_accuracy(pred_mask, gt_mask)
        prec, rec = self.compute_precision_recall(pred_mask, gt_mask)
        bf = self.compute_boundary_f1(pred_mask, gt_mask, tolerance_px=tolerance_px)

        return EvaluationMetrics(
            iou=round(iou, 4),
            dice=round(dice, 4),
            pixel_accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            boundary_f1=round(bf, 4),
        )
