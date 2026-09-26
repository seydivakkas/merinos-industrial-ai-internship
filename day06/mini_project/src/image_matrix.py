"""Day 06 - Carpet Image Matrix Manipulations.

Provides NumPy routines for creating synthetic carpet pattern patches,
performing multi-axis slicing, patch extraction, and energy computation.
"""

from __future__ import annotations

from typing import List
import numpy as np


class ImageMatrixToolkit:
    """Manipulates image matrices using direct NumPy strides and views."""

    @staticmethod
    def generate_synthetic_carpet_patch(
        height: int = 128,
        width: int = 128,
        pattern_freq: float = 8.0,
        seed: int = 42,
    ) -> np.ndarray:
        """Generates a synthetic woven pattern matrix using trigonometric grids."""
        rng = np.random.default_rng(seed)
        y = np.linspace(0, pattern_freq * np.pi, height, dtype=np.float32)
        x = np.linspace(0, pattern_freq * np.pi, width, dtype=np.float32)
        xx, yy = np.meshgrid(x, y)

        # Simulated warp and weft weave pattern
        warp = np.sin(xx)
        weft = np.cos(yy)
        weave = (warp * weft + 1.0) * 0.5 * 200.0  # Range [0, 200]
        noise = rng.normal(0, 10, size=(height, width)).astype(np.float32)

        patch = np.clip(weave + noise, 0, 255).astype(np.uint8)
        return patch

    @staticmethod
    def slice_patches(image: np.ndarray, patch_size: int = 32) -> List[np.ndarray]:
        """Slices an image matrix into a list of non-overlapping subpatches."""
        h, w = image.shape[:2]
        patches = []
        for r in range(0, h - patch_size + 1, patch_size):
            for c in range(0, w - patch_size + 1, patch_size):
                patch = image[r : r + patch_size, c : c + patch_size]
                patches.append(patch)
        return patches

    @staticmethod
    def compute_patch_energy(patch: np.ndarray) -> float:
        """Computes root-mean-square energy of an image patch."""
        float_patch = patch.astype(np.float64)
        return float(np.sqrt(np.mean(float_patch ** 2)))
