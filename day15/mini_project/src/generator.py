"""Synthetic Test Fixture Generator for Merinos Vision CLI Toolkit (Day 15).

Generates four realistic industrial test carpets:
1. perfect_carpet.png -> Flawless production sample (expected ACCEPT)
2. defective_carpet.png -> Carpet with holes and yarn breaks (expected REJECT)
3. skewed_carpet.png -> Carpet with warped perspective / border skew (expected REJECT/WARNING)
4. faded_carpet.png -> Color-drifted / washed-out yarn carpet (expected WARNING/REJECT)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import cv2
import numpy as np

from day15.mini_project.src.toolkit import safe_write_image


class VisionToolkitFixtureGenerator:
    """Generates synthetic carpet samples for testing the Day 15 CLI toolkit."""

    def __init__(self, size: Tuple[int, int] = (600, 600)) -> None:
        self.width, self.height = size

    def _draw_base_jacquard_carpet(
        self,
        base_color: Tuple[int, int, int] = (32, 0, 128),  # Deep Burgundy in BGR
        border_color: Tuple[int, int, int] = (55, 175, 212),  # Gold in BGR
        motif_color: Tuple[int, int, int] = (220, 245, 245),  # Cream in BGR
        dark_accent: Tuple[int, int, int] = (51, 40, 28),  # Charcoal in BGR
    ) -> np.ndarray:
        """Create a multi-layered jacquard carpet pattern."""
        img = np.full((self.height, self.width, 3), base_color, dtype=np.uint8)

        # Micro-texture (simulating wool yarn weave)
        noise = np.random.normal(0, 4, (self.height, self.width, 3)).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Outer border flush with carpet perimeter
        cv2.rectangle(img, (0, 0), (self.width, self.height), border_color, 36)
        cv2.rectangle(img, (36, 36), (self.width - 36, self.height - 36), dark_accent, 4)

        # Central Medallion (layered smooth motif)
        cx, cy = self.width // 2, self.height // 2
        cv2.circle(img, (cx, cy), 130, motif_color, -1)

        return img

    def create_perfect_carpet(self) -> np.ndarray:
        """Create a flawless carpet sample adhering to all Merinos QA tolerances."""
        return self._draw_base_jacquard_carpet()

    def create_defective_carpet(self) -> np.ndarray:
        """Create a carpet with simulated yarn breaks, holes, and slub knots."""
        img = self._draw_base_jacquard_carpet()

        # 4 distinct localized defects clearly isolated outside the central medallion
        cv2.circle(img, (100, 200), 6, (255, 255, 255), -1)
        cv2.circle(img, (500, 200), 6, (255, 255, 255), -1)
        cv2.circle(img, (100, 400), 6, (255, 255, 255), -1)
        cv2.circle(img, (500, 400), 6, (255, 255, 255), -1)

        return img

    def create_skewed_carpet(self) -> np.ndarray:
        """Create a carpet with perspective warp / optical camera alignment skew."""
        img = self._draw_base_jacquard_carpet()

        # Source coordinates
        src_pts = np.float32([[0, 0], [self.width, 0], [self.width, self.height], [0, self.height]])

        # Skewed target coordinates (simulating a tilted inspection camera)
        dst_pts = np.float32(
            [
                [45, 30],  # Top-left pulled inwards
                [self.width - 25, 15],  # Top-right slightly rotated
                [self.width - 55, self.height - 20],  # Bottom-right skewed
                [15, self.height - 40],  # Bottom-left distorted
            ]
        )

        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        skewed = cv2.warpPerspective(img, matrix, (self.width, self.height), borderValue=(20, 20, 20))
        return skewed

    def create_faded_carpet(self) -> np.ndarray:
        """Create a carpet with severe dye batch color drift (high Delta-E)."""
        # Distort the base colors (substituting deep burgundy with faded pastel lavender)
        img = self._draw_base_jacquard_carpet(
            base_color=(190, 150, 170),
            border_color=(130, 210, 140),
            motif_color=(100, 100, 180),
        )
        return img

    def generate_all_fixtures(
        self, output_dir: Optional[Union[str, Path]] = None
    ) -> Dict[str, Union[np.ndarray, Path]]:
        """Generate and optionally save all 4 test fixtures.

        Returns:
            Dict mapping fixture name to either file Path (if saved) or np.ndarray
        """
        fixtures = {
            "perfect_carpet": self.create_perfect_carpet(),
            "defective_carpet": self.create_defective_carpet(),
            "skewed_carpet": self.create_skewed_carpet(),
            "faded_carpet": self.create_faded_carpet(),
        }

        if output_dir is not None:
            out_path = Path(output_dir).resolve()
            out_path.mkdir(parents=True, exist_ok=True)
            saved_paths: Dict[str, Path] = {}
            for name, img in fixtures.items():
                file_path = out_path / f"{name}.png"
                safe_write_image(file_path, img)
                saved_paths[name] = file_path
            return saved_paths

        return fixtures
