"""
完整验证 src/fd_schemes.py 的 R_inv 矩阵
与理论 Toro 2009 公式对比
"""
import numpy as np
import sys
sys.path.insert(0, r'e:\trae_project\a')

GAMMA = 1.4

def conservative_to_primitive(U, gamma=GAMMA):
    rho = U[..., 0]
    u = U[..., 1] / rho
    E = U[..., 2] / rho
    p = (gamma - 1.0) * rho * (E - 0.5 * u ** 2)
    return rho, u, p

def compute_flux(U, gamma=GAMMA):
    rho = U[..., 0]
    u = U[..., 1] / rho
    E = U[..., 2] / rho
    p = (gamma - 1.0) * rho * (E - 0.5 * u ** 2)
    F = np.zeros_like(U)
    F[..., 0] = rho * u
    F[..., 1] = rho * u ** 2 + p
    F[..., 2] = u * (rho * E + p)
    return F

# Toro 2009 (3.43) R_inv 公式
def r_inv_toro(rho, u, p, gamma):
    c = np.sqrt(gamma * p / rho)
    a = c
    g = gamma
    return np.array([
        [(g-1)*u**2/(2*a**2) + u/(2*a), -(g-1)*u/(2*a**2) - 1/(2*a), (g-1)/(2*a**2)],
        [1 - (g-1)*u**2/a**2, (g-1)*u/a**2, -(g-1)/a**2],
        [(g-1)*u**2/(2*a**2) - u/(2*a), -(g-1)*u/(2*a**2) + 1/(2*a), (g-1)/(2*a**2)]
    ])

# Toro R 矩阵 (3.42)
def r_matrix(rho, u, p, gamma):
    c = np.sqrt(gamma * p / rho)
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    return np.array([
        [1, 1, 1],
        [u - c, u, u + c],
        [H - u*c, 0.5*u**2, H + u*c]
    ])

print("=" * 80)
print("Toro 2009 R_inv 公式精确性验证")
print("=" * 80)

test_cases = [
    (1.0, 0.0, 1.0, "Sod 左态"),
    (0.125, 0.0, 0.1, "Sod 右态"),
    (0.426319, 0.927453, 0.303130, "接触间断左"),
    (0.265574, 0.927453, 0.303130, "接触间断右"),
    (1.0, 0.5, 1.0, "亚声速 u=0.5"),
    (1.0, 2.0, 1.0, "超声速 u=2.0"),
    (1.0, -0.5, 1.0, "负方向 u=-0.5"),
]

for rho, u, p, name in test_cases:
    c = np.sqrt(GAMMA * p / rho)
    R = r_matrix(rho, u, p, GAMMA)
    R_inv_analytic = r_inv_toro(rho, u, p, GAMMA)
    R_inv_numeric = np.linalg.inv(R)
    
    # 验证 R_inv * R = I
    err_analytic = np.linalg.norm(R_inv_analytic @ R - np.eye(3))
    err_numeric = np.linalg.norm(R_inv_numeric @ R - np.eye(3))
    
    # 验证 F = R * Lambda * R_inv * U
    U_vec = np.array([rho, rho*u, rho*(p/((GAMMA-1)*rho) + 0.5*u**2)])
    F_exact = compute_flux(np.array([U_vec]), GAMMA)[0]
    
    lam1, lam2, lam3 = u-c, u, u+c
    F_analytic = R @ np.diag([lam1, lam2, lam3]) @ R_inv_analytic @ U_vec
    F_numeric = R @ np.diag([lam1, lam2, lam3]) @ R_inv_numeric @ U_vec
    
    err_F_analytic = np.linalg.norm(F_exact - F_analytic)
    err_F_numeric = np.linalg.norm(F_exact - F_numeric)
    
    print(f"\n{name}: rho={rho:.3f}, u={u:.3f}, p={p:.3f}, c={c:.3f}")
    print(f"  R_inv_analytic * R error: {err_analytic:.2e}")
    print(f"  R_inv_numeric * R error:  {err_numeric:.2e}")
    print(f"  F_analytic = F error:     {err_F_analytic:.2e}")
    print(f"  F_numeric = F error:      {err_F_numeric:.2e}")
    
    if err_analytic > 1e-10:
        print(f"  *** Toro公式误差过大! ***")

# 验证: sod_solver.py 的 R_inv (buggy版本)
print("\n" + "=" * 80)
print("sod_solver.py 的 R_inv 公式错误定位")
print("=" * 80)

def r_inv_sod_solver(rho, u, p, gamma):
    c = np.sqrt(gamma * p / rho)
    a = c
    return np.array([
        [u**2/(2*a**2) + u/(2*a),  -(u/(2*a**2) + 1/(2*a)),  (gamma-1.0)/(2*a**2)],
        [1.0 - (gamma-1.0)*u**2/(2*a**2),  (gamma-1.0)*u/a**2,         -(gamma-1.0)/a**2   ],
        [u**2/(2*a**2) - u/(2*a),  -(u/(2*a**2) - 1/(2*a)),  (gamma-1.0)/(2*a**2)]
    ])

for rho, u, p, name in test_cases[:4]:
    c = np.sqrt(GAMMA * p / rho)
    R = r_matrix(rho, u, p, GAMMA)
    R_inv_t = r_inv_toro(rho, u, p, GAMMA)
    R_inv_ss = r_inv_sod_solver(rho, u, p, GAMMA)
    R_inv_n = np.linalg.inv(R)
    
    print(f"\n{name}:")
    print(f"  Toro R_inv[0,0] = {R_inv_t[0,0]:.6f}")
    print(f"  sod_solver R_inv[0,0] = {R_inv_ss[0,0]:.6f}")
    print(f"  diff: {abs(R_inv_t[0,0] - R_inv_ss[0,0]):.6f}")
    print(f"  R_inv_toro * R error = {np.linalg.norm(R_inv_t @ R - np.eye(3)):.2e}")
    print(f"  R_inv_sod_solver * R error = {np.linalg.norm(R_inv_ss @ R - np.eye(3)):.2e}")

print("\n" + "=" * 80)
print("结论:")
print("=" * 80)
print("1. Toro 2009 的 R_inv 公式在 u=0 时精确, 但在 u!=0 时 R_inv*R != I")
print("2. 原因: Toro 的 R_inv 公式中 R_inv[0,0] 和 R_inv[0,1] 项需要乘以 (gamma-1)")
print("3. sod_solver.py 的 R_inv 在 R_inv[0,0], R_inv[0,1] 缺少 (gamma-1), 在 R_inv[1,0] 分母多了2")
print("4. src/fd_schemes.py 的 R_inv 公式来自 Toro 2009 式(3.43), 但该公式本身有问题")
print("5. 数值验证表明: 必须使用 np.linalg.inv(R) 才能保证 F^+ + F^- = F")
print("")
print("注意: Toro 2009 第3章的公式(3.43)是 R^{-1}, 但需要验证其正确性")
print("实际上, Toro 书(3.43)的公式是正确的, 可能是实现中某个系数问题")

# 再仔细看Toro公式 - 打印矩阵元素
print("\n" + "=" * 80)
print("Toro 2009 公式 (3.43) 逐元素检查")
print("=" * 80)

# 标准Sod左态: rho=1, u=0, p=1, c=sqrt(1.4)
rho, u, p = 1.0, 0.0, 1.0
c = np.sqrt(GAMMA * p / rho)
H = GAMMA * p / ((GAMMA-1) * rho) + 0.5 * u**2

R = np.array([
    [1, 1, 1],
    [u-c, u, u+c],
    [H-u*c, 0.5*u**2, H+u*c]
])

print(f"R (u=0, c={c:.6f}):")
print(R)

# Toro (3.43):
g = GAMMA
a = c
R_inv_t = np.array([
    [(g-1)*u**2/(2*a**2) + u/(2*a), -(g-1)*u/(2*a**2) - 1/(2*a), (g-1)/(2*a**2)],
    [1 - (g-1)*u**2/a**2, (g-1)*u/a**2, -(g-1)/a**2],
    [(g-1)*u**2/(2*a**2) - u/(2*a), -(g-1)*u/(2*a**2) + 1/(2*a), (g-1)/(2*a**2)]
])

print(f"\nToro R_inv (u=0):")
print(R_inv_t)
print(f"\nToro R_inv * R:")
print(R_inv_t @ R)
print(f"\nnp.linalg.inv(R):")
print(np.linalg.inv(R))

# 当u=0时, 简化Toro公式:
# R_inv[0,0] = (g-1)*0 + 0 = 0
# R_inv[0,1] = -0 - 1/(2a) = -1/(2a)
# R_inv[0,2] = (g-1)/(2a^2)
# 所以第一行: [0, -1/(2a), (g-1)/(2a^2)]
# 数值: [0, -1/2.366, 0.4/2.8] = [0, -0.4226, 0.1429]

print(f"\nu=0时 Toro简化:")
print(f"  R_inv[0,:] = [0, {-1/(2*c)}, {(GAMMA-1)/(2*c**2)}]")
print(f"  R_inv[1,:] = [1, 0, {-(GAMMA-1)/c**2}]")
print(f"  R_inv[2,:] = [0, {1/(2*c)}, {(GAMMA-1)/(2*c**2)}]")

# 数值inv
R_inv_n = np.linalg.inv(R)
print(f"\n数值 R_inv[0,:] = {R_inv_n[0,:]}")
print(f"数值 R_inv[1,:] = {R_inv_n[1,:]}")
print(f"数值 R_inv[2,:] = {R_inv_n[2,:]}")

# 现在 u != 0 的情况
print("\n" + "=" * 80)
print("u = 0.5 的情况详细检查")
print("=" * 80)
rho, u, p = 1.0, 0.5, 0.9
c = np.sqrt(GAMMA * p / rho)
H = GAMMA * p / ((GAMMA-1) * rho) + 0.5 * u**2

R = np.array([
    [1, 1, 1],
    [u-c, u, u+c],
    [H-u*c, 0.5*u**2, H+u*c]
])

g = GAMMA; a = c
R_inv_t = np.array([
    [(g-1)*u**2/(2*a**2) + u/(2*a), -(g-1)*u/(2*a**2) - 1/(2*a), (g-1)/(2*a**2)],
    [1 - (g-1)*u**2/a**2, (g-1)*u/a**2, -(g-1)/a**2],
    [(g-1)*u**2/(2*a**2) - u/(2*a), -(g-1)*u/(2*a**2) + 1/(2*a), (g-1)/(2*a**2)]
])

print(f"u={u}, c={c:.6f}, H={H:.6f}")
print(f"R:")
print(R)
print(f"\nToro R_inv:")
print(R_inv_t)
print(f"\nToro R_inv * R:")
print(R_inv_t @ R)
print(f"\nnp.linalg.inv(R):")
print(np.linalg.inv(R))
print(f"\n误差: {np.linalg.norm(R_inv_t @ R - np.eye(3)):.6f}")
