"""
Merinos Industrial AI Internship - Day 29
Phase 1 Data Lake Collector, Internet Harvester & SAP PM Maintenance History Generator.

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
"""

from __future__ import annotations
from datetime import datetime, timedelta
import json
from pathlib import Path
import random
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from day29.mini_project.src.models import (
    ISO14224TaxonomyNode,
    ISO14224FailureRecord,
    ReliabilityMetrics
)


class OpenTechnicalSource(BaseModel):
    """İnternet üzerinde taranabilir açık üretici ve mühendislik dokümantasyon kaynağı."""
    manufacturer: str
    equipment_family: str
    doc_type: str
    title: str
    online_url: str
    format: str = "PDF"
    access_protocol: str = Field(default="PUBLIC_WEB", description="PUBLIC_WEB, OEM_PORTAL, PATENT_INDEX")
    verified_checksum_or_id: Optional[str] = None


class SyntheticSapPmRecord(BaseModel):
    """SAP PM modülünden çekilen 5 yıllık kurumsal iş emri ve arıza geçmiş kaydı."""
    model_config = ConfigDict(populate_by_name=True)

    notification_id: str = Field(description="IW21 Bildirim Numarası (Örn: IW21-2024-88412)")
    work_order_id: str = Field(description="IW32 İş Emri Numarası (Örn: IW32-4500912)")
    order_id: str = Field(default="", description="İş emri ana kodu")
    functional_location: str = Field(description="ISO 14224 Hiyerarşik Konum (Örn: MER-T01-LN-W02-VDW-14)")
    machine_name: str
    department: str
    timestamp: str
    downtime_minutes: float
    mtbf_hours: float = 324.5
    mttr_hours: float = 0.75
    symptom: str
    failure_mode_code: str
    root_cause_analysis: str
    corrective_action_performed: str
    parts_consumed: List[Dict[str, Any]]
    labor_hours: float
    loto_applied: bool = True
    loto_required: bool = True
    teco_technician_notes: str
    technician_log: str = ""
    status: str = "TECO"
    teco_status: str = "TECO_COMPLETED"


class MobileMaintenanceTicket(BaseModel):
    """Faz 4: Sahadaki teknisyenlerin telefonlarından gönderilen canlı arıza bildirim modeli."""
    model_config = ConfigDict(populate_by_name=True)

    ticket_id: str = Field(default="MOB-TKT-1001", description="Mobil bilet kimliği")
    device_id: str = Field(description="Teknisyen mobil cihaz ID (IMEI / Cihaz Token)")
    technician_name: str
    shift: str = "VARDIYA_1"
    scanned_qr_code: str = Field(description="Tezgah üzerindeki DataMatrix/QR etiketinden okunan kod")
    loom_id: Optional[str] = None
    voice_note_transcription: Optional[str] = None
    manual_symptom_text: str
    sap_notification_id: Optional[str] = None
    captured_photo_path: Optional[str] = None
    safety_gate_status: str = Field(default="LOTO_ISOLATION_REQUIRED", description="LOTO doğrulama durumu")
    loto_checklist_verified: bool = False



class DataLakeCollectorEngine:
    """
    Faz 1 Veri Gölü ve Sayısallaştırma Motoru:
    1. Açık web ve OEM portallarından teknik dokümantasyon indeksleme.
    2. Son 5 yıllık sentetik ve gerçeğe dayalı SAP PM arıza geçmişi üretimi.
    3. Hiyerarşik veri gölü dizinleme ve bölümleme (partitioning).
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent
        self.data_lake_dir = self.base_dir / "data_lake"
        self.fixtures_dir = self.base_dir / "fixtures"

        self.data_lake_dir.mkdir(parents=True, exist_ok=True)
        (self.data_lake_dir / "raw_manuals").mkdir(parents=True, exist_ok=True)
        (self.data_lake_dir / "schematics").mkdir(parents=True, exist_ok=True)
        (self.data_lake_dir / "sap_pm_history").mkdir(parents=True, exist_ok=True)
        (self.data_lake_dir / "hmi_fault_codes").mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_curated_internet_sources() -> List[OpenTechnicalSource]:
        """İnternetten çekilebilecek ve RAG sistemine beslenebilecek doğrulanmış açık doküman URL kataloğu."""
        return [
            OpenTechnicalSource(
                manufacturer="Vandewiele",
                equipment_family="RCE / RCE2+ / RCF Carpet Weaving",
                doc_type="Product_Brochure_Technical_Overview",
                title="Advanced Carpet Weaving Technology - RCE2+ Technical Brief",
                online_url="https://vandewiele.com/weaving/carpet-weaving/rce2+",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="BRO_VDW_RCE2+_EN"
            ),
            OpenTechnicalSource(
                manufacturer="Vandewiele",
                equipment_family="Fast Creel & Atkı Besleme",
                doc_type="Engineering_Patent_Specification",
                title="Rapier Drive and Shed Formation Kinematic Control (Google Patents)",
                online_url="https://patents.google.com/?q=Vandewiele+carpet+rapier+gripper",
                format="PDF/HTML",
                access_protocol="PATENT_INDEX",
                verified_checksum_or_id="EP2418312B1"
            ),
            OpenTechnicalSource(
                manufacturer="Superba",
                equipment_family="TVP3 / TVP2S Saturated Steam Heat-Setting",
                doc_type="Technical_Specification_Datasheet",
                title="Superba Continuous Yarn Heat-Setting Process & Pressure Chamber Overview",
                online_url="https://superba.com/en/downloads",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="SUP-TVP3-SPEC-2024"
            ),
            OpenTechnicalSource(
                manufacturer="Saurer Volkmann",
                equipment_family="CarpetCabler / CarpetTwister",
                doc_type="System_Overview_Brochure",
                title="Two-for-One Twisting and Direct Cabling for Carpet Yarns",
                online_url="https://saurer.com/en/services",
                format="PDF",
                access_protocol="OEM_PORTAL",
                verified_checksum_or_id="SAU-VOLK-VTS-EN"
            ),
            OpenTechnicalSource(
                manufacturer="Siemens",
                equipment_family="SIMATIC S7-1500 & ET 200SP",
                doc_type="OEM_Hardware_Manual",
                title="SIMATIC S7-1500 / ET 200SP Diagnostics and Profinet IO Manual",
                online_url="https://support.industry.siemens.com/cs/document/59191792",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="SIOS-S71500-DIAG-V18"
            ),
            OpenTechnicalSource(
                manufacturer="Lenze",
                equipment_family="Lenze 9400 HighLine Servo",
                doc_type="Electronic_Drive_Manual",
                title="Lenze 9400 Servo Inverter Hardware Manual & Error Codes",
                online_url="https://download.lenze.com/file.php?file=9400_Hardware_Manual_en",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="LENZE-9400-HW-EN"
            ),
            OpenTechnicalSource(
                manufacturer="Atlas Copco",
                equipment_family="ZR / ZT Oil-Free Air Compressors",
                doc_type="Service_Manual",
                title="Atlas Copco ZR 110-750 Rotary Screw Oil-Free Air Compressor Manual",
                online_url="https://www.atlascopco.com/compressors/manuals",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="AC-ZR-SERIES-MANUAL"
            ),
            OpenTechnicalSource(
                manufacturer="Brückner",
                equipment_family="Ramöz Kurutma & Apre Fırını",
                doc_type="Thermal_Finishing_Overview",
                title="Brückner POWER-FRAME Stenter Line Technical Data",
                online_url="https://www.brueckner-textil.de/en/products/stenter-frames",
                format="PDF",
                access_protocol="PUBLIC_WEB",
                verified_checksum_or_id="BRK-PF-STENTER-2023"
            )
        ]

    def generate_synthetic_sap_pm_history(
        self,
        num_records: int = 120,
        start_year: int = 2021,
        end_year: int = 2026
    ) -> List[SyntheticSapPmRecord]:
        """
        Merinos Gaziantep tesislerinin son 5 yıllık SAP PM bakım geçmişini üretir.
        Gerekçe: Sahada 100.000+ sayfalık orijinal dokümanlar ve gizli SAP arşivi bulunmadığında,
        gerçek saha parametreleriyle zenginleştirilmiş kurumsal arıza verisi simüle edilir.
        """
        random.seed(42)  # Tekrarlanabilir simülasyon
        machines = [
            ("VDW-RCE2-14", "Van de Wiele RCE2+", "DOKUMA", "MER-T01-LN-W02-VDW-14"),
            ("VDW-RCF-03", "Van de Wiele RCF", "DOKUMA", "MER-T01-LN-W01-VDW-03"),
            ("SCH-ALP-07", "Schönherr ALPHA 500", "DOKUMA", "MER-T01-LN-W03-SCH-07"),
            ("SUP-TVP-02", "Superba TVP3 Fikse Tüneli", "IPLIK_BCF", "MER-T01-LN-Y01-SUP-02"),
            ("SAU-VOL-11", "Saurer Volkmann VTS-08", "IPLIK_BCF", "MER-T01-LN-Y02-SAU-11"),
            ("BRK-RAM-01", "Brückner Ramöz Fikse Fırını", "RAMOZ_TERBIYE", "MER-T01-LN-F01-BRK-01"),
            ("MON-LAT-04", "Mondomix Lateks Köpük Hattı", "RAMOZ_TERBIYE", "MER-T01-LN-F02-MON-04"),
            ("VOL-SHE-02", "Vollenweider Halı Tıraş Makinesi", "KONFEKSIYON", "MER-T01-LN-K01-VOL-02")
        ]

        scenarios = [
            {
                "symptom": "Sol verici rapyerden sağ alıcı rapyere atkı devir-teslim kaçırması",
                "failure_mode": "MEC-TRN-BRK",
                "root_cause": "Kıskaç mandal yayının yorulması ve kılavuz tırnak aşınması (>0.08 mm).",
                "action": "Sentil çakısıyla buluşma açıklığı 0.35 mm'ye getirildi; aşınan tırnaklar yenilendi.",
                "parts": [{"part_code": "MRP-RAP-101", "qty": 1, "name": "Rapyer Kıskacı"}],
                "downtime": 42.0,
                "labor": 1.5,
                "notes": "LOTO uygulandı, ana motor şalteri kilitlendi. 180° ana mil açısı inching ile doğrulandı."
            },
            {
                "symptom": "Döner hav bıçağında körelme ve alt-üst halı ayrımında lif saçaklanması",
                "failure_mode": "MEC-CUT-DUL",
                "root_cause": "Otomatik elmas bileyici taşının aşınması ve kayış gevşemesi.",
                "action": "Bileme taşı 15° açıyla sıfırlandı, traverse rayına kuru PTFE sprey uygulandı.",
                "parts": [{"part_code": "MRP-BIC-305", "qty": 1, "name": "Hav Kesme Döner Bıçağı"}],
                "downtime": 28.0,
                "labor": 1.0,
                "notes": "Bıçak dönüş motoru izole edildi, acil durdurma kilidi takıldı."
            },
            {
                "symptom": "SCADA ekranında Profinet Rack 2 Drop hatası ve aniden acil duruş",
                "failure_mode": "ELC-NET-TMO",
                "root_cause": "ET 200SP panosundaki Ethernet kablosunda motor kablosundan kaynaklı EMI paraziti.",
                "action": "Cat6 STP kablo sinyal tavasına alındı, TIA Portal watchdog süresi 100 ms yapıldı.",
                "parts": [{"part_code": "MRP-PLC-622", "qty": 1, "name": "ET 200SP Profinet Modülü"}],
                "downtime": 35.0,
                "labor": 1.2,
                "notes": "Topraklama barası direnci ölçüldü (< 0.1 Ohm), klemensler sıkıldı."
            },
            {
                "symptom": "Buhar tüneli giriş kilit contasından yoğun doymuş buhar tahliyesi",
                "failure_mode": "MEC-SEA-LKE",
                "root_cause": "140°C buhar altında dudak contasının termal sertleşmesi ve yırtılması.",
                "action": "Tünel çift vana ile blöflendi, soğuma beklendi, yeni conta kiti takıldı.",
                "parts": [{"part_code": "EE106144", "qty": 2, "name": "Superba Basınç Contası"}],
                "downtime": 75.0,
                "labor": 2.5,
                "notes": "Çift blöf körleme ve manometre sıfır basınç testi yapılmadan kapak açılmadı."
            },
            {
                "symptom": "Jakar 4. çerçevede lingo düşmesi ve desen çizgi hatası",
                "failure_mode": "ELC-MOD-SHR",
                "root_cause": "Solenoid bobin aşırı ısınması ve lingo geri çekme yayının kopması.",
                "action": "Bobin direnci 45 Ohm doğrulandı, kopuk lingo yayı yenilendi.",
                "parts": [{"part_code": "MRP-YAY-112", "qty": 4, "name": "Lingo Geri Çekme Yayı"}],
                "downtime": 22.0,
                "labor": 0.8,
                "notes": "Jakar kafa yağ seviyesi ISO VG 68 kontrol edildi."
            }
        ]

        records: List[SyntheticSapPmRecord] = []
        base_time = datetime(start_year, 1, 15, 8, 30)

        for i in range(num_records):
            mac_code, mac_name, dept, func_loc = random.choice(machines)
            scen = random.choice(scenarios)

            # Rastgele tarih üretimi
            day_offset = random.randint(0, (end_year - start_year) * 365)
            hour_offset = random.randint(0, 23)
            rec_date = base_time + timedelta(days=day_offset, hours=hour_offset)

            notif_id = f"IW21-{rec_date.year}-{10000 + i}"
            wo_id = f"IW32-{4500000 + i}"

            record = SyntheticSapPmRecord(
                notification_id=notif_id,
                work_order_id=wo_id,
                order_id=wo_id,
                functional_location=func_loc,
                machine_name=mac_name,
                department=dept,
                timestamp=rec_date.strftime("%Y-%m-%d %H:%M:%S"),
                downtime_minutes=round(scen["downtime"] * random.uniform(0.85, 1.25), 1),
                mtbf_hours=round(random.uniform(280.0, 360.0), 1),
                mttr_hours=round(scen["labor"], 2),
                symptom=f"{mac_name}: {scen['symptom']}",
                failure_mode_code=scen["failure_mode"],
                root_cause_analysis=scen["root_cause"],
                corrective_action_performed=scen["action"],
                parts_consumed=scen["parts"],
                labor_hours=round(scen["labor"] * random.uniform(0.9, 1.2), 1),
                loto_applied=True,
                loto_required=True,
                teco_technician_notes=f"TECO Kapanış Onayı: {scen['notes']} Bakım Şefi: K. Özdemir (Sicil: 4108).",
                technician_log=f"TECO Kapanış Onayı: {scen['notes']} Bakım Şefi: K. Özdemir (Sicil: 4108).",
                status="TECO",
                teco_status="TECO_COMPLETED"
            )
            records.append(record)

        # Tarihe göre sırala
        records.sort(key=lambda r: r.timestamp)

        # JSON olarak kaydet
        out_file = self.fixtures_dir / "merinos_sap_pm_history.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in records], f, ensure_ascii=False, indent=2)

        return records

    def get_open_technical_sources(self) -> List[OpenTechnicalSource]:
        """Açık teknik kaynak kataloğunu döndürür."""
        return self.get_curated_internet_sources()

    def create_mobile_ticket(
        self,
        loom_id: str,
        technician: str,
        symptom: str,
        sap_notification_id: str = "IW21-TEMP",
        shift: str = "VARDIYA_1",
        loto_verified: bool = False
    ) -> MobileMaintenanceTicket:
        """Faz 4 Mobil uygulama üzerinden arıza bileti oluşturur."""
        tkt_id = f"MOB-TKT-{random.randint(10000, 99999)}"
        safety_status = "LOTO_ISOLATION_VERIFIED" if loto_verified else "LOTO_ISOLATION_REQUIRED"
        return MobileMaintenanceTicket(
            ticket_id=tkt_id,
            device_id=f"DEV-{loom_id}",
            technician_name=technician,
            shift=shift,
            scanned_qr_code=f"QR-{loom_id}-4.OSB",
            loom_id=loom_id,
            manual_symptom_text=symptom,
            sap_notification_id=sap_notification_id,
            safety_gate_status=safety_status,
            loto_checklist_verified=loto_verified
        )

    def populate_data_lake_documents(self) -> Dict[str, int]:
        """
        Veri gölü klasörlerine fiziksel teknik kılavuz, şema ve hata kodu belgelerini yazar.
        Gerekçe: OEM portalları şasi numarasıyla kapalı olduğunda, sahadaki mühendislik ve patent
        bilgileri RAG arama motorunun ve Docling'in okuyabileceği yapılandırılmış dokümanlara dönüştürülür.
        """
        raw_dir = self.data_lake_dir / "raw_manuals"
        sch_dir = self.data_lake_dir / "schematics"
        hmi_dir = self.data_lake_dir / "hmi_fault_codes"

        # 1. Vandewiele RCE2+ Teknik Servis El Kitabı
        vdw_content = """# Vandewiele RCE2+ / RCF Çift Rapyerli Halı Dokuma Tezgâhı Teknik Bakım Kılavuzu
## Merinos Gaziantep 4. OSB Dokuma Salonu 2 Bakım Dokümantasyonu
**Doküman ID:** OEM-VDW-RCE2-DOC-2024
**Sistem:** Yüksek Hızlı Çift Parça (Face-to-Face) Elektronik Jakarlı Halı Tezgâhı

### 1. Mekanik Kinematik ve Rapyer Devir-Teslim Ayarları
- **Buluşma Açıklığı (Gripper Clearance):** Verici rapyer (sol) ve alıcı rapyer (sağ) tezgâh merkezinde 180° ana mil açısında buluşur. Sentil çakısıyla ölçülen tırnak açıklığı **0.35 mm ± 0.03 mm** olmalıdır.
- **Aşınma Toleransı:** Rapyer alüminyum kılavuz rayı ve polyamid tırnak aşınması en fazla **0.08 mm** olabilir. Bu değer aşıldığında atkı kaçırma (MEC-TRN-BRK) arızası oluşur.
- **Sıkma Torkları:** Kıskaç tespit civataları (M8 x 1.25) tork anahtarı ile **24 Nm** torkla sıkılmalıdır.

### 2. Döner Hav Kesme Bıçağı (Pile Knife System)
- **Bileme Açısı:** Hav kesme döner bıçağı 15° elmas taşlama açısıyla bilenmelidir.
- **Traverse Rayı Yağlaması:** Sıvı yağ hav tozlarını yapıştıracağından dolayı kılavuz çubuğuna kuru PTFE teflon sprey uygulanmalıdır.

### 3. Yağlama Şartnamesi
- **Kam Kutusu (Cam Box):** ISO VG 68 tam sentetik dişli yağı kullanılmalıdır. Yağ değişim periyodu 4000 çalışma saatidir.
- **Merkezi Gres Pompası:** NLGI Sınıf 2 lityum kompleks gres. Günlük 1.5 cm³ enjeksiyon.

### 4. İSG ve LOTO (Kilitleme/Etiketleme) Zorunluluğu
- Rapyer alanına veya jakar harness bölgesine yapılacak tüm müdahalelerde Q1 ana enerji şalteri asma kilitle kilitlenmeli, tezgâh panosuna LOTO bilgi kartı asılmalıdır.
"""
        (raw_dir / "VDW_RCE2_Rapier_Carpet_Loom_Manual.md").write_text(vdw_content, encoding="utf-8")

        # 2. Superba TVP3 Doymuş Buhar Fikse Tüneli Servis Kılavuzu
        sup_content = """# Superba TVP3 Sürekli İplik Doymuş Buhar Fikse ve Basınç Tüneli Bakım Prosedürü
## Merinos BCF İplik Tesisleri
**Doküman ID:** SUP-TVP3-MAINT-2024
**Sistem:** Doymuş Buhar Termal İplik Fikseleme (Heat-Setting)

### 1. Basınç Odası ve Kilit Contası Değişimi
- **Çalışma Basıncı:** 2.5 - 5.5 bar doymuş buhar, çalışma sıcaklığı 135°C - 145°C.
- **Giriş Dudak Contası (Lip Seal EE106144):** Contalar her 720 çalışma saatinde kontrol edilmeli, termal sertleşme veya mikro-yırtılma görüldüğünde değiştirilmelidir.
- **Güvenlik Blöfü:** Basınç odası kapağı açılmadan önce çift tahliye vanası açılmalı ve manometrenin 0.00 bar gösterdiği teyit edilmelidir.

### 2. Sıcaklık ve Basınç Sensörleri Kalibrasyonu
- PT100 sıcaklık transmitterleri 3 ayda bir kuru blok kalibratör ile ±0.5°C toleransla doğrulanmalıdır.
"""
        (raw_dir / "SUPERBA_TVP3_HeatSetting_Pressure_Tunnel_SOP.md").write_text(sup_content, encoding="utf-8")

        # 3. Saurer Volkmann VTS-08 İplik Büküm Kılavuzu
        sau_content = """# Saurer Volkmann VTS-08 Çift Büküm (Two-for-One) İplik Büküm Makinesi
## Merinos İplik Büküm Salonu
**Doküman ID:** SAU-VTS08-SPEC-2023

### 1. İğ Devri ve Kayış Gerginliği
- İğ devri 8000 - 9500 rpm aralığındadır. Tangential tahrik kayışı frekans ölçer (optik tansiyonmetre) ile 45 Hz gerginlik değerine ayarlanmalıdır.
- Seramik iplik kılavuz yüksüklerinde çentik oluşumu BCF filament kopuşuna neden olur.
"""
        (raw_dir / "SAURER_VOLKMANN_VTS08_CarpetTwister_Guide.md").write_text(sau_content, encoding="utf-8")

        # 4. Siemens S7-1500 & Profinet Teşhis Kılavuzu
        sie_content = """# Siemens SIMATIC S7-1500 & ET 200SP Profinet Otomasyon ve Teşhis El Kitabı
**Doküman ID:** SIOS-S71500-DIAG-V18

### 1. Profinet Haberleşme ve Bus Hatası Giderme
- **Hata Modu ELC-NET-TMO:** ET 200SP rack haberleşme kesintisi.
- **Topraklama Direnci:** Pano içi bakır bara toprak direnci < 0.1 Ohm olmalıdır.
- **Kablo Ekranlama:** Cat6 STP ekran örgüsü klemens girişinde 360° bilezik kelepçe ile topraklanmalıdır.
- **OB82 / OB86 Teşhis Kesmeleri:** TIA Portal diagnostik bufferında istasyon kesintisi kontrol edilmelidir.
"""
        (raw_dir / "SIEMENS_S71500_ET200SP_Profinet_Diagnostics.md").write_text(sie_content, encoding="utf-8")

        # 5. Atlas Copco Yağsız Vidalı Kompresör Bakımı
        ac_content = """# Atlas Copco ZR 110-750 Yağsız Vidalı Hava Kompresörü Servis Kılavuzu
**Doküman ID:** AC-ZR-AIR-2023

### 1. Dokuma Salonu Basınçlı Hava Şebekesi
- Rapyer tezgâhları için çıkış basıncı 7.5 bar regüle edilmeli, çiğlenme noktası (dew point) +3°C altına inmemelidir.
- Yağsız hava filtresi partikül tutma: 0.01 mikron.
"""
        (raw_dir / "ATLAS_COPCO_ZR_OilFree_Compressor_Service.md").write_text(ac_content, encoding="utf-8")

        # 6. Schematics (Tek Hat ve Kinematik Şemalar)
        schematic_vdw = {
            "schematic_id": "SCH-VDW-RAP-01",
            "title": "Vandewiele RCE2+ Rapier Drive Kinematic Linkage & Shed Angle",
            "source": "Google Patents EP2418312B1 / Vandewiele Kinematics",
            "parameters": {
                "stroke_length_mm": 4200.0,
                "loom_speed_nominal_rpm": 180.0,
                "gripper_overlap_angle_deg": 180.0,
                "gripper_clearance_nominal_mm": 0.35,
                "clearance_tolerance_mm": 0.03,
                "cam_dwell_angle_deg": 65.0,
                "rapier_tape_material": "Carbon-Fiber Reinforced Polyepoxide",
                "pinion_module": 2.5
            }
        }
        with open(sch_dir / "SCHEMATIC_VDW_RCE2_RAPIER_KINEMATICS.json", "w", encoding="utf-8") as f:
            json.dump(schematic_vdw, f, ensure_ascii=False, indent=2)

        schematic_profinet = {
            "schematic_id": "SCH-SIE-PROFI-02",
            "title": "Dokuma Salonu 2 MRP Halka (Ring) Profinet Topolojisi",
            "source": "Siemens SIOS & TIA Portal Hardware Config",
            "topology": "Ring Redundancy (MRP Master: S7-1518F, MRP Clients: ET 200SP)",
            "devices": [
                {"id": "PLC-01", "ip": "192.168.10.1", "name": "CPU 1518F-4 PN/DP"},
                {"id": "ET200-W02-14", "ip": "192.168.10.24", "name": "VDW-RCE2-14 ET200SP Remote IO"},
                {"id": "DRV-SERVO-01", "ip": "192.168.10.51", "name": "Lenze 9400 Servo Inverter Atkı"}
            ]
        }
        with open(sch_dir / "SCHEMATIC_SIEMENS_PROFINET_RING_TOPOLOGY.json", "w", encoding="utf-8") as f:
            json.dump(schematic_profinet, f, ensure_ascii=False, indent=2)

        # 7. HMI Arıza Kodları Kataloğu
        vdw_faults = {
            "catalog_id": "VDW-VDIRECT-FAULT-CODES",
            "machine_family": "Vandewiele RCE2+ / RCF / VTR",
            "fault_codes": [
                {
                    "code": "ERR-RAP-05",
                    "hmi_message": "Left/Right Rapier Gripper Yarn Handover Failure",
                    "description": "Atkı ipliği sol verici rapyerden sağ alıcı rapyere aktarılamadı.",
                    "probable_cause": "Kıskaç mandal yay yorulması veya sentil açıklığı > 0.38 mm.",
                    "remedy": "Kıskaç sentil ayarını 0.35 mm'ye getiriniz, aşınan tırnakları yenileyiniz.",
                    "iso_failure_mode": "MEC-TRN-BRK"
                },
                {
                    "code": "ERR-BIC-07",
                    "hmi_message": "Pile Loop Cutting Blade Temperature or Dull Warning",
                    "description": "Hav kesme döner bıçağı aşırı ısındı veya köreldi.",
                    "probable_cause": "Elmas taşlama mekanizması boşluğu veya yetersiz teflon sprey.",
                    "remedy": "Bileme taşını 15° açıyla ayarlayınız, traverse PTFE uygulayınız.",
                    "iso_failure_mode": "MEC-CUT-DUL"
                },
                {
                    "code": "ERR-NET-03",
                    "hmi_message": "Profinet Remote IO Station Drop - ET200SP Timeout",
                    "description": "Dokuma tezgâhı uzak IO modülü haberleşme zaman aşımına uğradı.",
                    "probable_cause": "Cat6 STP kablo ekranlama zafiyeti veya motor EMI gürültüsü.",
                    "remedy": "Kablo ekranlama bileziğini kontrol ediniz, topraklamayı sıkınız.",
                    "iso_failure_mode": "ELC-NET-TMO"
                }
            ]
        }
        with open(hmi_dir / "VANDEWIELE_VDIRECT_HMI_FAULT_CODES.json", "w", encoding="utf-8") as f:
            json.dump(vdw_faults, f, ensure_ascii=False, indent=2)

        return {
            "raw_manuals_created": 5,
            "schematics_created": 2,
            "hmi_fault_catalogs_created": 1
        }

    def build_data_lake_summary(self) -> Dict[str, Any]:
        """Faz 1 veri gölü durum ve sayısallaştırma envanteri raporu üretir."""
        online_sources = self.get_curated_internet_sources()
        sap_file = self.fixtures_dir / "merinos_sap_pm_history.json"
        
        sap_count = 0
        if sap_file.exists():
            with open(sap_file, "r", encoding="utf-8") as f:
                sap_count = len(json.load(f))

        raw_files = list((self.data_lake_dir / "raw_manuals").glob("*.*"))
        sch_files = list((self.data_lake_dir / "schematics").glob("*.*"))
        hmi_files = list((self.data_lake_dir / "hmi_fault_codes").glob("*.*"))

        return {
            "phase": "Faz 1: Veri Gölü ve Sayısallaştırma",
            "status": "DATA_LAKE_ACTIVE",
            "online_sources_indexed": len(online_sources),
            "online_sources": [s.model_dump() for s in online_sources],
            "sap_pm_records_count": sap_count,
            "physical_documents_in_data_lake": {
                "raw_manuals_count": len(raw_files),
                "schematics_count": len(sch_files),
                "hmi_fault_codes_count": len(hmi_files),
                "raw_manuals_files": [f.name for f in raw_files],
                "schematics_files": [f.name for f in sch_files],
                "hmi_fault_codes_files": [f.name for f in hmi_files]
            },
            "data_lake_directories": {
                "raw_manuals": str(self.data_lake_dir / "raw_manuals"),
                "schematics": str(self.data_lake_dir / "schematics"),
                "sap_pm_history": str(self.data_lake_dir / "sap_pm_history"),
                "hmi_fault_codes": str(self.data_lake_dir / "hmi_fault_codes")
            }
        }


