"""
网格生成模块 (src/mesh_generator.py)
====================================
生成一维均匀网格，用于Sod激波管问题求解。

依据: Build文档 §5.1
文献: Laney (1998) [3]
"""

import numpy as np


def generate_mesh(n_points=100, x_left=0.0, x_right=1.0):
    """
    生成一维均匀网格。

    依据: Build文档 §5.1, Laney (1998) [3]

    参数:
        n_points: 网格节点数 (默认100)
        x_left: 左边界坐标 (默认0.0)
        x_right: 右边界坐标 (默认1.0)

    返回:
        x: 网格坐标数组, 形状 (N,)
        dx: 网格间距 (标量)
    """
    x = np.linspace(x_left, x_right, n_points)
    dx = x[1] - x[0]
    return x, dx
