"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Kenar ve Dikiş Sürekliliği (Seam Continuity / Tileability) Analizörü
Staj Defteri Yaprak 58 Müfredatı
"""

from __future__ import annotations
import logging
from typing import Tuple

import cv2
import numpy as np

from day29.mini_project.src.models import SeamContinuityResult

logger = logging.getLogger("MerinosSeamAnalyzer")


class SeamContinuityAnalyzer:
    """
    Staj Defteri Yaprak 58: Üretilen halı görselinin kenar sürekliliğini (sol-sağ ve üst-alt
    dikiş hatları arasındaki renk atlaması ve motif kopukluğu kontrolü) inceleyen analiz motoru.
    """

    def __init__(self, strip_width: int = 8, acceptable_mse_threshold: float = 1200.0):
        self.strip_width = strip_width
        self.acceptable_mse_threshold = acceptable_mse_threshold

    def evaluate_seam_continuity(
        self,
        image_rgb: np.ndarray
    ) -> Tuple[float, float, float, bool]:
        """
        Sol-sağ ve üst-alt kenar şeritlerinin uyumunu hesaplar.
        Dönüş: (lr_mse, tb_mse, continuity_score [0-1], has_discontinuity)
        """
        h, w, _ = image_rgb.shape
        strip = min(self.strip_width, w // 4, h // 4)

        # 1. Sol ve Sağ Kenar Şeritleri (RGB piksel farkı)
        left_strip = image_rgb[:, :strip, :].astype(np.float64)
        right_strip = image_rgb[:, -strip:, :].astype(np.float64)
        lr_mse = float(np.mean((left_strip - right_strip) ** 2))

        # 2. Üst ve Alt Kenar Şeritleri
        top_strip = image_rgb[:strip, :, :].astype(np.float64)
        bottom_strip = image_rgb[-strip:, :, :].astype(np.float64)
        tb_mse = float(np.mean((top_strip - bottom_strip) ** 2))

        # 3. Kenar Gradyan Sürekliliği (Sobel ile ani parlaklık/renk sıçramaları)
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_lr_diff = float(np.mean((sobel_x[:, :strip] - sobel_x[:, -strip:]) ** 2))

        # Ortalama kenar sapması
        combined_mse = (lr_mse + tb_mse + grad_lr_diff * 0.2) / 2.0

        # Normalizasyon: 0.0 ile 1.0 arası (0 MSE -> 1.0 skor, 5000+ MSE -> ~0.1 skor)
        continuity_score = max(0.0, min(1.0, 1.0 / (1.0 + combined_mse / 800.0)))
        has_discontinuity = combined_mse > self.acceptable_mse_threshold

        return round(lr_mse, 2), round(tb_mse, 2), round(continuity_score, 3), has_discontinuity

    def analyze(self, image_rgb: np.ndarray) -> SeamContinuityResult:
        """
        Kenar süreklilik analizini çalıştırır ve Yaprak 58 formatında raporlar.
        """
        lr_mse, tb_mse, continuity_score, has_discontinuity = self.evaluate_seam_continuity(image_rgb)

        if not has_discontinuity:
            verdict = (
                f"YÜKSEK KENAR SÜREKLİLİĞİ (Skor: {continuity_score}, Sol-Sağ MSE: {lr_mse}, Üst-Alt MSE: {tb_mse}): "
                f"Desen kenarları arasında ani renk sıçraması veya keskin motif kırılması tespit edilmedi. "
                f"Görsel yan yana döşenebilirlik (tileability) hissini desteklemektedir."
            )
        else:
            verdict = (
                f"BELİRGİN KENAR KOPUKLUĞU / DİKİŞ FARKI (Skor: {continuity_score}, Sol-Sağ MSE: {lr_mse}, Üst-Alt MSE: {tb_mse}): "
                f"Kenar şeritleri arasında belirgin renk veya motif uyumsuzluğu bulundu. "
                f"Desen çerçeveli/kapalı bir bordüre sahip olabilir ya da uç uca döşendiğinde dikiş çizgisi bariz görünür."
            )

        verdict += (
            " (Not: Buradaki amaç gerçek üretim uygunluğu kararı vermek değildir; "
            "yalnızca desenin kenarlarında ani kopukluk ve motif kırılması olup olmadığını gözlemlemektir - Yaprak 58)."
        )

        return SeamContinuityResult(
            strip_width_pixels=self.strip_width,
            left_right_mse=lr_mse,
            top_bottom_mse=tb_mse,
            continuity_score=continuity_score,
            has_seam_discontinuity=has_discontinuity,
            verdict=verdict
        )
