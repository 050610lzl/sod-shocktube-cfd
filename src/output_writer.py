"""
结果输出模块 (src/output_writer.py)
===================================
保存数值解数据、精确解数据到指定路径。

依据: Build文档 §5.7
强制铁律2: 按时间戳归档数据与图片
"""

import os
import numpy as np


def save_results(U, x, scheme_name, n_points, output_dir='results/data',
                 timestamp=None, seq=None):
    """
    保存数值解数据到.npy文件。

    依据: Build文档 §5.7, 强制铁律2

    强制铁律2要求:
    - 按时间戳创建文件夹
    - 数据文件命名: 时间戳_data_序号.npy

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        x: 网格坐标数组
        scheme_name: 格式名称
        n_points: 网格节点数
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档)
        seq: 序号 (用于归档)
    """
    if timestamp:
        output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    if timestamp and seq is not None:
        filepath = os.path.join(output_dir, f'{timestamp}_data_{seq}.npy')
    else:
        filepath = os.path.join(output_dir, f'{scheme_name}_N{n_points}.npy')

    np.save(filepath, {'x': x, 'U': U})
    print(f"  {scheme_name}: 已保存至 {filepath}")


def save_exact_solution(rho, u, p, x, n_points, output_dir='results/exact',
                        timestamp=None):
    """
    保存精确解数据到.npy文件。

    依据: Build文档 §5.7, 强制铁律2

    参数:
        rho: 精确密度
        u: 精确速度
        p: 精确压力
        x: 网格坐标
        n_points: 网格节点数
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档)
    """
    if timestamp:
        output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    if timestamp:
        filepath = os.path.join(output_dir, f'{timestamp}_data_exact.npy')
    else:
        filepath = os.path.join(output_dir, f'exact_solution_N{n_points}.npy')

    np.save(filepath, {'x': x, 'rho': rho, 'u': u, 'p': p})
    print(f"  精确解: 已保存至 {filepath}")
