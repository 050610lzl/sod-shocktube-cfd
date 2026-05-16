"""
流场初始化模块单元测试 (tests/test_initialization.py)
=====================================================
验证Sod激波管标准初始条件的正确赋值。

依据: Build文档 §5.2, §7.1
文献: Sod (1978) [1], Anderson (1984) [2], OneFlow-CFD [4]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.flow_initializer import initialize_flow


def setup_mesh(n=100):
    x = np.linspace(0.0, 1.0, n)
    return x


def test_left_density():
    x = setup_mesh()
    U = initialize_flow(x)
    left_indices = x < 0.5
    assert np.allclose(U[left_indices, 0], 1.0)


def test_right_density():
    x = setup_mesh()
    U = initialize_flow(x)
    right_indices = x >= 0.5
    assert np.allclose(U[right_indices, 0], 0.125)


def test_left_velocity():
    x = setup_mesh()
    U = initialize_flow(x)
    left_indices = x < 0.5
    assert np.allclose(U[left_indices, 1], 0.0)


def test_right_velocity():
    x = setup_mesh()
    U = initialize_flow(x)
    right_indices = x >= 0.5
    assert np.allclose(U[right_indices, 1], 0.0)


def test_left_total_energy():
    x = setup_mesh()
    U = initialize_flow(x)
    left_indices = x < 0.5
    expected_E = 2.5
    assert np.allclose(U[left_indices, 2], 1.0 * expected_E)


def test_right_total_energy():
    x = setup_mesh()
    U = initialize_flow(x)
    right_indices = x >= 0.5
    expected_E = 2.0
    assert np.allclose(U[right_indices, 2], 0.125 * expected_E)


def test_diaphragm_position():
    x = setup_mesh()
    U = initialize_flow(x, diaphragm_pos=0.5)
    idx = np.argmax(x >= 0.5)
    assert U[idx, 0] == 0.125
    assert U[idx - 1, 0] == 1.0


def test_output_shape():
    x = setup_mesh(n=200)
    U = initialize_flow(x)
    assert U.shape == (200, 3)


def test_conservative_consistency():
    x = setup_mesh()
    U = initialize_flow(x)
    assert np.all(U[:, 0] >= 0.0)
    rho = U[:, 0]
    u = U[:, 1] / rho
    assert np.allclose(u[x < 0.5], 0.0)
    assert np.allclose(u[x >= 0.5], 0.0)
