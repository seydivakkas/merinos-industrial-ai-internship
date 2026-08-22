"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Simetri ve Tekrar Yapısı Analizörü
Staj Defteri Yaprak 57 Müfredatı
"""

from __future__ import annotations
import logging
from typing import Tuple

import cv2
import numpy as np

from day29.mini_project.src.models import SymmetryAnalysisResult

logger = logging.getLogger("MerinosSymmetryAnalyzer")


class StructuralSymmetryAnalyzer:
    """
    Halı görsellerindeki yatay ve dikey simetri özelliklerini analiz eden sınıf (Staj Defteri Yaprak 57).
    Üretilen desenin yatay/dikey ayna simetrisini ve otokorelasyon tabanlı periyodik tekrar yapısını inceler.
    """

    def __init__(self, blur_kernel: int = 5):
        self.blur_kernel = blur_kernel

    def analyze_symmetry(self, image_path: str) -> Dict[str, float]:
        """Görselin yatay ve dikey simetri skorlarını hesaplar (Şekil 57 minimal implementasyonu)."""
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            try:
                image = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            except Exception:
                pass
        if image is None:
            raise ValueError(f"Görüntü okunamadı: {image_path}")

        # Yatay simetri
        h_sym = self._horizontal_symmetry_score(image)
        # Dikey simetri
        v_sym = self._vertical_symmetry_score(image)

        return {
            "horizontal_symmetry": float(h_sym),
            "vertical_symmetry": float(v_sym)
        }

    def _horizontal_symmetry_score(self, image: np.ndarray) -> float:
        """Yatay simetri skorunu hesaplar."""
        h, w = image.shape
        top = image[:h // 2, :]
        bottom = cv2.flip(image[h // 2:, :], 0)
        diff = cv2.absdiff(top, bottom)
        score = 1.0 - (np.mean(diff) / 255.0)
        return float(score)

    def _vertical_symmetry_score(self, image: np.ndarray) -> float:
        """Dikey simetri skorunu hesaplar."""
        h, w = image.shape
        left = image[:, :w // 2]
        right = cv2.flip(image[:, w // 2:], 1)
        diff = cv2.absdiff(left, right)
        score = 1.0 - (np.mean(diff) / 255.0)
        return float(score)

    def _prepare_gray(self, image_rgb: np.ndarray) -> np.ndarray:
        """Görüntüyü gri tonlamaya çevirip mikro gürültüyü hafifçe yumuşatır."""
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        if self.blur_kernel > 1:
            gray = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        return gray

    def calculate_horizontal_symmetry(self, image_rgb: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Yatay (sol-sağ / bilateral) ayna simetrisini hesaplar.
        Görüntü sol-sağ aynalanır (fliplr) ve orijinaliyle korelasyonu hesaplanır.
        Dönüş: (simetri_skoru [0.0 - 1.0], ayna_fark_haritasi)
        """
        gray = self._prepare_gray(image_rgb).astype(np.float64)
        flipped_lr = np.fliplr(gray)

        diff = np.abs(gray - flipped_lr).astype(np.uint8)
        var = float(np.var(gray))
        if var < 1e-6:
            return 1.0, diff

        cov = float(np.mean((gray - np.mean(gray)) * (flipped_lr - np.mean(flipped_lr))))
        corr = cov / var
        score = max(0.0, min(1.0, corr))
        return round(float(score), 3), diff

    def calculate_vertical_symmetry(self, image_rgb: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Dikey (üst-alt) ayna simetrisini hesaplar.
        Görüntü üst-alt aynalanır (flipud) ve orijinaliyle korelasyonu hesaplanır.
        Dönüş: (simetri_skoru [0.0 - 1.0], ayna_fark_haritasi)
        """
        gray = self._prepare_gray(image_rgb).astype(np.float64)
        flipped_ud = np.flipud(gray)

        diff = np.abs(gray - flipped_ud).astype(np.uint8)
        var = float(np.var(gray))
        if var < 1e-6:
            return 1.0, diff

        cov = float(np.mean((gray - np.mean(gray)) * (flipped_ud - np.mean(flipped_ud))))
        corr = cov / var
        score = max(0.0, min(1.0, corr))
        return round(float(score), 3), diff

    def calculate_four_way_symmetry(self, image_rgb: np.ndarray) -> float:
        """
        4-çeyrekli Osmanlı saray simetrisini hesaplar (hem yatay hem dikey).
        """
        h_score, _ = self.calculate_horizontal_symmetry(image_rgb)
        v_score, _ = self.calculate_vertical_symmetry(image_rgb)
        return round(float(np.sqrt(h_score * v_score)), 3)

    def calculate_repeat_autocorrelation(self, image_rgb: np.ndarray) -> float:
        """
        Görüntü içi periyodik motif tekrar hissini 2D kaydırmalı korelasyon ile sayısallaştırır.
        """
        gray = self._prepare_gray(image_rgb).astype(np.float32)
        gray_norm = gray - np.mean(gray)
        norm_std = np.std(gray_norm)
        if norm_std > 1e-6:
            gray_norm = gray_norm / norm_std

        # Görüntünün 1/4 ve 1/8 kaydırmalarındaki otokorelasyon tepe noktalarını ara
        h, w = gray.shape
        shifts = [(h // 4, 0), (0, w // 4), (h // 4, w // 4)]
        corr_scores = []

        for sy, sx in shifts:
            shifted = np.roll(gray_norm, shift=(sy, sx), axis=(0, 1))
            corr = float(np.mean(gray_norm * shifted))
            corr_scores.append(corr)

        max_corr = max(corr_scores) if corr_scores else 0.0
        # Normalizasyon: 0.0 ile 1.0 arası
        repeat_score = max(0.0, min(1.0, (max_corr + 0.5) / 1.5))
        return round(float(repeat_score), 3)

    def analyze(self, image_rgb: np.ndarray) -> SymmetryAnalysisResult:
        """
        Tüm simetri ve tekrar yapısı analizlerini çalıştırıp Yaprak 57 formatında raporlar.
        """
        h_score, _ = self.calculate_horizontal_symmetry(image_rgb)
        v_score, _ = self.calculate_vertical_symmetry(image_rgb)
        four_way = self.calculate_four_way_symmetry(image_rgb)
        repeat_score = self.calculate_repeat_autocorrelation(image_rgb)

        # Mühendislik değerlendirmesi (Yaprak 57)
        if h_score >= 0.85 and v_score >= 0.85:
            verdict = (
                f"TAM DÖRT ÇEYREK SARAY SİMETRİSİ (Yatay: {h_score}, Dikey: {v_score}): "
                f"Görsel merkez madalyon ve köşe bordürleri açısından her iki eksende de yüksek yapısal intizama sahiptir."
            )
        elif h_score >= 0.80:
            verdict = (
                f"GÜÇLÜ BİLATERAL (SOL-SAĞ) AYNA SİMETRİSİ (Yatay: {h_score}, Dikey: {v_score}): "
                f"Desen mihrap veya klasik göbek düzeninde sol-sağ ekseninde simetriktir."
            )
        elif repeat_score >= 0.70:
            verdict = (
                f"PERİYODİK TEKRAR DOKUSU (Tekrar Skoru: {repeat_score}, Simetri: {h_score}): "
                f"Desen ayna simetrisi yerine tekrarlayan ritmik motiflerden (ör. baklava, geometrik) oluşmaktadır."
            )
        else:
            verdict = (
                f"ASİMETRİK / SERBEST KOMPOZİSYON (Yatay: {h_score}, Dikey: {v_score}): "
                f"Görsel ayna simetrisi veya belirgin bir periyodik tekrar içermeyen modern serbest tasarım karakterindedir."
            )

        verdict += (
            " (Not: Simetri ve tekrar incelemeleri yapısal düzen hakkında ipucu verir; "
            "tek bir skora aşırı anlam yüklenmemeli, destekleyici bir mühendislik göstergesi olarak değerlendirilmelidir - Yaprak 57)."
        )

        return SymmetryAnalysisResult(
            horizontal_symmetry=h_score,
            vertical_symmetry=v_score,
            four_way_symmetry=four_way,
            repeat_autocorrelation_score=repeat_score,
            verdict=verdict
        )
