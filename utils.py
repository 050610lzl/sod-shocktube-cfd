"""
工具函数模块 (utils.py)
========================
包含网格生成、流场初始化、边界处理、原始变量提取、精确解计算等工具函数。

文献依据:
- Sod问题初始条件: Sod (1978) [1]
- 边界条件规范: OneFlow-CFD [4], Laney (1998) [3]
- 精确解方法: Toro (2009) [2]
"""

import numpy as np
from scipy.optimize import brentq


# =============================================================================
# 物理常量 (依据: Sod (1978) [1], OneFlow-CFD [4])
# =============================================================================
GAMMA = 1.4  # 比热比 (理想气体)


# =============================================================================
# 网格生成模块
# 依据: Build文档 §5.1, Laney (1998) [3]
# =============================================================================
def generate_mesh(n_points=100, x_left=0.0, x_right=1.0):
    """
    生成一维均匀网格。

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


# =============================================================================
# 流场初始化模块
# 依据: Sod (1978) [1], OneFlow-CFD [4], Anderson (1984) [2]
# 初始条件:
#   左态 (x < 0.5): rho_L=1.0, u_L=0.0, p_L=1.0
#   右态 (x >= 0.5): rho_R=0.125, u_R=0.0, p_R=0.1
# =============================================================================
def initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5,
                    left_state=None, right_state=None):
    """
    按Sod激波管标准初始条件初始化流场。

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


# =============================================================================
# 原始变量提取模块
# 依据: Anderson (1984) [2]
# =============================================================================
def conservative_to_primitive(U, gamma=GAMMA):
    """
    将守恒变量转换为原始变量 (rho, u, p)。

    参数:
        U: 守恒变量数组, 形状 (N, 3) 或 (3,)
        gamma: 比热比

    返回:
        rho: 密度
        u: 速度
        p: 压力
    """
    rho = U[..., 0]
    u = U[..., 1] / rho
    E = U[..., 2] / rho
    p = (gamma - 1.0) * rho * (E - 0.5 * u ** 2)
    return rho, u, p


def compute_flux(U, gamma=GAMMA):
    """
    计算Euler方程通量向量 F(U)。

    依据: Toro (2009) [2], 一维Euler方程通量定义

    参数:
        U: 守恒变量数组, 形状 (N, 3) 或 (3,)
        gamma: 比热比

    返回:
        F: 通量数组, 形状与U相同
    """
    rho = U[..., 0]
    u = U[..., 1] / rho
    E = U[..., 2] / rho
    p = (gamma - 1.0) * rho * (E - 0.5 * u ** 2)

    F = np.zeros_like(U)
    F[..., 0] = rho * u
    F[..., 1] = rho * u ** 2 + p
    F[..., 2] = u * (rho * E + p)
    return F


def compute_sound_speed(U, gamma=GAMMA):
    """
    计算当地声速 c = sqrt(gamma * p / rho)。

    依据: Anderson (1984) [2]

    参数:
        U: 守恒变量数组
        gamma: 比热比

    返回:
        c: 声速数组
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    return np.sqrt(gamma * p / rho)


def compute_max_eigenvalue(U, gamma=GAMMA):
    """
    计算Jacobian矩阵的最大特征值 |u| + c。

    依据: LeVeque (2002) [5], CFL稳定性条件

    参数:
        U: 守恒变量数组
        gamma: 比热比

    返回:
        lambda_max: 最大特征值 (标量)
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(gamma * p / rho)
    return np.max(np.abs(u) + c)


# =============================================================================
# 边界处理模块 (零梯度/外推边界)
# 依据: Build文档 §5.4, Laney (1998) [3], OneFlow-CFD [4]
# 左边界: U[0] = U[1]
# 右边界: U[N-1] = U[N-2]
# =============================================================================
def apply_boundary_condition(U):
    """
    施加零梯度外推边界条件。

    参数:
        U: 守恒变量数组, 形状 (N, 3)

    返回:
        U: 施加边界条件后的数组 (原地修改)
    """
    U[0, :] = U[1, :]       # 左边界外推
    U[-1, :] = U[-2, :]     # 右边界外推
    return U


# =============================================================================
# 精确解计算模块 (Sod激波管Riemann精确解)
# 依据: Toro (2009) [2] 第4章, Sod (1978) [1]
# =============================================================================
def sod_exact_solution(x, t, gamma=GAMMA):
    """
    计算Sod激波管问题在时刻t的解析精确解。

    算法依据: Toro (2009) [2] 第4章 - Riemann问题精确解法
    初始条件: Sod (1978) [1]

    参数:
        x: 网格坐标数组
        t: 仿真时刻
        gamma: 比热比

    返回:
        rho_exact: 精确密度数组
        u_exact: 精确速度数组
        p_exact: 精确压力数组
    """
    # 初始状态 (依据: Sod (1978) [1])
    rho_L, u_L, p_L = 1.0, 0.0, 1.0
    rho_R, u_R, p_R = 0.125, 0.0, 0.1

    # 左/右声速
    a_L = np.sqrt(gamma * p_L / rho_L)
    a_R = np.sqrt(gamma * p_R / rho_R)

    # ---- 步骤1: 求解接触间断压力 p* (Toro (2009) [2], 式4.46) ----
    def pressure_function(p_star):
        """Riemann不变量方程 f(p*) = 0"""
        # 左波函数 (稀疏波)
        if p_star <= p_L:
            f_L = (2.0 * a_L / (gamma - 1.0)) * \
                  ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            # 激波 - 公式: (p*-p_L) * sqrt(A_L / (p*+B_L)), Toro (2009) 式4.46
            A_L = 2.0 / ((gamma + 1.0) * rho_L)
            B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
            f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

        # 右波函数 (激波, 因为p* > p_R)
        if p_star <= p_R:
            f_R = (2.0 * a_R / (gamma - 1.0)) * \
                  ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_R = 2.0 / ((gamma + 1.0) * rho_R)
            B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
            f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))

        return f_L + f_R + (u_R - u_L)

    # 使用Brent方法求解 p* (Toro (2009) [2])
    p_star = brentq(pressure_function, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-12)

    # ---- 步骤2: 求解接触间断速度 u* (Toro (2009) [2], 式4.47) ----
    if p_star <= p_L:
        u_star = u_L - (2.0 * a_L / (gamma - 1.0)) * \
                 ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        # 激波分支 - 公式: u* = u_L - (p*-p_L) * sqrt(A_L/(p*+B_L)), Toro (2009) 式4.47
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

    # ---- 步骤3: 计算接触间断两侧密度 (Toro (2009) [2]) ----
    # 左侧 (稀疏波尾部)
    if p_star <= p_L:
        rho_star_L = rho_L * (p_star / p_L) ** (1.0 / gamma)
    else:
        # 激波压缩
        rho_star_L = rho_L * (p_star / p_L + (gamma - 1.0) / (gamma + 1.0)) / \
                     (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_L)

    # 右侧
    if p_star <= p_R:
        rho_star_R = rho_R * (p_star / p_R) ** (1.0 / gamma)
    else:
        rho_star_R = rho_R * (p_star / p_R + (gamma - 1.0) / (gamma + 1.0)) / \
                     (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_R)

    # ---- 步骤4: 计算波头/波尾位置 (Toro (2009) [2]) ----
    # 左稀疏波头 (head)
    x_head = 0.5 - a_L * t
    # 左稀疏波尾 (tail)
    x_tail_L = 0.5 + (u_star - np.sqrt(gamma * p_star / rho_star_L)) * t
    # 接触间断
    x_contact = 0.5 + u_star * t
    # 右激波
    if p_star > p_R:
        # 激波速度 (Toro (2009) [2], 式4.54)
        S_R = u_R + a_R * np.sqrt((gamma + 1.0) / (2.0 * gamma) * p_star / p_R +
                                   (gamma - 1.0) / (2.0 * gamma))
    else:
        S_R = u_R + a_R
    x_shock = 0.5 + S_R * t

    # ---- 步骤5: 在各区域分配精确解 ----
    n = len(x)
    rho_exact = np.zeros(n)
    u_exact = np.zeros(n)
    p_exact = np.zeros(n)

    for i in range(n):
        xi = x[i]

        if xi <= x_head:
            # 区域1: 未扰动左态
            rho_exact[i] = rho_L
            u_exact[i] = u_L
            p_exact[i] = p_L

        elif xi <= x_tail_L:
            # 区域2: 稀疏波区 (等熵膨胀, Toro (2009) [2], 式4.62-4.64)
            # 在稀疏波内, 使用自相似变量 xi/t
            xi_local = (xi - 0.5) / t
            u_val = 2.0 / (gamma + 1.0) * (a_L + xi_local)
            a_val = a_L - (gamma - 1.0) / 2.0 * (u_val - u_L)
            rho_exact[i] = rho_L * (a_val / a_L) ** (2.0 / (gamma - 1.0))
            u_exact[i] = u_val
            p_exact[i] = p_L * (a_val / a_L) ** (2.0 * gamma / (gamma - 1.0))

        elif xi <= x_contact:
            # 区域3: 接触间断左侧
            rho_exact[i] = rho_star_L
            u_exact[i] = u_star
            p_exact[i] = p_star

        elif xi <= x_shock:
            # 区域4: 激波左侧 (接触间断右侧)
            rho_exact[i] = rho_star_R
            u_exact[i] = u_star
            p_exact[i] = p_star

        else:
            # 区域5: 未扰动右态
            rho_exact[i] = rho_R
            u_exact[i] = u_R
            p_exact[i] = p_R

    return rho_exact, u_exact, p_exact


# =============================================================================
# 时间步长计算 (CFL条件)
# 依据: LeVeque (2002) [5], Build文档 §4.4
# =============================================================================
def compute_dt(U, dx, cfl=0.8, gamma=GAMMA):
    """
    按CFL条件计算时间步长。

    公式: dt = CFL * dx / max(|u| + c)

    参数:
        U: 守恒变量数组
        dx: 网格间距
        cfl: CFL数 (默认0.8)
        gamma: 比热比

    返回:
        dt: 时间步长
    """
    lambda_max = compute_max_eigenvalue(U, gamma)
    if lambda_max < 1e-15:
        lambda_max = 1e-15
    return cfl * dx / lambda_max
