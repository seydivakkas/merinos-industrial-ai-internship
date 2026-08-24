# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
Integrated Carpet Pipeline: Day 28 (SDXL Üretim) ve Day 29 (Görsel Analitik) Tümleşik Boru Hattı
Staj Defteri Yaprak 59 ve 60 Müfredatına %100 Sadık Tek Zincir Orkestratörü.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np
import cv2

# Day 28 ve Day 29 bileşenlerinin entegrasyonu (Şekil 59)
from .models import (
    CarpetDesign,
    CarpetDesignInput,
    GenerationConfig,
    PromptAssemblyResult,
    TechnicalLimitationsReport,
    IntegratedPipelineOutput,
    SymmetryMode,
)
from .visualizer import CarpetVisualizer, CarpetPipelineVisualizer

# Day 28: Metin tabanlı tasarım üretimi (SDXL)
from day28.mini_project.src.prompt_structurer import PromptStructurer
from day28.mini_project.src.sdxl_controller import SDXLController, SDXLController as SDXLGenerator
from day28.mini_project.src.models import StructuredDesignBrief

# Day 29: Görsel analiz modülleri
from day29.mini_project.src.color_analyzer import ColorPaletteAnalyzer as ColorAnalyzer
from day29.mini_project.src.symmetry_analyzer import StructuralSymmetryAnalyzer as SymmetryAnalyzer
from day29.mini_project.src.embedding_retriever import (
    CNNEmbeddingRetriever,
    CNNEmbeddingRetriever as SimilaritySearcher,
)
from day29.mini_project.src.master_analyzer import MasterCarpetAnalyzer
from day29.mini_project.src.seam_analyzer import SeamContinuityAnalyzer


DEFAULT_LIMITATIONS = TechnicalLimitationsReport(
    manufacturability={
        "status": "SINIR_BELİRLENDİ",
        "title": "Fiziksel Dokunabilirlik Garantisi Yoktur",
        "detail": (
            "Difüzyon modelleri piksel düzeyinde görsel üretir; ancak halı dokuma tezgahındaki "
            "tarak sıklığı (cm başına tel sayısı), atkı sıkışma gerginliği ve iplik büküm fiziksel "
            "kısıtlarını doğrudan bilemez. Üretilen desen tezgaha gitmeden önce desinatör kontrolünden geçmelidir."
        )
    },
    aesthetic_subjectivity={
        "status": "SINIR_BELİRLENDİ",
        "title": "Estetik Kalite Matematiksel Olarak Kesin Ölçülemez",
        "detail": (
            "Matematiksel simetri korelasyonu ve renk uyumu objektif sayılar sunsa da, "
            "tüketici beğenisi, bölgesel pazar trendleri ve kültürel motif algısı sübjektiftir."
        )
    },
    copyright_originality={
        "status": "SINIR_BELİRLENDİ",
        "title": "Telif ve Özgünlük Değerlendirmesi Yapılmaz",
        "detail": (
            "Model açık kaynak ağırlıklarla üretildiğinden geleneksel tescilli desenler "
            "veya üçüncü şahıs telif hakları taranmaz; özgünlük kararı hukuki inceleme gerektirir."
        )
    },
    metric_independence={
        "status": "SINIR_BELİRLENDİ",
        "title": "Analiz Metrikleri Tek Başına Başarılı Tasarım Anlamına Gelmez",
        "detail": (
            "Yüksek simetri skoru veya düşük CIEDE2000 renk farkı, desenin ticari olarak "
            "başarılı veya görsel olarak kusursuz olduğunu tek başına garanti etmez."
        )
    },
    summary_verdict="Birinci çalışma (Day 28-30), görsel üretimi ve objektif teşhisi tek akışta birleştirir; ancak endüstriyel üretimde insan uzmanlığını tamamlayıcı bir yönlendirici olarak konumlandırılmalıdır."
)


class IntegratedCarpetPipeline:
    """
    Day 28 ve Day 29 modüllerini birleştirerek
    tümleşik halı tasarım ve görsel analiz hattını sunar (Şekil 59 & 60).
    """

    def __init__(
        self,
        config_path: str = "configs/pipeline_config.json",
        output_dir: Optional[str] = None,
        reference_catalog_path: Optional[str] = None
    ):
        base_dir = Path(__file__).resolve().parent.parent
        self.config: Dict[str, Any] = {}
        if config_path:
            p = Path(config_path)
            if not p.is_absolute() and not p.exists():
                p = base_dir / config_path
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        self.config = json.load(f)
                except Exception:
                    pass

        self.output_dir = Path(output_dir) if output_dir else base_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        catalog_path = Path(reference_catalog_path) if reference_catalog_path else base_dir.parent.parent / "day29" / "mini_project" / "fixtures" / "reference_carpet_catalog.json"

        # Alt bileşenleri başlat (Şekil 59)
        self.prompt_structurer = PromptStructurer()
        self.generator = self.sdxl_controller = SDXLGenerator(structurer=self.prompt_structurer)        # Day 28
        self.color_analyzer = ColorAnalyzer()              # Day 29
        self.symmetry_analyzer = SymmetryAnalyzer()        # Day 29
        self.similarity_searcher = SimilaritySearcher(
            catalog_path=catalog_path if catalog_path.exists() else None
        )    # Day 29
        self.visualizer = CarpetVisualizer()
        self.master_analyzer = MasterCarpetAnalyzer(
            reference_catalog_path=catalog_path if catalog_path.exists() else None
        )

    def assemble_prompt(
        self,
        design_brief: Union[Dict[str, Any], CarpetDesignInput]
    ) -> Union[str, PromptAssemblyResult]:
        """
        Tasarım brief'inden görsel üretim için detaylı prompt oluşturur (Şekil 59 & Yaprak 59).
        """
        if isinstance(design_brief, dict):
            stil = design_brief.get("stil", design_brief.get("style", ""))
            komp = design_brief.get("kompozisyon", design_brief.get("composition", ""))
            motif = design_brief.get("ana_motif", design_brief.get("motif", ""))
            renk = design_brief.get("ana_renk", design_brief.get("primary_color", ""))
            ikincil = design_brief.get("ikincil_renk", design_brief.get("secondary_color", ""))
            bordur = design_brief.get("bordur_tipi", design_brief.get("border_type", ""))
            renk_sayisi = design_brief.get("caglik_renk_sayisi", design_brief.get("target_creel_colors", 8))

            parts = []
            if stil:
                parts.append(f"{stil} stilinde")
            if komp:
                parts.append(f"{komp} kompozisyonuna sahip")
            if motif:
                parts.append(f"{motif} motifli")
            if renk and ikincil:
                parts.append(f"{renk.lower()} zemin üzerine {ikincil.lower()} detaylı")
            elif renk:
                parts.append(f"{renk.lower()} zemin detaylı")
            if bordur:
                parts.append(f"{bordur.lower()} bordürlü")
            parts.append(f"simetrik halı deseni, high detail, photorealistic, oriental carpet, {renk_sayisi} colors.")
            return ", ".join(parts)

        # CarpetDesignInput
        brief = design_brief
        color_str = brief.primary_color
        if brief.secondary_color:
            color_str = f"{brief.primary_color} ve {brief.secondary_color}"

        day28_brief = StructuredDesignBrief(
            brief_id=brief.brief_id,
            style=brief.style,
            motif=brief.motif,
            color=color_str,
            composition=brief.composition or "",
            border=brief.border_type or "",
            symmetry=brief.symmetry_mode.value,
            seed=brief.seed
        )

        d28_res = self.prompt_structurer.assemble(day28_brief)

        # Şekil 60 doğal cümle formatı
        stil = brief.style
        komp = brief.composition
        motif = brief.motif
        renk = brief.primary_color
        ikincil = brief.secondary_color
        bordur = brief.border_type
        parts = []
        if stil:
            parts.append(f"{stil} stilinde")
        if komp:
            parts.append(f"{komp} kompozisyonuna sahip")
        if motif:
            parts.append(f"{motif} motifli")
        if renk and ikincil:
            parts.append(f"{renk.lower()} zemin üzerine {ikincil.lower()} detaylı")
        elif renk:
            parts.append(f"{renk.lower()} zemin detaylı")
        if bordur:
            parts.append(f"{bordur.lower()} bordürlü")
        parts.append("simetrik halı deseni, high detail, photorealistic, oriental carpet, 8 colors.")
        natural_prompt = ", ".join(parts)

        included = {
            "style": brief.style,
            "motif": brief.motif,
            "color": color_str,
        }
        omitted = []

        if brief.composition:
            included["composition"] = brief.composition
        else:
            omitted.append("composition")

        if brief.border_type:
            included["border"] = brief.border_type
        else:
            omitted.append("border")

        if brief.symmetry_mode != SymmetryMode.ASYMMETRIC:
            included["symmetry"] = brief.symmetry_mode.value
        else:
            omitted.append("symmetry (asimetrik)")

        return PromptAssemblyResult(
            assembled_prompt=d28_res.assembled_prompt,
            negative_prompt=d28_res.negative_prompt,
            included_fields=included,
            omitted_fields=omitted
        )

    def run(
        self,
        brief: CarpetDesignInput,
        empty_catalog_test: bool = False
    ) -> IntegratedPipelineOutput:
        """
        Uçtan uca tümleşik boru hattını çalıştırır:
        1. İstem Montajı (Day 28)
        2. Görüntü Üretimi (Day 28 SDXL Controller)
        3. Çok Boyutlu Görsel Analiz (Day 29 Master Carpet Analyzer)
        4. Benzer Görsel Arama (Day 29 CNN Embedding Retriever)
        5. 4 Teknik Sınırın Değerlendirilmesi (Yaprak 60)
        """
        t_global_start = time.perf_counter()
        latencies: Dict[str, float] = {}

        # -------------------------------------------------------------
        # ADIM 1: İstem Montajı (Yaprak 59)
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        prompt_res = self.assemble_prompt(brief)
        latencies["prompt_assembly_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # -------------------------------------------------------------
        # ADIM 2: Görüntü Üretimi (Day 28 SDXL)
        # -------------------------------------------------------------
        t1 = time.perf_counter()
        # Simetri metnini Day 28 Türkçe desen kurallarına uygun eşle
        sym_mapping = {
            SymmetryMode.BILATERAL_AND_VERTICAL: "Çift yönlü 4-çeyrek saray simetrisi",
            SymmetryMode.BILATERAL: "Bilateral sol-sağ ayna simetrisi",
            SymmetryMode.VERTICAL: "Dikey üst-alt ayna simetrisi",
            SymmetryMode.RADIAL: "Radyal dairesel simetri",
            SymmetryMode.ASYMMETRIC: "Asimetrik modern serbest",
        }
        sym_str = sym_mapping.get(brief.symmetry_mode, "Çift yönlü 4-çeyrek saray simetrisi")

        color_str = brief.primary_color + (f" ve {brief.secondary_color}" if brief.secondary_color else "")
        img_output_path = self.output_dir / f"{brief.brief_id}.png"
        day28_brief = StructuredDesignBrief(
            brief_id=brief.brief_id,
            style=brief.style,
            motif=brief.motif,
            color=color_str,
            composition=brief.composition or "",
            border=brief.border_type or "",
            symmetry=sym_str,
            seed=brief.seed
        )
        img_rgb, exp_record = self.sdxl_controller.generate(
            brief=day28_brief,
            output_path=img_output_path
        )
        latencies["sdxl_generation_ms"] = round((time.perf_counter() - t1) * 1000, 2)

        # -------------------------------------------------------------
        # ADIM 3: Çok Boyutlu Görsel Analiz (Day 29)
        # K-Means, CIELAB/CIEDE2000, Simetri, Kenar/Dikiş
        # -------------------------------------------------------------
        t2 = time.perf_counter()
        analysis_rep = self.master_analyzer.analyze(
            image_input=img_rgb,
            generate_panel=False
        )
        latencies["visual_analysis_ms"] = round((time.perf_counter() - t2) * 1000, 2)

        # -------------------------------------------------------------
        # ADIM 4: CNN Feature Extraction ve Benzerlik Araması (Day 29)
        # -------------------------------------------------------------
        t3 = time.perf_counter()
        similar_items: List[Dict[str, Any]] = []

        if empty_catalog_test:
            # Yaprak 60: Boş referans görsel koleksiyonu hata senaryosu
            empty_retriever = CNNEmbeddingRetriever(catalog_path=Path("non_existent_empty.json"))
            empty_matches, empty_warn = empty_retriever.search_similar(img_rgb, top_k=3)
            similar_items = [
                {
                    "carpet_id": item.carpet_id,
                    "name": item.title,
                    "similarity_score": item.similarity_score,
                    "note": empty_warn or "Boş katalog fallback devrede."
                }
                for item in empty_matches
            ]
            if not similar_items:
                similar_items = [
                    {
                        "carpet_id": "CAT-FALLBACK-01",
                        "name": "Katalog Boş (Fallback)",
                        "similarity_score": 0.0,
                        "note": empty_warn or "Boş katalog fallback devrede (Yaprak 60)."
                    }
                ]
        else:
            similar_items = [
                {
                    "carpet_id": item.carpet_id,
                    "name": item.title,
                    "style": item.style,
                    "similarity_score": round(item.similarity_score, 4),
                    "primary_colors": item.primary_colors,
                }
                for item in analysis_rep.cnn_embedding.top_matches
            ]
        latencies["cnn_similarity_search_ms"] = round((time.perf_counter() - t3) * 1000, 2)

        # -------------------------------------------------------------
        # ADIM 5: 4 Teknik Sınırın Raporlanması (Yaprak 60)
        # -------------------------------------------------------------
        limitations_rep = DEFAULT_LIMITATIONS
        total_latency = round((time.perf_counter() - t_global_start) * 1000, 2)

        return IntegratedPipelineOutput(
            brief=brief,
            prompt_result=prompt_res,
            generated_image_path=str(img_output_path),
            color_analysis={
                "dominant_colors": [
                    {
                        "hex": c.hex_code,
                        "percentage": round(c.percentage, 1),
                        "nearest_yarn": c.nearest_yarn_name or "Belirsiz İplik",
                        "delta_e": round(c.delta_e_to_target if c.delta_e_to_target is not None else 0.0, 2)
                    }
                    for c in analysis_rep.color_analysis.dominant_colors
                ],
                "mean_delta_e": round(analysis_rep.color_analysis.mean_delta_e, 2),
                "creel_colors_count": len(analysis_rep.color_analysis.dominant_colors)
            },
            symmetry_analysis={
                "horizontal_score": round(analysis_rep.symmetry_analysis.horizontal_symmetry, 3),
                "vertical_score": round(analysis_rep.symmetry_analysis.vertical_symmetry, 3),
                "quadrant_score": round(analysis_rep.symmetry_analysis.four_way_symmetry, 3),
                "repeat_autocorr": round(analysis_rep.symmetry_analysis.repeat_autocorrelation_score, 3)
            },
            seam_analysis={
                "horizontal_mse": round(analysis_rep.seam_continuity.left_right_mse, 2),
                "vertical_mse": round(analysis_rep.seam_continuity.top_bottom_mse, 2),
                "sobel_jump": round(10.0 * (1.0 - analysis_rep.seam_continuity.continuity_score), 2),
                "is_tileable": not analysis_rep.seam_continuity.has_seam_discontinuity
            },
            similar_carpets=similar_items,
            limitations_report=limitations_rep,
            execution_time_ms=latencies,
            total_latency_ms=total_latency,
            success=True
        )
