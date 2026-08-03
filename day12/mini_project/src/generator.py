"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 12
Sentetik Halı Bordür Fikstür Üretici (CarpetBorderFixtureGenerator)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, Tuple
import cv2
import numpy as np


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


class CarpetBorderFixtureGenerator:
    """Endüstriyel bordür analizi ve kalite testleri için sentetik jakarlı halı fikstürleri üretir."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def generate_base_carpet(
        self,
        width: int = 800,
        height: int = 800,
        bg_color: Tuple[int, int, int] = (195, 210, 220),  # Bej/Krem (BGR)
    ) -> np.ndarray:
        """Jakarlı doku ve madalyon desenli temel halı zemini oluşturur."""
        carpet = np.full((height, width, 3), bg_color, dtype=np.uint8)

        # 1. Periyodik jakarlı atkı ve çözgü dokusu
        y_grid, x_grid = np.ogrid[:height, :width]
        weave = ((x_grid % 4 == 0) | (y_grid % 4 == 0)).astype(np.uint8) * 15
        carpet = cv2.subtract(carpet, cv2.merge([weave, weave, weave]))

        # 2. İç Madalyon ve Geometrik Desen
        center = (width // 2, height // 2)
        cv2.circle(carpet, center, 140, (30, 40, 140), -1)  # Kırmızı madalyon
        cv2.circle(carpet, center, 110, (140, 60, 30), -1)  # Lacivert iç daire
        cv2.circle(carpet, center, 80, (40, 160, 220), -1)  # Altın sarısı göbek
        cv2.circle(carpet, center, 30, (220, 220, 230), -1)  # Krem çiçek

        # Hafif Gauss gürültüsü
        noise = self.rng.normal(0, 3, carpet.shape).astype(np.int16)
        carpet = np.clip(carpet.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        return carpet

    def generate_clean_parallel_carpet(
        self,
        width: int = 800,
        height: int = 800,
        margin: int = 60,
        border_thickness: int = 16,
    ) -> np.ndarray:
        """Kusursuz paralel kenarlara sahip 1. kalite referans Merinos halısı üretir."""
        carpet = self.generate_base_carpet(width, height)

        # Dış Koyu Lacivert Bordür Çerçevesi
        x1, y1 = margin, margin
        x2, y2 = width - margin, height - margin

        # Kalın dış bordür çizgisi (Lacivert: 130, 50, 25 BGR)
        cv2.rectangle(carpet, (x1, y1), (x2, y2), (130, 50, 25), border_thickness)

        # İnce iç altın bordür çizgisi (Altın: 30, 180, 220 BGR)
        in_margin = margin + border_thickness + 10
        cv2.rectangle(carpet, (in_margin, in_margin), (width - in_margin, height - in_margin), (30, 180, 220), 4)

        return carpet

    def generate_skewed_angular_carpet(
        self,
        width: int = 800,
        height: int = 800,
        margin: int = 60,
        border_thickness: int = 16,
        skew_angle_deg: float = 1.85,
    ) -> np.ndarray:
        """Alt bordürün açılı eğrildiği (dokuma çekme/gerginlik hatası) halı üretir."""
        carpet = self.generate_base_carpet(width, height)

        x1, y1 = margin, margin
        x2, y2 = width - margin, height - margin

        # Üst, Sol ve Sağ bordürler düzgün
        # Üst bordür (y1 sabit)
        cv2.line(carpet, (x1, y1), (x2, y1), (130, 50, 25), border_thickness, cv2.LINE_AA)
        # Sol bordür
        cv2.line(carpet, (x1, y1), (x1, y2), (130, 50, 25), border_thickness, cv2.LINE_AA)
        # Sağ bordür
        cv2.line(carpet, (x2, y1), (x2, y2), (130, 50, 25), border_thickness, cv2.LINE_AA)

        # Alt bordür: skew_angle_deg açısıyla eğik çizilir
        # dy = tan(theta) * dx
        rad = np.deg2rad(skew_angle_deg)
        dy = int(round(np.tan(rad) * (x2 - x1)))
        y2_skewed = y2 + dy

        cv2.line(carpet, (x1, y2), (x2, y2_skewed), (130, 50, 25), border_thickness, cv2.LINE_AA)

        # İnce iç bordür de benzer şekilde alt kenarda eğrilir
        in_m = margin + border_thickness + 10
        cv2.line(carpet, (in_m, in_m), (width - in_m, in_m), (30, 180, 220), 4, cv2.LINE_AA)
        cv2.line(carpet, (in_m, in_m), (in_m, height - in_m), (30, 180, 220), 4, cv2.LINE_AA)
        cv2.line(carpet, (width - in_m, in_m), (width - in_m, height - in_m), (30, 180, 220), 4, cv2.LINE_AA)
        cv2.line(carpet, (in_m, height - in_m), (width - in_m, height - in_m + dy), (30, 180, 220), 4, cv2.LINE_AA)

        return carpet

    def generate_wavy_carpet(
        self,
        width: int = 800,
        height: int = 800,
        margin: int = 60,
        wave_amplitude: float = 6.0,
        wave_cycles: int = 3,
    ) -> np.ndarray:
        """Alt bordürde dalgalanma (overlok büzülmesi / wavy distortion) olan halı üretir."""
        carpet = self.generate_clean_parallel_carpet(width, height, margin=margin)

        # Alt bordür bölgesini sinüzoidal dalgayla modifiye et
        xs = np.arange(margin, width - margin)
        # y = y_base + A * sin(2*pi * f * x / L)
        y_base = height - margin
        ys = y_base + wave_amplitude * np.sin(2.0 * np.pi * wave_cycles * (xs - margin) / (width - 2 * margin))

        # Orijinal düz alt bordürü arka plan rengiyle kapatıp dalgalı bordürü çiz
        cv2.line(carpet, (margin - 5, y_base), (width - margin + 5, y_base), (195, 210, 220), 22)

        pts = np.column_stack((xs, ys.astype(np.int32)))
        cv2.polylines(carpet, [pts], False, (130, 50, 25), 16, cv2.LINE_AA)

        return carpet

    def generate_broken_border_carpet(
        self,
        width: int = 800,
        height: int = 800,
        margin: int = 60,
        gap_start_x: int = 350,
        gap_size: int = 80,
    ) -> np.ndarray:
        """Bordür çizgisi üzerinde dikiş kaçığı / kesinti (broken edge) olan halı üretir."""
        carpet = self.generate_clean_parallel_carpet(width, height, margin=margin)

        # Üst bordür üzerinde bir kısmı sil (kesinti simülasyonu)
        cv2.line(
            carpet,
            (gap_start_x, margin),
            (gap_start_x + gap_size, margin),
            (195, 210, 220),
            24,
        )
        return carpet

    def generate_all_fixtures(self, output_dir: Path) -> Dict[str, Path]:
        """Tüm sentetik senaryo fikstürlerini üretir ve kaydeder."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}

        fixtures = {
            "carpet_border_clean_parallel.png": self.generate_clean_parallel_carpet(),
            "carpet_border_skewed_angular.png": self.generate_skewed_angular_carpet(skew_angle_deg=1.85),
            "carpet_border_wavy_distortion.png": self.generate_wavy_carpet(wave_amplitude=6.5),
            "carpet_border_broken_edge.png": self.generate_broken_border_carpet(gap_size=90),
        }

        for filename, img in fixtures.items():
            path = output_dir / filename
            success = _safe_imwrite(path, img)
            if success:
                paths[filename] = path

        return paths
