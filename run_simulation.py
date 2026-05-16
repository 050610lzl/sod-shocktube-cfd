"""
主程序入口 (run_simulation.py)
==============================
流程编排: 按Build文档 §3.3 的仿真运行流程执行

依据: Build文档 §3.3
强制铁律2: 按时间戳归档数据与图片
"""

import os
import sys
import argparse
import yaml
import datetime
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow, GAMMA
from src.fd_schemes import FD_SCHEMES, solve_with_scheme
from src.exact_solver import sod_exact_solution
from src.output_writer import save_results, save_exact_solution
from src.validator import (
    compute_errors,
    generate_comparison_plots,
    generate_error_report,
    generate_all_schemes_comparison,
)


def load_config(config_path='config/simulation_config.yaml'):
    """加载配置文件。"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_simulation(config=None, scheme_list=None, n_points=None, cfl=None):
    """
    执行完整仿真流程。

    依据: Build文档 §3.3
    强制铁律2: 按时间戳归档数据与图片

    参数:
        config: 配置字典 (None则从文件加载)
        scheme_list: 要运行的格式列表
        n_points: 网格节点数 (覆盖配置)
        cfl: CFL数 (覆盖配置)
    """
    if config is None:
        config = load_config()

    # 提取参数
    mesh_cfg = config['mesh']
    phys_cfg = config['physics']
    sim_cfg = config['simulation']
    out_cfg = config['output']

    n_pts = n_points if n_points is not None else mesh_cfg['n_points']
    cfl_val = cfl if cfl is not None else sim_cfg['cfl']
    t_final = sim_cfg['t_final']
    gamma = phys_cfg['gamma']

    schemes = scheme_list if scheme_list is not None else config['schemes']

    # 强制铁律2: 生成时间戳
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"\n[时间戳归档] {timestamp}")
    print(f"  数据目录: results/data/{timestamp}/")
    print(f"  图片目录: results/figures/{timestamp}/")
    print(f"  精确解目录: results/exact/{timestamp}/")

    print("=" * 60)
    print("一维Sod激波管CFD求解器 (有限差分法)")
    print("=" * 60)
    print(f"\n仿真参数:")
    print(f"  网格节点数: N = {n_pts}")
    print(f"  CFL数:      CFL = {cfl_val}")
    print(f"  终止时间:   t_final = {t_final}")
    print(f"  比热比:     gamma = {gamma}")
    print()

    # 步骤1: 网格生成 (Build §3.3 步骤2)
    print("[步骤1] 生成一维均匀网格...")
    x, dx = generate_mesh(
        n_points=n_pts,
        x_left=mesh_cfg['x_left'],
        x_right=mesh_cfg['x_right']
    )
    print(f"  计算域: [{mesh_cfg['x_left']}, {mesh_cfg['x_right']}], "
          f"节点数: {n_pts}, 间距: dx = {dx:.6f}\n")

    # 步骤2: 流场初始化 (Build §3.3 步骤3)
    print("[步骤2] 初始化流场...")
    U0 = initialize_flow(
        x, gamma=gamma,
        diaphragm_pos=phys_cfg['diaphragm_pos'],
        left_state=phys_cfg['left_state'],
        right_state=phys_cfg['right_state']
    )
    print(f"  左态: rho={phys_cfg['left_state']['rho']}, "
          f"u={phys_cfg['left_state']['u']}, p={phys_cfg['left_state']['p']}")
    print(f"  右态: rho={phys_cfg['right_state']['rho']}, "
          f"u={phys_cfg['right_state']['u']}, p={phys_cfg['right_state']['p']}")
    print(f"  间断位置: x = {phys_cfg['diaphragm_pos']}\n")

    # 步骤3-5: 时间迭代求解 (Build §3.3 步骤4)
    print("[步骤3] 时间迭代求解...")
    all_results = {}
    all_errors = {}

    for seq, scheme_name in enumerate(schemes):
        print(f"\n{'=' * 50}")
        U_final, t_final_actual, n_steps = solve_with_scheme(
            scheme_name=scheme_name,
            U=U0, x=x, dx=dx,
            t_final=t_final, cfl=cfl_val, gamma=gamma
        )
        all_results[scheme_name] = U_final

        # 步骤4: 计算误差 (Build §3.3 步骤7)
        print(f"\n[步骤4] 计算误差 ({scheme_name})...")
        rho_exact, u_exact, p_exact = sod_exact_solution(x, t_final_actual, gamma)
        errors = compute_errors(U_final, rho_exact, u_exact, p_exact)
        all_errors[scheme_name] = errors

        for var, errs in errors.items():
            print(f"  {var}误差: L1={errs['L1']:.6e}, L2={errs['L2']:.6e}")

        # 步骤5: 生成对比图 (Build §3.3 步骤7, 强制铁律1+2)
        print(f"\n[步骤5] 生成对比图 ({scheme_name})...")
        generate_comparison_plots(
            x, U_final, rho_exact, u_exact, p_exact,
            scheme_name, n_pts, t_final_actual, cfl_val,
            output_dir=out_cfg['figures_dir'],
            timestamp=timestamp
        )

        # 保存数值解 (Build §3.3 步骤5, 强制铁律2)
        save_results(U_final, x, scheme_name, n_pts,
                     output_dir=out_cfg['data_dir'],
                     timestamp=timestamp, seq=seq)

    # 步骤6: 精确解计算与保存 (Build §3.3 步骤6, 强制铁律2)
    print(f"\n[步骤6] 保存精确解...")
    rho_exact, u_exact, p_exact = sod_exact_solution(x, t_final, gamma)
    save_exact_solution(rho_exact, u_exact, p_exact, x, n_pts,
                        output_dir=out_cfg['exact_dir'],
                        timestamp=timestamp)

    # 步骤7: 生成叠加对比图 (强制铁律1+2)
    print(f"\n[步骤7] 生成叠加对比图...")
    generate_all_schemes_comparison(
        all_results, x, rho_exact, u_exact, p_exact,
        n_pts, t_final, cfl_val,
        output_dir=out_cfg['figures_dir'],
        timestamp=timestamp
    )

    # 步骤8: 生成误差报告
    print(f"\n[步骤8] 生成误差报告...")
    generate_error_report(all_errors, out_cfg['error_report'])

    # 强制铁律2: 输出归档说明
    print("\n" + "=" * 60)
    print("求解完成!")
    print(f"\n[归档说明] 时间戳文件夹: {timestamp}")
    print(f"  数据文件: results/data/{timestamp}/")
    for seq, scheme_name in enumerate(schemes):
        print(f"    - {timestamp}_data_{seq}.npy  ({scheme_name})")
    print(f"    - {timestamp}_data_exact.npy  (精确解)")
    print(f"  图片文件: results/figures/{timestamp}/")
    for scheme_name in schemes:
        print(f"    - {timestamp}_plot_{scheme_name}.png")
    print(f"    - {timestamp}_plot_all_schemes.png")
    print(f"  误差报告: {out_cfg['error_report']}")
    print("=" * 60)


def main():
    """命令行入口。"""
    parser = argparse.ArgumentParser(description='一维Sod激波管CFD求解器 (有限差分法)')
    parser.add_argument('--config', type=str, default='config/simulation_config.yaml',
                        help='配置文件路径')
    parser.add_argument('--n_points', type=int, default=None,
                        help='网格节点数 (覆盖配置文件)')
    parser.add_argument('--cfl', type=float, default=None,
                        help='CFL数 (覆盖配置文件)')
    parser.add_argument('--scheme', type=str, default=None,
                        help='指定单个格式运行 (lax_friedrichs/lax_wendroff/macormack/upwind)')
    parser.add_argument('--schemes', type=str, nargs='+', default=None,
                        help='指定多个格式运行')

    args = parser.parse_args()

    config = load_config(args.config)

    scheme_list = None
    if args.scheme:
        scheme_list = [args.scheme]
    elif args.schemes:
        scheme_list = args.schemes

    run_simulation(config=config, scheme_list=scheme_list,
                   n_points=args.n_points, cfl=args.cfl)


if __name__ == '__main__':
    main()
