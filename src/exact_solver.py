"""
精确解计算模块 (src/exact_solver.py)
====================================
计算Sod激波管问题在时刻t的解析精确解。

依据: Build文档 §5.6
文献: Toro (2009) [2] 第4章, Sod (1978) [1]
"""

import numpy as np
from scipy.optimize import brentq

GAMMA = 1.4


def sod_exact_solution(x, t, gamma=GAMMA):
    """
    计算Sod激波管问题在时刻t的解析精确解。

    算法依据: Build文档 §5.6, Toro (2009) [2] 第4章 - Riemann问题精确解法
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
        """Riemann不变量方程 f(p*) = 0, 依据: Toro (2009) 第4章"""
        if p_star <= p_L:
            f_L = (2.0 * a_L / (gamma - 1.0)) * \
                  ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_L = 2.0 / ((gamma + 1.0) * rho_L)
            B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
            f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

        if p_star <= p_R:
            f_R = (2.0 * a_R / (gamma - 1.0)) * \
                  ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_R = 2.0 / ((gamma + 1.0) * rho_R)
            B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
            f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))

        return f_L + f_R + (u_R - u_L)

    p_star = brentq(pressure_function, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-12)

    # ---- 步骤2: 求解接触间断速度 u* (Toro (2009) [2], 式4.47) ----
    if p_star <= p_L:
        u_star = u_L - (2.0 * a_L / (gamma - 1.0)) * \
                 ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

    # ---- 步骤3: 计算接触间断两侧密度 (Toro (2009) [2]) ----
    if p_star <= p_L:
        rho_star_L = rho_L * (p_star / p_L) ** (1.0 / gamma)
    else:
        rho_star_L = rho_L * (p_star / p_L + (gamma - 1.0) / (gamma + 1.0)) / \
                     (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_L)

    if p_star <= p_R:
        rho_star_R = rho_R * (p_star / p_R) ** (1.0 / gamma)
    else:
        rho_star_R = rho_R * (p_star / p_R + (gamma - 1.0) / (gamma + 1.0)) / \
                     (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_R)

    # ---- 步骤4: 计算波头/波尾位置 (Toro (2009) [2]) ----
    x_head = 0.5 - a_L * t
    x_tail_L = 0.5 + (u_star - np.sqrt(gamma * p_star / rho_star_L)) * t
    x_contact = 0.5 + u_star * t

    if p_star > p_R:
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
            rho_exact[i] = rho_L
            u_exact[i] = u_L
            p_exact[i] = p_L

        elif xi <= x_tail_L:
            xi_local = (xi - 0.5) / t
            u_val = 2.0 / (gamma + 1.0) * (a_L + xi_local)
            a_val = a_L - (gamma - 1.0) / 2.0 * (u_val - u_L)
            rho_exact[i] = rho_L * (a_val / a_L) ** (2.0 / (gamma - 1.0))
            u_exact[i] = u_val
            p_exact[i] = p_L * (a_val / a_L) ** (2.0 * gamma / (gamma - 1.0))

        elif xi <= x_contact:
            rho_exact[i] = rho_star_L
            u_exact[i] = u_star
            p_exact[i] = p_star

        elif xi <= x_shock:
            rho_exact[i] = rho_star_R
            u_exact[i] = u_star
            p_exact[i] = p_star

        else:
            rho_exact[i] = rho_R
            u_exact[i] = u_R
            p_exact[i] = p_R

    return rho_exact, u_exact, p_exact
