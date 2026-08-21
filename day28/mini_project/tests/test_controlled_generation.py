"""
Merinos Industrial AI Internship - Day 28
Test Suite for Controlled Carpet Image Generation & Comparative Analysis.
Staj Defteri Yaprak 55 ve 56 Müfredatı Uyum Testleri.
Copyright (c) 2026 Seydi Eryilmaz (@seydivakkas). All Rights Reserved.
"""

import json
from pathlib import Path
import numpy as np
import pytest

from day28.mini_project.src.comparator_engine import ComparatorEngine
from day28.mini_project.src.models import (
    ComparisonResult,
    ExperimentRunRecord,
    ExperimentType,
    PromptAssemblyResult,
    ReproducibilityVerificationResult,
    StructuredDesignBrief,
)
from day28.mini_project.src.prompt_structurer import PromptStructurer
from day28.mini_project.src.sdxl_controller import SDXLController
from day28.mini_project.src.visualizer import Day28Visualizer


# ==============================================================================
# 1. YAPRAK 55: TASARIM İSTEĞİNİN ALANLARA AYRILMASI VE DOĞRULAMA TESTLERİ
# ==============================================================================

def test_structured_brief_validation():
    """Zorunlu alanların doğrulanmasını ve geçersiz boş alanların reddedilmesini test eder."""
    valid_brief = StructuredDesignBrief(
        brief_id="BRF-T01",
        title="Test Klasik Saray",
        style="Klasik Osmanlı",
        motif="Barok Madalyon",
        color="Krem ve Bordo",
        composition="Merkezi madalyon",
        border="Su bordürü",
        symmetry="Çift yönlü 4-çeyrek simetri",
        seed=42
    )
    assert valid_brief.style == "Klasik Osmanlı"
    assert valid_brief.seed == 42

    # Boş zorunlu alan (Hata fırlatmalı)
    with pytest.raises(ValueError):
        StructuredDesignBrief(
            brief_id="BRF-ERR",
            style="", # Boş
            motif="Madalyon",
            color="Krem"
        )


def test_prompt_assembly_fixed_ordering():
    """Staj Defteri Yaprak 55: Alanların sabit sırada birleştirilmesini ve boş alanların filtrelenmesini test eder."""
    structurer = PromptStructurer()
    brief = StructuredDesignBrief(
        brief_id="BRF-T02",
        title="Test İskandinav",
        style="İskandinav Minimalist",
        motif="Üçgen Prizma",
        color="Taş Grisi",
        composition="", # Boş
        border="",      # Boş
        symmetry="Yalnızca dikey ayna",
        seed=108
    )
    res = structurer.assemble(brief)
    
    # Sıralama kontrolü: style -> motif -> color -> symmetry
    assert res.field_order == ["style", "motif", "color", "symmetry"]
    assert "composition" in res.omitted_fields
    assert "border" in res.omitted_fields
    assert "İskandinav Minimalist" in res.assembled_prompt
    assert "Üçgen Prizma" in res.assembled_prompt
    assert "Merinos woven carpet" in res.assembled_prompt


# ==============================================================================
# 2. YAPRAK 55: SEED DENEYLERİ VE DETERMINİZM TESTLERİ
# ==============================================================================

def test_sdxl_controller_deterministic_output(tmp_path):
    """Aynı seed ile iki bağımsız çalıştırmanın piksel düzeyinde %100 aynı görsel ürettiğini test eder."""
    controller = SDXLController()
    brief = StructuredDesignBrief(
        brief_id="BRF-DET-01",
        style="Klasik Osmanlı",
        motif="Madalyon",
        color="Krem ve Bordo",
        seed=42
    )

    img1, rec1 = controller.generate(brief, output_path=tmp_path / "run1.png")
    img2, rec2 = controller.generate(brief, output_path=tmp_path / "run2.png")

    assert img1.shape == (512, 512, 3)
    assert img2.shape == (512, 512, 3)
    # Piksel denkliği
    diff = np.max(np.abs(img1.astype(int) - img2.astype(int)))
    assert diff == 0, f"Determinizm bozuldu, maksimum piksel farkı: {diff}"


def test_sdxl_controller_seed_sensitivity(tmp_path):
    """Staj Defteri Yaprak 55: Farklı seed'lerin farklı görsel çıktılar ürettiğini test eder."""
    controller = SDXLController()
    brief_seed42 = StructuredDesignBrief(
        brief_id="BRF-S42",
        style="Klasik Osmanlı",
        motif="Madalyon",
        color="Krem ve Bordo",
        seed=42
    )
    brief_seed108 = brief_seed42.model_copy(update={"seed": 108})

    img42, _ = controller.generate(brief_seed42, output_path=tmp_path / "s42.png")
    img108, _ = controller.generate(brief_seed108, output_path=tmp_path / "s108.png")

    # İki görselin pikselleri farklı olmalı
    diff = np.mean(np.abs(img42.astype(float) - img108.astype(float)))
    assert diff > 5.0, "Farklı seed değerleri anlamlı görsel çeşitlilik oluşturmalıdır."


def test_seed_variation_experiment(tmp_path):
    """Staj Defteri Yaprak 55: Çoklu seed varyasyonu deneyini test eder."""
    comparator = ComparatorEngine()
    brief = StructuredDesignBrief(
        brief_id="BRF-VAR-01",
        style="Klasik Osmanlı",
        motif="Madalyon",
        color="Krem ve Bordo",
        seed=42
    )
    comp_res, images = comparator.run_seed_variation_experiment(
        base_brief=brief,
        seeds=[42, 108, 256],
        output_dir=tmp_path
    )

    assert comp_res.experiment_type == ExperimentType.SEED_VARIATION
    assert len(comp_res.runs) == 3
    assert len(images) == 3
    assert len(comp_res.findings) == 4


# ==============================================================================
# 3. YAPRAK 56: TEK DEĞİŞKENLİ PROMPT KARŞILAŞTIRMA TESTLERİ
# ==============================================================================

def test_single_variable_mutation_field_integrity():
    """Yalnızca istenen tek bir alanın değiştiğini, seed ve diğer alanların korunduğunu test eder."""
    structurer = PromptStructurer()
    brief = StructuredDesignBrief(
        brief_id="BRF-MUT-01",
        style="Klasik Osmanlı",
        motif="Barok Madalyon",
        color="Krem ve Bordo",
        seed=42,
        steps=30
    )

    mutated = structurer.mutate_single_field(brief, "color", "Gece Laciverti ve Altın")
    assert mutated.color == "Gece Laciverti ve Altın"
    assert mutated.style == brief.style
    assert mutated.motif == brief.motif
    assert mutated.seed == 42 # Seed sabit kalmalı
    assert mutated.steps == 30


def test_single_variable_mutation_invalid_field():
    """Geçersiz alan adı veya boş değerle mutasyon yapılmaya çalışıldığında hata fırlatıldığını test eder."""
    structurer = PromptStructurer()
    brief = StructuredDesignBrief(
        brief_id="BRF-MUT-02",
        style="Klasik",
        motif="Madalyon",
        color="Krem",
        seed=42
    )

    with pytest.raises(ValueError):
        structurer.mutate_single_field(brief, "non_existent_field", "Yeni Değer")

    with pytest.raises(ValueError):
        structurer.mutate_single_field(brief, "color", "")


def test_single_variable_experiment(tmp_path):
    """Staj Defteri Yaprak 56: Tek değişkenli kontrollü karşılaştırma çalıştırmasını test eder."""
    comparator = ComparatorEngine()
    brief = StructuredDesignBrief(
        brief_id="BRF-MUT-EXP",
        style="Klasik Osmanlı",
        motif="Barok Madalyon",
        color="Krem Fildişi",
        seed=42
    )

    comp_res, images = comparator.run_single_variable_experiment(
        base_brief=brief,
        field_to_change="color",
        new_values=["Gece Laciverti Zemin"],
        output_dir=tmp_path
    )

    assert comp_res.experiment_type == ExperimentType.SINGLE_VARIABLE_MUTATION
    assert len(comp_res.runs) == 2 # 1 baz + 1 mutasyon
    assert len(images) == 2
    # Seed aynı kalmalı
    assert comp_res.runs[0].seed == comp_res.runs[1].seed == 42
    assert comp_res.runs[1].mutated_field == "color"


# ==============================================================================
# 4. YAPRAK 56: TEKRARLANABİLİRLİK DOĞRULAMA VE LOGLAMA TESTLERİ
# ==============================================================================

def test_reproducibility_verification_success():
    """Staj Defteri Yaprak 56: Aynı seed ve prompt ile MSE = 0.0 teyidini test eder."""
    comparator = ComparatorEngine()
    brief = StructuredDesignBrief(
        brief_id="BRF-VERIF",
        style="Modern Geometrik",
        motif="Prizma",
        color="Taş Grisi",
        seed=77
    )
    verif_res = comparator.verify_reproducibility(brief)
    assert verif_res.is_identical is True
    assert verif_res.pixel_mse == 0.0
    assert "TEKRARLANABİLİRLİK DOĞRULANDI" in verif_res.verdict


def test_experiment_logging(tmp_path):
    """Her çıkarımın parametreleriyle birlikte loglandığını test eder."""
    controller = SDXLController()
    controller.log_file = tmp_path / "test_log.json"

    brief = StructuredDesignBrief(
        brief_id="BRF-LOG",
        style="Klasik",
        motif="Madalyon",
        color="Krem",
        seed=99
    )
    controller.generate(brief, output_path=tmp_path / "log_test.png")

    assert controller.log_file.exists()
    with open(controller.log_file, "r", encoding="utf-8") as f:
        logs = json.load(f)
    assert len(logs) == 1
    assert logs[0]["brief_id"] == "BRF-LOG"
    assert logs[0]["seed"] == 99
    assert logs[0]["scheduler"] == "EulerDiscreteScheduler"


# ==============================================================================
# 5. GÖRSELLEŞTİRME PANELLERİ TESTLERİ (300 DPI)
# ==============================================================================

def test_visualizer_seed_variation_grid(tmp_path):
    """300 DPI seed varyasyon panelinin oluşturulmasını ve dosya boyutunu test eder."""
    comparator = ComparatorEngine()
    visualizer = Day28Visualizer(dpi=150) # Hızlı test için 150 DPI

    brief = StructuredDesignBrief(
        brief_id="BRF-VIS-SEED",
        style="Klasik Osmanlı",
        motif="Madalyon",
        color="Krem ve Bordo",
        seed=42
    )
    comp_res, images = comparator.run_seed_variation_experiment(
        base_brief=brief,
        seeds=[42, 108],
        output_dir=tmp_path
    )
    panel_file = tmp_path / "test_seed_grid.png"
    visualizer.plot_seed_variations(comp_res, images, panel_file)

    assert panel_file.exists()
    assert panel_file.stat().st_size > 20 * 1024


def test_visualizer_single_variable_comparison(tmp_path):
    """300 DPI tek değişkenli karşılaştırma panelinin oluşturulmasını test eder."""
    comparator = ComparatorEngine()
    visualizer = Day28Visualizer(dpi=150)

    brief = StructuredDesignBrief(
        brief_id="BRF-VIS-MUT",
        style="Klasik Osmanlı",
        motif="Madalyon",
        color="Krem",
        seed=42
    )
    comp_res, images = comparator.run_single_variable_experiment(
        base_brief=brief,
        field_to_change="color",
        new_values=["Gece Laciverti"],
        output_dir=tmp_path
    )
    panel_file = tmp_path / "test_mut_panel.png"
    visualizer.plot_single_variable_comparison(comp_res, images, panel_file)

    assert panel_file.exists()
    assert panel_file.stat().st_size > 20 * 1024
