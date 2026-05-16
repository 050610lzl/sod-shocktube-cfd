"""
时间推进模块 (src/time_marcher.py)
==================================
按CFL条件计算时间步长，实现显式时间迭代。

依据: Build文档 §5.5
文献: LeVeque (1992) [5], Laney (1998) [3]
"""

import numpy as np

GAMMA = 1.4


def conservative_to_primitive(U, gamma=GAMMA):
    """
    将守恒变量转换为原始变量 (rho, u, p)。

    依据: Anderson (1984) [2]

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


def compute_dt(U, dx, cfl=0.8, gamma=GAMMA):
    """
    按CFL条件计算时间步长。

    依据: Build文档 §4.4, §5.5, LeVeque (1992) [5]

    公式: dt = CFL * dx / max(|u| + c)

    参数:
        U: 守恒变量数组
        dx: 网格间距
        cfl: CFL数 (默认0.8)
        gamma: 比热比

    返回:
        dt: 时间步长
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    lambda_max = np.max(np.abs(u) + c)
    if lambda_max < 1e-15:
        lambda_max = 1e-15
    return cfl * dx / lambda_max


def time_march(U, dx, dt, scheme_func, gamma=GAMMA):
    """
    执行一步时间推进。

    依据: Build文档 §5.5

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        scheme_func: 差分格式函数
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    return scheme_func(U, dx, dt, gamma)


# =============================================================================
# 守恒性检查模块
# 依据: Toro (2009) [2] 第1章, LeVeque (2002) 守恒律基本性质
# 守恒量: 总质量/总动量/总能量应随时间保持不变 (忽略边界通量贡献)
# =============================================================================

def compute_conserved_quantities(U, dx, gamma=GAMMA):
    """
    计算全场守恒量 (质量/动量/能量)。

    依据: Toro (2009) [2] 第1章 - 守恒律积分形式

    对于一维守恒律 ∂U/∂t + ∂F/∂x = 0, 在无边界通量的周期域内,
    积分量 ∫U dx 应为常数。对于零梯度边界, 边界通量为零, 守恒量近似保持。

    参数:
        U: 守恒变量数组, 形状 (N, 3)
           U[:,0] = rho (密度)
           U[:,1] = rho*u (动量密度)
           U[:,2] = rho*E (总能量密度)
        dx: 网格间距
        gamma: 比热比

    返回:
        mass: 总质量 = sum(rho) * dx
        momentum: 总动量 = sum(rho*u) * dx
        energy: 总能量 = sum(rho*E) * dx
    """
    mass = np.sum(U[:, 0]) * dx
    momentum = np.sum(U[:, 1]) * dx
    energy = np.sum(U[:, 2]) * dx
    return mass, momentum, energy


def check_conservation(U_current, U_initial, dx, step_num, gamma=GAMMA):
    """
    检查守恒量的变化百分比, 并打印报告。

    每100步调用一次, 报告质量/动量/能量的相对变化。

    参数:
        U_current: 当前步守恒变量
        U_initial: 初始时刻守恒变量
        dx: 网格间距
        step_num: 当前步数
        gamma: 比热比
    """
    mass_cur, mom_cur, eng_cur = compute_conserved_quantities(
        U_current, dx, gamma)
    mass_ini, mom_ini, eng_ini = compute_conserved_quantities(
        U_initial, dx, gamma)

    # 避免除零; 对于初始值接近零的量(如初始动量=0), 改用绝对误差报告
    eps = 1e-15
    if abs(mass_ini) > eps:
        mass_pct = abs(mass_cur - mass_ini) / abs(mass_ini) * 100.0
    else:
        mass_pct = abs(mass_cur - mass_ini) * 100.0  # 绝对值报告

    if abs(mom_ini) > eps:
        mom_pct = abs(mom_cur - mom_ini) / abs(mom_ini) * 100.0
    else:
        mom_pct = abs(mom_cur - mom_ini) * 100.0  # 初始动量为0时用绝对值

    if abs(eng_ini) > eps:
        eng_pct = abs(eng_cur - eng_ini) / abs(eng_ini) * 100.0
    else:
        eng_pct = abs(eng_cur - eng_ini) * 100.0

    print(f"  [守恒性检查 步数={step_num}] "
          f"质量变化: {mass_pct:.6e}%, "
          f"动量变化: {mom_pct:.6e}%, "
          f"能量变化: {eng_pct:.6e}%")

    return {
        'mass_change_pct': mass_pct,
        'momentum_change_pct': mom_pct,
        'energy_change_pct': eng_pct,
        'mass_current': mass_cur,
        'momentum_current': mom_cur,
        'energy_current': eng_cur
    }
