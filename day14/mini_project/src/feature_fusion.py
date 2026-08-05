"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Çok Modlu Öznitelik Füzyonu ve Desen Sınıflandırıcı (CarpetPatternClassifierAndMatcher)
Doku (GLCM) + Renk (HSV) + Anahtar Nokta (ORB/SIFT) Bütünleştirmesi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from .color_histogram import ColorHistogramEngine
from .glcm_engine import GLCMFeatureEngine
from .keypoint_engine import KeypointFeatureEngine
from .models import (
    CarpetFeatureVector,
    KeypointDescriptorType,
    PatternClass,
    PatternMatchResult,
)


class CarpetPatternClassifierAndMatcher:
    """Klasik öznitelikleri (Doku, Renk, Anahtar Nokta) birleştiren ve Top-K arama/sınıflandırma yapan motor."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.keypoint_engine = KeypointFeatureEngine(self.config)
        self.glcm_engine = GLCMFeatureEngine(self.config)
        self.color_engine = ColorHistogramEngine(self.config)

        clf_cfg = self.config.get("classification", {})
        self.top_k = int(clf_cfg.get("top_k", 3))
        self.fusion_weights = clf_cfg.get(
            "fusion_weights",
            {"glcm": 0.35, "color_hist": 0.45, "keypoint_stats": 0.20},
        )

        # İndekslenmiş referans katalog vektörleri
        self.catalog_vectors: Dict[str, CarpetFeatureVector] = {}
        self.catalog_images: Dict[str, np.ndarray] = {}

    def build_feature_vector(
        self,
        image: np.ndarray,
        image_name: str = "carpet",
        pattern_class: Optional[PatternClass] = None,
        keypoint_type: KeypointDescriptorType = KeypointDescriptorType.ORB,
    ) -> CarpetFeatureVector:
        """Görüntüden GLCM doku, HSV renk ve anahtar nokta istatistiklerini çıkarıp birleştirir."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")

        w_glcm = float(self.fusion_weights.get("glcm", 0.35))
        w_color = float(self.fusion_weights.get("color_hist", 0.45))
        w_kp = float(self.fusion_weights.get("keypoint_stats", 0.20))

        # 1. GLCM Doku Vektörü (7 Boyut)
        glcm_feats = self.glcm_engine.extract_features(image)
        glcm_vec = self.glcm_engine.to_vector(glcm_feats) * w_glcm

        # 2. HSV Renk Histogramı Vektörü (1024 Boyut)
        color_hist_vec, _ = self.color_engine.compute_histogram(image)
        # Renk vektörünü kendi içinde L2 normalize et
        c_norm = np.linalg.norm(color_hist_vec)
        if c_norm > 1e-6:
            color_hist_vec = (color_hist_vec / c_norm) * w_color

        # 3. Anahtar Nokta İstatistikleri (4 Boyut)
        if keypoint_type == KeypointDescriptorType.SIFT:
            _, _, kp_stats = self.keypoint_engine.extract_sift(image)
        else:
            _, _, kp_stats = self.keypoint_engine.extract_orb(image)

        # İstatistikleri [0, 1] aralığına ölçekle
        kp_vec = np.array(
            [
                min(1.0, kp_stats.count / 1000.0),
                min(1.0, kp_stats.mean_response / 100.0),
                min(1.0, kp_stats.mean_size / 50.0),
                min(1.0, kp_stats.angle_entropy / 5.2),
            ],
            dtype=np.float32,
        )
        kp_norm = np.linalg.norm(kp_vec)
        if kp_norm > 1e-6:
            kp_vec = (kp_vec / kp_norm) * w_kp

        # 4. Birleştirme (Fusion) ve Global L2 Normalizasyonu
        fused_raw = np.concatenate([glcm_vec, color_hist_vec, kp_vec]).astype(np.float32)
        total_norm = np.linalg.norm(fused_raw)
        if total_norm > 1e-6:
            fused = (fused_raw / total_norm).tolist()
        else:
            fused = fused_raw.tolist()

        return CarpetFeatureVector(
            image_name=image_name,
            total_dimension=len(fused),
            glcm_dim=len(glcm_vec),
            color_hist_dim=len(color_hist_vec),
            keypoint_dim=len(kp_vec),
            vector=[round(float(v), 5) for v in fused],
            pattern_class=pattern_class,
        )

    def index_catalog(
        self,
        catalog_items: Dict[str, Tuple[np.ndarray, PatternClass]],
        keypoint_type: KeypointDescriptorType = KeypointDescriptorType.ORB,
    ):
        """Katalogdaki referans halıları öznitelik vektörleriyle indeksler."""
        self.catalog_vectors.clear()
        self.catalog_images.clear()

        for name, (img, p_class) in catalog_items.items():
            feat_vec = self.build_feature_vector(
                image=img,
                image_name=name,
                pattern_class=p_class,
                keypoint_type=keypoint_type,
            )
            self.catalog_vectors[name] = feat_vec
            self.catalog_images[name] = img

    def find_top_k_similar(
        self,
        query_image: np.ndarray,
        query_name: str = "query_carpet",
        k: Optional[int] = None,
        keypoint_type: KeypointDescriptorType = KeypointDescriptorType.ORB,
    ) -> List[PatternMatchResult]:
        """Sorgu halısına katalogda en çok benzeyen Top-K halıyı kosinüs benzerliği ile bulur."""
        if not self.catalog_vectors:
            raise ValueError("Katalog boştur. Önce index_catalog metodunu çağırınız.")

        top_limit = k if k is not None else self.top_k
        query_vec_model = self.build_feature_vector(
            image=query_image,
            image_name=query_name,
            keypoint_type=keypoint_type,
        )
        q_vec = np.array(query_vec_model.vector, dtype=np.float32)

        results: List[PatternMatchResult] = []

        # Sorgu için anahtar noktaları hazırla (detaylı eşleşme için)
        if keypoint_type == KeypointDescriptorType.SIFT:
            q_kpts, q_desc, _ = self.keypoint_engine.extract_sift(query_image)
        else:
            q_kpts, q_desc, _ = self.keypoint_engine.extract_orb(query_image)

        for cat_name, cat_model in self.catalog_vectors.items():
            c_vec = np.array(cat_model.vector, dtype=np.float32)
            # L2 normalize vektörlerde Kosinüs Benzerliği = İç Çarpım
            cos_sim = float(np.dot(q_vec, c_vec))
            # [0, 1] arası normalize benzerlik skoru (%)
            sim_score = max(0.0, min(100.0, cos_sim * 100.0))
            distance = float(np.linalg.norm(q_vec - c_vec))

            # Anahtar nokta eşleşmesi doğrulaması
            good_matches_count = None
            inlier_ratio = None
            cat_img = self.catalog_images.get(cat_name)
            if cat_img is not None and q_desc is not None:
                if keypoint_type == KeypointDescriptorType.SIFT:
                    c_kpts, c_desc, _ = self.keypoint_engine.extract_sift(cat_img)
                else:
                    c_kpts, c_desc, _ = self.keypoint_engine.extract_orb(cat_img)

                if c_desc is not None:
                    good_matches = self.keypoint_engine.match_features(
                        q_desc, c_desc, method=keypoint_type
                    )
                    good_matches_count = len(good_matches)
                    if len(good_matches) >= 4:
                        _, inlier_ratio = self.keypoint_engine.compute_homography_inliers(
                            q_kpts, c_kpts, good_matches
                        )

            results.append(
                PatternMatchResult(
                    query_name=query_name,
                    catalog_name=cat_name,
                    predicted_class=cat_model.pattern_class or PatternClass.MEDALLION_CLASSIC,
                    similarity_score=round(sim_score, 2),
                    distance=round(distance, 4),
                    good_matches_count=good_matches_count,
                    inlier_ratio=inlier_ratio,
                )
            )

        # Benzerlik skoruna göre azalan sırala
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_limit]

    def classify_pattern(
        self,
        query_image: np.ndarray,
        k: int = 3,
        keypoint_type: KeypointDescriptorType = KeypointDescriptorType.ORB,
    ) -> Tuple[PatternClass, float]:
        """k-NN benzerlik oylaması ile sorgu halısının desen sınıfını tahmin eder."""
        top_matches = self.find_top_k_similar(
            query_image=query_image,
            k=k,
            keypoint_type=keypoint_type,
        )

        class_votes: Dict[PatternClass, float] = {}
        total_weight = 0.0

        for m in top_matches:
            weight = m.similarity_score
            class_votes[m.predicted_class] = class_votes.get(m.predicted_class, 0.0) + weight
            total_weight += weight

        # En yüksek ağırlıklı sınıfı seç
        best_class = max(class_votes.items(), key=lambda item: item[1])[0]
        confidence = (class_votes[best_class] / total_weight * 100.0) if total_weight > 0 else 0.0

        return best_class, round(confidence, 2)
