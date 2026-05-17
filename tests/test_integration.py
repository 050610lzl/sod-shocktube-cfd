"""
CFD求解器集成测试 (tests/test_integration.py)
===============================================
验证9种数值格式的完整求解流程（多步迭代至 t=0.2）和CFL稳定性。

依据: Build文档 §7.2
文献: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt
from src.fd_schemes import (
    lax_friedrichs_step, lax_wendroff_step, macormack_step, upwind_step,
    rusanov_step, godunov_step, roe_step, hllc_step, tvd_minmod_step
)
import src.fd_schemes

SCHEMES = {
    'lax_friedrichs': lax_friedrichs_step,
    'lax_wendroff': lax_wendroff_step,
    'macormack': macormack_step,
    'upwind': upwind_step,
    'rusanov': rusanov_step,
    'godunov': godunov_step,
    'roe': roe_step,
    'hllc': hllc_step,
    'tvd_minmod': tvd_minmod_step,
}


def _run_scheme_to_tfinal(scheme_func, n_points=100, t_final=0.2, cfl=0.8):
    src.fd_schemes._macormack_step_counter = 0
    x, dx = generate_mesh(n_points=n_points)
    U = initialize_flow(x)
    t = 0.0
    steps = 0
    while t < t_final:
        dt = compute_dt(U, dx, cfl=cfl)
        if t + dt > t_final:
            dt = t_final - t
        U = scheme_func(U, dx, dt)
        U = apply_boundary_condition(U)
        t += dt
        steps += 1
        if steps > 100000:
            raise RuntimeError("Simulation did not converge within 100000 steps")
    rho = U[:, 0]
    u = U[:, 1] / rho
    p = (1.4 - 1.0) * (U[:, 2] - 0.5 * U[:, 1] ** 2 / rho)
    return steps, rho, u, p


@pytest.mark.parametrize("scheme_name,scheme_func", SCHEMES.items())
def test_scheme_positive_density_pressure(scheme_name, scheme_func):
    steps, rho, u, p = _run_scheme_to_tfinal(scheme_func)
    assert np.all(rho > 0), f'{scheme_name}: negative density detected'
    assert np.all(p > 0), f'{scheme_name}: negative pressure detected'
    assert steps > 0, f'{scheme_name}: zero steps taken'


@pytest.mark.parametrize("scheme_name,scheme_func", SCHEMES.items())
def test_scheme_physical_velocity(scheme_name, scheme_func):
    steps, rho, u, p = _run_scheme_to_tfinal(scheme_func)
    assert np.max(np.abs(u)) < 2.0, \
        f'{scheme_name}: unphysical velocity {np.max(np.abs(u)):.2f}'


def test_cfl_stability_check():
    x, dx = generate_mesh(n_points=100)
    U = initialize_flow(x)
    dt = compute_dt(U, dx, cfl=0.8)
    U_new = upwind_step(U, dx, dt)

    rho = U_new[:, 0]
    u = U_new[:, 1] / rho
    p = (1.4 - 1.0) * (U_new[:, 2] - 0.5 * U_new[:, 1] ** 2 / rho)

    assert np.all(rho > 0), 'Negative density after single upwind step'
    assert np.all(p > 0), 'Negative pressure after single upwind step'
    assert np.max(u) < 1.0, f'Unphysical velocity after single step: {np.max(u)}'


def test_mass_conservation_all_schemes():
    x, dx = generate_mesh(n_points=100)
    for name, func in SCHEMES.items():
        U = initialize_flow(x)
        mass_before = np.sum(U[1:-1, 0]) * dx
        U_new = func(U, dx, compute_dt(U, dx, cfl=0.8))
        mass_after = np.sum(U_new[1:-1, 0]) * dx
        if abs(mass_before) > 1e-10:
            rel_error = abs(mass_after - mass_before) / abs(mass_before)
            assert rel_error < 0.1, \
                f'{name}: mass conservation error {rel_error:.4f}'