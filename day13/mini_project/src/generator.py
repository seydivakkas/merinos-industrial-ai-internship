"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 13
Sentetik Halı ve Birebir Ground Truth Maske Üretici (CarpetSegmentationFixtureGenerator)

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
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


class CarpetSegmentationFixtureGenerator:
    """Segmentasyon test ve kıyaslaması için sentetik jakarlı halılar ve kusursuz GT maskeleri üretir."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def generate_medallion_carpet(
        self,
        width: int = 600,
        height: int = 600,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Klasik oryantal madalyon halısı, ikili motif GT maskesi ve çok sınıflı GT maskesi üretir."""
        # 1. Koyu Lacivert Zemin Kumaşı (BGR: 45, 30, 20)
        carpet = np.full((height, width, 3), (45, 30, 20), dtype=np.uint8)
        gt_motif = np.zeros((height, width), dtype=np.uint8)
        gt_multiclass = np.zeros((height, width), dtype=np.uint8)  # 0: Zemin

        # Periyodik kumaş atkı/çözgü doku paraziti
        y_grid, x_grid = np.ogrid[:height, :width]
        weave = ((x_grid % 3 == 0) | (y_grid % 3 == 0)).astype(np.uint8) * 10
        carpet = cv2.add(carpet, cv2.merge([weave, weave, weave]))

        # 2. Dış Bordür Çerçevesi (Altın ve Kırmızı şeritler)
        m_out = 35
        thick_out = 16
        cv2.rectangle(carpet, (m_out, m_out), (width - m_out, height - m_out), (30, 50, 160), thick_out)
        cv2.rectangle(gt_multiclass, (m_out, m_out), (width - m_out, height - m_out), 1, thick_out)  # 1: Bordür

        m_in = 65
        cv2.rectangle(carpet, (m_in, m_in), (width - m_in, height - m_in), (40, 160, 220), 4)
        cv2.rectangle(gt_multiclass, (m_in, m_in), (width - m_in, height - m_in), 1, 4)

        # 3. Köşe Spandrelleri (Köşe Üçgen Motifleri)
        corner_len = 110
        corners = [
            [(m_in, m_in), (m_in + corner_len, m_in), (m_in, m_in + corner_len)],  # TL
            [(width - m_in, m_in), (width - m_in - corner_len, m_in), (width - m_in, m_in + corner_len)],  # TR
            [(m_in, height - m_in), (m_in + corner_len, height - m_in), (m_in, height - m_in - corner_len)],  # BL
            [(width - m_in, height - m_in), (width - m_in - corner_len, height - m_in), (width - m_in, height - m_in - corner_len)],  # BR
        ]
        for pts in corners:
            poly = np.array(pts, dtype=np.int32)
            cv2.fillPoly(carpet, [poly], (50, 60, 180))
            cv2.fillPoly(gt_motif, [poly], 255)
            cv2.fillPoly(gt_multiclass, [poly], 2)

        # 4. Merkez Madalyon Yapısı
        center = (width // 2, height // 2)

        # Dış madalyon lobları (8 köşeli çiçekli yapı)
        cv2.circle(carpet, center, 140, (40, 70, 190), -1)  # Kırmızı taban
        cv2.circle(gt_motif, center, 140, 255, -1)
        cv2.circle(gt_multiclass, center, 140, 2, -1)

        # Lob çıkıntıları
        for angle in range(0, 360, 45):
            rad = np.deg2rad(angle)
            cx = int(center[0] + 135 * np.cos(rad))
            cy = int(center[1] + 135 * np.sin(rad))
            cv2.circle(carpet, (cx, cy), 35, (40, 70, 190), -1)
            cv2.circle(gt_motif, (cx, cy), 35, 255, -1)
            cv2.circle(gt_multiclass, (cx, cy), 35, 2, -1)

        # Madalyon içi altın çember ve krem göbek
        cv2.circle(carpet, center, 100, (40, 180, 230), -1)  # Altın halka
        cv2.circle(carpet, center, 60, (200, 215, 225), -1)  # Krem çiçek
        cv2.circle(carpet, center, 25, (30, 40, 140), -1)   # Kırmızı tohum

        # Hafif doğal gürültü ekle
        noise = self.rng.normal(0, 2.5, carpet.shape).astype(np.int16)
        carpet = np.clip(carpet.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        return carpet, gt_motif, gt_multiclass

    def generate_geometric_carpet(
        self,
        width: int = 600,
        height: int = 600,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Modern geometrik desenli halı ve GT maskesi üretir."""
        carpet = np.full((height, width, 3), (210, 210, 215), dtype=np.uint8)  # Açık gri zemin
        gt_motif = np.zeros((height, width), dtype=np.uint8)
        gt_multiclass = np.zeros((height, width), dtype=np.uint8)

        # Dış siyah bordür
        cv2.rectangle(carpet, (20, 20), (width - 20, height - 20), (30, 30, 30), 10)
        cv2.rectangle(gt_multiclass, (20, 20), (width - 20, height - 20), 1, 10)

        # Merkez büyük baklava (Diamond) motifi
        center = (width // 2, height // 2)
        r = 180
        diamond_pts = np.array([
            (center[0], center[1] - r),
            (center[0] + r, center[1]),
            (center[0], center[1] + r),
            (center[0] - r, center[1]),
        ], dtype=np.int32)

        cv2.fillPoly(carpet, [diamond_pts], (40, 50, 160))  # Kırmızı
        cv2.fillPoly(gt_motif, [diamond_pts], 255)
        cv2.fillPoly(gt_multiclass, [diamond_pts], 2)

        # İç ters baklava (Hardal sarısı)
        r_in = 100
        in_pts = np.array([
            (center[0], center[1] - r_in),
            (center[0] + r_in, center[1]),
            (center[0], center[1] + r_in),
            (center[0] - r_in, center[1]),
        ], dtype=np.int32)
        cv2.fillPoly(carpet, [in_pts], (40, 160, 210))

        return carpet, gt_motif, gt_multiclass

    def generate_all_fixtures(self, output_dir: Path) -> Dict[str, Path]:
        """Tüm sentetik halı ve GT maske fikstürlerini üretir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}

        # 1. Klasik Madalyon Halı
        c_med, gt_med, gt_multi = self.generate_medallion_carpet()
        p1 = output_dir / "carpet_medallion_classic.png"
        p2 = output_dir / "carpet_medallion_classic_gt_mask.png"
        p3 = output_dir / "carpet_medallion_classic_gt_multiclass.png"

        _safe_imwrite(p1, c_med)
        _safe_imwrite(p2, gt_med)
        _safe_imwrite(p3, gt_multi * 85)  # 0, 85, 170, 255 görselleştirilebilir
        paths["medallion_carpet"] = p1
        paths["medallion_gt"] = p2

        # 2. Modern Geometrik Halı
        c_geo, gt_geo, _ = self.generate_geometric_carpet()
        p4 = output_dir / "carpet_geometric_modern.png"
        p5 = output_dir / "carpet_geometric_modern_gt_mask.png"
        _safe_imwrite(p4, c_geo)
        _safe_imwrite(p5, gt_geo)
        paths["geometric_carpet"] = p4
        paths["geometric_gt"] = p5

        return paths
