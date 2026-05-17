"""
边界处理模块 (src/boundary_handler.py)
======================================
实现多种边界条件类型:
  1. zero_gradient  (零梯度/外推, 默认)
  2. reflective     (固壁反射)
  3. periodic       (周期)
  4. transmissive   (无反射/透射)

依据: Build文档 §5.4
文献: Laney (1998) [3], LeVeque (1992) [5], Anderson (1984) [2], OneFlow-CFD [4]
"""

import numpy as np

# 支持的边界条件类型注册表
# 依据: Laney (1998) [3] §5.4 - 边界条件分类
BOUNDARY_TYPES = {
    'zero_gradient': {
        'description': '零梯度/外推边界条件',
        'reference': 'Laney (1998) [3], OneFlow-CFD [4]'
    },
    'reflective': {
        'description': '固壁反射边界条件 (法向速度反号)',
        'reference': 'Anderson (1984) [2], LeVeque (1992) [5]'
    },
    'periodic': {
        'description': '周期边界条件',
        'reference': 'LeVeque (1992) [5], Laney (1998) [3]'
    },
    'transmissive': {
        'description': '无反射/透射边界条件 (高阶外推)',
        'reference': 'LeVeque (1992) [5], Anderson (1984) [2]'
    }
}


def apply_boundary_condition(U, bc_type='zero_gradient'):
    """
    施加指定类型的边界条件。

    依据: Build文档 §5.4, Laney (1998) [3], LeVeque (1992) [5]

    支持4种边界条件类型:
    - 'zero_gradient'  (零梯度/外推, 默认):
        左边界: U[0] = U[1]
        右边界: U[N-1] = U[N-2]
        依据: Laney (1998) [3] §5.4.1

    - 'reflective'  (固壁反射):
        左边界: rho[0]=rho[1], u[0]=-u[1], E[0]=E[1], 即 U[0,1]=-U[1,1]
        右边界: rho[-1]=rho[-2], u[-1]=-u[-2], E[-1]=E[-2], 即 U[-1,1]=-U[-2,1]
        依据: Anderson (1984) [2] §6.3, LeVeque (1992) [5] §7.1

    - 'periodic'  (周期):
        左边界: U[0] = U[-2]
        右边界: U[-1] = U[1]
        依据: LeVeque (1992) [5] §7.1, Laney (1998) [3] §5.4.2

    - 'transmissive'  (无反射/透射, 高阶外推):
        左边界: U[0] = 2*U[1] - U[2]  (线性外推)
        右边界: U[-1] = 2*U[-2] - U[-3]
        依据: LeVeque (1992) [5] §7.1, Anderson (1984) [2] §6.4

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        bc_type: 边界条件类型 (默认 'zero_gradient')

    返回:
        U: 施加边界条件后的数组 (原地修改)
    """
    if bc_type not in BOUNDARY_TYPES:
        raise ValueError(
            f"未知边界条件类型: '{bc_type}'. "
            f"可选类型: {list(BOUNDARY_TYPES.keys())}"
        )

    if bc_type == 'zero_gradient':
        # 零梯度外推: U[0] = U[1], U[N-1] = U[N-2]
        # 依据: Laney (1998) [3] §5.4.1, OneFlow-CFD [4]
        U[0, :] = U[1, :]
        U[-1, :] = U[-2, :]

    elif bc_type == 'reflective':
        # 固壁反射: 密度和能量不变, 动量(法向速度)反号
        # 依据: Anderson (1984) [2] §6.3, LeVeque (1992) [5] §7.1
        # u 反号 -> rho*u 反号 -> 能量 E~u^2 不变
        U[0, :] = U[1, :]
        U[0, 1] = -U[1, 1]  # 动量分量反号 (法向速度反射)
        U[-1, :] = U[-2, :]
        U[-1, 1] = -U[-2, 1]

    elif bc_type == 'periodic':
        # 周期边界: 左边界取右内部, 右边界取左内部
        # 依据: LeVeque (1992) [5] §7.1, Laney (1998) [3] §5.4.2
        U[0, :] = U[-2, :]
        U[-1, :] = U[1, :]

    elif bc_type == 'transmissive':
        # 无反射/透射边界: 二阶(线性)外推
        # 依据: LeVeque (1992) [5] §7.1, Anderson (1984) [2] §6.4
        U[0, :] = 2.0 * U[1, :] - U[2, :]
        U[-1, :] = 2.0 * U[-2, :] - U[-3, :]

    return U