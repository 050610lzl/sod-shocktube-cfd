"""
网格生成模块单元测试 (tests/test_mesh.py)
=========================================
验证网格生成的正确性。

依据: Build文档 §5.1, §7.1
文献: Laney (1998) [3]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.mesh_generator import generate_mesh


def test_default_mesh():
    x, dx = generate_mesh()
    assert len(x) == 100
    assert abs(x[0] - 0.0) < 1e-15
    assert abs(x[-1] - 1.0) < 1e-15
    assert abs(dx - 1.0 / 99.0) < 1e-10


def test_custom_n_points():
    for n in [50, 200, 400, 800]:
        x, dx = generate_mesh(n_points=n)
        assert len(x) == n
        assert abs(dx - 1.0 / (n - 1)) < 1e-10


def test_uniform_spacing():
    x, dx = generate_mesh(n_points=100)
    diffs = np.diff(x)
    assert np.allclose(diffs, dx, atol=1e-15)


def test_left_boundary():
    x, _ = generate_mesh(n_points=100, x_left=0.0, x_right=1.0)
    assert abs(x[0] - 0.0) < 1e-15


def test_right_boundary():
    x, _ = generate_mesh(n_points=100, x_left=0.0, x_right=1.0)
    assert abs(x[-1] - 1.0) < 1e-15


def test_midpoint():
    x, _ = generate_mesh(n_points=101)
    assert abs(x[50] - 0.5) < 1e-15
