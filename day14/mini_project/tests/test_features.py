"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Geleneksel Öznitelik Çıkarımı (ORB, SIFT, GLCM, Renk Histogramı) Test Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import json
import cv2
import numpy as np
import pytest

from day14.mini_project.src.benchmark import FeatureBenchmarkEngine
from day14.mini_project.src.color_histogram import ColorHistogramEngine
from day14.mini_project.src.feature_fusion import CarpetPatternClassifierAndMatcher
from day14.mini_project.src.generator import CarpetPatternFixtureGenerator
from day14.mini_project.src.glcm_engine import GLCMFeatureEngine
from day14.mini_project.src.keypoint_engine import KeypointFeatureEngine
from day14.mini_project.src.models import (
    CarpetFeatureVector,
    ColorHistogramFeatures,
    FeatureBenchmarkReport,
    GLCMFeatures,
    KeypointDescriptorType,
    PatternClass,
)


# ---------------------------------------------------------------------------
# Test 1: ORB Anahtar Nokta ve İkili Tanımlayıcı Doğrulaması
# ---------------------------------------------------------------------------
def test_orb_extraction_keypoints_and_descriptors():
    """ORB algoritması yeterli sayıda anahtar nokta ve 256-bit (32 byte) ikili tanımlayıcı üretmelidir."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    carpet, _ = generator.generate_medallion_classic(300, 300)

    engine = KeypointFeatureEngine()
    keypoints, descriptors, stats = engine.extract_orb(carpet)

    assert len(keypoints) > 50, f"Yetersiz ORB anahtar noktası: {len(keypoints)}"
    assert descriptors is not None
    assert descriptors.shape[1] == 32, f"ORB tanımlayıcısı 32 bayt (256-bit) olmalıdır: {descriptors.shape}"
    assert descriptors.dtype == np.uint8
    assert stats.count == len(keypoints)
    assert stats.mean_response > 0.0
    assert stats.angle_entropy > 0.0


# ---------------------------------------------------------------------------
# Test 2: SIFT Anahtar Nokta ve Ölçek Değişmezliği
# ---------------------------------------------------------------------------
def test_sift_extraction_and_scale_invariance():
    """SIFT algoritması 128-boyutlu float32 tanımlayıcı üretmeli ve ölçek değişiminde kararlı kalmalıdır."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    carpet, _ = generator.generate_geometric_modern(300, 300)
    scaled_carpet = cv2.resize(carpet, (450, 450), interpolation=cv2.INTER_LINEAR)

    engine = KeypointFeatureEngine()
    kpts1, desc1, stats1 = engine.extract_sift(carpet)
    kpts2, desc2, stats2 = engine.extract_sift(scaled_carpet)

    assert len(kpts1) > 40
    assert len(kpts2) > 40
    assert desc1 is not None and desc2 is not None
    assert desc1.shape[1] == 128, f"SIFT tanımlayıcısı 128-D olmalıdır: {desc1.shape}"
    assert desc1.dtype == np.float32


# ---------------------------------------------------------------------------
# Test 3: Özdeş Görsellerde Anahtar Nokta Eşleme ve RANSAC Doğrulaması
# ---------------------------------------------------------------------------
def test_feature_matching_identical_images():
    """Aynı görsel eşlendiğinde Lowe ratio testinden geçen nokta sayısı yüksek ve inlier oranı >%90 olmalıdır."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    carpet, _ = generator.generate_floral_traditional(300, 300)

    engine = KeypointFeatureEngine()
    kpts1, desc1, _ = engine.extract_orb(carpet)
    kpts2, desc2, _ = engine.extract_orb(carpet)

    good_matches = engine.match_features(desc1, desc2, method=KeypointDescriptorType.ORB)
    assert len(good_matches) > 30, f"Yetersiz iyi eşleşme: {len(good_matches)}"

    H, inlier_ratio = engine.compute_homography_inliers(kpts1, kpts2, good_matches)
    assert H is not None, "Homografi matrisi hesaplanamadı."
    assert inlier_ratio >= 0.90, f"Inlier oranı %90'ın altında kaldı: {inlier_ratio}"


# ---------------------------------------------------------------------------
# Test 4: GLCM Haralick Doku Analizi ve Karşılaştırması
# ---------------------------------------------------------------------------
def test_glcm_texture_features_computation():
    """GLCM motoru homojen vs pürüzlü dokularda Haralick özelliklerini doğru yönde ayrıştırmalıdır."""
    engine = GLCMFeatureEngine()

    # 1. Pürüzsüz / Düz renkli görsel
    smooth = np.full((200, 200, 3), 128, dtype=np.uint8)
    # 2. Yüksek kontrastlı pürüzlü görsel
    noisy = np.random.RandomState(42).randint(0, 256, (200, 200, 3), dtype=np.uint8)

    f_smooth = engine.extract_features(smooth)
    f_noisy = engine.extract_features(noisy)

    assert f_smooth.homogeneity > f_noisy.homogeneity, "Düz görselin homojenliği daha yüksek olmalıdır."
    assert f_noisy.contrast > f_smooth.contrast, "Gürültülü görselin kontrastı daha yüksek olmalıdır."
    assert f_smooth.energy > f_noisy.energy, "Düz görselin enerjisi (ASM) daha yüksek olmalıdır."

    vec = engine.to_vector(f_noisy)
    assert vec.shape == (7,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


# ---------------------------------------------------------------------------
# Test 5: 3D HSV Renk Histogramı Normalizasyon ve Mesafesi
# ---------------------------------------------------------------------------
def test_color_histogram_hsv_properties():
    """3D HSV histogramı L1 normalize olmalı (toplam=1.0) ve farklı renkleri ayırt edebilmelidir."""
    engine = ColorHistogramEngine()

    # Mavi görsel vs Kırmızı görsel
    blue_img = np.zeros((150, 150, 3), dtype=np.uint8)
    blue_img[:, :] = (200, 30, 20)  # Mavi ağırlıklı BGR

    red_img = np.zeros((150, 150, 3), dtype=np.uint8)
    red_img[:, :] = (20, 30, 200)   # Kırmızı ağırlıklı BGR

    hist_b, feats_b = engine.compute_histogram(blue_img)
    hist_r, feats_r = engine.compute_histogram(red_img)

    assert abs(hist_b.sum() - 1.0) < 1e-4, f"Histogram L1 normalize olmalıdır: {hist_b.sum()}"
    assert feats_b.dimension == 16 * 8 * 8  # 1024

    # Bhattacharyya mesafesi farklı renklerde yüksek olmalıdır (> 0.5)
    bhatt_dist = engine.compare_histograms(hist_b, hist_r, method="bhattacharyya")
    assert bhatt_dist > 0.50, f"Bhattacharyya mesafesi beklenenin altında: {bhatt_dist}"


# ---------------------------------------------------------------------------
# Test 6: Çok Modlu Öznitelik Füzyonu Vektör Boyutları ve Normalizasyon
# ---------------------------------------------------------------------------
def test_feature_fusion_vector_dimensions():
    """Füzyon motoru GLCM (7), Renk (1024) ve Anahtar Nokta (4) vektörlerini birleştirip L2 normalize etmelidir."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    carpet, _ = generator.generate_vintage_distressed(250, 250)

    matcher = CarpetPatternClassifierAndMatcher()
    feat_model = matcher.build_feature_vector(carpet, image_name="vintage_sample")

    expected_dim = 7 + 1024 + 4  # 1035
    assert feat_model.total_dimension == expected_dim
    assert len(feat_model.vector) == expected_dim
    assert feat_model.glcm_dim == 7
    assert feat_model.color_hist_dim == 1024
    assert feat_model.keypoint_dim == 4

    vec = np.array(feat_model.vector, dtype=np.float32)
    l2_norm = np.linalg.norm(vec)
    assert abs(l2_norm - 1.0) < 1e-3, f"Birleşik vektör L2 normalize olmalıdır: {l2_norm}"


# ---------------------------------------------------------------------------
# Test 7: 4 Sınıflı Jakarlı Halı Desen Sınıflandırma Başarısı
# ---------------------------------------------------------------------------
def test_carpet_pattern_classification_accuracy():
    """Katalogdaki 4 farklı desen sınıfı sorgulandığında her biri kendi sınıfına doğru atanmalıdır."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    c_med, p_med = generator.generate_medallion_classic(300, 300)
    c_geo, p_geo = generator.generate_geometric_modern(300, 300)
    c_flo, p_flo = generator.generate_floral_traditional(300, 300)
    c_vin, p_vin = generator.generate_vintage_distressed(300, 300)

    catalog = {
        "cat_medallion": (c_med, p_med),
        "cat_geometric": (c_geo, p_geo),
        "cat_floral": (c_flo, p_flo),
        "cat_vintage": (c_vin, p_vin),
    }

    matcher = CarpetPatternClassifierAndMatcher()
    matcher.index_catalog(catalog, keypoint_type=KeypointDescriptorType.ORB)

    # Test sorguları
    for test_img, expected_class in [(c_med, p_med), (c_geo, p_geo), (c_flo, p_flo), (c_vin, p_vin)]:
        pred_class, confidence = matcher.classify_pattern(test_img, k=1)
        assert pred_class == expected_class, f"Hatalı sınıflandırma: Beklenen {expected_class}, Alınan {pred_class}"
        assert confidence > 50.0, f"Güven skoru yetersiz: {confidence}"


# ---------------------------------------------------------------------------
# Test 8: Top-K Benzer Desen Arama (Visual Retrieval) Sıralaması
# ---------------------------------------------------------------------------
def test_top_k_visual_retrieval_ranking():
    """Katalogda sorgulanan halı Top-1 sırada en yüksek benzerlik skoruyla (%98+) bulunmalıdır."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    c_med, p_med = generator.generate_medallion_classic(300, 300)
    c_geo, p_geo = generator.generate_geometric_modern(300, 300)

    catalog = {
        "cat_medallion": (c_med, p_med),
        "cat_geometric": (c_geo, p_geo),
    }

    matcher = CarpetPatternClassifierAndMatcher()
    matcher.index_catalog(catalog)

    results = matcher.find_top_k_similar(c_geo, query_name="query_geo", k=2)

    assert len(results) == 2
    top1 = results[0]
    assert top1.catalog_name == "cat_geometric"
    assert top1.predicted_class == PatternClass.GEOMETRIC_MODERN
    assert top1.similarity_score > 98.0, f"Top-1 benzerlik skoru beklenenden düşük: {top1.similarity_score}"


# ---------------------------------------------------------------------------
# Test 9: Döndürülmüş Görsellerde SIFT Rotasyon Değişmezliği
# ---------------------------------------------------------------------------
def test_rotation_invariance_under_affine_transform():
    """25 derece döndürülmüş halıda SIFT anahtar noktaları başarılı eşleşme ve yüksek inlier üretmelidir."""
    generator = CarpetPatternFixtureGenerator(seed=42)
    carpet, _ = generator.generate_geometric_modern(300, 300)

    # 25 derece döndür
    h, w = carpet.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), 25, 1.0)
    rotated = cv2.warpAffine(carpet, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    engine = KeypointFeatureEngine()
    k1, d1, _ = engine.extract_sift(carpet)
    k2, d2, _ = engine.extract_sift(rotated)

    matches = engine.match_features(d1, d2, method=KeypointDescriptorType.SIFT, ratio_threshold=0.80)
    assert len(matches) >= 10, f"Döndürülmüş görselde yetersiz SIFT eşleşmesi: {len(matches)}"

    H, inlier_ratio = engine.compute_homography_inliers(k1, k2, matches, ransac_reproj_thresh=5.0)
    assert H is not None, "Homografi matrisi hesaplanmalıydı."
    assert inlier_ratio > 0.25, f"SIFT inlier oranı beklenenin altında: {inlier_ratio}"


# ---------------------------------------------------------------------------
# Test 10: Rapor Serileştirme ve Benchmark Motoru Doğrulaması
# ---------------------------------------------------------------------------
def test_cli_pipeline_and_report_serialization():
    """Benchmark motoru tüm metrikleri hatasız hesaplamalı ve Pydantic JSON serileştirmesi geçerli olmalıdır."""
    engine = FeatureBenchmarkEngine()
    report, catalog_raw = engine.run_benchmark(iterations=1)

    assert isinstance(report, FeatureBenchmarkReport)
    assert report.orb_fps > 0.0
    assert report.sift_fps > 0.0
    assert report.glcm_fps > 0.0
    assert report.classification_accuracy >= 75.0, f"Sınıflandırma başarısı düşük: {report.classification_accuracy}"

    # JSON Serileştirme
    json_str = report.model_dump_json(indent=2)
    parsed = json.loads(json_str)
    assert "classification_accuracy" in parsed
    assert "orb_fps" in parsed
    assert len(parsed["industrial_recommendations"]) >= 3

    # Görsel Panel Grid
    grid = engine.create_feature_summary_panel(catalog_raw)
    assert grid is not None
    assert len(grid.shape) == 3
    assert grid.shape[2] == 3
