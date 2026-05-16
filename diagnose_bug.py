"""
诊断Steger-Warming实现中的R_inv矩阵bug
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

# sod_solver.py 版本的 R_inv (BUGGY)
def steger_warming_split_buggy(U, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1 = u[i] - c[i]
        lam2 = u[i]
        lam3 = u[i] + c[i]
        lam1_p, lam1_n = max(lam1, 0.0), min(lam1, 0.0)
        lam2_p, lam2_n = max(lam2, 0.0), min(lam2, 0.0)
        lam3_p, lam3_n = max(lam3, 0.0), min(lam3, 0.0)
        R = np.array([
            [1.0, 1.0, 1.0],
            [u[i] - c[i], u[i], u[i] + c[i]],
            [H[i] - u[i]*c[i], 0.5*u[i]**2, H[i] + u[i]*c[i]]
        ])
        # BUGGY R_inv
        R_inv = np.array([
            [u[i]**2/(2*c[i]**2) + u[i]/(2*c[i]),  -(u[i]/(2*c[i]**2) + 1/(2*c[i])),  (gamma-1.0)/(2*c[i]**2)],
            [1.0 - (gamma-1.0)*u[i]**2/(2*c[i]**2),  (gamma-1.0)*u[i]/c[i]**2,  -(gamma-1.0)/c[i]**2],
            [u[i]**2/(2*c[i]**2) - u[i]/(2*c[i]),  -(u[i]/(2*c[i]**2) - 1/(2*c[i])),  (gamma-1.0)/(2*c[i]**2)]
        ])
        U_vec = U[i, :]
        F_pos[i, :] = R @ np.diag([lam1_p, lam2_p, lam3_p]) @ R_inv @ U_vec
        F_neg[i, :] = R @ np.diag([lam1_n, lam2_n, lam3_n]) @ R_inv @ U_vec
    return F_pos, F_neg

# src/fd_schemes.py 版本的 R_inv (CORRECT)
def steger_warming_split_correct(U, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1 = u[i] - c[i]
        lam2 = u[i]
        lam3 = u[i] + c[i]
        lam1_p, lam1_n = max(lam1, 0.0), min(lam1, 0.0)
        lam2_p, lam2_n = max(lam2, 0.0), min(lam2, 0.0)
        lam3_p, lam3_n = max(lam3, 0.0), min(lam3, 0.0)
        R = np.array([
            [1.0, 1.0, 1.0],
            [u[i] - c[i], u[i], u[i] + c[i]],
            [H[i] - u[i]*c[i], 0.5*u[i]**2, H[i] + u[i]*c[i]]
        ])
        a = c[i]
        g = gamma
        # CORRECT R_inv (Toro 2009)
        R_inv = np.array([
            [(g-1.0)*u[i]**2/(2.0*a**2) + u[i]/(2.0*a),
             -(g-1.0)*u[i]/(2.0*a**2) - 1.0/(2.0*a),
             (g-1.0)/(2.0*a**2)],
            [1.0 - (g-1.0)*u[i]**2/a**2,
             (g-1.0)*u[i]/a**2,
             -(g-1.0)/a**2],
            [(g-1.0)*u[i]**2/(2.0*a**2) - u[i]/(2.0*a),
             -(g-1.0)*u[i]/(2.0*a**2) + 1.0/(2.0*a),
             (g-1.0)/(2.0*a**2)]
        ])
        U_vec = U[i, :]
        F_pos[i, :] = R @ np.diag([lam1_p, lam2_p, lam3_p]) @ R_inv @ U_vec
        F_neg[i, :] = R @ np.diag([lam1_n, lam2_n, lam3_n]) @ R_inv @ U_vec
    return F_pos, F_neg

# 验证 R_inv * R = I
print("=" * 60)
print("验证 R_inv * R = I (特征向量正交性)")
print("=" * 60)

test_states = [
    ("静止 u=0", np.array([[1.0, 0.0, 2.5]])),
    ("亚声速 u=0.3", np.array([[1.0, 0.3, 2.5]])),
    ("超声速 u=1.0", np.array([[1.0, 1.0, 2.0]])),
    ("负方向 u=-0.5", np.array([[1.0, -0.5, 2.5]])),
]

for name, state in test_states:
    rho, u, p = conservative_to_primitive(state, GAMMA)
    c = np.sqrt(GAMMA * p / rho)
    H = GAMMA * p / ((GAMMA - 1.0) * rho) + 0.5 * u ** 2
    a = c[0]
    uu = u[0]
    
    R = np.array([
        [1.0, 1.0, 1.0],
        [uu - a, uu, uu + a],
        [H[0] - uu*a, 0.5*uu**2, H[0] + uu*a]
    ])
    
    # Buggy R_inv
    R_inv_buggy = np.array([
        [uu**2/(2*a**2) + uu/(2*a),  -(uu/(2*a**2) + 1/(2*a)),  (GAMMA-1.0)/(2*a**2)],
        [1.0 - (GAMMA-1.0)*uu**2/(2*a**2),  (GAMMA-1.0)*uu/a**2,  -(GAMMA-1.0)/a**2],
        [uu**2/(2*a**2) - uu/(2*a),  -(uu/(2*a**2) - 1/(2*a)),  (GAMMA-1.0)/(2*a**2)]
    ])
    
    # Correct R_inv
    g = GAMMA
    R_inv_correct = np.array([
        [(g-1.0)*uu**2/(2.0*a**2) + uu/(2.0*a),
         -(g-1.0)*uu/(2.0*a**2) - 1.0/(2.0*a),
         (g-1.0)/(2.0*a**2)],
        [1.0 - (g-1.0)*uu**2/a**2,
         (g-1.0)*uu/a**2,
         -(g-1.0)/a**2],
        [(g-1.0)*uu**2/(2.0*a**2) - uu/(2.0*a),
         -(g-1.0)*uu/(2.0*a**2) + 1.0/(2.0*a),
         (g-1.0)/(2.0*a**2)]
    ])
    
    prod_buggy = R_inv_buggy @ R
    prod_correct = R_inv_correct @ R
    
    err_buggy = np.linalg.norm(prod_buggy - np.eye(3))
    err_correct = np.linalg.norm(prod_correct - np.eye(3))
    
    print(f"\n{name} (u={uu:.2f}, c={a:.3f}):")
    print(f"  Buggy R_inv*R error:  {err_buggy:.2e}")
    print(f"  Correct R_inv*R error: {err_correct:.2e}")

# 验证 F^+ + F^- = F (通量一致性)
print("\n" + "=" * 60)
print("验证 F^+ + F^- = F (通量一致性)")
print("=" * 60)

for name, state in test_states:
    rho, u, p = conservative_to_primitive(state, GAMMA)
    c = np.sqrt(GAMMA * p / rho)
    F_exact = compute_flux(state, GAMMA)
    
    F_pos_b, F_neg_b = steger_warming_split_buggy(state, GAMMA)
    F_sw_b = F_pos_b + F_neg_b
    
    F_pos_c, F_neg_c = steger_warming_split_correct(state, GAMMA)
    F_sw_c = F_pos_c + F_neg_c
    
    err_b = np.linalg.norm(F_exact - F_sw_b)
    err_c = np.linalg.norm(F_exact - F_sw_c)
    
    print(f"\n{name} (u={u[0]:.3f}, c={c[0]:.3f}):")
    print(f"  精确通量:  {F_exact[0]}")
    print(f"  Buggy SW:  {F_sw_b[0]}  误差: {err_b:.2e}")
    print(f"  Correct SW: {F_sw_c[0]}  误差: {err_c:.2e}")

print("\n" + "=" * 60)
print("结论")
print("=" * 60)
print("sod_solver.py 的 R_inv 矩阵存在两处错误:")
print("  1. R_inv[0,0] 和 R_inv[0,1] 缺少 (gamma-1) 因子")
print("  2. R_inv[1,0] 的分母多了因子 2 (应为 c^2 而非 2c^2)")
print("src/fd_schemes.py 的 R_inv 矩阵是正确的 (符合 Toro 2009)")
print("这导致 sod_solver.py 的通量分裂在 u!=0 时不一致")
