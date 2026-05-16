"""
核心求解器模块 (sod_solver.py)
==============================
实现4种经典有限差分格式求解一维Sod激波管问题:
  1. Lax-Friedrichs 格式 (一阶)
  2. Lax-Wendroff 格式 (二阶)
  3. MacCormack 预估校正格式 (二阶)
  4. 一阶迎风格式 (Steger-Warming通量分裂)

文献依据:
- Lax-Friedrichs: Sod (1978) [1], LeVeque (2002) [5]
- Lax-Wendroff: Sod (1978) [1], Laney (1998) [3]
- MacCormack: Sod (1978) [1], Laney (1998) [3]
- 一阶迎风: LeVeque (2002) [5], Laney (1998) [3]
"""

import numpy as np
from utils import compute_flux, conservative_to_primitive, GAMMA


# =============================================================================
# 辅助函数: Steger-Warming 通量分裂 (用于迎风格式)
# 依据: Laney (1998) [3], LeVeque (2002) [5], Steger & Warming (1981)
# =============================================================================
def steger_warming_split(U, gamma=GAMMA):
    """
    Steger-Warming 通量分裂: F = F^+ + F^-

    依据: Steger & Warming (1981), Laney (1998) [3] 第13章
    熵修复: Harten (1983), Toro (2009) [2] 第11章, 式11.35-11.38

    方法: 基于特征分解 F^+/- = R Lambda^+/- R^{-1} U

    参数:
        U: 守恒变量, 形状 (N, 3)
        gamma: 比热比

    返回:
        F_pos: 正特征值方向通量 F^+
        F_neg: 负特征值方向通量 F^-
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2  # 总焓

    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)

    for i in range(n):
        # 特征值
        lam1 = u[i] - c[i]  # u - c
        lam2 = u[i]          # u
        lam3 = u[i] + c[i]  # u + c

        # ---- Harten熵修复 (Harten 1983, Toro 2009 第11章, 式11.35-11.38) ----
        # 在跨音速点(特征值过零)处, max/min函数不可导, 产生非物理膨胀激波.
        # 使用固定的小常数 eps, 而非基于特征值变化量的自适应参数.
        # 关键: eps 应在 0.05-0.1 范围内. 自适应参数在激波附近过大,
        # 会减少数值耗散, 破坏一阶格式的TVD性质, 导致非物理振荡.
        eps = 0.1  # 固定熵修复阈值 (Harten 1983)

        def entropy_fix_abs(lam):
            """Harten熵修复: 光滑化 |lambda| 在零点附近的尖角.

            |lambda|_fix = { |lambda|,                  if |lambda| >= eps
                           { (lambda^2 + eps^2)/(2*eps), if |lambda| < eps

            依据: Toro (2009) [2] 式11.35-11.38
            """
            abs_lam = abs(lam)
            if abs_lam >= eps:
                return abs_lam
            else:
                return (lam ** 2 + eps ** 2) / (2.0 * eps)

        abs_lam1 = entropy_fix_abs(lam1)
        abs_lam2 = entropy_fix_abs(lam2)
        abs_lam3 = entropy_fix_abs(lam3)

        # 正/负部分: lambda^+ = 0.5*(lambda + |lambda|_fix)
        lam1_p = 0.5 * (lam1 + abs_lam1)
        lam1_n = 0.5 * (lam1 - abs_lam1)
        lam2_p = 0.5 * (lam2 + abs_lam2)
        lam2_n = 0.5 * (lam2 - abs_lam2)
        lam3_p = 0.5 * (lam3 + abs_lam3)
        lam3_n = 0.5 * (lam3 - abs_lam3)

        # 右特征向量矩阵 R (Toro 2009, 第3章)
        R = np.array([
            [1.0,              1.0,              1.0             ],
            [u[i] - c[i],      u[i],             u[i] + c[i]     ],
            [H[i] - u[i]*c[i], 0.5*u[i]**2,      H[i] + u[i]*c[i]]
        ])

        # R的逆矩阵: 使用数值求逆替代手写公式 (Laney 1998)
        R_inv = np.linalg.inv(R)

        # 守恒变量向量
        U_vec = U[i, :]

        # F^+ = R Lambda^+ R^{-1} U, F^- = R Lambda^- R^{-1} U
        F_pos[i, :] = R @ np.diag([lam1_p, lam2_p, lam3_p]) @ R_inv @ U_vec
        F_neg[i, :] = R @ np.diag([lam1_n, lam2_n, lam3_n]) @ R_inv @ U_vec

    return F_pos, F_neg


# =============================================================================
# 格式1: Lax-Friedrichs 有限差分格式 (一阶)
# 依据: Sod (1978) [1], LeVeque (2002) [5]
# 离散公式:
#   U_i^{n+1} = 0.5*(U_{i+1}^n + U_{i-1}^n) - dt/(2*dx)*(F_{i+1}^n - F_{i-1}^n)
# =============================================================================
def lax_friedrichs_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Lax-Friedrichs格式时间推进。

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界, 边界由外部处理)
    """
    n = len(U)
    F = compute_flux(U, gamma)

    U_new = np.zeros_like(U)

    # 内部节点差分 (i = 1, ..., N-2)
    # 依据: Sod (1978) [1], LeVeque (2002) [5]
    U_new[1:-1, :] = 0.5 * (U[2:, :] + U[:-2, :]) - \
                     (dt / (2.0 * dx)) * (F[2:, :] - F[:-2, :])

    return U_new


# =============================================================================
# 格式2: Lax-Wendroff 有限差分格式 (二阶)
# 依据: Sod (1978) [1], Laney (1998) [3]
# 离散公式:
#   U_i^{n+1} = U_i^n - dt/(2*dx)*(F_{i+1}^n - F_{i-1}^n)
#             + dt^2/(2*dx^2)*[A_{i+1/2}*(F_{i+1}^n - F_i^n) - A_{i-1/2}*(F_i^n - F_{i-1}^n)]
# 其中 A = dF/dU 为Jacobian矩阵
# =============================================================================
def lax_wendroff_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Lax-Wendroff格式时间推进。

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    F = compute_flux(U, gamma)

    U_new = np.zeros_like(U)

    # 计算Jacobian矩阵 A = dF/dU 在各节点的值
    # 依据: Laney (1998) [3], 式3.24-3.26
    A = compute_jacobian(U, gamma)

    # 内部节点 (i = 1, ..., N-2)
    for i in range(1, n - 1):
        # 二阶修正项
        # A_{i+1/2} 近似为 0.5*(A_i + A_{i+1})
        A_ip_half = 0.5 * (A[i, :, :] + A[i + 1, :, :])
        A_im_half = 0.5 * (A[i, :, :] + A[i - 1, :, :])

        dF_ip = F[i + 1, :] - F[i, :]
        dF_im = F[i, :] - F[i - 1, :]

        U_new[i, :] = U[i, :] - (dt / (2.0 * dx)) * (F[i + 1, :] - F[i - 1, :]) + \
                      (dt ** 2 / (2.0 * dx ** 2)) * (A_ip_half @ dF_ip - A_im_half @ dF_im)

    return U_new


def compute_jacobian(U, gamma=GAMMA):
    """
    计算Euler方程Jacobian矩阵 dF/dU。

    依据: Toro (2009) [2], 第3章

    参数:
        U: 守恒变量, 形状 (N, 3)
        gamma: 比热比

    返回:
        A: Jacobian矩阵, 形状 (N, 3, 3)
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    E = p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    H = E + p / rho  # 总焓

    n = len(U)
    A = np.zeros((n, 3, 3))

    for i in range(n):
        A[i, 0, 0] = 0.0
        A[i, 0, 1] = 1.0
        A[i, 0, 2] = 0.0

        A[i, 1, 0] = 0.5 * (gamma - 3.0) * u[i] ** 2
        A[i, 1, 1] = (3.0 - gamma) * u[i]
        A[i, 1, 2] = gamma - 1.0

        A[i, 2, 0] = u[i] * ((gamma - 1.0) * 0.5 * u[i] ** 2 - H[i])
        A[i, 2, 1] = H[i] - (gamma - 1.0) * u[i] ** 2
        A[i, 2, 2] = gamma * u[i]

    return A


# =============================================================================
# 格式3: MacCormack 预估校正格式 (二阶)
# 依据: Sod (1978) [1], Laney (1998) [3]
# 预估步: U_i^* = U_i^n - dt/dx*(F_{i+1}^n - F_i^n)
# 校正步: U_i^{**} = U_i^n - dt/dx*(F_i^* - F_{i-1}^*)
# 最终解: U_i^{n+1} = 0.5*(U_i^* + U_i^{**})
# =============================================================================
def macormack_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步MacCormack预估校正格式时间推进。

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    F = compute_flux(U, gamma)

    # ---- 预估步 (前差分) ----
    # 依据: Laney (1998) [3], Sod (1978) [1]
    U_star = np.zeros_like(U)
    for i in range(1, n - 1):
        U_star[i, :] = U[i, :] - (dt / dx) * (F[i + 1, :] - F[i, :])

    # 预估步边界
    U_star[0, :] = U_star[1, :]
    U_star[-1, :] = U_star[-2, :]

    # ---- 校正步 (后差分) ----
    F_star = compute_flux(U_star, gamma)
    U_starstar = np.zeros_like(U)
    for i in range(1, n - 1):
        U_starstar[i, :] = U[i, :] - (dt / dx) * (F_star[i, :] - F_star[i - 1, :])

    # ---- 取平均 ----
    U_new = 0.5 * (U_star + U_starstar)

    return U_new


# =============================================================================
# 格式4: 一阶迎风格式 (Steger-Warming通量分裂)
# 依据: LeVeque (2002) [5], Laney (1998) [3]
# 离散公式:
#   U_i^{n+1} = U_i^n - dt/dx*[(F_i^+ - F_{i-1}^+) + (F_{i+1}^- - F_i^-)]
# =============================================================================
def upwind_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步一阶迎风格式时间推进 (Steger-Warming通量分裂)。

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)

    # 通量分裂
    F_pos, F_neg = steger_warming_split(U, gamma)

    U_new = np.zeros_like(U)

    # 内部节点 (i = 1, ..., N-2)
    # 依据: Laney (1998) [3], LeVeque (2002) [5]
    for i in range(1, n - 1):
        U_new[i, :] = U[i, :] - (dt / dx) * (
            (F_pos[i, :] - F_pos[i - 1, :]) +
            (F_neg[i + 1, :] - F_neg[i, :])
        )

    return U_new


# =============================================================================
# 格式注册表 (统一接口)
# =============================================================================
FD_SCHEMES = {
    'lax_friedrichs': {
        'func': lax_friedrichs_step,
        'order': 1,
        'description': 'Lax-Friedrichs格式 (一阶中心耗散)',
        'reference': 'Sod (1978) [1], LeVeque (2002) [5]'
    },
    'lax_wendroff': {
        'func': lax_wendroff_step,
        'order': 2,
        'description': 'Lax-Wendroff格式 (二阶中心色散)',
        'reference': 'Sod (1978) [1], Laney (1998) [3]'
    },
    'macormack': {
        'func': macormack_step,
        'order': 2,
        'description': 'MacCormack预估校正格式 (二阶)',
        'reference': 'Sod (1978) [1], Laney (1998) [3]'
    },
    'upwind': {
        'func': upwind_step,
        'order': 1,
        'description': '一阶迎风格式 (Steger-Warming分裂)',
        'reference': 'LeVeque (2002) [5], Laney (1998) [3]'
    }
}


def solve_sod(scheme_name, x, dx, U0, t_final=0.2, cfl=0.8, gamma=GAMMA):
    """
    使用指定有限差分格式求解Sod激波管问题。

    参数:
        scheme_name: 格式名称 ('lax_friedrichs', 'lax_wendroff', 'macormack', 'upwind')
        x: 网格坐标数组
        dx: 网格间距
        U0: 初始守恒变量
        t_final: 仿真终止时间 (默认0.2, 依据: Sod (1978) [1])
        cfl: CFL数 (默认0.8)
        gamma: 比热比

    返回:
        U: 最终守恒变量
        t: 最终时间
        n_steps: 迭代步数
    """
    from utils import apply_boundary_condition, compute_dt

    if scheme_name not in FD_SCHEMES:
        raise ValueError(f"未知格式: {scheme_name}. 可选: {list(FD_SCHEMES.keys())}")

    scheme = FD_SCHEMES[scheme_name]
    step_func = scheme['func']

    U = U0.copy()
    t = 0.0
    n_steps = 0

    print(f"开始求解: {scheme['description']}")
    print(f"  文献依据: {scheme['reference']}")
    print(f"  格式精度: {scheme['order']}阶")

    while t < t_final:
        # 计算时间步长 (CFL条件)
        dt = compute_dt(U, dx, cfl, gamma)

        # 确保不超过终止时间
        if t + dt > t_final:
            dt = t_final - t

        # 有限差分格式推进
        U_new = step_func(U, dx, dt, gamma)

        # 施加边界条件 (零梯度外推)
        U_new = apply_boundary_condition(U_new)

        U = U_new
        t += dt
        n_steps += 1

        # 每100步输出一次进度
        if n_steps % 100 == 0:
            print(f"  步数: {n_steps}, 时间: {t:.4f}/{t_final}, dt: {dt:.6f}")

    print(f"  求解完成: {n_steps} 步, 最终时间: {t:.4f}")

    return U, t, n_steps
