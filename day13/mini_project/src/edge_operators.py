"""
Kenar tespit operatörleri
Sentetik halı görüntüleri üzerinde farklı kenar tespit yöntemlerini
uygulamak için yardımcı fonksiyonlar.
"""

from typing import Any, Dict, Optional, Tuple
import cv2
import numpy as np


def compute_sobel(image: np.ndarray) -> np.ndarray:
    """Sobel kenar tespiti uygular."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad = cv2.magnitude(sobelx, sobely)
    grad = np.uint8(np.clip(grad, 0, 255))
    return grad


def compute_scharr(image: np.ndarray) -> np.ndarray:
    """Scharr kenar tespiti uygular."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    scharrx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    scharry = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    grad = cv2.magnitude(scharrx, scharry)
    grad = np.uint8(np.clip(grad, 0, 255))
    return grad


def compute_laplacian(image: np.ndarray) -> np.ndarray:
    """Laplacian kenar tespiti uygular."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap = np.uint8(np.absolute(lap))
    return lap


def compute_canny(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
    """Canny kenar tespiti uygular."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    return edges


class EdgeOperatorEngine:
    """1. ve 2. derece gradyan operatörlerini ve Canny algoritmasını çalıştıran motor."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        edge_cfg = self.config.get("edge_operators", {})
        self.blur_cfg = edge_cfg.get("gaussian_blur", {"ksize": [5, 5], "sigma": 1.2})
        self.sobel_cfg = edge_cfg.get("sobel", {"ksize": 3, "scale": 1.0, "delta": 0.0})
        self.scharr_cfg = edge_cfg.get("scharr", {"scale": 1.0, "delta": 0.0})
        self.laplacian_cfg = edge_cfg.get("laplacian", {"ksize": 3, "scale": 1.0, "delta": 0.0})
        self.canny_cfg = edge_cfg.get(
            "canny",
            {"low_threshold": 50, "high_threshold": 150, "aperture_size": 3, "l2_gradient": True},
        )

    def preprocess_gray(self, image: np.ndarray, apply_blur: bool = True) -> np.ndarray:
        """Giriş görüntüsünü tek kanallı gri seviyeye ve isteğe bağlı Gauss yumuşatmasına dönüştürür."""
        if image is None or image.size == 0:
            raise ValueError("Girdi görüntüsü boş olamaz.")

        if len(image.shape) == 3 and image.shape[2] >= 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            gray = image.copy()
        else:
            raise ValueError(f"Desteklenmeyen görüntü boyutu: {image.shape}")

        if apply_blur:
            ksize = tuple(self.blur_cfg.get("ksize", [5, 5]))
            sigma = float(self.blur_cfg.get("sigma", 1.2))
            if ksize[0] > 1 and ksize[1] > 1:
                gray = cv2.GaussianBlur(gray, ksize, sigmaX=sigma, sigmaY=sigma)

        return gray

    def compute_sobel(
        self,
        gray: np.ndarray,
        ksize: Optional[int] = None,
        scale: Optional[float] = None,
        delta: Optional[float] = None,
    ) -> Dict[str, np.ndarray]:
        """Sobel 1. derece türev operatörünü uygular ($G_x, G_y, |G|, \\theta$)."""
        k = ksize if ksize is not None else self.sobel_cfg.get("ksize", 3)
        s = scale if scale is not None else self.sobel_cfg.get("scale", 1.0)
        d = delta if delta is not None else self.sobel_cfg.get("delta", 0.0)

        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k, scale=s, delta=d)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k, scale=s, delta=d)

        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        # Yön açısı: [-180°, 180°]
        direction_deg = np.rad2deg(np.arctan2(grad_y, grad_x))

        max_val = np.max(magnitude)
        if max_val > 1e-6:
            magnitude_uint8 = np.clip((magnitude / max_val) * 255.0, 0, 255).astype(np.uint8)
        else:
            magnitude_uint8 = np.zeros_like(gray, dtype=np.uint8)

        return {
            "grad_x": grad_x,
            "grad_y": grad_y,
            "magnitude": magnitude,
            "magnitude_uint8": magnitude_uint8,
            "direction_deg": direction_deg,
        }

    def compute_scharr(
        self,
        gray: np.ndarray,
        scale: Optional[float] = None,
        delta: Optional[float] = None,
    ) -> Dict[str, np.ndarray]:
        """Yüksek rotasyonel izotropili Scharr 1. derece gradyan operatörünü uygular."""
        s = scale if scale is not None else self.scharr_cfg.get("scale", 1.0)
        d = delta if delta is not None else self.scharr_cfg.get("delta", 0.0)

        grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0, scale=s, delta=d)
        grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1, scale=s, delta=d)

        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        direction_deg = np.rad2deg(np.arctan2(grad_y, grad_x))

        max_val = np.max(magnitude)
        if max_val > 1e-6:
            magnitude_uint8 = np.clip((magnitude / max_val) * 255.0, 0, 255).astype(np.uint8)
        else:
            magnitude_uint8 = np.zeros_like(gray, dtype=np.uint8)

        return {
            "grad_x": grad_x,
            "grad_y": grad_y,
            "magnitude": magnitude,
            "magnitude_uint8": magnitude_uint8,
            "direction_deg": direction_deg,
        }

    def compute_laplacian(
        self,
        gray: np.ndarray,
        ksize: Optional[int] = None,
        scale: Optional[float] = None,
        delta: Optional[float] = None,
        detect_zero_crossings: bool = True,
        zc_threshold: float = 12.0,
    ) -> Dict[str, np.ndarray]:
        """İkinci derece Laplacian/LoG operatörünü ve sıfır geçişi (zero-crossing) kenarlarını hesaplar."""
        k = ksize if ksize is not None else self.laplacian_cfg.get("ksize", 3)
        s = scale if scale is not None else self.laplacian_cfg.get("scale", 1.0)
        d = delta if delta is not None else self.laplacian_cfg.get("delta", 0.0)

        lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=k, scale=s, delta=d)
        abs_lap = np.abs(lap)

        max_val = np.max(abs_lap)
        if max_val > 1e-6:
            lap_uint8 = np.clip((abs_lap / max_val) * 255.0, 0, 255).astype(np.uint8)
        else:
            lap_uint8 = np.zeros_like(gray, dtype=np.uint8)

        zero_crossings = np.zeros_like(gray, dtype=np.uint8)
        if detect_zero_crossings:
            # 4-bağlantılı komşulukta zıt işaretli ve eşiği aşan geçişler
            h, w = lap.shape
            # Yatay komşular
            diff_h = lap[:, 1:] * lap[:, :-1]
            mag_h = np.abs(lap[:, 1:] - lap[:, :-1])
            zc_h = (diff_h < 0) & (mag_h >= zc_threshold)
            zero_crossings[:, :-1] |= (zc_h * 255).astype(np.uint8)

            # Dikey komşular
            diff_v = lap[1:, :] * lap[:-1, :]
            mag_v = np.abs(lap[1:, :] - lap[:-1, :])
            zc_v = (diff_v < 0) & (mag_v >= zc_threshold)
            zero_crossings[:-1, :] |= (zc_v * 255).astype(np.uint8)

        return {
            "laplacian_float": lap,
            "laplacian_uint8": lap_uint8,
            "zero_crossings": zero_crossings,
        }

    def compute_canny(
        self,
        gray: np.ndarray,
        low_threshold: Optional[int] = None,
        high_threshold: Optional[int] = None,
        aperture_size: Optional[int] = None,
        l2_gradient: Optional[bool] = None,
    ) -> np.ndarray:
        """Canny çok aşamalı optimal kenar tespiti algoritmasını çalıştırır."""
        low = low_threshold if low_threshold is not None else self.canny_cfg.get("low_threshold", 50)
        high = high_threshold if high_threshold is not None else self.canny_cfg.get("high_threshold", 150)
        aperture = aperture_size if aperture_size is not None else self.canny_cfg.get("aperture_size", 3)
        l2 = l2_gradient if l2_gradient is not None else self.canny_cfg.get("l2_gradient", True)

        edges = cv2.Canny(gray, low, high, apertureSize=aperture, L2gradient=l2)
        return edges

    @staticmethod
    def create_color_orientation_map(
        grad_x: np.ndarray,
        grad_y: np.ndarray,
        magnitude: Optional[np.ndarray] = None,
        min_magnitude_thresh: float = 20.0,
    ) -> np.ndarray:
        """Gradyan yönünü (Hue) ve büyüklüğünü (Value) renk kodlayan BGR görsel üretir."""
        if magnitude is None:
            magnitude = np.sqrt(grad_x**2 + grad_y**2)

        angle = np.arctan2(grad_y, grad_x)  # [-pi, pi]
        angle_deg = np.rad2deg(angle) % 180.0  # [0, 180)

        # OpenCV HSV uzayı: H in [0, 180], S in [0, 255], V in [0, 255]
        h_channel = angle_deg.astype(np.uint8)
        s_channel = np.full_like(h_channel, 255, dtype=np.uint8)

        max_mag = np.max(magnitude)
        if max_mag > 1e-6:
            v_channel = np.clip((magnitude / max_mag) * 255.0, 0, 255).astype(np.uint8)
        else:
            v_channel = np.zeros_like(h_channel, dtype=np.uint8)

        # Eşiğin altındaki gürültüyü siyaha çek
        v_channel[magnitude < min_magnitude_thresh] = 0

        hsv = cv2.merge([h_channel, s_channel, v_channel])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return bgr
