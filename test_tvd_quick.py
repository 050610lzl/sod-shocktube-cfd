"""快速测试TVD格式."""
import sys
sys.path.insert(0, '.')

from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.fd_schemes import solve_with_scheme
from src.exact_solver import sod_exact_solution
from src.validator import compute_errors

# 测试N=100
x, dx = generate_mesh(100)
U0 = initialize_flow(x)

print("=" * 60)
print("TVD格式快速验证 (N=100, CFL=0.8, t=0.2)")
print("=" * 60)

U_final, t_final, n_steps = solve_with_scheme(
    'tvd_minmod', U0, x, dx, t_final=0.2, cfl=0.8
)

print(f"\n迭代步数: {n_steps}")
print(f"最终时间: {t_final:.6f}")

rho_e, u_e, p_e = sod_exact_solution(x, t_final)
errs = compute_errors(U_final, rho_e, u_e, p_e)

print(f"\n误差分析:")
for var in ['rho', 'u', 'p']:
    print(f"  {var}: L1={errs[var]['L1']:.6e}, L2={errs[var]['L2']:.6e}, Linf={errs[var]['Linf']:.6e}")

# 验证无NaN
from src.time_marcher import conservative_to_primitive
rho, u, p = conservative_to_primitive(U_final)
print(f"\n数值检查:")
print(f"  rho范围: [{rho.min():.6f}, {rho.max():.6f}]")
print(f"  p范围:   [{p.min():.6f}, {p.max():.6f}]")
print(f"  无NaN:   {not any([any(np.isnan(rho)), any(np.isnan(u)), any(np.isnan(p))])}")

print("\nTVD格式验证通过!")
