"""
yarn_matcher.py - Factory Yarn Catalog Matching & Jacquard Creel Bobbin Allocation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np

from .color_models import (
    CatalogYarn,
    ExtractedColor,
    MatchGrade,
    YarnMatchResult,
    CreelAllocationPlan,
)
from .ciede2000 import ciede2000_scalar


class YarnMatcher:
    """Matches arbitrary design colors to certified Merinos production yarn bobbins."""

    def __init__(
        self,
        catalog: Optional[List[CatalogYarn]] = None,
        config_path: Optional[Union[str, Path]] = None,
    ):
        if catalog is not None:
            self.catalog = catalog
        else:
            cfg = self._load_config(config_path)
            self.catalog = [CatalogYarn(**item) for item in cfg.get("catalog_yarns", [])]

        if not self.catalog:
            raise ValueError("Yarn catalog is empty. Please provide valid catalog items.")

        # Cache catalog LAB vectors for fast matching
        self._catalog_labs = np.array([y.cielab for y in self.catalog], dtype=np.float64)

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        """Load palette configuration JSON."""
        if config_path is None:
            default_path = Path(__file__).resolve().parent.parent / "configs" / "palette_config.json"
            config_path = default_path

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def match_color(self, extracted: ExtractedColor) -> YarnMatchResult:
        """Find the closest factory yarn bobbin for a single extracted dominant color."""
        target_lab = np.array(extracted.cielab, dtype=np.float64)

        # Compute CIEDE2000 and CIE 1976 distances against all catalog bobbins
        scored_matches = []
        for i, yarn in enumerate(self.catalog):
            dE00 = ciede2000_scalar(target_lab, yarn.cielab)
            # CIE 1976 Euclidean
            dE76 = float(np.linalg.norm(target_lab - np.array(yarn.cielab)))
            scored_matches.append({
                "yarn": yarn,
                "delta_e_00": round(dE00, 3),
                "delta_e_76": round(dE76, 3),
            })

        # Sort ascending by Delta E_00
        scored_matches.sort(key=lambda x: x["delta_e_00"])
        best = scored_matches[0]
        best_yarn: CatalogYarn = best["yarn"]
        dE00_val = best["delta_e_00"]
        dE76_val = best["delta_e_76"]

        # Determine Match Grade
        if dE00_val < 1.0:
            grade = MatchGrade.EXACT
        elif dE00_val < 2.0:
            grade = MatchGrade.ACCEPTABLE
        elif dE00_val < 4.0:
            grade = MatchGrade.WARNING
        else:
            grade = MatchGrade.OUT_OF_SPEC

        # Alternative Top-3 matches (excluding best)
        alternatives = [
            {
                "yarn_id": m["yarn"].yarn_id,
                "name": m["yarn"].name,
                "delta_e_00": m["delta_e_00"],
                "in_stock": m["yarn"].in_stock,
            }
            for m in scored_matches[1:4]
        ]

        return YarnMatchResult(
            extracted_color=extracted,
            matched_yarn=best_yarn,
            delta_e_00=dE00_val,
            delta_e_76=dE76_val,
            match_grade=grade,
            alternative_matches=alternatives,
        )

    def match_palette(self, palette: List[ExtractedColor]) -> List[YarnMatchResult]:
        """Match all colors in an extracted palette to catalog bobbins."""
        return [self.match_color(color) for color in palette]

    def generate_creel_allocation_plan(
        self,
        palette: List[ExtractedColor],
        pattern_name: str = "Carpet Pattern",
        pile_weight_kg_m2: float = 2.2,
    ) -> CreelAllocationPlan:
        """Build jacquard loom bobbin creel allocation and estimated material cost report."""
        matches = self.match_palette(palette)
        unique_yarns = {m.matched_yarn.yarn_id for m in matches}

        # Estimate weighted yarn cost per m^2
        total_cost = 0.0
        out_of_spec_count = 0

        for m in matches:
            weight_fraction = (m.extracted_color.percentage / 100.0) * pile_weight_kg_m2
            color_cost = weight_fraction * m.matched_yarn.cost_per_kg
            total_cost += color_cost
            if m.match_grade == MatchGrade.OUT_OF_SPEC:
                out_of_spec_count += 1

        return CreelAllocationPlan(
            allocation_id=f"CREEL-ALLOC-{pattern_name.replace(' ', '_').upper()}",
            pattern_name=pattern_name,
            target_creel_size=len(palette),
            active_bobbins=matches,
            unique_yarn_count=len(unique_yarns),
            total_estimated_yarn_cost_per_m2=round(total_cost, 2),
            uncatalogued_colors_count=out_of_spec_count,
        )
