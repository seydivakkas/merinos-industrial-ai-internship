"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Segmentasyon Kıyaslama Laboratuvarı Motoru (SegmentationBenchmarkEngine)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import time
from typing import Any, Dict, Optional, Tuple
import cv2
import numpy as np

from .evaluator import SegmentationEvaluator
from .grabcut_segmenter import GrabCutSegmenter
from .models import (
    AlgorithmBenchmarkResult,
    CarpetSegmentationReport,
    EvaluationMetrics,
    SegmentationMethod,
)
from .otsu_segmenter import OtsuSegmenter
from .watershed_segmenter import WatershedSegmenter


class SegmentationBenchmarkEngine:
    """Otsu, Watershed ve GrabCut algoritmalarını hız ve doğruluk yönünden kıyaslayan motor."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.otsu_engine = OtsuSegmenter(self.config)
        self.watershed_engine = WatershedSegmenter(self.config)
        self.grabcut_engine = GrabCutSegmenter(self.config)
        self.evaluator = SegmentationEvaluator()

    def run_benchmark(
        self,
        image: np.ndarray,
        gt_mask: Optional[np.ndarray] = None,
        iterations: int = 10,
    ) -> Tuple[CarpetSegmentationReport, Dict[str, np.ndarray]]:
        """Üç segmentasyon algoritmasını çalıştırır, sürelerini ve metriklerini kıyaslar."""
        h, w = image.shape[:2]
        masks: Dict[str, np.ndarray] = {}
        benchmarks: Dict[str, AlgorithmBenchmarkResult] = {}

        # -------------------------------------------------------------
        # 1. Otsu Global Segmentasyon
        # -------------------------------------------------------------
        for _ in range(3):
            self.otsu_engine.segment_global(image)
        t0 = time.perf_counter()
        otsu_mask = None
        for _ in range(iterations):
            otsu_mask, _ = self.otsu_engine.segment_global(image)
        t_otsu = (time.perf_counter() - t0) / iterations * 1000.0
        fps_otsu = 1000.0 / t_otsu if t_otsu > 0 else 0.0

        masks[SegmentationMethod.OTSU.value] = otsu_mask
        otsu_metrics = self.evaluator.evaluate_all(otsu_mask, gt_mask) if gt_mask is not None else None
        cov_otsu = float((otsu_mask > 0).sum() / otsu_mask.size) * 100.0

        benchmarks[SegmentationMethod.OTSU.value] = AlgorithmBenchmarkResult(
            method=SegmentationMethod.OTSU,
            latency_ms=round(t_otsu, 3),
            fps=round(fps_otsu, 1),
            metrics=otsu_metrics,
            foreground_coverage_pct=round(cov_otsu, 2),
        )

        # -------------------------------------------------------------
        # 2. Watershed Segmentasyon
        # -------------------------------------------------------------
        for _ in range(3):
            self.watershed_engine.segment(image)
        t0 = time.perf_counter()
        ws_mask = None
        for _ in range(iterations):
            ws_mask, _, _ = self.watershed_engine.segment(image)
        t_ws = (time.perf_counter() - t0) / iterations * 1000.0
        fps_ws = 1000.0 / t_ws if t_ws > 0 else 0.0

        masks[SegmentationMethod.WATERSHED.value] = ws_mask
        ws_metrics = self.evaluator.evaluate_all(ws_mask, gt_mask) if gt_mask is not None else None
        cov_ws = float((ws_mask > 0).sum() / ws_mask.size) * 100.0

        benchmarks[SegmentationMethod.WATERSHED.value] = AlgorithmBenchmarkResult(
            method=SegmentationMethod.WATERSHED,
            latency_ms=round(t_ws, 3),
            fps=round(fps_ws, 1),
            metrics=ws_metrics,
            foreground_coverage_pct=round(cov_ws, 2),
        )

        # -------------------------------------------------------------
        # 3. GrabCut Segmentasyon
        # -------------------------------------------------------------
        gc_iters = max(1, min(iterations, 3))  # GrabCut ağırdır, 3 tekrar yeterlidir
        for _ in range(1):
            self.grabcut_engine.segment_with_rect(image, iterations=3)
        t0 = time.perf_counter()
        gc_mask = None
        for _ in range(gc_iters):
            gc_mask, _ = self.grabcut_engine.segment_with_rect(image, iterations=3)
        t_gc = (time.perf_counter() - t0) / gc_iters * 1000.0
        fps_gc = 1000.0 / t_gc if t_gc > 0 else 0.0

        masks[SegmentationMethod.GRABCUT.value] = gc_mask
        gc_metrics = self.evaluator.evaluate_all(gc_mask, gt_mask) if gt_mask is not None else None
        cov_gc = float((gc_mask > 0).sum() / gc_mask.size) * 100.0

        benchmarks[SegmentationMethod.GRABCUT.value] = AlgorithmBenchmarkResult(
            method=SegmentationMethod.GRABCUT,
            latency_ms=round(t_gc, 3),
            fps=round(fps_gc, 1),
            metrics=gc_metrics,
            foreground_coverage_pct=round(cov_gc, 2),
        )

        # -------------------------------------------------------------
        # 4. Rapor ve Karar Önerisi
        # -------------------------------------------------------------
        notes = [
            f"Otsu Eşikleme: Ultra hızlı ({t_otsu:.2f} ms, {fps_otsu:.0f} FPS), ancak doku gradyanlarına duyarlıdır.",
            f"Watershed: Hızlı ({t_ws:.2f} ms, {fps_ws:.0f} FPS), mesafe dönüşümü ile tohumlama yaparak sınırları iyi ayırır.",
            f"GrabCut: En yüksek sınır hassasiyeti (GMM optimizasyonu), ancak yüksek işlem süresi ({t_gc:.2f} ms).",
        ]

        report = CarpetSegmentationReport(
            image_shape=(h, w),
            evaluated_methods=[SegmentationMethod.OTSU, SegmentationMethod.WATERSHED, SegmentationMethod.GRABCUT],
            results=benchmarks,
            recommended_online_method=SegmentationMethod.WATERSHED,
            recommended_offline_method=SegmentationMethod.GRABCUT,
            industrial_notes=notes,
        )

        return report, masks

    @staticmethod
    def create_comparison_grid(
        image: np.ndarray,
        masks: Dict[str, np.ndarray],
        gt_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Orijinal görsel, GT ve algoritmaların maskelerini yan yana gösteren karşılaştırma paneli oluşturur."""
        h, w = image.shape[:2]
        canvas_h = h
        target_w = w

        panels = []

        # 1. Orijinal Görsel
        bgr = image if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        p1 = bgr.copy()
        cv2.putText(p1, "ORIJINAL HALI", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        panels.append(p1)

        # 2. GT Maske (Varsa)
        if gt_mask is not None:
            gt_bgr = cv2.cvtColor(gt_mask, cv2.COLOR_GRAY2BGR)
            cv2.putText(gt_bgr, "GROUND TRUTH", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            panels.append(gt_bgr)

        # 3. Yöntem Maskeleri ve Kontur Overlayleri
        colors = {
            "OTSU": (255, 100, 0),      # Mavi
            "WATERSHED": (0, 200, 255), # Sarı
            "GRABCUT": (50, 220, 50),   # Yeşil
        }

        for name, mask in masks.items():
            overlay = bgr.copy()
            # Konturları çiz
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            color = colors.get(name, (0, 0, 255))
            cv2.drawContours(overlay, contours, -1, color, 2)
            cv2.putText(overlay, f"METOD: {name}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            panels.append(overlay)

        grid = np.hstack(panels)
        return grid
