"""
网格收敛性最终验证图生成脚本
生成修复后的迎风格式网格收敛图，展示正确的收敛行为。
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
print("网格收敛性最终验证 (修复后迎风格式)")
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
    
    err_rho = np.mean(np.abs(rho_num - rho_ex))
    err_u = np.mean(np.abs(u_num - u_ex))
    err_p = np.mean(np.abs(p_num - p_ex))
    
    all_results[N] = {
        'x': x, 'rho_num': rho_num, 'u_num': u_num, 'p_num': p_num,
        'rho_ex': rho_ex, 'u_ex': u_ex, 'p_ex': p_ex,
        'err_rho': err_rho, 'err_u': err_u, 'err_p': err_p,
        'n_steps': n_steps
    }
    
    print(f"N={N}: steps={n_steps}")
    print(f"  L1(rho)={err_rho:.6e}, L1(u)={err_u:.6e}, L1(p)={err_p:.6e}")

# ================================================================
# 生成图表
# ================================================================
fig_dir = r'e:\trae_project\a\results\figures'
os.makedirs(fig_dir, exist_ok=True)

# ---- 图1: 网格收敛对比图 (密度/速度/压力) ----
colors_map = {50: 'red', 100: 'orange', 200: 'green', 400: 'blue', 800: 'purple'}

fig, axes = plt.subplots(3, 1, figsize=(10, 14))

for N in resolutions:
    c = colors_map[N]
    x = all_results[N]['x']
    
    axes[0].plot(x, all_results[N]['rho_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.85)
    axes[1].plot(x, all_results[N]['u_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.85)
    axes[2].plot(x, all_results[N]['p_num'], '-', color=c, linewidth=1.5, 
                 label=f'N={N}', alpha=0.85)

# 精确解参考线
axes[0].plot(all_results[800]['x'], all_results[800]['rho_ex'], 'k-', linewidth=3.0, 
             label='Exact', zorder=10)
axes[1].plot(all_results[800]['x'], all_results[800]['u_ex'], 'k-', linewidth=3.0, 
             label='Exact', zorder=10)
axes[2].plot(all_results[800]['x'], all_results[800]['p_ex'], 'k-', linewidth=3.0, 
             label='Exact', zorder=10)

for ax in axes:
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)

axes[0].set_ylabel(r'$\rho$', fontsize=16)
axes[0].set_title('Grid Convergence - Steger-Warming Flux Vector Splitting (Fixed)', fontsize=16, fontweight='bold')
axes[0].set_ylim(0, 1.1)

axes[1].set_ylabel(r'$u$', fontsize=16)
axes[1].set_title('Velocity', fontsize=14)
axes[1].set_ylim(-0.1, 1.05)

axes[2].set_ylabel(r'$p$', fontsize=16)
axes[2].set_xlabel('$x$', fontsize=16)
axes[2].set_title('Pressure', fontsize=14)
axes[2].set_ylim(0, 1.1)

plt.tight_layout(h_pad=2.0)
plt.savefig(os.path.join(fig_dir, 'grid_convergence_final.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("\n已保存: grid_convergence_final.png")

# ---- 图2: L1误差收敛图 (对数坐标) ----
fig, ax = plt.subplots(figsize=(8, 6))
Ns = np.array(resolutions)
dxs = 1.0 / Ns

rho_l1 = np.array([all_results[N]['err_rho'] for N in resolutions])
u_l1 = np.array([all_results[N]['err_u'] for N in resolutions])
p_l1 = np.array([all_results[N]['err_p'] for N in resolutions])

ax.loglog(dxs, rho_l1, 'ro-', linewidth=2.5, markersize=10, label=r'L1($\rho$)')
ax.loglog(dxs, u_l1, 'bs-', linewidth=2.5, markersize=10, label=r'L1($u$)')
ax.loglog(dxs, p_l1, 'g^-', linewidth=2.5, markersize=10, label=r'L1($p$)')

# 一阶收敛参考线
ref_rho = dxs / dxs[0] * rho_l1[0]
ref_u = dxs / dxs[0] * u_l1[0]
ref_p = dxs / dxs[0] * p_l1[0]
ax.loglog(dxs, ref_rho, 'r--', linewidth=1, alpha=0.5, label='O($\Delta x$) ref')
ax.loglog(dxs, ref_u, 'b--', linewidth=1, alpha=0.5)
ax.loglog(dxs, ref_p, 'g--', linewidth=1, alpha=0.5)

ax.set_xlabel(r'$\Delta x$', fontsize=16)
ax.set_ylabel('L1 Error', fontsize=16)
ax.set_title('Convergence Rate - Steger-Warming Upwind (Fixed)', fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3, which='both')

# 计算收敛阶
p_rho = np.log(rho_l1[-1] / rho_l1[0]) / np.log(dxs[-1] / dxs[0])
p_u = np.log(u_l1[-1] / u_l1[0]) / np.log(dxs[-1] / dxs[0])
p_p = np.log(p_l1[-1] / p_l1[0]) / np.log(dxs[-1] / dxs[0])

ax.text(0.05, 0.05, 
        f'Convergence order (N=50->800):\n'
        f'  rho: {p_rho:.2f}\n'
        f'  u:   {p_u:.2f}\n'
        f'  p:   {p_p:.2f}\n\n'
        f'Note: Sub-optimal orders are expected\n'
        f'for problems with discontinuities\n'
        f'(contact discontinuity + shock)',
        transform=ax.transAxes, fontsize=11, verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'convergence_rate_final.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: convergence_rate_final.png")

# ---- 图3: 高分辨率细节图 (N=800) ----
fig, axes = plt.subplots(3, 1, figsize=(10, 14))
x = all_results[800]['x']

axes[0].plot(x, all_results[800]['rho_ex'], 'k-', linewidth=3.0, label='Exact Solution')
axes[0].plot(x, all_results[800]['rho_num'], 'purple', linewidth=1.5, 
             label='Steger-Warming Upwind (N=800)')
axes[0].set_ylabel(r'$\rho$', fontsize=16)
axes[0].set_title('Density - N=800', fontsize=16)
axes[0].legend(fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim(0, 1)

axes[1].plot(x, all_results[800]['u_ex'], 'k-', linewidth=3.0, label='Exact Solution')
axes[1].plot(x, all_results[800]['u_num'], 'purple', linewidth=1.5, 
             label='Steger-Warming Upwind (N=800)')
axes[1].set_ylabel(r'$u$', fontsize=16)
axes[1].set_title('Velocity - N=800', fontsize=16)
axes[1].legend(fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(0, 1)

axes[2].plot(x, all_results[800]['p_ex'], 'k-', linewidth=3.0, label='Exact Solution')
axes[2].plot(x, all_results[800]['p_num'], 'purple', linewidth=1.5, 
             label='Steger-Warming Upwind (N=800)')
axes[2].set_ylabel(r'$p$', fontsize=16)
axes[2].set_xlabel('$x$', fontsize=16)
axes[2].set_title('Pressure - N=800', fontsize=16)
axes[2].legend(fontsize=12)
axes[2].grid(True, alpha=0.3)
axes[2].set_xlim(0, 1)

plt.tight_layout(h_pad=2.0)
plt.savefig(os.path.join(fig_dir, 'upwind_N800_final.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: upwind_N800_final.png")

# ---- 图4: 误差分布图 ----
fig, axes = plt.subplots(3, 1, figsize=(10, 12))

for N in [200, 400, 800]:
    x = all_results[N]['x']
    err_rho = np.abs(all_results[N]['rho_num'] - all_results[N]['rho_ex'])
    err_u = np.abs(all_results[N]['u_num'] - all_results[N]['u_ex'])
    err_p = np.abs(all_results[N]['p_num'] - all_results[N]['p_ex'])
    
    axes[0].plot(x, err_rho, linewidth=1.5, label=f'N={N}', alpha=0.85)
    axes[1].plot(x, err_u, linewidth=1.5, label=f'N={N}', alpha=0.85)
    axes[2].plot(x, err_p, linewidth=1.5, label=f'N={N}', alpha=0.85)

for ax in axes:
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)

axes[0].set_ylabel(r'$|\rho_{num} - \rho_{ex}|$', fontsize=14)
axes[0].set_title('Pointwise Error Distribution', fontsize=14)
axes[1].set_ylabel(r'$|u_{num} - u_{ex}|$', fontsize=14)
axes[2].set_ylabel(r'$|p_{num} - p_{ex}|$', fontsize=14)
axes[2].set_xlabel('x', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'error_distribution_final.png'), dpi=300, 
            bbox_inches='tight')
plt.close()
print("已保存: error_distribution_final.png")

# ================================================================
# 打印收敛阶统计
# ================================================================
print("\n" + "=" * 60)
print("收敛阶统计")
print("=" * 60)

print(f"\n整体收敛阶 (N=50 -> N=800):")
print(f"  rho: {p_rho:.2f}")
print(f"  u:   {p_u:.2f}")
print(f"  p:   {p_p:.2f}")

print(f"\n相邻网格误差比:")
for i in range(len(resolutions)-1):
    N1 = resolutions[i]
    N2 = resolutions[i+1]
    ratio_rho = all_results[N1]['err_rho'] / all_results[N2]['err_rho']
    ratio_u = all_results[N1]['err_u'] / all_results[N2]['err_u']
    ratio_p = all_results[N1]['err_p'] / all_results[N2]['err_p']
    print(f"  N={N1}/N={N2}: rho_ratio={ratio_rho:.3f}, u_ratio={ratio_u:.3f}, p_ratio={ratio_p:.3f}")

print(f"\n说明: 对于含间断的问题 (接触间断+激波), 一阶格式的")
print(f"      实际收敛阶通常低于理论值1.0, 这是已知现象。")
print(f"      参考: LeVeque (2002), Finite Volume Methods for Hyperbolic Problems.")

print("\n所有图表生成完成!")
