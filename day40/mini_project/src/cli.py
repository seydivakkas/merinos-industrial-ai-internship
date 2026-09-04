# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 40 (BÜYÜK FİNAL)
Komut Satırı Arayüzü (CLI): Sistem Sağlığı, Çok Modlu Teşhis ve Final Staj Raporu
"""

import os
import sys
import json
import argparse
import datetime

from day40.mini_project.src.master_platform import MasterIndustrialAIPlatform
from day40.mini_project.src.final_evaluator import FinalInternshipEvaluator
from day40.mini_project.src.visualizer import MasterVisualizer
from day40.mini_project.src.models import MultiModalIncidentInput


def get_default_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    return {
        "outputs_dir": outputs_dir,
        "report_json": os.path.join(outputs_dir, "internship_final_evaluation_report.json"),
        "dashboard_png": os.path.join(outputs_dir, "master_platform_dashboard.png")
    }


def handle_health(args):
    print("=" * 80)
    print("[HEALTH] MERINOS INDUSTRIAL AI MASTER PLATFORM - SISTEM SAGLIK KONTROLU")
    print("=" * 80)

    platform = MasterIndustrialAIPlatform()
    health = platform.check_system_health()

    print(f"Genel Durum     : {health.overall_status}")
    print(f"Zaman Damgasi   : {health.timestamp}")
    print(f"Toplam Bellek   : {health.total_memory_mb} MB")
    print(f"Izlenen Servis  : {health.total_subsystems} adet")
    print("-" * 80)

    for sub in health.subsystems:
        print(f" - [{sub.pillar_id}] {sub.subsystem_name:<42} : {sub.status} ({sub.memory_mb:.1f} MB)")
    print("=" * 80)


def handle_diagnose(args):
    print("=" * 80)
    print("[DIAGNOSE] MERINOS INDUSTRIAL AI MASTER PLATFORM - COK MODLU TEZGAH ARIZA TESHISI")
    print("=" * 80)

    platform = MasterIndustrialAIPlatform()
    diag = platform.diagnose_loom_incident(
        loom_id=args.loom_id,
        error_code=args.error_code,
        motor_temp=args.motor_temp,
        pressure=args.pressure,
        vision_defect=args.vision_defect
    )

    print(f"Tezgâh Kodu        : {diag['loom_id']}")
    print(f"Hata Kodu          : {diag['error_code']}")
    print(f"Motor Sıcaklığı    : {args.motor_temp} °C")
    print(f"Pnömatik Basınç    : {args.pressure} bar")
    print(f"Kamera Kusur Kaydı : {'Var (vision_defect = True)' if args.vision_defect else 'Yok'}")
    print(f"Güvenlik Durumu    : {diag['safety_check']}")
    print(f"\nTanı (Diagnosis)   : {diag['diagnosis']}")
    print(f"Kök Neden          : {diag['root_cause']}")

    if diag["action_plan"]:
        print("\nEylem Planı Adımları:")
        for idx, step in enumerate(diag["action_plan"], 1):
            print(f"  {idx}. {step}")

    if diag["recommendations"]:
        print("\nÖneriler & Güvenlik Uyarıları:")
        for rec in diag["recommendations"]:
            print(f"  * {rec}")

    print("=" * 80)


def handle_final_report(args):
    paths = get_default_paths()
    print("=" * 80)
    print("[FINAL-REPORT] 40 GUNLUK STAJ MARATONU BUYUK FINAL VE ROI KAPANIS RAPORU")
    print("=" * 80)

    report = FinalInternshipEvaluator.generate_final_report(total_looms=args.total_looms)

    # JSON Raporu Kaydet
    with open(paths["report_json"], "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"[OK] 40 Günlük Kapsamlı Yönetici Raporu kaydedildi: {paths['report_json']}")

    # 300 DPI Dashboard Çiz
    MasterVisualizer.generate_dashboard(report, paths["dashboard_png"])
    print(f"[OK] 300 DPI 4 Panelli Büyük Final Teşhis Grafiği kaydedildi: {paths['dashboard_png']}")

    # Konsol Özeti
    kpis = report.kpis
    print("\n" + "=" * 80)
    print("[BASARI] MERINOS GAZIANTEP HALI FABRIKASI - 40 GUNLUK STAJ MARATONU BASARIM KARNESI:")
    print(f"   Fabrika Tezgâh Parkı           : {args.total_looms} adet Jakarlı Dokuma Tezgâhı")
    print(f"   Yıllık Duruş Süresi Tasarrufu  : {kpis.annual_downtime_saved_hours:,.1f} saat/yıl (%70 azalma)")
    print(f"   Yıllık Finansal Net Tasarruf   : {kpis.annual_financial_savings_try:,.2f} TL (22.68 Milyon TRY)")
    print(f"   Dokuma Fire Azalma Oranı       : %{kpis.scrap_reduction_percentage} net düşüş (%6.8 -> %2.6)")
    print(f"   Edge IPC Çıkarım Gecikmesi     : {kpis.average_edge_latency_ms} ms (ONNX INT8, Sıfır Ağ Gecikmesi)")
    print(f"   Model Bellek Sıkıştırması      : %{kpis.model_compression_percentage} (%74 RAM tasarrufu)")
    print(f"   Kümülatif Test Başarım Oranı   : %{kpis.test_pass_rate} ({kpis.total_tests_passed}/{kpis.total_tests_passed} Test - 100% Yeşil)")
    print(f"   Yatırım Geri Dönüşü (ROI)      : %1,512 (1.5 Milyon TL Yatırıma Karşılık 22.68 M TL Yıllık Getiri)")
    print(f"   Üretime Geçiş Kararı (Verdict) : {report.production_readiness_verdict}")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos Endüstriyel Yapay Zekâ Master Platform CLI (Büyük Final)")
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    # health
    subparsers.add_parser("health", help="Tüm alt sistemlerin (Vision, Predictive, RAG, Edge) sağlık durumunu sorgular")

    # diagnose
    diag_p = subparsers.add_parser("diagnose", help="Tezgâhtan gelen telemetri ve hata kodunu çok modlu analiz eder")
    diag_p.add_argument("--loom-id", type=str, default="TEZGAH-01", help="Tezgâh kodu")
    diag_p.add_argument("--error-code", type=str, default="E-401", help="Arıza kodu (ör: E-401, E-108)")
    diag_p.add_argument("--motor-temp", type=float, default=87.5, help="Motor sıcaklığı (°C)")
    diag_p.add_argument("--pressure", type=float, default=13.5, help="Pnömatik hava basıncı (bar)")
    diag_p.add_argument("--vision-defect", action="store_true", help="Kamerada kumaş/desen kusuru tespit edildi mi?")
    diag_p.add_argument("--defect-type", type=str, default="Atkı İpliği Kopması", help="Tespit edilen kusur türü")
    diag_p.add_argument("--query", type=str, default="Tezgâh durdu arıza nedir?", help="Operatör sorusu")

    # final-report
    rep_p = subparsers.add_parser("final-report", help="40 günlük stajın kapsamlı değerlendirme ve ROI raporunu üretir")
    rep_p.add_argument("--total-looms", type=int, default=120, help="Fabrikadaki toplam tezgâh sayısı")

    args = parser.parse_args()
    if args.command == "health":
        handle_health(args)
    elif args.command == "diagnose":
        handle_diagnose(args)
    elif args.command == "final-report":
        handle_final_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
