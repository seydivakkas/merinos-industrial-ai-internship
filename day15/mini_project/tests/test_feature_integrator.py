"""Unit tests for Day 15 Visual Feature Integrator."""

import numpy as np
import pytest
from day15.mini_project.src.feature_integrator import VisualFeatureIntegrator


def test_visual_feature_fusion():
    integrator = VisualFeatureIntegrator()
    dummy_bgr = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    vec = integrator.fuse_features(dummy_bgr)

    assert len(vec.texture_features) == 4
    assert len(vec.color_moments) == 6
    assert len(vec.hu_moments) == 7
    assert vec.total_dimension == 17
