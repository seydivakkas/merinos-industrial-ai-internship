"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Geleneksel Öznitelik Kıyaslama ve Performans Laboratuvarı (FeatureBenchmarkEngine)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from .feature_fusion import CarpetPatternClassifierAndMatcher
from .generator import CarpetPatternFixtureGenerator
from .glcm_engine import GLCMFeatureEngine
from .keypoint_engine import KeypointFeatureEngine
from .models import (
    FeatureBenchmarkReport,
    KeypointDescriptorType,
    PatternClass,
)


class FeatureBenchmarkEngine:
    """ORB, SIFT ve GLCM öznitelik çıkarıcılarının hızını ve sınıflandırma başarısını kıyaslar."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.kp_engine = KeypointFeatureEngine(self.config)
        self.glcm_engine = GLCMFeatureEngine(self.config)
        self.matcher = CarpetPatternClassifierAndMatcher(self.config)

    def run_benchmark(
        self,
        iterations: int = 10,
    ) -> Tuple[FeatureBenchmarkReport, Dict[str, np.ndarray]]:
        """Sentetik veri üzerinde kapsamlı hız ve sınıflandırma kıyaslaması yürütür."""
        generator = CarpetPatternFixtureGenerator(seed=42)

        # 4 Sınıf Halı Görsellerini Oluştur
        c_med, p_med = generator.generate_medallion_classic(400, 400)
        c_geo, p_geo = generator.generate_geometric_modern(400, 400)
        c_flo, p_flo = generator.generate_floral_traditional(400, 400)
        c_vin, p_vin = generator.generate_vintage_distressed(400, 400)

        catalog = {
            "medallion_classic": (c_med, p_med),
            "geometric_modern": (c_geo, p_geo),
            "floral_traditional": (c_flo, p_flo),
            "vintage_distressed": (c_vin, p_vin),
        }

        # 1. ORB Hız Ölçümü
        for _ in range(3):
            self.kp_engine.extract_orb(c_med)
        t0 = time.perf_counter()
        for _ in range(iterations):
            self.kp_engine.extract_orb(c_med)
        t_orb = (time.perf_counter() - t0) / iterations * 1000.0
        fps_orb = 1000.0 / t_orb if t_orb > 0 else 0.0

        # 2. SIFT Hız Ölçümü
        for _ in range(2):
            self.kp_engine.extract_sift(c_med)
        sift_iters = max(1, min(iterations, 5))
        t0 = time.perf_counter()
        for _ in range(sift_iters):
            self.kp_engine.extract_sift(c_med)
        t_sift = (time.perf_counter() - t0) / sift_iters * 1000.0
        fps_sift = 1000.0 / t_sift if t_sift > 0 else 0.0

        # 3. GLCM Hız Ölçümü
        for _ in range(2):
            self.glcm_engine.extract_features(c_med)
        glcm_iters = max(1, min(iterations, 5))
        t0 = time.perf_counter()
        for _ in range(glcm_iters):
            self.glcm_engine.extract_features(c_med)
        t_glcm = (time.perf_counter() - t0) / glcm_iters * 1000.0
        fps_glcm = 1000.0 / t_glcm if t_glcm > 0 else 0.0

        # 4. Katalog İndeksleme ve Top-K Arama Gecikmesi
        self.matcher.index_catalog(catalog, keypoint_type=KeypointDescriptorType.ORB)

        t0 = time.perf_counter()
        retrieval_iters = max(1, iterations)
        for _ in range(retrieval_iters):
            self.matcher.find_top_k_similar(c_geo, query_name="query_geo", k=3)
        t_retrieval = (time.perf_counter() - t0) / retrieval_iters * 1000.0

        # 5. Sınıflandırma Başarısı (Katalog Görselleri + Döndürülmüş/Gürültülü Test Görselleri)
        test_samples = [
            (c_med, p_med),
            (c_geo, p_geo),
            (c_flo, p_flo),
            (c_vin, p_vin),
        ]
        # Hafif rotasyon ve varyasyon ekle
        for img, p_class in [(c_med, p_med), (c_geo, p_geo)]:
            # 15 derece döndür
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w // 2, h // 2), 15, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
            test_samples.append((rotated, p_class))

        correct = 0
        for sample_img, expected_class in test_samples:
            pred_class, _ = self.matcher.classify_pattern(sample_img, k=1)
            if pred_class == expected_class:
                correct += 1

        accuracy = (correct / len(test_samples)) * 100.0

        notes = [
            f"ORB Anahtar Noktaları: Ultra hızlı ({t_orb:.2f} ms, {fps_orb:.0f} FPS). Canlı tezgâh izleme için uygundur.",
            f"SIFT Anahtar Noktaları: Ölçek/rotasyon değişmez, yüksek tanımlama ({t_sift:.2f} ms, {fps_sift:.0f} FPS). Arşiv kontrolü için uygundur.",
            f"GLCM Haralick: İplik sıklığı ve kumaş pürüzlülüğü için sağlam doku özetlemesi ({t_glcm:.2f} ms).",
            f"Çok Modlu Füzyon: Top-K arama gecikmesi {t_retrieval:.2f} ms, 4 sınıflı desen sınıflandırma doğruluğu %{accuracy:.1f}.",
        ]

        report = FeatureBenchmarkReport(
            orb_latency_ms=round(t_orb, 3),
            orb_fps=round(fps_orb, 1),
            sift_latency_ms=round(t_sift, 3),
            sift_fps=round(fps_sift, 1),
            glcm_latency_ms=round(t_glcm, 3),
            glcm_fps=round(fps_glcm, 1),
            retrieval_latency_ms=round(t_retrieval, 3),
            classification_accuracy=round(accuracy, 2),
            industrial_recommendations=notes,
        )

        catalog_raw = {k: v[0] for k, v in catalog.items()}
        return report, catalog_raw

    def create_feature_summary_panel(
        self,
        catalog_images: Dict[str, np.ndarray],
    ) -> np.ndarray:
        """4 desen sınıfını ve üzerindeki ORB anahtar noktalarını 2x2 grid olarak görselleştirir."""
        panels = []
        for name, img in catalog_images.items():
            vis = img.copy()
            kpts, _, _ = self.kp_engine.extract_orb(img)
            # Anahtar noktaları yeşil çemberler olarak çiz
            vis = cv2.drawKeypoints(
                vis,
                kpts[:150],
                None,
                color=(0, 255, 0),
                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
            # Başlık ekle
            title = name.replace("_", " ").upper()
            cv2.putText(vis, title, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
            cv2.putText(vis, f"ORB KP: {len(kpts)}", (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
            panels.append(vis)

        # 2x2 birleştirme
        if len(panels) >= 4:
            row1 = np.hstack([panels[0], panels[1]])
            row2 = np.hstack([panels[2], panels[3]])
            grid = np.vstack([row1, row2])
        else:
            grid = np.hstack(panels)

        return grid
