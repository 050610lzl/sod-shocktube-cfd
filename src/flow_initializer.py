"""
流场初始化模块 (src/flow_initializer.py)
========================================
按Sod激波管标准初始条件初始化流场。

依据: Build文档 §5.2
文献: Sod (1978) [1], Anderson (1984) [2], OneFlow-CFD [4]
"""

import numpy as np

GAMMA = 1.4  # 比热比 (理想气体), 依据: Sod (1978) [1], OneFlow-CFD [4]


def initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5,
                    left_state=None, right_state=None):
    """
    按Sod激波管标准初始条件初始化流场。

    依据: Build文档 §5.2, Sod (1978) [1], OneFlow-CFD [4]

    初始条件:
        左态 (x < 0.5): rho_L=1.0, u_L=0.0, p_L=1.0
        右态 (x >= 0.5): rho_R=0.125, u_R=0.0, p_R=0.1

    参数:
        x: 网格坐标数组, 形状 (N,)
        gamma: 比热比 (默认1.4)
        diaphragm_pos: 隔膜位置 (默认0.5)
        left_state: 左侧状态字典 {'rho': ..., 'u': ..., 'p': ...}
        right_state: 右侧状态字典 {'rho': ..., 'u': ..., 'p': ...}

    返回:
        U: 守恒变量数组, 形状 (N, 3)
           U[:,0] = rho (密度)
           U[:,1] = rho*u (动量)
           U[:,2] = rho*E (总能)
    """
    if left_state is None:
        left_state = {'rho': 1.0, 'u': 0.0, 'p': 1.0}
    if right_state is None:
        right_state = {'rho': 0.125, 'u': 0.0, 'p': 0.1}

    n_points = len(x)
    U = np.zeros((n_points, 3))

    for i in range(n_points):
        if x[i] < diaphragm_pos:
            rho = left_state['rho']
            u = left_state['u']
            p = left_state['p']
        else:
            rho = right_state['rho']
            u = right_state['u']
            p = right_state['p']

        # 总能: E = p/((gamma-1)*rho) + 0.5*u^2  (依据: Anderson (1984) [2])
        E = p / ((gamma - 1.0) * rho) + 0.5 * u ** 2

        U[i, 0] = rho
        U[i, 1] = rho * u
        U[i, 2] = rho * E

    return U
