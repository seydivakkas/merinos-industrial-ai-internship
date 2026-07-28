"""Synthetic Carpet Image Generator for Day 07 Image Analytics Toolkit.

Generates realistic textile patterns with borders, medallions, noise,
and illumination artifacts to benchmark filters, color spaces, and CLAHE.
"""

from pathlib import Path
import cv2
import numpy as np


class SyntheticCarpetGenerator:
    """Generates synthetic carpet imagery with controllable artifacts."""

    def __init__(self, height: int = 360, width: int = 480, seed: int = 42):
        self.height = height
        self.width = width
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_base_carpet(self) -> np.ndarray:
        """Generates a standard BGR carpet pattern with border and central medallion."""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Base background: deep royal navy / burgundy weave
        # BGR: Navy blue base [110, 45, 25]
        img[:, :] = [110, 45, 25]

        # Inner field: Cream / beige [180, 215, 235]
        b_margin = 35
        img[b_margin : self.height - b_margin, b_margin : self.width - b_margin] = [180, 215, 235]

        # Outer border line: Gold [45, 175, 215]
        cv2.rectangle(img, (15, 15), (self.width - 15, self.height - 15), (45, 175, 215), 4)
        cv2.rectangle(
            img,
            (b_margin, b_margin),
            (self.width - b_margin, self.height - b_margin),
            (40, 40, 140),
            3,
        )

        # Central Medallion
        c_x, c_y = self.width // 2, self.height // 2
        # Outer ellipse
        cv2.ellipse(img, (c_x, c_y), (90, 65), 0, 0, 360, (40, 40, 140), -1)
        # Inner ellipse
        cv2.ellipse(img, (c_x, c_y), (70, 50), 0, 0, 360, (45, 175, 215), -1)
        # Core flower
        cv2.circle(img, (c_x, c_y), 25, (180, 215, 235), -1)
        cv2.circle(img, (c_x, c_y), 10, (40, 40, 140), -1)

        # Micro weave texture (subtle yarn pattern)
        y_grid, x_grid = np.ogrid[: self.height, : self.width]
        weave = ((np.sin(x_grid * 0.5) * np.cos(y_grid * 0.5) + 1.0) * 10).astype(np.int16)
        img_int = img.astype(np.int16)
        img_int[:, :, 0] = np.clip(img_int[:, :, 0] + weave, 0, 255)
        img_int[:, :, 1] = np.clip(img_int[:, :, 1] + weave, 0, 255)
        img_int[:, :, 2] = np.clip(img_int[:, :, 2] + weave, 0, 255)

        return img_int.astype(np.uint8)

    def generate_low_contrast(self, base_img: np.ndarray) -> np.ndarray:
        """Generates a washed-out, underexposed carpet image with squashed dynamic range."""
        # Scale into narrow intensity band [40, 110]
        f_img = base_img.astype(np.float32) / 255.0
        squashed = f_img * 70.0 + 40.0
        return np.clip(squashed, 0, 255).astype(np.uint8)

    def generate_noisy_carpet(self, base_img: np.ndarray) -> np.ndarray:
        """Adds salt & pepper noise and Gaussian sensor noise to simulate loom debris and sensor gain."""
        noisy = base_img.copy()

        # Gaussian noise
        gauss = self.rng.normal(0, 12, base_img.shape).astype(np.float32)
        noisy = np.clip(noisy.astype(np.float32) + gauss, 0, 255).astype(np.uint8)

        # Salt & Pepper noise (optical dust / yarn fly)
        num_sp = int(self.height * self.width * 0.015)
        # Salt
        y_coords = self.rng.integers(0, self.height, num_sp)
        x_coords = self.rng.integers(0, self.width, num_sp)
        noisy[y_coords, x_coords] = [255, 255, 255]
        # Pepper
        y_coords = self.rng.integers(0, self.height, num_sp)
        x_coords = self.rng.integers(0, self.width, num_sp)
        noisy[y_coords, x_coords] = [0, 0, 0]

        return noisy

    def generate_uneven_illumination(self, base_img: np.ndarray) -> np.ndarray:
        """Simulates non-uniform loom lighting (bright center-left, dark vignette at edges)."""
        x = np.linspace(-1.0, 1.0, self.width)
        y = np.linspace(-1.0, 1.0, self.height)
        xx, yy = np.meshgrid(x, y)

        # Gradient mask centered at (-0.3, -0.2)
        dist = np.sqrt((xx + 0.3) ** 2 + (yy + 0.2) ** 2)
        illum_mask = np.clip(1.4 - 0.9 * dist, 0.25, 1.3)
        illum_mask = np.expand_dims(illum_mask, axis=-1)

        result = base_img.astype(np.float32) * illum_mask
        return np.clip(result, 0, 255).astype(np.uint8)

    def create_fixture_suite(self, output_dir: Path) -> dict[str, Path]:
        """Creates and saves the full set of synthetic carpet test images using Unicode-safe encoding."""
        output_dir.mkdir(parents=True, exist_ok=True)

        base = self.generate_base_carpet()
        low_con = self.generate_low_contrast(base)
        noisy = self.generate_noisy_carpet(base)
        uneven = self.generate_uneven_illumination(base)

        files = {
            "carpet_normal": output_dir / "carpet_normal.png",
            "carpet_low_contrast": output_dir / "carpet_low_contrast.png",
            "carpet_noisy": output_dir / "carpet_noisy.png",
            "carpet_uneven_illumination": output_dir / "carpet_uneven_illumination.png",
        }

        for key, path in files.items():
            img_to_save = {
                "carpet_normal": base,
                "carpet_low_contrast": low_con,
                "carpet_noisy": noisy,
                "carpet_uneven_illumination": uneven,
            }[key]

            # Unicode-safe write using cv2.imencode + tofile
            is_success, buffer = cv2.imencode(".png", img_to_save)
            if is_success:
                with open(path, "wb") as f:
                    f.write(buffer)

        return files


if __name__ == "__main__":
    fixtures_path = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    generator = SyntheticCarpetGenerator()
    created = generator.create_fixture_suite(fixtures_path)
    print(f"Created {len(created)} fixture images in {fixtures_path}")
