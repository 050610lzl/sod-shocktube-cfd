"""
详细验证 R_inv 解析公式
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

# Steger-Warming 正确实现: 使用 np.linalg.inv(R)
def steger_warming_numerical(U, gamma=GAMMA):
    """Steger-Warming 分裂, 使用数值求逆 R_inv = inv(R)"""
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    H = gamma * p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    n = len(U)
    F_pos = np.zeros_like(U)
    F_neg = np.zeros_like(U)
    for i in range(n):
        lam1, lam2, lam3 = u[i]-c[i], u[i], u[i]+c[i]
        R = np.array([
            [1, 1, 1],
            [u[i]-c[i], u[i], u[i]+c[i]],
            [H[i]-u[i]*c[i], 0.5*u[i]**2, H[i]+u[i]*c[i]]
        ])
        R_inv = np.linalg.inv(R)  # 数值精确求逆
        Uv = U[i,:]
        F_pos[i,:] = R @ np.diag([max(lam1,0), max(lam2,0), max(lam3,0)]) @ R_inv @ Uv
        F_neg[i,:] = R @ np.diag([min(lam1,0), min(lam2,0), min(lam3,0)]) @ R_inv @ Uv
    return F_pos, F_neg

def upwind_step_correct(U, dx, dt, gamma=GAMMA):
    """一阶迎风格式时间推进, 使用数值精确的SW分裂"""
    n = len(U)
    F_pos, F_neg = steger_warming_numerical(U, gamma)
    U_new = U.copy()
    for i in range(1, n - 1):
        U_new[i, :] = U[i, :] - (dt / dx) * (
            (F_pos[i, :] - F_pos[i - 1, :]) +
            (F_neg[i + 1, :] - F_neg[i, :])
        )
    # 边界条件
    U_new[0, :] = U_new[1, :]
    U_new[-1, :] = U_new[-2, :]
    return U_new

def generate_mesh(n_points=100, x_left=0.0, x_right=1.0):
    x = np.linspace(x_left, x_right, n_points)
    dx = x[1] - x[0]
    return x, dx

def initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5):
    n_points = len(x)
    U = np.zeros((n_points, 3))
    left_state = {'rho': 1.0, 'u': 0.0, 'p': 1.0}
    right_state = {'rho': 0.125, 'u': 0.0, 'p': 0.1}
    for i in range(n_points):
        if x[i] < diaphragm_pos:
            rho, u, p = left_state['rho'], left_state['u'], left_state['p']
        else:
            rho, u, p = right_state['rho'], right_state['u'], right_state['p']
        E = p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
        U[i, 0] = rho
        U[i, 1] = rho * u
        U[i, 2] = rho * E
    return U

def compute_dt(U, dx, cfl=0.8, gamma=GAMMA):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(gamma * p / rho)
    lambda_max = np.max(np.abs(u) + c)
    if lambda_max < 1e-15:
        lambda_max = 1e-15
    return cfl * dx / lambda_max

def solve_upwind_correct(x, dx, U0, t_final=0.2, cfl=0.8, gamma=GAMMA):
    """使用数值精确SW分裂的迎风格式"""
    U = U0.copy()
    t = 0.0
    n_steps = 0
    while t < t_final:
        dt = compute_dt(U, dx, cfl, gamma)
        if t + dt > t_final:
            dt = t_final - t
        U = upwind_step_correct(U, dx, dt, gamma)
        t += dt
        n_steps += 1
    return U, t, n_steps

from scipy.optimize import brentq

def sod_exact_solution(x, t, gamma=GAMMA):
    rho_L, u_L, p_L = 1.0, 0.0, 1.0
    rho_R, u_R, p_R = 0.125, 0.0, 0.1
    a_L = np.sqrt(gamma * p_L / rho_L)
    a_R = np.sqrt(gamma * p_R / rho_R)
    def pressure_function(p_star):
        if p_star <= p_L:
            f_L = (2.0 * a_L / (gamma - 1.0)) * ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_L = 2.0 / ((gamma + 1.0) * rho_L)
            B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
            f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))
        if p_star <= p_R:
            f_R = (2.0 * a_R / (gamma - 1.0)) * ((p_star / p_R) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        else:
            A_R = 2.0 / ((gamma + 1.0) * rho_R)
            B_R = (gamma - 1.0) / (gamma + 1.0) * p_R
            f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))
        return f_L + f_R + (u_R - u_L)
    p_star = brentq(pressure_function, 1e-10, max(p_L, p_R) * 2.0, xtol=1e-15)
    if p_star <= p_L:
        u_star = u_L - (2.0 * a_L / (gamma - 1.0)) * ((p_star / p_L) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
    else:
        A_L = 2.0 / ((gamma + 1.0) * rho_L)
        B_L = (gamma - 1.0) / (gamma + 1.0) * p_L
        u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))
    if p_star <= p_L:
        rho_star_L = rho_L * (p_star / p_L) ** (1.0 / gamma)
    else:
        rho_star_L = rho_L * (p_star / p_L + (gamma - 1.0) / (gamma + 1.0)) / (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_L)
    if p_star <= p_R:
        rho_star_R = rho_R * (p_star / p_R) ** (1.0 / gamma)
    else:
        rho_star_R = rho_R * (p_star / p_R + (gamma - 1.0) / (gamma + 1.0)) / (1.0 + (gamma - 1.0) / (gamma + 1.0) * p_star / p_R)
    x_head = 0.5 - a_L * t
    x_tail_L = 0.5 + (u_star - np.sqrt(gamma * p_star / rho_star_L)) * t
    x_contact = 0.5 + u_star * t
    if p_star > p_R:
        S_R = u_R + a_R * np.sqrt((gamma + 1.0) / (2.0 * gamma) * p_star / p_R + (gamma - 1.0) / (2.0 * gamma))
    else:
        S_R = u_R + a_R
    x_shock = 0.5 + S_R * t
    n = len(x)
    rho_exact = np.zeros(n)
    u_exact = np.zeros(n)
    p_exact = np.zeros(n)
    for i in range(n):
        xi = x[i]
        if xi <= x_head:
            rho_exact[i], u_exact[i], p_exact[i] = rho_L, u_L, p_L
        elif xi <= x_tail_L:
            xi_local = (xi - 0.5) / t
            u_val = 2.0 / (gamma + 1.0) * (a_L + xi_local)
            a_val = a_L - (gamma - 1.0) / 2.0 * (u_val - u_L)
            rho_exact[i] = rho_L * (a_val / a_L) ** (2.0 / (gamma - 1.0))
            u_exact[i] = u_val
            p_exact[i] = p_L * (a_val / a_L) ** (2.0 * gamma / (gamma - 1.0))
        elif xi <= x_contact:
            rho_exact[i], u_exact[i], p_exact[i] = rho_star_L, u_star, p_star
        elif xi <= x_shock:
            rho_exact[i], u_exact[i], p_exact[i] = rho_star_R, u_star, p_star
        else:
            rho_exact[i], u_exact[i], p_exact[i] = rho_R, u_R, p_R
    return rho_exact, u_exact, p_exact

def compute_errors(U, x, t, gamma=GAMMA):
    rho_num, u_num, p_num = conservative_to_primitive(U, gamma)
    rho_ex, u_ex, p_ex = sod_exact_solution(x, t, gamma)
    errors = {}
    for var_name, num, ex in [('rho', rho_num, rho_ex), ('u', u_num, u_ex), ('p', p_num, p_ex)]:
        errors[var_name] = {
            'L1': np.mean(np.abs(num - ex)),
            'L2': np.sqrt(np.mean((num - ex)**2)),
            'Linf': np.max(np.abs(num - ex))
        }
    return errors

# ================================================================
# 运行数值精确版迎风格式
# ================================================================
print("=" * 60)
print("使用数值精确 R_inv = inv(R) 的迎风格式验证")
print("=" * 60)

resolutions = [50, 100, 200, 400, 800]
results = {}

for N in resolutions:
    x, dx = generate_mesh(N)
    U0 = initialize_flow(x)
    U_final, t_f, n_steps = solve_upwind_correct(x, dx, U0, 0.2, 0.8, GAMMA)
    errors = compute_errors(U_final, x, t_f, GAMMA)
    results[N] = {'x': x, 'U': U_final, 'errors': errors, 't': t_f, 'n_steps': n_steps}
    
    rho_n, u_n, p_n = conservative_to_primitive(U_final, GAMMA)
    print(f"\nN={N}: {n_steps}步")
    print(f"  rho: L1={errors['rho']['L1']:.6e}, L2={errors['rho']['L2']:.6e}, Linf={errors['rho']['Linf']:.6e}")
    print(f"  u:   L1={errors['u']['L1']:.6e}, L2={errors['u']['L2']:.6e}, Linf={errors['u']['Linf']:.6e}")
    print(f"  p:   L1={errors['p']['L1']:.6e}, L2={errors['p']['L2']:.6e}, Linf={errors['p']['Linf']:.6e}")

# 计算收敛阶
print("\n" + "=" * 60)
print("网格收敛率分析")
print("=" * 60)
dxs = [1.0/N for N in resolutions]
for var in ['rho', 'u', 'p']:
    l1_vals = [results[N]['errors'][var]['L1'] for N in resolutions]
    p_order = np.log(l1_vals[-1] / l1_vals[0]) / np.log(dxs[-1] / dxs[0])
    print(f"  {var}: L1收敛阶 = {p_order:.2f}")

# 验证: 与 sod_solver.py 对比 (buggy)
print("\n" + "=" * 60)
print("与原 sod_solver.py (buggy) 对比")
print("=" * 60)

from sod_solver import steger_warming_split as sw_buggy

x_test, dx_test = generate_mesh(100)
U0_test = initialize_flow(x_test)

# 用buggy版本
U_buggy = U0_test.copy()
t = 0.0
n_steps = 0
while t < 0.2:
    dt = compute_dt(U_buggy, dx_test, 0.8, GAMMA)
    if t + dt > 0.2:
        dt = 0.2 - t
    F_pos, F_neg = sw_buggy(U_buggy, GAMMA)
    U_new = U_buggy.copy()
    for i in range(1, len(U_buggy)-1):
        U_new[i, :] = U_buggy[i, :] - (dt/dx_test) * (
            (F_pos[i,:] - F_pos[i-1,:]) + (F_neg[i+1,:] - F_neg[i,:]))
    U_new[0,:] = U_new[1,:]
    U_new[-1,:] = U_new[-2,:]
    U_buggy = U_new
    t += dt
    n_steps += 1

errors_buggy = compute_errors(U_buggy, x_test, t, GAMMA)
errors_correct = results[100]['errors']

print(f"\nN=100 对比:")
for var in ['rho', 'u', 'p']:
    print(f"  {var}:")
    print(f"    Buggy:  L1={errors_buggy[var]['L1']:.6e}, L2={errors_buggy[var]['L2']:.6e}")
    print(f"    Correct: L1={errors_correct[var]['L1']:.6e}, L2={errors_correct[var]['L2']:.6e}")
    print(f"    L1改善: {(errors_buggy[var]['L1']-errors_correct[var]['L1'])/errors_buggy[var]['L1']*100:.1f}%")

# ================================================================
# 生成可视化
# ================================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

fig_dir = r'e:\trae_project\a\results\figures'
os.makedirs(fig_dir, exist_ok=True)

# 正确版本 N=100
fig, axes = plt.subplots(3, 1, figsize=(10, 12))
rho_ex, u_ex, p_ex = sod_exact_solution(results[100]['x'], results[100]['t'], GAMMA)
rho_n, u_n, p_n = conservative_to_primitive(results[100]['U'], GAMMA)

axes[0].plot(results[100]['x'], rho_ex, 'k-', lw=2, label='Exact')
axes[0].plot(results[100]['x'], rho_n, 'ro', ms=3, label='Upwind Corrected (N=100)')
axes[0].set_ylabel(r'$\rho$', fontsize=14); axes[0].legend(); axes[0].grid(True, alpha=0.3)

axes[1].plot(results[100]['x'], u_ex, 'k-', lw=2, label='Exact')
axes[1].plot(results[100]['x'], u_n, 'bo', ms=3, label='Upwind Corrected (N=100)')
axes[1].set_ylabel(r'$u$', fontsize=14); axes[1].legend(); axes[1].grid(True, alpha=0.3)

axes[2].plot(results[100]['x'], p_ex, 'k-', lw=2, label='Exact')
axes[2].plot(results[100]['x'], p_n, 'go', ms=3, label='Upwind Corrected (N=100)')
axes[2].set_ylabel(r'$p$', fontsize=14); axes[2].set_xlabel('x', fontsize=14); axes[2].legend(); axes[2].grid(True, alpha=0.3)

plt.suptitle('Steger-Warming Upwind (Numerical R_inv, N=100, t=0.2)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'upwind_corrected_N100.png'), dpi=300, bbox_inches='tight')
plt.close()
print("\n已保存: upwind_corrected_N100.png")

# 收敛图
fig, ax = plt.subplots(figsize=(8, 6))
Ns = np.array(resolutions)
dxs_arr = 1.0 / Ns
for var, color in [('rho','r'), ('u','b'), ('p','g')]:
    l1 = np.array([results[N]['errors'][var]['L1'] for N in resolutions])
    ax.loglog(dxs_arr, l1, f'{color}o-', lw=2, ms=8, label=f'L1({var})')

ref = dxs_arr / dxs_arr[0] * results[50]['errors']['rho']['L1']
ax.loglog(dxs_arr, ref, 'k--', lw=1.5, label='O(dx)')
ax.set_xlabel(r'$\Delta x$', fontsize=14); ax.set_ylabel('L1 Error', fontsize=14)
ax.set_title('Convergence - Corrected Steger-Warming Upwind', fontsize=14)
ax.legend(); ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'convergence_corrected_upwind.png'), dpi=300, bbox_inches='tight')
plt.close()
print("已保存: convergence_corrected_upwind.png")

# Bug vs Correct 对比图
fig, axes = plt.subplots(3, 1, figsize=(10, 12))
x = results[100]['x']
rho_ex, u_ex, p_ex = sod_exact_solution(x, 0.2, GAMMA)
rho_n, u_n, p_n = conservative_to_primitive(results[100]['U'], GAMMA)
rho_b, u_b, p_b = conservative_to_primitive(U_buggy, GAMMA)

axes[0].plot(x, rho_ex, 'k-', lw=2, label='Exact')
axes[0].plot(x, rho_n, 'b-', lw=1.5, label='Corrected')
axes[0].plot(x, rho_b, 'r--', lw=1, label='Buggy (sod_solver.py)')
axes[0].set_ylabel(r'$\rho$'); axes[0].legend(); axes[0].grid(True, alpha=0.3)
axes[0].set_title('Bug Comparison: Corrected vs Buggy R_inv', fontsize=14)

axes[1].plot(x, u_ex, 'k-', lw=2, label='Exact')
axes[1].plot(x, u_n, 'b-', lw=1.5, label='Corrected')
axes[1].plot(x, u_b, 'r--', lw=1, label='Buggy (sod_solver.py)')
axes[1].set_ylabel(r'$u$'); axes[1].legend(); axes[1].grid(True, alpha=0.3)

axes[2].plot(x, p_ex, 'k-', lw=2, label='Exact')
axes[2].plot(x, p_n, 'b-', lw=1.5, label='Corrected')
axes[2].plot(x, p_b, 'r--', lw=1, label='Buggy (sod_solver.py)')
axes[2].set_ylabel(r'$p$'); axes[2].set_xlabel('x'); axes[2].legend(); axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'bug_comparison_upwind.png'), dpi=300, bbox_inches='tight')
plt.close()
print("已保存: bug_comparison_upwind.png")

# 保存修正版收敛数据
with open(os.path.join(r'e:\trae_project\a\results', 'convergence_corrected.txt'), 'w') as f:
    f.write("N,dx,rho_L1,rho_L2,rho_Linf,u_L1,u_L2,u_Linf,p_L1,p_L2,p_Linf,n_steps\n")
    for N in resolutions:
        e = results[N]['errors']
        dx = 1.0 / N
        f.write(f"{N},{dx:.8e},{e['rho']['L1']:.6e},{e['rho']['L2']:.6e},{e['rho']['Linf']:.6e},"
                f"{e['u']['L1']:.6e},{e['u']['L2']:.6e},{e['u']['Linf']:.6e},"
                f"{e['p']['L1']:.6e},{e['p']['L2']:.6e},{e['p']['Linf']:.6e},"
                f"{results[N]['n_steps']}\n")

print("\n验证完成!")
