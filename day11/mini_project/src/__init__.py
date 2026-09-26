"""Day 11 - K-Means ile Baskın Renk ve Palet Çıkarımı Paketi.

Renk Kuantizasyonu, Baskın Renk Paleti Çıkarımı, CIEDE2000 Hata Haritası ve
Merinos Tezgâh Cağlık Bobin Eşleştirme Motoru.
"""

from day11.mini_project.src.ciede2000 import (
    bgr_to_cielab_float,
    cielab_to_bgr_uint8,
    ciede2000_error_map,
    ciede2000_scalar,
    ciede2000_vectorized,
)
from day11.mini_project.src.color_models import (
    CatalogYarn,
    CreelAllocationPlan,
    ExtractedColor,
    MatchGrade,
    PaletteExtractionResult,
    QuantizationReport,
    YarnMatchResult,
)
from day11.mini_project.src.generator import (
    create_all_synthetic_fixtures,
    generate_modern_geometric_carpet,
    generate_monochrome_textured_carpet,
    generate_oriental_classic_carpet,
)
from day11.mini_project.src.kmeans_palette import KMeansPaletteExtractor
from day11.mini_project.src.kmeans_palette_engine import (
    ColorCluster,
    DominantPaletteResult,
    KMeansPaletteExtractor as SimpleKMeansPaletteExtractor,
)
from day11.mini_project.src.quantizer import CarpetQuantizer
from day11.mini_project.src.yarn_matcher import YarnMatcher

__all__ = [
    "KMeansPaletteExtractor",
    "SimpleKMeansPaletteExtractor",
    "CarpetQuantizer",
    "YarnMatcher",
    "ColorCluster",
    "DominantPaletteResult",
    "CatalogYarn",
    "ExtractedColor",
    "MatchGrade",
    "PaletteExtractionResult",
    "YarnMatchResult",
    "CreelAllocationPlan",
    "QuantizationReport",
    "ciede2000_scalar",
    "ciede2000_vectorized",
    "ciede2000_error_map",
    "bgr_to_cielab_float",
    "cielab_to_bgr_uint8",
    "generate_oriental_classic_carpet",
    "generate_modern_geometric_carpet",
    "generate_monochrome_textured_carpet",
    "create_all_synthetic_fixtures",
]
