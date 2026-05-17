# Sod激波管CFD项目 -- 测试计划

| 项目 | 内容 |
|------|------|
| **项目名称** | 一维Sod激波管CFD数值格式对比项目 |
| **项目版本** | v1.5.1 |
| **文档编号** | TP-SOD-20260517-v1.1 |
| **编写日期** | 2026-05-17 |
| **编写人** | Sod激波管CFD验证Agent |
| **审核状态** | 待审核 |

---

## 1. 测试目标

本测试计划旨在通过系统性、可复现的测试活动，验证一维Sod激波管CFD求解器（9种数值格式）在以下四个维度上的质量水平：

| 维度 | 目标 | 验收标准 | 文献依据 |
|------|------|----------|----------|
| **正确性** | 验证9种格式的代码实现是否符合理论规范 | 所有格式物理场无负密度/压力、波系位置误差<2dx、精确解对比误差在合理范围 | Sod (1978) [1], Toro (2009) [2], Laney (1998) [3] |
| **精度** | 量化各格式的L1/L2/Linf误差，验证误差排序符合理论预期 | Riemann求解器类格式误差最低，中心耗散型格式误差最高，排序与文献 [1][3] 一致 | Sod (1978) [1], Blazek (2015) [4] |
| **稳定性** | 验证CFL条件边界、TVD性质、守恒性 | CFL<=1.0稳定，CFL>1.4崩溃；质量/能量守恒误差<1e-7%；无负密度/压力 | LeVeque (2002) [5], Toro (2009) [2] |
| **收敛性** | 验证网格加密时误差的衰减率是否符合理论收敛阶 | 一阶格式收敛阶0.5~1.0（含间断），符合LeVeque (2002) 理论预期 | LeVeque (2002) [5], Laney (1998) [3] |

---

## 2. 测试范围

### 2.1 被测对象概览

本项目实现了基于有限差分法（FDM）与有限体积法（FVM）的9种经典数值格式，求解一维可压缩Euler方程：

| 编号 | 格式名称 | 阶数 | 技术类别 | 核心文件 |
|------|----------|------|----------|----------|
| FDM-1 | Lax-Friedrichs | 一阶 | 中心耗散型 | src/fd_schemes.py |
| FDM-2 | Lax-Wendroff | 二阶 | 中心色散型 | src/fd_schemes.py |
| FDM-3 | MacCormack | 二阶 | 预估校正型 | src/fd_schemes.py |
| FDM-4 | 一阶迎风 | 一阶 | Steger-Warming FVS | src/fd_schemes.py |
| FDM-5 | Rusanov | 一阶 | 局部Lax-Friedrichs | src/fd_schemes.py |
| FDM-6 | Godunov | 一阶 | 精确Riemann求解器 | src/fd_schemes.py |
| FDM-7 | Roe | 一阶 | 近似Riemann求解器 | src/fd_schemes.py |
| FDM-8 | HLLC | 一阶 | 三波模型 | src/fd_schemes.py |
| FDM-9 | TVD-MUSCL/Minmod | 二阶 | TVD限制器型 | src/fd_schemes.py |

### 2.2 测试层级

| 测试层级 | 范围 | 说明 | 状态 |
|----------|------|------|------|
| **单元测试** | 8个核心模块 | 网格生成、流场初始化、边界处理、9种数值格式单步推进、通量计算、守恒变量转换、Jacobian矩阵 | 39项已实现 |
| **集成测试** | 全链路求解 | 各格式从初始条件到t=0.2的全过程求解，包含时间推进、边界施加、守恒性检查 | CI中已覆盖 |
| **系统测试** | 端到端验证 | 精确解对比、波系位置验证、CFL稳定性边界扫描、网格收敛性分析 | 部分完成 |
| **回归测试** | 全量自动化 | 所有39项单元测试 + CI流水线（push/PR触发） | CI已配置 |
| **性能测试** | 运行时间与内存 | 各格式在不同网格分辨率下的运行时间、内存占用、收敛速率 | 待系统化 |
| **验收测试** | 发布标准 | 基于Build文档的多维度评分（代码工程30分 + 仿真结果25分 + 可视化15分 + 文档20分 + 交付物10分） | 已完成v1.0评分95/100 |

### 2.3 已覆盖测试模块

| 模块 | 源文件 | 测试文件 | 用例数 | 覆盖内容 |
|------|--------|----------|--------|----------|
| 网格生成 | src/mesh_generator.py | tests/test_mesh.py | 6 | 默认网格、自定义点数、均匀间距、边界、中点 |
| 流场初始化 | src/flow_initializer.py | tests/test_initialization.py | 9 | 左右密度/速度/能量、隔膜位置、输出形状、守恒一致性 |
| 边界处理 | src/boundary_handler.py | tests/test_boundary.py | 13 | 四种边界条件（零梯度外推/固壁反射/周期/透射）：各类型左右边界全分量验证 |
| 数值格式 | src/fd_schemes.py | tests/test_fd_schemes.py | 11 | 通量物理一致性、原变量转换、Jacobian形状、4种格式单步推进、Steger-Warming一致性、Lax-Friedrichs守恒性、Upwind单调性、Lax-Wendroff对称性 |

---

## 3. 测试策略

### 3.1 白盒测试策略

| 策略项 | 说明 | 依据 |
|--------|------|------|
| **代码路径覆盖** | 所有数值格式的核心函数（通量计算、单步推进）必须有至少一个单元测试覆盖 | Laney (1998) [3] |
| **边界条件验证** | 对四种边界条件（零梯度外推/固壁反射/周期/透射），验证各类型边界处理逻辑的正确性 | OneFlow-CFD [6], Laney (1998) [3] |
| **物理一致性检查** | 通量计算满足F = (rho*u, rho*u^2+p, u*(rho*E+p))；Steger-Warming分裂满足F^+ + F^- = F | Toro (2009) [2] |
| **异常路径验证** | TVD格式的负密度/压力退化保护逻辑已被覆盖 | Harten (1983) [8] |

### 3.2 黑盒测试策略

| 策略项 | 说明 | 依据 |
|--------|------|------|
| **精确解对比** | 数值解与Toro (2009) 精确Riemann解进行L1/L2/Linf误差计算 | Blazek (2015) [4] |
| **波系位置验证** | 4个特征波面（稀疏波头/尾、接触间断、激波）位置误差<2dx | Sod (1978) [1] |
| **CFL稳定性边界** | CFL从0.2扫描至1.5，验证稳定性边界与理论（CFL<=1）一致 | LeVeque (2002) [5] |
| **网格收敛性** | 在N=50/100/200/400/800五种分辨率下计算误差衰减率 | LeVeque (2002) [5] |

### 3.3 自动化CI策略

项目已配置GitHub Actions CI流水线（`.github/workflows/ci.yml`），包含三个Job：

| Job | 触发条件 | Python版本 | 内容 |
|-----|----------|-----------|------|
| **test** | push/PR到master/main | 3.9, 3.10, 3.11 | 版本验证、39项单元测试、迎风格式单步运行、CFL/TVD性质检查 |
| **lint** | push/PR到master/main | 3.11 | flake8代码风格检查（忽略E501/W503/W504） |
| **integration** | push/PR到master/main | 3.11 | 9种格式全链路求解，验证无负密度/负压力 |

**CI通过标准**：所有Job均通过方可合并PR。

---

## 4. 测试环境

### 4.1 硬件环境

| 项目 | CI环境 | 本地开发环境 |
|------|--------|-------------|
| 操作系统 | Ubuntu 22.04 (GitHub Actions `ubuntu-latest`) | Windows 10/11 |
| CPU | 2-core (GitHub Actions 标准) | 开发者本机 |
| 内存 | 7 GB (GitHub Actions 标准) | >= 8 GB |

### 4.2 软件环境

| 组件 | CI版本 | 本地版本 | 约束 |
|------|--------|----------|------|
| Python | 3.9, 3.10, 3.11 | 3.9+ | `requires-python = ">=3.9"` [pyproject.toml] |
| numpy | 最新兼容版本 | >=1.21.0, <2.0.0 | `<2.0.0` 避免不兼容变更 |
| matplotlib | 最新兼容版本 | >=3.5.0 | - |
| scipy | 最新兼容版本 | >=1.7.0 | Godunov格式使用brentq求根 |
| pyyaml | 最新兼容版本 | >=6.0 | 配置文件解析 |
| pytest | >=7.0.0 | >=7.0.0 | 单元测试框架 |
| flake8 | >=5.0.0 | >=5.0.0 | 代码风格检查 |

### 4.3 配置参数

标准测试工况（来源于参考文献 [1][2]）：

| 参数 | 值 | 说明 |
|------|------|------|
| 管长 L | 1.0 | 无量纲长度 |
| 隔膜位置 x0 | 0.5 | 初始间断位置 |
| 终止时间 t_final | 0.2 | Sod问题标准终止时间 |
| 比热比 gamma | 1.4 | 理想气体 |
| CFL数 | 0.8 | 稳定性与效率的平衡值 |
| 网格分辨率 N | 100（默认）/ 50,200,400,800（收敛性测试） | - |
| 左态密度 rho_L | 1.0 | Sod (1978) 标准初始条件 |
| 左态速度 u_L | 0.0 | Sod (1978) 标准初始条件 |
| 左态压力 p_L | 1.0 | Sod (1978) 标准初始条件 |
| 右态密度 rho_R | 0.125 | Sod (1978) 标准初始条件 |
| 右态速度 u_R | 0.0 | Sod (1978) 标准初始条件 |
| 右态压力 p_R | 0.1 | Sod (1978) 标准初始条件 |

---

## 5. 测试用例清单

### 5.1 现有测试用例（39项）

#### 5.1.1 网格生成模块（test_mesh.py -- 6项）

| 用例ID | 用例名称 | 验证内容 | 预期结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-MESH-001 | test_default_mesh | 默认N=100, x[0]=0, x[-1]=1, dx=1/99 | 断言全部通过 | 通过 |
| TC-MESH-002 | test_custom_n_points | N=[50,200,400,800]的正确性 | 断言全部通过 | 通过 |
| TC-MESH-003 | test_uniform_spacing | 网格间距均匀性: np.diff(x)全相等 | 容差1e-15 | 通过 |
| TC-MESH-004 | test_left_boundary | 左边界x[0]=0.0 | 容差1e-15 | 通过 |
| TC-MESH-005 | test_right_boundary | 右边界x[-1]=1.0 | 容差1e-15 | 通过 |
| TC-MESH-006 | test_midpoint | N=101时x[50]=0.5 | 容差1e-15 | 通过 |

#### 5.1.2 流场初始化模块（test_initialization.py -- 9项）

| 用例ID | 用例名称 | 验证内容 | 文献依据 | 状态 |
|--------|----------|----------|----------|------|
| TC-INIT-001 | test_left_density | 左态密度=1.0 | Sod (1978) [1] | 通过 |
| TC-INIT-002 | test_right_density | 右态密度=0.125 | Sod (1978) [1] | 通过 |
| TC-INIT-003 | test_left_velocity | 左态动量=0.0 | Sod (1978) [1] | 通过 |
| TC-INIT-004 | test_right_velocity | 右态动量=0.0 | Sod (1978) [1] | 通过 |
| TC-INIT-005 | test_left_total_energy | 左态E=2.5 (p=1.0) | Sod (1978) [1] | 通过 |
| TC-INIT-006 | test_right_total_energy | 右态E=2.0 (p=0.1) | Sod (1978) [1] | 通过 |
| TC-INIT-007 | test_diaphragm_position | 隔膜位置=0.5处密度跳变 | Sod (1978) [1] | 通过 |
| TC-INIT-008 | test_output_shape | N=200输出形状=(200,3) | - | 通过 |
| TC-INIT-009 | test_conservative_consistency | 速度由动量/密度反算与预期一致 | - | 通过 |

#### 5.1.3 边界处理模块（test_boundary.py -- 13项）

| 用例ID | 用例名称 | 验证内容 | 文献依据 | 状态 |
|--------|----------|----------|----------|------|
| TC-BC-001 | test_left_boundary_rho | 左边界密度=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-002 | test_left_boundary_momentum | 左边界动量=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-003 | test_left_boundary_energy | 左边界能量=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-004 | test_right_boundary_rho | 右边界密度=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-005 | test_right_boundary_momentum | 右边界动量=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-006 | test_right_boundary_energy | 右边界能量=相邻内点（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-007 | test_all_components | 全分量同时外推正确（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-008 | test_interior_preserved | 内部网格点不被边界处理修改（零梯度） | Laney (1998) [3] | 通过 |
| TC-BC-009 | test_reflective_boundary | 固壁反射：左右边界动量反号 | Hirsch (1990) [3], Blazek (2015) [4] | 通过 |
| TC-BC-010 | test_periodic_boundary | 周期边界：U[0]=U[-2], U[-1]=U[1] | Hirsch (1990) [3] | 通过 |
| TC-BC-011 | test_transmissive_boundary | 透射边界：二阶外推 U[0]=2U[1]-U[2] | Hirsch (1990) [3] | 通过 |
| TC-BC-012 | test_zero_gradient_default | 默认参数为zero_gradient类型 | OneFlow-CFD [6] | 通过 |
| TC-BC-013 | test_boundary_types_registry | BOUNDARY_TYPES注册表含4种类型 | - | 通过 |

#### 5.1.4 数值格式模块（test_fd_schemes.py -- 11项）

| 用例ID | 用例名称 | 验证内容 | 文献依据 | 状态 |
|--------|----------|----------|----------|------|
| TC-FD-001 | test_flux_physical_consistency | 通量F = (rho*u, rho*u^2+p, ...) | Toro (2009) [2] | 通过 |
| TC-FD-002 | test_conservative_to_primitive | 原变量转换，密度/压力均为正 | Toro (2009) [2] | 通过 |
| TC-FD-003 | test_jacobian_shape | Jacobian形状=(N,3,3) | Laney (1998) [3] | 通过 |
| TC-FD-004 | test_lax_friedrichs_step | Lax-Friedrichs单步无NaN、密度为正 | Sod (1978) [1] | 通过 |
| TC-FD-005 | test_lax_wendroff_step | Lax-Wendroff单步无NaN、密度为正 | Sod (1978) [1] | 通过 |
| TC-FD-006 | test_macormack_step | MacCormack单步无NaN、密度为正 | Sod (1978) [1] | 通过 |
| TC-FD-007 | test_upwind_step | 迎风单步无NaN、密度为正 | Laney (1998) [3] | 通过 |
| TC-FD-008 | test_steger_warming_consistency | F^+ + F^- = F (u=0时) | Steger & Warming (1981) [9] | 通过 |
| TC-FD-009 | test_lax_friedrichs_conservation | Lax-Friedrichs单步质量守恒<1% | LeVeque (2002) [5] | 通过 |
| TC-FD-010 | test_upwind_monotonicity | 迎风单步密度非负 | Toro (2009) [2] | 通过 |
| TC-FD-011 | test_lax_wendroff_symmetry | Lax-Wendroff单步无NaN | Sod (1978) [1] | 通过 |

### 5.2 CI集成测试（已有，但非pytest用例）

| 用例ID | 用例名称 | 内容 | 触发 | 状态 |
|--------|----------|------|------|------|
| TC-CI-001 | pytest单元测试 | python -m pytest tests/ -v | push/PR | 通过 |
| TC-CI-002 | 迎风格式验证 | run_simulation.py --n_points 100 --cfl 0.8 --scheme upwind | push/PR | 通过 |
| TC-CI-003 | CFL/TVD性质检查 | 单步后密度>0、压力>0、速度<1.0 | push/PR | 通过 |
| TC-CI-004 | flake8代码风格 | flake8 src/ --max-line-length=120 | push/PR | 通过 |
| TC-CI-005 | 9种格式集成测试 | 9种格式全链路t=0.2运行，无负密度/压力 | push/PR | 通过 |
| TC-CI-006 | VERSION格式验证 | 版本号符合MAJOR.MINOR.PATCH | push/PR | 通过 |

### 5.3 需补充的测试用例

以下测试用例在当前版本中缺失，建议在后续版本中补充：

| 用例ID | 用例名称 | 测试层级 | 优先级 | 说明 |
|--------|----------|----------|--------|------|
| TC-SUP-001 | test_rusanov_step | 单元测试 | 高 | Rusanov格式单步推进测试（已有代码但测试文件未覆盖） |
| TC-SUP-002 | test_godunov_step | 单元测试 | 高 | Godunov精确Riemann求解器单步测试 |
| TC-SUP-003 | test_roe_step | 单元测试 | 高 | Roe近似Riemann求解器单步测试 |
| TC-SUP-004 | test_hllc_step | 单元测试 | 高 | HLLC三波模型单步测试 |
| TC-SUP-005 | test_tvd_minmod_step | 单元测试 | 高 | TVD-MUSCL格式单步测试 |
| TC-SUP-006 | test_roe_entropy_fix | 单元测试 | 中 | Roe熵修复功能启用/关闭对比测试 |
| TC-SUP-007 | test_hllc_entropy_fix | 单元测试 | 中 | HLLC熵修复功能启用/关闭对比测试 |
| TC-SUP-008 | test_roe_average | 单元测试 | 中 | _roe_average函数独立测试 |
| TC-SUP-009 | test_minmod_limiter | 单元测试 | 中 | Minmod限制器独立测试 |
| TC-SUP-010 | test_exact_solver | 单元测试 | 中 | 精确Riemann求解器关键参数测试（p*, u*, 波速） |
| TC-SUP-011 | test_conservation_all_schemes | 系统测试 | 中 | 9种格式全链路质量/能量守恒检验 |
| TC-SUP-012 | test_convergence_rate_upwind | 系统测试 | 中 | Upwind格式收敛阶自动化计算与验证 |
| TC-SUP-013 | test_convergence_rate_all_schemes | 系统测试 | 高 | 全9种格式收敛阶自动化计算 |
| TC-SUP-014 | test_cfl_boundary_all_schemes | 系统测试 | 中 | 全格式CFL稳定性边界自动化扫描 |
| TC-SUP-015 | test_wave_positions_all_schemes | 系统测试 | 中 | 全格式4个波面位置误差验证 |
| TC-SUP-016 | test_memory_usage | 性能测试 | 低 | 各格式不同分辨率下的内存占用测试 |
| TC-SUP-017 | test_runtime_scaling | 性能测试 | 低 | 各格式运行时间随N的缩放率测试 |
| TC-SUP-018 | test_performance_regression | 回归测试 | 低 | 性能回归检测（比较两次构建的运行时间） |

---

## 6. 测试进度安排

### 6.1 里程碑与时间线

| 阶段 | 内容 | 预计完成 | 状态 |
|------|------|----------|------|
| **Phase 0: 基础建设** | 项目初始化、初始条件/边界条件验证、精确Riemann求解器实现与验证 | 2026-04-28 ~ 2026-05-01 | 已完成 |
| **Phase 1: 核心功能测试** | 4种必选格式实现与单元测试、34项pytest用例编写与调试 | 2026-05-01 ~ 2026-05-03 | 已完成 |
| **Phase 2: 缺陷修复与增强** | Steger-Warming R_inv修复、MacCormack交替方向、熵修复功能、守恒性检查 | 2026-05-03 ~ 2026-05-06 | 已完成 |
| **Phase 3: 系统验证** | 全9种格式N=100验证、CFL稳定性扫描、网格收敛性分析、验收评分 | 2026-05-06 ~ 2026-05-07 | 已完成 |
| **Phase 4: 补充完善** | 补充5种扩展格式单元测试、全格式收敛数据、性能测试、文档完善（含v1.5.1边界条件扩展） | 2026-05-16 ~ 2026-06-01 | 进行中 |
| **Phase 5: 发布准备** | 回归测试、性能基准建立、v1.5.1发布 | 2026-06-01 ~ 2026-06-15 | 未开始 |

### 6.2 测试执行频率

| 测试类型 | 执行频率 | 触发条件 |
|----------|----------|----------|
| 单元测试（39项） | 每次push/PR | CI自动 |
| flake8代码风格 | 每次push/PR | CI自动 |
| 集成测试 | 每次push/PR | CI自动 |
| 全格式系统验证 | 版本发布前 | 手动执行 |
| 网格收敛性测试 | 版本发布前 | 手动执行 |
| 性能测试 | 版本发布前 | 手动执行 |

---

## 7. 风险与应对

| 风险编号 | 风险描述 | 可能性 | 影响 | 应对措施 |
|----------|----------|--------|------|----------|
| R-001 | numpy 2.0发布导致不兼容变更 | 中 | 高 | requirements.txt已限制 `numpy<2.0.0`；后续版本需适配numpy 2.x API |
| R-002 | CI Runner资源限制导致Godunov（精确Riemann求解器）超时 | 低 | 中 | Godunov格式在N<=200下运行时间可接受；必要时增加timeout参数 |
| R-003 | 跨平台兼容性问题（Windows vs Ubuntu） | 低 | 中 | CI使用Ubuntu runner覆盖Linux；Windows本地开发验证 |
| R-004 | Python 3.12/3.13新版本兼容性 | 低 | 低 | CI matrix目前覆盖3.9~3.11；后续版本扩展matrix |
| R-005 | 精确解计算错误未被察觉（已发生一次，见utils.py激波公式修复记录） | 低 | 极高 | 已建立精确解与Toro (2009)理论值的交叉验证机制；所有关键参数（p*, u*, 波速）均有理论参考值 |
| R-006 | TVD/Minmod格式在极端网格下性能退化 | 低 | 低 | 已有负密度/压力退化保护机制；限制N<=800 |
| R-007 | 测试覆盖率不足（当前仅4个格式有单元测试，5种扩展格式无独立测试） | 高 | 中 | Phase 4规划补充TC-SUP-001至TC-SUP-005 |

---

## 8. 交付物清单

### 8.1 测试文档

| 编号 | 文档名称 | 路径 | 状态 |
|------|----------|------|------|
| D1 | 测试计划（本文档） | docs/04_testing/04_test_plan.md | 当前交付 |
| D2 | 性能测试报告 | docs/04_testing/04_performance_test_report.md | 当前交付 |
| D3 | Bug清单与修复记录 | docs/04_testing/04_bug_tracking.md | 当前交付 |
| D4 | 测试报告 v1.0 | docs/test_report_v1.0.md | 已交付（2026-05-07） |
| D5 | 代码修复与增强报告 | docs/code_fixes_report.md | 已交付（2026-05-06） |
| D6 | 网格收敛振荡修复报告 | docs/grid_convergence_oscillation_fix.md | 已交付（2026-05-07） |
| D7 | 精确解计算错误诊断报告 | docs/convergence_plot_fix_report.md | 已交付（2026-05-07） |
| D8 | 最终验收报告 | results/final_acceptance_report.md | 已交付（2026-05-07） |
| D9 | MacCormack收敛分析 | docs/macormack_convergence_analysis.md | 已交付（2026-05-07） |
| D10 | 改进计划 | docs/improvement_plan.md | 已交付（2026-05-07） |

### 8.2 测试代码

| 编号 | 文件 | 用例数 | 路径 | 状态 |
|------|------|--------|------|------|
| T1 | test_mesh.py | 6 | tests/test_mesh.py | 已交付 |
| T2 | test_initialization.py | 9 | tests/test_initialization.py | 已交付 |
| T3 | test_boundary.py | 13 | tests/test_boundary.py | 已交付 |
| T4 | test_fd_schemes.py | 11 | tests/test_fd_schemes.py | 已交付 |

### 8.3 CI配置

| 编号 | 文件 | 路径 | 状态 |
|------|------|------|------|
| C1 | GitHub Actions CI | .github/workflows/ci.yml | 已交付 |

### 8.4 数据产物

| 编号 | 类型 | 路径 | 说明 |
|------|------|------|------|
| F1 | 精确解数据 | results/exact/ | 多时间戳目录（含exact_solution_N100.npy） |
| F2 | 数值解数据 | results/data/ | 各格式数值解.npy文件 |
| F3 | 误差报告 | results/error_report.csv | 各格式L1/L2/Linf误差 |
| F4 | 收敛数据 | results/convergence_data.txt | Upwind格式N=50~800收敛数据 |
| F5 | 可视化图表 | results/figures/ | 16+张PNG图表（DPI=300） |

---

## 9. 参考文献

| 编号 | 文献 | 用途 |
|------|------|------|
| [1] | Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. *J. Comput. Phys.*, 27(1), 1-31. | Sod问题原始定义、初始条件与精确解 |
| [2] | Toro, E. F. (2009). *Riemann Solvers and Numerical Methods for Fluid Dynamics* (3rd ed.). Springer. | Riemann精确解、数值格式理论、熵修复方法 |
| [3] | Laney, C. B. (1998). *Computational Gasdynamics*. Cambridge University Press. | 数值格式理论、通量分裂方法、MacCormack交替方向 |
| [4] | Blazek, J. (2015). *Computational Fluid Dynamics: Principles and Applications* (3rd ed.). Elsevier. | CFD求解器验证、误差分析标准方法 |
| [5] | LeVeque, R. J. (2002). *Finite Volume Methods for Hyperbolic Problems*. Cambridge University Press. | CFL条件、收敛性理论 |
| [6] | OneFlow-CFD Documentation: Sod Shock Tube Example. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html | 初始条件、边界条件参考实现 |
| [7] | Roe, P. L. (1981). Approximate Riemann solvers, parameter vectors, and difference schemes. *J. Comput. Phys.*, 43(2), 357-372. | Roe近似Riemann求解器理论 |
| [8] | Harten, A. (1983). On the Numerical Solution of Transonic Flow. *SIAM J. Numer. Anal.* | 熵修复与TVD限制器理论 |
| [9] | Steger, J. L. & Warming, R. F. (1981). Flux Vector Splitting of the Inviscid Gasdynamic Equations. *J. Comput. Phys.*, 40(2), 263-293. | Steger-Warming通量分裂方法 |
| [10] | Toro, E. F., Spruce, M. & Speares, W. (1994). Restoration of the contact surface in the HLL Riemann solver. *Shock Waves*, 4(1), 25-34. | HLLC三波模型理论 |
| [11] | 项目构建文档 (Sod_ShockTube_CFD_Project_Build.md) | 项目验收标准与评分体系 |

---

*文档编号: TP-SOD-20260517-v1.1*
*生成时间: 2026-05-17*
*Sod激波管CFD验证Agent*