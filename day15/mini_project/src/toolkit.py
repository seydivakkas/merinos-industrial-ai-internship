import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import json
import os

# Day 15: Endüstriyel görsel denetim araç kiti
# Önceki günlerde geliştirilen görüntü işleme modüllerinin
# ortak bir arayüzde birleştirilmesi


def safe_read_image(path: Union[str, Path]) -> np.ndarray:
    """Read an image safely handling Windows Unicode and Turkish characters."""
    p = str(Path(path).resolve())
    if not os.path.exists(p):
        raise FileNotFoundError(f"Image not found at path: {p}")
    data = np.fromfile(p, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not decode image at path: {p}")
    return img


def safe_write_image(path: Union[str, Path], img: np.ndarray) -> bool:
    """Write an image safely handling Windows Unicode and Turkish characters."""
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower() if p.suffix else ".png"
    success, enc = cv2.imencode(ext, img)
    if success:
        enc.tofile(str(p))
        return True
    return False


class MerinosIndustrialVisionToolkit:
    """
    Merinos Endüstriyel halı denetimi için görüntü işleme araç kiti.
    Day 15 kapsamında önceki günlerde geliştirilen modülleri
    birleştirir ve CLI, pipeline ve benchmark bileşenleri için
    ortak fonksiyonlar sağlar.
    """

    def __init__(self, config_path: Optional[Union[str, Path, Dict[str, Any]]] = None):
        """
        Araç kiti başlangıcı.

        Args:
            config_path: JSON konfigürasyon dosyası yolu
        """
        if isinstance(config_path, dict):
            self.config_path = "../configs/toolkit_config.json"
            self.config = config_path
        else:
            self.config_path = str(config_path) if config_path else "../configs/toolkit_config.json"
            self.config = self._load_config()
        self.version = "2.0.0"
        # Önceki günlerde geliştirilen modüllerle entegrasyon
        self._init_modules()

    def _load_config(self) -> Dict:
        """
        JSON konfigürasyon dosyasını yükler.
        """
        try:
            cfg_p = Path(self.config_path)
            if not cfg_p.exists():
                fallback = Path(__file__).resolve().parent.parent / "configs" / "toolkit_config.json"
                if fallback.exists():
                    cfg_p = fallback
            if cfg_p.exists():
                with open(cfg_p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _init_modules(self) -> None:
        """Önceki günlerde geliştirilen modüllerle entegrasyon."""
        pass

    # -------------------------------------------------------------
    # Day 07: I/O, Filtering and Resizing
    # -------------------------------------------------------------
    def filter_image(
        self,
        image: np.ndarray,
        filter_type: str = "bilateral",
        kernel_size: int = 5,
        sigma_color: float = 75.0,
        sigma_space: float = 75.0,
    ) -> np.ndarray:
        """Apply noise reduction or smoothing filters."""
        if filter_type == "bilateral":
            return cv2.bilateralFilter(
                image, d=kernel_size, sigmaColor=sigma_color, sigmaSpace=sigma_space
            )
        elif filter_type == "gaussian":
            k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
            return cv2.GaussianBlur(image, (k, k), 0)
        elif filter_type == "median":
            k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
            return cv2.medianBlur(image, k)
        else:
            return cv2.blur(image, (kernel_size, kernel_size))

    def resize_image(self, image: np.ndarray, width: int, height: int) -> np.ndarray:
        """Resize image to target dimensions."""
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    # -------------------------------------------------------------
    # Day 08 & 09: Color Analysis & CIEDE2000 Matching
    # -------------------------------------------------------------
    def extract_dominant_colors(
        self, image: np.ndarray, n_colors: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract dominant palette colors using K-Means clustering.

        Returns:
            centers_rgb: (K, 3) array of RGB cluster centers
            weights: (K,) array of percentage coverage [0, 1]
        """
        from day09.mini_project.src.kmeans_palette import KMeansPaletteExtractor

        extractor = KMeansPaletteExtractor(default_k=n_colors, random_state=42)
        res = extractor.extract_palette(image, k=n_colors)
        centers_rgb = np.array([c.rgb for c in res.palette], dtype=np.uint8)
        weights = np.array([c.percentage / 100.0 for c in res.palette], dtype=np.float32)
        return centers_rgb, weights

    def calculate_delta_e(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """Calculate CIEDE2000 perceptual color difference between two LAB colors."""
        from day09.mini_project.src.ciede2000 import ciede2000_scalar

        return float(ciede2000_scalar(lab1, lab2))

    # -------------------------------------------------------------
    # Day 10: Perspective Rectification & Homography
    # -------------------------------------------------------------
    def rectify_carpet(
        self, image: np.ndarray, target_width: int = 600, target_height: int = 600
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Detect carpet corners, compute homography and warp perspective.

        Returns:
            warped: (H, W, 3) rectified carpet image
            H: (3, 3) homography transformation matrix
        """
        from day10.mini_project.src.rectifier import CarpetPerspectiveRectifier

        rectifier = CarpetPerspectiveRectifier()
        warped_img, rep = rectifier.rectify(image)
        if (warped_img.shape[1], warped_img.shape[0]) != (target_width, target_height):
            warped_img = cv2.resize(warped_img, (target_width, target_height))
        H_matrix = rep.homography.to_numpy()
        return warped_img, H_matrix

    # -------------------------------------------------------------
    # Day 11: Morphological Defect Detection
    # -------------------------------------------------------------
    def detect_defects(
        self, image: np.ndarray, min_area: int = 25, max_area: int = 5000
    ) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """Detect yarn breaks, holes, or oil spots using morphological operations.

        Returns:
            defects: List of detected defect metadata dicts
            defect_mask: Binary mask of detected defects
        """
        from day11.mini_project.src.defect_detector import CarpetDefectDetector

        detector = CarpetDefectDetector(min_area=float(min_area), max_area=float(max_area))
        report, debug_masks = detector.inspect(image)
        defects_info = [
            {
                "defect_id": f"DEF-{idx+1:03d}",
                "defect_type": d.defect_type.value,
                "severity": d.severity.value,
                "area_px": d.bbox.area,
                "bbox": [d.bbox.x, d.bbox.y, d.bbox.width, d.bbox.height],
                "confidence": d.confidence,
            }
            for idx, d in enumerate(report.defects)
        ]
        mask_top = debug_masks.get("mask_tophat", np.zeros(image.shape[:2], dtype=np.uint8))
        mask_bot = debug_masks.get("mask_blackhat", np.zeros(image.shape[:2], dtype=np.uint8))
        mask = cv2.bitwise_or(mask_top, mask_bot)
        return defects_info, mask

    # -------------------------------------------------------------
    # Day 12: Edge & Border Parallelism Analysis
    # -------------------------------------------------------------
    def analyze_borders(
        self,
        image: np.ndarray,
        canny_low: int = 50,
        canny_high: int = 150,
        hough_threshold: int = 60,
    ) -> Dict[str, Any]:
        """Analyze edge features, Hough lines, and jacquard border parallelism.

        Returns:
            border_metrics: Dict with max_skew_deg, orthogonality_error_deg, is_parallel
        """
        from day12.mini_project.src.border_analyzer import CarpetBorderAnalyzer

        analyzer = CarpetBorderAnalyzer()
        report, _ = analyzer.analyze_carpet(image)

        max_skew = 0.0
        if report.horizontal_parallelism is not None:
            diff_h = report.horizontal_parallelism.angle_difference_deg % 180.0
            max_skew = max(max_skew, min(diff_h, 180.0 - diff_h))
        if report.vertical_parallelism is not None:
            diff_v = report.vertical_parallelism.angle_difference_deg % 180.0
            max_skew = max(max_skew, min(diff_v, 180.0 - diff_v))

        ortho_err = report.orthogonality_deviation_deg or 0.0
        if ortho_err > 90.0:
            ortho_err = abs(180.0 - ortho_err)

        return {
            "max_skew_deg": round(max_skew, 2),
            "orthogonality_error_deg": round(ortho_err, 2),
            "is_parallel": report.decision.value in ["ACCEPT", "WARNING"],
            "detected_lines_count": report.total_lines_detected,
            "quality_grade": report.decision.value,
        }

    # -------------------------------------------------------------
    # Day 13: Classical Segmentation (Watershed / Otsu)
    # -------------------------------------------------------------
    def segment_motif(
        self, image: np.ndarray, method: str = "watershed"
    ) -> Tuple[np.ndarray, float]:
        """Segment jacquard motifs from background.

        Returns:
            mask: Binary segmentation mask (255: motif, 0: background)
            coverage_pct: Motif pixel coverage percentage [0, 100]
        """
        if method.lower() == "otsu":
            from day13.mini_project.src.otsu_segmenter import OtsuSegmenter

            seg = OtsuSegmenter()
            mask, _ = seg.segment_global(image)
        else:
            from day13.mini_project.src.watershed_segmenter import WatershedSegmenter

            seg = WatershedSegmenter()
            mask, _, _ = seg.segment(image)

        coverage_pct = float((np.count_nonzero(mask) / mask.size) * 100.0)
        return mask, coverage_pct

    # -------------------------------------------------------------
    # Day 14: Visual Feature Extraction & Fusion
    # -------------------------------------------------------------
    def extract_multimodal_features(
        self, image: np.ndarray, n_keypoints: int = 500
    ) -> Dict[str, Any]:
        """Extract ORB keypoints, GLCM texture, and HSV color histograms.

        Returns:
            features: Dict containing keypoint count, GLCM contrast/homogeneity/energy,
                      and fused vector dimension
        """
        from day14.mini_project.src.feature_fusion import CarpetPatternClassifierAndMatcher

        matcher = CarpetPatternClassifierAndMatcher()
        glcm_feats = matcher.glcm_engine.extract_features(image)
        _, _, kp_stats = matcher.keypoint_engine.extract_orb(image)
        vector = matcher.build_feature_vector(image, image_name="sample")

        return {
            "keypoint_count": kp_stats.count,
            "glcm_contrast": float(glcm_feats.contrast),
            "glcm_homogeneity": float(glcm_feats.homogeneity),
            "glcm_energy": float(glcm_feats.energy),
            "fused_vector_dim": int(vector.total_dimension),
            "fused_vector": np.array(vector.vector, dtype=np.float32),
        }
