"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: K-Means Renk Paleti ve CIELAB Delta E* Analizörü
Staj Defteri Yaprak 57 Müfredatı
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import cv2
import numpy as np
from sklearn.cluster import KMeans

from day29.mini_project.src.models import DominantColor, ColorAnalysisResult

logger = logging.getLogger("MerinosColorAnalyzer")


def rgb_to_cielab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Standart 8-bit RGB [0, 255] değerini CIELAB (L*, a*, b*) koordinatlarına dönüştürür.
    OpenCV COLOR_RGB2LAB çıktısını standart L* [0, 100], a* [-128, 127], b* [-128, 127] aralığına ölçekler.
    """
    arr = np.uint8([[list(rgb)]])
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)[0, 0]
    # OpenCV uint8 dönüşümünde L = L * 255/100, a = a + 128, b = b + 128
    L = float(lab[0]) * 100.0 / 255.0
    a = float(lab[1]) - 128.0
    b = float(lab[2]) - 128.0
    return (round(L, 2), round(a, 2), round(b, 2))


def calculate_delta_e_cielab(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]) -> float:
    """
    İki CIELAB rengi arasındaki Öklid renk farkını (CIE76 Delta E*) hesaplar:
    Delta E* = sqrt((dL)^2 + (da)^2 + (db)^2)
    """
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return float(np.sqrt(dL**2 + da**2 + db**2))


def calculate_ciede2000(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]) -> float:
    """
    İki CIELAB rengi arasındaki CIEDE2000 renk farkını hesaplar.
    İnsan gözünün algısal duyarlılığına en yakın endüstriyel tekstil standardıdır.
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    C1 = np.sqrt(a1**2 + b1**2)
    C2 = np.sqrt(a2**2 + b2**2)
    C_bar = (C1 + C2) / 2.0

    G = 0.5 * (1.0 - np.sqrt(C_bar**7 / (C_bar**7 + 25**7 + 1e-9)))
    a1_prime = (1.0 + G) * a1
    a2_prime = (1.0 + G) * a2

    C1_prime = np.sqrt(a1_prime**2 + b1**2)
    C2_prime = np.sqrt(a2_prime**2 + b2**2)

    h1_prime = np.degrees(np.arctan2(b1, a1_prime)) % 360.0
    h2_prime = np.degrees(np.arctan2(b2, a2_prime)) % 360.0

    dL_prime = L2 - L1
    dC_prime = C2_prime - C1_prime

    if C1_prime * C2_prime == 0:
        dh_prime = 0.0
    elif abs(h1_prime - h2_prime) <= 180.0:
        dh_prime = h2_prime - h1_prime
    elif h2_prime <= h1_prime:
        dh_prime = h2_prime - h1_prime + 360.0
    else:
        dh_prime = h2_prime - h1_prime - 360.0

    dH_prime = 2.0 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(dh_prime / 2.0))

    L_bar_prime = (L1 + L2) / 2.0
    C_bar_prime = (C1_prime + C2_prime) / 2.0

    if C1_prime * C2_prime == 0:
        h_bar_prime = h1_prime + h2_prime
    elif abs(h1_prime - h2_prime) <= 180.0:
        h_bar_prime = (h1_prime + h2_prime) / 2.0
    elif (h1_prime + h2_prime) < 360.0:
        h_bar_prime = (h1_prime + h2_prime + 360.0) / 2.0
    else:
        h_bar_prime = (h1_prime + h2_prime - 360.0) / 2.0

    T = (1.0 - 0.17 * np.cos(np.radians(h_bar_prime - 30.0))
         + 0.24 * np.cos(np.radians(2.0 * h_bar_prime))
         + 0.32 * np.cos(np.radians(3.0 * h_bar_prime + 6.0))
         - 0.20 * np.cos(np.radians(4.0 * h_bar_prime - 63.0)))

    d_theta = 30.0 * np.exp(-(((h_bar_prime - 275.0) / 25.0)**2))
    R_C = 2.0 * np.sqrt(C_bar_prime**7 / (C_bar_prime**7 + 25**7 + 1e-9))
    S_L = 1.0 + (0.015 * (L_bar_prime - 50.0)**2) / np.sqrt(20.0 + (L_bar_prime - 50.0)**2)
    S_C = 1.0 + 0.045 * C_bar_prime
    S_H = 1.0 + 0.015 * C_bar_prime * T
    R_T = -np.sin(np.radians(2.0 * d_theta)) * R_C

    k_L, k_C, k_H = 1.0, 1.0, 1.0
    term_L = dL_prime / (k_L * S_L)
    term_C = dC_prime / (k_C * S_C)
    term_H = dH_prime / (k_H * S_H)

    de00 = np.sqrt(term_L**2 + term_C**2 + term_H**2 + R_T * term_C * term_H)
    return float(round(de00, 3))


class ColorPaletteAnalyzer:
    """
    Halı görsellerindeki baskın renkleri analiz eden sınıf (Staj Defteri Yaprak 57).
    Üretilen halı deseninin K-Means ile baskın renklerini çıkaran, CIELAB uzayında
    renk mesafesi (Delta E) ve hedef palet uyumunu hesaplayan analiz motoru.
    """

    def __init__(
        self,
        n_colors: int = 5,
        target_palettes_path: Optional[Path | str] = None
    ):
        # Eğer ilk argüman hedef palet yolu olarak geçildiyse uyumluluk sağla
        if isinstance(n_colors, (str, Path)) and target_palettes_path is None:
            target_palettes_path = n_colors
            self.n_colors = 5
        else:
            self.n_colors = int(n_colors)

        self.target_palettes: List[Dict[str, Any]] = []
        if target_palettes_path:
            p = Path(target_palettes_path)
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        self.target_palettes = json.load(f)
                except Exception as e:
                    logger.warning(f"Hedef renk paletleri yüklenemedi: {e}")

    def get_dominant_colors(self, image_path: str) -> List[Tuple[int, int, int]]:
        """Görseldeki baskın renkleri döndürür (Şekil 57 minimal implementasyonu)."""
        image = cv2.imread(image_path)
        if image is None:
            try:
                image = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
            except Exception:
                pass
        if image is None:
            raise ValueError(f"Görüntü okunamadı: {image_path}")

        # BGR'den RGB'ye çevir
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = image.reshape(-1, 3)

        # KMeans ile baskın renkleri bul
        kmeans = KMeans(n_clusters=self.n_colors, random_state=42)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int)

        return [tuple(int(c) for c in color) for color in colors]

    def extract_dominant_colors(
        self,
        image_rgb: np.ndarray,
        num_clusters: int = 5,
        random_state: int = 42
    ) -> List[DominantColor]:
        """
        K-Means kümeleme ile görüntüden num_clusters adet merkez rengi ve yüzdelerini çıkarır.
        """
        # Hızlı ve kararlı işlem için 256x256'ya yeniden boyutlandır
        h, w = image_rgb.shape[:2]
        if h > 256 or w > 256:
            resized = cv2.resize(image_rgb, (256, 256), interpolation=cv2.INTER_AREA)
        else:
            resized = image_rgb

        pixels = resized.reshape((-1, 3)).astype(np.float32)

        # K-Means çalıştır
        kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, n_init=10, max_iter=150)
        labels = kmeans.fit_predict(pixels)
        centers = kmeans.cluster_centers_

        # Piksel yüzdelerini hesapla
        total_pixels = len(labels)
        counts = np.bincount(labels, minlength=num_clusters)

        dominant_colors = []
        for i in range(num_clusters):
            rgb_tuple = tuple(int(round(c)) for c in centers[i])
            rgb_clamped = (
                max(0, min(255, rgb_tuple[0])),
                max(0, min(255, rgb_tuple[1])),
                max(0, min(255, rgb_tuple[2]))
            )
            hex_code = f"#{rgb_clamped[0]:02X}{rgb_clamped[1]:02X}{rgb_clamped[2]:02X}"
            lab_coords = rgb_to_cielab(rgb_clamped)
            pct = round(float(counts[i]) / total_pixels * 100.0, 2)

            dominant_colors.append(
                DominantColor(
                    cluster_index=i,
                    rgb=rgb_clamped,
                    hex_code=hex_code,
                    lab=lab_coords,
                    percentage=pct
                )
            )

        # Yüzdeye göre azalan sırada sırala
        dominant_colors.sort(key=lambda c: c.percentage, reverse=True)
        return dominant_colors

    def analyze(
        self,
        image_rgb: np.ndarray,
        num_clusters: int = 5,
        target_palette_id: Optional[str] = None
    ) -> ColorAnalysisResult:
        """
        Görseli analiz eder, hedef palet ile CIELAB Delta E mesafesini ölçer.
        """
        dominant_colors = self.extract_dominant_colors(image_rgb, num_clusters=num_clusters)

        # Hedef paleti seç
        chosen_palette = None
        if self.target_palettes:
            if target_palette_id:
                for p in self.target_palettes:
                    if p.get("palette_id") == target_palette_id:
                        chosen_palette = p
                        break
            if not chosen_palette:
                chosen_palette = self.target_palettes[0]

        delta_e_list = []
        if chosen_palette:
            target_colors = chosen_palette.get("colors", [])
            for dom_col in dominant_colors:
                best_de = 999.0
                best_name = None
                for tc in target_colors:
                    t_lab = tuple(tc["lab"])
                    de = calculate_ciede2000(dom_col.lab, t_lab)
                    if de < best_de:
                        best_de = de
                        best_name = tc["name"]

                dom_col.nearest_yarn_name = best_name
                dom_col.delta_e_to_target = round(best_de, 2)
                delta_e_list.append(best_de)

        mean_de = round(float(np.mean(delta_e_list)), 2) if delta_e_list else 0.0
        min_de = round(float(np.min(delta_e_list)), 2) if delta_e_list else 0.0

        # Mühendislik değerlendirme yorumu (Yaprak 57)
        if mean_de < 3.0:
            verdict = (
                f"YÜKSEK RENK UYUMU (Ort. ΔE* = {mean_de}): Çıkarılan K-Means renk merkezleri, "
                f"hedef Merinos paleti ile insan gözünün ayırt edemeyeceği kadar yakın bir örtüşme gösterdi."
            )
        elif mean_de < 6.0:
            verdict = (
                f"KABUL EDİLEBİLİR RENK YAKINLIĞI (Ort. ΔE* = {mean_de}): Difüzyon/tasarım aşaması "
                f"ana renk tonlarını yakaladı, ancak ton geçişlerinde endüstriyel bobin toleranslarına yakın sapmalar mevcut."
            )
        else:
            verdict = (
                f"BELİRGİN RENK FARKI (Ort. ΔE* = {mean_de}): Model hedef paletten belirgin biçimde saptı. "
                f"İstenen renk tonları ile üretilen piksel merkezleri arasında algısal kontrast yüksektir."
            )

        verdict += (
            " (Not: K-Means analizi yalnız baskın renklerin varlığını ve oranını ölçer; "
            "renklerin desen içindeki geometrik konumunu veya motif yapısını doğrudan açıklamaz - Yaprak 57)."
        )

        return ColorAnalysisResult(
            num_clusters=num_clusters,
            dominant_colors=dominant_colors,
            target_palette_name=chosen_palette.get("name") if chosen_palette else None,
            mean_delta_e=mean_de,
            min_delta_e=min_de,
            verdict=verdict
        )
