"""
generator.py - Synthetic Perspective-Distorted Carpet Fixture Generator.
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


def create_flat_carpet_patch(width: int = 400, height: int = 600) -> np.ndarray:
    """Create a crisp, high-contrast rectangular carpet pattern (400x600)."""
    carpet = np.zeros((height, width, 3), dtype=np.uint8)

    # Base field: Silk Cream (BGR)
    carpet[:] = (233, 243, 246)

    c_navy = (72, 38, 24)
    c_red = (45, 28, 152)
    c_gold = (52, 156, 198)

    # Outer border (Navy)
    border_w = 32
    cv2.rectangle(carpet, (0, 0), (width - 1, height - 1), c_navy, border_w)

    # Secondary inner border (Red)
    cv2.rectangle(carpet, (border_w, border_w), (width - border_w - 1, height - border_w - 1), c_red, 12)

    # Thin Gold guard stripe
    g_offset = border_w + 12
    cv2.rectangle(carpet, (g_offset, g_offset), (width - g_offset - 1, height - g_offset - 1), c_gold, 4)

    # Central Medallion (Ellipse & concentric rings)
    cx, cy = width // 2, height // 2
    cv2.ellipse(carpet, (cx, cy), (100, 150), 0, 0, 360, c_navy, -1)
    cv2.ellipse(carpet, (cx, cy), (80, 120), 0, 0, 360, c_red, -1)
    cv2.ellipse(carpet, (cx, cy), (60, 90), 0, 0, 360, c_gold, -1)
    cv2.ellipse(carpet, (cx, cy), (35, 55), 0, 0, 360, c_navy, -1)

    # Corner spandrels
    c_r = 60
    c_off = border_w + 16
    cv2.circle(carpet, (c_off, c_off), c_r, c_navy, -1)
    cv2.circle(carpet, (width - c_off, c_off), c_r, c_navy, -1)
    cv2.circle(carpet, (c_off, height - c_off), c_r, c_navy, -1)
    cv2.circle(carpet, (width - c_off, height - c_off), c_r, c_navy, -1)

    return carpet


def apply_synthetic_homography(
    carpet: np.ndarray,
    canvas_size: Tuple[int, int],
    src_corners: np.ndarray,
    dst_corners: np.ndarray,
    bg_color: Tuple[int, int, int] = (20, 20, 22),
) -> Tuple[np.ndarray, np.ndarray]:
    """Warp carpet onto a background canvas using perspective transformation."""
    cw, ch = canvas_size
    canvas = np.zeros((ch, cw, 3), dtype=np.uint8)
    canvas[:] = bg_color

    # Add subtle concrete / conveyor belt texture to background
    rng = np.random.default_rng(42)
    noise = rng.integers(-5, 6, size=(ch, cw, 3), dtype=np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    H = cv2.getPerspectiveTransform(src_corners.astype(np.float32), dst_corners.astype(np.float32))

    # Warp carpet with black border
    warped_carpet = cv2.warpPerspective(carpet, H, (cw, ch), flags=cv2.INTER_LINEAR)

    # Create mask of warped carpet
    mask = cv2.warpPerspective(
        np.ones(carpet.shape[:2], dtype=np.uint8) * 255,
        H,
        (cw, ch),
        flags=cv2.INTER_NEAREST,
    )

    # Blend onto background
    inv_mask = cv2.bitwise_not(mask)
    bg_part = cv2.bitwise_and(canvas, canvas, mask=inv_mask)
    fg_part = cv2.bitwise_and(warped_carpet, warped_carpet, mask=mask)
    composite = cv2.add(bg_part, fg_part)

    return composite, dst_corners


def generate_all_synthetic_rectification_fixtures(output_dir: Path) -> Dict[str, str]:
    """Generate 3 perspective-distorted carpet fixtures: 25 deg, 35 deg, 45 deg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    carpet = create_flat_carpet_patch(width=400, height=600)
    h_c, w_c = carpet.shape[:2]
    src_quad = np.array([[0, 0], [w_c - 1, 0], [w_c - 1, h_c - 1], [0, h_c - 1]], dtype=np.float32)

    canvas_w, canvas_h = 700, 700

    # 1. 25 deg moderate oblique pitch
    dst_25 = np.array([
        [150.0, 100.0],  # TL
        [550.0, 120.0],  # TR
        [590.0, 620.0],  # BR
        [90.0,  590.0],  # BL
    ], dtype=np.float32)
    img_25, _ = apply_synthetic_homography(
        carpet, (canvas_w, canvas_h), src_quad, dst_25, bg_color=(20, 20, 24)
    )
    p_25 = output_dir / "carpet_skewed_oblique_25deg.png"
    _safe_imwrite(p_25, img_25)

    # 2. 35 deg conveyor perspective
    dst_35 = np.array([
        [200.0, 80.0],   # TL (converging)
        [500.0, 85.0],   # TR (converging)
        [620.0, 640.0],  # BR (wide foreground)
        [70.0,  630.0],  # BL (wide foreground)
    ], dtype=np.float32)
    img_35, _ = apply_synthetic_homography(
        carpet, (canvas_w, canvas_h), src_quad, dst_35, bg_color=(18, 18, 22)
    )
    p_35 = output_dir / "carpet_skewed_conveyor_35deg.png"
    _safe_imwrite(p_35, img_35)

    # 3. 45 deg severe keystone angle
    dst_45 = np.array([
        [240.0, 90.0],   # TL
        [470.0, 110.0],  # TR
        [640.0, 610.0],  # BR
        [50.0,  580.0],  # BL
    ], dtype=np.float32)
    img_45, _ = apply_synthetic_homography(
        carpet, (canvas_w, canvas_h), src_quad, dst_45, bg_color=(16, 16, 20)
    )
    p_45 = output_dir / "carpet_skewed_severe_45deg.png"
    _safe_imwrite(p_45, img_45)

    return {
        "oblique_25deg": str(p_25),
        "conveyor_35deg": str(p_35),
        "severe_45deg": str(p_45),
    }
