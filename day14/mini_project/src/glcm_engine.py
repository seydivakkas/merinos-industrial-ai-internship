"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Gri Seviye Eş-Oluşum Matrisi (GLCM) ve Haralick Doku Öznitelik Motoru

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, List, Optional
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops

from .models import GLCMFeatures


class GLCMFeatureEngine:
    """Halı kumaş dokusu, iplik sıklığı ve periyodik desen karakterizasyonu için GLCM motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        glcm_cfg = self.config.get("glcm", {})
        
        self.distances = list(glcm_cfg.get("distances", [1, 3, 5]))
        self.angles = list(glcm_cfg.get("angles", [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]))
        self.levels = int(glcm_cfg.get("levels", 64))
        self.symmetric = bool(glcm_cfg.get("symmetric", True))
        self.normed = bool(glcm_cfg.get("normed", True))

    def _preprocess_gray(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü gri seviyeye çevirir ve belirtilen seviye sayısına kuantize eder."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        if len(image.shape) == 3 and image.shape[2] >= 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            gray = image.copy()
        else:
            raise ValueError(f"Geçersiz görüntü şekli: {image.shape}")

        # 256 seviyeyi self.levels (örn: 64) seviyeye kuantize et
        scale = 256 // self.levels
        quantized = (gray // scale).astype(np.uint8)
        quantized = np.clip(quantized, 0, self.levels - 1)
        return quantized

    def extract_features(self, image: np.ndarray) -> GLCMFeatures:
        """Kuantize edilmiş görüntüden GLCM matrisini ve Haralick özniteliklerini çıkarır."""
        quantized = self._preprocess_gray(image)

        # GLCM Hesaplama: Shape = (levels, levels, len(distances), len(angles))
        glcm = graycomatrix(
            quantized,
            distances=self.distances,
            angles=self.angles,
            levels=self.levels,
            symmetric=self.symmetric,
            normed=self.normed,
        )

        # Haralick Özellikleri
        contrast = float(np.mean(graycoprops(glcm, "contrast")))
        dissimilarity = float(np.mean(graycoprops(glcm, "dissimilarity")))
        homogeneity = float(np.mean(graycoprops(glcm, "homogeneity")))
        energy = float(np.mean(graycoprops(glcm, "energy")))
        correlation = float(np.mean(graycoprops(glcm, "correlation")))

        # Yönler arasındaki kontrast varyansı (doku anizotropisi)
        # Sadece mesafe=1 için 4 açıdaki kontrastlar
        contrast_by_angle = graycoprops(glcm, "contrast")[0, :]
        dir_variance = float(np.var(contrast_by_angle))

        # Shannon Entropisi: -sum(p * log2(p))
        eps = 1e-12
        entropy_slices = []
        for d_idx in range(len(self.distances)):
            for a_idx in range(len(self.angles)):
                p = glcm[:, :, d_idx, a_idx]
                p_nz = p[p > eps]
                ent = -np.sum(p_nz * np.log2(p_nz))
                entropy_slices.append(ent)
        mean_entropy = float(np.mean(entropy_slices))

        return GLCMFeatures(
            contrast=round(contrast, 4),
            dissimilarity=round(dissimilarity, 4),
            homogeneity=round(homogeneity, 4),
            energy=round(energy, 4),
            correlation=round(correlation, 4),
            entropy=round(mean_entropy, 4),
            direction_variance=round(dir_variance, 4),
        )

    def to_vector(self, features: GLCMFeatures) -> np.ndarray:
        """GLCM özniteliklerini 7 boyutlu normalize bir vektöre dönüştürür."""
        vec = np.array(
            [
                features.contrast,
                features.dissimilarity,
                features.homogeneity,
                features.energy,
                features.correlation,
                features.entropy,
                features.direction_variance,
            ],
            dtype=np.float32,
        )
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec
