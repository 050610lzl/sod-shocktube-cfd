# 一维Sod激波管CFD项目代码说明

## 项目概述

本项目基于**有限差分法(FDM)**求解一维Sod激波管问题，实现4种经典数值格式并与解析精确解进行定量对比验证。

**依据**: `CFD_Sod_ShockTube_Project_Plan.md`, `Sod_ShockTube_CFD_Project_Build.md`

## 项目结构

```
sod_shocktube_fdm/
├── config/
│   └── simulation_config.yaml   # 仿真参数配置
├── src/
│   ├── __init__.py              # 包初始化
│   ├── mesh_generator.py        # 网格生成 (Build §5.1)
│   ├── flow_initializer.py      # 流场初始化 (Build §5.2)
│   ├── fd_schemes.py            # 有限差分格式 (Build §5.3)
│   ├── boundary_handler.py      # 边界处理 (Build §5.4)
│   ├── time_marcher.py          # 时间推进 (Build §5.5)
│   ├── exact_solver.py          # 精确解计算 (Build §5.6)
│   ├── output_writer.py         # 结果输出 (Build §5.7)
│   └── validator.py             # 验证分析 (Build §5.8)
├── results/                     # 结果输出目录
├── tests/                       # 单元测试目录
├── docs/                        # 文档目录
├── run_simulation.py            # 主程序入口 (Build §3.3)
── requirements.txt             # Python依赖 (Build §3.2)
└── README_CODE.md               # 本文件
```

## 运行说明

### 环境要求

```bash
pip install -r requirements.txt
```

### 基本运行

```bash
# 使用默认配置运行所有4种格式
python run_simulation.py

# 指定网格分辨率
python run_simulation.py --n_points 200

# 指定CFL数
python run_simulation.py --cfl 0.9

# 仅运行指定格式
python run_simulation.py --scheme lax_friedrichs

# 运行多个指定格式
python run_simulation.py --schemes lax_friedrichs upwind
```

### 配置文件

编辑 `config/simulation_config.yaml` 可修改:
- 网格节点数 (n_points)
- CFL数 (cfl)
- 仿真终止时间 (t_final)
- 比热比 (gamma)
- 初始条件 (left_state, right_state)

## 模块说明

| 模块 | 文件 | 功能 | 文献依据 |
|------|------|------|---------|
| 网格生成 | `src/mesh_generator.py` | 一维均匀网格离散 | Laney (1998) [3] |
| 流场初始化 | `src/flow_initializer.py` | Sod标准初始条件赋值 | Sod (1978) [1], OneFlow-CFD [4] |
| 有限差分格式 | `src/fd_schemes.py` | 4种FDM格式实现 | Sod (1978) [1], Laney (1998) [3] |
| 边界处理 | `src/boundary_handler.py` | 零梯度外推边界 | Laney (1998) [3], OneFlow-CFD [4] |
| 时间推进 | `src/time_marcher.py` | CFL时间步长计算 | LeVeque (1992) [5] |
| 精确解 | `src/exact_solver.py` | Riemann解析解 | Toro (2009) [2] |
| 结果输出 | `src/output_writer.py` | 数据保存 | Build §5.7 |
| 验证分析 | `src/validator.py` | 误差计算与可视化 | Laney (1998) [3] |

## 数值格式

| 格式 | 精度 | 类型 | 文献 |
|------|------|------|------|
| Lax-Friedrichs | 一阶 | 中心耗散 | Sod (1978) [1] |
| Lax-Wendroff | 二阶 | 中心色散 | Sod (1978) [1] |
| MacCormack | 二阶 | 预估校正 | Sod (1978) [1] |
| 一阶迎风 | 一阶 | Steger-Warming分裂 | Laney (1998) [3] |

## 参考文献

[1] Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. Journal of Computational Physics, 27(1), 1-31.

[2] Anderson, J. D. (1984). Modern Compressible Flow: With Historical Perspective. McGraw-Hill Education.

[3] Laney, C. B. (1998). Computational Gasdynamics. Cambridge University Press.

[4] OneFlow-CFD Documentation. Sod's shock-tube problem. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html

[5] LeVeque, R. J. (1992). Numerical Methods for Conservation Laws. Birkhäuser.

[6] 陶文. 计算流体力学基础与应用. 西安交通大学出版社, 2018.
