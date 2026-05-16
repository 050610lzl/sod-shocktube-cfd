# 测试用例清单

## 一、测试用例总览

| 测试模块 | 用例数量 | 测试文件 | 状态 |
|----------|----------|----------|------|
| 网格生成 | 6 | test_mesh.py | ✅ 全部通过 |
| 流场初始化 | 9 | test_initialization.py | ✅ 全部通过 |
| 边界条件 | 8 | test_boundary.py | ✅ 全部通过 |
| 数值格式 | 11 | test_fd_schemes.py | ✅ 全部通过 |
| **合计** | **34** | | **34/34 通过** |

## 二、网格生成测试 (test_mesh.py)

| 编号 | 用例名称 | 测试内容 | 预期结果 |
|------|----------|----------|----------|
| TC-MESH-001 | test_mesh_size | 验证生成网格的节点数正确 | len(x) == n_points |
| TC-MESH-002 | test_mesh_range | 验证网格覆盖整个计算域 | x[0]==x_left, x[-1]==x_right |
| TC-MESH-003 | test_mesh_uniform | 验证网格均匀性 | dx = 常数 |
| TC-MESH-004 | test_dx_calculation | 验证网格间距计算公式 | dx = (x_right-x_left)/(n-1) |
| TC-MESH-005 | test_different_n_points | 验证不同节点数的网格 | N=50,100,200全部正确 |
| TC-MESH-006 | test_dx_positive | 验证网格间距为正 | dx > 0 |

## 三、流场初始化测试 (test_initialization.py)

| 编号 | 用例名称 | 测试内容 | 预期结果 |
|------|----------|----------|----------|
| TC-INIT-001 | test_initialize_flow_shape | 验证U的形状 | U.shape == (N, 3) |
| TC-INIT-002 | test_left_density | 验证左态密度 | U_left[:,0] == 1.0 |
| TC-INIT-003 | test_right_density | 验证右态密度 | U_right[:,0] == 0.125 |
| TC-INIT-004 | test_left_velocity | 验证左态速度为零 | U_left[:,1]/rho == 0.0 |
| TC-INIT-005 | test_right_velocity | 验证右态速度为零 | U_right[:,1]/rho == 0.0 |
| TC-INIT-006 | test_left_pressure | 验证左态压力 | p_left == 1.0 |
| TC-INIT-007 | test_right_pressure | 验证右态压力 | p_right == 0.1 |
| TC-INIT-008 | test_positive_density | 验证密度全部为正 | 所有rho > 0 |
| TC-INIT-009 | test_positive_pressure | 验证压力全部为正 | 所有p > 0 |

## 四、边界条件测试 (test_boundary.py)

| 编号 | 用例名称 | 测试内容 | 预期结果 |
|------|----------|----------|----------|
| TC-BC-001 | test_left_boundary_extrapolation | 验证左边界零梯度 | U[0,:] == U[1,:] |
| TC-BC-002 | test_right_boundary_extrapolation | 验证右边界零梯度 | U[-1,:] == U[-2,:] |
| TC-BC-003 | test_boundary_preserves_positivity | 验证边界不产生负值 | 所有值 >= 0 |
| TC-BC-004 | test_boundary_rho | 验证边界密度连续性 | rho边界合理 |
| TC-BC-005 | test_boundary_u | 验证边界速度连续性 | u边界合理 |
| TC-BC-006 | test_boundary_p | 验证边界压力连续性 | p边界合理 |
| TC-BC-007 | test_idempotent | 验证重复施加边界不改变结果 | apply(apply(U)) == apply(U) |
| TC-BC-008 | test_boundary_array_shape | 验证边界不改变数组形状 | shape不变 |

## 五、数值格式测试 (test_fd_schemes.py)

| 编号 | 用例名称 | 测试内容 | 预期结果 |
|------|----------|----------|----------|
| TC-FD-001 | test_lax_friedrichs_step_shape | Lax-Friedrichs输出形状正确 | U_new.shape == U.shape |
| TC-FD-002 | test_lax_wendroff_step_shape | Lax-Wendroff输出形状正确 | U_new.shape == U.shape |
| TC-FD-003 | test_macormack_step_shape | MacCormack输出形状正确 | U_new.shape == U.shape |
| TC-FD-004 | test_upwind_step_shape | 迎风格式输出形状正确 | U_new.shape == U.shape |
| TC-FD-005 | test_scheme_positive_density | 各格式单步后密度为正 | rho > 0 |
| TC-FD-006 | test_scheme_positive_pressure | 各格式单步后压力为正 | p > 0 |
| TC-FD-007 | test_scheme_conservation | 各格式质量守恒 | Σρ ≈ 常数 |
| TC-FD-008 | test_fd_schemes_registry | FD_SCHEMES注册9种格式 | len(FD_SCHEMES) == 9 |
| TC-FD-009 | test_solve_with_scheme | 集成测试完整仿真 | t_final == 0.2, 结果合理 |
| TC-FD-010 | test_invalid_scheme_name | 无效格式名抛出异常 | ValueError |
| TC-FD-011 | test_all_schemes_basic | 所有9种格式基本运行 | 全部不崩溃 |

## 六、CI集成测试

| 编号 | 用例名称 | 位置 | 测试内容 |
|------|----------|------|----------|
| CI-001 | Unit tests all Python versions | ci.yml job:test | Python 3.9/3.10/3.11全部通过 |
| CI-002 | Upwind single scheme validation | ci.yml job:test | N=100, CFL=0.8完整运行 |
| CI-003 | CFL stability check | ci.yml job:test | 密度/压力/速度物理合理性 |
| CI-004 | Flake8 linting | ci.yml job:lint | src/零错误 |
| CI-005 | All 9 schemes integration | ci.yml job:integration | 全部格式190步左右完成 |
| CI-006 | Version format check | ci.yml job:test | VERSION格式MAJOR.MINOR.PATCH |

## 七、待补充测试用例

| 编号 | 用例名称 | 优先级 | 说明 |
|------|----------|--------|------|
| TC-PEND-001 | test_convergence_rate_lax_friedrichs | P3 | 验证Lax-Friedrichs收敛阶~1.0 |
| TC-PEND-002 | test_convergence_rate_lax_wendroff | P3 | 验证Lax-Wendroff收敛阶~2.0 |
| TC-PEND-003 | test_convergence_rate_upwind | P3 | 验证迎风收敛阶~1.0 |
| TC-PEND-004 | test_rusanov_step | P3 | Rusanov格式独立单步测试 |
| TC-PEND-005 | test_godunov_step | P3 | Godunov格式独立单步测试 |
| TC-PEND-006 | test_roe_step | P3 | Roe格式独立单步测试 |
| TC-PEND-007 | test_hllc_step | P3 | HLLC格式独立单步测试 |
| TC-PEND-008 | test_tvd_minmod_step | P3 | TVD-Minmod格式独立单步测试 |
| TC-PEND-009 | test_exact_solver_consistency | P3 | 精确解自洽性验证 |
| TC-PEND-010 | test_config_loading | P3 | YAML配置文件加载测试 |
| TC-PEND-011 | test_output_writer | P3 | 输出写入功能测试 |
| TC-PEND-012 | test_validator_errors | P3 | 误差计算正确性测试 |
| TC-PEND-013 | test_cfl_edge_cases | P3 | CFL=0.1, 0.9边界情况 |
| TC-PEND-014 | test_large_n_performance | P3 | N=800性能基准测试 |
| TC-PEND-015 | test_timestamp_archiving | P3 | 时间戳归档功能 |
| TC-PEND-016 | test_gamma_sensitivity | P3 | 不同gamma值(1.2, 1.4, 1.67) |
| TC-PEND-017 | test_initial_condition_variants | P3 | 非标准Sod初始条件 |
| TC-PEND-018 | test_version_file_exists | P3 | VERSION文件存在性 |

---

*文档版本: v1.0 | 更新日期: 2026-05-16 | 测试通过率: 34/34 (100%)*