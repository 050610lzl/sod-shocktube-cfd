# 需求规格说明书 (Software Requirements Specification, SRS)

## 一维Sod激波管CFD数值格式对比项目

| 项目 | 内容 |
|------|------|
| 文档编号 | SRS-SOD-CFD-1.5 |
| 版本号 | 1.5.1 |
| 编制日期 | 2026-05-17 |
| 编制人 | CFD课程项目组 |
| 审核状态 | 草案 |
| 文档密级 | 内部 |

---

## 1. 引言

### 1.1 目的

本文档定义了一维Sod激波管CFD数值格式对比项目的完整软件需求规格。该项目的核心目的是：基于Sod(1978)提出的标准激波管问题设置，采用多种有限差分格式(FDM)求解一维可压缩Euler方程，并将各数值格式的解与解析精确解进行定量对比验证[1][2]。

本文档旨在明确项目的功能需求、非功能需求、接口需求与数据需求，为后续的软件设计、代码实现和验收测试提供统一的规范基准。

### 1.2 范围

本软件产品为一维可压缩Euler方程的有限差分数值求解器，主要功能包括：

- 一维均匀网格的自动生成
- 基于Sod标准初始条件的流场初始化
- 9种经典有限差分格式的数值求解（涵盖一阶/二阶、中心/迎风、经典/现代格式）
- Riemann精确解的解析计算
- 数值解与精确解的L1/L2/L∞误差定量分析
- 对比图表的自动生成（密度、速度、压力、总能四幅子图）
- CLI命令行接口与YAML配置文件的参数管理

本软件适用于CFD课程教学、数值格式对比研究等场景，计算域限定为一维区间$x \in [0,1]$，物理模型为无黏可压缩理想气体（比热比$\gamma = 1.4$）。

### 1.3 术语与定义

| 术语/缩写 | 英文全称 | 中文释义 | 参考文献 |
|-----------|---------|---------|---------|
| Sod | Sod Shock Tube | Sod激波管标准问题 | [1] |
| FDM | Finite Difference Method | 有限差分法 | [3][4] |
| Euler | Euler Equations | 可压缩无黏Euler方程组 | [2] |
| CFL | Courant-Friedrichs-Lewy | CFL稳定性条件 | [4] |
| TVD | Total Variation Diminishing | 总变差不增 | [5] |
| HLLC | Harten-Lax-van Leer-Contact | 恢复接触间断的HLL格式 | [2] |
| Riemann | Riemann Problem | 黎曼问题（间断分解问题） | [2] |
| L1/L2/L∞ | L1/L2/L∞ Norm | 误差范数（绝对值/均方根/最大值） | [4] |
| CLI | Command Line Interface | 命令行接口 | -- |
| YAML | YAML Ain't Markup Language | YAML配置语言 | -- |

### 1.4 参考文献

本文档引用的核心文献如下（完整文献信息见第8章）：

1. Sod (1978) -- 激波管问题的原始定义与多种格式对比[1]
2. Toro (2009) -- Riemann求解器与数值方法的权威教材[2]
3. Laney (1998) -- 可压缩流CFD基础教材[3]
4. LeVeque (1992) -- 守恒律数值方法的经典教材[4]

---

## 2. 总体描述

### 2.1 产品视角

本软件产品是一个**独立的命令行数值仿真工具**，不依赖外部CFD商业软件或框架。其系统边界与外部交互如下图所示：

```
+---------------------------------------------------+
|             Sod激波管CFD求解器 v1.0                 |
|                                                   |
|  [YAML配置文件] --> [配置解析模块]                      |
|                     ↓                              |
|  [CLI参数]      --> [参数合并] --> [主控制器]          |
|                                    ↓               |
|              [网格生成] --> [流场初始化]               |
|                                    ↓               |
|              [9种FDM求解] ←→ [精确解计算]              |
|                                    ↓               |
|              [误差分析] --> [可视化] --> [结果输出]      |
|                                                   |
+---------------------------------------------------+
        ↑                ↓                ↓
   OneFlow-CFD      精确解数据        对比图/误差报告
   文档[6]         (.npy/.csv)        (.png/.csv)
```

本软件参考OneFlow-CFD官方文档[6]中Sod激波管示例的问题设置，但采用自研代码实现求解器核心逻辑，确保数值格式的完全可控性与对比研究的可复现性。

### 2.2 用户特征

本软件的目标用户群体及其特征如下：

| 用户类别 | 背景知识要求 | 使用方式 |
|---------|-------------|---------|
| CFD课程学生 | 具备流体力学基础，了解Euler方程和有限差分法概念 | 通过CLI运行仿真，查看对比图表，撰写实验报告 |
| 授课教师 | 精通CFD，可对结果进行专业评判 | 验证教学案例，检查学生项目的正确性 |
| 数值方法研究者 | 精通数值格式理论，关注格式对比细节 | 扩展新格式，进行系统的网格收敛性分析 |

用户需具备以下最低技能：
- 能够使用命令行终端执行Python脚本
- 能够编辑YAML格式的文本配置文件
- 理解CFL条件、误差范数等基本CFD概念

### 2.3 运行环境

| 环境要素 | 最低要求 | 推荐配置 |
|---------|---------|---------|
| 操作系统 | Windows 10 / macOS 11 / Ubuntu 20.04 | 同最低要求 |
| Python版本 | Python 3.8+ | Python 3.10+ |
| 依赖库 | NumPy >= 1.20, SciPy >= 1.7, Matplotlib >= 3.4 | 最新稳定版 |
| 内存 | 512 MB | 2 GB |
| 磁盘空间 | 100 MB | 500 MB |
| 其他 | PyYAML >= 5.4 | -- |

### 2.4 设计约束

1. **语言约束**：所有代码使用Python 3编写，遵循PEP 8编码规范。
2. **平台约束**：必须能在Windows、macOS、Linux三类主流操作系统上不加修改地运行。
3. **性能约束**：在N=100网格条件下，**单个数值格式**的完整仿真（含精确解计算与误差分析）总耗时不得超过5秒。
4. **精度约束**：所有格式在N=100网格条件下，密度场的L1误差范数不得超过$1 \times 10^{-2}$。
5. **文献合规**：所有数值格式的实现必须标注明确的文献出处[1][2][3][4]。
6. **开源合规**：仅使用开源库（NumPy、SciPy、Matplotlib、PyYAML），不依赖任何商业软件或专有库。

---

## 3. 功能需求

### 3.1 功能模块总览

| 功能编号 | 功能名称 | 优先级 | 描述 |
|---------|---------|-------|------|
| F-01 | 网格生成 | 高 | 生成一维均匀计算网格 |
| F-02 | 流场初始化 | 高 | 按Sod标准条件初始化守恒变量场 |
| F-03 | 9种FDM格式求解 | 高 | 实现9种有限差分格式的时间推进 |
| F-04 | 精确解计算 | 高 | 计算Riemann问题的解析精确解 |
| F-05 | 误差分析 | 高 | 计算L1/L2/L∞三种误差范数 |
| F-06 | 可视化 | 中 | 生成数值解与精确解的对比图 |
| F-07 | 配置管理 | 中 | 支持YAML文件配置仿真参数 |
| F-08 | 版本管理 | 低 | 提供版本号查询与更新机制 |

### 3.2 F-01: 网格生成

#### 描述
生成一维均匀结构化计算网格，覆盖计算域$x \in [x_L, x_R]$。

#### 输入
| 参数名 | 类型 | 范围 | 默认值 | 说明 |
|--------|------|------|--------|------|
| n_points | int | [50, 10000] | 100 | 网格节点总数 |
| x_left | float | [0.0, 0.4] | 0.0 | 左边界坐标 |
| x_right | float | [0.6, 2.0] | 1.0 | 右边界坐标 |

#### 输出
- `x`: 一维坐标数组，形状为`(n_points,)`，等间距分布
- `dx`: 网格间距标量，$dx = (x_R - x_L) / (N - 1)$

#### 前置条件
- `n_points >= 2`
- `x_left < x_right`

#### 后置条件
- `x[0] == x_left`（精确到浮点误差）
- `x[-1] == x_right`（精确到浮点误差）
- 相邻节点间距误差$< 10^{-12}$

#### 文献依据
标准CFD网格生成方法[3][4]。对于一维均匀网格，节点坐标为$x_i = x_L + i \cdot \Delta x, i = 0,1,...,N-1$。

---

### 3.3 F-02: 流场初始化

#### 描述
按照Sod标准初始条件[1]，将计算域在$x = x_{\text{diaphragm}}$处划分为左右两个均匀区域，分别赋予不同的密度、速度和压力，并将其转换为守恒变量。

#### 输入
| 参数名 | 类型 | 说明 |
|--------|------|------|
| x | ndarray | 网格坐标数组（来自F-01） |
| diaphragm_pos | float | 隔膜位置，默认0.5 |
| left_state: {rho, u, p} | dict | 左侧状态：$\rho_L=1.0, u_L=0.0, p_L=1.0$ |
| right_state: {rho, u, p} | dict | 右侧状态：$\rho_R=0.125, u_R=0.0, p_R=0.1$ |
| gamma | float | 比热比，默认1.4 |

#### 输出
- `U`: 守恒变量数组，形状为`(n_points, 3)`，分量依次为$[\rho, \rho u, \rho E]$
- 其中$\rho E = p/(\gamma-1) + 0.5\rho u^2$

#### 前置条件
- 网格坐标数组已正确生成（F-01完成）
- 左右状态压力均为正值

#### 后置条件
- 守恒变量中密度和压力均为正值（$\rho > 0, p > 0$）
- $x < x_{\text{diaphragm}}$区域为左状态，$x \ge x_{\text{diaphragm}}$区域为右状态
- 网格节点$x_i = x_{\text{diaphragm}}$处赋值为右状态（依据Sod原始论文的惯例[1]）

#### 文献依据
Sod(1978)[1]定义的标准初始条件：$(\rho_L, u_L, p_L) = (1.0, 0.0, 1.0), (\rho_R, u_R, p_R) = (0.125, 0.0, 0.1)$。守恒变量变换依据Toro(2009)[2]第3章及Laney(1998)[3]。

---

### 3.4 F-03: 9种FDM格式求解

#### 描述
实现9种经典有限差分格式的时间推进求解，每种格式采用统一的调用接口，完成从$t=0$到$t=t_{\text{final}}$的时间积分。9种格式按类别分组如下：

**中心差分格式（3种）**：
1. FDM-1: Lax-Friedrichs 格式（一阶）[1][4]
2. FDM-2: Lax-Wendroff 格式（二阶）[1][4]
3. FDM-3: MacCormack 预估校正格式（二阶）[1][3]

**迎风/通量分裂格式（2种）**：
4. FDM-4: 一阶迎风格式（Steger-Warming通量分裂）[3][4]
5. FDM-5: Rusanov 格式（局部Lax-Friedrichs）[2]

**Riemann求解器格式（3种）**：
6. FDM-6: Godunov 格式（精确Riemann求解器）[2]
7. FDM-7: Roe 格式（近似Riemann求解器）[2]
8. FDM-8: HLLC 格式（恢复接触间断）[2]

**高阶TVD格式（1种）**：
9. FDM-9: TVD-Minmod 格式（Roe通量 + Minmod限制器）[5]

#### 输入
| 参数名 | 类型 | 说明 |
|--------|------|------|
| scheme_name | str | 格式名称，来自`FD_SCHEMES`注册表 |
| U | ndarray | 初始守恒变量，形状`(n_points, 3)` |
| x | ndarray | 网格坐标数组 |
| dx | float | 网格间距 |
| t_final | float | 仿真终止时间，默认0.2 |
| cfl | float | CFL数，默认0.8 |
| gamma | float | 比热比，默认1.4 |

#### 输出
- `U_final`: 最终时刻的守恒变量数组
- `t`: 实际到达的最终时间（应等于`t_final`）
- `n_steps`: 完成的时间推进步数

#### 前置条件
- 流场已正确初始化（F-02完成）
- 指定格式名称在`FD_SCHEMES`注册表中存在
- CFL数在(0, 1]范围内

#### 后置条件
- 守恒变量中密度和压力均为正值（$\rho > 0, p > 0$）
- 每个时间步的CFL条件满足：$\max(|u|+c) \cdot \Delta t / \Delta x \le \text{CFL}$
- 边界条件在每个时间步后正确施加（透射/固定边界条件）
- MacCormack格式：交替方向计数器在每次求解开始时重置为0

#### 文献依据
各格式的离散公式与理论依据详见项目技术文档`CFD_Sod_ShockTube_Project_Plan.md`第5章，核心文献包括Sod(1978)[1]、Toro(2009)[2]、Laney(1998)[3]、LeVeque(1992)[4]与Harten(1983)[5]。

---

### 3.5 F-04: 精确解计算

#### 描述
基于Riemann问题的精确解法[2]，计算Sod激波管问题在指定时刻$t$的解析精确解，输出密度$\rho(x,t)$、速度$u(x,t)$和压力$p(x,t)$的空间分布。

#### 输入
| 参数名 | 类型 | 说明 |
|--------|------|------|
| x | ndarray | 网格坐标数组 |
| t | float | 目标时刻，通常为0.2 |
| gamma | float | 比热比，默认1.4 |

#### 输出
- `rho_exact`: 精确密度数组，形状`(len(x),)`
- `u_exact`: 精确速度数组，形状`(len(x),)`
- `p_exact`: 精确压力数组，形状`(len(x),)`

#### 前置条件
- $t > 0$（零时刻即初始条件，无需求解）
- 使用标准Sod初始条件（硬编码，不可通过参数修改）

#### 后置条件
- 精确解包含4个流动区域（从左到右：左未扰动区、稀疏波区、星区、右未扰动区）及5个波系特征（左稀疏波头、左稀疏波尾、接触间断、激波、右未扰动区边界）
- 各区域密度、速度、压力满足Riemann不变量与Rankine-Hugoniot关系
- 精确解在$x=0.5$附近存在间断过渡（对激波管问题而言是物理真实的）

#### 文献依据
精确解算法完全依据Toro(2009)[2]第4章"The Riemann Problem for the Euler Equations"中描述的标准迭代法：使用Brent方法求解压力方程$f(p_*)=0$，然后反推速度$u_*$、密度$\rho_*$及各波系位置。

---

### 3.6 F-05: 误差分析

#### 描述
对每一种数值格式的计算结果，在密度、速度、压力三个物理量上分别计算L1、L2、L∞三种误差范数，并以结构化表格输出。

#### 输入
| 参数名 | 类型 | 说明 |
|--------|------|------|
| U_num | ndarray | 数值解守恒变量，形状`(n_points, 3)` |
| rho_exact | ndarray | 精确密度（来自F-04） |
| u_exact | ndarray | 精确速度（来自F-04） |
| p_exact | ndarray | 精确压力（来自F-04） |

#### 输出
- `errors`: 字典结构，包含9个误差值（3个物理量 x 3种范数）

误差定义：
- $L_1 = \frac{1}{\Omega}\int_\Omega |q_{\text{num}} - q_{\text{exact}}| dx \approx \sum_i |q_{\text{num},i} - q_{\text{exact},i}| \cdot \Delta x$
- $L_2 = \sqrt{\frac{1}{\Omega}\int_\Omega (q_{\text{num}} - q_{\text{exact}})^2 dx} \approx \sqrt{\sum_i (q_{\text{num},i} - q_{\text{exact},i})^2 \cdot \Delta x}$
- $L_\infty = \max_i |q_{\text{num},i} - q_{\text{exact},i}|$

#### 前置条件
- 数值解与精确解定义在相同网格坐标上
- 数值解已完成时间推进（F-03完成）
- 精确解已正确计算（F-04完成）

#### 后置条件
- 所有误差值为非负数
- L∞误差不小于L1误差和L2误差

#### 文献依据
误差范数定义依据ASME V&V 20-2009标准[7]及Oberkampf与Trucano(2002)[8]关于CFD验证的误差度量方法论。Laney(1998)[3]第7章讨论了数值格式的精度与误差分析。

---

### 3.7 F-06: 可视化

#### 描述
为每一种数值格式生成4幅子图的对比图表，包含密度$\rho$、速度$u$、压力$p$和总能量$E$的空间分布，并同时绘制精确解（实线）与数值解（圆圈标记）。

#### 输入
| 参数名 | 类型 | 说明 |
|--------|------|------|
| x | ndarray | 网格坐标 |
| U_num | ndarray | 数值解 |
| rho_exact | ndarray | 精确密度 |
| u_exact | ndarray | 精确速度 |
| p_exact | ndarray | 精确压力 |
| scheme_name | str | 格式名称（用于标题标注） |
| n_points | int | 网格点数（用于标题标注） |
| t_final | float | 终止时间（用于标题标注） |
| cfl | float | CFL数（用于标题标注） |

#### 输出
- PNG格式对比图文件，命名规则：`plot_<scheme_name>.png`
- 文件保存于`results/figures/`目录
- 额外生成一张汇总对比图`plot_all_schemes.png`，将9种格式的密度场绘制在同一图中

#### 前置条件
- 数值解与精确解已计算完成（F-03、F-04完成）
- 输出目录存在或可自动创建
- Matplotlib后端可用（使用非交互式'Agg'后端）

#### 后置条件
- 每张图片包含4个子图（$\rho, u, p, E$）
- 每张图片标题包含格式名称、网格点数、$t=0.2$、CFL数
- 精确解以实线绘制，数值解以圆圈标记绘制
- 文件可被标准图片查看器正常打开

#### 文献依据
CFD结果可视化的学术规范参见Laney(1998)[3]及Sod(1978)[1]（其原始论文即以类似的对比图展示结果）。

---

### 3.8 F-07: 配置管理

#### 描述
支持通过YAML格式的文本配置文件管理仿真参数，包括网格参数、物理参数、数值格式选择与输出配置。同时支持CLI命令行参数覆盖YAML中的对应设置。

#### 输入
- YAML配置文件路径（默认：`config/simulation_config.yaml`）
- CLI命令行可选参数（优先级高于YAML配置）

#### 输出
- 合并后的运行时参数集（Python字典或命名空间对象）

#### YAML配置结构
```yaml
mesh:          # 网格参数
  n_points: 100
  x_left: 0.0
  x_right: 1.0
physics:       # 物理参数
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state: {rho: 1.0, u: 0.0, p: 1.0}
  right_state: {rho: 0.125, u: 0.0, p: 0.1}
simulation:    # 仿真控制参数
  t_final: 0.2
  cfl: 0.8
schemes:       # 数值格式列表
  - lax_friedrichs
  - lax_wendroff
  - macormack
  - upwind
  - rusanov
  - godunov
  - roe
  - hllc
  - tvd_minmod
output:        # 输出配置
  data_dir: results/data
  exact_dir: results/exact
  figures_dir: results/figures
  error_report: results/error_report.csv
```

#### 前置条件
- PyYAML库已安装
- 配置文件路径有效（文件存在且格式合法）
- 配置文件中的数值在合法范围内

#### 后置条件
- CLI参数覆盖YAML中对应的默认值（CLI优先级规则）
- 参数合并后的值通过合法性校验

---

### 3.9 F-08: 版本管理

#### 描述
提供软件的语义化版本号（Semantic Versioning 2.0.0）管理，支持版本号查询与更新。

#### 输入
- `VERSION`文件（存储当前版本号）
- 版本号更新命令（major/minor/patch）

#### 输出
- 更新后的`VERSION`文件
- 对应的`CHANGELOG.md`更新条目

#### 前置条件
- 版本号符合`MAJOR.MINOR.PATCH`格式
- `VERSION`文件存在于项目根目录

#### 后置条件
- `VERSION`中的版本号格式正确
- 版本号按照语义化版本规范递增

---

## 4. 非功能需求

### 4.1 性能需求

| 性能指标 | 目标值 | 测量条件 | 文献依据 |
|---------|--------|---------|---------|
| 单格式求解耗时 | < 5秒 | N=100网格, $t=0.2$, CFL=0.8 | [3][4]指出N=100的1D Euler求解应在秒级完成 |
| 精确解计算耗时 | < 0.5秒 | N=100网格 | Brent迭代在20次内收敛[2] |
| 9种格式全量求解耗时 | < 45秒 | N=100网格, 串行执行 | 9 x 5 = 45秒上限 |
| 内存占用峰值 | < 200 MB | N=100网格 | 每格式仅需存储`(N,3)`数组 |

性能测试环境：Python 3.10, Intel Core i5或同等性能CPU, 8 GB RAM。

### 4.2 精度需求

| 精度指标 | 目标值 | 适用条件 | 验证方法 |
|---------|--------|---------|---------|
| 密度L1误差上限 | < $1 \times 10^{-2}$ | N=100, 全部9种格式 | 与Riemann精确解对比[2] |
| 质量守恒误差 | < $1 \times 10^{-6}$ | 全部9种格式 | 初始总质量与最终总质量之差[3] |
| Roe格式: 跨音速熵修正 | 无膨胀激波 | 跨音速稀疏波区域 | 对比熵修复前后结果[2] |

精度要求依据Sod(1978)[1]的同类实验结果：在N=100分辨率下，一阶格式（如Lax-Friedrichs）的L1误差典型值为$10^{-3}\sim10^{-2}$量级。

### 4.3 可靠性需求

| 需求编号 | 需求描述 |
|---------|---------|
| R-01 | 所有格式在标准Sod初始条件下不得因负密度/负压力而导致求解崩溃 |
| R-02 | CFL数违反条件时应给出明确警告，不静默执行 |
| R-03 | 无效的格式名称参数应输出可用格式列表并终止 |
| R-04 | 配置文件解析失败时应输出具体错误行号和错误原因 |
| R-05 | 所有数值格式的实现必须通过对应的单元测试（覆盖率 >= 80%） |

### 4.4 可维护性需求

| 需求编号 | 需求描述 |
|---------|---------|
| M-01 | 代码遵循PEP 8规范，函数和方法包含docstring |
| M-02 | 每种数值格式封装在独立函数中，通过`FD_SCHEMES`注册表统一管理 |
| M-03 | 新增格式仅需实现`xxx_step(U, dx, dt, gamma)`函数并注册即可 |
| M-04 | 项目目录结构清晰：`src/`（核心模块）、`tests/`（测试）、`config/`（配置）、`docs/`（文档）、`results/`（输出） |

### 4.5 可移植性需求

| 需求编号 | 需求描述 |
|---------|---------|
| P-01 | 代码在Windows/macOS/Linux三平台均可运行 |
| P-02 | 仅依赖NumPy、SciPy、Matplotlib、PyYAML四个纯Python开源库 |
| P-03 | 不依赖MATLAB、Fluent、ANSYS等商业软件 |
| P-04 | 不依赖任何平台特定的系统调用 |
| P-05 | 文件路径使用`os.path.join`或`pathlib.Path`，避免硬编码分隔符 |

---

## 5. 接口需求

### 5.1 CLI命令行接口

#### 程序入口
```bash
python main.py [OPTIONS]
```

#### 参数列表

| 参数 | 类型 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| `--scheme` | str | `all` | `all`, `lax_friedrichs`, `lax_wendroff`, `macormack`, `upwind`, `rusanov`, `godunov`, `roe`, `hllc`, `tvd_minmod` | 选择求解格式 |
| `--n_points` | int | 100 | 50-10000 | 网格节点数 |
| `--cfl` | float | 0.8 | 0.1-1.0 | CFL数 |
| `--t_final` | float | 0.2 | > 0 | 仿真终止时间 |
| `--gamma` | float | 1.4 | > 1.0 | 比热比 |
| `--output_dir` | str | `results` | 有效路径 | 输出根目录 |

#### 使用示例
```bash
# 运行所有9种格式, 使用默认参数
python main.py

# 仅运行Roe格式, N=200网格
python main.py --scheme roe --n_points 200

# 运行所有格式, 增大CFL数
python main.py --cfl 0.95

# 网格收敛性分析 (需多次运行, 通过脚本调用)
python main.py --n_points 100
python main.py --n_points 200
python main.py --n_points 400
```

#### 退出码
| 退出码 | 含义 |
|--------|------|
| 0 | 正常完成 |
| 1 | 参数错误 |
| 2 | 运行时错误（如负密度崩溃） |

### 5.2 YAML配置接口

YAML配置文件位于`config/simulation_config.yaml`，完整结构见第3.8节F-07中的YAML配置结构。

配置文件的优先级规则如下：
1. YAML文件中的值作为**默认值**
2. CLI参数（如`--n_points 200`）**覆盖**YAML中的对应默认值
3. 如果YAML中某字段缺失，使用程序内置的硬编码默认值

### 5.3 Python API接口（程序内部模块接口）

本软件的Python模块划分如下：

| 模块 | 文件 | 主要导出 |
|------|------|---------|
| 网格生成 | `src/mesh_generator.py` | `generate_mesh(n_points, x_left, x_right)` |
| 流场初始化 | `src/flow_initializer.py` | `initialize_flow(x, diaphragm_pos, left_state, right_state, gamma)` |
| 有限差分格式 | `src/fd_schemes.py` | `FD_SCHEMES`字典, `solve_with_scheme(scheme_name, U, x, dx, ...)` |
| 时间推进器 | `src/time_marcher.py` | `compute_dt(U, dx, cfl, gamma)`, `check_conservation(...)` |
| 边界处理 | `src/boundary_handler.py` | `apply_boundary_condition(U)` |
| 精确解计算 | `src/exact_solver.py` | `sod_exact_solution(x, t, gamma)` |
| 误差分析 | `src/validator.py` | `compute_errors(U_num, rho_exact, u_exact, p_exact)` |
| 输出写入 | `src/output_writer.py` | `save_results(...)`, `save_exact_solution(...)` |

模块间通过标准的Python函数调用进行数据传递，不通过网络或进程间通信。

---

## 6. 数据需求

### 6.1 输入数据格式

#### 6.1.1 YAML配置文件

- **格式**：YAML 1.2
- **编码**：UTF-8
- **位置**：`config/simulation_config.yaml`
- **校验规则**：
  - `mesh.n_points`：整数，范围[50, 10000]
  - `physics.gamma`：浮点数，范围(1.0, 2.0]
  - `simulation.cfl`：浮点数，范围(0, 1.0]
  - `simulation.t_final`：浮点数，>0
  - `schemes`：字符串列表，每个字符串必须在`FD_SCHEMES.keys()`中

#### 6.1.2 命令行参数

- **格式**：GNU风格长选项（`--option value`）
- **编码**：终端默认编码（UTF-8）
- **校验规则**：同YAML对应字段

### 6.2 输出数据格式

#### 6.2.1 数值解数据文件

- **格式**：NumPy `.npy`二进制格式
- **命名规则**：`<timestamp>_data_<scheme_name>.npy`
- **示例**：`20260516_120000_data_roe.npy`
- **内容**：最终时刻守恒变量数组，形状`(n_points, 3)`，dtype=float64

#### 6.2.2 精确解数据文件

- **格式**：NumPy `.npy`二进制格式
- **命名规则**：`<timestamp>_data_exact.npy`
- **内容**：字典`{rho, u, p}`，每项形状`(n_points,)`，dtype=float64

#### 6.2.3 误差报告文件

- **格式**：CSV逗号分隔值
- **命名**：`error_report.csv`
- **编码**：UTF-8 with BOM（兼容Excel）
- **列结构**：

| scheme | mesh_N | rho_L1 | rho_L2 | rho_Linf | u_L1 | u_L2 | u_Linf | p_L1 | p_L2 | p_Linf |
|--------|--------|--------|--------|----------|-----|-----|--------|-----|-----|--------|

#### 6.2.4 对比图文件

- **格式**：PNG（Portable Network Graphics）
- **命名规则**：`plot_<scheme_name>.png` 和 `plot_all_schemes.png`
- **分辨率**：至少1200 x 900像素，DPI=150
- **布局**：2x2子图（密度、速度、压力、总能）

### 6.3 文件命名规则汇总

| 文件类型 | 命名模式 | 输出目录 |
|---------|---------|---------|
| 数值解数据 | `<timestamp>_data_<scheme>.npy` | `results/data/` |
| 精确解数据 | `<timestamp>_data_exact.npy` | `results/exact/` |
| 误差报告 | `error_report.csv` | `results/` |
| 单格式对比图 | `plot_<scheme>.png` | `results/figures/` / `docs/` |
| 全格式汇总图 | `plot_all_schemes.png` | `results/figures/` / `docs/` |

时间戳格式：`YYYYMMDD_HHMMSS`（例如`20260516_120000`）。

---

## 7. 验收标准

### 7.1 功能验收清单

| 验收项 | 验收条件 | 验证方法 |
|--------|---------|---------|
| AC-01 | 网格生成正确：N=100时共101个节点（包含两端边界），间距一致 | 单元测试 |
| AC-02 | 流场初始化正确：密度在$x<0.5$处=1.0，$x\ge0.5$处=0.125 | 单元测试 |
| AC-03 | 9种格式均可在N=100网格上完成$t=0.2$求解，无崩溃 | 集成测试 |
| AC-04 | 精确解在$t=0.2$时包含明确的稀疏波-接触间断-激波结构 | 与Toro(2009)结果对比[2] |
| AC-05 | L1/L2/L∞误差均为非负数，且L∞>=L1 | 单元测试 |
| AC-06 | 对比图包含4幅子图，精确解(实线)与数值解(标记)清晰可辨 | 人工审查 |
| AC-07 | YAML配置正确解析，CLI参数可覆盖YAML默认值 | 手动测试 |
| AC-08 | 所有格式的误差报告正确写入CSV文件 | 集成测试 |

### 7.2 性能验收

| 验收项 | 验收条件 |
|--------|---------|
| AC-P01 | 单格式求解总耗时（含精确解+误差分析）< 5秒（N=100） |
| AC-P02 | 9种格式全量求解总耗时 < 60秒（N=100, 串行） |

### 7.3 精度验收

| 验收项 | 验收条件 | 测量量 |
|--------|---------|--------|
| AC-A01 | 所有格式在N=100时密度L1误差 < $1 \times 10^{-2}$ | `compute_errors`输出 |
| AC-A02 | 质量守恒误差 < $1 \times 10^{-6}$ | `check_conservation`输出 |
| AC-A03 | 网格加倍后（N=200），二阶格式的L1误差应减小约75%（即二阶收敛） | 网格收敛性分析 |

### 7.4 文献合规验收

| 验收项 | 验收条件 |
|--------|---------|
| AC-L01 | 每个格式函数的docstring中标注了明确的文献出处 |
| AC-L02 | 问题设置（初始条件、边界条件）与Sod(1978)[1]一致 |
| AC-L03 | 精确解算法与Toro(2009)[2]第4章一致 |
| AC-L04 | 项目报告中参考文献不少于10篇，格式符合GB/T 7714-2015 |

---

## 8. 参考文献

[1] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31. DOI: 10.1016/0021-9991(78)90023-2.

[2] TORO E F. Riemann solvers and numerical methods for fluid dynamics: a practical introduction[M]. 3rd ed. Berlin: Springer, 2009. DOI: 10.1007/b79761.

[3] LANEY C B. Computational gasdynamics[M]. Cambridge: Cambridge University Press, 1998. DOI: 10.1017/CBO9780511605604.

[4] LEVEQUE R J. Numerical methods for conservation laws[M]. 2nd ed. Basel: Birkhauser, 1992. DOI: 10.1007/978-3-0348-8629-1.

[5] HARTEN A. High resolution schemes for hyperbolic conservation laws[J]. Journal of Computational Physics, 1983, 49(3): 357-393. DOI: 10.1016/0021-9991(83)90136-5.

[6] OneFlow-CFD Documentation. Sod shock tube example[EB/OL]. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html. 访问日期: 2026-05-16.

[7] ASME. Standard for verification and validation in computational fluid dynamics and heat transfer: ASME V&V 20-2009[S]. New York: American Society of Mechanical Engineers, 2009.

[8] OBERKAMPF W L, TRUCANO T G. Verification and validation in computational fluid dynamics[J]. Progress in Aerospace Sciences, 2002, 38(3): 209-272. DOI: 10.1016/S0376-0421(02)00005-2.

---

**文档控制信息**：
- 编制：CFD课程项目组 | 2026-05-16
- 审核：--（待审核）
- 批准：--（待批准）
- 下次评审日期：2026-06-01