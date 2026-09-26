"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Hough Çizgi Dönüşümü Motoru (Probabilistic Hough Lines & Bordür Kümeleme)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from .models import BorderEdge, BorderSide, LineSegment


class HoughLineEngine:
    """Olasılıksal Hough Dönüşümü (PPHT) ile çizgi çıkarımı ve bordür uydurma motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        hough_cfg = self.config.get("hough_transform", {})
        self.rho = float(hough_cfg.get("rho", 1.0))
        self.theta_degrees = float(hough_cfg.get("theta_degrees", 1.0))
        self.threshold = int(hough_cfg.get("threshold", 40))
        self.min_line_length = float(hough_cfg.get("min_line_length", 60.0))
        self.max_line_gap = float(hough_cfg.get("max_line_gap", 15.0))

        border_cfg = self.config.get("border_analysis", {})
        self.margin_fraction = float(border_cfg.get("margin_fraction", 0.22))
        self.tol_horizontal = float(border_cfg.get("angle_tolerance_horizontal_deg", 15.0))
        self.tol_vertical = float(border_cfg.get("angle_tolerance_vertical_deg", 15.0))

    def detect_lines_probabilistic(
        self,
        edge_map: np.ndarray,
        rho: Optional[float] = None,
        theta_degrees: Optional[float] = None,
        threshold: Optional[int] = None,
        min_line_length: Optional[float] = None,
        max_line_gap: Optional[float] = None,
    ) -> List[LineSegment]:
        """İkili kenar haritasından PPHT ile çizgi parçalarını çıkarır."""
        r = rho if rho is not None else self.rho
        th_deg = theta_degrees if theta_degrees is not None else self.theta_degrees
        th = threshold if threshold is not None else self.threshold
        min_len = min_line_length if min_line_length is not None else self.min_line_length
        max_gap = max_line_gap if max_line_gap is not None else self.max_line_gap

        theta_rad = np.deg2rad(th_deg)
        raw_lines = cv2.HoughLinesP(
            edge_map,
            rho=r,
            theta=theta_rad,
            threshold=th,
            minLineLength=min_len,
            maxLineGap=max_gap,
        )

        segments: List[LineSegment] = []
        if raw_lines is None:
            return segments

        for line in raw_lines:
            x1, y1, x2, y2 = line[0]
            dx = float(x2 - x1)
            dy = float(y2 - y1)
            length = float(np.sqrt(dx**2 + dy**2))
            if length < 1e-3:
                continue

            # Açı [-90°, 90°] aralığına normalize edilir
            raw_angle = np.rad2deg(np.arctan2(dy, dx))
            if raw_angle > 90.0:
                norm_angle = raw_angle - 180.0
            elif raw_angle < -90.0:
                norm_angle = raw_angle + 180.0
            else:
                norm_angle = raw_angle

            slope = float(dy / dx) if abs(dx) > 1e-4 else None
            intercept = float(y1 - slope * x1) if slope is not None else None

            segments.append(
                LineSegment(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    length=length,
                    angle_deg=round(float(norm_angle), 3),
                    slope=round(slope, 5) if slope is not None else None,
                    intercept=round(intercept, 2) if intercept is not None else None,
                )
            )

        return segments

    def filter_by_orientation(
        self,
        segments: List[LineSegment],
        orientation: str = "horizontal",
        tolerance_deg: Optional[float] = None,
    ) -> List[LineSegment]:
        """Çizgileri yatay veya dikey açı toleransına göre süzer."""
        filtered: List[LineSegment] = []
        if orientation == "horizontal":
            tol = tolerance_deg if tolerance_deg is not None else self.tol_horizontal
            for seg in segments:
                if abs(seg.angle_deg) <= tol:
                    filtered.append(seg)
        elif orientation == "vertical":
            tol = tolerance_deg if tolerance_deg is not None else self.tol_vertical
            for seg in segments:
                if abs(abs(seg.angle_deg) - 90.0) <= tol:
                    filtered.append(seg)
        else:
            raise ValueError(f"Geçersiz oryantasyon: {orientation}. 'horizontal' veya 'vertical' olmalıdır.")

        return filtered

    def cluster_and_fit_borders(
        self,
        segments: List[LineSegment],
        image_shape: Tuple[int, int],
        margin_fraction: Optional[float] = None,
    ) -> Dict[str, Optional[BorderEdge]]:
        """Hough çizgilerini çeper yakınlıklarına göre TOP, BOTTOM, LEFT, RIGHT bordürlerine atar ve doğruları uydurur."""
        h, w = image_shape[:2]
        margin = margin_fraction if margin_fraction is not None else self.margin_fraction

        y_top_limit = h * margin
        y_bot_limit = h * (1.0 - margin)
        x_left_limit = w * margin
        x_right_limit = w * (1.0 - margin)

        horiz_segments = self.filter_by_orientation(segments, "horizontal")
        vert_segments = self.filter_by_orientation(segments, "vertical")

        top_candidates: List[LineSegment] = []
        bottom_candidates: List[LineSegment] = []
        for s in horiz_segments:
            mid_y = (s.y1 + s.y2) / 2.0
            if mid_y <= y_top_limit:
                top_candidates.append(s)
            elif mid_y >= y_bot_limit:
                bottom_candidates.append(s)

        left_candidates: List[LineSegment] = []
        right_candidates: List[LineSegment] = []
        for s in vert_segments:
            mid_x = (s.x1 + s.x2) / 2.0
            if mid_x <= x_left_limit:
                left_candidates.append(s)
            elif mid_x >= x_right_limit:
                right_candidates.append(s)

        borders: Dict[str, Optional[BorderEdge]] = {
            "TOP": self._fit_single_border(top_candidates, BorderSide.TOP, image_shape),
            "BOTTOM": self._fit_single_border(bottom_candidates, BorderSide.BOTTOM, image_shape),
            "LEFT": self._fit_single_border(left_candidates, BorderSide.LEFT, image_shape),
            "RIGHT": self._fit_single_border(right_candidates, BorderSide.RIGHT, image_shape),
        }
        return borders

    def _fit_single_border(
        self,
        candidates: List[LineSegment],
        side: BorderSide,
        image_shape: Tuple[int, int],
    ) -> Optional[BorderEdge]:
        """Aday segmentler grubuna en küçük kareler regresyonu ile tekil bordür doğrusu uydurur."""
        if not candidates:
            return None

        h, w = image_shape[:2]
        is_horizontal = side in (BorderSide.TOP, BorderSide.BOTTOM)

        # En dış bordür kenarını izole et (iç dekorasyon çizgileri ve kalın bant çift kenarlarını filtrele)
        if is_horizontal:
            mid_coords = [(c.y1 + c.y2) / 2.0 for c in candidates]
            outer_ref = min(mid_coords) if side == BorderSide.TOP else max(mid_coords)
            selected_candidates = [
                c for c, m in zip(candidates, mid_coords) if abs(m - outer_ref) <= 12.0
            ]
        else:
            mid_coords = [(c.x1 + c.x2) / 2.0 for c in candidates]
            outer_ref = min(mid_coords) if side == BorderSide.LEFT else max(mid_coords)
            selected_candidates = [
                c for c, m in zip(candidates, mid_coords) if abs(m - outer_ref) <= 12.0
            ]

        if not selected_candidates:
            selected_candidates = candidates

        # Segmentlerin uç noktalarını ve uzunluk ağırlıklarını çıkar
        pts_list: List[Tuple[float, float]] = []
        weights_list: List[float] = []
        for c in selected_candidates:
            # Segment uzunluğuna orantılı ağırlık
            pts_list.append((c.x1, c.y1))
            pts_list.append((c.x2, c.y2))
            weights_list.append(c.length)
            weights_list.append(c.length)

        pts = np.array(pts_list, dtype=np.float64)
        weights = np.array(weights_list, dtype=np.float64)

        if len(pts) < 2:
            return None

        if is_horizontal:
            # y = m * x + b regresyonu
            x = pts[:, 0]
            y = pts[:, 1]
            poly = np.polyfit(x, y, 1, w=weights)
            slope = float(poly[0])
            intercept = float(poly[1])

            x1 = 0.0
            y1 = float(intercept)
            x2 = float(w - 1)
            y2 = float(slope * (w - 1) + intercept)

            # Açı (derece)
            angle_deg = float(np.rad2deg(np.arctan(slope)))
            fitted_y = slope * x + intercept
            rms_error = float(np.sqrt(np.mean((y - fitted_y) ** 2)))
            mean_coord = float(np.mean(y))

        else:
            # dikey kenar için: x = m * y + b
            x = pts[:, 0]
            y = pts[:, 1]
            poly = np.polyfit(y, x, 1, w=weights)
            slope_inv = float(poly[0])
            intercept_x = float(poly[1])

            y1 = 0.0
            x1 = float(intercept_x)
            y2 = float(h - 1)
            x2 = float(slope_inv * (h - 1) + intercept_x)

            # Dikey açı: 90° ± sapma
            angle_deg = float(90.0 - np.rad2deg(np.arctan(slope_inv)))
            if angle_deg > 90.0:
                angle_deg -= 180.0

            fitted_x = slope_inv * y + intercept_x
            rms_error = float(np.sqrt(np.mean((x - fitted_x) ** 2)))
            mean_coord = float(np.mean(x))

        return BorderEdge(
            side=side,
            x1=round(x1, 2),
            y1=round(y1, 2),
            x2=round(x2, 2),
            y2=round(y2, 2),
            angle_deg=round(angle_deg, 3),
            segment_count=len(candidates),
            straightness_rms=round(rms_error, 3),
            mean_coordinate=round(mean_coord, 2),
        )
