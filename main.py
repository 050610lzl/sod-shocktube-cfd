"""
主程序入口 (main.py)
====================
一维Sod激波管CFD求解器 - 有限差分法

功能:
  使用多种有限差分格式求解一维Sod激波管问题,
  并将数值解与解析精确解进行对比验证。

文献依据:
  - 问题定义: Sod (1978) [1], OneFlow-CFD [4]
  - 数值格式: Sod (1978) [1], Laney (1998) [3], LeVeque (2002) [5]
  - 验证方法: Sod (1978) [1], Toro (2009) [2]

运行方式:
  python main.py                    # 使用默认参数运行所有格式
  python main.py --scheme upwind    # 仅运行指定格式
  python main.py --n_points 200     # 指定网格分辨率
"""

import argparse
import os
import numpy as np
from utils import (
    generate_mesh, initialize_flow, conservative_to_primitive,
    compute_flux, sod_exact_solution, GAMMA
)
from sod_solver import solve_sod, FD_SCHEMES
from validation import compute_all_errors, plot_comparison, plot_all_schemes_comparison, generate_error_report


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='一维Sod激波管CFD求解器 (有限差分法)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                        # 运行所有格式, N=100
  python main.py --scheme lax_friedrichs  # 仅运行Lax-Friedrichs格式
  python main.py --n_points 200          # N=200网格
  python main.py --cfl 0.9               # CFL=0.9
        """
    )

    parser.add_argument('--scheme', type=str, default='all',
                        choices=list(FD_SCHEMES.keys()) + ['all'],
                        help='选择求解格式 (默认: all, 运行所有格式)')
    parser.add_argument('--n_points', type=int, default=100,
                        help='网格节点数 (默认: 100)')
    parser.add_argument('--cfl', type=float, default=0.8,
                        help='CFL数 (默认: 0.8)')
    parser.add_argument('--t_final', type=float, default=0.2,
                        help='仿真终止时间 (默认: 0.2)')
    parser.add_argument('--gamma', type=float, default=1.4,
                        help='比热比 (默认: 1.4)')
    parser.add_argument('--output_dir', type=str, default='results',
                        help='输出目录 (默认: results)')

    return parser.parse_args()


def main():
    """主程序入口"""
    args = parse_arguments()

    print("=" * 60)
    print("一维Sod激波管CFD求解器 (有限差分法)")
    print("=" * 60)
    print(f"\n仿真参数:")
    print(f"  网格节点数: N = {args.n_points}")
    print(f"  CFL数:      CFL = {args.cfl}")
    print(f"  终止时间:   t_final = {args.t_final}")
    print(f"  比热比:     gamma = {args.gamma}")
    print()

    # ---- 步骤1: 网格生成 ----
    # 依据: Build文档 §5.1, Laney (1998) [3]
    print("[步骤1] 生成一维均匀网格...")
    x, dx = generate_mesh(n_points=args.n_points, x_left=0.0, x_right=1.0)
    print(f"  计算域: [0, 1], 节点数: {args.n_points}, 间距: dx = {dx:.6f}")

    # ---- 步骤2: 流场初始化 ----
    # 依据: Sod (1978) [1], OneFlow-CFD [4]
    print("\n[步骤2] 初始化流场...")
    U0 = initialize_flow(x, gamma=args.gamma, diaphragm_pos=0.5)
    rho0, u0, p0 = conservative_to_primitive(U0)
    print(f"  左态: rho=1.0, u=0.0, p=1.0")
    print(f"  右态: rho=0.125, u=0.0, p=0.1")
    print(f"  间断位置: x = 0.5")

    # ---- 步骤3: 时间迭代求解 ----
    # 依据: Build文档 §3.3, §5.5
    print("\n[步骤3] 时间迭代求解...")

    # 确定要运行的格式
    if args.scheme == 'all':
        schemes_to_run = list(FD_SCHEMES.keys())
    else:
        schemes_to_run = [args.scheme]

    results_dict = {}
    all_errors = {}

    for scheme_name in schemes_to_run:
        print(f"\n{'='*50}")
        U_final, t_final_actual, n_steps = solve_sod(
            scheme_name=scheme_name,
            x=x, dx=dx,
            U0=U0,
            t_final=args.t_final,
            cfl=args.cfl,
            gamma=args.gamma
        )

        results_dict[scheme_name] = U_final

        # ---- 步骤4: 误差计算 ----
        # 依据: Build文档 §6.2, Laney (1998) [3]
        print(f"\n[步骤4] 计算误差 ({scheme_name})...")
        errors = compute_all_errors(U_final, x, t_final_actual, args.gamma)
        all_errors[scheme_name] = errors

        # 打印误差摘要
        print(f"  密度误差: L1={errors['rho']['L1']:.6e}, L2={errors['rho']['L2']:.6e}")
        print(f"  速度误差: L1={errors['u']['L1']:.6e}, L2={errors['u']['L2']:.6e}")
        print(f"  压力误差: L1={errors['p']['L1']:.6e}, L2={errors['p']['L2']:.6e}")

        # ---- 步骤5: 可视化 ----
        # 依据: Build文档 §6.4
        print(f"\n[步骤5] 生成对比图 ({scheme_name})...")
        fig_dir = os.path.join(args.output_dir, 'figures')
        plot_comparison(x, U_final, t_final_actual, scheme_name, save_dir=fig_dir, gamma=args.gamma)

    # ---- 步骤6: 叠加对比图 ----
    if len(results_dict) > 1:
        print(f"\n[步骤6] 生成叠加对比图...")
        plot_all_schemes_comparison(results_dict, x, args.t_final,
                                    save_dir=fig_dir, gamma=args.gamma)

    # ---- 步骤7: 误差报告 ----
    print(f"\n[步骤7] 生成误差报告...")
    generate_error_report(all_errors, save_dir=args.output_dir)

    # ---- 步骤8: 保存数值解数据 ----
    print(f"\n[步骤8] 保存数值解数据...")
    data_dir = os.path.join(args.output_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    for scheme_name, U in results_dict.items():
        rho, u, p = conservative_to_primitive(U)
        save_path = os.path.join(data_dir, f'{scheme_name}_N{args.n_points}.npy')
        np.save(save_path, {
            'x': x,
            'U': U,
            'rho': rho,
            'u': u,
            'p': p,
            't': args.t_final
        })
        print(f"  {scheme_name}: 已保存至 {save_path}")

    # 保存精确解
    print(f"\n  保存精确解...")
    exact_dir = os.path.join(args.output_dir, 'exact')
    os.makedirs(exact_dir, exist_ok=True)
    rho_ex, u_ex, p_ex = sod_exact_solution(x, args.t_final, args.gamma)
    exact_path = os.path.join(exact_dir, f'exact_solution_N{args.n_points}.npy')
    np.save(exact_path, {
        'x': x,
        'rho': rho_ex,
        'u': u_ex,
        'p': p_ex,
        't': args.t_final
    })
    print(f"  精确解: 已保存至 {exact_path}")

    print("\n" + "=" * 60)
    print("求解完成!")
    print(f"  结果目录: {args.output_dir}/")
    print(f"    - 数据文件: {args.output_dir}/data/")
    print(f"    - 精确解:   {args.output_dir}/exact/")
    print(f"    - 对比图:   {args.output_dir}/figures/")
    print(f"    - 误差报告: {args.output_dir}/error_report.csv")
    print("=" * 60)


if __name__ == '__main__':
    main()
