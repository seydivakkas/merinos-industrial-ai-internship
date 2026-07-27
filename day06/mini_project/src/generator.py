"""
Merinos Industrial AI Internship - Day 06
generator.py: Synthetic Carpet Embedding & Manufacturing Feature Generator
"""

from pathlib import Path
from typing import Dict, List, Tuple, Union
import numpy as np


class CarpetEmbeddingGenerator:
    """Generates synthetic high-dimensional carpet feature embeddings and raw manufacturing vectors."""

    COLLECTIONS = ["Prestij", "Usak", "Elegance", "Vintage", "ModernLine"]

    @classmethod
    def generate_embeddings_and_features(
        cls,
        n_samples: int = 100,
        seed: int = 42,
    ) -> Dict[str, Union[np.ndarray, List[str]]]:
        rng = np.random.default_rng(seed)
        samples_per_col = n_samples // len(cls.COLLECTIONS)

        product_ids = [f"MRP-{1000 + i + 1}" for i in range(n_samples)]
        collections = []
        for col_name in cls.COLLECTIONS:
            collections.extend([col_name] * samples_per_col)
        # Handle remainder if any
        while len(collections) < n_samples:
            collections.append(cls.COLLECTIONS[-1])

        # 1. 32-D and 128-D Embeddings with clustered collection distributions
        centers_32d = rng.standard_normal((len(cls.COLLECTIONS), 32)) * 2.0
        centers_128d = rng.standard_normal((len(cls.COLLECTIONS), 128)) * 2.0

        embeds_32d = np.zeros((n_samples, 32), dtype=np.float32)
        embeds_128d = np.zeros((n_samples, 128), dtype=np.float32)

        for i in range(n_samples):
            col_idx = cls.COLLECTIONS.index(collections[i])
            embeds_32d[i] = centers_32d[col_idx] + rng.normal(0, 0.4, size=32)
            embeds_128d[i] = centers_128d[col_idx] + rng.normal(0, 0.4, size=128)

        # 2. Raw Manufacturing Features with drastically different scales
        # Col 0: pile_height_mm [8.0, 16.0]
        # Col 1: knot_count_total [300000, 900000]
        # Col 2: weight_gsm [1500, 3800]
        # Col 3: warp_tension_n [25, 65]
        pile_height = rng.uniform(8.0, 16.0, size=(n_samples, 1))
        knot_count = rng.uniform(300000.0, 900000.0, size=(n_samples, 1))
        weight_gsm = 1200.0 + (knot_count / 350.0) + rng.uniform(-100, 100, size=(n_samples, 1))
        warp_tension = rng.uniform(25.0, 65.0, size=(n_samples, 1))

        raw_features = np.hstack([pile_height, knot_count, weight_gsm, warp_tension]).astype(np.float32)

        return {
            "product_ids": product_ids,
            "collections": collections,
            "embeddings_32d": embeds_32d,
            "embeddings_128d": embeds_128d,
            "raw_manufacturing_features": raw_features,
        }

    @classmethod
    def save_fixtures(cls, output_path: Union[str, Path]) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = cls.generate_embeddings_and_features()

        np.savez_compressed(
            path,
            product_ids=np.array(data["product_ids"]),
            collections=np.array(data["collections"]),
            embeddings_32d=data["embeddings_32d"],
            embeddings_128d=data["embeddings_128d"],
            raw_manufacturing_features=data["raw_manufacturing_features"],
        )
        return path


if __name__ == "__main__":
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
    fixture_file = fixtures_dir / "carpet_feature_embeddings.npz"
    CarpetEmbeddingGenerator.save_fixtures(fixture_file)
    print(f"Carpet feature fixtures saved successfully at: {fixture_file}")
