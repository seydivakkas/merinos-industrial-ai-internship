"""
Merinos Industrial AI Internship - Day 05
generator.py: Synthetic Carpet Pattern & Matrix Generator
"""

from pathlib import Path
from typing import Tuple, Union
import numpy as np


class CarpetPatternGenerator:
    """Generates synthetic high-resolution carpet matrix tensors and knot grids for benchmarking."""

    @staticmethod
    def generate_rgb_pattern(
        height: int = 512,
        width: int = 512,
        seed: int = 42,
        dtype: np.dtype = np.float32,
    ) -> np.ndarray:
        """
        Generates a synthetic (H, W, 3) RGB carpet pattern with central medallion,
        outer borders, and texture variations.
        """
        rng = np.random.default_rng(seed)

        # Coordinate grids
        y = np.linspace(-1, 1, height, dtype=dtype)[:, None]
        x = np.linspace(-1, 1, width, dtype=dtype)[None, :]
        radius = np.sqrt(x**2 + y**2)

        # 1. Central Medallion (radial harmonic function)
        medallion = np.cos(8 * radius) * np.exp(-2.5 * radius)

        # 2. Geometric border frame (distance to image border)
        border_x = np.minimum(np.arange(width), np.arange(width)[::-1]) / float(width)
        border_y = np.minimum(np.arange(height), np.arange(height)[::-1]) / float(height)
        border_dist = np.minimum(border_x[None, :], border_y[:, None])
        border_pattern = np.sin(30 * border_dist)

        # 3. Base background texture noise
        noise = rng.uniform(0.0, 0.15, size=(height, width)).astype(dtype)

        # Channel composition (Red / Gold / Navy Palette)
        channel_r = 0.5 + 0.35 * medallion + 0.15 * border_pattern + noise
        channel_g = 0.3 + 0.25 * medallion + 0.25 * border_pattern + 0.5 * noise
        channel_b = 0.2 + 0.40 * (1.0 - radius) + 0.10 * border_pattern

        pattern = np.stack([channel_r, channel_g, channel_b], axis=-1)
        # Clip to valid unit range [0.0, 1.0]
        pattern = np.clip(pattern, 0.0, 1.0).astype(dtype)

        return pattern

    @staticmethod
    def generate_knot_grid(
        height: int = 512,
        width: int = 512,
        knot_range: Tuple[float, float] = (500.0, 900.0),
        seed: int = 42,
        dtype: np.dtype = np.float32,
    ) -> np.ndarray:
        """
        Generates an (H, W) float32 matrix simulating knot density per dm^2 across loom warp/weft.
        """
        rng = np.random.default_rng(seed)
        low, high = knot_range
        base = rng.uniform(low, high, size=(height, width)).astype(dtype)
        return base

    @classmethod
    def generate_and_save_fixtures(cls, output_path: Union[str, Path]) -> Path:
        """Generates small, medium, and large patterns and saves them as a compressed .npz fixture."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        p_small = cls.generate_rgb_pattern(128, 128, seed=101)
        p_medium = cls.generate_rgb_pattern(512, 512, seed=102)
        p_large = cls.generate_rgb_pattern(1024, 1024, seed=103)

        k_small = cls.generate_knot_grid(128, 128, seed=201)
        k_medium = cls.generate_knot_grid(512, 512, seed=202)

        np.savez_compressed(
            path,
            pattern_small=p_small,
            pattern_medium=p_medium,
            pattern_large=p_large,
            knot_grid_small=k_small,
            knot_grid_medium=k_medium,
        )
        return path


if __name__ == "__main__":
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
    fixture_file = fixtures_dir / "synthetic_patterns.npz"
    CarpetPatternGenerator.generate_and_save_fixtures(fixture_file)
    print(f"Fixture saved successfully at: {fixture_file}")
