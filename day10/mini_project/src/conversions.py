"""Color Science Conversion Engine for RGB, HSV, and CIELAB Color Spaces.

Provides high-precision floating-point CIE D65 transformations as well as
fast vectorized OpenCV matrix transformations for carpet image arrays.
"""

from typing import Sequence
import cv2
import numpy as np


class ColorConversionError(Exception):
    """Raised when an invalid color array or triplet is supplied."""

    pass


class ColorConverter:
    """Mathematical color conversions adhering to standard CIE 1931 / CIE 1976 protocols."""

    # CIE standard illuminant D65 reference white point
    D65_WHITE = np.array([0.950489, 1.000000, 1.088840], dtype=np.float64)

    # sRGB to XYZ conversion matrix
    M_SRGB_TO_XYZ = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ],
        dtype=np.float64,
    )

    @staticmethod
    def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
        """Converts a hex color code (e.g. '#1A2B4C') to integer RGB triplet."""
        clean_hex = hex_str.strip().lstrip("#")
        if len(clean_hex) != 6:
            raise ColorConversionError(f"Invalid hex string: {hex_str}. Must have 6 hex digits.")
        try:
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
            return (r, g, b)
        except ValueError as err:
            raise ColorConversionError(f"Invalid hex characters in {hex_str}") from err

    @staticmethod
    def rgb_to_hex(rgb: Sequence[int]) -> str:
        """Converts an RGB integer triplet to uppercase Hex string."""
        if len(rgb) != 3:
            raise ColorConversionError(f"Expected 3 components for RGB, got {len(rgb)}")
        r, g, b = [int(np.clip(c, 0, 255)) for c in rgb]
        return f"#{r:02X}{g:02X}{b:02X}"

    @classmethod
    def rgb_to_cielab_exact(cls, rgb: Sequence[float | int]) -> tuple[float, float, float]:
        """Converts sRGB [0-255] to standard CIELAB (L*: 0-100, a*: -128 to 127, b*: -128 to 127).

        Uses rigorous CIE D65 gamma linearization and non-linear cube root formulation.
        """
        # Step 1: Normalize sRGB to [0, 1]
        srgb = np.array(rgb, dtype=np.float64) / 255.0

        # Step 2: Gamma expansion (linearization)
        linear_rgb = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)

        # Step 3: Linear RGB to XYZ
        xyz = np.dot(cls.M_SRGB_TO_XYZ, linear_rgb)

        # Step 4: XYZ to CIELAB under D65
        xyz_norm = xyz / cls.D65_WHITE
        delta = 6.0 / 29.0
        delta_cubed = delta**3

        def f_t(t: np.ndarray) -> np.ndarray:
            return np.where(t > delta_cubed, np.cbrt(t), (t / (3.0 * delta**2)) + (4.0 / 29.0))

        f_xyz = f_t(xyz_norm)

        l_star = 116.0 * f_xyz[1] - 16.0
        a_star = 500.0 * (f_xyz[0] - f_xyz[1])
        b_star = 200.0 * (f_xyz[1] - f_xyz[2])

        return (round(float(l_star), 2), round(float(a_star), 2), round(float(b_star), 2))

    @classmethod
    def bgr_image_to_cielab_float(cls, img_bgr: np.ndarray) -> np.ndarray:
        """Converts an entire BGR uint8 image array to full-precision standard CIELAB float32.

        L* is in [0, 100], a* is in [-127, 127], b* is in [-127, 127].
        """
        if img_bgr.ndim != 3 or img_bgr.shape[2] != 3:
            raise ColorConversionError(f"Expected 3-channel BGR image, got shape {img_bgr.shape}")

        # Normalize to float32 [0, 1]
        bgr_f = img_bgr.astype(np.float32) / 255.0
        # OpenCV converts float32 BGR directly to standard L* [0, 100], a* [-127, 127], b* [-127, 127]
        lab_f = cv2.cvtColor(bgr_f, cv2.COLOR_BGR2Lab)
        return lab_f

    @classmethod
    def bgr_image_to_hsv(cls, img_bgr: np.ndarray) -> np.ndarray:
        """Converts a BGR uint8 image to HSV uint8 (H: 0-180, S: 0-255, V: 0-255)."""
        if img_bgr.ndim != 3 or img_bgr.shape[2] != 3:
            raise ColorConversionError(f"Expected 3-channel BGR image, got shape {img_bgr.shape}")
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    @classmethod
    def rgb_to_hsv_triplet(cls, rgb: Sequence[int]) -> tuple[int, int, int]:
        """Converts an RGB triplet to OpenCV HSV uint8 triplet (H: 0-180, S: 0-255, V: 0-255)."""
        pixel = np.uint8([[[rgb[2], rgb[1], rgb[0]]]])  # to BGR 1x1
        hsv_pixel = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_pixel[0, 0]
        return (int(h), int(s), int(v))
