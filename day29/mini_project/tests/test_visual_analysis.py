"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Görsel Analiz Kapsamlı Test Paketi
Staj Defteri Yaprak 57 ve 58 Doğrulama Testleri
"""

import pytest
import numpy as np
import cv2
from pathlib import Path

from day29.mini_project.src.models import (
    DominantColor,
    ColorAnalysisResult,
    SymmetryAnalysisResult,
    SeamContinuityResult,
    CNNEmbeddingResult,
    ComprehensiveVisualReport,
)
from day29.mini_project.src.color_analyzer import (
    ColorPaletteAnalyzer,
    rgb_to_cielab,
    calculate_delta_e_cielab,
    calculate_ciede2000,
)
from day29.mini_project.src.symmetry_analyzer import StructuralSymmetryAnalyzer
from day29.mini_project.src.seam_analyzer import SeamContinuityAnalyzer
from day29.mini_project.src.embedding_retriever import CNNEmbeddingRetriever
from day29.mini_project.src.master_analyzer import MasterCarpetAnalyzer


@pytest.fixture
def sample_carpet_image():
    """Testler için 256x256 sentetik Osmanlı saray halısı deseni üretir."""
    img = np.full((256, 256, 3), (139, 30, 30), dtype=np.uint8)  # Kırmızı zemin
    # Çift katmanlı merkez madalyon
    cv2.circle(img, (128, 128), 60, (245, 239, 235), -1)        # Krem göbek
    cv2.circle(img, (128, 128), 40, (212, 175, 55), 4)          # Altın varak halka
    cv2.circle(img, (128, 128), 20, (26, 36, 63), -1)           # Lacivert çekirdek
    # 4 köşe bordür rozeti
    for cx, cy in [(20, 20), (236, 20), (20, 236), (236, 236)]:
        cv2.circle(img, (cx, cy), 15, (212, 175, 55), -1)
    return img


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures"


# ------------------------------------------------------------------------------
# 1. K-MEANS VE CIELAB RENK ANALİZİ TESTLERİ (Yaprak 57)
# ------------------------------------------------------------------------------

def test_rgb_to_cielab_conversion():
    """RGB'den CIELAB uzayına dönüşüm doğruluğunu ve sınırlarını test eder."""
    # Siyah (0, 0, 0)
    lab_black = rgb_to_cielab((0, 0, 0))
    assert lab_black[0] == pytest.approx(0.0, abs=1.5)

    # Beyaz (255, 255, 255)
    lab_white = rgb_to_cielab((255, 255, 255))
    assert lab_white[0] == pytest.approx(100.0, abs=1.5)

    # Saf Kırmızı (255, 0, 0) -> a* değeri pozitif ve yüksek olmalı
    lab_red = rgb_to_cielab((255, 0, 0))
    assert lab_red[1] > 50.0


def test_delta_e_cielab_and_ciede2000():
    """Öklid Delta E ve CIEDE2000 formüllerinin tutarlılığını test eder."""
    color1 = (50.0, 20.0, 30.0)
    color2 = (50.0, 20.0, 30.0)
    # Aynı renk için fark 0.0 olmalı
    assert calculate_delta_e_cielab(color1, color2) == 0.0
    assert calculate_ciede2000(color1, color2) == 0.0

    # Farklı renkler için pozitif olmalı
    color3 = (60.0, 25.0, 40.0)
    assert calculate_delta_e_cielab(color1, color3) > 0.0
    assert calculate_ciede2000(color1, color3) > 0.0


def test_kmeans_dominant_color_extraction(sample_carpet_image):
    """K-Means kümeleme ile k=5 renk merkezi ve yüzdelerin toplamını doğrular."""
    analyzer = ColorPaletteAnalyzer()
    dominant_cols = analyzer.extract_dominant_colors(sample_carpet_image, num_clusters=5)

    assert len(dominant_cols) == 5
    # Yüzdelerin toplamı yaklaşık %100 olmalı
    total_pct = sum(c.percentage for c in dominant_cols)
    assert total_pct == pytest.approx(100.0, abs=1.0)

    # Yüzdeye göre azalan sırada sıralı olmalı
    for i in range(len(dominant_cols) - 1):
        assert dominant_cols[i].percentage >= dominant_cols[i + 1].percentage


def test_color_analyzer_with_target_palette(sample_carpet_image, fixtures_dir):
    """Hedef Merinos paleti ile karşılaştırma ve Delta E analizini test eder."""
    palette_path = fixtures_dir / "merinos_target_palettes.json"
    analyzer = ColorPaletteAnalyzer(target_palettes_path=palette_path)
    res = analyzer.analyze(sample_carpet_image, num_clusters=5, target_palette_id="PAL-OSMANLI-01")

    assert isinstance(res, ColorAnalysisResult)
    assert res.target_palette_name == "Klasik Osmanlı Saray Paleti"
    assert res.mean_delta_e >= 0.0
    assert "YÜKSEK RENK UYUMU" in res.verdict or "KABUL EDİLEBİLİR" in res.verdict
    assert len(res.dominant_colors) == 5
    assert res.dominant_colors[0].nearest_yarn_name is not None


# ------------------------------------------------------------------------------
# 2. SİMETRİ VE TEKRAR YAPISI TESTLERİ (Yaprak 57)
# ------------------------------------------------------------------------------

def test_symmetry_perfect_bilateral_image():
    """Tam sol-sağ ayna simetrisine sahip görselde yatay simetri skoru ~1.0 olmalıdır."""
    # Rastgele sol yarı oluştur, sağ yarıya aynala
    rng = np.random.RandomState(42)
    half = rng.randint(0, 256, (128, 64, 3), dtype=np.uint8)
    symmetric_img = np.hstack([half, np.fliplr(half)])

    analyzer = StructuralSymmetryAnalyzer()
    h_score, _ = analyzer.calculate_horizontal_symmetry(symmetric_img)
    assert h_score >= 0.95


def test_symmetry_perfect_vertical_image():
    """Tam üst-alt ayna simetrisine sahip görselde dikey simetri skoru ~1.0 olmalıdır."""
    rng = np.random.RandomState(42)
    half = rng.randint(0, 256, (64, 128, 3), dtype=np.uint8)
    symmetric_img = np.vstack([half, np.flipud(half)])

    analyzer = StructuralSymmetryAnalyzer()
    v_score, _ = analyzer.calculate_vertical_symmetry(symmetric_img)
    assert v_score >= 0.95


def test_symmetry_asymmetric_image():
    """Asimetrik rastgele görselde simetri skorunun düşük olduğunu doğrular."""
    rng = np.random.RandomState(99)
    asym_img = rng.randint(0, 256, (128, 128, 3), dtype=np.uint8)

    analyzer = StructuralSymmetryAnalyzer()
    res = analyzer.analyze(asym_img)
    assert res.horizontal_symmetry < 0.70
    assert "ASİMETRİK" in res.verdict or "SERBEST" in res.verdict


def test_symmetry_repeat_autocorrelation():
    """Tekrarlayan çizgili desenin periyodik otokorelasyon skorunu test eder."""
    # Yatay periyodik çizgili desen
    striped = np.zeros((128, 128, 3), dtype=np.uint8)
    striped[::16, :, :] = 255
    striped[8::16, :, :] = 128

    analyzer = StructuralSymmetryAnalyzer()
    repeat_score = analyzer.calculate_repeat_autocorrelation(striped)
    assert repeat_score >= 0.40


# ------------------------------------------------------------------------------
# 3. KENAR VE DİKİŞ SÜREKLİLİĞİ TESTLERİ (Yaprak 58)
# ------------------------------------------------------------------------------

def test_seam_continuity_tileable_image():
    """Sol ve sağ kenarları birebir aynı olan görselde dikiş kopukluğu olmamalıdır."""
    tileable = np.full((128, 128, 3), 100, dtype=np.uint8)
    # Sol ve sağ 8 piksel şeridine aynı rengi ver
    tileable[:, :8, :] = (200, 50, 50)
    tileable[:, -8:, :] = (200, 50, 50)
    tileable[:8, :, :] = (50, 200, 50)
    tileable[-8:, :, :] = (50, 200, 50)

    analyzer = SeamContinuityAnalyzer(strip_width=8)
    res = analyzer.analyze(tileable)

    assert isinstance(res, SeamContinuityResult)
    assert res.left_right_mse == pytest.approx(0.0, abs=1.0)
    assert res.top_bottom_mse == pytest.approx(0.0, abs=1.0)
    assert res.has_seam_discontinuity is False
    assert res.continuity_score >= 0.90


def test_seam_continuity_abrupt_discontinuity():
    """Sol ve sağ kenarları tamamen zıt renkte olan görselde kopukluk tespit edilmelidir."""
    broken = np.zeros((128, 128, 3), dtype=np.uint8)
    broken[:, :8, :] = 255  # Sol kenar beyaz
    broken[:, -8:, :] = 0   # Sağ kenar siyah

    analyzer = SeamContinuityAnalyzer(strip_width=8, acceptable_mse_threshold=1000.0)
    res = analyzer.analyze(broken)

    assert res.has_seam_discontinuity is True
    assert res.left_right_mse > 1000.0
    assert "BELİRGİN KENAR KOPUKLUĞU" in res.verdict


# ------------------------------------------------------------------------------
# 4. PRETRAINED CNN EMBEDDING VE TOP-K TESTLERİ (Yaprak 58)
# ------------------------------------------------------------------------------

def test_cnn_embedding_extraction_and_l2_norm(sample_carpet_image):
    """CNN embedding'in 512 boyutlu ve L2 normalize (norm ~ 1.0) olduğunu doğrular."""
    retriever = CNNEmbeddingRetriever()
    emb = retriever.extract_embedding(sample_carpet_image)

    assert isinstance(emb, np.ndarray)
    assert emb.shape == (512,)
    l2_norm = np.linalg.norm(emb)
    assert l2_norm == pytest.approx(1.0, abs=0.01)


def test_cnn_retriever_top_k_ordering(sample_carpet_image, fixtures_dir):
    """Katalog üzerinde Top-K aramasında skorların azalan sırada olduğunu doğrular."""
    catalog_path = fixtures_dir / "reference_carpet_catalog.json"
    retriever = CNNEmbeddingRetriever(catalog_path=catalog_path)
    res = retriever.analyze(sample_carpet_image, top_k=3)

    assert isinstance(res, CNNEmbeddingResult)
    assert len(res.top_matches) == 3
    # Skorların azalan sırada olduğunu teyit et
    for i in range(len(res.top_matches) - 1):
        assert res.top_matches[i].similarity_score >= res.top_matches[i + 1].similarity_score
    assert res.top_matches[0].rank == 1


def test_cnn_retriever_empty_catalog_fallback(sample_carpet_image, tmp_path):
    """Boş katalog verildiğinde çökmeden graceful uyarı döndüğünü doğrular (Yaprak 60 kuralı)."""
    empty_catalog = tmp_path / "empty_catalog.json"
    empty_catalog.write_text("[]", encoding="utf-8")

    retriever = CNNEmbeddingRetriever(catalog_path=empty_catalog)
    matches, warn = retriever.search_similar(sample_carpet_image, top_k=3)

    assert len(matches) == 0
    assert warn is not None
    assert "UYARI: Referans halı kataloğu boş" in warn


# ------------------------------------------------------------------------------
# 5. TÜMLEŞİK MASTER ANALYZER VE DASHBOARD TESTLERİ
# ------------------------------------------------------------------------------

def test_master_carpet_analyzer_end_to_end(sample_carpet_image, tmp_path):
    """Master analizörün 4 analizi çalıştırıp 300 DPI panel ve JSON rapor ürettiğini doğrular."""
    master = MasterCarpetAnalyzer()
    report = master.analyze(
        image_input=sample_carpet_image,
        target_palette_id="PAL-OSMANLI-01",
        top_k=3,
        output_dir=tmp_path,
        generate_panel=True
    )

    assert isinstance(report, ComprehensiveVisualReport)
    assert report.color_analysis is not None
    assert report.symmetry_analysis is not None
    assert report.seam_continuity is not None
    assert report.cnn_embedding is not None
    assert len(report.technical_limitations) == 4
    assert report.execution_time_sec >= 0.0

    # Dosyaların varlığını kontrol et
    assert report.diagnostic_panel_path is not None
    panel_file = Path(report.diagnostic_panel_path)
    assert panel_file.exists()
    assert panel_file.stat().st_size > 10000

    report_json = tmp_path / f"{report.report_id}_report.json"
    assert report_json.exists()


def test_master_carpet_analyzer_invalid_file_handling():
    """Olmayan görsel dosya yolu verildiğinde FileNotFoundError fırlatılmalıdır."""
    master = MasterCarpetAnalyzer()
    with pytest.raises(FileNotFoundError):
        master.analyze("gecersiz_olmayan_hali_yolu.png")
