# 一维Sod激波管CFD项目（有限差分法）构建文档

## 1. 项目概述

### 1.1 项目背景与意义

一维Sod激波管问题是计算流体力学（CFD）领域最经典的验证基准问题之一，由Gary A. Sod于1978年提出[1]。该问题是一个典型的Riemann问题，其解包含激波（shock）、接触间断（contact discontinuity）和稀疏波（rarefaction wave）三种典型的流体动力学间断结构[1]。由于该问题存在解析精确解，使其成为检验数值格式对间断捕捉能力的理想测试案例[3]。

有限差分法（Finite Difference Method, FDM）是求解双曲型守恒律方程的经典数值方法，具有格式简单、易于实现、计算效率高等优点[2]。通过采用多种有限差分格式求解Sod激波管问题，并与解析精确解进行定量对比，可以系统地评估不同格式在间断捕捉、数值耗散、数值色散等方面的表现差异[1]。

### 1.2 项目目标

本项目的核心目标为：

1. **数值求解目标**：基于有限差分法离散一维可压缩Euler方程组，采用多种经典FDM格式（Lax-Friedrichs、Lax-Wendroff、MacCormack、一阶迎风）求解Sod激波管问题[1][3]。

2. **验证对比目标**：将数值解与Riemann解析精确解进行定量对比，评估各格式的激波捕捉精度、接触间断分辨率及数值振荡特性[1]。

3. **工程学习目标**：建立一套可复用的CFD项目框架，为后续复杂问题的数值方法选择提供依据[3]。

### 1.3 文献依据与标准来源

本项目所有规范、参数设置、稳定性条件、验证标准均基于以下权威文献：

- **问题定义**：严格遵循OneFlow-CFD官方Sod激波管文档[4]与Sod原始论文[1]；
- **控制方程与气体参数**：参考Anderson可压缩流经典教材[2]；
- **有限差分格式理论**：参考Laney计算气体动力学教材[3]与Sod原始论文[1]；
- **验证标准**：采用Sod论文中的对比方法[1]与Laney教材中的误差分析框架[3]。

---

## 2. 问题标准定义（严格遵循OneFlow-CFD）

### 2.1 控制方程（一维可压缩欧拉方程）

本项目求解的控制方程为一维可压缩无黏Euler方程组（守恒形式）[1][2]：

$$\frac{\partial \mathbf{U}}{\partial t} + \frac{\partial \mathbf{F}(\mathbf{U})}{\partial x} = 0$$

其中守恒变量向量$\mathbf{U}$与通量向量$\mathbf{F}(\mathbf{U})$分别为：

$$\mathbf{U} = \begin{bmatrix} \rho \\ \rho u \\ \rho E \end{bmatrix}, \quad \mathbf{F}(\mathbf{U}) = \begin{bmatrix} \rho u \\ \rho u^2 + p \\ u(\rho E + p) \end{bmatrix}$$

式中各物理量定义：
- $\rho$：流体密度（kg/m³）
- $u$：流体速度（m/s）
- $p$：流体压力（Pa）
- $E$：单位质量总能（J/kg），$E = e + \frac{1}{2}u^2$，其中$e$为单位质量内能

理想气体状态方程[2]：

$$p = (\gamma - 1)\left(\rho E - \frac{1}{2}\rho u^2\right) = (\gamma - 1)\rho e$$

其中比热比$\gamma = 1.4$（标准空气）[1][4]。

### 2.2 初始条件（左/右状态参数）

根据OneFlow-CFD官方文档[4]与Sod原始论文[1]，计算域为$x \in [0, 1]$，初始间断位于$x = 0.5$处。$t = 0$时刻的初始条件为：

$$\begin{cases} (\rho_L, u_L, p_L) = (1.0, 0.0, 1.0), & 0 \leq x < 0.5 \quad \text{（高压侧）} \\ (\rho_R, u_R, p_R) = (0.125, 0.0, 0.1), & 0.5 \leq x \leq 1.0 \quad \text{（低压侧）} \end{cases}$$

**参数说明**：
- 左侧为高压高密度区，右侧为低压低密度区；
- 初始速度全场为零；
- 所有参数均为无量纲形式[1][4]。

### 2.3 边界条件（实现规则）

计算域左右两端采用**零梯度/外推边界条件**（zero-gradient / extrapolation boundary condition）[4]。

**实现规则**：

| 边界位置 | 实现方式 | 数学表述 |
|---------|---------|---------|
| 左边界（$x=0$） | 外推边界 | $\mathbf{U}_0^{n+1} = \mathbf{U}_1^{n+1}$ |
| 右边界（$x=1$） | 外推边界 | $\mathbf{U}_{N}^{n+1} = \mathbf{U}_{N-1}^{n+1}$ |

其中$N$为计算域最右侧网格节点索引。该边界条件假设边界处的物理量梯度为零，适用于激波管问题在仿真时间内波未传播至边界的情况[3][4]。

### 2.4 仿真参数（网格范围、终止时间、CFL约束）

| 参数名称 | 参数值/范围 | 说明 | 文献依据 |
|---------|------------|------|---------|
| 计算域 | $x \in [0, 1]$ | 一维空间范围 | [1][4] |
| 初始间断位置 | $x = 0.5$ | 隔膜位置 | [1][4] |
| 仿真终止时间 | $t = 0.2$ | 输出时刻 | [1][4] |
| 网格分辨率 | $N = 100, 200, 400$（推荐） | 网格节点数，用于收敛性分析 | [3] |
| CFL数 | $0.8 \leq \text{CFL} \leq 0.95$ | 推荐取值范围 | [3] |
| 比热比 | $\gamma = 1.4$ | 理想气体 | [1][2] |

---

## 3. 项目整体架构

### 3.1 项目目录结构

```
sod_shocktube_fdm/
├── config/                      # 配置文件目录
│   ├── simulation_config.yaml            # YAML 仿真参数配置
│   ├── simulation_config.json            # JSON 仿真参数配置 (v1.7.0+)
│   ├── simulation_config_custom_sod.json # 自定义初始条件 JSON 配置
│   └── simulation_config_high_res.json   # 高分辨率 JSON 配置
├── src/                         # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── mesh_generator.py        # 网格生成模块
│   ├── flow_initializer.py      # 流场初始化模块
│   ├── fd_schemes.py            # 有限差分格式模块（含多种FDM格式）
│   ├── boundary_handler.py      # 边界处理模块
│   ├── time_marcher.py          # 时间推进模块
│   ├── exact_solver.py          # 精确解计算模块
│   ├── output_writer.py         # 结果输出模块
│   └── validator.py             # 验证与误差分析模块
├── results/                     # 结果输出目录（自动创建）
│   ├── data/                    # 数值解数据文件
│   ├── exact/                   # 精确解数据文件
│   └── figures/                 # 可视化图表
├── tests/                       # 单元测试目录
│   ├── test_mesh.py             # 网格生成测试
│   ├── test_initialization.py   # 初始化测试
│   ├── test_boundary.py         # 边界条件测试
│   └── test_fd_schemes.py       # 差分格式测试
├── docs/                        # 文档目录
│   └── project_plan.md          # 项目计划书
├── requirements.txt             # Python依赖清单
├── run_simulation.py            # 主程序入口（流程编排）
└── README.md                    # 项目说明文档
```

**各目录用途说明**：

| 目录/文件 | 用途 |
|----------|------|
| `config/` | 存放仿真参数配置文件，支持不修改代码调整仿真参数 |
| `src/` | 核心求解器代码，按功能模块分离 |
| `results/` | 自动创建，存放数值解、精确解、对比图表 |
| `tests/` | 单元测试，确保各模块功能正确 |
| `docs/` | 项目文档，包括计划书、技术说明等 |
| `requirements.txt` | Python依赖包及版本要求 |
| `run_simulation.py` | 主程序入口，负责流程编排与模块调用 |

### 3.2 开发环境与依赖

**推荐开发环境**：

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | ≥ 3.8 | 推荐Python 3.10+ |
| NumPy | ≥ 1.21 | 数组运算与线性代数 |
| Matplotlib | ≥ 3.5 | 结果可视化 |
| PyYAML | ≥ 6.0 | 配置文件解析 |
| SciPy | ≥ 1.7 | 精确解求解辅助（非线性方程求解） |

**依赖清单文件**（`requirements.txt`）内容规范：

```
numpy>=1.21.0
matplotlib>=3.5.0
pyyaml>=6.0
scipy>=1.7.0
```

### 3.3 开发与运行流程

项目运行遵循以下标准流程[3]：

```
┌─────────────────────────────────────────────────────────────────┐
│                        仿真运行流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  步骤1: 配置加载                                                 │
│  ↓ 读取config/simulation_config.yaml，获取CFL、网格、终止时间等   │
│                                                                 │
│  步骤2: 网格生成                                                 │
│  ↓ 调用mesh_generator，生成一维均匀网格                          │
│                                                                 │
│  步骤3: 流场初始化                                               │
│  ↓ 调用flow_initializer，按初始条件赋值ρ、u、p                    │
│                                                                 │
│  步骤4: 时间迭代循环                                             │
│  ↓ while t < t_final:                                           │
│  │   4.1 计算时间步长Δt（CFL条件）                               │
│  │   4.2 调用fd_schemes计算空间导数                              │
│  │   4.3 调用time_marcher更新守恒变量                            │
│  │   4.4 调用boundary_handler施加边界条件                        │
│  │   4.5 t = t + Δt                                             │
│                                                                 │
│  步骤5: 结果输出                                                 │
│  ↓ 调用output_writer保存数值解数据                               │
│                                                                 │
│  步骤6: 精确解计算                                               │
│  ↓ 调用exact_solver计算t=0.2时刻的解析解                         │
│                                                                 │
│  步骤7: 验证与对比                                               │
│  ↓ 调用validator计算误差、生成对比图表                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 有限差分法核心方案设计

### 4.1 离散策略（空间离散+时间离散）

**空间离散**：

采用有限差分法对Euler方程的空间导数项$\partial\mathbf{F}/\partial x$进行离散[1][3]。在均匀网格$x_i = i\Delta x$上，空间导数近似为：

$$\left.\frac{\partial \mathbf{F}}{\partial x}\right|_i \approx \mathcal{D}(\mathbf{F})_i$$

其中$\mathcal{D}$为差分算子，具体形式取决于所选格式（中心差分、迎风差分等）[3]。

**时间离散**：

采用显式时间推进方法[3]。对于守恒形式$\partial\mathbf{U}/\partial t = -\partial\mathbf{F}/\partial x$，时间离散为：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n + \Delta t \cdot \mathcal{T}\left(-\mathcal{D}(\mathbf{F})_i\right)$$

其中$\mathcal{T}$为时间推进算子（如前向Euler、Runge-Kutta等）[3]。

### 4.2 拟选用FDM格式

根据Sod原始论文[1]与Laney教材[3]，本项目拟选用以下4种经典有限差分格式：

| 格式编号 | 格式名称 | 精度 | 类型 | 文献依据 |
|---------|---------|------|------|---------|
| FDM-1 | Lax-Friedrichs | 一阶 | 中心型耗散格式 | [1][3] |
| FDM-2 | Lax-Wendroff | 二阶 | 中心型色散格式 | [1][3] |
| FDM-3 | MacCormack | 二阶 | 预估校正型 | [1][3] |
| FDM-4 | 一阶迎风 | 一阶 | 迎风型 | [3] |

### 4.3 格式选型依据、精度、稳定性、间断捕捉特性

#### FDM-1: Lax-Friedrichs格式

**离散公式**[1][3]：

$$\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_{i+1}^n + \mathbf{U}_{i-1}^n\right) - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right)$$

| 特性 | 说明 | 文献依据 |
|------|------|---------|
| 空间精度 | 一阶$O(\Delta x)$ | [3] |
| 时间精度 | 一阶$O(\Delta t)$ | [3] |
| 稳定性 | CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$ | [3] |
| 数值耗散 | 大，激波被抹平3-5个网格 | [1][3] |
| 数值振荡 | 无 | [3] |
| 间断捕捉 | 激波位置准确，接触间断分辨率差 | [1] |

#### FDM-2: Lax-Wendroff格式

**离散公式**[1][3]：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right) + \frac{(\Delta t)^2}{2(\Delta x)^2}\left[\mathbf{A}_{i+1/2}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right) - \mathbf{A}_{i-1/2}\left(\mathbf{F}_i^n - \mathbf{F}_{i-1}^n\right)\right]$$

其中$\mathbf{A} = \partial\mathbf{F}/\partial\mathbf{U}$为Jacobian矩阵[3]。

| 特性 | 说明 | 文献依据 |
|------|------|---------|
| 空间精度 | 二阶$O(\Delta x^2)$ | [3] |
| 时间精度 | 二阶$O(\Delta t^2)$ | [3] |
| 稳定性 | CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$ | [3] |
| 数值耗散 | 小 | [3] |
| 数值振荡 | 显著（间断附近过冲/下冲） | [1][3] |
| 间断捕捉 | 光滑区精度高，间断区振荡严重 | [1] |

#### FDM-3: MacCormack格式

**离散公式**[1][3]：

预估步：$\mathbf{U}_i^* = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right)$

校正步：$\mathbf{U}_i^{**} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_i^* - \mathbf{F}_{i-1}^*\right)$

最终解：$\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_i^* + \mathbf{U}_i^{**}\right)$

| 特性 | 说明 | 文献依据 |
|------|------|---------|
| 空间精度 | 二阶$O(\Delta x^2)$ | [3] |
| 时间精度 | 二阶$O(\Delta t^2)$ | [3] |
| 稳定性 | CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$ | [3] |
| 数值耗散 | 小 | [3] |
| 数值振荡 | 中等（小于Lax-Wendroff） | [1] |
| 间断捕捉 | 激波位置准确，接触间断有振荡 | [1] |

#### FDM-4: 一阶迎风格式

**离散公式**（以Steger-Warming通量分裂为例）[3]：

$$\mathbf{F} = \mathbf{F}^+ + \mathbf{F}^-$$

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left[\left(\mathbf{F}_{i}^+ - \mathbf{F}_{i-1}^+\right) + \left(\mathbf{F}_{i+1}^- - \mathbf{F}_i^-\right)\right]$$

| 特性 | 说明 | 文献依据 |
|------|------|---------|
| 空间精度 | 一阶$O(\Delta x)$ | [3] |
| 时间精度 | 一阶$O(\Delta t)$ | [3] |
| 稳定性 | CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$ | [3] |
| 数值耗散 | 中等 | [3] |
| 数值振荡 | 无 | [3] |
| 间断捕捉 | 激波锐利（2-3网格），接触间断抹平 | [3] |

### 4.4 CFL稳定性条件与时间步长计算规则

**CFL条件**[3]：

显式有限差分格式必须满足CFL（Courant-Friedrichs-Lewy）稳定性条件：

$$\text{CFL} = |\lambda_{\max}| \frac{\Delta t}{\Delta x} \leq 1$$

其中$\lambda_{\max}$为Euler方程Jacobian矩阵的最大特征值：

$$\lambda_{\max} = \max_i\left(|u_i| + c_i\right)$$

式中$c = \sqrt{\gamma p / \rho}$为当地声速[2]。

**时间步长计算规则**：

$$\Delta t = \text{CFL}_{\text{target}} \cdot \frac{\Delta x}{\max_i\left(|u_i| + c_i\right)}$$

**推荐参数**：

| 格式 | 推荐CFL数 | 说明 |
|------|----------|------|
| Lax-Friedrichs | 0.8-0.9 | 耗散大，CFL可取较大值 |
| Lax-Wendroff | 0.8-0.9 | 需控制振荡 |
| MacCormack | 0.8-0.9 | 需控制振荡 |
| 一阶迎风 | 0.8-0.95 | 稳定性好 |

---

## 5. 核心模块构建规范

### 5.1 网格生成模块（参数、分辨率、离散规则）

**模块文件**：`src/mesh_generator.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 网格类型 | 一维均匀网格 |
| 计算域 | $x \in [0, 1]$ |
| 网格节点数 | 可配置，推荐$N = 100, 200, 400$ |
| 网格间距 | $\Delta x = 1 / (N - 1)$ |
| 节点坐标 | $x_i = (i-1)\Delta x$，$i = 1, 2, \ldots, N$ |
| 输出 | 返回网格坐标数组`x`与间距`dx` |

**输入参数**：

| 参数名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `n_points` | int | 网格节点数 | 100 |
| `x_left` | float | 左边界坐标 | 0.0 |
| `x_right` | float | 右边界坐标 | 1.0 |

**输出数据**：

| 输出名 | 类型 | 说明 |
|--------|------|------|
| `x` | numpy.ndarray | 网格坐标数组，形状`(N,)` |
| `dx` | float | 网格间距 |

### 5.2 流场初始化模块（初始条件赋值规则）

**模块文件**：`src/flow_initializer.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 初始化变量 | 守恒变量$\mathbf{U} = [\rho, \rho u, \rho E]^T$ |
| 间断位置 | $x = 0.5$ |
| 左侧状态 | $\rho_L=1.0, u_L=0, p_L=1.0$ |
| 右侧状态 | $\rho_R=0.125, u_R=0, p_R=0.1$ |
| 总能计算 | $E = \frac{p}{(\gamma-1)\rho} + \frac{1}{2}u^2$ |
| 比热比 | $\gamma = 1.4$ |

**输入参数**：

| 参数名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `x` | numpy.ndarray | 网格坐标数组 | - |
| `gamma` | float | 比热比 | 1.4 |
| `diaphragm_pos` | float | 隔膜位置 | 0.5 |
| `left_state` | dict | 左侧状态`{'rho': 1.0, 'u': 0.0, 'p': 1.0}` | 见左列 |
| `right_state` | dict | 右侧状态`{'rho': 0.125, 'u': 0.0, 'p': 0.1}` | 见左列 |

**输出数据**：

| 输出名 | 类型 | 说明 | 形状 |
|--------|------|------|------|
| `U` | numpy.ndarray | 守恒变量数组 | `(N, 3)` |

**赋值规则**：

- 对于$x_i < 0.5$的节点，赋左侧状态；
- 对于$x_i \geq 0.5$的节点，赋右侧状态；
- 原始变量$(\rho, u, p)$需转换为守恒变量$(\rho, \rho u, \rho E)$[2]。

### 5.3 有限差分离散模块（空间/时间差分实现规范）

**模块文件**：`src/fd_schemes.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 格式数量 | 至少实现4种格式（Lax-Friedrichs、Lax-Wendroff、MacCormack、一阶迎风） |
| 接口统一 | 各格式采用统一的函数签名 |
| 通量计算 | 内部需实现从守恒变量到通量的转换 |
| 内部节点 | 仅对内部节点$i=2,\ldots,N-1$进行差分计算 |
| 边界节点 | 由边界处理模块单独处理 |

**统一接口规范**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `U` | numpy.ndarray | 当前时间层守恒变量，形状`(N, 3)` |
| `dx` | float | 网格间距 |
| `dt` | float | 时间步长 |
| `gamma` | float | 比热比 |

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `U_new` | numpy.ndarray | 下一时间层守恒变量，形状`(N, 3)` |

**各格式实现要点**：

| 格式 | 实现要点 |
|------|---------|
| Lax-Friedrichs | 使用相邻节点平均值替代中心节点，计算中心差分通量 |
| Lax-Wendroff | 计算Jacobian矩阵或采用守恒形式的二阶修正项 |
| MacCormack | 分预估步（前差）和校正步（后差），取平均 |
| 一阶迎风 | 实现Steger-Warming通量分裂，按特征值符号分离通量 |

### 5.4 边界处理模块（零梯度实现逻辑）

**模块文件**：`src/boundary_handler.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 边界类型 | 零梯度/外推边界 |
| 左边界 | $\mathbf{U}_0 = \mathbf{U}_1$ |
| 右边界 | $\mathbf{U}_{N-1} = \mathbf{U}_{N-2}$ |
| 施加时机 | 每个时间步更新守恒变量后 |

**输入参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `U` | numpy.ndarray | 守恒变量数组，形状`(N, 3)` |

**输出数据**：

| 输出名 | 类型 | 说明 |
|--------|------|------|
| `U` | numpy.ndarray | 施加边界条件后的守恒变量数组 |

**实现逻辑**：

1. 将左边界节点（索引0）的值设置为相邻内部节点（索引1）的值；
2. 将右边界节点（索引N-1）的值设置为相邻内部节点（索引N-2）的值；
3. 该操作在所有守恒变量分量上独立执行[3][4]。

### 5.5 时间推进模块（显式迭代规则）

**模块文件**：`src/time_marcher.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 推进方式 | 显式时间推进 |
| 时间步长 | 按CFL条件动态计算 |
| 终止条件 | $t \geq t_{\text{final}} = 0.2$ |
| 迭代计数 | 记录总迭代步数 |

**时间步长计算规则**：

1. 从当前流场提取速度$u$和声速$c = \sqrt{\gamma p / \rho}$；
2. 计算最大特征值$\lambda_{\max} = \max(|u| + c)$；
3. 按$\Delta t = \text{CFL} \cdot \Delta x / \lambda_{\max}$计算时间步长；
4. 确保$t + \Delta t$不超过$t_{\text{final}}$，若超过则取$\Delta t = t_{\text{final}} - t$。

**输入参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `U` | numpy.ndarray | 当前守恒变量 |
| `dx` | float | 网格间距 |
| `cfl` | float | CFL数 |
| `gamma` | float | 比热比 |
| `t_current` | float | 当前时间 |
| `t_final` | float | 终止时间 |

**输出数据**：

| 输出名 | 类型 | 说明 |
|--------|------|------|
| `dt` | float | 计算得到的时间步长 |
| `U_new` | numpy.ndarray | 推进后的守恒变量 |

### 5.6 结果输出模块（数据保存、格式、路径）

**模块文件**：`src/output_writer.py`

**功能规范**：

| 规范项 | 要求 |
|--------|------|
| 输出格式 | NumPy `.npy`格式（数值解）+ CSV格式（便于查看） |
| 输出路径 | `results/data/`目录 |
| 文件命名 | `{scheme_name}_N{num_points}.npy` |
| 输出内容 | 网格坐标`x`、守恒变量`U`、原始变量`rho, u, p`、仿真时间`t` |

**输出数据结构**：

| 数据项 | 形状 | 说明 |
|--------|------|------|
| `x` | `(N,)` | 网格坐标 |
| `U` | `(N, 3)` | 守恒变量 |
| `rho` | `(N,)` | 密度 |
| `u` | `(N,)` | 速度 |
| `p` | `(N,)` | 压力 |
| `t` | 标量 | 仿真终止时间 |

**目录结构**：

```
results/
├── data/
│   ├── lax_friedrichs_N100.npy
│   ├── lax_wendroff_N100.npy
│   ├── macormack_N100.npy
│   └── upwind_N100.npy
├── exact/
│   └── exact_solution_N100.npy
└── figures/
    ├── density_comparison.png
    ├── velocity_comparison.png
    └── pressure_comparison.png
```

---

## 6. 验证与评估方案

### 6.1 精确解来源（Riemann解析解）

Sod激波管问题的精确解为Riemann问题的解析解[1][3]。在$t=0.2$时刻，解的结构包含以下区域[1]：

| 区域 | 位置范围 | 波的类型 | 说明 |
|------|---------|---------|------|
| 区域1 | $x < x_{\text{head}}$ | 未扰动区 | 保持左侧初始状态 |
| 区域2 | $x_{\text{head}} \leq x < x_{\text{contact}}$ | 稀疏波区 | 等熵膨胀，解析表达式可求 |
| 区域3 | $x_{\text{contact}} \leq x < x_{\text{shock}}$ | 接触间断后 | 密度间断，速度压力连续 |
| 区域4 | $x \geq x_{\text{shock}}$ | 激波后 | 保持右侧初始状态 |

**精确解计算模块**：`src/exact_solver.py`

该模块需实现Riemann精确解的计算，包括[3]：
1. 求解接触间断处的压力$p^*$（通过非线性方程迭代）；
2. 计算稀疏波区域内的解析解；
3. 计算激波位置与激波后状态；
4. 输出与数值解相同网格位置的精确解数据。

### 6.2 对比指标（压力/密度/速度剖面、L2误差）

**定性对比**：

| 对比项 | 说明 | 文献依据 |
|--------|------|---------|
| 密度剖面 | 检验接触间断分辨率 | [1] |
| 速度剖面 | 检验稀疏波与激波捕捉 | [1] |
| 压力剖面 | 检验激波位置与强度 | [1] |

**定量对比**：

采用L2范数误差作为定量评估指标[3]：

$$L_2\text{误差} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}\left(\phi_i^{\text{num}} - \phi_i^{\text{exact}}\right)^2}$$

其中$\phi$为待比较的物理量（$\rho$、$u$或$p$），上标`num`表示数值解，`exact`表示精确解[3]。

**误差评估表**：

| 格式 | $L_2(\rho)$ | $L_2(u)$ | $L_2(p)$ | 网格数 |
|------|------------|----------|----------|--------|
| Lax-Friedrichs | - | - | - | 100/200/400 |
| Lax-Wendroff | - | - | - | 100/200/400 |
| MacCormack | - | - | - | 100/200/400 |
| 一阶迎风 | - | - | - | 100/200/400 |

### 6.3 验证流程（分步验证+整体验证）

**分步验证**：

| 步骤 | 验证内容 | 验证方法 |
|------|---------|---------|
| 步骤1 | 网格生成正确性 | 检查网格间距、节点数、边界坐标 |
| 步骤2 | 初始条件正确性 | 检查左右状态赋值、间断位置 |
| 步骤3 | 边界条件正确性 | 检查边界节点值是否等于相邻内部节点 |
| 步骤4 | 单步差分正确性 | 对已知流场执行单步差分，检查输出合理性 |
| 步骤5 | 时间推进正确性 | 检查时间步长计算、CFL条件满足 |

**整体验证**：

| 步骤 | 验证内容 | 验证方法 |
|------|---------|---------|
| 步骤6 | 数值解与精确解对比 | 绘制密度/速度/压力剖面对比图 |
| 步骤7 | 误差定量分析 | 计算L2误差，评估格式精度 |
| 步骤8 | 网格收敛性 | 比较N=100/200/400的误差变化 |

### 6.4 结果可视化规范（绘图维度、对比方式）

**绘图规范**：

| 规范项 | 要求 |
|--------|------|
| 图表数量 | 至少3张（密度、速度、压力对比图） |
| 图表格式 | PNG格式，分辨率≥300 DPI |
| 图例 | 包含数值解（不同格式用不同颜色/线型）与精确解（黑色实线） |
| 坐标轴 | 横轴为位置$x$，纵轴为对应物理量 |
| 标题 | 包含格式名称、网格数、仿真时间 |
| 保存路径 | `results/figures/` |

**对比图示例结构**：

| 图表文件 | 横轴 | 纵轴 | 曲线 |
|---------|------|------|------|
| `density_comparison.png` | $x$ | $\rho$ | 各格式数值解 + 精确解 |
| `velocity_comparison.png` | $x$ | $u$ | 各格式数值解 + 精确解 |
| `pressure_comparison.png` | $x$ | $p$ | 各格式数值解 + 精确解 |

---

## 7. 项目交付物清单

### 7.1 代码工程交付物

| 交付物 | 说明 | 存放位置 |
|--------|------|---------|
| 完整项目代码 | 包含所有模块的Python源代码 | `src/` |
| 配置文件 | 仿真参数配置YAML文件 | `config/` |
| 依赖清单 | Python依赖包及版本要求 | `requirements.txt` |
| 主程序入口 | 流程编排脚本 | `run_simulation.py` |
| 单元测试 | 各模块功能测试脚本 | `tests/` |

### 7.2 文档交付物

| 交付物 | 说明 | 存放位置 |
|--------|------|---------|
| 项目计划书 | Plan阶段规划文档 | `docs/project_plan.md` |
| 项目构建文档 | 本文档 | 项目根目录 |
| README | 项目说明、安装与运行指南 | `README.md` |
| 数值方法调研报告 | 有限差分格式调研总结 | `docs/fdm_survey.md` |

### 7.3 结果交付物

| 交付物 | 说明 | 存放位置 |
|--------|------|---------|
| 数值解数据 | 各格式的数值解（.npy + .csv） | `results/data/` |
| 精确解数据 | Riemann解析解（.npy + .csv） | `results/exact/` |
| 对比图表 | 密度/速度/压力对比图（.png） | `results/figures/` |
| 误差分析报告 | 各格式L2误差汇总表格 | `results/error_report.csv` |

---

## 8. 参考文献（GB/T 7714格式）

[1] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31. DOI: 10.1016/0021-9991(78)90023-2.

[2] ANDERSON J D. Modern compressible flow: with historical perspective[M]. 2nd ed. New York: McGraw-Hill Education, 1984.

[3] LANEY C B. Computational gasdynamics[M]. Cambridge: Cambridge University Press, 1998.

[4] OneFlow-CFD Documentation. Sod's shock-tube problem[EB/OL]. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html.
