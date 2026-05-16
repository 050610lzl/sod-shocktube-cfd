# 用户使用手册

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.0 |
| 发布日期 | 2026-05-16 |
| 适用版本 | v1.3.0 |
| 文档编号 | USER-MANUAL-001 |

---

## 1. 软件简介

### 1.1 什么是 Sod 激波管

Sod 激波管是计算流体力学（CFD）领域的经典基准测试问题，由 Gary A. Sod 于 1978 年在其论文 [1] 中提出。它模拟以下物理场景：

- 一根管道被隔膜分隔为高压区和低压区
- 隔膜破裂后，产生三种典型的流体动力学波系：
  - **左稀疏波**（Rarefaction Wave）：向左传播，压力平滑下降
  - **接触间断**（Contact Discontinuity）：密度不连续但压力/速度连续
  - **右激波**（Shock Wave）：向右传播，密度/压力/速度的强间断

Sod 激波管是检验 CFD 数值格式对间断捕捉能力的"Hello World"级基准测试。

### 1.2 标准 Sod 工况参数

| 物理量 | 左态（高压区） | 右态（低压区） |
|--------|:------------:|:------------:|
| 密度 rho | 1.0 | 0.125 |
| 速度 u | 0.0 | 0.0 |
| 压力 p | 1.0 | 0.1 |

- 计算域: x in [0, 1]
- 隔膜位置: x = 0.5
- 比热比: gamma = 1.4
- 仿真时间: t = 0.2
- 边界条件: 零梯度（外推边界）

### 1.3 本软件支持的 9 种数值格式

| 序号 | 格式名称 | 精度 | CLI 参数 | 类型 |
|:----:|----------|:----:|----------|------|
| 1 | Lax-Friedrichs | 一阶 | `lax_friedrichs` | 中心耗散型 |
| 2 | Lax-Wendroff | 二阶 | `lax_wendroff` | 中心色散型 |
| 3 | MacCormack | 二阶 | `macormack` | 预估校正型 |
| 4 | 一阶迎风 | 一阶 | `upwind` | Steger-Warming 分裂 |
| 5 | Rusanov | 一阶 | `rusanov` | 局部 Lax-Friedrichs |
| 6 | Godunov | 一阶 | `godunov` | 精确 Riemann 求解器 |
| 7 | Roe | 一阶 | `roe` | 近似 Riemann 求解器 |
| 8 | HLLC | 一阶 | `hllc` | 恢复接触间断 |
| 9 | TVD-Minmod | 二阶 | `tvd_minmod` | 通量限制型 |

### 1.4 核心功能

- 多格式对比验证：一次运行对比所有 9 种格式
- Riemann 精确解：基于 Toro (2009) 的精确 Riemann 求解器
- 定量误差分析：L1、L2、Linf 三种误差范数
- 可视化对比：密度、速度、压力的数值解与精确解对比图
- 时间戳归档：每次运行自动以时间戳归档，避免数据覆盖
- YAML 配置：通过配置文件控制所有仿真参数

---

## 2. 安装步骤

### 2.1 前置条件

- Python 3.9、3.10 或 3.11
- pip（Python 包管理器）
- Git（可选，用于克隆仓库）

### 2.2 安装步骤

**步骤 1: 获取源代码**

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
```

**步骤 2: 创建虚拟环境（强烈推荐）**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

**步骤 3: 安装项目**

```bash
pip install -e ".[test,dev]"
```

**步骤 4: 验证安装**

```bash
python -c "from src.mesh_generator import generate_mesh; print('OK')"
python -m pytest tests/ -v --tb=short
```

预期所有 34 项测试通过。

---

## 3. 快速入门

### 3.1 运行第一个仿真

在项目根目录执行：

```bash
python run_simulation.py --n_points 100 --scheme upwind
```

**预期输出**：

```
============================================================
一维Sod激波管CFD求解器 (有限差分法)
============================================================
[步骤1] 生成一维均匀网格...
[步骤2] 初始化流场...
[步骤3] 时间迭代求解...
  -> upwind: t=0.2000, 23 steps
[步骤4] 计算误差 (upwind)...
  rho误差: L1=1.234e-02, L2=1.560e-03
  u误差: L1=8.765e-03, L2=1.102e-03
  p误差: L1=1.512e-02, L2=2.015e-03
[步骤5] 生成对比图 (upwind)...
============================================================
求解完成!
```

### 3.2 查看结果

仿真完成后，在 `results/` 目录下查看：

```
results/
├── data/20260516_230000/         # 数值解数据（.npy 格式）
├── exact/20260516_230000/        # 精确解数据（.npy 格式）
├── figures/20260516_230000/      # 对比图（.png 格式）
└── error_report.csv              # 误差汇总表
```

打开 `results/figures/20260516_230000/20260516_230000_plot_upwind.png` 查看密度、速度、压力的对比图。

### 3.3 运行全部格式

```bash
python run_simulation.py --n_points 100
```

这将运行全部 9 种格式，并生成叠加对比图 `..._plot_all_schemes.png`。

---

## 4. 命令行参数详解

### 4.1 run_simulation.py 参数

```bash
python run_simulation.py [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--config` | str | `config/simulation_config.yaml` | 配置文件路径 |
| `--n_points` | int | `None`（使用配置文件值） | 网格节点数，覆盖配置文件 |
| `--cfl` | float | `None`（使用配置文件值） | CFL 数，覆盖配置文件 |
| `--scheme` | str | `None` | 指定单个格式运行 |
| `--schemes` | list | `None` | 指定多个格式运行 |

### 4.2 main.py 参数

```bash
python main.py [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--scheme` | str | `all` | 选择求解格式（`all` 或格式名称） |
| `--n_points` | int | `100` | 网格节点数 |
| `--cfl` | float | `0.8` | CFL 数 |
| `--t_final` | float | `0.2` | 仿真终止时间 |
| `--gamma` | float | `1.4` | 比热比 |
| `--output_dir` | str | `results` | 输出目录 |

### 4.3 命令行示例

```bash
# 基础用法
python run_simulation.py

# 指定分辨率
python run_simulation.py --n_points 200

# 指定 CFL
python run_simulation.py --cfl 0.5

# 单格式
python run_simulation.py --scheme roe

# 多格式
python run_simulation.py --schemes lax_friedrichs roe hllc

# 自定义配置
python run_simulation.py --config my_config.yaml --n_points 400 --cfl 0.9

# 网格收敛性研究（批量运行）
python run_simulation.py --n_points 50
python run_simulation.py --n_points 100
python run_simulation.py --n_points 200
python run_simulation.py --n_points 400
```

---

## 5. 配置文件详解

### 5.1 配置文件位置

`config/simulation_config.yaml`

### 5.2 配置项说明

#### mesh（网格参数）

```yaml
mesh:
  n_points: 100          # 网格节点数
  x_left: 0.0            # 左边界坐标
  x_right: 1.0           # 右边界坐标
```

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `n_points` | int | 100 | 20-2000 | 计算域内网格节点总数 |
| `x_left` | float | 0.0 | - | 计算域左边界 |
| `x_right` | float | 1.0 | - | 计算域右边界 |

#### physics（物理参数）

```yaml
physics:
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state:
    rho: 1.0
    u: 0.0
    p: 1.0
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `gamma` | float | 1.4 | 比热比（理想气体=1.4） |
| `diaphragm_pos` | float | 0.5 | 隔膜（初始间断）位置 |
| `left_state.rho` | float | 1.0 | 左态密度 |
| `left_state.u` | float | 0.0 | 左态速度 |
| `left_state.p` | float | 1.0 | 左态压力 |
| `right_state.rho` | float | 0.125 | 右态密度 |
| `right_state.u` | float | 0.0 | 右态速度 |
| `right_state.p` | float | 0.1 | 右态压力 |

#### simulation（仿真参数）

```yaml
simulation:
  t_final: 0.2
  cfl: 0.8
```

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `t_final` | float | 0.2 | 0-1.0 | 仿真终止时间 |
| `cfl` | float | 0.8 | 0.1-0.95 | CFL 数（受稳定性限制） |

#### schemes（数值格式列表）

```yaml
schemes:
  - lax_friedrichs
  - lax_wendroff
  - macormack
  - upwind
  - rusanov
  - godunov
  - roe
  - hllc
  - tvd_minmod
```

可选值：`lax_friedrichs`, `lax_wendroff`, `macormack`, `upwind`, `rusanov`, `godunov`, `roe`, `hllc`, `tvd_minmod`

#### output（输出配置）

```yaml
output:
  data_dir: results/data
  exact_dir: results/exact
  figures_dir: results/figures
  error_report: results/error_report.csv
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data_dir` | str | `results/data` | 数值解数据输出目录 |
| `exact_dir` | str | `results/exact` | 精确解数据输出目录 |
| `figures_dir` | str | `results/figures` | 对比图输出目录 |
| `error_report` | str | `results/error_report.csv` | 误差报告文件路径 |

---

## 6. 结果解读

### 6.1 输出文件说明

| 文件/目录 | 格式 | 内容 |
|----------|------|------|
| `results/data/<timestamp>/<timestamp>_data_<N>.npy` | NumPy 二进制 | 单个格式的密度、速度、压力、守恒变量 |
| `results/exact/<timestamp>/<timestamp>_data_exact.npy` | NumPy 二进制 | Riemann 精确解 |
| `results/figures/<timestamp>/<timestamp>_plot_<scheme>.png` | PNG 图像 | 单格式三图对比（密度/速度/压力） |
| `results/figures/<timestamp>/<timestamp>_plot_all_schemes.png` | PNG 图像 | 所有格式叠加对比 |
| `results/error_report.csv` | CSV 表格 | 所有格式的 L1/L2/Linf 误差汇总 |

### 6.2 图表含义

每张对比图包含三个子图：

- **密度 (rho)**: 展示左稀疏波、接触间断（密度跳变）、右激波
- **速度 (u)**: 展示稀疏波区域加速、接触间断（速度连续）、激波压缩
- **压力 (p)**: 展示稀疏波区域降压、接触间断（压力连续）、激波增压

图中：
- 蓝色实线：精确解（Toro 2009 算法）
- 橙色虚线：数值解（当前格式）
- 标题：格式名称、网格数、CFL 数

### 6.3 误差报告解读

`error_report.csv` 包含每种格式对密度、速度、压力的三类误差：

| 误差类型 | 全称 | 含义 |
|----------|------|------|
| L1 | 平均绝对误差 | 整体偏差的度量 |
| L2 | 均方根误差 | 对大偏差更敏感 |
| Linf | 最大绝对误差 | 最差情况的度量 |

**典型误差范围**（N=100 网格）：

| 格式 | L1(rho) | 备注 |
|------|---------|------|
| Lax-Friedrichs | ~0.04 | 耗散大，误差较大 |
| 迎风/Rusanov | ~0.02 | 一阶精度典型范围 |
| Lax-Wendroff | ~0.01 | 二阶精度但可能有振荡 |
| TVD-Minmod | ~0.008 | 当前最优格式 |

---

## 7. 进阶用法

### 7.1 网格收敛性研究

通过改变网格节点数验证格式的理论收敛阶：

```bash
# 批量运行不同分辨率
for N in 50 100 200 400; do
    python run_simulation.py --n_points $N
done
```

分析 `results/error_report.csv` 中各分辨率下的误差变化：
- 一阶格式：误差随 N 增大呈 O(N^(-1)) 递减
- 二阶格式：误差随 N 增大呈 O(N^(-2)) 递减

### 7.2 格式对比研究

```bash
# 运行全部格式，观察误差差异
python run_simulation.py --n_points 200
```

打开叠加对比图，观察：
- 一阶格式在激波处被"抹平"
- 二阶格式在激波处有振荡
- TVD 格式既锐利又无振荡
- HLLC 对接触间断分辨最好

### 7.3 自定义初始条件

编辑 `config/simulation_config.yaml`，修改 `left_state` 和 `right_state`：

```yaml
# 自定义 Sod 变体问题（压力比增大）
physics:
  left_state:
    rho: 1.0
    u: 0.0
    p: 5.0      # 增大高压侧压力
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
```

> **注意**：压力比过大可能导致部分格式崩溃，建议适当降低 CFL 数（如 0.3-0.5）。

### 7.4 编程接口使用

```python
import sys
sys.path.insert(0, '.')

from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.fd_schemes import solve_with_scheme
from src.exact_solver import sod_exact_solution
from src.validator import compute_errors

# 生成网格
x, dx = generate_mesh(n_points=100)

# 初始化流场
U0 = initialize_flow(x, gamma=1.4)

# 求解
U_final, t, steps = solve_with_scheme(
    'roe', U0, x, dx, t_final=0.2, cfl=0.8, gamma=1.4
)

# 获取精确解
rho_ex, u_ex, p_ex = sod_exact_solution(x, 0.2, 1.4)

# 计算误差
errors = compute_errors(U_final, rho_ex, u_ex, p_ex)
print(f"L1(rho) = {errors['rho']['L1']:.6e}")
```

### 7.5 性能优化建议

| 场景 | 建议 |
|------|------|
| 快速预览 | N=50, --scheme upwind |
| 日常开发 | N=100, --schemes lax_friedrichs roe hllc |
| 精度验证 | N=200, --scheme tvd_minmod |
| 最终报告 | N=400, 全部9种格式 |
| 收敛性研究 | N=50,100,200,400,800 批量运行 |

---

## 附录: 项目源码模块一览

| 模块 | 文件 | 功能 |
|------|------|------|
| 网格生成 | `src/mesh_generator.py` | 一维均匀网格生成 |
| 流场初始化 | `src/flow_initializer.py` | Sod 初始条件赋值 |
| 有限差分格式 | `src/fd_schemes.py` | 9 种 FDM 格式实现 |
| 边界处理 | `src/boundary_handler.py` | 零梯度外推边界 |
| 时间推进 | `src/time_marcher.py` | CFL 条件时间步长计算 |
| 精确解 | `src/exact_solver.py` | Riemann 精确解（Toro 2009） |
| 结果输出 | `src/output_writer.py` | 时间戳归档数据输出 |
| 验证模块 | `src/validator.py` | 误差计算与可视化 |

---

> **参考文献**:
> [1] Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. JCP, 27(1), 1-31.
> [2] Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.
> [3] Laney, C. B. (1998). Computational Gasdynamics. Cambridge University Press.
> [4] Anderson, J. D. (1995). Computational Fluid Dynamics: The Basics with Applications. McGraw-Hill.