"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Bordür Paralellik ve Çizgi Analiz Motoru (CarpetBorderAnalyzer)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from .edge_operators import EdgeOperatorEngine
from .hough_engine import HoughLineEngine
from .models import (
    BorderEdge,
    BorderParallelismReport,
    EdgeOperatorType,
    LineSegment,
    ParallelismMetric,
    QualityDecision,
)


class CarpetBorderAnalyzer:
    """Kenar tespiti, Hough dönüşümü ve jakarlı halı bordür paralellik analizi motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.edge_engine = EdgeOperatorEngine(self.config)
        self.hough_engine = HoughLineEngine(self.config)

        border_cfg = self.config.get("border_analysis", {})
        self.parallelism_tol = float(border_cfg.get("parallelism_tolerance_deg", 0.50))
        self.orthogonality_tol = float(border_cfg.get("orthogonality_tolerance_deg", 0.75))
        self.max_width_var = float(border_cfg.get("max_width_variance_px", 4.0))
        self.max_rms = float(border_cfg.get("max_straightness_rms_px", 2.5))

        rules = self.config.get("quality_decision_rules", {})
        self.accept_rules = rules.get(
            "accept",
            {
                "max_parallelism_deviation_deg": 0.50,
                "max_orthogonality_deviation_deg": 0.75,
                "max_straightness_rms_px": 2.0,
            },
        )
        self.warning_rules = rules.get(
            "warning",
            {
                "max_parallelism_deviation_deg": 1.20,
                "max_orthogonality_deviation_deg": 1.80,
                "max_straightness_rms_px": 4.0,
            },
        )

    def analyze_carpet(
        self,
        image: np.ndarray,
        edge_method: str = "CANNY",
    ) -> Tuple[BorderParallelismReport, Dict[str, Any]]:
        """Giriş görüntüsünü analiz eder, bordür doğrularını çıkarır ve paralellik raporu üretir."""
        t_start = time.perf_counter()

        if image is None or image.size == 0:
            raise ValueError("Girdi görüntüsü boş olamaz.")

        h, w = image.shape[:2]
        gray = self.edge_engine.preprocess_gray(image, apply_blur=True)

        method_upper = edge_method.upper()
        intermediates: Dict[str, Any] = {"gray": gray}

        if method_upper == EdgeOperatorType.CANNY:
            edge_map = self.edge_engine.compute_canny(gray)
        elif method_upper == EdgeOperatorType.SOBEL:
            res = self.edge_engine.compute_sobel(gray)
            edge_map = (res["magnitude_uint8"] > 40).astype(np.uint8) * 255
            intermediates.update(res)
        elif method_upper == EdgeOperatorType.SCHARR:
            res = self.edge_engine.compute_scharr(gray)
            edge_map = (res["magnitude_uint8"] > 40).astype(np.uint8) * 255
            intermediates.update(res)
        elif method_upper == EdgeOperatorType.LAPLACIAN:
            res = self.edge_engine.compute_laplacian(gray, detect_zero_crossings=True)
            edge_map = res["zero_crossings"]
            intermediates.update(res)
        else:
            raise ValueError(f"Desteklenmeyen kenar metodu: {edge_method}")

        intermediates["edge_map"] = edge_map

        # Hough Çizgi Çıkarımı
        segments = self.hough_engine.detect_lines_probabilistic(edge_map)
        intermediates["segments"] = segments

        # 4 Kenar Bordür Uydurma
        borders = self.hough_engine.cluster_and_fit_borders(segments, (h, w))

        # Paralellik Hesaplamaları
        horiz_metric = self._compute_horizontal_parallelism(borders.get("TOP"), borders.get("BOTTOM"), w)
        vert_metric = self._compute_vertical_parallelism(borders.get("LEFT"), borders.get("RIGHT"), h)

        # Ortogonalite (Diklik 90° Testi)
        ortho_angle, ortho_dev = self._compute_orthogonality(
            borders.get("TOP"), borders.get("BOTTOM"), borders.get("LEFT"), borders.get("RIGHT")
        )

        # Kalite Kararı
        decision, notes = self._evaluate_quality_decision(horiz_metric, vert_metric, ortho_dev, borders)

        t_elapsed = (time.perf_counter() - t_start) * 1000.0

        report = BorderParallelismReport(
            image_shape=(h, w),
            total_lines_detected=len(segments),
            borders=borders,
            horizontal_parallelism=horiz_metric,
            vertical_parallelism=vert_metric,
            orthogonality_angle_deg=round(ortho_angle, 3) if ortho_angle is not None else None,
            orthogonality_deviation_deg=round(ortho_dev, 3) if ortho_dev is not None else None,
            decision=decision,
            decision_notes=notes,
            processing_time_ms=round(t_elapsed, 2),
        )

        return report, intermediates

    def _compute_horizontal_parallelism(
        self,
        top: Optional[BorderEdge],
        bottom: Optional[BorderEdge],
        width: int,
    ) -> Optional[ParallelismMetric]:
        """Üst ve alt bordür arasındaki paralellik ve mesafe varyansını hesaplar."""
        if top is None or bottom is None:
            return None

        angle_diff = abs(top.angle_deg - bottom.angle_deg)
        is_parallel = angle_diff <= self.parallelism_tol

        # x ekseni boyunca 50 noktada dikey mesafe profil analizi
        xs = np.linspace(0, width - 1, 50)
        # y = y1 + (y2 - y1)/(x2 - x1) * x
        top_slope = (top.y2 - top.y1) / max(top.x2 - top.x1, 1e-4)
        bot_slope = (bottom.y2 - bottom.y1) / max(bottom.x2 - bottom.x1, 1e-4)

        y_top_vals = top.y1 + top_slope * xs
        y_bot_vals = bottom.y1 + bot_slope * xs
        distances = y_bot_vals - y_top_vals

        return ParallelismMetric(
            pair_name="TOP-BOTTOM",
            angle_difference_deg=round(float(angle_diff), 3),
            is_parallel=is_parallel,
            distance_min_px=round(float(np.min(distances)), 2),
            distance_max_px=round(float(np.max(distances)), 2),
            distance_mean_px=round(float(np.mean(distances)), 2),
            distance_std_px=round(float(np.std(distances)), 2),
        )

    def _compute_vertical_parallelism(
        self,
        left: Optional[BorderEdge],
        right: Optional[BorderEdge],
        height: int,
    ) -> Optional[ParallelismMetric]:
        """Sol ve sağ bordür arasındaki paralellik ve mesafe varyansını hesaplar."""
        if left is None or right is None:
            return None

        angle_diff = abs(left.angle_deg - right.angle_deg)
        is_parallel = angle_diff <= self.parallelism_tol

        # y ekseni boyunca 50 noktada yatay mesafe profil analizi
        ys = np.linspace(0, height - 1, 50)
        left_slope_inv = (left.x2 - left.x1) / max(left.y2 - left.y1, 1e-4)
        right_slope_inv = (right.x2 - right.x1) / max(right.y2 - right.y1, 1e-4)

        x_left_vals = left.x1 + left_slope_inv * ys
        x_right_vals = right.x1 + right_slope_inv * ys
        distances = x_right_vals - x_left_vals

        return ParallelismMetric(
            pair_name="LEFT-RIGHT",
            angle_difference_deg=round(float(angle_diff), 3),
            is_parallel=is_parallel,
            distance_min_px=round(float(np.min(distances)), 2),
            distance_max_px=round(float(np.max(distances)), 2),
            distance_mean_px=round(float(np.mean(distances)), 2),
            distance_std_px=round(float(np.std(distances)), 2),
        )

    def _compute_orthogonality(
        self,
        top: Optional[BorderEdge],
        bottom: Optional[BorderEdge],
        left: Optional[BorderEdge],
        right: Optional[BorderEdge],
    ) -> Tuple[Optional[float], Optional[float]]:
        """Yatay ve dikey eksenler arasındaki diklik açısını (90°) ve sapmasını hesaplar."""
        h_angles = [b.angle_deg for b in (top, bottom) if b is not None]
        v_angles = [b.angle_deg for b in (left, right) if b is not None]

        if not h_angles or not v_angles:
            return None, None

        mean_h = float(np.mean(h_angles))
        mean_v = float(np.mean(v_angles))

        # Dikey açı 90° civarında, yatay açı 0° civarında
        corner_angle = abs(mean_v - mean_h)
        dev = abs(90.0 - corner_angle)
        return corner_angle, dev

    def _evaluate_quality_decision(
        self,
        h_metric: Optional[ParallelismMetric],
        v_metric: Optional[ParallelismMetric],
        ortho_dev: Optional[float],
        borders: Dict[str, Optional[BorderEdge]],
    ) -> Tuple[QualityDecision, List[str]]:
        """Tüm metrikleri değerlendirerek rulo kabul/uyarı/ret kararını verir."""
        notes: List[str] = []

        # Eksik bordür kontrolü
        missing = [side for side, edge in borders.items() if edge is None]
        if missing:
            notes.append(f"Kritik Hata: Bordür kenarları tespit edilemedi: {', '.join(missing)}")
            return QualityDecision.REJECT, notes

        assert h_metric is not None
        assert v_metric is not None

        max_par_dev = max(h_metric.angle_difference_deg, v_metric.angle_difference_deg)
        od = ortho_dev if ortho_dev is not None else 0.0

        rms_values = [b.straightness_rms for b in borders.values() if b is not None]
        max_rms = max(rms_values) if rms_values else 0.0

        acc_par = self.accept_rules["max_parallelism_deviation_deg"]
        acc_ortho = self.accept_rules["max_orthogonality_deviation_deg"]
        acc_rms = self.accept_rules["max_straightness_rms_px"]

        warn_par = self.warning_rules["max_parallelism_deviation_deg"]
        warn_ortho = self.warning_rules["max_orthogonality_deviation_deg"]
        warn_rms = self.warning_rules["max_straightness_rms_px"]

        if max_par_dev <= acc_par and od <= acc_ortho and max_rms <= acc_rms:
            notes.append(
                f"1. Kalite Bordür: Paralellik sapması ({max_par_dev:.2f}°) <= {acc_par}°, "
                f"Diklik sapması ({od:.2f}°) <= {acc_ortho}°, RMS ({max_rms:.2f} px) <= {acc_rms} px."
            )
            return QualityDecision.ACCEPT, notes

        elif max_par_dev <= warn_par and od <= warn_ortho and max_rms <= warn_rms:
            notes.append(
                f"Şartlı Kabul (UYARI): Paralellik sapması {max_par_dev:.2f}° veya "
                f"Diklik sapması {od:.2f}° tolerans sınırına yakın."
            )
            return QualityDecision.WARNING, notes

        else:
            notes.append(
                f"KALİTE RED (HATA): Paralellik sapması {max_par_dev:.2f}° > {warn_par}° veya "
                f"Diklik sapması {od:.2f}° > {warn_ortho}° limitlerini aştı."
            )
            return QualityDecision.REJECT, notes

    def annotate_borders(
        self,
        image: np.ndarray,
        report: BorderParallelismReport,
        segments: Optional[List[LineSegment]] = None,
    ) -> np.ndarray:
        """Tespit edilen çizgileri, temsilci bordür doğrularını ve HUD metrik panelini görsel üzerine çizer."""
        canvas = image.copy()
        if len(canvas.shape) == 2:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

        h, w = canvas.shape[:2]

        # 1. Ham Hough segmentlerini ince şeffaf çizgi olarak çiz
        if segments:
            for s in segments:
                p1 = (int(round(s.x1)), int(round(s.y1)))
                p2 = (int(round(s.x2)), int(round(s.y2)))
                cv2.line(canvas, p1, p2, (180, 180, 50), 1, cv2.LINE_AA)

        # 2. Temsilci Bordür Doğrularını Çiz
        color_map = {
            QualityDecision.ACCEPT: (0, 220, 0),  # Yeşil
            QualityDecision.WARNING: (0, 165, 255),  # Turuncu
            QualityDecision.REJECT: (0, 0, 230),  # Kırmızı
        }
        edge_color = color_map[report.decision]

        for side_name, border in report.borders.items():
            if border is None:
                continue

            p1 = (int(round(border.x1)), int(round(border.y1)))
            p2 = (int(round(border.x2)), int(round(border.y2)))
            cv2.line(canvas, p1, p2, edge_color, 3, cv2.LINE_AA)

            # Etiket ve açı bilgisi
            mid_x = int((border.x1 + border.x2) / 2.0)
            mid_y = int((border.y1 + border.y2) / 2.0)
            lbl = f"{side_name}: {border.angle_deg:+.2f}° (RMS={border.straightness_rms:.1f}px)"
            cv2.putText(
                canvas,
                lbl,
                (max(mid_x - 90, 10), max(mid_y - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                canvas,
                lbl,
                (max(mid_x - 90, 10), max(mid_y - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        # 3. HUD Bilgi Kutusu Çizimi (Sol Üst)
        hud_w, hud_h = 320, 140
        overlay = canvas.copy()
        cv2.rectangle(overlay, (10, 10), (10 + hud_w, 10 + hud_h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)
        cv2.rectangle(canvas, (10, 10), (10 + hud_w, 10 + hud_h), edge_color, 2)

        cv2.putText(
            canvas,
            f"MERINOS BORDER QA: {report.decision.value}",
            (20, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            edge_color,
            2,
            cv2.LINE_AA,
        )

        h_diff = report.horizontal_parallelism.angle_difference_deg if report.horizontal_parallelism else 0.0
        v_diff = report.vertical_parallelism.angle_difference_deg if report.vertical_parallelism else 0.0
        ortho = report.orthogonality_deviation_deg if report.orthogonality_deviation_deg is not None else 0.0

        lines_info = [
            f"Horiz Delta: {h_diff:.2f}° (Tol: {self.parallelism_tol:.2f}°)",
            f"Vert Delta:  {v_diff:.2f}° (Tol: {self.parallelism_tol:.2f}°)",
            f"Ortho Dev:   {ortho:.2f}° (90° +/- {self.orthogonality_tol:.2f}°)",
            f"Hough Lines: {report.total_lines_detected} | Time: {report.processing_time_ms:.1f}ms",
        ]
        for i, text in enumerate(lines_info):
            cv2.putText(
                canvas,
                text,
                (20, 56 + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (220, 220, 220),
                1,
                cv2.LINE_AA,
            )

        return canvas
