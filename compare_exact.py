"""
对比诊断脚本：比较utils.py和src/exact_solver.py的精确解计算
"""
import numpy as np
from scipy.optimize import brentq
import sys
sys.path.insert(0, r'e:\trae_project\a')

from utils import sod_exact_solution as utils_exact
from src.exact_solver import sod_exact_solution as src_exact

GAMMA = 1.4
gamma = GAMMA

# 理论参考值
THEO = {'p_star': 0.30313, 'u_star': 0.92745, 'rho_star_L': 0.42632, 'rho_star_R': 0.26557}

# 测试数据
x = np.linspace(0, 1, 1001)
t = 0.2

print("=" * 70)
print("对比utils.py和src/exact_solver.py的精确解")
print("=" * 70)

# 调用两个函数
rho_u, u_u, p_u = utils_exact(x, t, GAMMA)
rho_s, u_s, p_s = src_exact(x, t, GAMMA)

print(f"\nutils.py结果:")
print(f"  u范围: [{u_u.min():.8f}, {u_u.max():.8f}]")
print(f"  rho范围: [{rho_u.min():.8f}, {rho_u.max():.8f}]")
print(f"  p范围: [{p_u.min():.8f}, {p_u.max():.8f}]")

print(f"\nsrc/exact_solver.py结果:")
print(f"  u范围: [{u_s.min():.8f}, {u_s.max():.8f}]")
print(f"  rho范围: [{rho_s.min():.8f}, {rho_s.max():.8f}]")
print(f"  p范围: [{p_s.min():.8f}, {p_s.max():.8f}]")

# 关键对比：u的最大值
print(f"\n{'参数':<20} {'utils.py':<15} {'src/exact_solver':<15} {'理论值':<15} {'差异':<10}")
print("-" * 75)
print(f"u_max               {u_u.max():<15.8f} {u_s.max():<15.8f} {THEO['u_star']:<15.8f} {'不同' if abs(u_u.max() - u_s.max()) > 0.01 else '相同':<10}")
print(f"rho_min             {rho_u.min():<15.8f} {rho_s.min():<15.8f} {THEO['rho_star_R']:<15.8f} {'不同' if abs(rho_u.min() - rho_s.min()) > 0.01 else '相同':<10}")

# 找出差异位置
diff_idx = np.where(np.abs(u_u - u_s) > 0.01)[0]
if len(diff_idx) > 0:
    print(f"\n发现{len(diff_idx)}个位置存在显著差异")
    print(f"差异区域x范围: [{x[diff_idx[0]]:.4f}, {x[diff_idx[-1]]:.4f}]")
    
    # 在稀疏波区采样对比
    print(f"\n稀疏波区采样对比:")
    for x_pos in [0.3, 0.35, 0.4, 0.45]:
        idx = np.argmin(np.abs(x - x_pos))
        print(f"  x={x_pos:.2f}: utils.u={u_u[idx]:.6f}, src.u={u_s[idx]:.6f}, 差={abs(u_u[idx]-u_s[idx]):.6f}")
    
    # 在星号区采样对比
    print(f"\n星号区采样对比:")
    for x_pos in [0.55, 0.6, 0.65, 0.7, 0.75, 0.8]:
        idx = np.argmin(np.abs(x - x_pos))
        print(f"  x={x_pos:.2f}: utils.u={u_u[idx]:.6f}, src.u={u_s[idx]:.6f}, 差={abs(u_u[idx]-u_s[idx]):.6f}")

# 检查pressure_function的差异
print("\n" + "=" * 70)
print("检查pressure_function的差异")
print("=" * 70)

rho_L, u_L, p_L = 1.0, 0.0, 1.0
rho_R, u_R, p_R = 0.125, 0.0, 0.1
a_L = np.sqrt(gamma * p_L / rho_L)
a_R = np.sqrt(gamma * p_R / rho_R)

# utils.py的pressure_function（有bug的版本）
def pressure_function_utils(p_star):
    if p_star <= p_L:
        f_L = (2.0 * a_L / (gamma - 1.0)) * \
              ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        f_L = (p_star - p_L) / np.sqrt(A_L * (p_star + B_L))  # <-- 注意这里
    
    if p_star <= p_R:
        f_R = (2.0 * a_R / (gamma - 1.0)) * \
              ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_R = 2.0 / ((gamma + 1.0) * rho_R)
        B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
        f_R = (p_star - p_R) / np.sqrt(A_R * (p_star + B_R))  # <-- 注意这里
    
    return f_L + f_R + (u_R - u_L)

# src/exact_solver.py的pressure_function（正确版本）
def pressure_function_src(p_star):
    if p_star <= p_L:
        f_L = (2.0 * a_L / (gamma - 1.0)) * \
              ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))  # <-- 正确公式
    
    if p_star <= p_R:
        f_R = (2.0 * a_R / (gamma - 1.0)) * \
              ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_R = 2.0 / ((gamma + 1.0) * rho_R)
        B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
        f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))  # <-- 正确公式
    
    return f_L + f_R + (u_R - u_L)

p_star_utils = brentq(pressure_function_utils, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-15)
p_star_src = brentq(pressure_function_src, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-15)

print(f"utils.py计算的p*: {p_star_utils:.10f}")
print(f"src/exact_solver计算的p*: {p_star_src:.10f}")
print(f"理论p*: {THEO['p_star']:.10f}")
print(f"差异: {abs(p_star_utils - p_star_src):.2e}")

# 验证公式差异
test_p_star = 0.5  # 大于p_L和p_R，会进入激波分支
A_L = 2.0 / ((gamma + 1.0) * rho_L)
B_L = (gamma - 1.0) / (gamma + 1.0) * p_L

f_L_utils = (test_p_star - p_L) / np.sqrt(A_L * (test_p_star + B_L))
f_L_src = (test_p_star - p_L) * np.sqrt(A_L / (test_p_star + B_L))

print(f"\n验证公式差异 (p_star=0.5):")
print(f"  utils.py公式: (p*-p_L) / sqrt(A_L * (p*+B_L)) = {f_L_utils:.8f}")
print(f"  src/exact_solver公式: (p*-p_L) * sqrt(A_L / (p*+B_L)) = {f_L_src:.8f}")
print(f"  两者比值: {f_L_utils / f_L_src:.8f}")
print(f"  注意: 1/sqrt(A) = sqrt(1/A)，所以差异在于 sqrt(A) vs 1/sqrt(A)")

print("\n" + "=" * 70)
if abs(p_star_utils - THEO['p_star']) > 0.01:
    print("结论: utils.py的pressure_function存在公式错误!")
    print("根因: 激波分支使用了 (p*-p) / sqrt(A*(p*+B)) 而非 (p*-p) * sqrt(A/(p*+B))")
else:
    print("结论: utils.py和src/exact_solver.py公式一致")
print("=" * 70)
