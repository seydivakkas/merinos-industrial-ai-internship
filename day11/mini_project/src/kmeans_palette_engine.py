"""Day 11 - K-Means Dominant Color Palette Extraction for Textile Design.

Uses scikit-learn / OpenCV K-Means to cluster image pixels into K dominant
centroid colors and calculates proportion distribution for industrial jacquard weaving.
"""

from typing import List, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans


class ColorCluster(BaseModel):
    """Represents a dominant color cluster in the carpet pattern."""
    rgb: Tuple[int, int, int]
    hex_code: str
    proportion_pct: float


class DominantPaletteResult(BaseModel):
    """Result of K-Means dominant palette extraction."""
    k_clusters: int
    clusters: List[ColorCluster]


class KMeansPaletteExtractor:
    """Extracts dominant color palettes from textile images using K-Means."""

    def __init__(self, n_colors: int = 5, random_state: int = 42) -> None:
        self.n_colors = n_colors
        self.random_state = random_state

    def extract_palette(self, image_bgr: np.ndarray) -> DominantPaletteResult:
        """Clusters image pixels and returns sorted dominant colors."""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pixels = image_rgb.reshape(-1, 3).astype(np.float32)

        # Downsample for computational speed if image is very large
        if len(pixels) > 50000:
            indices = np.random.RandomState(self.random_state).choice(len(pixels), 50000, replace=False)
            pixels = pixels[indices]

        kmeans = KMeans(n_clusters=self.n_colors, random_state=self.random_state, n_init=5)
        labels = kmeans.fit_predict(pixels)
        centroids = kmeans.cluster_centers_

        counts = np.bincount(labels, minlength=self.n_colors)
        total_count = len(labels)

        clusters: List[ColorCluster] = []
        for idx in range(self.n_colors):
            c_rgb = tuple(int(round(x)) for x in centroids[idx])
            hex_str = f"#{c_rgb[0]:02X}{c_rgb[1]:02X}{c_rgb[2]:02X}"
            prop = round((counts[idx] / total_count) * 100.0, 2)
            clusters.append(ColorCluster(rgb=c_rgb, hex_code=hex_str, proportion_pct=prop))

        # Sort by dominant proportion descending
        clusters.sort(key=lambda c: c.proportion_pct, reverse=True)
        return DominantPaletteResult(k_clusters=self.n_colors, clusters=clusters)
