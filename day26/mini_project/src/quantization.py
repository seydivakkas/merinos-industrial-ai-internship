"""
Merinos Industrial AI Internship - Day 26
Vector Quantization: Scalar Quantization (SQ8) & Product Quantization (PQ)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import Tuple, List, Optional
import numpy as np


class ScalarQuantizer:
    """
    32-bit Kayan Noktalı (Float32) vektörleri 8-bit tamsayılara (Uint8/Int8) dönüştürerek
    %75 (%75 = 1 - 8/32) bellek tasarrufu sağlayan Skaler Kuantizasyon (SQ8) motoru.
    
    Dönüşüm Formülü:
        q = round((x - min_val) / (max_val - min_val) * 255)
    Ters Dönüşüm (Dequantization):
        x_recon = q * scale + min_val
        burada scale = (max_val - min_val) / 255.0
    """

    def __init__(self, quantile: float = 0.99):
        self.quantile = quantile
        self.scales: Optional[np.ndarray] = None
        self.offsets: Optional[np.ndarray] = None
        self.is_fitted: bool = False

    def fit(self, vectors: np.ndarray) -> "ScalarQuantizer":
        """Vektör matrisi üzerinden ölçek ve ofset parametrelerini hesaplar."""
        if vectors.ndim != 2:
            raise ValueError("Vektörler 2-boyutlu matris olmalıdır (N x D).")

        # Her vektör için min ve max sınırları (veya global quantile sınırları)
        # Vektör bazlı (per-vector) kuantizasyon yüksek doğruluk sağlar
        min_vals = np.min(vectors, axis=1, keepdims=True)
        max_vals = np.max(vectors, axis=1, keepdims=True)

        diff = max_vals - min_vals
        diff[diff == 0] = 1e-7  # Sıfıra bölme engeli

        self.scales = diff / 255.0
        self.offsets = min_vals
        self.is_fitted = True
        return self

    def quantize(self, vectors: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Float32 vektörleri uint8 dizisine sıkıştırır."""
        min_vals = np.min(vectors, axis=1, keepdims=True)
        max_vals = np.max(vectors, axis=1, keepdims=True)
        diff = max_vals - min_vals
        diff[diff == 0] = 1e-7

        scales = (diff / 255.0).astype(np.float32)
        offsets = min_vals.astype(np.float32)
        self.scales = scales
        self.offsets = offsets

        normalized = (vectors - offsets) / scales
        quantized = np.clip(np.round(normalized), 0, 255).astype(np.uint8)

        return quantized, scales, offsets

    def dequantize(
        self,
        quantized_vectors: np.ndarray,
        scales: Optional[np.ndarray] = None,
        offsets: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Uint8 kuantize vektörleri yeniden Float32 uzayına dönüştürür."""
        if scales is None:
            scales = self.scales
        if offsets is None:
            offsets = self.offsets
        reconstructed = quantized_vectors.astype(np.float32) * scales + offsets
        # Vektör normunu normalize et
        norms = np.linalg.norm(reconstructed, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return reconstructed / norms

    def compute_asymmetric_cosine_distances(
        self,
        query_vector: np.ndarray,
        quantized_vectors: np.ndarray,
        scales: Optional[np.ndarray] = None,
        offsets: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Asimetrik Mesafe Hesaplama (Asymmetric Distance Computation - ADC):
        Sorgu float32 kalır, veritabanı vektörleri kuantize durumdan hızlıca çözülerek
        kosinüs benzerliği hesaplanır.
        """
        reconstructed = self.dequantize(quantized_vectors, scales, offsets)
        # Normalize sorgu ve rekonstrükte vektörler için nokta çarpımı kosinüs benzerliğidir
        q_norm = query_vector / (np.linalg.norm(query_vector) + 1e-9)
        similarities = np.dot(reconstructed, q_norm)
        return similarities


class ProductQuantizer:
    """
    Vektör uzayını M adet alt-uzaya bölerek her alt-uzayda k-means kümelemesi ile
    kod defteri (codebook) oluşturan Ürün Kuantizasyonu (PQ) motoru.
    """

    def __init__(
        self,
        num_subvectors: int = 8,
        num_clusters: int = 16,
        n_subspaces: Optional[int] = None,
        n_clusters: Optional[int] = None,
        random_state: int = 42
    ):
        self.num_subvectors = n_subspaces if n_subspaces is not None else num_subvectors
        self.num_clusters = n_clusters if n_clusters is not None else num_clusters
        self.n_subspaces = self.num_subvectors
        self.n_clusters = self.num_clusters
        self.random_state = random_state
        self._codebooks: Optional[np.ndarray] = None
        self.subvector_dim: int = 0

    @property
    def sub_dim(self) -> int:
        return self.subvector_dim

    @property
    def codebooks(self) -> Optional[np.ndarray]:
        return self._codebooks

    def fit(self, vectors: np.ndarray) -> "ProductQuantizer":
        """Alt-uzaylar için centroid kod defterlerini eğitir."""
        n_samples, dim = vectors.shape
        if dim % self.num_subvectors != 0:
            raise ValueError(f"Boyut ({dim}), alt-vektör sayısına ({self.num_subvectors}) tam bölünmelidir.")

        self.subvector_dim = dim // self.num_subvectors
        c_list = []

        from sklearn.cluster import MiniBatchKMeans

        for m in range(self.num_subvectors):
            start = m * self.subvector_dim
            end = (m + 1) * self.subvector_dim
            sub_vecs = vectors[:, start:end]

            n_c = min(self.num_clusters, n_samples)
            kmeans = MiniBatchKMeans(n_clusters=n_c, random_state=self.random_state, batch_size=64, n_init=3)
            kmeans.fit(sub_vecs)
            c_list.append(kmeans.cluster_centers_.astype(np.float32))

        self._codebooks = np.array(c_list)
        return self

    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """Vektörleri kod defteri indekslerine dönüştürür (N x M uint8)."""
        if self._codebooks is None:
            raise RuntimeError("PQ henüz eğitilmedi (fit çağrılmalı).")

        n_samples = vectors.shape[0]
        codes = np.zeros((n_samples, self.num_subvectors), dtype=np.uint8)

        for m in range(self.num_subvectors):
            start = m * self.subvector_dim
            end = (m + 1) * self.subvector_dim
            sub_vecs = vectors[:, start:end]
            cb = self._codebooks[m]

            # En yakın centroid indeksini bul
            dists = np.linalg.norm(sub_vecs[:, np.newaxis, :] - cb[np.newaxis, :, :], axis=2)
            codes[:, m] = np.argmin(dists, axis=1).astype(np.uint8)

        return codes
