"""Unicode-safe Image I/O and Industrial Metadata Validator.

Provides fault-tolerant image reading and writing on Windows operating systems
where non-ASCII and Turkish characters (e.g. 'Merinos 40 Günlük Staj Deneyimim')
frequently cause native cv2.imread and cv2.imwrite to silently fail or return None.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import cv2
import numpy as np


class ImageIOError(Exception):
    """Raised when an image cannot be read, decoded, encoded or written."""

    pass


class ImageValidationError(Exception):
    """Raised when an image array violates structural or numeric invariants."""

    pass


@dataclass
class ImageMetadata:
    """Rich metadata profile for industrial carpet scan images."""

    path: str
    height: int
    width: int
    channels: int
    dtype: str
    size_bytes: int
    aspect_ratio: float
    is_c_contiguous: bool
    min_intensity: float
    max_intensity: float
    mean_intensity: float
    std_intensity: float

    def to_dict(self) -> dict[str, Any]:
        """Serializes metadata to a dictionary."""
        return asdict(self)


class ImageIOValidator:
    """Production-grade image I/O handler with Unicode path support and schema validation."""

    @staticmethod
    def read_image(path: str | Path, flags: int = cv2.IMREAD_COLOR) -> np.ndarray:
        """Safely reads an image from disk using raw binary decoding.

        Standard cv2.imread fails silently on Windows paths containing non-ASCII
        characters. np.fromfile + cv2.imdecode bypasses Windows CRT path issues.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Image path does not exist: {p}")
        if not p.is_file():
            raise ImageIOError(f"Target path is not a valid file: {p}")

        try:
            raw_bytes = np.fromfile(str(p), dtype=np.uint8)
            if raw_bytes.size == 0:
                raise ImageIOError(f"Target image file is empty (0 bytes): {p}")

            img = cv2.imdecode(raw_bytes, flags)
            if img is None:
                raise ImageIOError(f"Failed to decode image from buffer: {p}")
            return img
        except Exception as err:
            if isinstance(err, (FileNotFoundError, ImageIOError)):
                raise
            raise ImageIOError(f"Unexpected error while reading {p}: {err}") from err

    @staticmethod
    def write_image(img: np.ndarray, path: str | Path, ext: str = ".png") -> Path:
        """Safely writes an image to disk using Unicode-safe encoding."""
        if not isinstance(img, np.ndarray):
            raise ImageValidationError("Input must be a numpy.ndarray.")
        if img.size == 0:
            raise ImageValidationError("Cannot write an empty image array.")

        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if not target_path.suffix:
            target_path = target_path.with_suffix(ext)

        file_ext = target_path.suffix.lower()
        success, encoded_buf = cv2.imencode(file_ext, img)
        if not success:
            raise ImageIOError(f"Failed to encode image with format {file_ext}")

        try:
            with open(target_path, "wb") as f:
                f.write(encoded_buf)
            return target_path
        except Exception as err:
            raise ImageIOError(f"Failed to write image to {target_path}: {err}") from err

    @staticmethod
    def extract_metadata(img: np.ndarray, source_path: str | Path = "") -> ImageMetadata:
        """Extracts structural and statistical attributes from an image array."""
        if not isinstance(img, np.ndarray):
            raise ImageValidationError("Input must be a numpy.ndarray.")
        if img.size == 0 or img.ndim not in (2, 3):
            raise ImageValidationError(f"Invalid image array shape: {img.shape}")

        h = int(img.shape[0])
        w = int(img.shape[1])
        c = int(img.shape[2]) if img.ndim == 3 else 1

        aspect = round(float(w) / float(h), 4) if h > 0 else 0.0

        return ImageMetadata(
            path=str(source_path),
            height=h,
            width=w,
            channels=c,
            dtype=str(img.dtype),
            size_bytes=int(img.nbytes),
            aspect_ratio=aspect,
            is_c_contiguous=bool(img.flags.c_contiguous),
            min_intensity=float(np.min(img)),
            max_intensity=float(np.max(img)),
            mean_intensity=round(float(np.mean(img)), 2),
            std_intensity=round(float(np.std(img)), 2),
        )

    @classmethod
    def load_and_validate(
        cls,
        path: str | Path,
        expected_channels: int | None = None,
        min_dim: tuple[int, int] = (16, 16),
    ) -> tuple[np.ndarray, ImageMetadata]:
        """Convenience method: reads, validates dimensions and extracts metadata."""
        img = cls.read_image(path)
        meta = cls.extract_metadata(img, path)

        if expected_channels is not None and meta.channels != expected_channels:
            raise ImageValidationError(
                f"Channel mismatch for {path}: expected {expected_channels}, got {meta.channels}"
            )

        min_h, min_w = min_dim
        if meta.height < min_h or meta.width < min_w:
            raise ImageValidationError(
                f"Image dimensions ({meta.height}x{meta.width}) below minimum threshold ({min_h}x{min_w})"
            )

        return img, meta
