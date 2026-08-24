# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
Test Suite for Integrated Carpet Generation & Visual Analysis Pipeline.
Staj Defteri Yaprak 59 ve 60 Müfredatına %100 Uyumlu Test Paketi.
"""

from pathlib import Path
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from day30.mini_project.src.models import (
    CarpetDesignInput,
    IntegratedPipelineOutput,
    PromptAssemblyResult,
    SymmetryMode,
    TechnicalLimitationsReport,
)
from day30.mini_project.src.pipeline import IntegratedCarpetPipeline, DEFAULT_LIMITATIONS
from day30.mini_project.src.visualizer import CarpetPipelineVisualizer
from day30.mini_project.src.ui.web_server import app


# ==============================================================================
# 1. GİRDİ DOĞRULAMA & İSTEM MONTAJI TESTLERİ (Yaprak 59 & 60)
# ==============================================================================

def test_design_brief_validation_success():
    """Geçerli alanlarla oluşturulan brifin başarıyla doğrulandığını test eder."""
    brief = CarpetDesignInput(
        brief_id="BRF-T1",
        style="Klasik Osmanlı",
        motif="Barok Madalyon",
        primary_color="Krem",
        secondary_color="Bordo",
        composition="Merkezi madalyonlu kompozisyon",
        border_type="Geniş su bordürü",
        symmetry_mode=SymmetryMode.BILATERAL_AND_VERTICAL,
        seed=100
    )
    assert brief.style == "Klasik Osmanlı"
    assert brief.symmetry_mode == SymmetryMode.BILATERAL_AND_VERTICAL
    assert brief.seed == 100


def test_design_brief_validation_empty_required_field():
    """
    Yaprak 60 Hata Durumu 1: Boş bırakılan zorunlu alanların (stil, motif, renk)
    Pydantic tarafından ValueError ile yakalandığını test eder.
    """
    with pytest.raises(ValueError):
        CarpetDesignInput(
            style="",  # Boş zorunlu alan
            motif="Madalyon",
            primary_color="Krem"
        )

    with pytest.raises(ValueError):
        CarpetDesignInput(
            style="Klasik",
            motif="",  # Boş zorunlu alan
            primary_color="Krem"
        )

    with pytest.raises(ValueError):
        CarpetDesignInput(
            style="Klasik",
            motif="Madalyon",
            primary_color=""  # Boş zorunlu alan
        )


def test_prompt_assembly_fixed_ordering():
    """
    Yaprak 59: Kullanıcı girdilerinin sabit sırada (stil, motif, renk, kompozisyon,
    bordür, simetri) birleştirildiğini ve boş alanların prompt'a dahil edilmediğini test eder.
    """
    pipeline = IntegratedCarpetPipeline()
    brief = CarpetDesignInput(
        brief_id="BRF-T2",
        style="Modern Geometrik",
        motif="Soyut Prizmalar",
        primary_color="Taş Grisi",
        secondary_color="",       # Boş isteğe bağlı
        composition="",          # Boş isteğe bağlı
        border_type="İnce bordür",
        symmetry_mode=SymmetryMode.BILATERAL
    )
    res = pipeline.assemble_prompt(brief)

    assert isinstance(res, PromptAssemblyResult)
    assert "Modern Geometrik" in res.assembled_prompt
    assert "Soyut Prizmalar" in res.assembled_prompt
    assert "Taş Grisi" in res.assembled_prompt
    assert "İnce bordür" in res.assembled_prompt
    assert "composition" in res.omitted_fields
    assert "style" in res.included_fields


# ==============================================================================
# 2. UÇTAN UCA TÜMLEŞİK BORU HATTI TESTLERİ (Yaprak 59)
# ==============================================================================

def test_pipeline_run_e2e(tmp_path):
    """
    Day 28 (SDXL Üretim) ve Day 29 (Görsel Analiz) adımlarının
    uçtan uca hatasız zincirlendiğini test eder.
    """
    pipeline = IntegratedCarpetPipeline(output_dir=str(tmp_path))
    brief = CarpetDesignInput(
        brief_id="BRF-E2E-01",
        style="Klasik Osmanlı",
        motif="Madalyon",
        primary_color="Krem",
        secondary_color="Bordo",
        symmetry_mode=SymmetryMode.BILATERAL_AND_VERTICAL,
        seed=42
    )

    output = pipeline.run(brief)

    assert isinstance(output, IntegratedPipelineOutput)
    assert output.success is True
    assert Path(output.generated_image_path).exists()

    # Day 29 Renk Analizi
    assert "dominant_colors" in output.color_analysis
    assert len(output.color_analysis["dominant_colors"]) > 0
    assert output.color_analysis["mean_delta_e"] >= 0.0

    # Day 29 Simetri Analizi
    assert "horizontal_score" in output.symmetry_analysis
    assert "vertical_score" in output.symmetry_analysis
    assert output.symmetry_analysis["horizontal_score"] > 0.6  # Bilateral ve dikey simetrili üretim

    # Day 29 Dikiş Sürekliliği
    assert "sobel_jump" in output.seam_analysis
    assert "is_tileable" in output.seam_analysis

    # Day 29 CNN Benzerlik
    assert len(output.similar_carpets) > 0

    # Süre ve Rapor
    assert output.total_latency_ms > 0.0
    assert output.limitations_report is not None


# ==============================================================================
# 3. HATA DURUMLARI TESTLERİ (Yaprak 60)
# ==============================================================================

def test_empty_catalog_fallback_handling():
    """
    Yaprak 60 Hata Durumu 2: Referans halı kataloğunun boş veya bulunamadığı durumda
    sistemin çökmeden zarif fallback sağladığını test eder.
    """
    pipeline = IntegratedCarpetPipeline()
    brief = CarpetDesignInput(
        brief_id="BRF-FALLBACK",
        style="Klasik",
        motif="Madalyon",
        primary_color="Krem"
    )

    output = pipeline.run(brief, empty_catalog_test=True)

    assert output.success is True
    assert len(output.similar_carpets) > 0
    # Fallback notu veya sıfır benzerlik içermeli
    first_item = output.similar_carpets[0]
    assert "fallback" in first_item.get("note", "").lower() or first_item.get("similarity_score", 0) == 0.0


def test_corrupt_input_handling(tmp_path):
    """
    Yaprak 60 Hata Durumu 3: Bozuk görsel veya geçersiz matris durumunda
    analiz motorunun güvenli şekilde hata yönetimi sağladığını test eder.
    """
    pipeline = IntegratedCarpetPipeline(output_dir=str(tmp_path))
    corrupt_image = np.zeros((10, 10), dtype=np.uint8)  # 3 kanallı RGB değil, 2D siyah

    # Master analiz motorunun tek başına çağrılması durumunda güvenli koruma
    with pytest.raises(Exception):
        pipeline.master_analyzer.analyze_image(corrupt_image)


# ==============================================================================
# 4. TEKNİK ÇALIŞMA SINIRLARI TESTİ (Yaprak 60)
# ==============================================================================

def test_four_technical_limitations_report():
    """
    Yaprak 60'ta belirtilen 4 temel sınırın raporda eksiksiz yer aldığını doğrular:
    1. Fiziksel dokunabilirlik garantisi yoktur (tezgah kısıtları).
    2. Estetik kalite matematiksel olarak kesin ölçülemez (sübjektiflik).
    3. Telif ve özgünlük değerlendirmesi yapılmaz.
    4. Analiz metrikleri tek başına başarılı tasarım anlamına gelmez.
    """
    rep = DEFAULT_LIMITATIONS
    assert isinstance(rep, TechnicalLimitationsReport)

    assert rep.manufacturability["status"] == "SINIR_BELİRLENDİ"
    assert "dokunabilirlik" in rep.manufacturability["title"].lower()

    assert rep.aesthetic_subjectivity["status"] == "SINIR_BELİRLENDİ"
    assert "estetik" in rep.aesthetic_subjectivity["title"].lower()

    assert rep.copyright_originality["status"] == "SINIR_BELİRLENDİ"
    assert "telif" in rep.copyright_originality["title"].lower()

    assert rep.metric_independence["status"] == "SINIR_BELİRLENDİ"
    assert "metrik" in rep.metric_independence["title"].lower()

    assert len(rep.summary_verdict) > 30


# ==============================================================================
# 5. GÖRSELLEŞTİRME VE TEŞHİS PANELİ TESTİ (Yaprak 59-60)
# ==============================================================================

def test_visualizer_diagnostic_panel(tmp_path):
    """300 DPI 4-Panelli master teşhis grafiğinin başarıyla üretildiğini test eder."""
    pipeline = IntegratedCarpetPipeline(output_dir=str(tmp_path))
    brief = CarpetDesignInput(
        brief_id="BRF-VIZ-01",
        style="Modern Floral",
        motif="Lale",
        primary_color="Antrasit",
        secondary_color="Bakır",
        symmetry_mode=SymmetryMode.BILATERAL,
        seed=77
    )
    output = pipeline.run(brief)

    viz = CarpetPipelineVisualizer(dpi=100)
    save_path = tmp_path / "test_diagnostic_panel.png"
    result_path = viz.create_master_diagnostic_panel(output, save_path=save_path)

    assert result_path.exists()
    assert result_path.stat().st_size > 50000  # En az 50 KB


# ==============================================================================
# 6. WEB SUNUCUSU API UÇ NOKTA TESTLERİ (Yaprak 60 Basit Arayüz)
# ==============================================================================

def test_web_server_api_endpoints():
    """FastAPI web arayüzü uç noktalarının doğruluk testlerini yapar."""
    client = TestClient(app)

    # Health
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "HEALTHY"

    # Limitations
    r_lim = client.get("/api/pipeline/limitations")
    assert r_lim.status_code == 200
    assert "manufacturability" in r_lim.json()

    # Assemble Prompt
    payload = {
        "brief_id": "BRF-WEB-01",
        "style": "Klasik Saray",
        "motif": "Rumi",
        "primary_color": "Krem"
    }
    r_prompt = client.post("/api/pipeline/assemble-prompt", json=payload)
    assert r_prompt.status_code == 200
    data = r_prompt.json()
    assert "assembled_prompt" in data
    assert "Klasik Saray" in data["assembled_prompt"]

    # Boş Zorunlu Alan Hatası (Yaprak 60)
    invalid_payload = {
        "brief_id": "BRF-WEB-BAD",
        "style": "",
        "motif": "",
        "primary_color": "Krem"
    }
    r_bad = client.post("/api/pipeline/run", json=invalid_payload)
    assert r_bad.status_code == 422  # Unprocessable Entity
