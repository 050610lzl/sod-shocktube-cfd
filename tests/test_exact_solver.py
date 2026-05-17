"""
精确解计算模块单元测试 (tests/test_exact_solver.py)
=====================================================
验证Sod激波管Riemann精确解的正确性 (Toro 2009第4章)。

依据: Build文档 §7.1
文献: Toro (2009) [2] 第4章, Sod (1978) [1]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.exact_solver import sod_exact_solution


def test_exact_solution_shape():
    x = np.linspace(0.0, 1.0, 100)
    rho, u, p = sod_exact_solution(x, t=0.2)
    assert rho.shape == (100,)
    assert u.shape == (100,)
    assert p.shape == (100,)


def test_exact_solution_positive():
    x = np.linspace(0.0, 1.0, 100)
    rho, u, p = sod_exact_solution(x, t=0.2)
    assert np.all(rho > 0)
    assert np.all(p > 0)


def test_exact_solution_initial_condition():
    x_left = np.linspace(0.0, 0.3, 30)
    x_right = np.linspace(0.7, 1.0, 30)
    rho_l, u_l, p_l = sod_exact_solution(x_left, t=0.0)
    rho_r, u_r, p_r = sod_exact_solution(x_right, t=0.0)
    assert np.allclose(rho_l, 1.0, atol=1e-10)
    assert np.allclose(p_l, 1.0, atol=1e-10)
    assert np.allclose(rho_r, 0.125, atol=1e-10)
    assert np.allclose(p_r, 0.1, atol=1e-10)


def test_exact_solution_physical_range():
    x = np.linspace(0.0, 1.0, 100)
    rho, u, p = sod_exact_solution(x, t=0.2)
    assert np.min(rho) >= 0.1
    assert np.max(rho) <= 1.1
    assert np.min(p) >= 0.05
    assert np.max(p) <= 1.1
    assert np.max(u) >= -1.0
    assert np.max(u) <= 1.5


def test_exact_solution_no_nan():
    x = np.linspace(0.0, 1.0, 100)
    rho, u, p = sod_exact_solution(x, t=0.2)
    assert not np.any(np.isnan(rho))
    assert not np.any(np.isnan(u))
    assert not np.any(np.isnan(p))
    assert not np.any(np.isinf(rho))
    assert not np.any(np.isinf(u))
    assert not np.any(np.isinf(p))