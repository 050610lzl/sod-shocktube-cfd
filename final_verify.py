"""
最终验证脚本：确认修复后的精确解与理论值完全一致
"""
import numpy as np
import sys
sys.path.insert(0, r'e:\trae_project\a')

from utils import sod_exact_solution, GAMMA

# 理论参考值（Toro 2009经典值）
THEO = {
    'p_star': 0.30313018,
    'u_star': 0.92745258,
    'rho_star_L': 0.42631943,
    'rho_star_R': 0.26557361,
    'x_contact': 0.68549052,
    'x_shock': 0.85043110,
}

print("=" * 70)
print("修复后最终验证")
print("=" * 70)

x = np.linspace(0, 1, 1001)
t = 0.2
rho_ex, u_ex, p_ex = sod_exact_solution(x, t, GAMMA)

print(f"\n精确解关键值验证:")
print(f"  u* (平台值): {u_ex.max():.8f} (理论: {THEO['u_star']:.8f})")
print(f"  rho*_L: {rho_ex[(x > 0.55) & (x < 0.65)].mean():.8f} (理论: {THEO['rho_star_L']:.8f})")
print(f"  rho*_R: {rho_ex[(x > 0.70) & (x < 0.80)].mean():.8f} (理论: {THEO['rho_star_R']:.8f})")
print(f"  p*: {p_ex[(x > 0.55) & (x < 0.65)].mean():.8f} (理论: {THEO['p_star']:.8f})")

# 查找波位置
contact_idx = np.where(np.abs(u_ex - THEO['u_star']) < 0.01)[0]
if len(contact_idx) > 0:
    x_contact_num = x[contact_idx[-1]]
    print(f"  x_contact: {x_contact_num:.6f} (理论: {THEO['x_contact']:.6f})")

shock_idx = np.argmax(np.abs(np.diff(p_ex)))
x_shock_num = x[shock_idx]
print(f"  x_shock: {x_shock_num:.6f} (理论: {THEO['x_shock']:.6f})")

# 最终判断
u_error = abs(u_ex.max() - THEO['u_star'])
contact_error = abs(x_contact_num - THEO['x_contact']) if len(contact_idx) > 0 else 999
shock_error = abs(x_shock_num - THEO['x_shock'])

print(f"\n{'='*70}")
print(f"验证结果:")
print(f"  u*误差: {u_error:.2e} {'PASS' if u_error < 1e-5 else 'FAIL'}")
print(f"  x_contact误差: {contact_error:.2e} {'PASS' if contact_error < 1e-3 else 'FAIL'}")
print(f"  x_shock误差: {shock_error:.2e} {'PASS' if shock_error < 1e-3 else 'FAIL'}")

if u_error < 1e-5 and contact_error < 1e-3 and shock_error < 1e-3:
    print(f"\n【全部通过】修复成功！精确解计算现在与Toro (2009)理论值完全一致。")
else:
    print(f"\n【失败】仍存在偏差，需要进一步检查。")
print(f"{'='*70}")
