"""
边界处理模块单元测试 (tests/test_boundary.py)
=============================================
验证零梯度外推边界条件的正确性。

依据: Build文档 §5.4, §7.1
文献: Laney (1998) [3], OneFlow-CFD [4]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.boundary_handler import apply_boundary_condition
from src.flow_initializer import initialize_flow


def setup_flow(n=100):
    x = np.linspace(0.0, 1.0, n)
    U = initialize_flow(x)
    return U.copy()


def test_left_boundary_rho():
    U = setup_flow()
    U[1, 0] = 0.5
    U = apply_boundary_condition(U)
    assert abs(U[0, 0] - U[1, 0]) < 1e-15


def test_left_boundary_momentum():
    U = setup_flow()
    U[1, 1] = 0.3
    U = apply_boundary_condition(U)
    assert abs(U[0, 1] - U[1, 1]) < 1e-15


def test_left_boundary_energy():
    U = setup_flow()
    U[1, 2] = 3.0
    U = apply_boundary_condition(U)
    assert abs(U[0, 2] - U[1, 2]) < 1e-15


def test_right_boundary_rho():
    U = setup_flow()
    U[-2, 0] = 0.5
    U = apply_boundary_condition(U)
    assert abs(U[-1, 0] - U[-2, 0]) < 1e-15


def test_right_boundary_momentum():
    U = setup_flow()
    U[-2, 1] = 0.3
    U = apply_boundary_condition(U)
    assert abs(U[-1, 1] - U[-2, 1]) < 1e-15


def test_right_boundary_energy():
    U = setup_flow()
    U[-2, 2] = 3.0
    U = apply_boundary_condition(U)
    assert abs(U[-1, 2] - U[-2, 2]) < 1e-15


def test_all_components():
    U = setup_flow()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])
    U = apply_boundary_condition(U)
    assert np.allclose(U[0, :], U[1, :])
    assert np.allclose(U[-1, :], U[-2, :])


def test_interior_preserved():
    U = setup_flow()
    U_orig = U.copy()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])
    U = apply_boundary_condition(U)
    assert np.allclose(U[2:-2, :], U_orig[2:-2, :])
