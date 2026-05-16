"""
迎风格式网格收敛性快速诊断脚本
诊断 steger_warming_flux 的熵修复和收敛行为
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys
sys.path.insert(0, r'e:\trae_project\a')

from src.fd_schemes import upwind_step, steger_warming_flux, conservative_to_primitive
from src.exact_solver import sod_exact_solution
from src.flow_initializer import initialize_flow
from src.mesh_generator import generate_mesh
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt

GAMMA = 1.4

# ================================================================
# 1. 检查熵修复行为
# ================================================================
print("=" * 60)
print("1. 熵修复参数检查")
print("=" * 60)

# 检查稀疏波区内特征值的变化
x_test, dx_test = generate_mesh(n_points=400, x_left=0.0, x_right=1.0)
U_test = initialize_flow(x_test, gamma=GAMMA, diaphragm_pos=0.5)

# 做一步计算看看通量分裂
F_pos, F_neg = steger_warming_flux(U_test, GAMMA)
print(f"F_pos 范围: [{F_pos.min():.6e}, {F_pos.max():.6e}]")
print(f"F_neg 范围: [{F_neg.min():.6e}, {F_neg.max():.6e}]")

# 检查稀疏波区域(i=160附近)的特征值和分裂
idx = 160  # 稀疏波区域
rho, u, p = conservative_to_primitive(U_test[idx:idx+1], GAMMA)
c = np.sqrt(GAMMA * p / rho)
print(f"\n稀疏波区域 i={idx}:")
print(f"  rho={rho[0]:.6f}, u={u[0]:.6f}, p={p[0]:.6f}, c={c[0]:.6f}")
print(f"  lambda1=u-c={u[0]-c[0]:.6f}, lambda2=u={u[0]:.6f}, lambda3=u+c={u[0]+c[0]:.6f}")

# ================================================================
# 2. 运行不同分辨率
# ================================================================
print("\n" + "=" * 60)
print("2. 网格收敛性测试 (迎风格式)")
print("=" * 60)

resolutions = [50, 100, 200, 400, 800]
all_results = {}

for N in resolutions:
    x, dx = generate_mesh(n_points=N, x_left=0.0, x_right=1.0)
    U = initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5)
    
    t = 0.0
    t_final = 0.2
    n_steps = 0
    
    while t < t_final:
        dt = compute_dt(U, dx, cfl=0.8, gamma=GAMMA)
        if t + dt > t_final:
            dt = t_final - t
        
        U = upwind_step(U, dx, dt, GAMMA)
        U = apply_boundary_condition(U)
        t += dt
        n_steps += 1
    
    rho_num, u_num, p_num = conservative_to_primitive(U, GAMMA)
    rho_ex, u_ex, p_ex = sod_exact_solution(x, t_final, GAMMA)
    
    # 计算L1误差
    err_rho = np.mean(np.abs(rho_num - rho_ex))
    err_u = np.mean(np.abs(u_num - u_ex))
    err_p = np.mean(np.abs(p_num - p_ex))
    
    all_results[N] = {
        'x': x, 'rho_num': rho_num, 'u_num': u_num, 'p_num': p_num,
        'rho_ex': rho_ex, 'u_ex': u_ex, 'p_ex': p_ex,
        'err_rho': err_rho, 'err_u': err_u, 'err_p': err_p,
        'n_steps': n_steps
    }
    
    print(f"\nN={N}: steps={n_steps}, dx={dx:.6f}")
    print(f"  L1(rho)={err_rho:.6e}, L1(u)={err_u:.6e}, L1(p)={err_p:.6e}")

# ================================================================
# 3. 检查激波处和接触间断处的数值行为
# ================================================================
print("\n" + "=" * 60)
print("3. 间断处数值行为检查")
print("=" * 60)

for N in [200, 400, 800]:
    x = all_results[N]['x']
    rho_num = all_results[N]['rho_num']
    u_num = all_results[N]['u_num']
    p_num = all_results[N]['p_num']
    
    # 激波附近 (x ≈ 0.85)
    shock_region = (x > 0.8) & (x < 0.9)
    shock_max_p = p_num[shock_region].max()
    shock_min_p = p_num[shock_region].min()
    p_overshoot = shock_max_p - 0.303  # 精确解p* ≈ 0.303
    print(f"\nN={N}:")
    print(f"  激波区: max(p)={shock_max_p:.6f}, min(p)={shock_min_p:.6f}")
    print(f"  接触间断区: 检查密度平台...")
    
    # 接触间断附近 (0.6-0.7)
    contact_region = (x > 0.6) & (x < 0.7)
    rho_contact = rho_num[contact_region]
    print(f"  接触间断左侧密度: max={rho_contact.max():.6f}, min={rho_contact.min():.6f}")

# ================================================================
# 4. 生成收敛图
# ================================================================
print("\n" + "=" * 60)
print("4. 生成网格收敛图")
print("=" * 60)

fig_dir = r'e:\trae_project\a\results\figures'
os.makedirs(fig_dir, exist_ok=True)

colors_map = {50: 'red', 100: 'orange', 200: 'green', 400: 'blue', 800: 'purple'}

fig, axes = plt.subplots(3, 1, figsize=(10, 12))

for N in resolutions:
    c = colors_map[N]
    x = all_results[N]['x']
    
    axes[0].plot(x, all_results[N]['rho_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.8)
    axes[1].plot(x, all_results[N]['u_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.8)
    axes[2].plot(x, all_results[N]['p_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.8)

# 精确解参考线
axes[0].plot(all_results[800]['x'], all_results[800]['rho_ex'], 'k-', linewidth=2.5, 
             label='Exact')
axes[1].plot(all_results[800]['x'], all_results[800]['u_ex'], 'k-', linewidth=2.5, 
             label='Exact')
axes[2].plot(all_results[800]['x'], all_results[800]['p_ex'], 'k-', linewidth=2.5, 
             label='Exact')

for ax in axes:
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

axes[0].set_ylabel(r'$\rho$', fontsize=14)
axes[1].set_ylabel(r'$u$', fontsize=14)
axes[2].set_ylabel(r'$p$', fontsize=14)
axes[2].set_xlabel('x', fontsize=14)
axes[0].set_title('Grid Convergence - Steger-Warming Upwind (BEFORE FIX)', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'grid_convergence_BEFORE_FIX.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: grid_convergence_BEFORE_FIX.png")

# L1误差收敛图
fig, ax = plt.subplots(figsize=(8, 6))
Ns = np.array(resolutions)
dxs = 1.0 / Ns

rho_l1 = np.array([all_results[N]['err_rho'] for N in resolutions])
u_l1 = np.array([all_results[N]['err_u'] for N in resolutions])
p_l1 = np.array([all_results[N]['err_p'] for N in resolutions])

ax.loglog(dxs, rho_l1, 'ro-', linewidth=2, markersize=8, label=r'L1($\rho$)')
ax.loglog(dxs, u_l1, 'bs-', linewidth=2, markersize=8, label=r'L1($u$)')
ax.loglog(dxs, p_l1, 'g^-', linewidth=2, markersize=8, label=r'L1($p$)')

ref_slope = dxs / dxs[0] * rho_l1[0]
ax.loglog(dxs, ref_slope, 'k--', linewidth=1.5, label='O(dx) reference')

ax.set_xlabel(r'$\Delta x$', fontsize=14)
ax.set_ylabel('L1 Error', fontsize=14)
ax.set_title('Convergence Rate - Steger-Warming Upwind (BEFORE FIX)', fontsize=14)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3, which='both')

p_rho = np.log(rho_l1[-1] / rho_l1[0]) / np.log(dxs[-1] / dxs[0])
p_u = np.log(u_l1[-1] / u_l1[0]) / np.log(dxs[-1] / dxs[0])
p_p = np.log(p_l1[-1] / p_l1[0]) / np.log(dxs[-1] / dxs[0])

ax.text(0.05, 0.95, f'Convergence order:\n  rho: {p_rho:.2f}\n  u:   {p_u:.2f}\n  p:   {p_p:.2f}',
        transform=ax.transAxes, fontsize=12, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'convergence_rate_BEFORE_FIX.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: convergence_rate_BEFORE_FIX.png")

print("\n诊断完成!")
