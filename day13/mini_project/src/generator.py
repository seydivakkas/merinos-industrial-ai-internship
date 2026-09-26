"""
generator.py - Combined Synthetic Generator for Day 13 (Morphology, Edge, Line, Defects).

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from .border_generator import CarpetBorderFixtureGenerator, _safe_imread, _safe_imwrite
from .defect_generator import (
    create_woven_fabric_texture,
    inject_hole,
    inject_yarn_break,
    inject_slub_knot,
    inject_oil_stain,
    generate_all_synthetic_defect_fixtures,
)

__all__ = [
    "CarpetBorderFixtureGenerator",
    "create_woven_fabric_texture",
    "inject_hole",
    "inject_yarn_break",
    "inject_slub_knot",
    "inject_oil_stain",
    "generate_all_synthetic_defect_fixtures",
    "_safe_imread",
    "_safe_imwrite",
]
