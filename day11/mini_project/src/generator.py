"""generator.py - Synthetic Multi-Colored Carpet Generator for Day 11 Palette Fixtures."""

from pathlib import Path
import cv2
import numpy as np


def generate_oriental_classic_carpet(size: int = 512) -> np.ndarray:
    """Generate 6-color intricate oriental medallion carpet fixture.

    Colors:
    - Field: Silk Cream [246, 243, 233]
    - Medallion Main: Imperial Ruby Red [152, 28, 45]
    - Medallion Center & Corner: Royal Navy [24, 38, 72]
    - Inner Fill / Arabesque: Antique Gold [198, 156, 52]
    - Floral Accent 1: Olive Grove [88, 102, 56]
    - Floral Accent 2: Anatolian Terracotta [184, 84, 54]
    """
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    # 1. Base Field (Silk Cream - BGR)
    c_cream = (233, 243, 246)
    canvas[:] = c_cream

    c_navy = (72, 38, 24)
    c_red = (45, 28, 152)
    c_gold = (52, 156, 198)
    c_olive = (56, 102, 88)
    c_terracotta = (54, 84, 184)

    # 2. Main Outer Border (Royal Navy)
    cv2.rectangle(canvas, (0, 0), (size - 1, size - 1), c_navy, thickness=40)

    # 3. Inner Secondary Border (Imperial Red)
    cv2.rectangle(canvas, (40, 40), (size - 41, size - 41), c_red, thickness=16)

    # 4. Gold Guard Line
    cv2.rectangle(canvas, (56, 56), (size - 57, size - 57), c_gold, thickness=6)

    # 5. Corner Medallions (Royal Navy & Terracotta)
    center = size // 2
    r_corner = 70
    corners = [(60, 60), (size - 60, 60), (60, size - 60), (size - 60, size - 60)]
    for pt in corners:
        cv2.circle(canvas, pt, r_corner, c_navy, -1)
        cv2.circle(canvas, pt, r_corner - 20, c_terracotta, -1)
        cv2.circle(canvas, pt, r_corner - 40, c_gold, -1)

    # 6. Central Medallion (Star / Diamond / Circles)
    cv2.circle(canvas, (center, center), 120, c_navy, -1)
    cv2.circle(canvas, (center, center), 105, c_red, -1)
    cv2.circle(canvas, (center, center), 85, c_gold, -1)
    cv2.circle(canvas, (center, center), 65, c_olive, -1)
    cv2.circle(canvas, (center, center), 45, c_terracotta, -1)
    cv2.circle(canvas, (center, center), 25, c_navy, -1)

    # 7. Floral / Arabesque Sprigs in Field
    offsets = [
        (center - 130, center - 80), (center + 130, center - 80),
        (center - 130, center + 80), (center + 130, center + 80),
        (center, center - 150), (center, center + 150),
    ]
    for pt in offsets:
        cv2.circle(canvas, pt, 18, c_olive, -1)
        cv2.circle(canvas, pt, 10, c_gold, -1)

    # Add subtle textile noise
    rng = np.random.default_rng(42)
    noise = rng.integers(-4, 5, size=(size, size, 3), dtype=np.int16)
    noisy_carpet = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return noisy_carpet


def generate_modern_geometric_carpet(size: int = 512) -> np.ndarray:
    """Generate 5-color Bauhaus / Scandinavian geometric carpet fixture.

    Colors:
    - Charcoal Black [32, 34, 38]
    - Mustard Sun [215, 172, 48]
    - Slate Blue [76, 108, 138]
    - Ivory Bone [232, 226, 212]
    - Sage Mist [134, 154, 138]
    """
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    c_ivory = (212, 226, 232)      # BGR
    c_charcoal = (38, 34, 32)
    c_mustard = (48, 172, 215)
    c_slate = (138, 108, 76)
    c_sage = (138, 154, 134)

    # Base background: Ivory
    canvas[:] = c_ivory

    # Half diagonal color block (Sage)
    pts_triangle = np.array([[0, 0], [size, 0], [0, size]], dtype=np.int32)
    cv2.fillPoly(canvas, [pts_triangle], c_sage)

    # Large overlapping circle (Mustard Sun)
    cv2.circle(canvas, (size // 3, size // 2), 140, c_mustard, -1)

    # Overlapping rectangle (Slate Blue)
    cv2.rectangle(canvas, (size // 2 - 40, size // 4), (size - 50, 3 * size // 4), c_slate, -1)

    # Charcoal Black bold geometric accent arcs and lines
    cv2.ellipse(canvas, (size // 2 + 50, size // 2 + 50), (120, 80), 45, 0, 180, c_charcoal, 24)
    cv2.line(canvas, (40, size - 60), (size - 40, size - 60), c_charcoal, 12)

    # Secondary Charcoal circle
    cv2.circle(canvas, (3 * size // 4, size // 4 + 20), 40, c_charcoal, -1)

    # Small ivory cutout inside charcoal circle
    cv2.circle(canvas, (3 * size // 4, size // 4 + 20), 16, c_ivory, -1)

    # Add subtle textile noise
    rng = np.random.default_rng(99)
    noise = rng.integers(-3, 4, size=(size, size, 3), dtype=np.int16)
    return np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def generate_monochrome_textured_carpet(size: int = 512) -> np.ndarray:
    """Generate 4-color textured beige/taupe tone-on-tone carpet fixture.

    Colors:
    - Warm Taupe [148, 132, 120]
    - Silver Ash [188, 192, 196]
    - Ivory Bone [232, 226, 212]
    - Charcoal Black [32, 34, 38]
    """
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    c_ivory = (212, 226, 232)
    c_ash = (196, 192, 188)
    c_taupe = (120, 132, 148)
    c_charcoal = (38, 34, 32)

    # Base: Warm Taupe
    canvas[:] = c_taupe

    # Striped / woven texture bands
    band_h = 32
    for y in range(0, size, band_h * 2):
        canvas[y:y + band_h, :] = c_ash

    # Overlay large soft textured organic wave (Ivory)
    pts = []
    for x in range(0, size, 20):
        y = int(size // 2 + 80 * np.sin(2 * np.pi * x / size))
        pts.append([x, y])
    pts.append([size, size])
    pts.append([0, size])
    cv2.fillPoly(canvas, [np.array(pts, dtype=np.int32)], c_ivory)

    # Fine cross-hatch grid (Charcoal thin lines)
    for x in range(64, size, 64):
        cv2.line(canvas, (x, 0), (x, size), c_charcoal, 2)

    # Subtle pile loop microtexture
    rng = np.random.default_rng(123)
    noise = rng.integers(-6, 7, size=(size, size, 3), dtype=np.int16)
    return np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def _safe_imwrite(path: Path, img: np.ndarray) -> None:
    """Safely write image on Windows when path contains non-ASCII characters."""
    path.parent.mkdir(parents=True, exist_ok=True)
    success, enc = cv2.imencode(".png", img)
    if not success:
        raise RuntimeError(f"Failed to encode image for {path}")
    enc.tofile(str(path))


def create_all_synthetic_fixtures(output_dir: Path) -> dict:
    """Generate all 3 benchmark fixtures and save them to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)

    c1 = generate_oriental_classic_carpet(512)
    p1 = output_dir / "carpet_oriental_classic.png"
    _safe_imwrite(p1, c1)

    c2 = generate_modern_geometric_carpet(512)
    p2 = output_dir / "carpet_modern_geometric.png"
    _safe_imwrite(p2, c2)

    c3 = generate_monochrome_textured_carpet(512)
    p3 = output_dir / "carpet_monochrome_textured.png"
    _safe_imwrite(p3, c3)

    return {
        "oriental_classic": str(p1),
        "modern_geometric": str(p2),
        "monochrome_textured": str(p3),
    }
