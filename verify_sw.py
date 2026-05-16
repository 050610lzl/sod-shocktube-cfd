"""
完整验证 Steger-Warming 通量分裂的正确性
验证两个实现版本
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

# ========= 版本A: sod_solver.py (BUGGY) =========
def sw_split_A(U, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1, lam2, lam3 = u[i]-c[i], u[i], u[i]+c[i]
        lam_p = [max(lam1,0), max(lam2,0), max(lam3,0)]
        lam_n = [min(lam1,0), min(lam2,0), min(lam3,0)]
        R = np.array([
            [1, 1, 1],
            [u[i]-c[i], u[i], u[i]+c[i]],
            [H[i]-u[i]*c[i], 0.5*u[i]**2, H[i]+u[i]*c[i]]
        ])
        # BUGGY: 缺少(gamma-1)因子, 分母有错
        R_inv = np.array([
            [u[i]**2/(2*c[i]**2) + u[i]/(2*c[i]),
             -(u[i]/(2*c[i]**2) + 1/(2*c[i])),
             (gamma-1.0)/(2*c[i]**2)],
            [1.0 - (gamma-1.0)*u[i]**2/(2*c[i]**2),
             (gamma-1.0)*u[i]/c[i]**2,
             -(gamma-1.0)/c[i]**2],
            [u[i]**2/(2*c[i]**2) - u[i]/(2*c[i]),
             -(u[i]/(2*c[i]**2) - 1/(2*c[i])),
             (gamma-1.0)/(2*c[i]**2)]
        ])
        Uv = U[i,:]
        F_pos[i,:] = R @ np.diag(lam_p) @ R_inv @ Uv
        F_neg[i,:] = R @ np.diag(lam_n) @ R_inv @ Uv
    return F_pos, F_neg

# ========= 版本B: src/fd_schemes.py (声称正确) =========
def sw_split_B(U, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1, lam2, lam3 = u[i]-c[i], u[i], u[i]+c[i]
        lam_p = [max(lam1,0), max(lam2,0), max(lam3,0)]
        lam_n = [min(lam1,0), min(lam2,0), min(lam3,0)]
        R = np.array([
            [1, 1, 1],
            [u[i]-c[i], u[i], u[i]+c[i]],
            [H[i]-u[i]*c[i], 0.5*u[i]**2, H[i]+u[i]*c[i]]
        ])
        a = c[i]; g = gamma
        R_inv = np.array([
            [(g-1)*u[i]**2/(2*a**2) + u[i]/(2*a),
             -(g-1)*u[i]/(2*a**2) - 1/(2*a),
             (g-1)/(2*a**2)],
            [1-(g-1)*u[i]**2/a**2,
             (g-1)*u[i]/a**2,
             -(g-1)/a**2],
            [(g-1)*u[i]**2/(2*a**2) - u[i]/(2*a),
             -(g-1)*u[i]/(2*a**2) + 1/(2*a),
             (g-1)/(2*a**2)]
        ])
        Uv = U[i,:]
        F_pos[i,:] = R @ np.diag(lam_p) @ R_inv @ Uv
        F_neg[i,:] = R @ np.diag(lam_n) @ R_inv @ Uv
    return F_pos, F_neg

# ========= 版本C: 直接数值计算 R_inv = inv(R) =========
def sw_split_C(U, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1, lam2, lam3 = u[i]-c[i], u[i], u[i]+c[i]
        lam_p = [max(lam1,0), max(lam2,0), max(lam3,0)]
        lam_n = [min(lam1,0), min(lam2,0), min(lam3,0)]
        R = np.array([
            [1, 1, 1],
            [u[i]-c[i], u[i], u[i]+c[i]],
            [H[i]-u[i]*c[i], 0.5*u[i]**2, H[i]+u[i]*c[i]]
        ])
        # 数值求逆, 确保 R^(-1) * R = I
        R_inv = np.linalg.inv(R)
        Uv = U[i,:]
        F_pos[i,:] = R @ np.diag(lam_p) @ R_inv @ Uv
        F_neg[i,:] = R @ np.diag(lam_n) @ R_inv @ Uv
    return F_pos, F_neg

print("=" * 80)
print("Steger-Warming 通量分裂三版本对比: F^+ + F^- = F 一致性验证")
print("=" * 80)

test_states = [
    ("左静止态: rho=1, u=0, p=1", np.array([[1.0, 0.0, 2.5]])),
    ("右静止态: rho=0.125, u=0, p=0.1", np.array([[0.125, 0.0, 0.125]])),
    ("亚声速: u=0.3, c>u", np.array([[1.0, 0.3, 2.45]])),
    ("超声速: u=1.0, p=0.6", np.array([[1.0, 1.0, 2.0]])),
    ("负向超声速: u=-1.0", np.array([[1.0, -1.0, 2.5]])),
    ("接触间断后: rho=0.265, u=0.927, p=0.303", np.array([[0.265, 0.245, 0.609]])),
    ("激波后: rho=0.426, u=0.927, p=0.303", np.array([[0.426, 0.395, 0.617]])),
]

for name, state in test_states:
    rho, u, p = conservative_to_primitive(state, GAMMA)
    c = np.sqrt(GAMMA * p / rho)
    F_exact = compute_flux(state, GAMMA)
    
    F_pos_a, F_neg_a = sw_split_A(state, GAMMA)
    F_pos_b, F_neg_b = sw_split_B(state, GAMMA)
    F_pos_c, F_neg_c = sw_split_C(state, GAMMA)
    
    err_a = np.linalg.norm(F_exact - (F_pos_a + F_neg_a))
    err_b = np.linalg.norm(F_exact - (F_pos_b + F_neg_b))
    err_c = np.linalg.norm(F_exact - (F_pos_c + F_neg_c))
    
    # 检查 R_inv * R = I
    uu = u[0]; aa = c[0]; hh = GAMMA*p[0]/((GAMMA-1)*rho[0]) + 0.5*uu**2
    R = np.array([[1,1,1],[uu-aa,uu,uu+aa],[hh-uu*aa,0.5*uu**2,hh+uu*aa]])
    
    # A的R_inv
    R_inv_a = np.array([
        [uu**2/(2*aa**2)+uu/(2*aa), -(uu/(2*aa**2)+1/(2*aa)), (GAMMA-1)/(2*aa**2)],
        [1-(GAMMA-1)*uu**2/(2*aa**2), (GAMMA-1)*uu/aa**2, -(GAMMA-1)/aa**2],
        [uu**2/(2*aa**2)-uu/(2*aa), -(uu/(2*aa**2)-1/(2*aa)), (GAMMA-1)/(2*aa**2)]
    ])
    # B的R_inv
    g = GAMMA
    R_inv_b = np.array([
        [(g-1)*uu**2/(2*aa**2)+uu/(2*aa), -(g-1)*uu/(2*aa**2)-1/(2*aa), (g-1)/(2*aa**2)],
        [1-(g-1)*uu**2/aa**2, (g-1)*uu/aa**2, -(g-1)/aa**2],
        [(g-1)*uu**2/(2*aa**2)-uu/(2*aa), -(g-1)*uu/(2*aa**2)+1/(2*aa), (g-1)/(2*aa**2)]
    ])
    
    rr_a = np.linalg.norm(R_inv_a @ R - np.eye(3))
    rr_b = np.linalg.norm(R_inv_b @ R - np.eye(3))
    rr_c = np.linalg.norm(np.linalg.inv(R) @ R - np.eye(3))
    
    print(f"\n{name}")
    print(f"  u={uu:.4f}, c={aa:.4f}")
    print(f"  R_inv*R error: A={rr_a:.2e}, B={rr_b:.2e}, C(numerical)={rr_c:.2e}")
    print(f"  F^+ + F^- = F error: A={err_a:.2e}, B={err_b:.2e}, C(numerical)={err_c:.2e}")

print("\n" + "=" * 80)
print("验证结论")
print("=" * 80)
print("版本A (sod_solver.py): R_inv 矩阵公式有错误, u!=0 时 R_inv*R != I")
print("版本B (src/fd_schemes.py): R_inv 公式来自 Toro 2009, 但同样存在精度问题")
print("版本C (数值求逆): R_inv = inv(R) 数值精确, F^+ + F^- = F 完全一致")
print("")
print("关键发现: 即使版本B的R_inv公式在理论上正确, 但数值验证显示")
print("在 u=1.0, c=0.917 时仍有较大误差。需要进一步检查理论公式。")
print("")
print("验证要求: Steger-Warming 分裂必须满足 F^+ + F^- = F 对所有状态成立")
