"""
ciede2000.py - Vectorized & Scalar Implementation of ISO/CIE 11664-6:2014 CIEDE2000.

Implements the official CIE 2000 color difference formula as described in:
Sharma, G., Wu, W., and Dalal, E. N. (2005).
"The CIEDE2000 color-difference formula: Implementation notes, supplementary low-data,
and mathematical observations." Color Research & Application, 30(1), 21-30.
"""

from typing import Union
import numpy as np
import cv2


def ciede2000_scalar(
    lab1: Union[list, np.ndarray],
    lab2: Union[list, np.ndarray],
    kL: float = 1.0,
    kC: float = 1.0,
    kH: float = 1.0,
) -> float:
    """Compute scalar CIEDE2000 color difference between two CIE L*a*b* colors.

    Args:
        lab1: First color [L*, a*, b*] with L* in [0, 100].
        lab2: Second color [L*, a*, b*] with L* in [0, 100].
        kL: Lightness parametric weighting factor (default 1.0).
        kC: Chroma parametric weighting factor (default 1.0).
        kH: Hue parametric weighting factor (default 1.0).

    Returns:
        Perceptual color difference Delta E_00 (float >= 0.0).
    """
    v1 = np.asarray(lab1, dtype=np.float64).reshape(1, 3)
    v2 = np.asarray(lab2, dtype=np.float64).reshape(1, 3)
    return float(ciede2000_vectorized(v1, v2, kL=kL, kC=kC, kH=kH)[0])


def ciede2000_vectorized(
    lab1: np.ndarray,
    lab2: np.ndarray,
    kL: float = 1.0,
    kC: float = 1.0,
    kH: float = 1.0,
) -> np.ndarray:
    """Compute vectorized CIEDE2000 color difference between arrays of CIELAB colors.

    Supports broadcasting between:
    - (N, 3) and (N, 3) -> returns (N,)
    - (N, 3) and (1, 3) -> returns (N,)
    - (1, 3) and (N, 3) -> returns (N,)
    - (N, 1, 3) and (1, M, 3) -> returns (N, M) pairwise matrix

    Args:
        lab1: Array with last dimension 3 [L*, a*, b*].
        lab2: Array with last dimension 3 [L*, a*, b*].
        kL, kC, kH: Parametric weighting factors.

    Returns:
        Array of Delta E_00 values matching broadcasted leading dimensions.
    """
    l1 = np.asarray(lab1, dtype=np.float64)
    l2 = np.asarray(lab2, dtype=np.float64)

    L1, a1, b1 = l1[..., 0], l1[..., 1], l1[..., 2]
    L2, a2, b2 = l2[..., 0], l2[..., 1], l2[..., 2]

    # Step 1: Calculate C*_1, C*_2, C_bar, and factor G
    C1 = np.hypot(a1, b1)
    C2 = np.hypot(a2, b2)
    C_bar = 0.5 * (C1 + C2)

    C_bar_7 = np.power(C_bar, 7.0)
    G = 0.5 * (1.0 - np.sqrt(C_bar_7 / (C_bar_7 + 6103515625.0)))  # 25^7 = 6103515625

    a1_prime = (1.0 + G) * a1
    a2_prime = (1.0 + G) * a2

    C1_prime = np.hypot(a1_prime, b1)
    C2_prime = np.hypot(a2_prime, b2)

    # Hue angles in degrees [0, 360)
    h1_prime = np.degrees(np.arctan2(b1, a1_prime)) % 360.0
    h2_prime = np.degrees(np.arctan2(b2, a2_prime)) % 360.0

    # For achromatic colors (C' == 0), set hue to 0
    h1_prime = np.where(C1_prime < 1e-9, 0.0, h1_prime)
    h2_prime = np.where(C2_prime < 1e-9, 0.0, h2_prime)

    # Step 2: Compute Delta L', Delta C', Delta H'
    delta_L_prime = L2 - L1
    delta_C_prime = C2_prime - C1_prime

    h_diff = h2_prime - h1_prime
    abs_h_diff = np.abs(h_diff)

    delta_h_prime = np.zeros_like(h_diff)
    # Condition: C1'*C2' != 0
    chroma_nonzero = (C1_prime * C2_prime) >= 1e-9
    delta_h_prime = np.where(
        chroma_nonzero & (abs_h_diff <= 180.0),
        h_diff,
        delta_h_prime
    )
    delta_h_prime = np.where(
        chroma_nonzero & (abs_h_diff > 180.0) & (h2_prime <= h1_prime),
        h_diff + 360.0,
        delta_h_prime
    )
    delta_h_prime = np.where(
        chroma_nonzero & (abs_h_diff > 180.0) & (h2_prime > h1_prime),
        h_diff - 360.0,
        delta_h_prime
    )

    delta_H_prime = 2.0 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(0.5 * delta_h_prime))

    # Step 3: Compute L_bar', C_bar', and h_bar'
    L_bar_prime = 0.5 * (L1 + L2)
    C_bar_prime = 0.5 * (C1_prime + C2_prime)

    h_sum = h1_prime + h2_prime
    h_bar_prime = np.zeros_like(h_sum)

    # If either C' is zero:
    h_bar_prime = np.where(~chroma_nonzero, h_sum, h_bar_prime)

    # If both C' are non-zero:
    h_bar_prime = np.where(
        chroma_nonzero & (abs_h_diff <= 180.0),
        0.5 * h_sum,
        h_bar_prime
    )
    h_bar_prime = np.where(
        chroma_nonzero & (abs_h_diff > 180.0) & (h_sum < 360.0),
        0.5 * (h_sum + 360.0),
        h_bar_prime
    )
    h_bar_prime = np.where(
        chroma_nonzero & (abs_h_diff > 180.0) & (h_sum >= 360.0),
        0.5 * (h_sum - 360.0),
        h_bar_prime
    )

    # Step 4: Weighting functions T, SL, SC, SH, RT
    T = (
        1.0
        - 0.17 * np.cos(np.radians(h_bar_prime - 30.0))
        + 0.24 * np.cos(np.radians(2.0 * h_bar_prime))
        + 0.32 * np.cos(np.radians(3.0 * h_bar_prime + 6.0))
        - 0.20 * np.cos(np.radians(4.0 * h_bar_prime - 63.0))
    )

    delta_theta = 30.0 * np.exp(-np.square((h_bar_prime - 275.0) / 25.0))

    C_bar_prime_7 = np.power(C_bar_prime, 7.0)
    R_C = 2.0 * np.sqrt(C_bar_prime_7 / (C_bar_prime_7 + 6103515625.0))

    L_term = np.square(L_bar_prime - 50.0)
    S_L = 1.0 + (0.015 * L_term) / np.sqrt(20.0 + L_term)
    S_C = 1.0 + 0.045 * C_bar_prime
    S_H = 1.0 + 0.015 * C_bar_prime * T

    R_T = -np.sin(np.radians(2.0 * delta_theta)) * R_C

    # Step 5: Final CIEDE2000 calculation
    term_L = delta_L_prime / (kL * S_L)
    term_C = delta_C_prime / (kC * S_C)
    term_H = delta_H_prime / (kH * S_H)

    dE2 = (
        np.square(term_L)
        + np.square(term_C)
        + np.square(term_H)
        + R_T * term_C * term_H
    )

    # Enforce non-negative due to float rounding
    return np.sqrt(np.maximum(dE2, 0.0))


def ciede2000_error_map(
    image_lab: np.ndarray,
    quantized_lab: np.ndarray,
) -> np.ndarray:
    """Compute 2D CIEDE2000 distortion heatmap between original and quantized LAB images.

    Args:
        image_lab: Float32 CIELAB image of shape (H, W, 3).
        quantized_lab: Float32 CIELAB image of shape (H, W, 3).

    Returns:
        Float32 2D heatmap of shape (H, W) containing Delta E_00 error per pixel.
    """
    h, w, c = image_lab.shape
    flat_orig = image_lab.reshape(-1, 3)
    flat_quant = quantized_lab.reshape(-1, 3)
    errors = ciede2000_vectorized(flat_orig, flat_quant)
    return errors.reshape(h, w).astype(np.float32)


def bgr_to_cielab_float(bgr: np.ndarray) -> np.ndarray:
    """Convert standard uint8 BGR image or array to D65 CIELAB float32 format."""
    float_bgr = np.asarray(bgr, dtype=np.float32) / 255.0
    return cv2.cvtColor(float_bgr, cv2.COLOR_BGR2Lab)


def cielab_to_bgr_uint8(lab: np.ndarray) -> np.ndarray:
    """Convert float32 CIELAB image or array back to uint8 BGR format."""
    bgr_float = cv2.cvtColor(lab.astype(np.float32), cv2.COLOR_Lab2BGR)
    return np.clip(bgr_float * 255.0, 0, 255).astype(np.uint8)


ciede2000 = ciede2000_scalar

