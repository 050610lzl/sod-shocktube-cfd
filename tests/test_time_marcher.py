"""
时间推进模块单元测试 (tests/test_time_marcher.py)
==================================================
验证CFL时间步长计算、守恒量计算、守恒性检查等功能。

依据: Build文档 §7.1
文献: LeVeque (1992) [5], Laney (1998) [3]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.time_marcher import (
    conservative_to_primitive, compute_dt, time_march,
    compute_conserved_quantities, check_conservation
)
from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.fd_schemes import upwind_step


def test_compute_dt_positive():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt = compute_dt(U, dx, cfl=0.8)
    assert dt > 0
    assert dt < dx


def test_compute_dt_cfl_scaling():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt_08 = compute_dt(U, dx, cfl=0.8)
    dt_04 = compute_dt(U, dx, cfl=0.4)
    assert abs(dt_08 - 2.0 * dt_04) < 1e-14


def test_compute_dt_zero_velocity():
    U = np.zeros((10, 3))
    U[:, 0] = 1.0
    U[:, 2] = 2.5
    dx = 1.0
    dt = compute_dt(U, dx, cfl=0.8)
    assert dt > 0


def test_time_march():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt = compute_dt(U, dx, cfl=0.8)
    U_new = time_march(U, dx, dt, upwind_step)
    assert not np.any(np.isnan(U_new))
    assert U_new.shape == U.shape


def test_conserved_quantities():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    mass, momentum, energy = compute_conserved_quantities(U, dx)
    assert mass > 0
    assert energy > 0


def test_conservation_check():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    result = check_conservation(U, U, dx, 0)
    assert result['mass_change_pct'] < 1e-10
    assert result['momentum_change_pct'] < 1e-10
    assert result['energy_change_pct'] < 1e-10


def test_conservation_after_step():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt = compute_dt(U, dx, cfl=0.8)
    U_new = upwind_step(U, dx, dt)
    result = check_conservation(U_new, U, dx, 1)
    assert result['mass_current'] > 0
    assert result['energy_current'] > 0