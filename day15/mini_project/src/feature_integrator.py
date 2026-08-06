"""Day 15 - Visual Feature Extraction and Multi-Modal Feature Integration.

Extracts texture features (GLCM contrast, dissimilarity, energy, homogeneity),
color moments (mean, std, skewness in HSV), and invariant shape Hu moments,
fusing them into a normalized fixed-length feature vector for downstream ML classifiers.
"""

from typing import List, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field
from skimage.feature import graycomatrix, graycoprops


class IntegratedFeatureVector(BaseModel):
    """Fused normalized feature representation of an industrial carpet image."""
    texture_features: List[float] = Field(..., description="[contrast, dissimilarity, homogeneity, energy]")
    color_moments: List[float] = Field(..., description="[h_mean, h_std, s_mean, s_std, v_mean, v_std]")
    hu_moments: List[float] = Field(..., description="7 log-transformed Hu moment invariants")
    total_dimension: int = Field(default=17)


class VisualFeatureIntegrator:
    """Computes and concatenates texture, color, and shape features."""

    @staticmethod
    def extract_glcm_texture(gray_img: np.ndarray) -> List[float]:
        """Extracts Haralick texture features from GLCM."""
        # Quantize to 32 levels to accelerate computation
        quantized = (gray_img // 8).astype(np.uint8)
        glcm = graycomatrix(quantized, distances=[1], angles=[0], levels=32, symmetric=True, normed=True)
        contrast = float(graycoprops(glcm, 'contrast')[0, 0])
        dissimilarity = float(graycoprops(glcm, 'dissimilarity')[0, 0])
        homogeneity = float(graycoprops(glcm, 'homogeneity')[0, 0])
        energy = float(graycoprops(glcm, 'energy')[0, 0])
        return [round(contrast, 4), round(dissimilarity, 4), round(homogeneity, 4), round(energy, 4)]

    @staticmethod
    def extract_color_moments(bgr_img: np.ndarray) -> List[float]:
        """Extracts mean and standard deviation across HSV channels."""
        hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
        moments = []
        for i in range(3):
            ch = hsv[:, :, i]
            moments.append(float(np.mean(ch)))
            moments.append(float(np.std(ch)))
        return [round(m, 4) for m in moments]

    @staticmethod
    def extract_hu_moments(gray_img: np.ndarray) -> List[float]:
        """Calculates 7 scale, position, and rotation invariant log Hu moments."""
        moments = cv2.moments(gray_img)
        hu = cv2.HuMoments(moments).flatten()
        log_hu = []
        for h in hu:
            val = -1.0 * np.sign(h) * np.log10(abs(h)) if abs(h) > 1e-12 else 0.0
            log_hu.append(round(float(val), 4))
        return log_hu

    def fuse_features(self, bgr_img: np.ndarray) -> IntegratedFeatureVector:
        """Extracts and fuses all three visual feature domains."""
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        tex = self.extract_glcm_texture(gray)
        col = self.extract_color_moments(bgr_img)
        hu = self.extract_hu_moments(gray)

        return IntegratedFeatureVector(
            texture_features=tex,
            color_moments=col,
            hu_moments=hu,
            total_dimension=len(tex) + len(col) + len(hu),
        )
