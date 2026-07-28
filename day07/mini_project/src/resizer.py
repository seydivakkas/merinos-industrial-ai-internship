"""Aspect-Ratio Preserving Resizer and Interpolation Engine.

Provides industrial letterbox resizing with symmetric padding to avoid geometric
distortion of carpet medallions, borders, and yarn density during deep learning
model pre-processing.
"""

from dataclasses import dataclass
from typing import Literal
import cv2
import numpy as np


@dataclass
class ResizeResult:
    """Detailed output from letterbox resizing operation."""

    image: np.ndarray
    scale: float
    pad_top: int
    pad_bottom: int
    pad_left: int
    pad_right: int
    original_shape: tuple[int, int]
    target_shape: tuple[int, int]
    interpolation: str


class AspectPreservingResizer:
    """Industrial image resizer that guarantees aspect-ratio preservation."""

    INTERPOLATION_MAP = {
        "nearest": cv2.INTER_NEAREST,
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC,
        "area": cv2.INTER_AREA,
        "lanczos4": cv2.INTER_LANCZOS4,
    }

    @classmethod
    def letterbox(
        cls,
        img: np.ndarray,
        target_size: tuple[int, int] = (512, 512),
        pad_color: tuple[int, int, int] | int = (0, 0, 0),
        interpolation: str = "auto",
    ) -> ResizeResult:
        """Resizes an image into target_size (target_h, target_w) preserving aspect ratio.

        Adds symmetric border padding around the scaled content.
        """
        if img.ndim not in (2, 3):
            raise ValueError(f"Invalid image array shape: {img.shape}")

        orig_h, orig_w = img.shape[:2]
        target_h, target_w = target_size

        if orig_h <= 0 or orig_w <= 0 or target_h <= 0 or target_w <= 0:
            raise ValueError("Dimensions must be positive integers.")

        # Compute scaling factor
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = max(1, int(round(orig_w * scale)))
        new_h = max(1, int(round(orig_h * scale)))

        # Select appropriate interpolation if 'auto'
        if interpolation.lower() == "auto":
            interp_name = "area" if scale < 1.0 else "cubic"
        else:
            interp_name = interpolation.lower()

        interp_flag = cls.INTERPOLATION_MAP.get(interp_name)
        if interp_flag is None:
            raise ValueError(
                f"Unknown interpolation: {interpolation}. Allowed: {list(cls.INTERPOLATION_MAP.keys())}"
            )

        # Step 1: Scale content
        scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp_flag)

        # Step 2: Compute symmetric padding offsets
        pad_w = target_w - new_w
        pad_h = target_h - new_h

        pad_top = pad_h // 2
        pad_bottom = pad_h - pad_top
        pad_left = pad_w // 2
        pad_right = pad_w - pad_left

        # Step 3: Apply padding
        border_color = pad_color if img.ndim == 3 else (pad_color[0] if isinstance(pad_color, tuple) else pad_color)
        padded_img = cv2.copyMakeBorder(
            scaled_img,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            borderType=cv2.BORDER_CONSTANT,
            value=border_color,
        )

        return ResizeResult(
            image=padded_img,
            scale=scale,
            pad_top=pad_top,
            pad_bottom=pad_bottom,
            pad_left=pad_left,
            pad_right=pad_right,
            original_shape=(orig_h, orig_w),
            target_shape=(target_h, target_w),
            interpolation=interp_name,
        )

    @classmethod
    def stretch_resize(
        cls,
        img: np.ndarray,
        target_size: tuple[int, int] = (512, 512),
        interpolation: str = "linear",
    ) -> np.ndarray:
        """Directly scales image without padding (warning: changes aspect ratio)."""
        target_h, target_w = target_size
        interp_flag = cls.INTERPOLATION_MAP.get(interpolation.lower(), cv2.INTER_LINEAR)
        return cv2.resize(img, (target_w, target_h), interpolation=interp_flag)
