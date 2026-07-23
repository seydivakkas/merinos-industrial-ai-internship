"""
day03/mini_project/src/normalizer.py
Endüstriyel veriler için Pandas tabanlı temizleme, birim dönüştürme ve Pydantic model dökümü.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import ValidationError

# Ensure project root is in sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from day02.mini_project.src.models import (
    CarpetDimensions,
    CarpetProduct,
    MaterialEnum,
)


class DataNormalizer:
    """
    Heterojen üretim ve katalog verilerini tek tip endüstriyel formata dönüştüren ve
    Pydantic modelleri ile doğrulayan normalizer.
    """

    INCH_TO_CM = 2.54
    MM_TO_CM = 0.1

    MATERIAL_MAP = {
        "wool": MaterialEnum.WOOL,
        "yün": MaterialEnum.WOOL,
        "yun": MaterialEnum.WOOL,
        "acrylic": MaterialEnum.ACRYLIC,
        "akrilik": MaterialEnum.ACRYLIC,
        "polyester": MaterialEnum.POLYESTER,
        "poly": MaterialEnum.POLYESTER,
        "bamboo_silk": MaterialEnum.BAMBOO_SILK,
        "bambu_ipek": MaterialEnum.BAMBOO_SILK,
        "bambu": MaterialEnum.BAMBOO_SILK,
    }

    @classmethod
    def convert_dimension_to_cm(cls, val: Any, unit: Optional[str]) -> float:
        """Farklı ölçü birimlerini (inç, mm) cm formatına dönüştürür."""
        if val is None:
            raise ValueError("Boyut değeri boş (None) olamaz.")
        try:
            num = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Sayısal olmayan boyut değeri: '{val}'")

        if unit is None or not str(unit).strip():
            unit = "cm"

        unit_str = str(unit).strip().lower()
        if unit_str in ("inch", "inç", "in", "\""):
            return round(num * cls.INCH_TO_CM, 2)
        elif unit_str in ("mm", "milimetre"):
            return round(num * cls.MM_TO_CM, 2)
        elif unit_str in ("cm", "santimetre"):
            return round(num, 2)
        elif unit_str in ("m", "metre"):
            return round(num * 100.0, 2)
        else:
            raise ValueError(f"Desteklenmeyen ölçü birimi: '{unit}'")

    @classmethod
    def normalize_hex_color(cls, color: str) -> str:
        """Hex renk kodunu standart 7 karakterlik '#RRGGBB' biçimine dönüştürür."""
        if not color or not isinstance(color, str):
            raise ValueError(f"Geçersiz renk verisi: '{color}'")

        c = color.strip().upper()
        if not c.startswith("#"):
            c = "#" + c

        # 3 karakterlik kısa hex (#RGB -> #RRGGBB) desteği
        if len(c) == 4 and re.match(r"^#[0-9A-F]{3}$", c):
            c = f"#{c[1]*2}{c[2]*2}{c[3]*2}"

        if not re.match(r"^#[0-9A-F]{6}$", c):
            raise ValueError(f"Geçersiz hex renk şablonu: '{color}'")

        return c

    @classmethod
    def normalize_material(cls, mat_raw: Any) -> MaterialEnum:
        """Ham malzeme metnini MaterialEnum formatına dönüştürür."""
        if not mat_raw:
            return MaterialEnum.ACRYLIC

        key = str(mat_raw).strip().lower()
        if key in cls.MATERIAL_MAP:
            return cls.MATERIAL_MAP[key]

        # Doğrudan enum adı ile eşleşiyor mu kontrolü
        for e in MaterialEnum:
            if e.value.lower() == key or e.name.lower() == key:
                return e

        raise ValueError(f"Tanımlanamayan halı malzemesi: '{mat_raw}'")

    @classmethod
    def normalize_text(cls, text: Optional[str], default: str = "") -> str:
        """Boşlukları temizler ve baş harfleri standartlaştırır."""
        if not text:
            return default
        cleaned = re.sub(r"\s+", " ", str(text).strip())
        return cleaned

    def process_record(
        self,
        record: Dict[str, Any]
    ) -> Tuple[Optional[CarpetProduct], Optional[Dict[str, Any]]]:
        """
        Ham birleştirilmiş kaydı normalize eder ve Pydantic CarpetProduct modeline dönüştürür.
        Dönüş: (CarpetProduct, None) veya (None, quarantine_dict)
        """
        product_id = record.get("product_id") or record.get("product_code")
        if not product_id:
            return None, {
                "error": "Kayıtta 'product_id' veya 'product_code' alanı bulunamadı.",
                "raw_record": record
            }

        try:
            # 1. Boyut birim dönüşümleri
            unit = record.get("dimension_unit", "cm")
            raw_w = record.get("raw_width") or record.get("width_cm") or record.get("width")
            raw_l = record.get("raw_length") or record.get("length_cm") or record.get("length")
            pile = record.get("pile_height_mm") or record.get("pile_mm") or 10.0

            width_cm = self.convert_dimension_to_cm(raw_w, unit)
            length_cm = self.convert_dimension_to_cm(raw_l, unit)
            pile_height_mm = float(pile)

            dimensions = CarpetDimensions(
                width_cm=width_cm,
                length_cm=length_cm,
                pile_height_mm=pile_height_mm
            )

            # 2. Metin alanları
            name = self.normalize_text(record.get("product_name") or record.get("name"), default="Merinos Halı")
            collection = self.normalize_text(record.get("collection"), default="Klasik").title()

            # 3. Malzeme
            material = self.normalize_material(record.get("composition") or record.get("material"))

            # 4. Renk paleti normalizasyonu
            raw_palette = record.get("palette") or record.get("dominant_hex_palette") or ["#808080"]
            if isinstance(raw_palette, str):
                raw_palette = [c.strip() for c in raw_palette.split(",")]

            palette = [self.normalize_hex_color(c) for c in raw_palette]

            # 5. Pydantic Model Doğrulaması
            product = CarpetProduct(
                product_id=str(product_id).strip(),
                title=name,
                collection=collection,
                material=material,
                dimensions=dimensions,
                palette_hex=palette,
                is_active=True
            )
            return product, None

        except (ValidationError, ValueError) as e:
            return None, {
                "product_id": str(product_id),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "raw_record": record
            }
