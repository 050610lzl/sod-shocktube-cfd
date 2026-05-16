"""
验证与可视化模块 (validation.py)
=================================
实现数值解与精确解的对比分析、误差计算、结果可视化。

文献依据:
- 对比方法: Sod (1978) [1]
- 误差分析: Laney (1998) [3]
- 可视化规范: Build文档 §6.4
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from utils import sod_exact_solution, conservative_to_primitive, GAMMA


# =============================================================================
# 误差计算模块
# 依据: Laney (1998) [3], Build文档 §6.2
# =============================================================================
def compute_l2_error(numerical, exact):
    """
    计算L2范数误差。

    公式: L2 = sqrt(1/N * sum((num - exact)^2))

    参数:
        numerical: 数值解数组
        exact: 精确解数组

    返回:
        l2_error: L2误差值
    """
    return np.sqrt(np.mean((numerical - exact) ** 2))


def compute_l1_error(numerical, exact):
    """
    计算L1范数误差。

    公式: L1 = 1/N * sum(|num - exact|)

    参数:
        numerical: 数值解数组
        exact: 精确解数组

    返回:
        l1_error: L1误差值
    """
    return np.mean(np.abs(numerical - exact))


def compute_linf_error(numerical, exact):
    """
    计算L∞范数误差 (最大误差)。

    公式: L∞ = max(|num - exact|)

    参数:
        numerical: 数值解数组
        exact: 精确解数组

    返回:
        linf_error: L∞误差值
    """
    return np.max(np.abs(numerical - exact))


def compute_all_errors(U, x, t, gamma=GAMMA):
    """
    计算数值解与精确解的所有误差指标。

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        x: 网格坐标数组
        t: 仿真时刻
        gamma: 比热比

    返回:
        errors: 误差字典, 包含各物理量的L1/L2/L∞误差
    """
    # 提取原始变量
    rho_num, u_num, p_num = conservative_to_primitive(U, gamma)

    # 计算精确解
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t, gamma)

    # 计算误差
    errors = {
        'rho': {
            'L1': compute_l1_error(rho_num, rho_exact),
            'L2': compute_l2_error(rho_num, rho_exact),
            'Linf': compute_linf_error(rho_num, rho_exact)
        },
        'u': {
            'L1': compute_l1_error(u_num, u_exact),
            'L2': compute_l2_error(u_num, u_exact),
            'Linf': compute_linf_error(u_num, u_exact)
        },
        'p': {
            'L1': compute_l1_error(p_num, p_exact),
            'L2': compute_l2_error(p_num, p_exact),
            'Linf': compute_linf_error(p_num, p_exact)
        }
    }

    return errors


# =============================================================================
# 可视化模块
# 依据: Build文档 §6.4, Sod (1978) [1]
# =============================================================================
def plot_comparison(x, U, t, scheme_name, save_dir='results/figures', gamma=GAMMA):
    """
    绘制数值解与精确解的对比图 (密度/速度/压力)。

    参数:
        x: 网格坐标数组
        U: 守恒变量数组
        t: 仿真时刻
        scheme_name: 格式名称
        save_dir: 图表保存目录
        gamma: 比热比
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    # 提取原始变量
    rho_num, u_num, p_num = conservative_to_primitive(U, gamma)

    # 计算精确解
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t, gamma)

    # 设置绘图风格
    plt.rcParams.update({
        'font.size': 12,
        'axes.linewidth': 1.5,
        'lines.linewidth': 2,
        'lines.markersize': 4
    })

    # ---- 密度对比图 ----
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(x, rho_exact, 'k-', linewidth=2, label='Exact Solution')
    ax1.plot(x, rho_num, 'r--', linewidth=1.5, label=f'{scheme_name} (N={len(x)})')
    ax1.set_xlabel('Position x', fontsize=13)
    ax1.set_ylabel('Density $\\rho$', fontsize=13)
    ax1.set_title(f'Density Comparison - {scheme_name} (t={t:.2f})', fontsize=14)
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1.1)
    plt.tight_layout()
    fig1.savefig(os.path.join(save_dir, f'density_{scheme_name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig1)

    # ---- 速度对比图 ----
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(x, u_exact, 'k-', linewidth=2, label='Exact Solution')
    ax2.plot(x, u_num, 'b--', linewidth=1.5, label=f'{scheme_name} (N={len(x)})')
    ax2.set_xlabel('Position x', fontsize=13)
    ax2.set_ylabel('Velocity $u$', fontsize=13)
    ax2.set_title(f'Velocity Comparison - {scheme_name} (t={t:.2f})', fontsize=14)
    ax2.legend(loc='best', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.05, 0.35)
    plt.tight_layout()
    fig2.savefig(os.path.join(save_dir, f'velocity_{scheme_name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig2)

    # ---- 压力对比图 ----
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    ax3.plot(x, p_exact, 'k-', linewidth=2, label='Exact Solution')
    ax3.plot(x, p_num, 'g--', linewidth=1.5, label=f'{scheme_name} (N={len(x)})')
    ax3.set_xlabel('Position x', fontsize=13)
    ax3.set_ylabel('Pressure $p$', fontsize=13)
    ax3.set_title(f'Pressure Comparison - {scheme_name} (t={t:.2f})', fontsize=14)
    ax3.legend(loc='best', fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1.1)
    plt.tight_layout()
    fig3.savefig(os.path.join(save_dir, f'pressure_{scheme_name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig3)

    print(f"  对比图已保存至: {save_dir}")


def plot_all_schemes_comparison(results_dict, x, t, save_dir='results/figures', gamma=GAMMA):
    """
    绘制所有格式的对比图 (叠加在同一张图上)。

    参数:
        results_dict: 字典 {scheme_name: U_array}
        x: 网格坐标数组
        t: 仿真时刻
        save_dir: 图表保存目录
        gamma: 比热比
    """
    os.makedirs(save_dir, exist_ok=True)

    # 计算精确解
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t, gamma)

    # 颜色映射
    colors = {'lax_friedrichs': 'red', 'lax_wendroff': 'blue',
              'macormack': 'green', 'upwind': 'purple'}
    linestyles = {'lax_friedrichs': '--', 'lax_wendroff': '-.',
                  'macormack': ':', 'upwind': '--'}

    plt.rcParams.update({
        'font.size': 12,
        'axes.linewidth': 1.5,
        'lines.linewidth': 2
    })

    # ---- 密度叠加对比图 ----
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, rho_exact, 'k-', linewidth=2.5, label='Exact Solution')
    for name, U in results_dict.items():
        rho_num, _, _ = conservative_to_primitive(U, gamma)
        color = colors.get(name, 'gray')
        ls = linestyles.get(name, '--')
        ax.plot(x, rho_num, color=color, linestyle=ls, linewidth=1.5,
                label=f'{name} (N={len(x)})')
    ax.set_xlabel('Position x', fontsize=13)
    ax.set_ylabel('Density $\\rho$', fontsize=13)
    ax.set_title(f'Density Comparison - All Schemes (t={t:.2f})', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    plt.tight_layout()
    fig.savefig(os.path.join(save_dir, 'density_all_schemes.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ---- 速度叠加对比图 ----
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, u_exact, 'k-', linewidth=2.5, label='Exact Solution')
    for name, U in results_dict.items():
        _, u_num, _ = conservative_to_primitive(U, gamma)
        color = colors.get(name, 'gray')
        ls = linestyles.get(name, '--')
        ax.plot(x, u_num, color=color, linestyle=ls, linewidth=1.5,
                label=f'{name} (N={len(x)})')
    ax.set_xlabel('Position x', fontsize=13)
    ax.set_ylabel('Velocity $u$', fontsize=13)
    ax.set_title(f'Velocity Comparison - All Schemes (t={t:.2f})', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.05, 0.35)
    plt.tight_layout()
    fig.savefig(os.path.join(save_dir, 'velocity_all_schemes.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ---- 压力叠加对比图 ----
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, p_exact, 'k-', linewidth=2.5, label='Exact Solution')
    for name, U in results_dict.items():
        _, _, p_num = conservative_to_primitive(U, gamma)
        color = colors.get(name, 'gray')
        ls = linestyles.get(name, '--')
        ax.plot(x, p_num, color=color, linestyle=ls, linewidth=1.5,
                label=f'{name} (N={len(x)})')
    ax.set_xlabel('Position x', fontsize=13)
    ax.set_ylabel('Pressure $p$', fontsize=13)
    ax.set_title(f'Pressure Comparison - All Schemes (t={t:.2f})', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    plt.tight_layout()
    fig.savefig(os.path.join(save_dir, 'pressure_all_schemes.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"  叠加对比图已保存至: {save_dir}")


# =============================================================================
# 误差报告生成
# 依据: Build文档 §6.2-6.3
# =============================================================================
def generate_error_report(all_errors, save_dir='results'):
    """
    生成误差报告表格。

    参数:
        all_errors: 字典 {scheme_name: errors_dict}
        save_dir: 报告保存目录
    """
    os.makedirs(save_dir, exist_ok=True)

    # 打印到控制台
    print("\n" + "=" * 80)
    print("误差分析报告 (L1 / L2 / L∞)")
    print("=" * 80)
    print(f"{'格式':<20} | {'物理量':<8} | {'L1':<12} | {'L2':<12} | {'L∞':<12}")
    print("-" * 80)

    for scheme, errors in all_errors.items():
        for var in ['rho', 'u', 'p']:
            print(f"{scheme:<20} | {var:<8} | {errors[var]['L1']:<12.6e} | "
                  f"{errors[var]['L2']:<12.6e} | {errors[var]['Linf']:<12.6e}")
        print("-" * 80)

    # 保存为CSV
    csv_path = os.path.join(save_dir, 'error_report.csv')
    with open(csv_path, 'w') as f:
        f.write("Scheme,Variable,L1_Error,L2_Error,Linf_Error\n")
        for scheme, errors in all_errors.items():
            for var in ['rho', 'u', 'p']:
                f.write(f"{scheme},{var},{errors[var]['L1']:.6e},"
                        f"{errors[var]['L2']:.6e},{errors[var]['Linf']:.6e}\n")

    print(f"\n误差报告已保存至: {csv_path}")
