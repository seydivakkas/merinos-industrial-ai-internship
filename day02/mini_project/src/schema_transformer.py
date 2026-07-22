"""Day 02 - Schema Transformer and Relational Integrity Validator.

Converts structured tabular records and related media assets into
hierarchical semi-structured JSON documents with referential integrity checks.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from day02.mini_project.src.models import (
    ProductCompositeCatalog,
    ProductTabularRecord,
    ProductVisualRelationship,
    VisualAssetMetadata,
)

logger = logging.getLogger("Day02_SchemaTransformer")


class SchemaTransformer:
    """Manages transformations between flat tabular rows, relations, and composite JSON catalogs."""

    def __init__(self) -> None:
        self.products: Dict[str, ProductTabularRecord] = {}
        self.assets: Dict[str, VisualAssetMetadata] = {}
        self.relations: Dict[str, ProductVisualRelationship] = {}

    def add_product(self, product: ProductTabularRecord) -> None:
        self.products[product.product_id] = product

    def add_asset(self, asset: VisualAssetMetadata) -> None:
        self.assets[asset.image_id] = asset

    def link_product_to_images(self, product_id: str, image_ids: List[str]) -> None:
        self.relations[product_id] = ProductVisualRelationship(
            product_id=product_id,
            image_ids=image_ids
        )

    def validate_referential_integrity(self) -> Tuple[bool, List[str]]:
        """Verifies that all linked product and image identifiers exist."""
        errors: List[str] = []
        for pid, rel in self.relations.items():
            if pid not in self.products:
                errors.append(f"Referenced product_id '{pid}' does not exist in product catalog.")
            for iid in rel.image_ids:
                if iid not in self.assets:
                    errors.append(f"Referenced image_id '{iid}' for product '{pid}' not found in assets.")
        return len(errors) == 0, errors

    def build_composite_catalog(self, product_id: str) -> ProductCompositeCatalog:
        """Transforms relational entities into a composite hierarchical JSON model."""
        if product_id not in self.products:
            raise KeyError(f"Product {product_id} not found in catalog.")

        prod = self.products[product_id]
        rel = self.relations.get(product_id)
        linked_images = []
        if rel:
            for iid in rel.image_ids:
                if iid in self.assets:
                    linked_images.append(self.assets[iid])

        return ProductCompositeCatalog(
            product_id=prod.product_id,
            title=prod.title,
            collection=prod.collection,
            dimensions={"width_cm": prod.width_cm, "length_cm": prod.length_cm},
            primary_color=prod.primary_color,
            visual_assets=linked_images,
            tags=[prod.collection.lower(), f"{prod.width_cm}x{prod.length_cm}"],
        )

    def export_all_to_json(self, output_path: Path) -> None:
        """Exports all composite documents to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        catalogs = [self.build_composite_catalog(pid).model_dump() for pid in self.products]
        output_path.write_text(json.dumps(catalogs, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Exported {len(catalogs)} composite catalog entries to {output_path}")
