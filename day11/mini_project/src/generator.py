"""
generator.py - Synthetic Carpet Fabric & Physical Weaving Defect Fixtures Generator.
"""

from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import cv2


def _safe_imwrite(path: Path, img: np.ndarray) -> None:
    """Safely write image on Windows when path contains non-ASCII characters."""
    success, enc = cv2.imencode(".png", img)
    if not success:
        raise RuntimeError(f"Failed to encode image for {path}")
    enc.tofile(str(path))


def create_woven_fabric_texture(
    width: int = 512,
    height: int = 512,
    base_color: Tuple[int, int, int] = (195, 205, 215),  # Light slate grey/blue (BGR)
) -> np.ndarray:
    """Generate realistic woven carpet pile texture with warp and weft yarn grid."""
    fabric = np.zeros((height, width, 3), dtype=np.uint8)
    fabric[:] = base_color

    # Yarn thread pitch (pixels between threads)
    pitch = 4
    rng = np.random.default_rng(42)

    # Weft (horizontal) thread modulation
    y_idx = np.arange(height)
    weft_mod = (np.sin(2.0 * np.pi * y_idx / pitch) * 8.0).astype(np.int16)
    fabric[:, :, 0] = np.clip(fabric[:, :, 0].astype(np.int16) + weft_mod[:, None], 0, 255).astype(np.uint8)
    fabric[:, :, 1] = np.clip(fabric[:, :, 1].astype(np.int16) + weft_mod[:, None], 0, 255).astype(np.uint8)
    fabric[:, :, 2] = np.clip(fabric[:, :, 2].astype(np.int16) + weft_mod[:, None], 0, 255).astype(np.uint8)

    # Warp (vertical) thread modulation
    x_idx = np.arange(width)
    warp_mod = (np.sin(2.0 * np.pi * x_idx / pitch) * 8.0).astype(np.int16)
    fabric[:, :, 0] = np.clip(fabric[:, :, 0].astype(np.int16) + warp_mod[None, :], 0, 255).astype(np.uint8)
    fabric[:, :, 1] = np.clip(fabric[:, :, 1].astype(np.int16) + warp_mod[None, :], 0, 255).astype(np.uint8)
    fabric[:, :, 2] = np.clip(fabric[:, :, 2].astype(np.int16) + warp_mod[None, :], 0, 255).astype(np.uint8)

    # Fiber micro-texture noise
    noise = rng.integers(-4, 5, size=(height, width, 3), dtype=np.int16)
    fabric = np.clip(fabric.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return fabric


def inject_hole(
    fabric: np.ndarray,
    cx: int,
    cy: int,
    radius: int = 9,
    darkness: Tuple[int, int, int] = (25, 25, 30),
) -> np.ndarray:
    """Inject a dark localized weaving hole or puncture into the fabric."""
    out = fabric.copy()
    cv2.circle(out, (cx, cy), radius, darkness, -1)

    # Frayed hole boundary
    rng = np.random.default_rng(cx + cy)
    for _ in range(12):
        r_angle = rng.uniform(0, 2 * np.pi)
        r_dist = radius + rng.integers(1, 4)
        px = int(cx + r_dist * np.cos(r_angle))
        py = int(cy + r_dist * np.sin(r_angle))
        if 0 <= px < fabric.shape[1] and 0 <= py < fabric.shape[0]:
            out[py, px] = darkness

    return out


def inject_yarn_break(
    fabric: np.ndarray,
    x: int,
    y: int,
    length: int = 60,
    orientation: str = "horizontal",
    thickness: int = 2,
    darkness: Tuple[int, int, int] = (40, 40, 45),
) -> np.ndarray:
    """Inject a linear missing yarn break (horizontal weft or vertical warp)."""
    out = fabric.copy()
    if orientation == "horizontal":
        pt1 = (x, y)
        pt2 = (min(fabric.shape[1] - 1, x + length), y)
    else:
        pt1 = (x, y)
        pt2 = (x, min(fabric.shape[0] - 1, y + length))

    cv2.line(out, pt1, pt2, darkness, thickness)
    return out


def inject_slub_knot(
    fabric: np.ndarray,
    cx: int,
    cy: int,
    radius: int = 9,
    brightness: Tuple[int, int, int] = (255, 255, 255),
) -> np.ndarray:
    """Inject a bright thick yarn slub or knot anomaly."""
    out = fabric.copy()
    cv2.ellipse(out, (cx, cy), (radius + 2, radius), 30, 0, 360, brightness, -1)
    return out


def inject_oil_stain(
    fabric: np.ndarray,
    cx: int,
    cy: int,
    axes: Tuple[int, int] = (16, 12),
    angle: int = 20,
    dark_tint: Tuple[int, int, int] = (45, 60, 75),
) -> np.ndarray:
    """Inject a dark/brownish industrial loom oil stain."""
    out = fabric.copy()
    # Semi-transparent blending of oil stain
    mask = np.zeros(fabric.shape[:2], dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), axes, angle, 0, 360, 255, -1)
    mask_blurred = cv2.GaussianBlur(mask, (7, 7), 2.5)

    alpha = (mask_blurred.astype(np.float32) / 255.0) * 0.75
    for c in range(3):
        out[:, :, c] = np.clip(
            fabric[:, :, c] * (1.0 - alpha) + dark_tint[c] * alpha,
            0,
            255,
        ).astype(np.uint8)

    return out


def generate_all_synthetic_defect_fixtures(output_dir: Path) -> Dict[str, str]:
    """Generate the full set of clean and defective carpet fixtures for Day 11."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base = create_woven_fabric_texture(512, 512)

    # 1. Clean Reference Fabric
    p_clean = output_dir / "carpet_clean_reference.png"
    _safe_imwrite(p_clean, base)

    # 2. Yarn Break Fixture (Weft + Warp breaks)
    img_yarn = base.copy()
    img_yarn = inject_yarn_break(img_yarn, x=100, y=180, length=70, orientation="horizontal")
    img_yarn = inject_yarn_break(img_yarn, x=350, y=280, length=65, orientation="vertical")
    p_yarn = output_dir / "carpet_defect_yarn_break.png"
    _safe_imwrite(p_yarn, img_yarn)

    # 3. Hole Puncture Fixture (Multiple weaving punctures)
    img_hole = base.copy()
    img_hole = inject_hole(img_hole, cx=150, cy=150, radius=9)
    img_hole = inject_hole(img_hole, cx=360, cy=320, radius=12)
    p_hole = output_dir / "carpet_defect_hole_puncture.png"
    _safe_imwrite(p_hole, img_hole)

    # 4. Oil Stain & Slub Knot Fixture
    img_oil_slub = base.copy()
    img_oil_slub = inject_oil_stain(img_oil_slub, cx=200, cy=220, axes=(18, 14))
    img_oil_slub = inject_slub_knot(img_oil_slub, cx=380, cy=180, radius=7)
    p_oil_slub = output_dir / "carpet_defect_oil_slub.png"
    _safe_imwrite(p_oil_slub, img_oil_slub)

    return {
        "clean_reference": str(p_clean),
        "yarn_break": str(p_yarn),
        "hole_puncture": str(p_hole),
        "oil_slub": str(p_oil_slub),
    }
