"""
homography.py - Homography Matrix Calculation, Condition Number Analysis & Perspective Warping.
"""

from typing import Tuple, List
import numpy as np
import cv2

from .models import HomographyResult


def compute_homography(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
) -> Tuple[np.ndarray, HomographyResult]:
    """Compute the 3x3 perspective homography matrix mapping src_pts to dst_pts.

    Args:
        src_pts: Array of 4 source coplanar points of shape (4, 2).
        dst_pts: Array of 4 target rectified points of shape (4, 2).

    Returns:
        Tuple of:
        - H: (3, 3) float64 NumPy projection matrix.
        - result: HomographyResult containing condition number, det, and invertibility error.

    Raises:
        ValueError: If points are degenerate or matrix is singular.
    """
    s = np.asarray(src_pts, dtype=np.float32).reshape(4, 2)
    d = np.asarray(dst_pts, dtype=np.float32).reshape(4, 2)

    # Check for degenerate cases (collinear points)
    # Area of triangle formed by any 3 points should not be zero
    def triangle_area(p1, p2, p3):
        return 0.5 * abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]))

    if (
        triangle_area(s[0], s[1], s[2]) < 1.0
        or triangle_area(s[0], s[2], s[3]) < 1.0
        or triangle_area(d[0], d[1], d[2]) < 1.0
    ):
        raise ValueError("Degenerate collinear points detected. Cannot compute homography.")

    H = cv2.getPerspectiveTransform(s, d).astype(np.float64)

    # Normalize matrix scale so H[2, 2] == 1.0
    if abs(H[2, 2]) > 1e-9:
        H = H / H[2, 2]

    det = float(np.linalg.det(H))
    if abs(det) < 1e-9:
        raise ValueError(f"Singular homography matrix with near-zero determinant: {det:.2e}")

    cond = float(np.linalg.cond(H))
    try:
        H_inv = np.linalg.inv(H)
        inv_err = float(np.linalg.norm(np.dot(H, H_inv) - np.eye(3)))
    except np.linalg.LinAlgError:
        inv_err = float("inf")

    matrix_list = [[round(float(v), 8) for v in row] for row in H]

    result = HomographyResult(
        matrix=matrix_list,
        determinant=round(det, 6),
        condition_number=round(cond, 2),
        inverse_frobenius_error=round(inv_err, 8),
    )

    return H, result


def transform_points(points: np.ndarray, H: np.ndarray) -> np.ndarray:
    """Project 2D points through 3x3 homography matrix using homogeneous coordinates.

    Args:
        points: (N, 2) array of coordinates.
        H: (3, 3) homography projection matrix.

    Returns:
        (N, 2) array of transformed coordinates.
    """
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 2)
    n = pts.shape[0]

    # Convert to homogeneous (N, 3) [x, y, 1]
    homogeneous = np.hstack([pts, np.ones((n, 1), dtype=np.float64)])

    # Matrix multiplication: (3, 3) @ (3, N) -> (3, N) -> transpose to (N, 3)
    transformed_h = (H @ homogeneous.T).T

    # Perspective division by w component
    w = transformed_h[:, 2:3]
    w = np.where(np.abs(w) < 1e-9, 1e-9, w)
    projected = transformed_h[:, :2] / w

    return projected.astype(np.float32)


def warp_perspective(
    image: np.ndarray,
    H: np.ndarray,
    target_size: Tuple[int, int],
    flags: int = cv2.INTER_LINEAR,
    border_mode: int = cv2.BORDER_CONSTANT,
    border_value: int = 0,
) -> np.ndarray:
    """Warp image to rectified plane using homography matrix.

    Args:
        image: Source image array of shape (H, W) or (H, W, C).
        H: (3, 3) perspective homography matrix.
        target_size: Tuple of (target_width, target_height).
        flags: Interpolation flag (default: INTER_LINEAR).
        border_mode: OpenCV border mode.
        border_value: Fill value for border pixels.

    Returns:
        Rectified image of shape (target_height, target_width, C).
    """
    target_w, target_h = target_size
    return cv2.warpPerspective(
        image,
        H,
        (target_w, target_h),
        flags=flags,
        borderMode=border_mode,
        borderValue=border_value,
    )
