"""
K-Means kullanarak görüntüden baskın renk paleti çıkarma modülü.
Merinos - Industrial AI Internship (Day 09)
"""

import time
from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
import cv2
from PIL import Image
from sklearn.cluster import MiniBatchKMeans, KMeans

from .color_models import ExtractedColor, PaletteExtractionResult
from .ciede2000 import bgr_to_cielab_float, cielab_to_bgr_uint8


class KMeansPaletteExtractor:
    """Görüntüden K-Means ile baskın renk paleti çıkaran sınıf."""

    def __init__(
        self,
        n_colors: int = 8,
        random_state: int = 42,
        default_k: Optional[int] = None,
        color_space: str = "LAB",
        subsample_size: int = 15000,
        use_minibatch: bool = False,
    ):
        self.n_colors = default_k if default_k is not None else n_colors
        self.default_k = self.n_colors
        self.random_state = random_state
        self.color_space = color_space.upper()
        self.subsample_size = subsample_size
        self.use_minibatch = use_minibatch

    def extract_palette(
        self,
        image: Union[Image.Image, np.ndarray],
        k: Optional[int] = None,
        color_space: Optional[str] = None,
    ) -> Union[Tuple[np.ndarray, np.ndarray], PaletteExtractionResult]:
        """Görüntüden K-Means kullanarak baskın renk paletini çıkarır.

        Args:
            image: PIL Image (RGB) veya BGR np.ndarray
            k: Küme sayısı (isteğe bağlı, varsayılan: self.n_colors)
            color_space: 'LAB' veya 'RGB' (isteğe bağlı, varsayılan: self.color_space)

        Returns:
            image PIL Image ise:
                palette: (n_colors, 3) RGB renkleri [0-255]
                labels: Her piksel için küme etiketi
            image np.ndarray ise:
                PaletteExtractionResult nesnesi (palette, labels olarak da açılabilir)
        """
        target_k = k if k is not None else self.n_colors

        # PIL Image formatında doğrudan Şekil 17 akışı
        if isinstance(image, Image.Image):
            img = image.convert("RGB")
            data = np.array(img).reshape(-1, 3)

            # K-Means ile kümeleme
            kmeans = KMeans(n_clusters=target_k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(data)
            palette = kmeans.cluster_centers_.astype(np.uint8)

            return palette, labels

        # np.ndarray formatında tam endüstriyel CIELAB / sRGB analiz akışı
        start_time = time.perf_counter()
        image_bgr = image
        space = (color_space or self.color_space).upper()

        if space not in ("LAB", "RGB"):
            raise ValueError(f"Unsupported color space: {space}. Must be 'LAB' or 'RGB'.")

        h, w, _ = image_bgr.shape
        total_pixels = h * w

        # Prepare feature array based on requested space
        if space == "LAB":
            lab_img = bgr_to_cielab_float(image_bgr)
            flat_features = lab_img.reshape(-1, 3).astype(np.float64)
        else:
            rgb_img = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            flat_features = (rgb_img.reshape(-1, 3).astype(np.float64)) / 255.0

        # Subsampling for fast cluster initialization & fitting
        if total_pixels > self.subsample_size and self.subsample_size > 0:
            rng = np.random.default_rng(self.random_state)
            sample_idx = rng.choice(total_pixels, size=self.subsample_size, replace=False)
            fit_features = flat_features[sample_idx]
            sample_ratio = self.subsample_size / total_pixels
        else:
            fit_features = flat_features
            sample_ratio = 1.0

        # Fit K-Means model
        if self.use_minibatch and fit_features.shape[0] > 50000:
            kmeans = MiniBatchKMeans(
                n_clusters=target_k,
                random_state=self.random_state,
                batch_size=2048,
                n_init=3,
                max_iter=300,
            )
        else:
            kmeans = KMeans(
                n_clusters=target_k,
                random_state=self.random_state,
                n_init=5,
                max_iter=300,
            )

        kmeans.fit(fit_features)

        # Full image label assignment
        labels = kmeans.predict(flat_features)
        cluster_counts = np.bincount(labels, minlength=target_k)

        # Sort clusters by dominance (descending pixel count)
        sorted_indices = np.argsort(-cluster_counts)

        extracted_colors: List[ExtractedColor] = []
        centroids = kmeans.cluster_centers_

        for rank, cluster_idx in enumerate(sorted_indices):
            count = int(cluster_counts[cluster_idx])
            percentage = round(float((count / total_pixels) * 100.0), 3)
            center = centroids[cluster_idx]

            if space == "LAB":
                cielab_val = [round(float(center[0]), 2), round(float(center[1]), 2), round(float(center[2]), 2)]
                # Convert LAB centroid back to sRGB uint8
                center_lab_mat = np.array([[center]], dtype=np.float32)
                bgr_mat = cielab_to_bgr_uint8(center_lab_mat)
                rgb_val = [int(bgr_mat[0, 0, 2]), int(bgr_mat[0, 0, 1]), int(bgr_mat[0, 0, 0])]
            else:
                # Features were normalized RGB in [0, 1]
                rgb_uint8 = np.clip(center * 255.0, 0, 255).astype(np.uint8)
                rgb_val = [int(rgb_uint8[0]), int(rgb_uint8[1]), int(rgb_uint8[2])]
                # Convert sRGB to CIELAB
                rgb_mat = np.array([[rgb_uint8]], dtype=np.uint8)
                bgr_mat = cv2.cvtColor(rgb_mat, cv2.COLOR_RGB2BGR)
                lab_mat = bgr_to_cielab_float(bgr_mat)
                cielab_val = [round(float(lab_mat[0, 0, 0]), 2), round(float(lab_mat[0, 0, 1]), 2), round(float(lab_mat[0, 0, 2]), 2)]

            extracted_colors.append(
                ExtractedColor(
                    cluster_id=rank,
                    rgb=rgb_val,
                    cielab=cielab_val,
                    percentage=percentage,
                    pixel_count=count,
                )
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return PaletteExtractionResult(
            k=target_k,
            space_used=space,
            palette=extracted_colors,
            inertia=float(kmeans.inertia_),
            sample_ratio=round(sample_ratio, 4),
            total_pixels=total_pixels,
            elapsed_ms=elapsed_ms,
        )

    def find_optimal_k(
        self,
        image_bgr: np.ndarray,
        k_range: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Run Elbow curve analysis across a range of K values to find optimal cluster count."""
        candidates = k_range or [3, 4, 5, 6, 7, 8, 10]
        results = []

        for k in candidates:
            res = self.extract_palette(image_bgr, k=k)
            results.append({
                "k": k,
                "inertia": round(res.inertia, 2),
                "elapsed_ms": res.elapsed_ms,
            })

        return results
