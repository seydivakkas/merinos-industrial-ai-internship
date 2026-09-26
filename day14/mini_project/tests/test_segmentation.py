"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Klasik Segmentasyon Algoritmaları (Otsu, Watershed, GrabCut) Kapsamlı Test Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import json
import cv2
import numpy as np
import pytest

from day14.mini_project.src.benchmark import SegmentationBenchmarkEngine
from day14.mini_project.src.evaluator import SegmentationEvaluator
from day14.mini_project.src.generator import CarpetSegmentationFixtureGenerator
from day14.mini_project.src.grabcut_segmenter import GrabCutSegmenter
from day14.mini_project.src.models import (
    CarpetSegmentationReport,
    EvaluationMetrics,
    SegmentationClass,
    SegmentationMethod,
)
from day14.mini_project.src.otsu_segmenter import OtsuSegmenter
from day14.mini_project.src.watershed_segmenter import WatershedSegmenter


# ---------------------------------------------------------------------------
# Test 1: Otsu Global Eşikleme Doğruluğu
# ---------------------------------------------------------------------------
def test_otsu_global_threshold_accuracy():
    """İki modlu histogramda Otsu optimal eşik değerini ve ikili maskeyi doğru çıkarmalıdır."""
    segmenter = OtsuSegmenter()
    # Zemin: 40, Ön plan madalyon: 210
    img = np.full((200, 200), 40, dtype=np.uint8)
    gt_mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.circle(img, (100, 100), 50, 210, -1)
    cv2.circle(gt_mask, (100, 100), 50, 255, -1)

    binary_mask, threshold_val = segmenter.segment_global(img)

    assert 80 <= threshold_val <= 170, f"Optimal eşik beklenen aralıkta değil: {threshold_val}"
    iou = SegmentationEvaluator.compute_iou(binary_mask, gt_mask)
    assert iou > 0.95, f"Otsu IoU skoru beklenen seviyede değil: {iou}"


# ---------------------------------------------------------------------------
# Test 2: Çok Seviyeli Otsu (Multi-Otsu) Sınıflandırma
# ---------------------------------------------------------------------------
def test_multi_otsu_segmentation_classes():
    """Multi-Otsu algoritması 3 seviyeli histogramda 3 sınıfı (0, 1, 2) ve sıralı eşikleri üretmelidir."""
    segmenter = OtsuSegmenter()
    img = np.full((300, 300), 30, dtype=np.uint8)  # 0: Zemin
    cv2.rectangle(img, (40, 40), (260, 260), 120, -1)  # 1: Bordür
    cv2.circle(img, (150, 150), 40, 220, -1)  # 2: Madalyon

    labeled_mask, thresholds = segmenter.segment_multi_level(img, classes=3)

    assert len(thresholds) == 2
    assert thresholds[0] < thresholds[1], "Eşikler sıralı olmalıdır."
    unique_labels = np.unique(labeled_mask)
    assert set(unique_labels).issubset({0, 1, 2})
    assert len(unique_labels) == 3, f"3 farklı sınıf tespit edilmeliydi: {unique_labels}"


# ---------------------------------------------------------------------------
# Test 3: Watershed Mesafe Dönüşümü ve Tohum İşaretçileri
# ---------------------------------------------------------------------------
def test_watershed_distance_transform_markers():
    """Watershed algoritması mesafe dönüşümü ile tohumları doğru tespit etmeli ve ikili maske üretmelidir."""
    ws = WatershedSegmenter()
    # İki ayrı dairesel motif
    canvas = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.circle(canvas, (60, 100), 30, (200, 200, 200), -1)
    cv2.circle(canvas, (140, 100), 30, (200, 200, 200), -1)

    binary_mask, markers, dist = ws.segment(canvas)

    assert binary_mask.shape == (200, 200)
    assert binary_mask.dtype == np.uint8
    assert np.all(np.isin(np.unique(binary_mask), [0, 255]))
    assert markers.max() > 1, "En az iki ön plan tohumu etiketlenmeliydi."
    assert dist.max() > 0, "Mesafe haritası boş olmamalıdır."


# ---------------------------------------------------------------------------
# Test 4: Watershed Sınır Uyum Hassasiyeti
# ---------------------------------------------------------------------------
def test_watershed_boundary_adherence():
    """Watershed segmentasyon sınırları geometrik motif kenarlarıyla yüksek örtüşüm göstermelidir."""
    ws = WatershedSegmenter()
    img = np.full((200, 200, 3), 30, dtype=np.uint8)
    gt_mask = np.zeros((200, 200), dtype=np.uint8)

    cv2.rectangle(img, (50, 50), (150, 150), (220, 220, 220), -1)
    cv2.rectangle(gt_mask, (50, 50), (150, 150), 255, -1)

    binary_mask, _, _ = ws.segment(img)
    iou = SegmentationEvaluator.compute_iou(binary_mask, gt_mask)
    dice = SegmentationEvaluator.compute_dice(binary_mask, gt_mask)

    assert iou > 0.85, f"Watershed IoU beklentiyi karşılamadı: {iou}"
    assert dice > 0.90, f"Watershed Dice beklentiyi karşılamadı: {dice}"


# ---------------------------------------------------------------------------
# Test 5: GrabCut Grafik Kesme Enerji Minimizasyonu
# ---------------------------------------------------------------------------
def test_grabcut_energy_minimization():
    """GrabCut GMM iterasyonları ile ön plan motifini bounding box'tan daha keskin sınırlarla çıkarmalıdır."""
    gc = GrabCutSegmenter()
    img = np.full((160, 160, 3), 40, dtype=np.uint8)
    gt_mask = np.zeros((160, 160), dtype=np.uint8)

    center = (80, 80)
    cv2.circle(img, center, 40, (30, 180, 230), -1)  # Altın madalyon
    cv2.circle(gt_mask, center, 40, 255, -1)

    # Merkez dikdörtgen (rect) ile GrabCut çalıştır
    rect = (30, 30, 100, 100)
    binary_mask, raw_mask = gc.segment_with_rect(img, rect=rect, iterations=2)

    iou = SegmentationEvaluator.compute_iou(binary_mask, gt_mask)
    assert iou > 0.85, f"GrabCut IoU skoru beklenen seviyede değil: {iou}"
    assert np.sum(binary_mask == 255) > 0, "Ön plan maskesi boş olmamalıdır."


# ---------------------------------------------------------------------------
# Test 6: Değerlendirici Tam Örtüşme (Perfect Overlap) Metrikleri
# ---------------------------------------------------------------------------
def test_evaluator_perfect_overlap_metrics():
    """Birebir örtüşen maskelerde IoU, Dice, Accuracy ve Boundary F1 tam 1.0 olmalıdır."""
    evaluator = SegmentationEvaluator()
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (50, 50), 30, 255, -1)

    metrics = evaluator.evaluate_all(mask, mask)

    assert metrics.iou == 1.0
    assert metrics.dice == 1.0
    assert metrics.pixel_accuracy == 1.0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.boundary_f1 == 1.0


# ---------------------------------------------------------------------------
# Test 7: Değerlendirici Ayrık Maskeler (Disjoint) Metrikleri
# ---------------------------------------------------------------------------
def test_evaluator_disjoint_masks_metrics():
    """Hiç kesişmeyen maskelerde IoU ve Dice tam 0.0 olmalıdır."""
    pred = np.zeros((100, 100), dtype=np.uint8)
    gt = np.zeros((100, 100), dtype=np.uint8)

    pred[:, :40] = 255
    gt[:, 60:] = 255

    iou = SegmentationEvaluator.compute_iou(pred, gt)
    dice = SegmentationEvaluator.compute_dice(pred, gt)
    prec, rec = SegmentationEvaluator.compute_precision_recall(pred, gt)

    assert iou == 0.0
    assert dice == 0.0
    assert prec == 0.0
    assert rec == 0.0


# ---------------------------------------------------------------------------
# Test 8: Sentetik Halı Üzerinde Üç Algoritmanın Kıyaslama Motoru
# ---------------------------------------------------------------------------
def test_otsu_vs_watershed_vs_grabcut_on_synthetic_carpet():
    """Kıyaslama motoru sentetik halı üzerinde 3 algoritmayı hatasız çalıştırmalı ve geçerli rapor üretmelidir."""
    generator = CarpetSegmentationFixtureGenerator(seed=42)
    carpet, gt_motif, _ = generator.generate_medallion_carpet(width=300, height=300)

    engine = SegmentationBenchmarkEngine()
    report, masks = engine.run_benchmark(carpet, gt_mask=gt_motif, iterations=1)

    assert isinstance(report, CarpetSegmentationReport)
    assert len(masks) == 3
    assert SegmentationMethod.OTSU.value in report.results
    assert SegmentationMethod.WATERSHED.value in report.results
    assert SegmentationMethod.GRABCUT.value in report.results

    # Tüm metriklerin pozitif ve anlamlı olduğunu doğrula
    for method_name, result in report.results.items():
        assert result.latency_ms > 0.0
        assert result.fps > 0.0
        assert result.metrics is not None
        assert result.metrics.iou > 0.35, f"{method_name} IoU değeri 0.35'in altında kaldı: {result.metrics.iou}"
        assert result.metrics.dice > 0.50


# ---------------------------------------------------------------------------
# Test 9: Dokuma Kumaş Dokusu ve Gürültü Dayanıklılığı
# ---------------------------------------------------------------------------
def test_segmentation_robustness_to_texture_noise():
    """İplik atkı/çözgü ve Gauss gürültüsü altında segmentasyon kararlılığını korumalıdır."""
    base_img = np.full((200, 200, 3), 50, dtype=np.uint8)
    gt_mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.circle(base_img, (100, 100), 50, (200, 200, 200), -1)
    cv2.circle(gt_mask, (100, 100), 50, 255, -1)

    # Yoğun Gauss gürültüsü ekle
    rng = np.random.RandomState(42)
    noise = rng.normal(0, 15, base_img.shape).astype(np.int16)
    noisy_img = np.clip(base_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    otsu = OtsuSegmenter()
    mask_otsu, _ = otsu.segment_global(noisy_img)
    iou_otsu = SegmentationEvaluator.compute_iou(mask_otsu, gt_mask)

    ws = WatershedSegmenter()
    mask_ws, _, _ = ws.segment(noisy_img)
    iou_ws = SegmentationEvaluator.compute_iou(mask_ws, gt_mask)

    assert iou_otsu > 0.80, f"Gürültülü Otsu IoU beklenenin altında: {iou_otsu}"
    assert iou_ws > 0.80, f"Gürültülü Watershed IoU beklenenin altında: {iou_ws}"


# ---------------------------------------------------------------------------
# Test 10: Rapor Serileştirme ve Karşılaştırma Paneli (Grid) Doğrulaması
# ---------------------------------------------------------------------------
def test_report_serialization_and_cli():
    """Rapor Pydantic JSON serileştirmesini sağlamalı ve görsel panel matrisi doğru boyutta olmalıdır."""
    generator = CarpetSegmentationFixtureGenerator(seed=42)
    carpet, gt_motif, _ = generator.generate_geometric_carpet(width=250, height=250)

    engine = SegmentationBenchmarkEngine()
    report, masks = engine.run_benchmark(carpet, gt_mask=gt_motif, iterations=1)

    # JSON Serileştirme
    json_str = report.model_dump_json(indent=2)
    parsed = json.loads(json_str)
    assert "results" in parsed
    assert parsed["recommended_online_method"] == "WATERSHED"
    assert parsed["recommended_offline_method"] == "GRABCUT"

    # Görsel Panel Grid
    grid = engine.create_comparison_grid(carpet, masks, gt_mask=gt_motif)
    assert grid is not None
    assert grid.shape[0] == 250
    # Orijinal + GT + 3 Algoritma = 5 panel -> 250 * 5 = 1250
    assert grid.shape[1] == 250 * 5
    assert grid.shape[2] == 3
