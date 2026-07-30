"""Unit tests for Day 09 Image Preprocessor."""

import cv2
import numpy as np
import pytest
from day09.mini_project.src.image_preprocessor import ImagePreprocessor


def test_image_preprocessing_pipeline():
    preprocessor = ImagePreprocessor(target_size=(256, 256))
    dummy_bgr = np.random.randint(0, 256, (400, 600, 3), dtype=np.uint8)

    resized, enhanced = preprocessor.preprocess_pipeline(dummy_bgr)

    assert resized.shape == (256, 256, 3)
    assert enhanced.shape == (256, 256)
    assert enhanced.dtype == np.uint8
