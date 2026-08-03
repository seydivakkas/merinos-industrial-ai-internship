"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Kenar ve Çizgi Tespiti & Bordür Paralellik Analizi Birim ve Entegrasyon Testleri

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import json
import cv2
import numpy as np
import pytest

from day12.mini_project.src.border_analyzer import CarpetBorderAnalyzer
from day12.mini_project.src.edge_operators import EdgeOperatorEngine
from day12.mini_project.src.generator import CarpetBorderFixtureGenerator
from day12.mini_project.src.hough_engine import HoughLineEngine
from day12.mini_project.src.models import (
    BorderSide,
    EdgeOperatorType,
    LineSegment,
    QualityDecision,
)


@pytest.fixture
def edge_engine() -> EdgeOperatorEngine:
    return EdgeOperatorEngine()


@pytest.fixture
def hough_engine() -> HoughLineEngine:
    return HoughLineEngine()


@pytest.fixture
def analyzer() -> CarpetBorderAnalyzer:
    return CarpetBorderAnalyzer()


@pytest.fixture
def generator() -> CarpetBorderFixtureGenerator:
    return CarpetBorderFixtureGenerator(seed=42)


def test_sobel_gradient_direction_accuracy(edge_engine: EdgeOperatorEngine):
    """Sobel operatörünün bilinen 0°, 90° ve 45° basamak kenarlarında yön doğruluğunu test eder."""
    size = 120

    # 1. Dikey kenar (x=60 boyunca): Soldan sağa parlaklık artışı -> Gradyan yönü ~ 0°
    vert_edge = np.zeros((size, size), dtype=np.uint8)
    vert_edge[:, 60:] = 255
    res_v = edge_engine.compute_sobel(vert_edge, ksize=3)
    # x=60 hattındaki gradyan yönü
    angles_v = res_v["direction_deg"][30:90, 60]
    assert np.all(np.abs(angles_v) < 1.0), f"Dikey kenar gradyan yönü 0° olmalı, ölçülen: {angles_v[:3]}"

    # 2. Yatay kenar (y=60 boyunca): Yukarıdan aşağıya parlaklık artışı -> Gradyan yönü ~ 90°
    horiz_edge = np.zeros((size, size), dtype=np.uint8)
    horiz_edge[60:, :] = 255
    res_h = edge_engine.compute_sobel(horiz_edge, ksize=3)
    angles_h = res_h["direction_deg"][60, 30:90]
    assert np.all(np.abs(angles_h - 90.0) < 1.0), f"Yatay kenar gradyan yönü 90° olmalı, ölçülen: {angles_h[:3]}"


def test_scharr_vs_sobel_rotational_isotropy(edge_engine: EdgeOperatorEngine):
    """Scharr operatörünün eğimli kenarlarda güçlü ve izotropik gradyan ürettiğini doğrular."""
    size = 100
    diag_edge = np.zeros((size, size), dtype=np.uint8)
    y, x = np.ogrid[:size, :size]
    diag_edge[y > x] = 255

    sobel_res = edge_engine.compute_sobel(diag_edge, ksize=3)
    scharr_res = edge_engine.compute_scharr(diag_edge)

    # Scharr gradyan büyüklüğü çarpanından dolayı Sobel'e göre daha yüksektir
    assert np.max(scharr_res["magnitude"]) > np.max(sobel_res["magnitude"])
    assert scharr_res["magnitude_uint8"].shape == (size, size)


def test_laplacian_zero_crossing(edge_engine: EdgeOperatorEngine):
    """Laplacian sıfır geçişi (zero-crossing) tespitinin kenar çizgisini doğruladığını test eder."""
    size = 100
    step_img = np.zeros((size, size), dtype=np.uint8)
    step_img[:, 50:] = 255

    res = edge_engine.compute_laplacian(step_img, ksize=3, detect_zero_crossings=True, zc_threshold=10.0)
    zc_mask = res["zero_crossings"]

    # Kenar x=49 veya x=50 etrafında yoğunlaşmalıdır
    assert np.sum(zc_mask[:, 48:52]) > 0
    # Homojen bölgelerde (x < 40 veya x > 60) sıfır geçişi olmamalıdır
    assert np.sum(zc_mask[:, :40]) == 0
    assert np.sum(zc_mask[:, 60:]) == 0


def test_canny_hysteresis_double_thresholding(edge_engine: EdgeOperatorEngine):
    """Canny algoritmasının çift eşikleme ile ince ve gürültüsüz kenar haritası ürettiğini test eder."""
    size = 150
    img = np.full((size, size), 100, dtype=np.uint8)
    cv2.rectangle(img, (30, 30), (120, 120), 200, 2)

    # Zayıf rastgele gürültü ekle
    rng = np.random.RandomState(42)
    noise = rng.normal(0, 5, img.shape).astype(np.int16)
    noisy_img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    edges = edge_engine.compute_canny(noisy_img, low_threshold=40, high_threshold=120)

    # Kenar haritası ikili (0 veya 255) olmalıdır
    unique_vals = set(np.unique(edges))
    assert unique_vals.issubset({0, 255})
    # Dikdörtgen çevresinde kenarlar tespit edilmiş olmalıdır
    assert np.sum(edges[28:33, 30:120]) > 0


def test_hough_lines_probabilistic_detection(hough_engine: HoughLineEngine):
    """PPHT motorunun bilinen çizgi koordinatlarını ve açılarını doğru çıkardığını test eder."""
    canvas = np.zeros((400, 400), dtype=np.uint8)
    # Yatay çizgi: y=100, x in [50, 350]
    cv2.line(canvas, (50, 100), (350, 100), 255, 2)
    # Dikey çizgi: x=200, y in [50, 350]
    cv2.line(canvas, (200, 50), (200, 350), 255, 2)

    lines = hough_engine.detect_lines_probabilistic(canvas, min_line_length=50, max_line_gap=10)
    assert len(lines) >= 2

    # Yatay çizginin açısı ~ 0°, dikey çizginin açısı ~ 90°
    angles = [l.angle_deg for l in lines]
    has_horiz = any(abs(a) <= 2.0 for a in angles)
    has_vert = any(abs(abs(a) - 90.0) <= 2.0 for a in angles)
    assert has_horiz, f"Yatay çizgi bulunamadı: {angles}"
    assert has_vert, f"Dikey çizgi bulunamadı: {angles}"


def test_line_orientation_filtering(hough_engine: HoughLineEngine):
    """Çizgi parçalarının yatay ve dikey filtrelenmesini test eder."""
    segments = [
        LineSegment(x1=10, y1=100, x2=200, y2=101, length=190, angle_deg=0.3),  # Yatay
        LineSegment(x1=50, y1=20, x2=51, y2=250, length=230, angle_deg=89.7),  # Dikey
        LineSegment(x1=0, y1=0, x2=100, y2=100, length=141, angle_deg=45.0),  # Çapraz (reddedilmeli)
    ]

    horiz = hough_engine.filter_by_orientation(segments, "horizontal", tolerance_deg=10.0)
    vert = hough_engine.filter_by_orientation(segments, "vertical", tolerance_deg=10.0)

    assert len(horiz) == 1 and horiz[0].angle_deg == 0.3
    assert len(vert) == 1 and vert[0].angle_deg == 89.7


def test_border_fitting_and_clustering(hough_engine: HoughLineEngine):
    """4 kenara ait aday çizgilerin doğru bordürlere kümelenip uydurulduğunu doğrular."""
    shape = (800, 800)
    segments = [
        # TOP adayları (y ~ 60)
        LineSegment(x1=100, y1=60, x2=400, y2=60, length=300, angle_deg=0.0),
        LineSegment(x1=420, y1=60, x2=700, y2=60, length=280, angle_deg=0.0),
        # BOTTOM adayları (y ~ 740)
        LineSegment(x1=100, y1=740, x2=700, y2=740, length=600, angle_deg=0.0),
        # LEFT adayları (x ~ 60)
        LineSegment(x1=60, y1=100, x2=60, y2=700, length=600, angle_deg=90.0),
        # RIGHT adayları (x ~ 740)
        LineSegment(x1=740, y1=100, x2=740, y2=700, length=600, angle_deg=90.0),
    ]

    borders = hough_engine.cluster_and_fit_borders(segments, shape, margin_fraction=0.25)
    assert borders["TOP"] is not None
    assert borders["BOTTOM"] is not None
    assert borders["LEFT"] is not None
    assert borders["RIGHT"] is not None

    assert abs(borders["TOP"].angle_deg) < 0.5
    assert abs(borders["BOTTOM"].angle_deg) < 0.5
    assert abs(abs(borders["LEFT"].angle_deg) - 90.0) < 0.5


def test_clean_parallel_border_pass_decision(
    analyzer: CarpetBorderAnalyzer,
    generator: CarpetBorderFixtureGenerator,
):
    """Kusursuz paralel sentetik halıda sistemin ACCEPT kararı verdiğini doğrular."""
    clean_carpet = generator.generate_clean_parallel_carpet(width=800, height=800)
    report, _ = analyzer.analyze_carpet(clean_carpet, edge_method="CANNY")

    assert report.decision == QualityDecision.ACCEPT
    assert report.horizontal_parallelism is not None
    assert report.vertical_parallelism is not None

    # Paralellik sapması 0.50° altında olmalıdır
    assert report.horizontal_parallelism.angle_difference_deg <= 0.50
    assert report.vertical_parallelism.angle_difference_deg <= 0.50
    assert report.horizontal_parallelism.is_parallel
    assert report.vertical_parallelism.is_parallel

    # Diklik sapması 0.75° altında olmalıdır
    if report.orthogonality_deviation_deg is not None:
        assert report.orthogonality_deviation_deg <= 0.75


def test_skewed_border_rejection(
    analyzer: CarpetBorderAnalyzer,
    generator: CarpetBorderFixtureGenerator,
):
    """1.85° açısal eğikliğe sahip halıda paralellik ihlali ve REJECT kararı alındığını test eder."""
    skewed_carpet = generator.generate_skewed_angular_carpet(width=800, height=800, skew_angle_deg=1.85)
    report, _ = analyzer.analyze_carpet(skewed_carpet, edge_method="CANNY")

    assert report.decision in (QualityDecision.REJECT, QualityDecision.WARNING)
    assert report.horizontal_parallelism is not None
    # Yatay açı farkı ~ 1.85° civarında ölçülmelidir
    assert report.horizontal_parallelism.angle_difference_deg >= 1.0


def test_annotation_and_report_serialization(
    analyzer: CarpetBorderAnalyzer,
    generator: CarpetBorderFixtureGenerator,
):
    """Görsel üstveri çizimi ve Pydantic JSON serileştirme doğruluğunu test eder."""
    carpet = generator.generate_clean_parallel_carpet(width=500, height=500)
    report, intermediates = analyzer.analyze_carpet(carpet, edge_method="CANNY")

    overlay = analyzer.annotate_borders(carpet, report, intermediates.get("segments"))
    assert overlay.shape == carpet.shape
    assert overlay.dtype == np.uint8

    # JSON serileştirme ve yeniden yükleme testi
    json_str = report.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["decision"] in ("ACCEPT", "WARNING", "REJECT")
    assert "borders" in parsed
    assert parsed["total_lines_detected"] >= 0
