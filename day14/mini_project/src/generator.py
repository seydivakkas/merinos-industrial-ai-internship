"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
4 Farklı Jakar Desen Sınıfında Sentetik Halı Jeneratörü (CarpetPatternFixtureGenerator)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import cv2
import numpy as np

from .models import PatternClass


def _safe_imwrite(filepath: Path, image: np.ndarray) -> bool:
    """Windows Türkçe karakterli dosya yollarını destekleyen güvenli imwrite."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        ext = filepath.suffix if filepath.suffix else ".png"
        success, encoded = cv2.imencode(ext, image)
        if not success:
            return False
        with open(filepath, "wb") as f:
            f.write(encoded.tobytes())
        return True
    except Exception as e:
        print(f"Hata: Görsel yazılamadı ({filepath}): {e}")
        return False


def _safe_imread(filepath: Path, flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """Windows Türkçe karakterli dosya yollarını destekleyen güvenli imread."""
    try:
        if not filepath.exists():
            return None
        with open(filepath, "rb") as f:
            data = f.read()
        arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(arr, flags)
        return img
    except Exception as e:
        print(f"Hata: Görsel okunamadı ({filepath}): {e}")
        return None


class CarpetPatternFixtureGenerator:
    """Desen sınıflandırma ve görsel arama testleri için sentetik jakarlı halılar üretir."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def generate_medallion_classic(
        self,
        width: int = 400,
        height: int = 400,
    ) -> Tuple[np.ndarray, PatternClass]:
        """Klasik oryantal madalyon halısı üretir (Koyu lacivert zemin, kırmızı madalyon, altın bordür)."""
        carpet = np.full((height, width, 3), (50, 30, 20), dtype=np.uint8)  # Lacivert zemin
        
        # Kumaş dokusu
        y_grid, x_grid = np.ogrid[:height, :width]
        weave = ((x_grid % 3 == 0) | (y_grid % 3 == 0)).astype(np.uint8) * 8
        carpet = cv2.add(carpet, cv2.merge([weave, weave, weave]))

        # Dış ve iç bordürler
        cv2.rectangle(carpet, (20, 20), (width - 20, height - 20), (30, 60, 180), 12)  # Kırmızı şerit
        cv2.rectangle(carpet, (40, 40), (width - 40, height - 40), (40, 180, 220), 4)  # Altın şerit

        # Köşe spandrelleri (Üçgenler)
        c_size = 75
        corners = [
            [(40, 40), (40 + c_size, 40), (40, 40 + c_size)],
            [(width - 40, 40), (width - 40 - c_size, 40), (width - 40, 40 + c_size)],
            [(40, height - 40), (40 + c_size, height - 40), (40, height - 40 - c_size)],
            [(width - 40, height - 40), (width - 40 - c_size, height - 40), (width - 40, height - 40 - c_size)],
        ]
        for pts in corners:
            cv2.fillPoly(carpet, [np.array(pts, dtype=np.int32)], (40, 70, 190))

        # Merkez madalyon ve loblar
        center = (width // 2, height // 2)
        cv2.circle(carpet, center, 90, (40, 70, 190), -1)  # Kırmızı gövde
        for angle in range(0, 360, 45):
            rad = np.deg2rad(angle)
            cx = int(center[0] + 85 * np.cos(rad))
            cy = int(center[1] + 85 * np.sin(rad))
            cv2.circle(carpet, (cx, cy), 22, (40, 70, 190), -1)

        cv2.circle(carpet, center, 65, (40, 180, 220), -1)  # Altın halka
        cv2.circle(carpet, center, 40, (200, 215, 230), -1)  # Krem çiçek
        cv2.circle(carpet, center, 15, (30, 40, 140), -1)   # Kırmızı göbek

        return carpet, PatternClass.MEDALLION_CLASSIC

    def generate_geometric_modern(
        self,
        width: int = 400,
        height: int = 400,
    ) -> Tuple[np.ndarray, PatternClass]:
        """Modern Bauhaus geometrik halı üretir (Gri zemin, antrasit/hardal keskin prizmalar)."""
        carpet = np.full((height, width, 3), (215, 215, 220), dtype=np.uint8)  # Açık gri

        # Siyah dış çerçeve
        cv2.rectangle(carpet, (15, 15), (width - 15, height - 15), (35, 35, 40), 8)

        center = (width // 2, height // 2)
        r = 130

        # Büyük dış baklava (Koyu antrasit)
        diamond_pts = np.array([
            (center[0], center[1] - r),
            (center[0] + r, center[1]),
            (center[0], center[1] + r),
            (center[0] - r, center[1]),
        ], dtype=np.int32)
        cv2.fillPoly(carpet, [diamond_pts], (45, 45, 55))

        # İç ters baklava (Hardal sarısı)
        r_in = 80
        in_pts = np.array([
            (center[0], center[1] - r_in),
            (center[0] + r_in, center[1]),
            (center[0], center[1] + r_in),
            (center[0] - r_in, center[1]),
        ], dtype=np.int32)
        cv2.fillPoly(carpet, [in_pts], (30, 170, 220))

        # Merkez kare (Kiremit kırmızısı)
        cv2.rectangle(carpet, (center[0] - 35, center[1] - 35), (center[0] + 35, center[1] + 35), (40, 70, 180), -1)

        # Çapraz çizgiler
        cv2.line(carpet, (30, 30), (width - 30, height - 30), (35, 35, 40), 3)
        cv2.line(carpet, (30, height - 30), (width - 30, 30), (35, 35, 40), 3)

        return carpet, PatternClass.GEOMETRIC_MODERN

    def generate_floral_traditional(
        self,
        width: int = 400,
        height: int = 400,
    ) -> Tuple[np.ndarray, PatternClass]:
        """Geleneksel çiçekli halı üretir (Krem zemin, tekrarlayan küçük çiçekler ve sarmaşıklar)."""
        carpet = np.full((height, width, 3), (210, 230, 240), dtype=np.uint8)  # İpeksi krem zemin

        # Açık yeşil dalga bordür
        cv2.rectangle(carpet, (25, 25), (width - 25, height - 25), (100, 160, 110), 6)

        # Düzenli ızgarada küçük çiçek rozetleri
        step = 55
        for x in range(60, width - 50, step):
            for y in range(60, height - 50, step):
                # Çiçek taç yaprakları (Pembe)
                for dx, dy in [(-8, 0), (8, 0), (0, -8), (0, 8)]:
                    cv2.circle(carpet, (x + dx, y + dy), 7, (150, 130, 220), -1)
                # Çiçek göbeği (Sarı)
                cv2.circle(carpet, (x, y), 6, (30, 190, 230), -1)
                # Yaprak tendrili (Yeşil)
                cv2.ellipse(carpet, (x + 12, y + 12), (10, 5), 45, 0, 360, (90, 150, 100), -1)

        return carpet, PatternClass.FLORAL_TRADITIONAL

    def generate_vintage_distressed(
        self,
        width: int = 400,
        height: int = 400,
    ) -> Tuple[np.ndarray, PatternClass]:
        """Eskitme efektli vintage bukle halı üretir (Taşlanmış zemin, aşınmış konturlar, yüksek gren)."""
        # Soluk bej/gri taban
        carpet = np.full((height, width, 3), (170, 175, 180), dtype=np.uint8)

        # Soluk madalyon izleri
        center = (width // 2, height // 2)
        cv2.circle(carpet, center, 80, (150, 155, 165), -1)
        cv2.circle(carpet, center, 50, (180, 185, 195), -1)

        # Yoğun taşlanmış eskitme paraziti (Büyük varyanslı Gauss gürültüsü)
        noise = self.rng.normal(0, 22.0, carpet.shape).astype(np.int16)
        carpet = np.clip(carpet.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Aşınmış yatay traşlama çizgileri
        for y in range(10, height - 10, 12):
            if self.rng.rand() > 0.4:
                length = self.rng.randint(60, width - 80)
                start_x = self.rng.randint(20, width - length - 20)
                alpha_val = self.rng.randint(130, 220)
                cv2.line(carpet, (start_x, y), (start_x + length, y), (alpha_val, alpha_val, alpha_val), 1)

        return carpet, PatternClass.VINTAGE_DISTRESSED

    def generate_all_fixtures(self, output_dir: Path) -> Dict[str, Path]:
        """4 farklı sınıfta sentetik halı fikstürlerini üretir ve kaydeder."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}

        # 1. Medallion Classic (1. Klasik Madalyon)
        c_med, _ = self.generate_medallion_classic()
        p1 = output_dir / "carpet_class_medallion_classic.png"
        _safe_imwrite(p1, c_med)
        _safe_imwrite(output_dir / "carpet_001.png", c_med)
        paths["MEDALLION_CLASSIC"] = p1

        # 2. Floral Traditional (2. Çiçek Desenli)
        c_flo, _ = self.generate_floral_traditional()
        p3 = output_dir / "carpet_class_floral_traditional.png"
        _safe_imwrite(p3, c_flo)
        _safe_imwrite(output_dir / "carpet_002.png", c_flo)
        paths["FLORAL_TRADITIONAL"] = p3

        # 3. Geometric Modern (3. Geometrik)
        c_geo, _ = self.generate_geometric_modern()
        p2 = output_dir / "carpet_class_geometric_modern.png"
        _safe_imwrite(p2, c_geo)
        _safe_imwrite(output_dir / "carpet_003.png", c_geo)
        paths["GEOMETRIC_MODERN"] = p2

        # 4. Vintage Distressed (4. Modern / Eskitme)
        c_vin, _ = self.generate_vintage_distressed()
        p4 = output_dir / "carpet_class_vintage_distressed.png"
        _safe_imwrite(p4, c_vin)
        _safe_imwrite(output_dir / "carpet_004.png", c_vin)
        paths["VINTAGE_DISTRESSED"] = p4

        return paths
