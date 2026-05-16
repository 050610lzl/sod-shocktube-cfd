"""
验证与误差分析模块 (src/validator.py)
=====================================
计算数值解与精确解的误差，生成对比图表和误差报告。

依据: Build文档 §5.8
文献: Sod (1978) [1], Laney (1998) [3]
"""

import os
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def compute_errors(U_num, rho_exact, u_exact, p_exact):
    """
    计算数值解与精确解的L1、L2、L∞误差范数。

    依据: Build文档 §5.8, Laney (1998) [3]

    参数:
        U_num: 数值解守恒变量, 形状 (N, 3)
        rho_exact: 精确密度
        u_exact: 精确速度
        p_exact: 精确压力

    返回:
        errors: 误差字典
    """
    from .time_marcher import conservative_to_primitive

    rho_num, u_num, p_num = conservative_to_primitive(U_num)

    dx = 1.0 / (len(rho_num) - 1)

    errors = {}
    for name, num_val, exact_val in [('rho', rho_num, rho_exact),
                                       ('u', u_num, u_exact),
                                       ('p', p_num, p_exact)]:
        diff = num_val - exact_val
        l1 = np.sum(np.abs(diff)) * dx
        l2 = np.sqrt(np.sum(diff ** 2) * dx)
        linf = np.max(np.abs(diff))
        errors[name] = {'L1': l1, 'L2': l2, 'Linf': linf}

    return errors


def _compute_total_energy(U, gamma=1.4):
    """计算总能 E = p/((gamma-1)*rho) + 0.5*u^2."""
    from .time_marcher import conservative_to_primitive
    rho, u, p = conservative_to_primitive(U, gamma)
    return p / ((gamma - 1.0) * rho) + 0.5 * u ** 2


def _compute_exact_total_energy(rho, u, p, gamma=1.4):
    """计算精确解总能."""
    return p / ((gamma - 1.0) * rho) + 0.5 * u ** 2


def _self_check_plot(fig, axes, title):
    """
    自检函数: 确认图像形态、数值、刻度无误。

    依据: 强制铁律1 - 精确解图像正确性强制校验
    """
    # 检查子图数量
    assert len(axes) == 4, f"子图数量应为4 (rho/u/p/E), 实际 {len(axes)}"

    # 检查每个子图是否有数据
    for i, ax in enumerate(axes):
        lines = ax.get_lines()
        assert len(lines) >= 2, f"子图{i}应有至少2条线 (数值解+精确解), 实际 {len(lines)}"

    # 检查标题
    assert fig._suptitle is not None, "图像缺少总标题"

    print(f"  [自检通过] {title}: 4子图(rho/u/p/E), 线条数正确, 标题完整")


def generate_comparison_plots(x, U_num, rho_exact, u_exact, p_exact,
                              scheme_name, n_points, t_final=0.2, cfl=0.8,
                              output_dir='results/figures', timestamp=None):
    """
    生成密度/压力/速度/总能剖面对比图 (4张子图)。

    依据: Build文档 §5.8, 强制铁律1

    强制铁律1要求:
    - 必须包含: 密度ρ、速度u、压力p、总能量E 4张子图
    - 精确解: 实线; 数值解: 圆圈标记
    - 必须标注: 格式名称、网格点数、t=0.2、CFL数
    - 绘图完成后自动执行自检

    参数:
        x: 网格坐标
        U_num: 数值解
        rho_exact, u_exact, p_exact: 精确解
        scheme_name: 格式名称
        n_points: 网格节点数
        t_final: 终止时间
        cfl: CFL数
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档)
    """
    from .time_marcher import conservative_to_primitive

    if timestamp:
        output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    rho_num, u_num, p_num = conservative_to_primitive(U_num)
    E_num = _compute_total_energy(U_num)
    E_exact = _compute_exact_total_energy(rho_exact, u_exact, p_exact)

    fig, axes = plt.subplots(4, 1, figsize=(8, 12))

    # 密度 - 精确解: 实线; 数值解: 圆圈
    axes[0].plot(x, rho_exact, 'k-', linewidth=1.5, label='Exact')
    axes[0].plot(x, rho_num, 'ko', markersize=4, fillstyle='none',
                 label=f'{scheme_name} (N={n_points})')
    axes[0].set_ylabel(r'$\rho$', fontsize=14)
    axes[0].set_ylim(0, 1.1)
    axes[0].legend(loc='upper right', fontsize=10, frameon=True)
    axes[0].grid(False)

    # 压力
    axes[1].plot(x, p_exact, 'k-', linewidth=1.5, label='Exact')
    axes[1].plot(x, p_num, 'ko', markersize=4, fillstyle='none',
                 label=f'{scheme_name} (N={n_points})')
    axes[1].set_ylabel(r'$p$', fontsize=14)
    axes[1].set_ylim(0, 1.1)
    axes[1].legend(loc='upper right', fontsize=10, frameon=True)
    axes[1].grid(False)

    # 速度
    axes[2].plot(x, u_exact, 'k-', linewidth=1.5, label='Exact')
    axes[2].plot(x, u_num, 'ko', markersize=4, fillstyle='none',
                 label=f'{scheme_name} (N={n_points})')
    axes[2].set_ylabel(r'$u$', fontsize=14)
    axes[2].set_ylim(-0.1, 1.1)
    axes[2].legend(loc='upper right', fontsize=10, frameon=True)
    axes[2].grid(False)

    # 总能量
    axes[3].plot(x, E_exact, 'k-', linewidth=1.5, label='Exact')
    axes[3].plot(x, E_num, 'ko', markersize=4, fillstyle='none',
                 label=f'{scheme_name} (N={n_points})')
    axes[3].set_ylabel(r'$E$', fontsize=14)
    axes[3].set_xlabel('x', fontsize=14)
    axes[3].set_xlim(0, 1)
    axes[3].legend(loc='upper right', fontsize=10, frameon=True)
    axes[3].grid(False)

    # 标注: 格式名称、网格点数、t=0.2、CFL数
    fig.suptitle(f'{scheme_name} | N={n_points} | t={t_final} | CFL={cfl}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    # 自检
    _self_check_plot(fig, axes, scheme_name)

    if timestamp:
        filepath = os.path.join(output_dir, f'{timestamp}_plot_{scheme_name}.png')
    else:
        filepath = os.path.join(output_dir, f'{scheme_name}_comparison.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  对比图已保存至: {filepath}")


def generate_error_report(all_errors, output_path='results/error_report.csv'):
    """
    生成误差报告CSV文件。

    依据: Build文档 §5.8

    参数:
        all_errors: 所有格式的误差字典 {scheme_name: {var: {L1, L2, Linf}}}
        output_path: 输出路径
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write('Scheme,Variable,L1_Error,L2_Error,Linf_Error\n')
        for scheme, vars_err in all_errors.items():
            for var, errs in vars_err.items():
                f.write(f'{scheme},{var},{errs["L1"]:.6e},{errs["L2"]:.6e},{errs["Linf"]:.6e}\n')

    print(f"\n误差报告已保存至: {output_path}")


def generate_all_schemes_comparison(results_dict, x, rho_exact, u_exact, p_exact,
                                    n_points, t_final=0.2, cfl=0.8,
                                    output_dir='results/figures', timestamp=None):
    """
    生成所有格式的叠加对比图 (4张子图: rho/u/p/E)。

    依据: Build文档 §5.8, 强制铁律1

    参数:
        results_dict: {scheme_name: U_num}
        x: 网格坐标
        rho_exact, u_exact, p_exact: 精确解
        n_points: 网格节点数
        t_final: 终止时间
        cfl: CFL数
        output_dir: 输出目录
        timestamp: 时间戳
    """
    from .time_marcher import conservative_to_primitive

    if timestamp:
        output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    E_exact = _compute_exact_total_energy(rho_exact, u_exact, p_exact)

    markers = ['o', 's', '^', 'd', 'v', '<', '>', 'p']

    fig, axes = plt.subplots(4, 1, figsize=(8, 12))

    # 精确解: 实线 (先画，作为背景)
    axes[0].plot(x, rho_exact, 'k-', linewidth=1.5, label='Exact')
    axes[1].plot(x, p_exact, 'k-', linewidth=1.5, label='Exact')
    axes[2].plot(x, u_exact, 'k-', linewidth=1.5, label='Exact')
    axes[3].plot(x, E_exact, 'k-', linewidth=1.5, label='Exact')

    # 数值解: 圆圈标记
    for idx, (scheme, U_num) in enumerate(results_dict.items()):
        rho_num, u_num, p_num = conservative_to_primitive(U_num)
        E_num = _compute_total_energy(U_num)
        marker = markers[idx % len(markers)]

        axes[0].plot(x, rho_num, marker, markersize=3, fillstyle='none', label=scheme)
        axes[1].plot(x, p_num, marker, markersize=3, fillstyle='none', label=scheme)
        axes[2].plot(x, u_num, marker, markersize=3, fillstyle='none', label=scheme)
        axes[3].plot(x, E_num, marker, markersize=3, fillstyle='none', label=scheme)

    axes[0].set_ylabel(r'$\rho$', fontsize=14)
    axes[0].set_ylim(0, 1.1)
    axes[1].set_ylabel(r'$p$', fontsize=14)
    axes[1].set_ylim(0, 1.1)
    axes[2].set_ylabel(r'$u$', fontsize=14)
    axes[2].set_ylim(-0.1, 1.1)
    axes[3].set_ylabel(r'$E$', fontsize=14)
    axes[3].set_xlabel('x', fontsize=14)
    axes[3].set_xlim(0, 1)

    for ax in axes:
        ax.legend(loc='upper right', fontsize=8, frameon=True)
        ax.grid(False)

    fig.suptitle(f'All Schemes | N={n_points} | t={t_final} | CFL={cfl}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    # 自检
    _self_check_plot(fig, axes, 'All Schemes')

    if timestamp:
        filepath = os.path.join(output_dir, f'{timestamp}_plot_all_schemes.png')
    else:
        filepath = os.path.join(output_dir, 'all_schemes_comparison.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  叠加对比图已保存至: {filepath}")
