"""
有限差分格式模块 (src/fd_schemes.py)
====================================
实现8种经典数值格式求解一维Sod激波管问题:
  1. Lax-Friedrichs 格式 (一阶)
  2. Lax-Wendroff 格式 (二阶)
  3. MacCormack 预估校正格式 (二阶)
  4. 一阶迎风格式 (Steger-Warming通量分裂)
  5. Rusanov 格式 (局部Lax-Friedrichs)
  6. Godunov 格式 (精确Riemann求解器)
  7. Roe 格式 (近似Riemann求解器)
  8. HLLC 格式 (恢复接触间断)

依据: Build文档 §5.3
文献: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], LeVeque (1992) [5],
      Roe (1981) [7], Toro et al. (1994) [8]
"""

import numpy as np

GAMMA = 1.4


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


def conservative_to_primitive(U, gamma=GAMMA):
    """将守恒变量转换为原始变量 (rho, u, p)。"""
    rho = U[..., 0]
    u = U[..., 1] / rho
    E = U[..., 2] / rho
    p = (gamma - 1.0) * rho * (E - 0.5 * u ** 2)
    return rho, u, p


def compute_jacobian(U, gamma=GAMMA):
    """
    计算Euler方程Jacobian矩阵 dF/dU。

    依据: Laney (1998) [3], 式3.24-3.26

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
# 迎风格式实现 (Steger-Warming通量分裂 FVS)
# 依据: Steger & Warming (1981), Laney (1998) [3] 第13章, Toro (2009) [2] 第12章
# 注意: 特征分解迎风在强间断处易产生负密度导致崩溃。
#       Steger-Warming FVS在通量空间分裂，数值稳定性更好。
# 方法: F = F⁺ + F⁻ = R Λ⁺ R⁻¹ U + R Λ⁻ R⁻¹ U
#       U_i^{n+1} = U_i^n - (dt/dx) * [(F⁺_i - F⁺_{i-1}) + (F⁻_{i+1} - F⁻_i)]
# =============================================================================

def steger_warming_flux(U, gamma=GAMMA):
    """
    计算Steger-Warming通量分裂 F = F⁺ + F⁻。

    依据: Steger & Warming (1981), Laney (1998) [3] 第13章
    熵修复: Harten (1983), Toro (2009) [2] 第11章, 式11.35-11.38

    参数:
        U: 守恒变量, 形状 (N, 3)
        gamma: 比热比

    返回:
        F_pos: 正通量 F⁺
        F_neg: 负通量 F⁻
    """
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2

    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)

    # ---- 固定熵修复参数 (Harten 1983, Toro 2009 第11章) ----
    # 熵修复用于处理跨音速点 (特征值过零) 处 |lambda| 不可导导致的膨胀激波.
    # 使用固定的小常数 eps, 而非基于特征值变化量的自适应参数.
    # 关键: eps 应在 0.05-0.1 范围内 (Toro 2009, 式11.35-11.38).
    # 自适应参数 (如 eps = |lambda_R - lambda_L|) 在激波附近过大,
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

    for i in range(n):
        # 特征值
        lam1 = u[i] - c[i]
        lam2 = u[i]
        lam3 = u[i] + c[i]

        # 应用固定epsilon熵修复
        abs_lam1 = entropy_fix_abs(lam1)
        abs_lam2 = entropy_fix_abs(lam2)
        abs_lam3 = entropy_fix_abs(lam3)

        # 正负分裂: lambda^+ = 0.5*(lambda + |lambda|_fix), lambda^- = 0.5*(lambda
        # - |lambda|_fix)
        lam1_p = 0.5 * (lam1 + abs_lam1)
        lam1_n = 0.5 * (lam1 - abs_lam1)
        lam2_p = 0.5 * (lam2 + abs_lam2)
        lam2_n = 0.5 * (lam2 - abs_lam2)
        lam3_p = 0.5 * (lam3 + abs_lam3)
        lam3_n = 0.5 * (lam3 - abs_lam3)

        # 右特征向量矩阵 R (依据: Toro (2009) [2] 式3.43)
        R = np.array([
            [1.0, 1.0, 1.0],
            [u[i] - c[i], u[i], u[i] + c[i]],
            [H[i] - u[i] * c[i], 0.5 * u[i] ** 2, H[i] + u[i] * c[i]]
        ])

        # 左特征向量矩阵 R_inv: 使用 np.linalg.inv 数值求逆替代手写公式
        # 依据: Laney (1998) [3] 指出手写R_inv公式在 u != 0 时存在数值精度问题
        # 改用数值求逆保证在所有工况下的精度 (Steger & Warming, 1981)
        R_inv = np.linalg.inv(R)

        U_vec = U[i, :]

        # F⁺ = R Λ⁺ R⁻¹ U
        F_pos[i, :] = R @ np.diag([lam1_p, lam2_p, lam3_p]) @ R_inv @ U_vec
        # F⁻ = R Λ⁻ R⁻¹ U
        F_neg[i, :] = R @ np.diag([lam1_n, lam2_n, lam3_n]) @ R_inv @ U_vec

    return F_pos, F_neg


def upwind_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步一阶迎风格式时间推进 (Steger-Warming通量分裂)。

    依据: Steger & Warming (1981), Laney (1998) [3] 第13章

    离散公式:
        U_i^{n+1} = U_i^n - (dt/dx) * [(F⁺_i - F⁺_{i-1}) + (F⁻_{i+1} - F⁻_i)]

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    F_pos, F_neg = steger_warming_flux(U, gamma)
    U_new = U.copy()

    for i in range(1, n - 1):
        U_new[i, :] = U[i, :] - (dt / dx) * (
            (F_pos[i, :] - F_pos[i - 1, :]) +
            (F_neg[i + 1, :] - F_neg[i, :])
        )

    return U_new


# =============================================================================
# 格式1: Lax-Friedrichs 有限差分格式 (一阶)
# 依据: Build文档 §4.3 FDM-1, Sod (1978) [1], Laney (1998) [3]
# 离散公式:
#   U_i^{n+1} = 0.5*(U_{i+1}^n + U_{i-1}^n) - dt/(2*dx)*(F_{i+1}^n - F_{i-1}^n)
# =============================================================================
def lax_friedrichs_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Lax-Friedrichs格式时间推进。

    依据: Build文档 §4.3, Sod (1978) [1], Laney (1998) [3]

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    U_new = np.zeros_like(U)
    F = compute_flux(U, gamma)
    U_new[1:-1, :] = 0.5 * (U[2:, :] + U[:-2, :]) - \
        (dt / (2.0 * dx)) * (F[2:, :] - F[:-2, :])

    return U_new


# =============================================================================
# 格式2: Lax-Wendroff 有限差分格式 (二阶)
# 依据: Build文档 §4.3 FDM-2, Sod (1978) [1], Laney (1998) [3]
# =============================================================================
def lax_wendroff_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Lax-Wendroff格式时间推进。

    依据: Build文档 §4.3, Sod (1978) [1], Laney (1998) [3]

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
    A = compute_jacobian(U, gamma)
    U_new = np.zeros_like(U)

    for i in range(1, n - 1):
        A_ip_half = 0.5 * (A[i, :, :] + A[i + 1, :, :])
        A_im_half = 0.5 * (A[i, :, :] + A[i - 1, :, :])

        dF_ip = F[i + 1, :] - F[i, :]
        dF_im = F[i, :] - F[i - 1, :]

        U_new[i, :] = U[i, :] - (dt / (2.0 * dx)) * (F[i + 1, :] - F[i - 1, :]) + (
            dt ** 2 / (2.0 * dx ** 2)) * (A_ip_half @ dF_ip - A_im_half @ dF_im)

    return U_new


# =============================================================================
# 格式3: MacCormack 预估校正格式 (二阶)
# 依据: Build文档 §4.3 FDM-3, Sod (1978) [1], Laney (1998) [3]
# 说明: 标准MacCormack格式 = 预估(前差分) + 校正(后差分) + 平均
#       为改善对称性, 采用步数计数器实现方向交替:
#         - 偶数步: 预估向前 + 校正向后
#         - 奇数步: 预估向后 + 校正向前
#       依据: Laney (1998) 第9章, 交替方向可减少非对称数值耗散
# =============================================================================

# MacCormack格式的全局步数计数器 (用于交替方向)
_macormack_step_counter = 0


def macormack_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步MacCormack预估校正格式时间推进。

    依据: Build文档 §4.3, Sod (1978) [1], Laney (1998) [3]

    标准公式 (预估向前 + 校正向后):
        预估: U_i* = U_i^n - (dt/dx) * (F_{i+1}^n - F_i^n)
        校正: U_i** = U_i^n - (dt/dx) * (F_i* - F_{i-1}*)
        平均: U_i^{n+1} = 0.5 * (U_i* + U_i**)

    交替方向 (Laney 1998):
        偶数步: 预估向前 + 校正向后
        奇数步: 预估向后 + 校正向前

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    global _macormack_step_counter
    n = len(U)
    F = compute_flux(U, gamma)

    # 根据步数计数器选择方向 (实现交替)
    forward_predictor = (_macormack_step_counter % 2 == 0)

    if forward_predictor:
        # 偶数步: 预估向前 + 校正向后 (标准MacCormack)
        # 预估步 (前差分: F_{i+1} - F_i)
        U_star = np.zeros_like(U)
        for i in range(1, n - 1):
            U_star[i, :] = U[i, :] - (dt / dx) * (F[i + 1, :] - F[i, :])

        # 边界外推
        U_star[0, :] = U_star[1, :]
        U_star[-1, :] = U_star[-2, :]

        # 校正步 (后差分: F_i* - F_{i-1}*)
        F_star = compute_flux(U_star, gamma)
        U_starstar = np.zeros_like(U)
        for i in range(1, n - 1):
            U_starstar[i, :] = U[i, :] - \
                (dt / dx) * (F_star[i, :] - F_star[i - 1, :])
    else:
        # 奇数步: 预估向后 + 校正向前 (反向MacCormack)
        # 预估步 (后差分: F_i - F_{i-1})
        U_star = np.zeros_like(U)
        for i in range(1, n - 1):
            U_star[i, :] = U[i, :] - (dt / dx) * (F[i, :] - F[i - 1, :])

        # 边界外推
        U_star[0, :] = U_star[1, :]
        U_star[-1, :] = U_star[-2, :]

        # 校正步 (前差分: F_{i+1}* - F_i*)
        F_star = compute_flux(U_star, gamma)
        U_starstar = np.zeros_like(U)
        for i in range(1, n - 1):
            U_starstar[i, :] = U[i, :] - \
                (dt / dx) * (F_star[i + 1, :] - F_star[i, :])

    # 取平均
    U_new = 0.5 * (U_star + U_starstar)

    # 更新全局步数计数器
    _macormack_step_counter += 1

    return U_new


# =============================================================================
# 格式5: Rusanov 格式 (局部Lax-Friedrichs / Local Lax-Friedrichs)
# 依据: Toro (2009) [2] 第10章, Rusanov (1961)
# 通量: F_{i+1/2} = 0.5*(F_i + F_{i+1}) - 0.5*alpha*(U_{i+1} - U_i)
# alpha = max(|u|+c) 在 i 和 i+1 处的局部最大波速
# =============================================================================
def rusanov_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Rusanov格式时间推进 (局部Lax-Friedrichs)。

    依据: Toro (2009) [2] 第10章, Rusanov (1961)

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
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    S = np.abs(u) + c  # 局部波速 |u|+c

    U_new = np.zeros_like(U)

    for i in range(1, n - 1):
        alpha = max(S[i], S[i + 1])
        U_new[i,
              :] = U[i,
                     :] - (dt / dx) * (0.5 * (F[i + 1,
                                                :] + F[i,
                                       :]) - 0.5 * alpha * (U[i + 1,
                                                              :] - U[i,
                                                                     :]) - (0.5 * (F[i,
                                                                                     :] + F[i - 1,
                                                                                            :]) - 0.5 * max(S[i - 1],
                                                                                                            S[i]) * (U[i,
                                                                                                                       :] - U[i - 1,
                                                                                                                              :])))

    return U_new


# =============================================================================
# 格式6: Godunov 格式 (精确Riemann求解器)
# 依据: Toro (2009) [2] 第4章, Godunov (1959)
# 通量: F_{i+1/2} = F(U^*(0; U_i, U_{i+1}))  精确Riemann解在x/t=0处的通量
# =============================================================================
def _riemann_flux_godunov(U_L, U_R, gamma=GAMMA):
    """
    计算精确Riemann求解器通量 (Godunov通量)。

    依据: Toro (2009) [2] 第4章 - 精确Riemann求解器

    参数:
        U_L: 左状态守恒变量 (3,)
        U_R: 右状态守恒变量 (3,)
        gamma: 比热比

    返回:
        F: Godunov通量 (3,)
    """
    from scipy.optimize import brentq

    rho_L, u_L, p_L = conservative_to_primitive(U_L, gamma)
    rho_R, u_R, p_R = conservative_to_primitive(U_R, gamma)
    a_L = np.sqrt(gamma * p_L / rho_L)
    a_R = np.sqrt(gamma * p_R / rho_R)

    def pressure_function(p_star):
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

    p_star = brentq(pressure_function, 1e-10,
                    max(p_L, p_R) * 2.0 + 1.0, xtol=1e-12)

    if p_star <= p_L:
        u_star = u_L - (2.0 * a_L / (gamma - 1.0)) * \
            ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

    if u_star > 0:
        rho_star = rho_L * (p_star / p_L) ** (1.0 / gamma) if p_star <= p_L else \
            rho_L * (p_star / p_L + (gamma - 1.0) / (gamma + 1.0)) / \
            (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_L)
        F = np.array([rho_star *
                      u_star, rho_star *
                      u_star ** 2 +
                      p_star, u_star *
                      (rho_star *
                       (p_star /
                        ((gamma -
                          1.0) *
                         rho_star) +
                           0.5 *
                           u_star ** 2) +
                          p_star)])
    else:
        rho_star = rho_R * (p_star / p_R) ** (1.0 / gamma) if p_star <= p_R else \
            rho_R * (p_star / p_R + (gamma - 1.0) / (gamma + 1.0)) / \
            (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_R)
        F = np.array([rho_star *
                      u_star, rho_star *
                      u_star ** 2 +
                      p_star, u_star *
                      (rho_star *
                       (p_star /
                        ((gamma -
                          1.0) *
                         rho_star) +
                           0.5 *
                           u_star ** 2) +
                          p_star)])

    return F


def godunov_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步Godunov格式时间推进 (精确Riemann求解器)。

    依据: Toro (2009) [2] 第4章, Godunov (1959)

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    U_new = U.copy()

    for i in range(1, n - 1):
        F_right = _riemann_flux_godunov(U[i, :], U[i + 1, :], gamma)
        F_left = _riemann_flux_godunov(U[i - 1, :], U[i, :], gamma)
        U_new[i, :] = U[i, :] - (dt / dx) * (F_right - F_left)

    return U_new


# =============================================================================
# 格式7: Roe 格式 (近似Riemann求解器)
# 依据: Roe (1981) [7], Toro (2009) [2] 第11章
# 通量: F_{i+1/2} = 0.5*(F_L + F_R) - 0.5*|A~|*(U_R - U_L)
# A~: Roe平均Jacobian矩阵
# =============================================================================
def _entropy_fix_eigenvalue(lam, lam_left, lam_right, delta=1e-10):
    """
    Harten熵修复 (Entropy Fix) - 修正近似Riemann求解器在跨音速稀疏波中的非物理解。

    依据: Harten (1983) "On the Numerical Solution of Transonic Flow",
          Toro (2009) [2] 第11章, 式11.35-11.38

    问题: Roe格式在跨音速稀疏波中, 当特征值跨越零点时, |lambda| 产生膨胀激波(expansion shock)。
    解决: 用光滑函数替代 |lambda| 在零点附近的尖角。

    公式:
        如果 |lambda| >= epsilon:  |lambda|_fix = |lambda|
        如果 |lambda| < epsilon:   |lambda|_fix = (lambda^2 + epsilon^2) / (2*epsilon)

    其中 epsilon = max(0, lambda_right - lambda_left) 为跨波特征值变化量。

    参数:
        lam: 当前特征值 (标量)
        lam_left: 左状态特征值 (标量)
        lam_right: 右状态特征值 (标量)
        delta: 最小阈值, 防止epsilon过小
    返回:
        修复后的 |lambda|
    """
    eps = max(delta, lam_right - lam_left)
    abs_lam = abs(lam)
    if abs_lam >= eps:
        return abs_lam
    else:
        return (lam ** 2 + eps ** 2) / (2.0 * eps)


def _roe_average(U_L, U_R, gamma=GAMMA, entropy_fix=False):
    """
    计算Roe平均状态和|A~|*(U_R - U_L)。

    依据: Roe (1981) [7], Toro (2009) [2] 第11章

    参数:
        U_L, U_R: 左右状态
        gamma: 比热比
        entropy_fix: 是否启用Harten熵修复 (默认False)

    返回:
        dissipation: |A~|*(U_R - U_L) 耗散项
    """
    rho_L, u_L, p_L = conservative_to_primitive(U_L, gamma)
    rho_R, u_R, p_R = conservative_to_primitive(U_R, gamma)

    sqrt_rho_L = np.sqrt(rho_L)
    sqrt_rho_R = np.sqrt(rho_R)

    u_tilde = (sqrt_rho_L * u_L + sqrt_rho_R * u_R) / (sqrt_rho_L + sqrt_rho_R)
    H_L = gamma * p_L / ((gamma - 1.0) * rho_L) + 0.5 * u_L ** 2
    H_R = gamma * p_R / ((gamma - 1.0) * rho_R) + 0.5 * u_R ** 2
    H_tilde = (sqrt_rho_L * H_L + sqrt_rho_R * H_R) / (sqrt_rho_L + sqrt_rho_R)
    c_tilde = np.sqrt(np.maximum(
        (gamma - 1.0) * (H_tilde - 0.5 * u_tilde ** 2), 1e-15))

    dU = U_R - U_L
    d_rho = dU[0]
    d_u = dU[1] - u_tilde * dU[0]
    d_p = (gamma - 1.0) * (dU[2] - u_tilde *
                           dU[1] + 0.5 * u_tilde ** 2 * dU[0])

    alpha1 = 0.5 * (d_p / (c_tilde ** 2) - d_u / c_tilde)
    alpha2 = d_rho - d_p / (c_tilde ** 2)
    alpha3 = 0.5 * (d_p / (c_tilde ** 2) + d_u / c_tilde)

    r1 = np.array([1.0, u_tilde - c_tilde, H_tilde - u_tilde * c_tilde])
    r2 = np.array([1.0, u_tilde, 0.5 * u_tilde ** 2])
    r3 = np.array([1.0, u_tilde + c_tilde, H_tilde + u_tilde * c_tilde])

    # 特征值
    lambda1 = u_tilde - c_tilde
    lambda2 = u_tilde
    lambda3 = u_tilde + c_tilde

    if entropy_fix:
        # Harten熵修复 (Harten 1983, Toro 2009 第11章)
        # 计算左/右状态的波速 (用于确定特征值变化)
        a_L = np.sqrt(gamma * p_L / rho_L)
        a_R = np.sqrt(gamma * p_R / rho_R)

        # 对每个特征场应用熵修复
        abs_lambda1 = _entropy_fix_eigenvalue(lambda1, u_L - a_L, u_R - a_R)
        abs_lambda2 = _entropy_fix_eigenvalue(lambda2, u_L, u_R)
        abs_lambda3 = _entropy_fix_eigenvalue(lambda3, u_L + a_L, u_R + a_R)
    else:
        abs_lambda1 = np.abs(lambda1)
        abs_lambda2 = np.abs(lambda2)
        abs_lambda3 = np.abs(lambda3)

    dissipation = alpha1 * abs_lambda1 * r1 + \
        alpha2 * abs_lambda2 * r2 + \
        alpha3 * abs_lambda3 * r3

    return dissipation


def roe_step(U, dx, dt, gamma=GAMMA, entropy_fix=False):
    """
    执行一步Roe格式时间推进 (近似Riemann求解器)。

    依据: Roe (1981) [7], Toro (2009) [2] 第11章

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比
        entropy_fix: 是否启用Harten熵修复 (默认False)
                     防止跨音速稀疏波产生膨胀激波

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    F = compute_flux(U, gamma)
    U_new = np.zeros_like(U)

    for i in range(1, n - 1):
        D_right = _roe_average(U[i, :], U[i + 1, :],
                               gamma, entropy_fix=entropy_fix)
        D_left = _roe_average(U[i - 1, :], U[i, :],
                              gamma, entropy_fix=entropy_fix)

        U_new[i, :] = U[i, :] - (dt / dx) * (
            0.5 * (F[i + 1, :] + F[i, :]) - 0.5 * D_right -
            (0.5 * (F[i, :] + F[i - 1, :]) - 0.5 * D_left)
        )

    return U_new


# =============================================================================
# 格式8: HLLC 格式 (恢复接触间断的HLL)
# 依据: Toro et al. (1994) [8], Toro (2009) [2] 第10章
# 通量: 三波模型 (左波、接触间断、右波)
# =============================================================================
def _hllc_flux(U_L, U_R, gamma=GAMMA, entropy_fix=False):
    """
    计算HLLC Riemann求解器通量。

    依据: Toro et al. (1994) [8], Toro (2009) [2] 第10章

    参数:
        U_L, U_R: 左右状态
        gamma: 比热比
        entropy_fix: 是否启用Harten熵修复 (默认False)
                     在稀疏波区域对波速进行熵修正

    返回:
        F: HLLC通量 (3,)
    """
    rho_L, u_L, p_L = conservative_to_primitive(U_L, gamma)
    rho_R, u_R, p_R = conservative_to_primitive(U_R, gamma)
    c_L = np.sqrt(gamma * p_L / rho_L)
    c_R = np.sqrt(gamma * p_R / rho_R)

    PVRS = 0.5 * (p_L + p_R) - 0.5 * (u_R - u_L) * 0.5 * \
        (rho_L + rho_R) * 0.5 * (c_L + c_R)
    p_star = max(1e-10, PVRS)

    q_L = 1.0 if p_star <= p_L else np.sqrt(
        1.0 + (gamma + 1.0) / (2.0 * gamma) * (p_star / p_L - 1.0))
    q_R = 1.0 if p_star <= p_R else np.sqrt(
        1.0 + (gamma + 1.0) / (2.0 * gamma) * (p_star / p_R - 1.0))

    S_L = u_L - c_L * q_L
    S_R = u_R + c_R * q_R

    # Harten熵修复 (Harten 1983, Toro 2009 第11章)
    # 对稀疏波 (p_star < p_side) 的波速进行修正, 防止膨胀激波
    if entropy_fix:
        delta = 1e-10
        # 左波: 如果是稀疏波 (p_star < p_L), 修正 S_L
        if p_star < p_L:
            S_L_head = u_L - c_L  # 稀疏波头速度
            # 如果波头跨越音速 (u_L - c_L < 0 < S_L), 应用熵修复
            if S_L_head < 0 and S_L > 0:
                eps = max(delta, S_L - S_L_head)
                S_L = (S_L ** 2 + eps ** 2) / (2.0 * eps) - \
                    (S_L_head ** 2 + eps ** 2) / (2.0 * eps)
                S_L = min(S_L, S_L_head)  # 确保修正后的波速不大于波头
        # 右波: 如果是稀疏波 (p_star < p_R), 修正 S_R
        if p_star < p_R:
            S_R_head = u_R + c_R  # 稀疏波头速度
            if S_R_head > 0 and S_R < 0:
                eps = max(delta, S_R_head - S_R)
                S_R = (S_R ** 2 + eps ** 2) / (2.0 * eps)
                S_R = max(S_R, S_R_head)

    S_star = (p_R - p_L + rho_L * u_L * (S_L - u_L) - rho_R * u_R *
              (S_R - u_R)) / (rho_L * (S_L - u_L) - rho_R * (S_R - u_R))

    F_L = np.array([rho_L * u_L, rho_L * u_L ** 2 + p_L,
                    u_L * (rho_L * (p_L / ((gamma - 1.0) * rho_L) + 0.5 * u_L ** 2) + p_L)])
    F_R = np.array([rho_R * u_R, rho_R * u_R ** 2 + p_R,
                    u_R * (rho_R * (p_R / ((gamma - 1.0) * rho_R) + 0.5 * u_R ** 2) + p_R)])

    if S_L >= 0:
        return F_L
    elif S_star >= 0:
        D_star = rho_L * (S_L - u_L) / (S_L - S_star)
        U_star = D_star * np.array([1.0, S_star, p_L / ((gamma - 1.0)
                                   * rho_L) + 0.5 * (u_L ** 2 + (S_L - u_L) * (S_star - u_L))])
        return F_L + S_L * (U_star - U_L)
    elif S_R >= 0:
        D_star = rho_R * (S_R - u_R) / (S_R - S_star)
        U_star = D_star * np.array([1.0, S_star, p_R / ((gamma - 1.0)
                                   * rho_R) + 0.5 * (u_R ** 2 + (S_R - u_R) * (S_star - u_R))])
        return F_R + S_R * (U_star - U_R)
    else:
        return F_R


def hllc_step(U, dx, dt, gamma=GAMMA, entropy_fix=False):
    """
    执行一步HLLC格式时间推进。

    依据: Toro et al. (1994) [8], Toro (2009) [2] 第10章

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比
        entropy_fix: 是否启用Harten熵修复 (默认False)

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    U_new = U.copy()

    for i in range(1, n - 1):
        F_right = _hllc_flux(U[i, :], U[i + 1, :], gamma,
                             entropy_fix=entropy_fix)
        F_left = _hllc_flux(U[i - 1, :], U[i, :], gamma,
                            entropy_fix=entropy_fix)
        U_new[i, :] = U[i, :] - (dt / dx) * (F_right - F_left)

    return U_new


# =============================================================================
# 格式9: TVD 格式 (Roe通量 + Minmod限制器)
# 依据: Harten (1983) [13], Toro (2009) [2] 第11章, LeVeque (2002) [10]
# 数值通量: F_{i+1/2} = F_{i+1/2}^{Roe} + TVD修正项
# Minmod限制器: minmod(a,b) = sgn(a)*max(0, min(|a|,|b|))
# =============================================================================

def minmod_limiter(a, b):
    """
    Minmod限制器。

    minmod(a, b) = sgn(a) * max(0, min(|a|, sgn(a)*b))
                 = 0.5 * (sgn(a) + sgn(b)) * min(|a|, |b|)

    依据: Harten (1983) [13], Toro (2009) [2] 第11章

    参数:
        a, b: 标量或数组
    返回:
        minmod(a, b)
    """
    return 0.5 * (np.sign(a) + np.sign(b)) * np.minimum(np.abs(a), np.abs(b))


def _tvd_riemann_flux(U_L, U_R, gamma=GAMMA):
    """
    计算Roe Riemann求解器通量 (用于TVD格式的低阶通量)。

    依据: Roe (1981) [7], Toro (2009) [2] 第11章

    F_{i+1/2}^{Roe} = 0.5*(F_L + F_R) - 0.5*|A~|*(U_R - U_L)

    参数:
        U_L, U_R: 左右状态
        gamma: 比热比
    返回:
        F: Roe通量
    """
    F_L = compute_flux(U_L, gamma)
    F_R = compute_flux(U_R, gamma)

    dissipation = _roe_average(U_L, U_R, gamma)

    return 0.5 * (F_L + F_R) - 0.5 * dissipation


def tvd_minmod_step(U, dx, dt, gamma=GAMMA):
    """
    执行一步TVD格式时间推进 (Roe通量 + Minmod限制器)。

    依据: Harten (1983) [13], Toro (2009) [2] 第11章

    MUSCL重构:
        U_{i+1/2}^L = U_i + 0.5 * phi(r_i) * (U_i - U_{i-1})
        U_{i+1/2}^R = U_{i+1} - 0.5 * phi(r_{i+1}) * (U_{i+2} - U_{i+1})

    其中 phi(r) = minmod(1, r) 为Minmod限制器。

    Roe通量:
        F_{i+1/2} = F^{Roe}(U_{i+1/2}^L, U_{i+1/2}^R)

    时间推进:
        U_i^{n+1} = U_i^n - (dt/dx) * (F_{i+1/2} - F_{i-1/2})

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
    n = len(U)
    U_new = U.copy()

    # 计算斜率: delta_i = U_i - U_{i-1}
    delta = np.diff(U, axis=0)  # 形状 (n-1, 3), delta[i] = U[i+1] - U[i]

    # 计算梯度比 r_i = delta_{i-1} / delta_i (逐元素)
    # 为避免除零, 添加小量
    r = np.zeros_like(delta)
    for var in range(3):
        for i in range(1, n - 2):
            if abs(delta[i, var]) > 1e-15:
                r[i, var] = delta[i - 1, var] / delta[i, var]
            else:
                r[i, var] = 0.0

    # 计算限制器 phi(r) = minmod(1, r)
    phi = np.zeros_like(delta)
    for var in range(3):
        phi[:, var] = minmod_limiter(np.ones(n - 1), r[:, var])

    # MUSCL重构界面值
    # U_{i+1/2}^L = U_i + 0.5 * phi_i * delta_i
    # U_{i+1/2}^R = U_{i+1} - 0.5 * phi_{i+1} * delta_{i+1}
    U_left_half = np.zeros((n - 1, 3))
    U_right_half = np.zeros((n - 1, 3))

    for i in range(n - 1):
        # 左界面值
        U_left_half[i, :] = U[i, :] + 0.5 * phi[i, :] * delta[i, :]
        # 右界面值
        if i + 1 < n - 1:
            U_right_half[i, :] = U[i + 1, :] - \
                0.5 * phi[i + 1, :] * delta[i + 1, :]
        else:
            U_right_half[i, :] = U[i + 1, :]  # 右边界用一阶外推

    # 确保密度和压力为正 (TVD格式的额外保护)
    rho_l, _, p_l = conservative_to_primitive(U_left_half, gamma)
    rho_r, _, p_r = conservative_to_primitive(U_right_half, gamma)

    # 如果重构导致负密度/压力, 退化为一阶
    for i in range(n - 1):
        if rho_l[i] < 1e-10 or p_l[i] < 1e-10:
            U_left_half[i, :] = U[i, :]
        if rho_r[i] < 1e-10 or p_r[i] < 1e-10:
            U_right_half[i, :] = U[i + 1, :]

    # 计算 Roe 通量
    U_new_interior = U[1:-1, :].copy()
    for i in range(1, n - 1):
        # 界面 i+1/2 和 i-1/2 的 Roe 通量
        F_right = _tvd_riemann_flux(
            U_left_half[i, :], U_right_half[i, :], gamma)
        F_left = _tvd_riemann_flux(
            U_left_half[i - 1, :], U_right_half[i - 1, :], gamma)
        U_new_interior[i - 1, :] = U[i, :] - (dt / dx) * (F_right - F_left)

    U_new[1:-1, :] = U_new_interior

    return U_new


# =============================================================================
# 格式注册表 (统一接口)
# 依据: Build文档 §4.2, §5.3
# =============================================================================
FD_SCHEMES = {
    'lax_friedrichs': {
        'func': lax_friedrichs_step,
        'order': 1,
        'description': 'Lax-Friedrichs格式 (一阶中心耗散)',
        'reference': 'Sod (1978) [1], Laney (1998) [3]'
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
        'reference': 'Laney (1998) [3], LeVeque (1992) [5]'
    },
    'rusanov': {
        'func': rusanov_step,
        'order': 1,
        'description': 'Rusanov格式 (局部Lax-Friedrichs)',
        'reference': 'Toro (2009) [2], Rusanov (1961)'
    },
    'godunov': {
        'func': godunov_step,
        'order': 1,
        'description': 'Godunov格式 (精确Riemann求解器)',
        'reference': 'Toro (2009) [2], Godunov (1959)'
    },
    'roe': {
        'func': roe_step,
        'order': 1,
        'description': 'Roe格式 (近似Riemann求解器)',
        'reference': 'Roe (1981) [7], Toro (2009) [2]'
    },
    'hllc': {
        'func': hllc_step,
        'order': 1,
        'description': 'HLLC格式 (恢复接触间断)',
        'reference': 'Toro et al. (1994) [8], Toro (2009) [2]'
    },
    'tvd_minmod': {
        'func': tvd_minmod_step,
        'order': 2,
        'description': 'TVD格式 (Roe通量 + Minmod限制器)',
        'reference': 'Harten (1983) [13], Toro (2009) [2]'
    }
}


def solve_with_scheme(
        scheme_name,
        U,
        x,
        dx,
        t_final=0.2,
        cfl=0.8,
        gamma=GAMMA):
    """
    使用指定有限差分格式求解Sod激波管问题。

    依据: Build文档 §3.3 (步骤4), §5.3, §5.5

    参数:
        scheme_name: 格式名称
        U: 初始守恒变量
        x: 网格坐标数组
        dx: 网格间距
        t_final: 仿真终止时间 (默认0.2)
        cfl: CFL数 (默认0.8)
        gamma: 比热比

    返回:
        U: 最终守恒变量
        t: 最终时间
        n_steps: 迭代步数
    """
    from .time_marcher import compute_dt, check_conservation
    from .boundary_handler import apply_boundary_condition

    if scheme_name not in FD_SCHEMES:
        raise ValueError(f"未知格式: {scheme_name}. 可选: {list(FD_SCHEMES.keys())}")

    scheme = FD_SCHEMES[scheme_name]
    step_func = scheme['func']

    # 重置MacCormack格式的交替方向计数器 (确保每次求解从头开始)
    if scheme_name == 'macormack':
        global _macormack_step_counter
        _macormack_step_counter = 0

    U = U.copy()
    U_initial = U.copy()  # 保存初始状态用于守恒性检查
    t = 0.0
    n_steps = 0

    print(f"开始求解: {scheme['description']}")
    print(f"  文献依据: {scheme['reference']}")
    print(f"  格式精度: {scheme['order']}阶")

    while t < t_final:
        dt = compute_dt(U, dx, cfl, gamma)

        if t + dt > t_final:
            dt = t_final - t

        U_new = step_func(U, dx, dt, gamma)
        U_new = apply_boundary_condition(U_new)

        U = U_new
        t += dt
        n_steps += 1

        if n_steps % 100 == 0:
            print(f"  步数: {n_steps}, 时间: {t:.4f}/{t_final}, dt: {dt:.6f}")
            # 每100步执行守恒性检查
            check_conservation(U, U_initial, dx, n_steps, gamma)

    # 最终守恒性检查
    check_conservation(U, U_initial, dx, n_steps, gamma)

    return U, t, n_steps
