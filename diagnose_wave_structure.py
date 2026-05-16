"""
诊断脚本：检查Sod激波管求解器的波系结构问题
检查精确解计算和迎风格式实现
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from src.exact_solver import sod_exact_solution
from src.fd_schemes import conservative_to_primitive, upwind_step, compute_flux
from src.boundary_handler import apply_boundary_condition
from src.flow_initializer import initialize_flow
from src.time_marcher import compute_dt

def diagnose_exact_solver():
    """诊断精确解计算是否正确"""
    print("=" * 80)
    print("诊断1: 精确解计算验证")
    print("=" * 80)
    
    # 标准Sod问题参数
    gamma = 1.4
    rho_L, u_L, p_L = 1.0, 0.0, 1.0
    rho_R, u_R, p_R = 0.125, 0.0, 0.1
    t_final = 0.2
    N = 400
    x = np.linspace(0, 1, N)
    dx = 1.0 / (N - 1)
    
    # 计算精确解
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t_final, gamma)
    
    print(f"左态: rho={rho_L}, u={u_L}, p={p_L}")
    print(f"右态: rho={rho_R}, u={u_R}, p={p_R}")
    print(f"计算域: [0, 1], N={N}, t={t_final}")
    print()
    
    # 查找接触间断位置附近的值
    contact_idx = np.argmin(np.abs(x - 0.685))
    print(f"接触间断附近 (x≈{x[contact_idx]:.4f}):")
    print(f"  rho = {rho_exact[contact_idx]:.6f}")
    print(f"  u   = {u_exact[contact_idx]:.6f}")
    print(f"  p   = {p_exact[contact_idx]:.6f}")
    
    # 检查稀疏波尾部
    tail_idx = np.argmin(np.abs(x - 0.4))
    print(f"\n稀疏波尾部附近 (x≈{x[tail_idx]:.4f}):")
    print(f"  rho = {rho_exact[tail_idx]:.6f}")
    print(f"  u   = {u_exact[tail_idx]:.6f}")
    print(f"  p   = {p_exact[tail_idx]:.6f}")
    
    # 检查激波前
    shock_idx = np.argmin(np.abs(x - 0.85))
    print(f"\n激波前附近 (x≈{x[shock_idx]:.4f}):")
    print(f"  rho = {rho_exact[shock_idx]:.6f}")
    print(f"  u   = {u_exact[shock_idx]:.6f}")
    print(f"  p   = {p_exact[shock_idx]:.6f}")
    
    # 计算理论值
    a_L = np.sqrt(gamma * p_L / rho_L)
    a_R = np.sqrt(gamma * p_R / rho_R)
    print(f"\n理论参数:")
    print(f"  a_L = {a_L:.6f}")
    print(f"  a_R = {a_R:.6f}")
    
    # 手动计算p*和u*以验证
    from scipy.optimize import brentq
    
    def pressure_function(p_star):
        if p_star <= p_L:
            f_L = (2.0 * a_L / (gamma - 1.0)) * \
                  ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_L = 2.0 / ((gamma + 1.0) * rho_L)
            B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
            f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

        if p_star <= p_R:
            f_R = (2.0 * a_R / (gamma - 1.0)) * \
                  ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_R = 2.0 / ((gamma + 1.0) * rho_R)
            B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
            f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))

        return f_L + f_R + (u_R - u_L)
    
    p_star = brentq(pressure_function, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-12)
    
    if p_star <= p_L:
        u_star = u_L - (2.0 * a_L / (gamma - 1.0)) * \
                 ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))
    
    print(f"\n接触间断理论值:")
    print(f"  p* = {p_star:.6f} (理论值: 0.303)")
    print(f"  u* = {u_star:.6f} (理论值: 0.927)")
    
    # 检查稀疏波公式
    print(f"\n稀疏波内公式检查:")
    x_test = 0.4
    xi_local = (x_test - 0.5) / t_final
    u_val = 2.0 / (gamma + 1.0) * (a_L + xi_local)
    print(f"  x = {x_test}")
    print(f"  (x-0.5)/t = {xi_local:.6f}")
    print(f"  u = 2/(γ+1) * (a_L + (x-0.5)/t) = {u_val:.6f}")
    
    # 从精确解获取该位置的速度
    exact_idx = np.argmin(np.abs(x - x_test))
    print(f"  精确解u[{exact_idx}] = {u_exact[exact_idx]:.6f}")
    
    return rho_exact, u_exact, p_exact

def diagnose_upwind_scheme(rho_exact, u_exact, p_exact):
    """诊断迎风格式实现"""
    print("\n" + "=" * 80)
    print("诊断2: 迎风格式实现验证")
    print("=" * 80)
    
    gamma = 1.4
    t_final = 0.2
    N = 400
    x = np.linspace(0, 1, N)
    dx = 1.0 / (N - 1)
    cfl = 0.8
    
    # 初始化
    U = initialize_flow(x, gamma)
    
    print(f"初始状态检查:")
    rho_0, u_0, p_0 = conservative_to_primitive(U, gamma)
    print(f"  左半部分 (x=0.25): rho={rho_0[100]:.6f}, u={u_0[100]:.6f}, p={p_0[100]:.6f}")
    print(f"  右半部分 (x=0.75): rho={rho_0[300]:.6f}, u={u_0[300]:.6f}, p={p_0[300]:.6f}")
    
    # 时间推进
    t = 0.0
    n_steps = 0
    U_initial = U.copy()
    
    while t < t_final:
        dt = compute_dt(U, dx, cfl, gamma)
        if t + dt > t_final:
            dt = t_final - t
        
        U_new = upwind_step(U, dx, dt, gamma)
        U_new = apply_boundary_condition(U_new)
        U = U_new
        t += dt
        n_steps += 1
    
    print(f"\n求解完成:")
    print(f"  总步数: {n_steps}")
    print(f"  最终时间: {t:.6f}")
    
    # 获取数值解
    rho_num, u_num, p_num = conservative_to_primitive(U, gamma)
    
    # 检查接触间断附近
    contact_idx = np.argmin(np.abs(x - 0.685))
    print(f"\n接触间断附近 (x≈{x[contact_idx]:.4f}):")
    print(f"  数值解: rho={rho_num[contact_idx]:.6f}, u={u_num[contact_idx]:.6f}, p={p_num[contact_idx]:.6f}")
    print(f"  精确解: rho={rho_exact[contact_idx]:.6f}, u={u_exact[contact_idx]:.6f}, p={p_exact[contact_idx]:.6f}")
    print(f"  误差:   drho={abs(rho_num[contact_idx]-rho_exact[contact_idx]):.6f}, du={abs(u_num[contact_idx]-u_exact[contact_idx]):.6f}, dp={abs(p_num[contact_idx]-p_exact[contact_idx]):.6f}")
    
    # 检查稀疏波区域
    rarefaction_idx = np.argmin(np.abs(x - 0.3))
    print(f"\n稀疏波区域 (x≈{x[rarefaction_idx]:.4f}):")
    print(f"  数值解: rho={rho_num[rarefaction_idx]:.6f}, u={u_num[rarefaction_idx]:.6f}, p={p_num[rarefaction_idx]:.6f}")
    print(f"  精确解: rho={rho_exact[rarefaction_idx]:.6f}, u={u_exact[rarefaction_idx]:.6f}, p={p_exact[rarefaction_idx]:.6f}")
    print(f"  误差:   drho={abs(rho_num[rarefaction_idx]-rho_exact[rarefaction_idx]):.6f}, du={abs(u_num[rarefaction_idx]-u_exact[rarefaction_idx]):.6f}, dp={abs(p_num[rarefaction_idx]-p_exact[rarefaction_idx]):.6f}")
    
    # 检查激波位置
    shock_idx = np.argmin(np.abs(x - 0.85))
    print(f"\n激波位置附近 (x≈{x[shock_idx]:.4f}):")
    print(f"  数值解: rho={rho_num[shock_idx]:.6f}, u={u_num[shock_idx]:.6f}, p={p_num[shock_idx]:.6f}")
    print(f"  精确解: rho={rho_exact[shock_idx]:.6f}, u={u_exact[shock_idx]:.6f}, p={p_exact[shock_idx]:.6f}")
    print(f"  误差:   drho={abs(rho_num[shock_idx]-rho_exact[shock_idx]):.6f}, du={abs(u_num[shock_idx]-u_exact[shock_idx]):.6f}, dp={abs(p_num[shock_idx]-p_exact[shock_idx]):.6f}")
    
    # 计算L1误差
    dx = 1.0 / (N - 1)
    l1_rho = np.sum(np.abs(rho_num - rho_exact)) * dx
    l1_u = np.sum(np.abs(u_num - u_exact)) * dx
    l1_p = np.sum(np.abs(p_num - p_exact)) * dx
    
    print(f"\nL1误差:")
    print(f"  L1(rho) = {l1_rho:.6e}")
    print(f"  L1(u)   = {l1_u:.6e}")
    print(f"  L1(p)   = {l1_p:.6e}")
    
    # 保存数据用于绘图
    np.save('results/data/upwind_N400_diag.npy', U)
    np.save('results/data/exact_N400_diag.npy', np.column_stack([rho_exact, u_exact, p_exact]))
    
    return U, x

def check_flux_computation():
    """检查通量计算是否正确"""
    print("\n" + "=" * 80)
    print("诊断3: 通量计算验证")
    print("=" * 80)
    
    gamma = 1.4
    
    # 测试左态
    U_L = np.array([1.0, 0.0, 2.5])  # rho=1, u=0, E=2.5
    F_L = compute_flux(U_L, gamma)
    print(f"左态 U = {U_L}")
    print(f"  F(U) = {F_L}")
    print(f"  预期: [0, p, 0] = [0, {0.4*1.0*2.5:.2f}, 0]")
    
    # 测试右态
    U_R = np.array([0.125, 0.0, 0.625])  # rho=0.125, u=0, E=0.625
    F_R = compute_flux(U_R, gamma)
    print(f"\n右态 U = {U_R}")
    print(f"  F(U) = {F_R}")
    print(f"  预期: [0, p, 0] = [0, {0.4*0.125*0.625:.4f}, 0]")

def check_upwind_implementation():
    """检查迎风格式的具体实现细节"""
    print("\n" + "=" * 80)
    print("诊断4: 迎风格式实现细节检查")
    print("=" * 80)
    
    from src.fd_schemes import steger_warming_flux
    
    gamma = 1.4
    
    # 测试简单状态
    U = np.array([
        [1.0, 0.0, 2.5],
        [0.5, 0.0, 1.25]
    ])
    
    print("测试状态:")
    print(f"  U[0] = {U[0]}")
    print(f"  U[1] = {U[1]}")
    
    F_pos, F_neg = steger_warming_flux(U, gamma)
    
    print(f"\nSteger-Warming分裂:")
    print(f"  F_pos[0] = {F_pos[0]}")
    print(f"  F_neg[0] = {F_neg[0]}")
    print(f"  F_total[0] = {F_pos[0] + F_neg[0]}")
    print(f"  compute_flux = {compute_flux(U[0], gamma)}")
    print(f"  差异: {np.max(np.abs(F_pos[0] + F_neg[0] - compute_flux(U[0], gamma)))}")
    
    # 检查迎风格式的离散公式
    print(f"\n迎风格式离散公式:")
    print(f"  U_i^{n+1} = U_i^n - (dt/dx) * [(F⁺_i - F⁺_{{i-1}}) + (F⁻_{{i+1}} - F⁻_i)]")
    print(f"  这是Steger-Warming FVS的标准公式 (Laney 1998, Ch.13)")

if __name__ == "__main__":
    print("开始诊断Sod激波管求解器...")
    print()
    
    # 诊断1: 精确解
    rho_exact, u_exact, p_exact = diagnose_exact_solver()
    
    # 诊断2: 迎风格式
    U_final, x = diagnose_upwind_scheme(rho_exact, u_exact, p_exact)
    
    # 诊断3: 通量计算
    check_flux_computation()
    
    # 诊断4: 迎风格式实现细节
    check_upwind_implementation()
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)
