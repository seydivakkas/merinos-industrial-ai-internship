"""Synthetic Carpet Palette and Dye Lot Drift Generator for Day 08."""

from pathlib import Path
import cv2
import numpy as np


class SyntheticCarpetPaletteGenerator:
    """Generates synthetic carpets with precise yarn colors and controlled dye lot drifts."""

    def __init__(self, height: int = 360, width: int = 480, seed: int = 42):
        self.height = height
        self.width = width
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_carpet(
        self,
        bgr_navy: tuple[int, int, int] = (76, 43, 26),
        bgr_cream: tuple[int, int, int] = (235, 242, 245),
        bgr_gold: tuple[int, int, int] = (55, 175, 212),
        bgr_red: tuple[int, int, int] = (0, 0, 139),
        noise_level: float = 3.0,
    ) -> np.ndarray:
        """Generates a structured 4-color carpet pattern with specified BGR yarn colors."""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # 1. Outer field: Royal Navy
        img[:, :] = bgr_navy

        # 2. Outer border: Antique Gold
        cv2.rectangle(img, (12, 12), (self.width - 12, self.height - 12), bgr_gold, 5)

        # 3. Inner field: Silk Cream
        margin = 35
        img[margin : self.height - margin, margin : self.width - margin] = bgr_cream

        # 4. Inner border: Antique Gold
        cv2.rectangle(
            img,
            (margin, margin),
            (self.width - margin, self.height - margin),
            bgr_gold,
            3,
        )

        # 5. Central Medallion: Imperial Red
        c_x, c_y = self.width // 2, self.height // 2
        cv2.ellipse(img, (c_x, c_y), (85, 60), 0, 0, 360, bgr_red, -1)
        # Inner Gold Ring inside Medallion
        cv2.ellipse(img, (c_x, c_y), (50, 35), 0, 0, 360, bgr_gold, 4)
        # Core Red Rosette
        cv2.circle(img, (c_x, c_y), 20, bgr_red, -1)
        cv2.circle(img, (c_x, c_y), 8, bgr_gold, -1)

        # Micro-texture noise (yarn weave variation)
        if noise_level > 0.0:
            noise = self.rng.normal(0, noise_level, img.shape).astype(np.float32)
            img_f = np.clip(img.astype(np.float32) + noise, 0, 255)
            img = img_f.astype(np.uint8)

        return img

    def create_fixture_suite(self, output_dir: Path) -> dict[str, Path]:
        """Creates the set of 4 benchmark fixture images."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Master Reference (Exact standard colors)
        master = self.generate_carpet()

        # 2. Lot Drift PASS (Very slight shift: Delta E ~ 1.0 - 1.5)
        drift_pass = self.generate_carpet(
            bgr_navy=(77, 44, 28),
            bgr_cream=(234, 241, 244),
            bgr_gold=(57, 177, 214),
            bgr_red=(2, 4, 142),
        )

        # 3. Lot Drift WARNING (Noticeable shift: Delta E ~ 3.2 - 4.2)
        drift_warn = self.generate_carpet(
            bgr_navy=(82, 48, 32),
            bgr_cream=(225, 236, 240),
            bgr_gold=(65, 185, 225),
            bgr_red=(6, 9, 150),
        )

        # 4. Lot Drift REJECT (Severe shade error: Delta E ~ 7.0+)
        drift_reject = self.generate_carpet(
            bgr_navy=(95, 60, 45),
            bgr_cream=(210, 225, 230),
            bgr_gold=(80, 195, 240),
            bgr_red=(30, 45, 190),  # Red drifted strongly towards orange/bright red
        )

        files = {
            "master": output_dir / "carpet_palette_master.png",
            "drift_pass": output_dir / "carpet_lot_drift_pass.png",
            "drift_warning": output_dir / "carpet_lot_drift_warning.png",
            "drift_reject": output_dir / "carpet_lot_drift_reject.png",
        }

        for key, path in files.items():
            img_to_save = {
                "master": master,
                "drift_pass": drift_pass,
                "drift_warning": drift_warn,
                "drift_reject": drift_reject,
            }[key]

            # Unicode-safe write
            success, buf = cv2.imencode(".png", img_to_save)
            if success:
                with open(path, "wb") as f:
                    f.write(buf)

        return files


if __name__ == "__main__":
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_carpets"
    gen = SyntheticCarpetPaletteGenerator()
    created = gen.create_fixture_suite(fixtures_dir)
    print(f"Created {len(created)} fixture images in {fixtures_dir}")
