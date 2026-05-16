# 总体架构设计文档

> 文档版本: v1.0  
> 项目: 一维Sod激波管CFD求解器 (sod-shocktube-cfd)  
> 文献依据: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], OneFlow-CFD [4]

---

## 1. 架构概述

本项目采用**经典分层架构**（Layered Architecture），将系统划分为四个核心层次。各层之间通过明确定义的接口进行通信，上层依赖下层，下层对上层透明。

```
+--------------------------------------------------------------+
|                      CLI 层 (Presentation)                    |
|  run_simulation.py / main.py / sod_solver.py                 |
|  argparse 命令行参数解析, YAML 配置加载                      |
+--------------------------------------------------------------+
         |                              ^
         | 调用                         | 结果/状态返回
         v                              |
+--------------------------------------------------------------+
|                   业务逻辑层 (Business Logic)                 |
|  run_simulation.py::run_simulation() - 仿真流程编排          |
|  fd_schemes.py::solve_with_scheme() - 格式求解控制器         |
|  validator.py - 误差计算与可视化编排                         |
+--------------------------------------------------------------+
         |                              ^
         | 调用                         | 数据返回
         v                              |
+--------------------------------------------------------------+
|                    数值计算层 (Numerical Core)                |
|  mesh_generator.py   - 一维均匀网格生成                      |
|  flow_initializer.py - Sod初始条件 + 原始->守恒变量变换      |
|  fd_schemes.py       - 9种数值格式 (单体步进函数)            |
|  boundary_handler.py - 零梯度外推边界条件                    |
|  time_marcher.py     - CFL时间步长 + 守恒性检查              |
|  exact_solver.py     - Riemann精确解 (Toro 2009 第4章)       |
+--------------------------------------------------------------+
         |                              ^
         | 读写                         | 文件读取
         v                              |
+--------------------------------------------------------------+
|                    数据持久层 (Persistence)                   |
|  output_writer.py - .npy 数据归档, 时间戳目录管理            |
|  YAML 配置文件 - simulation_config.yaml                      |
|  validator.py - .png 对比图, .csv 误差报告                   |
+--------------------------------------------------------------+
```

### 1.1 层次职责

| 层次 | 职责 | 关键文件 |
|------|------|----------|
| CLI 层 | 解析命令行参数, 加载 YAML 配置, 启动仿真 | [run_simulation.py](file:///e:/trae_project/a/run_simulation.py) |
| 业务逻辑层 | 仿真流程编排, 格式调度, 误差分析调度, 可视化调度 | [run_simulation.py](file:///e:/trae_project/a/run_simulation.py), [fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py#L991-L1062), [validator.py](file:///e:/trae_project/a/src/validator.py) |
| 数值计算层 | 网格生成, 流场初始化, 数值通量, 时间推进, 精确解 | [src/](file:///e:/trae_project/a/src/) 下全部模块 |
| 数据持久层 | 结果保存, 图片输出, 配置文件读写 | [output_writer.py](file:///e:/trae_project/a/src/output_writer.py), [config/simulation_config.yaml](file:///e:/trae_project/a/config/simulation_config.yaml) |

---

## 2. 模块划分

本项目包含 8 个核心模块，均位于 `src/` 目录下。

### 2.1 模块清单

| 序号 | 模块名称 | 文件名 | 职责 |
|------|----------|--------|------|
| 1 | mesh_generator | [mesh_generator.py](file:///e:/trae_project/a/src/mesh_generator.py) | 生成一维均匀网格 |
| 2 | flow_initializer | [flow_initializer.py](file:///e:/trae_project/a/src/flow_initializer.py) | Sod初始条件设置, 原始变量->守恒变量转换 |
| 3 | fd_schemes | [fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py) | 9种数值格式实现 + 格式注册表 + 求解控制器 |
| 4 | boundary_handler | [boundary_handler.py](file:///e:/trae_project/a/src/boundary_handler.py) | 零梯度外推边界条件 |
| 5 | time_marcher | [time_marcher.py](file:///e:/trae_project/a/src/time_marcher.py) | CFL时间步长计算, 时间推进, 守恒性检查 |
| 6 | exact_solver | [exact_solver.py](file:///e:/trae_project/a/src/exact_solver.py) | Riemann问题精确解 (Newton-Raphson迭代) |
| 7 | output_writer | [output_writer.py](file:///e:/trae_project/a/src/output_writer.py) | .npy 数据归档, 时间戳目录管理 |
| 8 | validator | [validator.py](file:///e:/trae_project/a/src/validator.py) | L1/L2/Linf 误差计算, 对比图生成, 误差报告导出 |

### 2.2 模块依赖关系

```
run_simulation.py
  |
  +---> mesh_generator.py (无依赖)
  +---> flow_initializer.py (无依赖)
  +---> fd_schemes.py
  |       +---> time_marcher.py::compute_dt
  |       +---> time_marcher.py::check_conservation
  |       +---> boundary_handler.py
  +---> exact_solver.py (依赖 scipy.optimize.brentq)
  +---> output_writer.py (依赖 numpy)
  +---> validator.py
          +---> time_marcher.py::conservative_to_primitive
          +---> matplotlib.pyplot
```

### 2.3 模块间数据流

守恒变量 `U` (shape: `(N, 3)`) 是贯穿全流程的核心数据结构:

```
U[:,0] = rho      (密度)
U[:,1] = rho * u  (动量密度)
U[:,2] = rho * E  (总能量密度)
```

数据流路径:

1. `flow_initializer.initialize_flow()` 生成初始 `U0`
2. `fd_schemes.solve_with_scheme()` 接收 `U0`, 反复调用格式步进函数, 每步调用 `boundary_handler` 和 `compute_dt`
3. `exact_solver.sod_exact_solution()` 生成精确原始变量 `(rho, u, p)`
4. `validator.compute_errors()` 将 `U_final` 转原始变量后与精确解比对
5. `output_writer.save_results()` 将 `U` 和 `x` 打包为 .npy

---

## 3. 技术选型

| 技术 | 版本要求 | 选型理由 |
|------|----------|----------|
| Python | >= 3.9 | PyYAML 6.0+ 和 type hint 支持 |
| NumPy | >= 1.21.0, < 2.0.0 | 高性能数组运算, 向量化通量/Jacobian 计算 |
| SciPy | >= 1.7.0 | `brentq` 求解 Riemann 问题 (Godunov/精确解) |
| Matplotlib | >= 3.5.0 | 可视化对比图 (含 LaTeX 标签) |
| PyYAML | >= 6.0 | 配置文件读写 |
| setuptools | >= 61.0 | 构建与打包 (pyproject.toml) |
| pytest | >= 7.0.0 | 单元测试 (可选依赖 `[test]`) |
| flake8 | >= 5.0.0 | 代码风格检查 (可选依赖 `[dev]`) |

选型原则:
- **纯 Python 生态**: 无需编译, 跨平台 (Windows / macOS / Linux)
- **NumPy/SciPy 为核心**: 所有数值计算基于 NumPy 向量化
- **Matplotlib Agg 后端**: 无 GUI 模式, 适配 CI 环境
- **YAML 配置**: 可读性好, 支持注释, 便于参数扫描

---

## 4. 设计模式

### 4.1 策略模式 (Strategy Pattern) — 数值格式选择

**意图**: 将9种数值格式封装为可互换的策略, 运行时动态选择。

**实现**: [fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py#L933-L988) 中的 `FD_SCHEMES` 字典作为策略注册表:

```python
FD_SCHEMES = {
    'lax_friedrichs': {'func': lax_friedrichs_step, 'order': 1, ...},
    'lax_wendroff':   {'func': lax_wendroff_step,   'order': 2, ...},
    'macormack':      {'func': macormack_step,      'order': 2, ...},
    'upwind':         {'func': upwind_step,         'order': 1, ...},
    'rusanov':        {'func': rusanov_step,        'order': 1, ...},
    'godunov':        {'func': godunov_step,        'order': 1, ...},
    'roe':            {'func': roe_step,            'order': 1, ...},
    'hllc':           {'func': hllc_step,           'order': 1, ...},
    'tvd_minmod':     {'func': tvd_minmod_step,     'order': 2, ...},
}
```

所有格式步进函数遵循统一签名: `step_func(U, dx, dt, gamma) -> U_new`。

### 4.2 模板方法模式 (Template Method Pattern) — 求解流程

**意图**: 固定仿真流程骨架, 子步骤可变。

**实现**: [solve_with_scheme()](file:///e:/trae_project/a/src/fd_schemes.py#L991-L1062) 定义标准求解流程:

```
1. 验证格式名称 (查找 FD_SCHEMES)
2. 重置 MacCormack 交替方向计数器
3. 循环 (while t < t_final):
   a. compute_dt()     — CFL 时间步长
   b. 截断最终步长
   c. step_func()       — 策略模式调用
   d. apply_boundary()  — 边界条件
   e. 周期性守恒性检查 (每100步)
4. 最终守恒性检查
5. 返回 (U_final, t, n_steps)
```

---

## 5. 数据流设计

### 5.1 守恒变量 U 的完整传递路径

```
[YAML 配置文件]
      |
      v
flow_initializer.py
  原始变量 (rho, u, p)  ──转换──>  守恒变量 U0 (N, 3)
      |
      v
fd_schemes.py::solve_with_scheme()
      |
      +--- [循环] ---+
      |   compute_dt(U)          -> dt
      |   step_func(U, dx, dt)   -> U_new (不含边界)
      |   apply_boundary(U_new)  -> U_new (含边界)
      |   check_conservation()   -> 控制台报告
      +---------------+
      |
      v
U_final (N, 3) ──┬──> output_writer.save_results()  -> .npy
                  │
                  └──> validator.compute_errors()    -> {L1, L2, Linf}
```

### 5.2 守恒变量与原始变量的转换

| 方向 | 函数 | 位置 |
|------|------|------|
| 原始 -> 守恒 | `initialize_flow()` | [flow_initializer.py](file:///e:/trae_project/a/src/flow_initializer.py#L15-L64) |
| 守恒 -> 原始 | `conservative_to_primitive()` | [time_marcher.py](file:///e:/trae_project/a/src/time_marcher.py#L15-L34) 和 [fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py#L49-L55) |

转换公式 (依据 Anderson 1984 [2]):

```
U[0] = rho
U[1] = rho * u
U[2] = rho * E,  其中 E = p / ((gamma - 1) * rho) + 0.5 * u^2
```

反变换:

```
rho = U[0]
u   = U[1] / U[0]
p   = (gamma - 1) * rho * (E - 0.5 * u^2),  其中 E = U[2] / U[0]
```

---

## 6. 关键算法设计

### 6.1 通量计算

**Euler方程一维通量** (依据 Toro 2009 [2]):

```
F(U) = [rho * u, rho * u^2 + p, u * (rho * E + p)]^T
```

实现: [compute_flux()](file:///e:/trae_project/a/src/fd_schemes.py#L24-L46), 支持批量计算 (N, 3) 和单点 (3,)。

### 6.2 数值格式分类

| 类别 | 格式 | 阶数 | 核心思想 |
|------|------|------|----------|
| 中心格式 | Lax-Friedrichs | 1 | 中心平均 + 数值耗散 |
| 中心格式 | Lax-Wendroff | 2 | Taylor展开 + Jacobian修正 |
| 预估校正 | MacCormack | 2 | 预估(前差) + 校正(后差) + 平均, 交替方向 |
| 迎风格式 | Upwind (Steger-Warming) | 1 | 特征分解 + 通量分裂 + 熵修复 |
| 中心/迎风 | Rusanov (LLF) | 1 | 局部最大波速耗散 |
| Godunov型 | Godunov | 1 | 精确Riemann求解器 (brentq迭代) |
| Godunov型 | Roe | 1 | Roe平均 + 特征分解 + 可选熵修复 |
| Godunov型 | HLLC | 1 | 三波模型 (S_L, S*, S_R) + 可选熵修复 |
| TVD | TVD-Minmod | 2 | MUSCL重构 + Roe通量 + 限制器 |

### 6.3 时间推进 (显式 Euler)

**一阶向前 Euler** (所有格式共用):

```
U_i^{n+1} = U_i^n - (dt/dx) * (F_{i+1/2} - F_{i-1/2})
```

实现于各格式的 `_step()` 函数中。

### 6.4 CFL 条件

**公式** (依据 LeVeque 1992 [5]):

```
dt = CFL * dx / max_i(|u_i| + c_i)
```

其中 `c_i = sqrt(gamma * p_i / rho_i)` 为当地声速。

- CFL 推荐范围: 0.8 ~ 0.95
- 对于二阶格式 (Lax-Wendroff, MacCormack, TVD), 建议 CFL <= 0.8
- 实现: [compute_dt()](file:///e:/trae_project/a/src/time_marcher.py#L37-L59)

### 6.5 边界处理

**零梯度外推** (依据 OneFlow-CFD [4], Laney 1998 [3]):

```
左边界: U[0] = U[1]
右边界: U[N-1] = U[N-2]
```

对所有守恒变量分量 (rho, rho*u, rho*E) 统一施加。

### 6.6 精确解算法 (Toro 2009 第4章)

```
输入: x_数组, t, gamma
算法:
  1. 二分法 (brentq) 求解 f(p*) = 0, 区间 [1e-10, 2*max(pL,pR)]
  2. 计算接触间断速度 u*
  3. 计算接触间断两侧密度 rho*_L, rho*_R
  4. 计算波头/波尾位置 (稀疏波头, 稀疏波尾, 接触间断, 激波)
  5. 按区域分配 (x/t 判断):
     - 区域1 (未扰动左): rho_L, u_L, p_L
     - 区域2 (左稀疏波内部): 等熵关系
     - 区域3 (左星区): rho*_L, u*, p*
     - 区域4 (右星区): rho*_R, u*, p*
     - 区域5 (未扰动右): rho_R, u_R, p_R
```

---

## 7. 错误处理策略

### 7.1 错误分类

| 错误类型 | 处理方式 | 示例 |
|----------|----------|------|
| 配置错误 | 早期失败 + 明确报错 | 未知格式名, 无效CFL值 |
| 数值错误 | 防御性检查 + 回退 | 负密度/压力检测, 退化为一阶 |
| I/O错误 | 自动创建目录 + os.makedirs | 输出目录不存在 |
| 收敛错误 | brentq 迭代发散时 raise | 精确解压力求解失败 |

### 7.2 具体防御措施

1. **格式名称验证**: [solve_with_scheme()](file:///e:/trae_project/a/src/fd_schemes.py#L1021-L1022) 中检查 `scheme_name in FD_SCHEMES`, 未知格式直接 `raise ValueError`
2. **负密度/压力保护**: TVD-Minmod 格式的 MUSCL 重构后, 检测到负值则退化为一阶 (无重构)
3. **声速下限**: 声速计算 `c = sqrt(gamma * p / rho)` 使用 `np.maximum(..., 1e-15)` 防止除零
4. **CFL 安全**: `compute_dt()` 中 `lambda_max` 有最小值 `1e-15` 保护
5. **守恒性检查**: 每100步报告质量/动量/能量相对变化, 初始动量=0时改用绝对值报告避免除零

---

## 参考文献

1. Sod, G. A. (1978). "A Survey of Several Finite Difference Methods for Systems of Nonlinear Hyperbolic Conservation Laws." *Journal of Computational Physics*, 27(1), 1-31.
2. Toro, E. F. (2009). *Riemann Solvers and Numerical Methods for Fluid Dynamics: A Practical Introduction* (3rd ed.). Springer.
3. Laney, C. B. (1998). *Computational Gasdynamics*. Cambridge University Press.
4. OneFlow-CFD Documentation, Sod Shock Tube Example. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html
5. LeVeque, R. J. (1992). *Numerical Methods for Conservation Laws*. Birkhauser.