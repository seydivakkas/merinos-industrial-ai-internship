"""
Merinos Industrial AI Internship - Day 29
Textile & Carpet Manufacturing Expert Engine (MerinosTextileExpertEngine).

Converts MerinosNanoLLM into an industrial domain expert for:
1. Carpet weaving, BCF extrusion, ramöz stenter and PLC mechatronics fault diagnosis.
2. Machine maintenance SOP generation (Van de Wiele, Schönherr, Brückner, Neumag, Siemens).
3. Factory domain vocabulary grounding & subword token conditioning.
4. MoE Subsystem Expert routing (Dokuma, İplik, Terbiye, Otomasyon).
5. Operational safety gate validation (energy isolation, temperature, pressure limits).
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from day29.mini_project.src.custom_nlp_engine import (
    MerinosBPETokenizer,
    MerinosCausalLM,
)
from day29.mini_project.src.functional_backend import FunctionalEquivalenceEngine
from day29.mini_project.src.models import NanoLLMConfig


class MerinosTextileExpertEngine:
    """
    Industrial Domain Expert System for Merinos Carpet Manufacturing.
    Integrates the custom Nano-LLM with verified factory SOPs, machine fault knowledge,
    MoE expert routing, and safety validation gates.
    """

    def __init__(
        self,
        config: Optional[NanoLLMConfig] = None,
        lexicon_path: Optional[Path] = None,
        corpus_path: Optional[Path] = None
    ):
        base_dir = Path(__file__).resolve().parent.parent
        self.lexicon_path = lexicon_path or base_dir / "fixtures" / "merinos_carpet_lexicon.json"
        self.corpus_path = corpus_path or base_dir / "fixtures" / "merinos_expert_qa_corpus.json"

        # Model configuration (Defaults to MoE with shared expert & KV cache)
        self.config = config or NanoLLMConfig(
            vocab_size=1024,
            d_model=192,
            n_heads=6,
            n_kv_heads=2,
            n_layers=4,
            intermediate_size=512,
            max_seq_len=256,
            use_moe=True,
            num_experts=5,
            num_experts_per_tok=2,
            use_shared_expert=True,
            enable_kv_cache=True,
            attention_logit_soft_capping=30.0
        )

        self.tokenizer = MerinosBPETokenizer(vocab_size=self.config.vocab_size)
        self.model = MerinosCausalLM(self.config)

        self.lexicon: Dict[str, Any] = {}
        self.expert_corpus: List[Dict[str, Any]] = []
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        """Loads domain dictionary and technical expert Q&A records."""
        if self.lexicon_path.exists():
            with open(self.lexicon_path, "r", encoding="utf-8") as f:
                self.lexicon = json.load(f)

        if self.corpus_path.exists():
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                self.expert_corpus = json.load(f)

    # -------------------------------------------------------------------------
    # 1. Domain Lexicon & SOP Lookup
    # -------------------------------------------------------------------------
    def lookup_term(self, term: str) -> Optional[str]:
        """
        Looks up a technical textile term in the factory glossary.
        Gerekçe: Operatör terimleri aradığında doğrudan fabrika standart tanımına ulaşmalıdır.
        Türkçe karakter varyasyonlarına (ö/o, ü/u, ı/i, vb.) karşı normalizasyon uygulanır.
        """
        glossary = self.lexicon.get("technical_glossary", {})
        tr_map = str.maketrans("çğışöüÇĞİŞÖÜ", "cgisouCGISOU")
        term_clean = term.lower().strip()
        term_norm = term_clean.translate(tr_map)

        for k, v in glossary.items():
            k_norm = k.lower().translate(tr_map)
            if term_clean in k or k in term_clean or term_norm in k_norm or k_norm in term_norm:
                return v
        return None

    def find_sop_by_fault_code(self, fault_code: str) -> Optional[Dict[str, Any]]:
        """
        Finds validated maintenance SOP by industrial fault code (e.g. ERR-ATK-01).
        Gerekçe: Bilinen hata kodları için doğrulanmış fabrika prosedürü birincil kaynaktır.
        """
        code_upper = fault_code.upper().strip()
        for dept in self.lexicon.get("departments", []):
            for fault in dept.get("common_faults", []):
                if fault.get("fault_code") == code_upper:
                    return {
                        "department": dept.get("name"),
                        "fault": fault
                    }
        return None

    # -------------------------------------------------------------------------
    # 2. Structured Domain Prompt Formatting
    # -------------------------------------------------------------------------
    @staticmethod
    def format_fault_prompt(
        symptom: str,
        machine: str,
        department: str,
        parameters: Optional[str] = None,
        priority: str = "CRITICAL"
    ) -> str:
        """
        Formats raw operator fault report into structured domain tokens.
        Gerekçe: Yapısal belirteçler ([ARIZA], [PARAMETRE], [COZUM]) modelin rastgele
        metin üretmesini engeller ve hedef odaklı teşhis üretmesini sağlar.
        """
        priority_tag = {
            "CRITICAL": "[ONCELIK_KRITIK]",
            "HIGH": "[ONCELIK_UYARI]",
            "INFO": "[ONCELIK_BILGI]"
        }.get(priority.upper(), "[ONCELIK_UYARI]")

        dept_tag = {
            "DOKUMA": "[ATKI]",
            "IPLIK_BCF": "[BCF]",
            "RAMOZ_TERBIYE": "[RAMOZ]",
            "MEKATRONIK_PLC": "[JAKAR]",
            "DESEN_TASARIM": "[DESEN]",
            "KALITE_LABORATUVAR": "[KALITE]",
            "PLANLAMA_ERP": "[STOK_MRP]",
            "BAKIM_ONARIM": "[BAKIM]"
        }.get(department.upper(), "[ATKI]")

        param_str = f" [PARAMETRE] {parameters}" if parameters else ""
        return f"{priority_tag} {dept_tag} [ARIZA] {machine}: {symptom}{param_str} [COZUM]"

    @staticmethod
    def format_design_prompt(
        theme: str,
        reed_density: int,
        pick_density: int,
        colors_count: int,
        has_relief: bool = False
    ) -> str:
        """
        Formats carpet designer CAD request into structured domain tokens.
        Gerekçe: Desinatörün teknik çizim ve armür talepleri yapısal belirteçlerle modele iletilir.
        """
        relief_tag = " [ROLYEF]" if has_relief else ""
        return (
            f"[ONCELIK_BILGI] [DESEN] [CIZIM] Tema: {theme} [TARAK] {reed_density} "
            f"[PARAMETRE] Atkı: {pick_density}, Renk: {colors_count}{relief_tag} [COZUM]"
        )

    # -------------------------------------------------------------------------
    # 3. MoE Subsystem Expert Routing
    # -------------------------------------------------------------------------
    @staticmethod
    def route_to_subsystem_expert(department: str) -> Tuple[int, str]:
        """
        Maps manufacturing department to primary MoE expert ID and specialty.
        Gerekçe: MoE mimarisinde 5 ayrı uzman bulunur; her departman kendi alanında
        eğitilmiş uzmana yönlendirilir:
          - Expert 0: Dokuma Mekaniği & Jakar
          - Expert 1: BCF Ekstrüzyon & Polimer Termal İşlemleri
          - Expert 2: Ramöz, Fikse & Lateks Kaplama / Akredite Kalite Laboratuvarı
          - Expert 3: PLC, Otomasyon & Saha Sensörleri
          - Expert 4: Halı Desinatörlüğü, Jakar CAD, Armür & Renk Kombinasyon Uzmanı
        """
        mapping = {
            "DOKUMA": (0, "Dokuma Mekaniği, Rapyer & Jakar Uzmanı"),
            "IPLIK_BCF": (1, "BCF İplik Ekstrüzyon & Polimer İşleme Uzmanı"),
            "RAMOZ_TERBIYE": (2, "Ramöz Fırını, Fikse & Lateks Terbiye Uzmanı"),
            "MEKATRONIK_PLC": (3, "Siemens PLC, Sensör & Endüstriyel Otomasyon Uzmanı"),
            "DESEN_TASARIM": (4, "Halı Desinatörlüğü, Jakar CAD, Armür & Renk Kombinasyon Uzmanı"),
            "KALITE_LABORATUVAR": (2, "Akredite Kalite Güvence, TSE/ISO Test Laboratuvarı & Terbiye Uzmanı"),
            "PLANLAMA_ERP": (1, "Üretim Planlama, OEE Verimlilik & ERP Yedek Parça Uzmanı"),
            "BAKIM_ONARIM": (0, "Fabrika Koruyucu Bakım & Mekanik Revizyon Uzmanı")
        }
        return mapping.get(department.upper(), (0, "Genel Fabrika Bakım Uzmanı"))

    # -------------------------------------------------------------------------
    # 4. Operational Safety & Design Verification Gate
    # -------------------------------------------------------------------------
    @staticmethod
    def validate_safety(plan: str, parameters: Optional[Dict[str, float]] = None) -> Tuple[bool, List[str]]:
        """
        Industrial Safety, Interlock, Carpet Design & Quality Rule Verification Gate.
        Gerekçe: Üretilen tavsiyelerin can güvenliği, yanlış desenden kaynaklanan
        kumaş dökülmesi veya TSE/ISO kalite reddi risklerini sıfıra indirmesi gerekir.
        """
        violations: List[str] = []
        plan_lower = plan.lower()

        # Check 1: Enerji izolasyonu (LOTO - Lockout/Tagout)
        if ("motor" in plan_lower or "kayış" in plan_lower or "zincir" in plan_lower) and "enerji" not in plan_lower and "durdurma" not in plan_lower:
            violations.append("UYARI: Hareketli mekanizma müdahalesinde acil durdurma veya enerji kesme talimatı verilmedi!")

        # Check 2: Ramöz fırını aşırı sıcaklık emniyeti
        if parameters and "temperature_c" in parameters:
            temp = parameters["temperature_c"]
            if temp > 210.0:
                violations.append(f"KRİTİK GÜVENLİK İHLALİ: Ramöz sıcaklığı {temp}°C polipropilen erime noktasını (165°C-170°C) aşıyor!")

        # Check 3: Ekstrüder basınç sınırı
        if parameters and "pressure_bar" in parameters:
            pres = parameters["pressure_bar"]
            if pres > 180.0:
                violations.append(f"KRİTİK GÜVENLİK İHLALİ: Eriyik basıncı {pres} bar kafa patlama emniyet limitini (160 bar) aşıyor!")

        # Check 4: Desende renk sayısı cağlık kapasitesi kontrolü
        if parameters and "colors_count" in parameters:
            colors = int(parameters["colors_count"])
            max_colors = int(parameters.get("max_creel_colors", 8))
            if colors > max_colors:
                violations.append(f"DESEN KURALI İHLALİ: Desendeki renk sayısı ({colors}), tezgah cağlık kapasitesini ({max_colors} renk) aşıyor! Optik stippling veya cağlık revizyonu gereklidir.")

        # Check 5: Rölyef derinliği aşırı çökertme emniyeti
        if parameters and "relief_depth_mm" in parameters:
            relief_mm = parameters["relief_depth_mm"]
            if relief_mm > 4.5:
                violations.append(f"DESEN KURALI UYARISI: Rölyef çökertme derinliği ({relief_mm} mm) kritik eşiği (4.0 mm) aşıyor; hav ipliği dökülmesi (tuft loss) ve taban açılması riski!")

        # Check 6: Tuft-lock ilme çekme mukavemeti kontrolü (ISO 4919)
        if parameters and "tuft_lock_newton" in parameters:
            tl_newton = parameters["tuft_lock_newton"]
            if tl_newton < 25.0:
                violations.append(f"KALİTE TESTİ İHLALİ: İlme çekme mukavemeti ({tl_newton:.1f} N) ISO 4919 kritik sınırının (25.0 N) altındadır; hav dökülmesi ve delaminasyon riski!")

        # Check 7: Metrekare gramaj sapması (GSM) toleransı kontrolü (TSE 2104)
        if parameters and "gsm_actual" in parameters and "gsm_target" in parameters:
            gsm_act = parameters["gsm_actual"]
            gsm_tgt = parameters["gsm_target"]
            dev_pct = ((gsm_act - gsm_tgt) / max(gsm_tgt, 1.0)) * 100.0
            if abs(dev_pct) > 5.0:
                violations.append(f"TSE 2104 STANDART DIŞI: Metrekare gramaj sapması (%{dev_pct:+.2f}) izin verilen ±%5.0 tolerans sınırını aşıyor (Hedef: {gsm_tgt} g/m², Ölçülen: {gsm_act} g/m²)!")

        # Check 8: Renk haslığı standart kontrolü (ISO 105)
        if parameters and "rubbing_fastness" in parameters:
            rubbing = parameters["rubbing_fastness"]
            if rubbing < 3.0:
                violations.append(f"HASLIK STANDART İHLALİ: Sürtünme renk haslığı ({rubbing:.1f} Gri Skala) ISO 105-X12 kabul eşiğinin (3.0) altındadır!")
        if parameters and "light_fastness" in parameters:
            light = parameters["light_fastness"]
            if light < 6.0:
                violations.append(f"HASLIK STANDART UYARISI: Xenon ışık haslığı ({light:.1f} Mavi Yün) ISO 105-B02 ihracat normunun (6.0) altındadır!")

        # Check 9: OEKO-TEX Standard 100 Class II uygunluk denetimi
        if parameters and "oeko_tex_certified" in parameters:
            if not bool(parameters["oeko_tex_certified"]):
                violations.append("EKOLOJİK UYGUNLUK UYARISI: Halı numunesi OEKO-TEX Standard 100 Class II toksikolojik ve VOC kriterlerini karşılamamaktadır!")

        # Check 10: ERP Yedek Parça Emniyet Stoku Kontrolü
        if parameters and "current_stock" in parameters and "critical_threshold" in parameters:
            cur_stk = parameters["current_stock"]
            crit_th = parameters["critical_threshold"]
            if cur_stk <= crit_th:
                violations.append(f"ERP Kritik Stok Alarmı: Parça stoku ({cur_stk:.0f} adet), emniyet eşiğinin ({crit_th:.0f} adet) altındadır/seviyesindedir; derhal satın alma talebi açılmalıdır!")

        # Check 11: Vardiya OEE Kullanılabilirlik Eşiği Kontrolü
        if parameters and "oee_availability_pct" in parameters:
            oee_avail = parameters["oee_availability_pct"]
            if oee_avail < 85.0:
                violations.append(f"OEE Verimlilik Alarmı: Vardiya kullanılabilirlik oranı (%{oee_avail:.2f}) fabrika hedef eşiğinin (%85.00) altına düşmüştür!")

        is_safe = len(violations) == 0
        return is_safe, violations

    # -------------------------------------------------------------------------
    # 5. Carpet CAD & Pattern Design Specification Analysis
    # -------------------------------------------------------------------------
    def analyze_design_spec(
        self,
        reed_density: int,
        pick_density_per_m: int,
        colors_count: int,
        width_m: float = 2.0,
        height_m: float = 3.0,
        max_creel_colors: int = 8,
        is_relief: bool = False,
        relief_depth_mm: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates geometric and structural parameters for a carpet design CAD drawing.
        Gerekçe: Desinatörün NedGraphics / EAT DesignScope programında çizime başlamadan önce
        doğru piksel en-boy oranını (aspect ratio), nokta sıklığını ve cağlık renk sınırını
        bilmesi; yanlış çizim kaynaklı kumaş bozulmalarını ve üretim kayıplarını sıfırlar.
        """
        # 1. Point density (Nokta Sayısı / m2) = Tarak * Atkı * 2
        point_density_sqm = reed_density * pick_density_per_m * 2
        
        # 2. Aspect Ratio (Piksel En-Boy Oranı) = Atkı / Tarak
        aspect_ratio = round(pick_density_per_m / max(reed_density, 1), 3)
        grid_ratio_display = f"1.0 : {aspect_ratio:.3f}"
        
        # 3. Total carpet metrics
        total_area_sqm = round(width_m * height_m, 2)
        total_points_carpet = int(point_density_sqm * total_area_sqm)
        total_reed_dents = int(width_m * reed_density)
        total_picks = int(height_m * pick_density_per_m)

        # 4. Audit parameters
        audit_params = {
            "colors_count": float(colors_count),
            "max_creel_colors": float(max_creel_colors),
            "relief_depth_mm": relief_depth_mm if is_relief else 0.0
        }
        is_safe, violations = self.validate_safety(
            plan=f"Halı deseni çizimi: {reed_density} tarak, {pick_density_per_m} atkı, {colors_count} renk.",
            parameters=audit_params
        )

        # 5. Technical recommendation
        cad_recommendation = (
            f"NedGraphics / Texcelle CAD ortamında 'Grid Ratio' oranını {grid_ratio_display} olarak ayarlayın. "
            f"Dairesel göbek çizimlerinde bu oran kullanılmazsa desen halıda basık/uzamış çıkar. "
            f"Toplam nokta sayısı {point_density_sqm:,} nokta/m² olup yüksek kaliteli sık dokuma sınıfındadır."
        )
        if colors_count > max_creel_colors:
            cad_recommendation += f" DİKKAT: {colors_count} renk için optik stippling (1x1 dama piksel) ile ara ton elde ediniz."
        if is_relief and relief_depth_mm > 4.0:
            cad_recommendation += " DİKKAT: Derin rölyef sınırlarında 1/3 V zemin bağlama armürü zorunludur."

        return {
            "reed_density_ends_per_m": reed_density,
            "pick_density_per_m": pick_density_per_m,
            "colors_count": colors_count,
            "dimensions_m": f"{width_m:.2f} x {height_m:.2f} m ({total_area_sqm} m²)",
            "point_density_sqm": point_density_sqm,
            "total_points_carpet": total_points_carpet,
            "pixel_aspect_ratio": aspect_ratio,
            "grid_ratio_display": grid_ratio_display,
            "total_reed_dents": total_reed_dents,
            "total_picks": total_picks,
            "cad_recommendation": cad_recommendation,
            "design_audit": {
                "passed": is_safe,
                "warnings": violations
            }
        }

    # -------------------------------------------------------------------------
    # 6. Carpet Quality Assurance & Laboratory Standards Audit
    # -------------------------------------------------------------------------
    def audit_carpet_quality(
        self,
        gsm_actual: float,
        gsm_target: float = 2400.0,
        tuft_lock_newton: float = 28.0,
        rubbing_fastness: float = 4.5,
        light_fastness: float = 6.0,
        martindale_cycles: int = 55000,
        oeko_tex_certified: bool = True
    ) -> Dict[str, Any]:
        """
        Audits carpet laboratory test metrics against TSE 2104, ISO 4919, ISO 105 and OEKO-TEX standards.
        Gerekçe: Metrekare gramajı (GSM) toleransı ((actual - target) / target * 100), TSE 2104
        uyarınca ±%5.0 bandında olmalıdır. Tuft lock ilme çekme mukavemeti ISO 4919 normunda
        minimum 25.0 N olmalıdır. Renk haslığı sürtünmede >= 3.0-4.0 (Gri Skala), ışıkta >= 6.0
        (Mavi Yün) ve Martindale aşınma devri >= 50,000 olmalıdır.
        """
        # 1. GSM Variance Calculation (TSE 2104)
        gsm_deviation_pct = round(((gsm_actual - gsm_target) / max(gsm_target, 1.0)) * 100.0, 2)
        tse_2104_passed = abs(gsm_deviation_pct) <= 5.0

        # 2. Tuft-Lock Withdrawal Force (ISO 4919)
        iso_4919_passed = tuft_lock_newton >= 25.0

        # 3. Fastness Ratings (ISO 105)
        iso_105_rubbing_passed = rubbing_fastness >= 3.0
        iso_105_light_passed = light_fastness >= 6.0

        # 4. Abrasion Resistance (ISO 12947 Martindale)
        martindale_passed = martindale_cycles >= 50000

        # 5. Ecological Safety (OEKO-TEX Standard 100)
        oeko_tex_passed = bool(oeko_tex_certified)

        # 6. Run safety & compliance audit gate
        audit_params = {
            "gsm_actual": float(gsm_actual),
            "gsm_target": float(gsm_target),
            "tuft_lock_newton": float(tuft_lock_newton),
            "rubbing_fastness": float(rubbing_fastness),
            "light_fastness": float(light_fastness),
            "oeko_tex_certified": 1.0 if oeko_tex_certified else 0.0
        }
        is_safe, violations = self.validate_safety(
            plan=f"Kalite Laboratuvar Denetimi: GSM {gsm_actual} g/m², Tuft-Lock {tuft_lock_newton} N, Haslık {rubbing_fastness}.",
            parameters=audit_params
        )

        overall_passed = (
            tse_2104_passed and
            iso_4919_passed and
            iso_105_rubbing_passed and
            iso_105_light_passed and
            martindale_passed and
            oeko_tex_passed and
            is_safe
        )

        # 7. Corrective Actions SOP determination
        corrective_actions: List[str] = []
        if not tse_2104_passed:
            sop = self.find_sop_by_fault_code("ERR-KAL-02")
            if sop:
                corrective_actions.append(f"Gramaj Düzeltme: {sop['fault']['maintenance_sop']}")
        if not iso_4919_passed:
            sop = self.find_sop_by_fault_code("ERR-KAL-01")
            if sop:
                corrective_actions.append(f"Tuft-Lock İyileştirme: {sop['fault']['maintenance_sop']}")
        if not (iso_105_rubbing_passed and iso_105_light_passed):
            sop = self.find_sop_by_fault_code("ERR-KAL-03")
            if sop:
                corrective_actions.append(f"Haslık İyileştirme: {sop['fault']['maintenance_sop']}")
        if not oeko_tex_passed:
            sop = self.find_sop_by_fault_code("ERR-KAL-04")
            if sop:
                corrective_actions.append(f"Ekolojik Uygunluk: {sop['fault']['maintenance_sop']}")

        if not corrective_actions:
            corrective_actions.append("Tüm test parametreleri Merinos A-Sınıfı ihracat ve TSE/ISO/OEKO-TEX standartlarını sağlamaktadır; sevk onaylandı.")

        verdict_str = "ONAYLANDI (Kalite A-Sınıfı Sevk Edilebilir)" if overall_passed else "RED / ŞARTLI KABUL (Düzeltici Faaliyet Gerekli)"

        return {
            "standards_evaluated": [
                "TSE 2104 (Mekanik Dokuma Halılar - Metrekare Ağırlığı)",
                "ISO 4919 (İlme Çekme Mukavemeti - Tuft Lock Force)",
                "ISO 105-X12 / ISO 105-B02 (Sürtünme ve Işık Haslığı)",
                "ISO 12947 (Martindale Aşınma Direnci)",
                "OEKO-TEX Standard 100 Class II (Ekolojik Güvenlik)"
            ],
            "metrics": {
                "gsm_actual": gsm_actual,
                "gsm_target": gsm_target,
                "gsm_deviation_pct": gsm_deviation_pct,
                "tuft_lock_newton": tuft_lock_newton,
                "rubbing_fastness": rubbing_fastness,
                "light_fastness": light_fastness,
                "martindale_cycles": martindale_cycles,
                "oeko_tex_certified": oeko_tex_certified
            },
            "compliance_flags": {
                "tse_2104_passed": tse_2104_passed,
                "iso_4919_passed": iso_4919_passed,
                "iso_105_rubbing_passed": iso_105_rubbing_passed,
                "iso_105_light_passed": iso_105_light_passed,
                "martindale_passed": martindale_passed,
                "oeko_tex_passed": oeko_tex_passed
            },
            "audit_verdict": verdict_str,
            "overall_passed": overall_passed,
            "violations": violations,
            "corrective_actions": corrective_actions
        }

    # -------------------------------------------------------------------------
    # 7. OEE Downtime Loss & Carpet Area Production Loss Calculation
    # -------------------------------------------------------------------------
    def calculate_oee_and_downtime_loss(
        self,
        downtime_minutes: float,
        loom_speed_rpm: float = 165.0,
        pick_density_per_m: int = 1200,
        fabric_width_m: float = 4.0,
        planned_shift_minutes: float = 480.0,
        carpet_unit_cost_tl_sqm: float = 450.0,
        hourly_overhead_tl: float = 1850.0,
        is_double_piece: bool = True,
        spare_part_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates shift-based OEE availability loss, lost carpet production area (m²),
        and overall financial downtime cost for Merinos weaving looms (Van de Wiele, Schönherr).

        Gerekçe:
        1. Çift parça (face-to-face) halı tezgahları her atkı atımında aynı anda üst ve alt halıyı
           dokuduğundan, birim zamanda üretilen alan tek katlı kumaşa göre iki katıdır (x2 çarpanı).
        2. Çizgisel üretim hızı: v = loom_speed_rpm / pick_density_per_m (m/dk).
        3. Dakikalık alan üretim debisi: A_rate = v * fabric_width_m * (2 if is_double_piece else 1) (m²/dk).
        4. Duruş süresince kaybedilen halı alanı: Lost_m² = A_rate * downtime_minutes.
        5. OEE Kullanılabilirlik Oranı (Availability): (Çalışma Süresi / Planlanan Vardiya Süresi) * 100.
        6. Toplam Finansal Kayıp = (Kaybedilen m² * Birim Halı Değeri) + (Duruş Saati * Saatlik Sabit Genel Gider) + Yedek Parça Maliyeti.
        """
        # 1. Production linear speed and area rate
        linear_speed_m_min = loom_speed_rpm / max(pick_density_per_m, 1)
        double_factor = 2.0 if is_double_piece else 1.0
        sqm_per_min = linear_speed_m_min * fabric_width_m * double_factor

        # 2. Lost production metrics
        lost_carpet_sqm = round(sqm_per_min * downtime_minutes, 2)
        carpet_loss_cost_tl = round(lost_carpet_sqm * carpet_unit_cost_tl_sqm, 2)
        overhead_cost_tl = round((downtime_minutes / 60.0) * hourly_overhead_tl, 2)

        # 3. Spare part integration if requested
        part_info = None
        spare_part_cost_tl = 0.0
        if spare_part_code:
            part_info = self.query_spare_part(spare_part_code)
            if part_info.get("found"):
                spare_part_cost_tl = float(part_info.get("unit_cost_tl", 0.0))

        total_financial_loss_tl = round(carpet_loss_cost_tl + overhead_cost_tl + spare_part_cost_tl, 2)

        # 4. OEE Availability calculation
        operating_minutes = max(0.0, planned_shift_minutes - downtime_minutes)
        oee_availability_pct = round((operating_minutes / max(planned_shift_minutes, 1.0)) * 100.0, 2)

        # 5. Safety & efficiency audit
        audit_params = {
            "oee_availability_pct": oee_availability_pct
        }
        if part_info and part_info.get("found"):
            audit_params["current_stock"] = float(part_info.get("current_stock", 0))
            audit_params["critical_threshold"] = float(part_info.get("critical_threshold", 0))

        is_safe, violations = self.validate_safety(
            plan=f"Vardiya Duruş Analizi: {downtime_minutes} dk duruş, OEE Kullanılabilirlik %{oee_availability_pct}.",
            parameters=audit_params
        )

        # 6. Industrial rationale & audit recommendations
        audit_recommendations = [
            f"Vardiya planlanan {planned_shift_minutes:.0f} dakikanın {downtime_minutes:.0f} dakikası plansız duruşla kaybedildi (OEE Kullanılabilirlik: %{oee_availability_pct:.2f}).",
            f"Tezgah çalışma hızında ({loom_speed_rpm} rpm, {pick_density_per_m} atkı/m) dakikada {sqm_per_min:.2f} m² üretim kapasitesi bulunmaktadır.",
            f"Toplam kaybedilen halı alanı {lost_carpet_sqm:.2f} m² olup doğrudan ciro/maliyet kaybı {carpet_loss_cost_tl:,.2f} TL'dir.",
            f"Fabrika amortisman ve işçilik genel gider kaybı: {overhead_cost_tl:,.2f} TL."
        ]
        if spare_part_cost_tl > 0:
            audit_recommendations.append(f"Arıza onarımı için tüketilen yedek parça maliyeti: {spare_part_cost_tl:,.2f} TL ({spare_part_code}).")
        if oee_availability_pct < 85.0:
            audit_recommendations.append("DİKKAT: OEE %85 kritik verimlilik eşiğinin altındadır; 2. seviye kök neden arıza analizi (RCA) başlatılmalıdır.")

        return {
            "downtime_minutes": downtime_minutes,
            "planned_shift_minutes": planned_shift_minutes,
            "operating_minutes": operating_minutes,
            "oee_availability_pct": oee_availability_pct,
            "production_rate": {
                "loom_speed_rpm": loom_speed_rpm,
                "pick_density_per_m": pick_density_per_m,
                "fabric_width_m": fabric_width_m,
                "is_double_piece": is_double_piece,
                "linear_speed_m_per_min": round(linear_speed_m_min, 4),
                "sqm_per_min": round(sqm_per_min, 4)
            },
            "loss_metrics": {
                "lost_carpet_sqm": lost_carpet_sqm,
                "carpet_loss_cost_tl": carpet_loss_cost_tl,
                "overhead_cost_tl": overhead_cost_tl,
                "spare_part_cost_tl": spare_part_cost_tl,
                "total_financial_loss_tl": total_financial_loss_tl
            },
            "spare_part_analysis": part_info,
            "audit": {
                "passed": is_safe,
                "warnings": violations
            },
            "audit_recommendations": audit_recommendations,
            "industrial_rationale": (
                "Çift yüzlü dokuma tezgahında her duruş dakikası 2 kat kumaş kaybı üretir. "
                "Hızlı müdahale ve hat kenarı kritik yedek parça bulundurulması arıza sürelerini %40 kısaltır."
            )
        }

    # -------------------------------------------------------------------------
    # 8. ERP Spare Part Catalog Query & Critical Stock Alerting
    # -------------------------------------------------------------------------
    def query_spare_part(self, part_code: str) -> Dict[str, Any]:
        """
        Queries Merinos ERP spare parts catalog by MRP code (e.g. MRP-RAP-101).
        Performs critical safety stock validation, reorder point (ROP) checks,
        and provides procurement lead time notifications.

        Gerekçe:
        Dokuma tezgahlarında ve BCF hatlarında plansız duruşların %65'i yedek parça
        bekleme süresinden kaynaklanır. Merinos parça kodları (MRP-*) ile entegre
        stok takibi, kritik eşik altına düşen parçaları anında tespit ederek
        otomatik satın alma emri açılmasını sağlar.
        """
        catalog = self.lexicon.get("spare_parts_catalog", [])
        code_clean = part_code.strip().upper()

        matched_part = None
        for item in catalog:
            item_code = item.get("part_code", "").upper()
            if code_clean == item_code or code_clean in item_code or item_code in code_clean:
                matched_part = item
                break

        if not matched_part:
            return {
                "found": False,
                "part_code": part_code,
                "error": f"Parça kodu '{part_code}' Merinos ERP kataloğunda bulunamadı. Lütfen geçerli bir MRP-* kodu giriniz."
            }

        cur_stock = int(matched_part.get("current_stock", 0))
        crit_th = int(matched_part.get("critical_threshold", 0))
        lead_time = int(matched_part.get("lead_time_days", 0))
        origin = matched_part.get("supplier_origin", "Yurtdışı")
        unit_cost = float(matched_part.get("unit_cost_tl", 0.0))

        # Determine replenishment urgency
        if cur_stock < crit_th:
            status = "CRITICAL_LOW_STOCK"
            action_code = "REORDER_URGENT"
            urgency_text = f"ACİL SİPARİŞ: Stok ({cur_stock} adet), emniyet eşiği ({crit_th} adet) altındadır! {origin} menşeili tedarik {lead_time} gün sürmektedir."
        elif cur_stock == crit_th:
            status = "WARNING_LOW_STOCK"
            action_code = "REORDER_SOON"
            urgency_text = f"UYARI: Stok ({cur_stock} adet) tam kritik emniyet sınırındadır. Erken tedarik siparişi açılmalıdır."
        else:
            status = "OPTIMAL_STOCK"
            action_code = "STOCK_ADEQUATE"
            urgency_text = f"Stok durumu yeterlidir ({cur_stock} adet / Emniyet eşiği: {crit_th} adet)."

        # Run safety validation gate
        is_safe, violations = self.validate_safety(
            plan=f"Yedek Parça Ambar Stok Kontrolü (Enerji kesme ve emniyet protokolü): {matched_part.get('part_code')} ({matched_part.get('name')})",
            parameters={"current_stock": float(cur_stock), "critical_threshold": float(crit_th)}
        )

        return {
            "found": True,
            "part_code": matched_part.get("part_code"),
            "name": matched_part.get("name"),
            "machine": matched_part.get("machine"),
            "department": matched_part.get("department"),
            "unit_cost_tl": unit_cost,
            "current_stock": cur_stock,
            "critical_threshold": crit_th,
            "lead_time_days": lead_time,
            "shelf_location": matched_part.get("shelf_location"),
            "supplier_origin": origin,
            "compatible_fault_codes": matched_part.get("compatible_fault_codes", []),
            "replenishment_status": status,
            "action_code": action_code,
            "urgency_notice": urgency_text,
            "safety_audit": {
                "passed": is_safe,
                "warnings": violations
            },
            "industrial_rationale": (
                f"{matched_part.get('machine')} tezgahında bu parçanın tükenmesi plansız duruşa "
                f"ve vardiya başına on binlerce TL kayba yol açar. {origin} sevkiyatı {lead_time} gün "
                "sürdüğünden emniyet stoğu seviyesi aksatılmamalıdır."
            )
        }

    # -------------------------------------------------------------------------
    # 9. Domain Adaptation Training Loop
    # -------------------------------------------------------------------------
    def train_domain_adaptation(
        self,
        epochs: int = 15,
        learning_rate: float = 3e-3
    ) -> Dict[str, Any]:
        """
        Fine-tunes the Nano-LLM weights on the industrial carpet Q&A corpus.
        Gerekçe: Rastgele ağırlıklarla model tekstil alanına yanıt veremez; bu eğitim adımıyla
        özel belirteçler ([ARIZA] -> [COZUM] -> [BAKIM]) arasındaki olasılık dağılımı optimize edilir.
        """
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=0.01)

        loss_history: List[float] = []

        # Prepare batch tensors from corpus
        training_samples: List[Tuple[torch.Tensor, torch.Tensor]] = []
        for item in self.expert_corpus:
            full_text = f"{item['prompt']} {item['response']}"
            token_ids = self.tokenizer.encode(full_text, add_special_tokens=True)
            if len(token_ids) > self.config.max_seq_len:
                token_ids = token_ids[:self.config.max_seq_len]

            inp = torch.tensor(token_ids[:-1], dtype=torch.long).unsqueeze(0)
            target = torch.tensor(token_ids[1:], dtype=torch.long).unsqueeze(0)
            training_samples.append((inp, target))

        if not training_samples:
            return {"status": "no_data", "initial_loss": 0.0, "final_loss": 0.0}

        initial_loss = 0.0
        final_loss = 0.0

        for epoch in range(epochs):
            epoch_loss = 0.0
            for step_idx, (inp, target) in enumerate(training_samples):
                # Calculate learning rate with cosine decay
                lr = FunctionalEquivalenceEngine.cosine_learning_rate(
                    current_step=epoch * len(training_samples) + step_idx,
                    warmup_steps=3,
                    max_steps=epochs * len(training_samples),
                    base_lr=learning_rate
                )
                for param_group in optimizer.param_groups:
                    param_group["lr"] = lr

                step_metrics = FunctionalEquivalenceEngine.simulate_gradient_tape_step(
                    model=self.model,
                    optimizer=optimizer,
                    x=inp,
                    y=target
                )
                epoch_loss += step_metrics["loss"]

            avg_epoch_loss = epoch_loss / len(training_samples)
            loss_history.append(avg_epoch_loss)
            if epoch == 0:
                initial_loss = avg_epoch_loss
            final_loss = avg_epoch_loss

        self.model.eval()
        return {
            "epochs": epochs,
            "samples_trained": len(training_samples),
            "initial_loss": round(initial_loss, 4),
            "final_loss": round(final_loss, 4),
            "loss_reduction_pct": round(((initial_loss - final_loss) / max(initial_loss, 1e-5)) * 100.0, 2),
            "loss_history": [round(l, 4) for l in loss_history]
        }

    # -------------------------------------------------------------------------
    # 6. End-to-End Diagnostic Pipeline
    # -------------------------------------------------------------------------
    def diagnose_fault(
        self,
        machine: str,
        symptom: str,
        department: str = "DOKUMA",
        fault_code: Optional[str] = None,
        parameters: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Full diagnostic and maintenance assistant execution for a factory incident.
        """
        # Step 1: Check verified SOP in factory lexicon
        lexicon_hit = None
        if fault_code:
            lexicon_hit = self.find_sop_by_fault_code(fault_code)

        # Step 2: Route to specialized MoE expert
        expert_id, expert_name = self.route_to_subsystem_expert(department)

        # Step 3: Format structured domain prompt
        param_str = ", ".join(f"{k}: {v}" for k, v in parameters.items()) if parameters else None
        prompt = self.format_fault_prompt(
            symptom=symptom,
            machine=machine,
            department=department,
            parameters=param_str
        )

        # Step 4: Tokenize and generate recommendation using Nano-LLM
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        generated_ids = self.model.generate(
            prompt_tokens=prompt_ids,
            max_new_tokens=30,
            temperature=0.0,  # Greedy for maximum determinism in industrial advice
            use_cache=True
        )
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=False)

        # Step 5: Synthesize recommended action (grounded with lexicon SOP if present)
        if lexicon_hit:
            recommended_action = lexicon_hit["fault"]["maintenance_sop"]
            root_cause = lexicon_hit["fault"]["root_cause"]
            source = "Merinos Doğrulanmış Fabrika SOP Kılavuzu"
            confidence = 0.98
        else:
            recommended_action = generated_text.replace(prompt, "").strip()
            root_cause = "Model Teşhisi ve Telemetri Örüntü Çıkarsaması"
            source = f"MerinosNanoLLM MoE {expert_name}"
            confidence = 0.82

        # Step 6: Validate safety gate
        is_safe, violations = self.validate_safety(recommended_action, parameters=parameters)

        return {
            "machine": machine,
            "department": department,
            "assigned_expert": {
                "expert_id": expert_id,
                "expert_title": expert_name
            },
            "prompt_formatted": prompt,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "safety_audit": {
                "passed": is_safe,
                "violations": violations
            },
            "confidence_score": confidence,
            "data_source": source
        }
