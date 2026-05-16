"""
修复后验证脚本: 对比修复前后的迎风格式网格收敛性
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys
sys.path.insert(0, r'e:\trae_project\a')

from src.fd_schemes import upwind_step, conservative_to_primitive as cs_to_prim
from src.exact_solver import sod_exact_solution
from src.flow_initializer import initialize_flow
from src.mesh_generator import generate_mesh
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt

GAMMA = 1.4

# ================================================================
# 运行不同分辨率
# ================================================================
print("=" * 60)
print("网格收敛性测试 (修复后迎风格式)")
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
    
    rho_num, u_num, p_num = cs_to_prim(U, GAMMA)
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
# 检查间断处行为
# ================================================================
print("\n" + "=" * 60)
print("间断处数值行为检查 (修复后)")
print("=" * 60)

for N in [200, 400, 800]:
    x = all_results[N]['x']
    rho_num = all_results[N]['rho_num']
    p_num = all_results[N]['p_num']
    
    # 激波附近
    shock_region = (x > 0.8) & (x < 0.9)
    shock_max_p = p_num[shock_region].max()
    print(f"\nN={N}:")
    print(f"  激波区: max(p)={shock_max_p:.6f}")
    
    # 接触间断附近
    contact_region = (x > 0.6) & (x < 0.7)
    rho_contact = rho_num[contact_region]
    print(f"  接触间断左侧密度: max={rho_contact.max():.6f}, min={rho_contact.min():.6f}")

# ================================================================
# 生成网格收敛图 (AFTER FIX)
# ================================================================
print("\n" + "=" * 60)
print("生成修复后的网格收敛图")
print("=" * 60)

fig_dir = r'e:\trae_project\a\results\figures'
os.makedirs(fig_dir, exist_ok=True)

colors_map = {50: 'red', 100: 'orange', 200: 'green', 400: 'blue', 800: 'purple'}

# 图1: 网格收敛图
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
axes[0].set_title('Grid Convergence - Steger-Warming Upwind (AFTER FIX)', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'grid_convergence_AFTER_FIX.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: grid_convergence_AFTER_FIX.png")

# 图2: 误差收敛图
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
ax.set_title('Convergence Rate - Steger-Warming Upwind (AFTER FIX)', fontsize=14)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3, which='both')

p_rho = np.log(rho_l1[-1] / rho_l1[0]) / np.log(dxs[-1] / dxs[0])
p_u = np.log(u_l1[-1] / u_l1[0]) / np.log(dxs[-1] / dxs[0])
p_p = np.log(p_l1[-1] / p_l1[0]) / np.log(dxs[-1] / dxs[0])

ax.text(0.05, 0.95, f'Convergence order:\n  rho: {p_rho:.2f}\n  u:   {p_u:.2f}\n  p:   {p_p:.2f}',
        transform=ax.transAxes, fontsize=12, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'convergence_rate_AFTER_FIX.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: convergence_rate_AFTER_FIX.png")

# 图3: N=800对比图 (高分辨率细节)
fig, axes = plt.subplots(3, 1, figsize=(10, 12))
x = all_results[800]['x']
axes[0].plot(x, all_results[800]['rho_ex'], 'k-', linewidth=2.5, label='Exact')
axes[0].plot(x, all_results[800]['rho_num'], 'purple', linewidth=1.5, label='Upwind N=800 (fixed)')
axes[0].set_ylabel(r'$\rho$', fontsize=14)
axes[0].set_title('Density (N=800)', fontsize=14)
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

axes[1].plot(x, all_results[800]['u_ex'], 'k-', linewidth=2.5, label='Exact')
axes[1].plot(x, all_results[800]['u_num'], 'purple', linewidth=1.5, label='Upwind N=800 (fixed)')
axes[1].set_ylabel(r'$u$', fontsize=14)
axes[1].set_title('Velocity (N=800)', fontsize=14)
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)

axes[2].plot(x, all_results[800]['p_ex'], 'k-', linewidth=2.5, label='Exact')
axes[2].plot(x, all_results[800]['p_num'], 'purple', linewidth=1.5, label='Upwind N=800 (fixed)')
axes[2].set_ylabel(r'$p$', fontsize=14)
axes[2].set_xlabel('x', fontsize=14)
axes[2].set_title('Pressure (N=800)', fontsize=14)
axes[2].legend(fontsize=10)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'upwind_N800_AFTER_FIX.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: upwind_N800_AFTER_FIX.png")

# ================================================================
# 收敛阶对比表
# ================================================================
print("\n" + "=" * 60)
print("收敛阶计算结果")
print("=" * 60)

print(f"\n整体收敛阶 (N=50 -> N=800):")
print(f"  rho: {p_rho:.2f}")
print(f"  u:   {p_u:.2f}")
print(f"  p:   {p_p:.2f}")

print(f"\n误差比 (理论一阶应为2):")
for i in range(len(resolutions)-1):
    N1 = resolutions[i]
    N2 = resolutions[i+1]
    ratio_rho = all_results[N1]['err_rho'] / all_results[N2]['err_rho']
    ratio_u = all_results[N1]['err_u'] / all_results[N2]['err_u']
    ratio_p = all_results[N1]['err_p'] / all_results[N2]['err_p']
    print(f"  N={N1}/N={N2}: rho_ratio={ratio_rho:.2f}, u_ratio={ratio_u:.2f}, p_ratio={ratio_p:.2f}")

print("\n验证完成!")
