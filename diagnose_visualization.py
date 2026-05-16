"""
详细诊断和可视化：验证迎风格式和精确解
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

from src.exact_solver import sod_exact_solution
from src.fd_schemes import conservative_to_primitive, upwind_step
from src.boundary_handler import apply_boundary_condition
from src.flow_initializer import initialize_flow
from src.time_marcher import compute_dt

def run_upwind_detailed():
    """运行迎风格式并获取详细数据"""
    gamma = 1.4
    t_final = 0.2
    N = 400
    x = np.linspace(0, 1, N)
    dx = 1.0 / (N - 1)
    cfl = 0.8
    
    # 初始化
    U = initialize_flow(x, gamma)
    
    # 时间推进
    t = 0.0
    n_steps = 0
    
    while t < t_final:
        dt = compute_dt(U, dx, cfl, gamma)
        if t + dt > t_final:
            dt = t_final - t
        
        U_new = upwind_step(U, dx, dt, gamma)
        U_new = apply_boundary_condition(U_new)
        U = U_new
        t += dt
        n_steps += 1
    
    rho_num, u_num, p_num = conservative_to_primitive(U, gamma)
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t_final, gamma)
    
    return x, rho_num, u_num, p_num, rho_exact, u_exact, p_exact

def plot_comparison():
    """生成详细的对比图"""
    x, rho_num, u_num, p_num, rho_exact, u_exact, p_exact = run_upwind_detailed()
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    # 密度
    axes[0].plot(x, rho_exact, 'k-', linewidth=2, label='Exact')
    axes[0].plot(x, rho_num, 'b-', linewidth=1, alpha=0.7, label='Upwind (N=400)')
    axes[0].set_ylabel(r'$\rho$', fontsize=14)
    axes[0].set_ylim(0, 1.1)
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 速度
    axes[1].plot(x, u_exact, 'k-', linewidth=2, label='Exact')
    axes[1].plot(x, u_num, 'r-', linewidth=1, alpha=0.7, label='Upwind (N=400)')
    axes[1].set_ylabel(r'$u$', fontsize=14)
    axes[1].set_ylim(-0.1, 1.1)
    axes[1].legend(loc='upper right', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    # 压力
    axes[2].plot(x, p_exact, 'k-', linewidth=2, label='Exact')
    axes[2].plot(x, p_num, 'g-', linewidth=1, alpha=0.7, label='Upwind (N=400)')
    axes[2].set_ylabel(r'$p$', fontsize=14)
    axes[2].set_xlabel('x', fontsize=14)
    axes[2].set_ylim(0, 1.1)
    axes[2].legend(loc='upper right', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    
    fig.suptitle('Sod Shock Tube - Upwind vs Exact Solution (N=400, t=0.2)',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filepath = 'docs/wave_structure_detailed.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"详细对比图已保存至: {filepath}")
    
    # 计算关键位置的误差
    contact_idx = np.argmin(np.abs(x - 0.685))
    shock_idx = np.argmin(np.abs(x - 0.85))
    
    print("\n" + "=" * 80)
    print("关键位置详细分析:")
    print("=" * 80)
    print(f"\n接触间断附近 (x={x[contact_idx]:.4f}):")
    print(f"  精确解: rho={rho_exact[contact_idx]:.4f}, u={u_exact[contact_idx]:.4f}, p={p_exact[contact_idx]:.4f}")
    print(f"  数值解: rho={rho_num[contact_idx]:.4f}, u={u_num[contact_idx]:.4f}, p={p_num[contact_idx]:.4f}")
    print(f"  相对误差: drho={abs(rho_num[contact_idx]-rho_exact[contact_idx])/rho_exact[contact_idx]*100:.1f}%, "
          f"du={abs(u_num[contact_idx]-u_exact[contact_idx])/u_exact[contact_idx]*100:.1f}%, "
          f"dp={abs(p_num[contact_idx]-p_exact[contact_idx])/p_exact[contact_idx]*100:.1f}%")
    
    print(f"\n激波位置附近 (x={x[shock_idx]:.4f}):")
    print(f"  精确解: rho={rho_exact[shock_idx]:.4f}, u={u_exact[shock_idx]:.4f}, p={p_exact[shock_idx]:.4f}")
    print(f"  数值解: rho={rho_num[shock_idx]:.4f}, u={u_num[shock_idx]:.4f}, p={p_num[shock_idx]:.4f}")
    print(f"  相对误差: drho={abs(rho_num[shock_idx]-rho_exact[shock_idx])/rho_exact[shock_idx]*100:.1f}%, "
          f"du={abs(u_num[shock_idx]-u_exact[shock_idx])/u_exact[shock_idx]*100:.1f}%, "
          f"dp={abs(p_num[shock_idx]-p_exact[shock_idx])/p_exact[shock_idx]*100:.1f}%")

if __name__ == "__main__":
    plot_comparison()
