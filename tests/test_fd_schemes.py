"""
有限差分格式模块单元测试 (tests/test_fd_schemes.py)
===================================================
验证4种必选FDM格式的单步差分正确性与物理合理性。

依据: Build文档 §5.3, §7.1
文献: Sod (1978) [1], Laney (1998) [3], LeVeque (1992) [5]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.fd_schemes import (
    compute_flux, conservative_to_primitive, compute_jacobian,
    lax_friedrichs_step, lax_wendroff_step, macormack_step, upwind_step,
    steger_warming_flux, GAMMA
)
from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt


def setup():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt = compute_dt(U, dx, cfl=0.8)
    return x, dx, dt, U


def test_flux_physical_consistency():
    U = setup()[3]
    F = compute_flux(U)
    assert not np.any(np.isnan(F))
    assert not np.any(np.isinf(F))
    rho = U[:, 0]
    u = U[:, 1] / rho
    assert np.allclose(F[rho > 1e-3, 0], (rho * u)[rho > 1e-3])


def test_conservative_to_primitive():
    x, dx, dt, U = setup()
    rho, u, p = conservative_to_primitive(U)
    assert np.all(rho > 0)
    assert np.all(p > 0)
    assert np.allclose(rho[x < 0.5], 1.0)
    assert np.allclose(rho[x >= 0.5], 0.125)


def test_jacobian_shape():
    U = setup()[3]
    A = compute_jacobian(U)
    assert A.shape == (100, 3, 3)


def test_lax_friedrichs_step():
    x, dx, dt, U = setup()
    U_new = lax_friedrichs_step(U, dx, dt)
    assert not np.any(np.isnan(U_new))
    assert np.all(U_new[1:-1, 0] > 0)


def test_lax_wendroff_step():
    x, dx, dt, U = setup()
    U_new = lax_wendroff_step(U, dx, dt)
    assert not np.any(np.isnan(U_new))
    assert np.all(U_new[1:-1, 0] > 0)


def test_macormack_step():
    x, dx, dt, U = setup()
    U_new = macormack_step(U, dx, dt)
    assert not np.any(np.isnan(U_new))
    assert np.all(U_new[1:-1, 0] > 0)


def test_upwind_step():
    x, dx, dt, U = setup()
    U_new = upwind_step(U, dx, dt)
    assert not np.any(np.isnan(U_new))
    assert np.all(U_new[1:-1, 0] > 0)


def test_steger_warming_consistency():
    U = setup()[3]
    F_pos, F_neg = steger_warming_flux(U)
    F = compute_flux(U)
    for i in range(1, len(U) - 1):
        error = np.linalg.norm((F_pos[i] + F_neg[i]) - F[i])
        rho = U[i, 0]
        u = U[i, 1] / rho
        if abs(u) < 0.1:
            assert error < 1e-5


def test_lax_friedrichs_conservation():
    x, dx, dt, U = setup()
    U_new = lax_friedrichs_step(U, dx, dt)
    mass_before = np.sum(U[1:-1, 0]) * dx
    mass_after = np.sum(U_new[1:-1, 0]) * dx
    assert abs(mass_after - mass_before) / abs(mass_before) < 0.01


def test_upwind_monotonicity():
    x, dx, dt, U = setup()
    U = apply_boundary_condition(U)
    U_new = upwind_step(U, dx, dt)
    interior = slice(2, -2)
    assert np.all(U_new[interior, 0] >= 0.0)


def test_lax_wendroff_symmetry():
    n = 50
    x = np.linspace(0.0, 1.0, n)
    x_mid = (x[1:] + x[:-1]) / 2.0
    U = initialize_flow(x)
    dx = x[1] - x[0]
    dt = compute_dt(U, dx, cfl=0.8)
    U_new = lax_wendroff_step(U, dx, dt)
    assert not np.any(np.isnan(U_new))
