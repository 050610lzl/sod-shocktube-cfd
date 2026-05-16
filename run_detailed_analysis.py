"""
详细误差分析: 检查不同分辨率下数值解与精确解的详细对比
"""
import numpy as np
import sys
sys.path.insert(0, r'e:\trae_project\a')

from src.fd_schemes import upwind_step, conservative_to_primitive as cs_to_prim
from src.exact_solver import sod_exact_solution
from src.flow_initializer import initialize_flow
from src.mesh_generator import generate_mesh
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt

GAMMA = 1.4

# 在不同分辨率下检查接触间断附近的详细行为
print("详细误差分析")
print("=" * 60)

for N in [50, 100, 200, 400, 800]:
    x, dx = generate_mesh(n_points=N, x_left=0.0, x_right=1.0)
    U = initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5)
    
    t = 0.0
    t_final = 0.2
    while t < t_final:
        dt = compute_dt(U, dx, cfl=0.8, gamma=GAMMA)
        if t + dt > t_final:
            dt = t_final - t
        U = upwind_step(U, dx, dt, GAMMA)
        U = apply_boundary_condition(U)
        t += dt
    
    rho_num, u_num, p_num = cs_to_prim(U, GAMMA)
    rho_ex, u_ex, p_ex = sod_exact_solution(x, t_final, GAMMA)
    
    # 检查接触间断附近(0.65-0.72)的密度
    contact_mask = (x > 0.65) & (x < 0.72)
    if np.any(contact_mask):
        rho_c_num = rho_num[contact_mask]
        rho_c_ex = rho_ex[contact_mask]
        print(f"\nN={N}: 接触间断区密度")
        print(f"  数值解: min={rho_c_num.min():.4f}, max={rho_c_num.max():.4f}")
        print(f"  精确解: {rho_c_ex[0]:.4f}")
    
    # 检查激波附近(0.82-0.88)的压力
    shock_mask = (x > 0.82) & (x < 0.88)
    if np.any(shock_mask):
        p_s_num = p_num[shock_mask]
        p_s_ex = p_ex[shock_mask]
        print(f"  激波区压力: 数值={p_s_num.max():.4f}, 精确={p_s_ex.max():.4f}")
    
    # 计算误差在稀疏波区和平台区的分布
    # 稀疏波区
    rare_mask = (x > 0.26) & (x < 0.49)
    if np.any(rare_mask):
        err_rho_rare = np.mean(np.abs(rho_num[rare_mask] - rho_ex[rare_mask]))
        err_u_rare = np.mean(np.abs(u_num[rare_mask] - u_ex[rare_mask]))
        print(f"  稀疏波区L1误差: rho={err_rho_rare:.6e}, u={err_u_rare:.6e}")
    
    # 平台区
    plateau_mask = (x > 0.50) & (x < 0.65)
    if np.any(plateau_mask):
        err_rho_plateau = np.mean(np.abs(rho_num[plateau_mask] - rho_ex[plateau_mask]))
        err_u_plateau = np.mean(np.abs(u_num[plateau_mask] - u_ex[plateau_mask]))
        print(f"  平台区L1误差: rho={err_rho_plateau:.6e}, u={err_u_plateau:.6e}")

# 验证: 在精细网格上比较数值解与精确解的相对误差
print("\n" + "=" * 60)
print("相对误差分析 (N=800)")
x, dx = generate_mesh(n_points=800)
U = initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5)
t = 0.0
while t < 0.2:
    dt = compute_dt(U, dx, cfl=0.8, gamma=GAMMA)
    if t + dt > 0.2:
        dt = 0.2 - t
    U = upwind_step(U, dx, dt, GAMMA)
    U = apply_boundary_condition(U)
    t += dt

rho_num, u_num, p_num = cs_to_prim(U, GAMMA)
rho_ex, u_ex, p_ex = sod_exact_solution(x, 0.2, GAMMA)

# 最大绝对误差位置
for name, num, ex in [('rho', rho_num, rho_ex), ('u', u_num, u_ex), ('p', p_num, p_ex)]:
    err = np.abs(num - ex)
    idx = np.argmax(err)
    print(f"\n{name}: 最大误差={err[idx]:.6f} at x={x[idx]:.4f}")
    print(f"  数值解: {num[idx]:.6f}")
    print(f"  精确解: {ex[idx]:.6f}")
    # 检查该位置附近
    if idx > 5 and idx < len(x)-5:
        for j in range(idx-3, idx+4):
            print(f"  x={x[j]:.4f}: num={num[j]:.6f}, ex={ex[j]:.6f}")
