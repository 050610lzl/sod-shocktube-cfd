"""
深度诊断脚本：复现run_validation.py的完整流程，检查数据传递和绘图环节
"""
import numpy as np
import sys
import os
sys.path.insert(0, r'e:\trae_project\a')

# 尝试从utils导入
try:
    from utils import (generate_mesh, initialize_flow, conservative_to_primitive,
                       compute_flux, sod_exact_solution, GAMMA, compute_dt,
                       compute_max_eigenvalue)
    from sod_solver import steger_warming_split, upwind_step, solve_sod
    from validation import compute_all_errors
    print("成功导入utils/sod_solver/validation模块")
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)

print("=" * 70)
print("深度诊断：复现run_validation.py流程")
print("=" * 70)

# 模拟run_validation.py的流程
resolutions = [50, 100, 200, 400, 800]
all_results = {}

for N in [100, 800]:  # 只测试两个分辨率
    print(f"\n{'='*60}")
    print(f"测试 N={N}")
    print(f"{'='*60}")
    
    x, dx = generate_mesh(n_points=N, x_left=0.0, x_right=1.0)
    U0 = initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5)
    
    U_final, t_final_actual, n_steps = solve_sod(
        scheme_name='upwind', x=x, dx=dx, U0=U0,
        t_final=0.2, cfl=0.8, gamma=GAMMA
    )
    
    print(f"  实际终止时间: t_final_actual = {t_final_actual}")
    print(f"  迭代步数: n_steps = {n_steps}")
    
    # 计算精确解（关键：使用t_final_actual）
    rho_ex, u_ex, p_ex = sod_exact_solution(x, t_final_actual, GAMMA)
    
    print(f"  精确解u的范围: [{u_ex.min():.8f}, {u_ex.max():.8f}]")
    print(f"  精确解rho的范围: [{rho_ex.min():.8f}, {rho_ex.max():.8f}]")
    print(f"  精确解p的范围: [{p_ex.min():.8f}, {p_ex.max():.8f}]")
    
    # 检查星号区域
    u_star_region = (u_ex > 0.5) & (u_ex < 1.0)
    if np.any(u_star_region):
        u_star_vals = u_ex[u_star_region]
        print(f"  星号区域u值: [{u_star_vals.min():.8f}, {u_star_vals.max():.8f}]")
    else:
        print(f"  警告: 未找到星号区域 (u在0.5-1.0之间)")
    
    rho_num, u_num, p_num = conservative_to_primitive(U_final, GAMMA)
    
    # 检查数值解
    print(f"  数值解u的范围: [{u_num.min():.8f}, {u_num.max():.8f}]")
    print(f"  数值解rho的范围: [{rho_num.min():.8f}, {rho_num.max():.8f}]")
    
    # 查找接触间断位置（u接近u_star的区域的右边界）
    u_star_theoretical = 0.92745262
    contact_mask = np.abs(u_ex - u_star_theoretical) < 0.01
    contact_indices = np.where(contact_mask)[0]
    if len(contact_indices) > 0:
        contact_pos_ex = x[contact_indices[-1]]
        print(f"  精确解接触间断位置 (u≈u*): x ≈ {contact_pos_ex:.6f}")
    
    # 查找激波位置（压力跃变最大处）
    dp_dx = np.abs(np.diff(p_ex))
    shock_idx = np.argmax(dp_dx)
    shock_pos_ex = x[shock_idx]
    print(f"  精确解激波位置 (dp/dx最大): x ≈ {shock_pos_ex:.6f}")
    
    all_results[N] = {
        'x': x, 'U': U_final,
        'rho_num': rho_num, 'u_num': u_num, 'p_num': p_num,
        'rho_ex': rho_ex, 'u_ex': u_ex, 'p_ex': p_ex,
        't_final': t_final_actual, 'n_steps': n_steps
    }

# 对比N=100和N=800的精确解
print("\n" + "=" * 60)
print("对比N=100和N=800的精确解")
print("=" * 60)

x_100 = all_results[100]['x']
x_800 = all_results[800]['x']
u_ex_100 = all_results[100]['u_ex']
u_ex_800 = all_results[800]['u_ex']

print(f"N=100: x范围=[{x_100[0]:.4f}, {x_100[-1]:.4f}], 点数={len(x_100)}")
print(f"N=800: x范围=[{x_800[0]:.4f}, {x_800[-1]:.4f}], 点数={len(x_800)}")

# 检查在相同位置的u值
test_x = 0.55
idx_100 = np.argmin(np.abs(x_100 - test_x))
idx_800 = np.argmin(np.abs(x_800 - test_x))
print(f"\n在x={test_x}处:")
print(f"  N=100: u_ex = {u_ex_100[idx_100]:.8f}")
print(f"  N=800: u_ex = {u_ex_800[idx_800]:.8f}")

# 关键检查：如果使用N=800的精确解作为参考线，是否会出现问题？
print("\n" + "=" * 60)
print("检查绘图逻辑：使用N=800精确解作为参考线")
print("=" * 60)

# 模拟绘图时的数据使用
for N in [50, 100, 200, 400]:
    if N not in all_results:
        # 需要计算这些分辨率
        x, dx = generate_mesh(n_points=N, x_left=0.0, x_right=1.0)
        U0 = initialize_flow(x, gamma=GAMMA, diaphragm_pos=0.5)
        U_final, t_final_actual, n_steps = solve_sod(
            scheme_name='upwind', x=x, dx=dx, U0=U0,
            t_final=0.2, cfl=0.8, gamma=GAMMA
        )
        rho_ex, u_ex, p_ex = sod_exact_solution(x, t_final_actual, GAMMA)
        rho_num, u_num, p_num = conservative_to_primitive(U_final, GAMMA)
        all_results[N] = {
            'x': x, 'rho_num': rho_num, 'u_num': u_num, 'p_num': p_num,
            'rho_ex': rho_ex, 'u_ex': u_ex, 'p_ex': p_ex,
            't_final': t_final_actual, 'n_steps': n_steps
        }

# 现在检查如果用N=800的x坐标绘制N=50的数值解会怎样
print("\n检查坐标匹配问题:")
x_50 = all_results[50]['x']
x_800 = all_results[800]['x']
u_num_50 = all_results[50]['u_num']
u_ex_800 = all_results[800]['u_ex']

print(f"  N=50的x坐标范围: [{x_50[0]:.4f}, {x_50[-1]:.4f}], 长度={len(x_50)}")
print(f"  N=800的x坐标范围: [{x_800[0]:.4f}, {x_800[-1]:.4f}], 长度={len(x_800)}")

# 检查如果用x_50绘制u_ex_800会怎样（长度不匹配会导致matplotlib错误或截断）
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots()
    ax.plot(x_50, u_num_50, '-', label='N=50 numerical')
    # 这应该会产生警告或错误，因为长度不匹配
    ax.plot(x_800, u_ex_800, 'k-', label='Exact (N=800)')
    ax.legend()
    print("  绘图成功：x和y长度匹配")
    
    # 检查实际绘制的数据点
    lines = ax.get_lines()
    for i, line in enumerate(lines):
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        print(f"  线条{i}: x范围=[{xdata.min():.4f}, {xdata.max():.4f}], y范围=[{ydata.min():.4f}, {ydata.max():.4f}], 点数={len(xdata)}")
        if i == 1:  # 精确解线
            y_star_region = ydata[(ydata > 0.5) & (ydata < 1.0)]
            if len(y_star_region) > 0:
                print(f"    星号区域y值: [{y_star_region.min():.4f}, {y_star_region.max():.4f}]")
    
    plt.close()
except Exception as e:
    print(f"  绘图失败: {e}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
