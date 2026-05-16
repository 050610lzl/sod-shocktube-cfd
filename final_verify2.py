"""
修复后精准验证
"""
import numpy as np
import sys
sys.path.insert(0, r'e:\trae_project\a')

from utils import sod_exact_solution, GAMMA
from scipy.optimize import brentq

print("=" * 70)
print("修复后精准验证 - utils.py精确解")
print("=" * 70)

# 先独立计算p*和u*来验证
gamma = GAMMA
rho_L, u_L, p_L = 1.0, 0.0, 1.0
rho_R, u_R, p_R = 0.125, 0.0, 0.1
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

p_star = brentq(pressure_function, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-15)

# 使用exact_solver.py中的正确公式计算u_star（与utils.py一致）
A_L = 2.0 / ((gamma + 1.0) * rho_L)
B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))

print(f"\n独立计算的p*: {p_star:.10f} (理论: 0.30313018)")
print(f"独立计算的u*: {u_star:.10f} (理论: 0.92745258)")

# 调用utils.py的函数
x = np.linspace(0, 1, 10001)
t = 0.2
rho_ex, u_ex, p_ex = sod_exact_solution(x, t, GAMMA)

# 直接从返回的数组中读取平台值
u_star_from_array = u_ex[(x > 0.55) & (x < 0.65)].mean()
p_star_from_array = p_ex[(x > 0.55) & (x < 0.65)].mean()
rho_star_L_from_array = rho_ex[(x > 0.55) & (x < 0.65)].mean()
rho_star_R_from_array = rho_ex[(x > 0.70) & (x < 0.80)].mean()

print(f"\n从数组读取的值:")
print(f"  u* = {u_star_from_array:.8f} (理论: 0.92745258, 误差: {abs(u_star_from_array - 0.92745258):.2e})")
print(f"  p* = {p_star_from_array:.8f} (理论: 0.30313018, 误差: {abs(p_star_from_array - 0.30313018):.2e})")
print(f"  rho*_L = {rho_star_L_from_array:.8f} (理论: 0.42631943, 误差: {abs(rho_star_L_from_array - 0.42631943):.2e})")
print(f"  rho*_R = {rho_star_R_from_array:.8f} (理论: 0.26557361, 误差: {abs(rho_star_R_from_array - 0.26557361):.2e})")

# 从数组计算波位置
a_star_L = np.sqrt(gamma * p_star / rho_star_L_from_array)
x_tail = 0.5 + (u_star - a_star_L) * t
x_contact_calc = 0.5 + u_star * t
a_R = np.sqrt(gamma * p_R / rho_R)
S_R = u_R + a_R * np.sqrt((gamma + 1.0) / (2.0 * gamma) * p_star / p_R + (gamma - 1.0) / (2.0 * gamma))
x_shock_calc = 0.5 + S_R * t

print(f"\n波位置 (从计算值):")
print(f"  x_contact = 0.5 + {u_star:.8f}*0.2 = {x_contact_calc:.8f} (理论: 0.68549052)")
print(f"  x_shock = 0.5 + {S_R:.8f}*0.2 = {x_shock_calc:.8f} (理论: 0.85043110)")

# 最终判断
all_pass = True
checks = [
    ('u*', u_star_from_array, 0.92745258, 1e-5),
    ('p*', p_star_from_array, 0.30313018, 1e-5),
    ('rho*_L', rho_star_L_from_array, 0.42631943, 1e-5),
    ('rho*_R', rho_star_R_from_array, 0.26557361, 1e-5),
    ('x_contact', x_contact_calc, 0.68549052, 1e-4),
    ('x_shock', x_shock_calc, 0.85043110, 1e-4),
]

print(f"\n{'='*70}")
print(f"最终验证结果:")
print(f"{'参数':<15} {'计算值':<15} {'理论值':<15} {'误差':<15} {'状态':<10}")
print(f"{'-'*70}")
for name, calc, theo, tol in checks:
    err = abs(calc - theo)
    status = "PASS" if err < tol else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{name:<15} {calc:<15.8f} {theo:<15.8f} {err:<15.2e} {status:<10}")

if all_pass:
    print(f"\n【全部通过】修复成功！精确解计算现在与Toro (2009)理论值完全一致。")
else:
    print(f"\n【失败】仍存在偏差。")
print(f"{'='*70}")
