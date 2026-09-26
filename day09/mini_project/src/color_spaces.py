"""Color Space Conversion and Perceptual Representation Module.

Handles transformation between BGR (OpenCV native), RGB (visualization/PyTorch),
Grayscale, HSV (color thresholding/dye analysis), CIELAB (perceptual color difference),
and YCrCb (luminance-chrominance separation).
"""

from typing import Any
import cv2
import numpy as np


class ColorSpaceError(Exception):
    """Raised when an unsupported or invalid color transformation is requested."""

    pass


class ColorSpaceConverter:
    """Provides validated conversions across industrial color spaces."""

    SUPPORTED_SPACES = ("BGR", "RGB", "GRAY", "HSV", "LAB", "YCrCb")

    @classmethod
    def convert(cls, img: np.ndarray, source: str = "BGR", target: str | None = None) -> np.ndarray:
        """Converts an image array between two supported color spaces.
        
        Supports both:
            - convert(img, "RGB")               [source defaults to BGR]
            - convert(img, "BGR", "RGB")        [explicit source and target]
        """
        if target is None:
            target = source
            source = "BGR"

        src = source.upper()
        tgt = target.upper()

        if src not in cls.SUPPORTED_SPACES:
            raise ColorSpaceError(f"Unsupported source space: {src}. Must be in {cls.SUPPORTED_SPACES}")
        if tgt not in cls.SUPPORTED_SPACES:
            raise ColorSpaceError(f"Unsupported target space: {tgt}. Must be in {cls.SUPPORTED_SPACES}")

        if src == tgt:
            return img.copy()

        # Handle grayscale inputs
        if src == "GRAY":
            if img.ndim != 2 and not (img.ndim == 3 and img.shape[2] == 1):
                raise ColorSpaceError(f"Expected 1-channel image for GRAY source, got shape {img.shape}")
            gray_img = img if img.ndim == 2 else img[:, :, 0]
            if tgt == "BGR":
                return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
            if tgt == "RGB":
                return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2RGB)
            # Intermediate through BGR
            bgr_intermediate = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
            return cls.convert(bgr_intermediate, source="BGR", target=tgt)

        # Multi-channel conversions: Route through BGR as canonical hub if needed
        if src != "BGR":
            to_bgr_code = {
                "RGB": cv2.COLOR_RGB2BGR,
                "HSV": cv2.COLOR_HSV2BGR,
                "LAB": cv2.COLOR_Lab2BGR,
                "YCrCb": cv2.COLOR_YCrCb2BGR,
            }.get(src)
            if to_bgr_code is None:
                raise ColorSpaceError(f"Cannot map {src} to BGR hub.")
            bgr_img = cv2.cvtColor(img, to_bgr_code)
        else:
            bgr_img = img

        if tgt == "BGR":
            return bgr_img

        from_bgr_code = {
            "RGB": cv2.COLOR_BGR2RGB,
            "GRAY": cv2.COLOR_BGR2GRAY,
            "HSV": cv2.COLOR_BGR2HSV,
            "LAB": cv2.COLOR_BGR2Lab,
            "YCrCb": cv2.COLOR_BGR2YCrCb,
        }.get(tgt)

        if from_bgr_code is None:
            raise ColorSpaceError(f"Cannot map BGR to target {tgt}.")

        return cv2.cvtColor(bgr_img, from_bgr_code)

    @classmethod
    def split_channels(cls, img: np.ndarray, space: str = "BGR") -> dict[str, np.ndarray]:
        """Splits an image into named channel arrays according to its color space."""
        sp = space.upper()
        if sp == "GRAY":
            gray_img = img if img.ndim == 2 else img[:, :, 0]
            return {"Y": gray_img}

        if img.ndim != 3 or img.shape[2] != 3:
            raise ColorSpaceError(f"Expected 3-channel image for space {sp}, got shape {img.shape}")

        ch1, ch2, ch3 = cv2.split(img)

        channel_names = {
            "BGR": ("B", "G", "R"),
            "RGB": ("R", "G", "B"),
            "HSV": ("H", "S", "V"),
            "LAB": ("L", "A", "B"),
            "YCrCb": ("Y", "Cr", "Cb"),
        }.get(sp, ("Ch1", "Ch2", "Ch3"))

        return {
            channel_names[0]: ch1,
            channel_names[1]: ch2,
            channel_names[2]: ch3,
        }

    @classmethod
    def channel_statistics(cls, img: np.ndarray, space: str = "BGR") -> dict[str, dict[str, float]]:
        """Computes statistical metrics (mean, std, min, max) for each individual channel."""
        channels = cls.split_channels(img, space)
        stats: dict[str, dict[str, float]] = {}

        for ch_name, ch_arr in channels.items():
            stats[ch_name] = {
                "mean": round(float(np.mean(ch_arr)), 2),
                "std": round(float(np.std(ch_arr)), 2),
                "min": float(np.min(ch_arr)),
                "max": float(np.max(ch_arr)),
            }
        return stats
