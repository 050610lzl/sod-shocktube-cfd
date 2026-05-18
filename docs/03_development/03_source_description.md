# 源码说明文档

## 一、源码概况

| 指标 | 数值 |
|------|------|
| 编程语言 | Python 3.9+ |
| 总代码行数 | ~2700行 |
| 核心模块数 | 8个(src/) |
| 单元测试数 | 39项 |
| 数值格式 | 9种FDM格式 |
| 第三方依赖 | 4个核心 + 2个开发 |

## 二、源码目录结构

```
sod-shocktube-cfd/
├── src/                          # 核心求解器源码 (~1500行)
│   ├── __init__.py               # 包初始化，导出13个公共API (~30行)
│   ├── mesh_generator.py         # 一维均匀网格生成 (~30行)
│   ├── flow_initializer.py       # Sod初始条件与守恒变量转换 (~80行)
│   ├── fd_schemes.py             # 9种FDM格式核心实现 (~1000行)
│   ├── boundary_handler.py       # 多种边界条件 (zero_gradient/reflective/periodic/transmissive) (~100行)
│   ├── time_marcher.py           # CFL条件与时间推进 (~50行)
│   ├── exact_solver.py           # Riemann精确解 (Toro 2009) (~200行)
│   ├── output_writer.py          # 结果输出与时间戳归档 (~80行)
│   └── validator.py              # 误差计算(L1/L2/Linf)与可视化 (~200行)
├── tests/                        # 单元测试 (~500行)
│   ├── test_mesh.py              # 网格生成测试 (6项)
│   ├── test_initialization.py    # 流场初始化测试 (9项)
│   ├── test_boundary.py          # 边界条件测试 (13项)
│   └── test_fd_schemes.py        # 数值格式测试 (11项)
├── run_simulation.py             # CLI主程序入口 (~200行)
├── bump_version.py               # 版本号管理工具 (~130行)
├── config/
│   ├── simulation_config.yaml            # YAML 仿真参数配置
│   ├── simulation_config.json            # JSON 仿真参数配置 (v1.7.0+)
│   ├── simulation_config_custom_sod.json # 自定义初始条件 JSON 配置
│   └── simulation_config_high_res.json   # 高分辨率 JSON 配置
├── pyproject.toml                # Python包配置(PEP 517/518/621)
├── requirements.txt              # 依赖清单
└── docs/                         # 软件交付文档 (~40+份)
```

## 三、核心模块说明

### 3.1 mesh_generator.py
**功能**: 生成一维均匀网格。  
**输入**: 网格节点数n_points, 计算域[x_left, x_right]。  
**输出**: 节点坐标数组x(N,), 网格间距dx。  
**关键函数**: `generate_mesh(n_points, x_left, x_right)`  
**数学公式**: `dx = (x_right - x_left) / (n_points - 1)`, `x[i] = x_left + i * dx`

### 3.2 flow_initializer.py
**功能**: 根据Sod标准初始条件初始化守恒变量。  
**输入**: 网格坐标x, 左右态原始变量, 隔膜位置, 比热比gamma。  
**输出**: 守恒变量数组U(N, 3) = [ρ, ρu, E]。  
**关键函数**: `initialize_flow(x, gamma, diaphragm_pos, left_state, right_state)`  
**初始条件**:
- 左态: ρ=1.0, u=0.0, p=1.0
- 右态: ρ=0.125, u=0.0, p=0.1
- 转换: `E = p/(gamma-1) + 0.5*ρ*u²`

### 3.3 fd_schemes.py（核心模块）
**功能**: 实现9种有限差分法数值格式的单步推进。  
**关键结构**: `FD_SCHEMES`字典（策略模式注册表）。  
**关键函数**: `solve_with_scheme(scheme_name, U, x, dx, t_final, cfl, gamma)`。  

| 格式 | 函数名 | 精度 | 核心算法 |
|------|--------|------|----------|
| Lax-Friedrichs | `lax_friedrichs_step` | 一阶 | 相邻单元平均 + 通量差 |
| Lax-Wendroff | `lax_wendroff_step` | 二阶 | 半步预测 + Taylor展开修正 |
| MacCormack | `macormack_step` | 二阶 | 预估步(LF) + 校正步(LW) + 交替 |
| Upwind | `upwind_step` | 一阶 | Steger-Warming通量分裂 |
| Rusanov | `rusanov_step` | 一阶 | 局部最大波速耗散 |
| Godunov | `godunov_step` | 一阶 | 精确Riemann求解器(Toro 2009) |
| Roe | `roe_step` | 一阶 | Roe平均Jacobian近似 |
| HLLC | `hllc_step` | 一阶 | 三波模型 + 接触间断恢复 |
| TVD-Minmod | `tvd_minmod_step` | 二阶 | MUSCL重构 + Minmod限制器 + Roe通量 |

### 3.4 boundary_handler.py
**功能**: 施加多种边界条件，支持4种可配置类型。  
**输入/输出**: 守恒变量U(N, 3), 边界类型字符串bc_type。  
**边界条件类型**:
- `zero_gradient` (默认): 零梯度外推，`U[0,:]=U[1,:]`, `U[-1,:]=U[-2,:]`
- `reflective`: 固壁反射，动量分量取反，密度和能量零梯度
- `periodic`: 周期边界，`U[0,:]=U[-2,:]`, `U[-1,:]=U[1,:]`
- `transmissive`: 透射边界，基于特征线的对外行波外推

### 3.5 time_marcher.py
**功能**: 计算CFL条件约束的时间步长。  
**关键函数**: `compute_dt(U, dx, cfl)`  
**公式**: `dt = cfl * dx / max(|u| + c)`，其中c为当地声速。

### 3.6 exact_solver.py
**功能**: 计算Sod激波管问题的Riemann精确解。  
**算法**: 基于Toro (2009)的标准算法，使用Newton-Raphson迭代求解中间状态压力。  
**关键函数**: `sod_exact_solution(x, t, gamma)`  
**输出**: ρ(x,t), u(x,t), p(x,t)。

### 3.7 validator.py
**功能**: 误差计算与可视化。  
**误差范数**:
- L1: `sum(|数值解 - 精确解|) / N`
- L2: `sqrt(sum((数值解 - 精确解)²) / N)`  
- Linf: `max(|数值解 - 精确解|)`

## 四、数据流

```
config/YAML/JSON → run_simulation.py (load_any_config 自动检测格式)
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
mesh_generator  flow_initializer  exact_solver
    │               │               │
    ▼               ▼               ▼
    x, dx           U0         精确解数组
    │               │               │
    └───────┬───────┘               │
            ▼                       │
      solve_with_scheme             │
      (fd_schemes + boundary        │
       + time_marcher)              │
            │                       │
            ▼                       ▼
         U_final ──────► compute_errors ──► error_report.csv
            │
            ▼
   generate_comparison_plots ──► results/figures/*.png
   save_results ──► results/data/*.npy
```

## 五、依赖关系

```
numpy >= 1.21.0, < 2.0.0    [BSD-3-Clause]  数值计算核心
scipy >= 1.7.0               [BSD-3-Clause]  brentq求根(Riemann精确解)
matplotlib >= 3.5.0          [PSF-based]     可视化绘图
pyyaml >= 6.0                [MIT]           YAML配置解析 (JSON使用标准库)
pytest >= 7.0.0              [MIT]           测试框架(仅test)
flake8 >= 5.0.0              [MIT]           代码风格(仅dev)
```

## 六、注释规范

本项目遵循以下注释规范：

1. **模块级**: Google风格docstring，包含功能描述、文献依据
2. **函数级**: 参数/返回值/异常说明
3. **内联**: 仅在复杂算法处添加，说明物理意义
4. **语言**: 中文注释为主，关键术语保留英文

## 七、编译与构建

本项目为纯Python脚本，无需编译。通过pyproject.toml支持标准打包：

```bash
# 构建分发包
python -m build

# 生成文件
# dist/sod_shocktube_cfd-1.5.1-py3-none-any.whl
# dist/sod_shocktube_cfd-1.5.1.tar.gz
```

---

*文档版本: v1.5.1 | 更新日期: 2026-05-17*