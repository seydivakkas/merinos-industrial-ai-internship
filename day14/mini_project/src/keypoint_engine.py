import cv2
import numpy as np
from typing import Any, Dict, List, Optional, Tuple


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Görüntüyü gri tona çevirir."""
    if image.ndim == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def extract_orb(
    image: np.ndarray,
    n_features: int = 1000,
    scale_factor: float = 1.2,
    n_levels: int = 8,
) -> Tuple[list, np.ndarray]:
    """ORB yöntemiyle anahtar noktaları çıkarır."""
    gray = _to_gray(image)
    orb = cv2.ORB_create(
        nfeatures=n_features,
        scaleFactor=scale_factor,
        nlevels=n_levels,
    )
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return keypoints, descriptors


def extract_sift(
    image: np.ndarray,
    n_features: int = 1000,
    contrast_threshold: float = 0.04,
    edge_threshold: float = 10.0,
) -> Tuple[list, np.ndarray]:
    """SIFT yöntemiyle anahtar noktaları çıkarır."""
    gray = _to_gray(image)
    sift = cv2.SIFT_create(
        nfeatures=n_features,
        contrastThreshold=contrast_threshold,
        edgeThreshold=edge_threshold,
    )
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return keypoints, descriptors


from .models import KeypointDescriptorType, KeypointStats


class KeypointFeatureEngine:
    """ORB ve SIFT tabanlı yerel anahtar nokta çıkarımı ve eşleme motoru."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 1. ORB Konfigürasyonu
        orb_cfg = self.config.get("orb", {})
        n_orb = int(orb_cfg.get("n_features", 1000))
        scale_orb = float(orb_cfg.get("scale_factor", 1.2))
        levels_orb = int(orb_cfg.get("n_levels", 8))
        edge_orb = int(orb_cfg.get("edge_threshold", 31))
        patch_orb = int(orb_cfg.get("patch_size", 31))
        fast_thresh = int(orb_cfg.get("fast_threshold", 20))
        
        self.orb = cv2.ORB_create(
            nfeatures=n_orb,
            scaleFactor=scale_orb,
            nlevels=levels_orb,
            edgeThreshold=edge_orb,
            patchSize=patch_orb,
            fastThreshold=fast_thresh,
        )

        # 2. SIFT Konfigürasyonu
        sift_cfg = self.config.get("sift", {})
        n_sift = int(sift_cfg.get("n_features", 1000))
        octave_layers = int(sift_cfg.get("n_octave_layers", 3))
        contrast_thresh = float(sift_cfg.get("contrast_threshold", 0.04))
        edge_sift = float(sift_cfg.get("edge_threshold", 10.0))
        sigma_sift = float(sift_cfg.get("sigma", 1.6))

        self.sift = cv2.SIFT_create(
            nfeatures=n_sift,
            nOctaveLayers=octave_layers,
            contrastThreshold=contrast_thresh,
            edgeThreshold=edge_sift,
            sigma=sigma_sift,
        )

    def _to_gray(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü güvenli bir şekilde gri seviyeye dönüştürür."""
        if image is None or image.size == 0:
            raise ValueError("Görüntü boş olamaz.")
        if len(image.shape) == 3 and image.shape[2] >= 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            return image.copy()
        else:
            raise ValueError(f"Desteklenmeyen görüntü boyutu: {image.shape}")

    def _compute_keypoint_stats(self, keypoints: List[cv2.KeyPoint]) -> KeypointStats:
        """Anahtar nokta listesinden uzamsal ve açısal istatistikleri çıkarır."""
        count = len(keypoints)
        if count == 0:
            return KeypointStats(
                count=0,
                mean_response=0.0,
                mean_size=0.0,
                angle_entropy=0.0,
            )

        responses = [kp.response for kp in keypoints]
        sizes = [kp.size for kp in keypoints]
        angles = [kp.angle for kp in keypoints if kp.angle >= 0]

        mean_resp = float(np.mean(responses))
        mean_sz = float(np.mean(sizes))

        # Yön açılarının Shannon entropisi (36 bin, 10 derece aralık)
        if len(angles) > 1:
            hist, _ = np.histogram(angles, bins=36, range=(0, 360))
            prob = hist / float(len(angles))
            prob = prob[prob > 0]
            entropy = float(-np.sum(prob * np.log2(prob)))
        else:
            entropy = 0.0

        return KeypointStats(
            count=count,
            mean_response=round(mean_resp, 4),
            mean_size=round(mean_sz, 4),
            angle_entropy=round(entropy, 4),
        )

    def extract_orb(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[List[cv2.KeyPoint], Optional[np.ndarray], KeypointStats]:
        """Görüntüden ORB anahtar noktaları ve 256-bit ikili tanımlayıcılarını çıkarır."""
        gray = self._to_gray(image)
        keypoints, descriptors = self.orb.detectAndCompute(gray, mask)
        stats = self._compute_keypoint_stats(keypoints)
        return keypoints, descriptors, stats

    def extract_sift(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[List[cv2.KeyPoint], Optional[np.ndarray], KeypointStats]:
        """Görüntüden SIFT anahtar noktaları ve 128-boyutlu tanımlayıcılarını çıkarır."""
        gray = self._to_gray(image)
        keypoints, descriptors = self.sift.detectAndCompute(gray, mask)
        stats = self._compute_keypoint_stats(keypoints)
        return keypoints, descriptors, stats

    def match_features(
        self,
        descriptors1: Optional[np.ndarray],
        descriptors2: Optional[np.ndarray],
        method: KeypointDescriptorType = KeypointDescriptorType.ORB,
        ratio_threshold: float = 0.75,
    ) -> List[cv2.DMatch]:
        """Lowe's Ratio Test uygulayarak iki tanımlayıcı kümesi arasındaki iyi eşleşmeleri bulur."""
        if (
            descriptors1 is None
            or descriptors2 is None
            or len(descriptors1) < 2
            or len(descriptors2) < 2
        ):
            return []

        if method == KeypointDescriptorType.ORB or method == "ORB":
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        knn_matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

        good_matches: List[cv2.DMatch] = []
        for pair in knn_matches:
            if len(pair) == 2:
                m, n = pair
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append(m)

        # Mesafeye göre artan sırala
        good_matches.sort(key=lambda x: x.distance)
        return good_matches

    def compute_homography_inliers(
        self,
        keypoints1: List[cv2.KeyPoint],
        keypoints2: List[cv2.KeyPoint],
        matches: List[cv2.DMatch],
        ransac_reproj_thresh: float = 3.0,
    ) -> Tuple[Optional[np.ndarray], float]:
        """RANSAC ile iki görsel arasındaki homografi matrisini ve inlier oranını hesaplar."""
        if len(matches) < 4:
            return None, 0.0

        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        H, inlier_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_reproj_thresh)

        if inlier_mask is None:
            return None, 0.0

        inliers_count = int(np.sum(inlier_mask))
        ratio = float(inliers_count / len(matches))
        return H, round(ratio, 4)

    def draw_matches(
        self,
        img1: np.ndarray,
        kpts1: List[cv2.KeyPoint],
        img2: np.ndarray,
        kpts2: List[cv2.KeyPoint],
        matches: List[cv2.DMatch],
        max_matches: int = 40,
    ) -> np.ndarray:
        """İki görsel arasındaki iyi anahtar nokta eşleşmelerini yan yana çizen görsel panel üretir."""
        top_matches = matches[:max_matches]
        draw_params = dict(
            matchColor=(0, 255, 0),
            singlePointColor=(255, 0, 0),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )
        vis = cv2.drawMatches(img1, kpts1, img2, kpts2, top_matches, None, **draw_params)
        return vis
