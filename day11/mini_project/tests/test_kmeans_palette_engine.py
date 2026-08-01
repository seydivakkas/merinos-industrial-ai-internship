"""Unit tests for Day 11 K-Means Palette Extractor."""

import numpy as np
import pytest
from day11.mini_project.src.kmeans_palette_engine import KMeansPaletteExtractor


def test_kmeans_palette_extraction():
    extractor = KMeansPaletteExtractor(n_colors=3, random_state=42)

    # Synthetic image with 3 distinct regions
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:50, :] = [255, 0, 0]    # Blue (BGR)
    img[50:80, :] = [0, 255, 0]  # Green (BGR)
    img[80:, :] = [0, 0, 255]    # Red (BGR)

    res = extractor.extract_palette(img)

    assert res.k_clusters == 3
    assert len(res.clusters) == 3
    # Check that proportions sum close to 100%
    total_prop = sum(c.proportion_pct for c in res.clusters)
    assert total_prop == pytest.approx(100.0, abs=0.5)
    # Check hex format
    assert all(c.hex_code.startswith("#") for c in res.clusters)
