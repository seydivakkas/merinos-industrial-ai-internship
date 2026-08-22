"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Çok Boyutlu Görsel Analiz Orkestratörü (Master Analyzer)
Staj Defteri Yaprak 57 ve 58 Müfredatı
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Optional, Union, Dict, Any

import cv2
import numpy as np

from day29.mini_project.src.models import ComprehensiveVisualReport
from day29.mini_project.src.color_analyzer import ColorPaletteAnalyzer
from day29.mini_project.src.symmetry_analyzer import StructuralSymmetryAnalyzer
from day29.mini_project.src.seam_analyzer import SeamContinuityAnalyzer
from day29.mini_project.src.embedding_retriever import CNNEmbeddingRetriever
from day29.mini_project.src.visualizer import VisualAnalysisDashboard

logger = logging.getLogger("MerinosMasterAnalyzer")


def read_image_utf8(path: Path) -> np.ndarray:
    """Windows Türkçe karakterli dosya yollarında cv2.imread çökmesini önleyen ikili okuyucu."""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if bgr is not None:
            return bgr
    except Exception:
        pass
    return cv2.imread(str(path))


class MasterCarpetAnalyzer:
    """
    Staj Defteri Yaprak 57 ve 58'de tanımlanan 4 temel görsel analiz yöntemini
    tek bir orkestratör altında birleştiren ana sınıf.
    """

    def __init__(
        self,
        target_palettes_path: Optional[Path] = None,
        reference_catalog_path: Optional[Path] = None
    ):
        base_dir = Path(__file__).resolve().parent.parent
        fixtures_dir = base_dir / "fixtures"

        if target_palettes_path is None:
            target_palettes_path = fixtures_dir / "merinos_target_palettes.json"
        if reference_catalog_path is None:
            reference_catalog_path = fixtures_dir / "reference_carpet_catalog.json"

        self.color_analyzer = ColorPaletteAnalyzer(target_palettes_path=target_palettes_path)
        self.symmetry_analyzer = StructuralSymmetryAnalyzer()
        self.seam_analyzer = SeamContinuityAnalyzer()
        self.retriever = CNNEmbeddingRetriever(catalog_path=reference_catalog_path)
        self.visualizer = VisualAnalysisDashboard()

    def analyze(
        self,
        image_input: Union[str, Path, np.ndarray],
        target_palette_id: Optional[str] = "PAL-OSMANLI-01",
        top_k: int = 3,
        output_dir: Optional[Path] = None,
        generate_panel: bool = True
    ) -> ComprehensiveVisualReport:
        """
        Verilen halı görseli üzerinde Yaprak 57 ve 58 analizlerini sırayla yürütür:
        1. K-Means Renk Kümeleme & CIELAB Delta E*
        2. Yatay/Dikey Ayna Simetrisi & Tekrar Otokorelasyonu
        3. Kenar ve Dikiş Sürekliliği (Tileability)
        4. Pretrained CNN Embedding & Top-K Benzerlik Araması
        """
        start_time = time.time()

        # Görseli yükle
        if isinstance(image_input, (str, Path)):
            img_path = Path(image_input)
            if not img_path.exists():
                raise FileNotFoundError(f"Görsel bulunamadı: {img_path}")
            bgr = read_image_utf8(img_path)
            if bgr is None:
                raise ValueError(f"Görsel okunamadı: {img_path}")
            image_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            img_path_str = str(img_path)
            report_id = f"REP-{img_path.stem}"
        elif isinstance(image_input, np.ndarray):
            image_rgb = image_input
            img_path_str = "memory_array.png"
            report_id = f"REP-MEM-{int(start_time)}"
        else:
            raise TypeError("Geçersiz görsel girdisi: dosya yolu (str, Path) veya np.ndarray beklenir.")

        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
            output_dir = base_dir / "outputs"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Renk Analizi (Yaprak 57)
        color_res = self.color_analyzer.analyze(
            image_rgb,
            num_clusters=5,
            target_palette_id=target_palette_id
        )

        # 2. Simetri Analizi (Yaprak 57)
        symmetry_res = self.symmetry_analyzer.analyze(image_rgb)

        # 3. Kenar Sürekliliği Analizi (Yaprak 58)
        seam_res = self.seam_analyzer.analyze(image_rgb)

        # 4. CNN Embedding & Benzerlik (Yaprak 58)
        cnn_res = self.retriever.analyze(image_rgb, top_k=top_k)

        elapsed = round(time.time() - start_time, 3)

        # Mühendislik Sentez Yorumu (Yaprak 57 & 58 Kapanışı)
        synthesis = (
            f"ÇOK BOYUTLU GÖRSEL ANALİZ TAMAMLANDI (İşlem Süresi: {elapsed} sn). "
            f"K-Means ve CIELAB analizi baskın renk tonlarının hedef palete yakınlığını "
            f"(Ort. ΔE* = {color_res.mean_delta_e}) doğruladı. "
            f"Simetri motoru yatayda %{symmetry_res.horizontal_symmetry*100:.1f}, "
            f"dikeyde %{symmetry_res.vertical_symmetry*100:.1f} ayna düzeni tespit etti. "
            f"Kenar analizi %{seam_res.continuity_score*100:.1f} süreklilik puanı verdi. "
            f"CNN embedding ise en yakın referans olarak '{cnn_res.top_matches[0].title if cnn_res.top_matches else 'Yok'}' "
            f"desenini buldu. Bu ölçümlerin her biri görüntünün farklı bir mühendislik boyutunu aydınlatmakla "
            f"birlikte, hiçbiri tek başına 'iyi tasarım' veya 'üretilebilir halı' hükmü vermez (Yaprak 58)."
        )

        report = ComprehensiveVisualReport(
            report_id=report_id,
            image_path=img_path_str,
            color_analysis=color_res,
            symmetry_analysis=symmetry_res,
            seam_continuity=seam_res,
            cnn_embedding=cnn_res,
            synthesis_verdict=synthesis,
            execution_time_sec=elapsed
        )

        # 300 DPI Teşhis Paneli Üretimi
        if generate_panel:
            panel_path = output_dir / f"{report_id}_diagnostic_panel.png"
            self.visualizer.create_dashboard(report, image_rgb, panel_path)
            report.diagnostic_panel_path = str(panel_path)

        # JSON Raporunu Kaydet
        report_json_path = output_dir / f"{report_id}_report.json"
        with open(report_json_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        return report
