import cv2
import numpy as np
from typing import List, Tuple, Optional


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Dört köşe noktasını centroid'e göre sıralayarak
    TL, TR, BR, BL formatında döndürür.
    Args:
        pts: (4, 2) köşe noktaları
    Returns:
        np.ndarray: (4, 2) sıralı noktalar [TL, TR, BR, BL]
    """
    pts = np.asarray(pts, dtype=np.float32).reshape(4, 2)
    centroid = np.mean(pts, axis=0)

    def angle_from_center(p):
        return np.arctan2(p[1] - centroid[1], p[0] - centroid[0])

    angles = [angle_from_center(p) for p in pts]
    sorted_pts = [p for _, p in sorted(zip(angles, pts))]
    # TL, TR, BR, BL sırasına getir
    rect = np.zeros((4, 2), dtype=np.float32)
    rect[0] = sorted_pts[0]  # TL (en küçük açı)
    rect[1] = sorted_pts[1]  # TR
    rect[2] = sorted_pts[2]  # BR
    rect[3] = sorted_pts[3]  # BL
    return rect


class CornerDetector:
    def __init__(
        self,
        canny_low: int = 50,
        canny_high: int = 150,
        blur_kernel: Tuple[int, int] = (5, 5),
        morph_kernel_size: Tuple[int, int] = (5, 5),
        min_area_ratio: float = 0.15,
        approx_epsilon_ratio: float = 0.02,
    ):
        self.canny_low = canny_low
        self.canny_high = canny_high
        self.blur_kernel = blur_kernel
        self.morph_kernel_size = morph_kernel_size
        self.min_area_ratio = min_area_ratio
        self.approx_epsilon_ratio = approx_epsilon_ratio

    def detect_corners(self, image_bgr: np.ndarray) -> Optional[np.ndarray]:
        """
        Görüntüdeki halı dörtgeninin köşe noktalarını tespit eder.
        """
        # 1. Gri tona çevir ve Gaussian blur uygula
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # 2. Kenar tespiti
        edges = cv2.Canny(blur, 50, 150)
        # 3. Konturları bul
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 4. En büyük dörtgen konturu bul
        candidate_quad = None
        max_area = 0
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > max_area:
                    max_area = area
                    candidate_quad = approx.reshape(4, 2)
        if candidate_quad is not None:
            return order_points(candidate_quad)

        # Endüstriyel gürültülü ve konveyörlü ortamlar için çok aşamalı fallback
        h, w = image_bgr.shape[:2]
        total_area = float(h * w)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        for (low, high) in [(10, 35), (20, 60), (30, 100), (10, 80)]:
            e = cv2.Canny(blur, low, high)
            closed = cv2.morphologyEx(e, cv2.MORPH_CLOSE, kernel, iterations=3)
            c_list, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not c_list:
                continue

            sorted_cnts = sorted(c_list, key=cv2.contourArea, reverse=True)
            for cnt in sorted_cnts:
                area = cv2.contourArea(cnt)
                if area < self.min_area_ratio * total_area:
                    continue

                peri = cv2.arcLength(cnt, True)
                for eps in [0.02, 0.025, 0.03, 0.04]:
                    app = cv2.approxPolyDP(cnt, eps * peri, True)
                    if len(app) == 4 and cv2.isContourConvex(app):
                        return order_points(app.reshape(4, 2))

                # Convex hull yaklaşımı
                hull = cv2.convexHull(cnt)
                h_peri = cv2.arcLength(hull, True)
                for eps in [0.02, 0.025, 0.03]:
                    app = cv2.approxPolyDP(hull, eps * h_peri, True)
                    if len(app) == 4 and cv2.isContourConvex(app):
                        return order_points(app.reshape(4, 2))

        # En büyük konturun minimum alan sınırlayıcısı
        if contours:
            largest = sorted(contours, key=cv2.contourArea, reverse=True)[0]
            rect = cv2.minAreaRect(largest)
            box = cv2.boxPoints(rect)
            return order_points(box.astype(np.float32))

        return None

    def draw_corners_overlay(
        self,
        image_bgr: np.ndarray,
        corners: np.ndarray,
    ) -> np.ndarray:
        """Köşeleri işaretlenmiş görüntüyü üretir (Şekil 19 ve Şekil 20 standardı)."""
        overlay = image_bgr.copy()
        pts = corners.astype(np.int32)

        # Renkler: TL=Kırmızı, TR=Yeşil, BR=Mavi, BL=Sarı (BGR formatında)
        colors = [
            (0, 0, 255),    # TL - Kırmızı
            (0, 255, 0),    # TR - Yeşil
            (255, 0, 0),    # BR - Mavi
            (0, 255, 255),  # BL - Sarı
        ]
        labels = ["TL", "TR", "BR", "BL"]

        # Çerçeve çizgileri
        for i in range(4):
            pt1 = tuple(pts[i])
            pt2 = tuple(pts[(i + 1) % 4])
            cv2.line(overlay, pt1, pt2, (0, 255, 0), 2, cv2.LINE_AA)

        # Köşe noktaları ve etiketler
        for i in range(4):
            pt = tuple(pts[i])
            cv2.circle(overlay, pt, 8, colors[i], -1, cv2.LINE_AA)
            cv2.circle(overlay, pt, 10, (255, 255, 255), 1, cv2.LINE_AA)
            ox = 10 if "R" in labels[i] else -32
            oy = -10 if "T" in labels[i] else 25
            cv2.putText(
                overlay,
                labels[i],
                (pt[0] + ox, pt[1] + oy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                colors[i],
                2,
                cv2.LINE_AA,
            )

        return overlay
