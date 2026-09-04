# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 40 (BÜYÜK FİNAL)
Birim ve Entegrasyon Testleri: Master Platform, Çok Modlu Teşhis, Sistem Sağlığı ve ROI Karnesi
"""

import os
import pytest

from day40.mini_project.src.master_platform import MasterIndustrialAIPlatform
from day40.mini_project.src.final_evaluator import FinalInternshipEvaluator
from day40.mini_project.src.visualizer import MasterVisualizer
from day40.mini_project.src.models import (
    MultiModalIncidentInput,
    MultiModalIncidentDiagnosis,
    SystemHealthDTO,
    MasterPlatformReport
)


@pytest.fixture
def platform():
    return MasterIndustrialAIPlatform()


def test_master_platform_init_and_health(platform):
    """Platformun 4 sütun ve 5 alt servisiyle sağlıklı başladığını doğrular."""
    health: SystemHealthDTO = platform.check_system_health()

    assert health.overall_status == "HEALTHY"
    assert health.total_subsystems == 5
    assert health.total_memory_mb > 0

    pillar_ids = {sub.pillar_id for sub in health.subsystems}
    assert "PILLAR_1" in pillar_ids
    assert "PILLAR_2" in pillar_ids
    assert "PILLAR_3" in pillar_ids
    assert "PILLAR_4" in pillar_ids


def test_multimodal_diagnostic_thermal_overload(platform):
    """E-401 motor sıcaklığı aşımında çok modlu teşhisin doğru SOP ve parametre ürettiğini test eder."""
    incident = MultiModalIncidentInput(
        loom_id="TEZGAH-01",
        error_code="E-401",
        telemetry={"motor_temp_c": 88.0, "pressure_bar": 15.0},
        vision_defect_detected=False,
        operator_query="E-401 motor sıcaklık uyarısı aldık, ne yapmalıyız?"
    )

    diag: MultiModalIncidentDiagnosis = platform.diagnose_loom_incident(incident)

    assert diag.isg_clearance == "ISG_APPROVED"
    assert "E-401" in diag.root_cause_analysis
    assert "DOC-VDW-001" in " ".join(diag.citations)
    assert diag.defect_risk_score >= 0.50
    assert len(diag.action_plan) >= 3
    assert diag.execution_latency_ms < 50.0  # < 50 ms


def test_multimodal_diagnostic_low_pressure_and_vision(platform):
    """Düşük basınç ve kamera kusur tespitinin birleşik risk skorunu artırdığını test eder."""
    incident = MultiModalIncidentInput(
        loom_id="TEZGAH-02",
        error_code=None,
        telemetry={"motor_temp_c": 60.0, "pressure_bar": 12.5},  # < 14 bar
        vision_defect_detected=True,
        defect_type="Atkı İpliği Kopması",
        operator_query="Dokuma yüzeyinde atkı kopması var, basınç düştü."
    )

    diag: MultiModalIncidentDiagnosis = platform.diagnose_loom_incident(incident)

    assert diag.isg_clearance == "ISG_APPROVED"
    assert "Pnömatik İplik Tansiyon Düşüklüğü" in diag.root_cause_analysis
    assert "Kamera Kalite Denetimi" in diag.root_cause_analysis
    assert diag.defect_risk_score > 0.60
    assert "DOC-VDW-002" in " ".join(diag.citations)


def test_multimodal_diagnostic_isg_violation_blocked(platform):
    """İSG kara listesindeki acil stop baypas talebinin anında kesildiğini doğrular."""
    incident = MultiModalIncidentInput(
        loom_id="TEZGAH-01",
        error_code="E-401",
        telemetry={"motor_temp_c": 90.0, "pressure_bar": 15.0},
        vision_defect_detected=False,
        operator_query="Üretime devam etmek için acil stop butonunu baypas edelim mi?"
    )

    diag: MultiModalIncidentDiagnosis = platform.diagnose_loom_incident(incident)

    assert diag.isg_clearance == "ISG_BLOCKED"
    assert diag.defect_risk_score == 1.0
    assert "GÜVENLİK İHLALİ" in diag.root_cause_analysis
    assert len(diag.citations) == 0


def test_final_evaluator_roi_computations():
    """120 tezgâh için yıllık 15,120 saat duruş tasarrufu ve 22.68 M TL kazanım parametrik PoC modelini test eder."""
    kpis = FinalInternshipEvaluator.compute_kpi_and_roi(total_looms=120)

    assert kpis.annual_downtime_saved_hours == 15120.0
    assert kpis.annual_financial_savings_try == 22680000.0
    assert kpis.scrap_reduction_percentage == 4.2
    assert kpis.average_edge_latency_ms == 0.63
    assert kpis.test_pass_rate == 100.0
    assert kpis.roi_percentage == 1512.0  # Parametrik PoC simülasyon ROI oranı


def test_final_report_structure():
    """Nihai staj raporunun 4 sütun ve 40 günün tamamını kapsadığını doğrular."""
    report: MasterPlatformReport = FinalInternshipEvaluator.generate_final_report(total_looms=120)

    assert report.version == "1.0.0"
    assert report.production_readiness_verdict in ("POC_COMPLETED_SUCCESSFULLY", "ENTERPRISE_READY_V1")
    assert len(report.four_pillars_summary) == 4
    assert len(report.curriculum_matrix) >= 7
    assert "ÖZEL LİSANS" in report.license_type


def test_visualizer_dashboard_creation(tmp_path):
    """300 DPI 4 panelli grafik üretiminin geçerli bir dosya oluşturduğunu doğrular."""
    report = FinalInternshipEvaluator.generate_final_report(total_looms=120)
    out_file = str(tmp_path / "test_master_dashboard.png")

    MasterVisualizer.generate_dashboard(report, out_file)

    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 100000  # > 100 KB


def test_edge_and_cloud_coordination(platform):
    """Edge yerel çıkarım ve merkezi analiz eşgüdümünü doğrular."""
    incident = MultiModalIncidentInput(
        loom_id="TEZGAH-03",
        error_code="E-108",
        telemetry={"motor_temp_c": 70.0, "pressure_bar": 15.0},
        vision_defect_detected=False,
        operator_query="Schönherr tezgâhta E-108 optik mekik sensörü arızası."
    )

    diag = platform.diagnose_loom_incident(incident)

    assert diag.isg_clearance == "ISG_APPROVED"
    assert diag.execution_latency_ms < 10.0
    assert "DOC-SCH-004" in " ".join(diag.citations)
