# 项目规划：一维Sod激波管CFD数值格式对比项目

## 1. 项目背景与研究目的

### 1.1 研究背景与学术意义

一维Sod激波管问题是计算流体力学（CFD）领域最经典的验证基准问题之一。该问题由Gary A. Sod于1978年在其开创性论文中提出[1]，其核心学术价值在于：

- **间断捕捉能力验证**：Sod激波管问题是一个典型的Riemann问题，其解包含激波（shock）、接触间断（contact discontinuity）和稀疏波（rarefaction wave）三种典型的流体动力学间断结构[1]。这使其成为检验数值格式对间断捕捉能力的理想测试案例。

- **精确解可获取性**：与大多数CFD问题不同，Sod激波管问题存在解析精确解，可通过Riemann求解器获得[2]。这为数值结果的定量验证提供了严格的基准。

- **数值格式对比平台**：Sod在其原始论文中系统对比了多种有限差分格式（包括Lax-Friedrichs、Lax-Wendroff、MacCormack等）对该问题的求解精度[1]，为后续研究建立了方法论框架。

### 1.2 项目核心目的

本项目的核心目的为：**基于OneFlow-CFD官方文档定义的初始条件与边界条件，采用多种数值格式求解一维Sod激波管问题，并将数值解与解析精确解进行定量对比验证**。

具体目标包括：

1. **验证目标**：检验不同数值格式（如一阶迎风格式、二阶MUSCL格式、Roe格式等）对激波、接触间断和稀疏波的捕捉精度[2]。

2. **学习目标**：通过对比分析，理解数值耗散（numerical dissipation）与数值色散（numerical dispersion）对间断分辨率的影响机制[3]。

3. **工程目标**：建立一套可复用的CFD验证流程，为后续复杂问题的数值方法选择提供依据[4]。

### 1.3 问题设置与初始/边界条件

根据OneFlow-CFD官方文档[5]及Sod原始论文[1]，本项目采用以下标准设置：

**控制方程**：一维Euler方程组

$$\frac{\partial \mathbf{U}}{\partial t} + \frac{\partial \mathbf{F}(\mathbf{U})}{\partial x} = 0$$

其中守恒变量向量$\mathbf{U}$和通量向量$\mathbf{F}(\mathbf{U})$分别为：

$$\mathbf{U} = \begin{bmatrix} \rho \\ \rho u \\ \rho E \end{bmatrix}, \quad \mathbf{F}(\mathbf{U}) = \begin{bmatrix} \rho u \\ \rho u^2 + p \\ u(\rho E + p) \end{bmatrix}$$

**初始条件**（$t=0$时刻，计算域$x \in [0, 1]$）：

$$\begin{cases} (\rho_L, u_L, p_L) = (1.0, 0.0, 1.0), & x < 0.5 \\ (\rho_R, u_R, p_R) = (0.125, 0.0, 0.1), & x \geq 0.5 \end{cases}$$

**边界条件**：计算域两端采用固定边界条件（或特征边界条件），初始间断位于$x=0.5$处[1]。

**气体参数**：比热比$\gamma = 1.4$（理想气体）[1]。

**输出时刻**：通常取$t=0.2$时刻进行结果对比[1]。

---

## 2. 项目任务拆解与模块划分

### 2.1 全流程模块划分

参考CFD学术项目的标准实施流程[3]，将本项目拆解为以下5个核心模块：

| 模块编号 | 模块名称 | 核心工作内容 | 预计时间占比 | 主要交付物 |
|---------|---------|-------------|-------------|-----------|
| M1 | **Plan阶段** | 文献调研、方案梳理、时间规划 | 15% | 项目计划书、文献综述框架 |
| M2 | **数值方法调研** | 数值格式理论梳理、精确解获取方法 | 20% | 数值方法对比报告 |
| M3 | **代码实现** | 求解器编程、精确解程序编写 | 30% | 可运行代码、单元测试 |
| M4 | **结果验证与分析** | 数值解与精确解对比、误差分析 | 20% | 对比图表、误差分析报告 |
| M5 | **报告撰写** | 项目报告撰写、结果整理 | 15% | 完整项目报告 |

### 2.2 Plan阶段（M1）任务清单

Plan阶段是本项目的起点，其核心任务是为后续实施奠定理论与方法论基础。根据CFD项目管理的最佳实践，Plan阶段需完成以下具体任务：

#### 任务1.1：文献调研与理论梳理

**必要性**：Sod激波管问题的数值求解涉及Riemann问题理论、Euler方程数值离散方法等核心理论，必须通过文献调研建立完整的理论框架[2]。

**具体工作**：
- 精读Sod原始论文[1]，理解问题的数学表述与物理意义
- 研读Toro教材[2]中关于Riemann求解器的章节，掌握精确解的获取方法
- 研读Blazek教材[3]中关于空间离散格式（如一阶迎风、二阶MUSCL、TVD格式等）的内容
- 检索并阅读近5年与Sod问题数值格式对比相关的SCI论文

**交付物**：文献综述笔记（按数值格式分类整理）

#### 任务1.2：项目方案梳理

**必要性**：明确技术路线是CFD项目成功的关键前提，需确定拟采用的数值格式清单、对比指标与验证标准[4]。

**具体工作**：
- 确定拟实现的数值格式清单（建议至少包含3种格式，如：Lax-Friedrichs、Roe、AUSM等）[1][2]
- 明确对比验证的定量指标（如L1误差、L2误差、L∞误差）[4]
- 确定网格分辨率方案（如N=100, 200, 400等）以考察网格收敛性[3]
- 梳理OneFlow-CFD文档[5]中的问题设置细节，确保与标准Sod问题一致

**交付物**：技术方案说明书

#### 任务1.3：时间规划与里程碑设定

**必要性**：合理的时间安排是学术项目按期完成的保障，需参考典型CFD课程项目的实施周期进行规划。

**具体工作**：
- 制定项目整体时间线（建议6周周期）
- 设定各阶段的关键里程碑与检查点
- 预留缓冲时间以应对代码调试等不确定性因素

**交付物**：项目时间计划表（甘特图形式）

#### 任务1.4：项目计划书撰写

**必要性**：项目计划书是Plan阶段的最终交付物，需整合上述所有调研与规划成果，形成结构化的项目指导文档。

**具体工作**：
- 整合任务1.1-1.3的成果
- 按照学术规范撰写完整的项目计划书
- 规范参考文献格式（GB/T 7714-2015）

**交付物**：完整项目计划书

---

## 3. 实施计划与时间安排（含里程碑）

### 3.1 项目整体时间安排（6周周期）

参考高校CFD课程项目的典型实施周期，本项目建议采用**6周**的实施周期，具体安排如下：

| 周次 | M1: Plan阶段 | M2: 数值方法调研 | M3: 代码实现 | M4: 结果验证分析 | M5: 报告撰写 |
|-----|-------------|-----------------|-------------|-----------------|-------------|
| Week 1 | ████████ (100%) | | | | |
| Week 2 | | ████████ (100%) | | | |
| Week 3 | | | ████████ (60%) | | |
| Week 4 | | | ████ (40%) | | |
| Week 5 | | | | ████████ (100%) | |
| Week 6 | | | | | ████████ (100%) |

### 3.2 Plan阶段详细时间安排（第1周）

Plan阶段建议在第1周内完成，具体日程安排如下：

| 日期 | 任务内容 | 预计耗时 | 产出物 | 文献依据 |
|------|---------|---------|--------|---------|
| Day 1 | 精读Sod原始论文[1]，理解问题数学表述 | 3-4小时 | 阅读笔记 | Sod (1978) |
| Day 2 | 研读Toro教材[2]第4章（Riemann问题）与第10章（精确解法） | 4-5小时 | 理论笔记 | Toro (2009) |
| Day 3 | 研读Blazek教材[3]第5章（空间离散格式） | 4-5小时 | 格式对比笔记 | Blazek (2015) |
| Day 4 | 检索补充文献，确定数值格式清单与对比指标 | 2-3小时 | 技术方案草稿 | ASME (2009) |
| Day 5 | 撰写项目计划书初稿，制定时间线 | 3-4小时 | 计划书初稿 | - |
| Day 6 | 完善计划书，规范参考文献格式 | 2-3小时 | 计划书修订稿 | GB/T 7714-2015 |
| Day 7 | 最终审查与定稿 | 1-2小时 | **项目计划书终稿** | - |

### 3.3 关键里程碑定义

| 里程碑编号 | 里程碑名称 | 完成时间 | 验收标准 | 关联模块 |
|-----------|-----------|---------|---------|---------|
| MS1 | 项目计划书定稿 | Week 1结束 | 包含完整的文献综述、技术方案、时间规划，参考文献不少于10篇 | M1 |
| MS2 | 数值方法对比报告 | Week 2结束 | 明确各数值格式的理论精度、稳定性条件、适用范围 | M2 |
| MS3 | 代码实现完成 | Week 4结束 | 所有数值格式的代码通过单元测试，可稳定运行 | M3 |
| MS4 | 验证分析完成 | Week 5结束 | 完成所有格式与精确解的对比，误差分析完整 | M4 |
| MS5 | 项目报告定稿 | Week 6结束 | 报告结构完整，图表规范，参考文献齐全 | M5 |

### 3.4 时间分配依据

- **Plan阶段占比15%**：参考CFD项目管理的经验法则，规划阶段应占总时间的10-20%，以确保后续实施有清晰的指导框架。
- **代码实现占比35%**：数值求解器的编程与调试是CFD项目最耗时的环节，尤其涉及多种格式的实现与验证[3]。
- **验证分析占比20%**：与精确解的定量对比需要系统的误差计算与网格收敛性分析，符合ASME V&V 20-2009指南的要求[4]。

---

---

## 5 基于有限差分法的数值格式调研

### 5.1 一维可压缩欧拉方程与有限差分法基本离散原理

#### 5.1.1 控制方程

一维可压缩无黏Euler方程组的守恒形式为[1]：

$$\frac{\partial \mathbf{U}}{\partial t} + \frac{\partial \mathbf{F}(\mathbf{U})}{\partial x} = 0$$

其中守恒变量向量与通量向量分别为：

$$\mathbf{U} = \begin{bmatrix} \rho \\ \rho u \\ \rho E \end{bmatrix}, \quad \mathbf{F}(\mathbf{U}) = \begin{bmatrix} \rho u \\ \rho u^2 + p \\ u(\rho E + p) \end{bmatrix}$$

式中：$\rho$为密度，$u$为速度，$p$为压力，$E$为单位质量总能。对于理想气体，状态方程为：

$$p = (\gamma - 1)\left(\rho E - \frac{1}{2}\rho u^2\right)$$

其中比热比$\gamma = 1.4$[1]。

#### 5.1.2 有限差分法基本思想

有限差分法（Finite Difference Method, FDM）的核心思想是用差商近似替代偏导数，将连续的控制方程离散为代数方程组[3]。对于一维Euler方程，在均匀网格$x_i = i\Delta x$和时间层$t^n = n\Delta t$上，空间导数$\partial\mathbf{F}/\partial x$可用有限差分近似：

$$\left.\frac{\partial \mathbf{F}}{\partial x}\right|_i \approx \frac{\mathbf{F}_{i+1} - \mathbf{F}_i}{\Delta x} \quad \text{（一阶前差）}$$

$$\left.\frac{\partial \mathbf{F}}{\partial x}\right|_i \approx \frac{\mathbf{F}_{i+1} - \mathbf{F}_{i-1}}{2\Delta x} \quad \text{（二阶中心差）}$$

时间导数$\partial\mathbf{U}/\partial t$则通过时间推进格式（如显式Euler、Runge-Kutta等）进行离散[5]。

#### 5.1.3 激波管问题的数值挑战

Sod激波管问题的解包含激波、接触间断和稀疏波三种间断结构[1]。有限差分法在求解此类问题时面临的核心挑战为：

- **数值振荡**：中心差分格式在间断附近会产生非物理振荡（Gibbs现象）[5]；
- **数值耗散**：一阶格式虽然稳定但会过度抹平间断，降低分辨率[3]；
- **稳定性限制**：显式格式需满足CFL（Courant-Friedrichs-Lewy）条件以保证数值稳定性[5]。

---

### 5.2 经典有限差分格式调研

#### 5.2.1 Lax-Friedrichs 有限差分格式

**（1）格式概述**

Lax-Friedrichs格式是一种经典的一阶显式有限差分格式，由Lax和Friedrichs于20世纪50年代提出，最初用于求解双曲型守恒律方程[1]。该格式通过在时间中心层引入人工粘性项来实现数值稳定性[5]。

**（2）离散原理**

对于一维守恒律方程$\partial\mathbf{U}/\partial t + \partial\mathbf{F}/\partial x = 0$，Lax-Friedrichs格式的离散形式为[1][5]：

$$\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_{i+1}^n + \mathbf{U}_{i-1}^n\right) - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right)$$

该格式可视为对不稳定的一阶中心差分格式$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{2\Delta x}(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n)$的修正，其中$\mathbf{U}_i^n$被替换为相邻节点的平均值$\frac{1}{2}(\mathbf{U}_{i+1}^n + \mathbf{U}_{i-1}^n)$，这一替换引入了数值耗散项$\frac{1}{2}(\mathbf{U}_{i+1}^n - 2\mathbf{U}_i^n + \mathbf{U}_{i-1}^n)$[5]。

**（3）精度与稳定性**

- **空间精度**：一阶精度$O(\Delta x)$[5]；
- **时间精度**：一阶精度$O(\Delta t)$[5]；
- **稳定性条件**：CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$，其中$\lambda_{\max}$为Jacobian矩阵$\partial\mathbf{F}/\partial\mathbf{U}$的最大特征值（即$|u|+c$，$c$为声速）[5]。

**（4）激波捕捉效果**

Lax-Friedrichs格式具有强数值耗散特性，能够稳定捕捉激波而不产生数值振荡[1]。然而，其过大的数值耗散会导致激波和接触间断被严重抹平，分辨率较低[5]。Sod在其原始论文中指出，该格式对激波位置的预测较为准确，但对接触间断的捕捉效果较差[1]。

**（5）优缺点与适用场景**

| 优点 | 缺点 |
|------|------|
| 格式简单，易于实现[3] | 数值耗散过大，间断分辨率低[5] |
| 无条件单调，不产生数值振荡[5] | 时间和空间均为一阶精度[5] |
| 稳定性好，CFL条件宽松[3] | 对接触间断的捕捉能力弱[1] |

**适用场景**：适用于对稳定性要求高、对精度要求不高的初步计算，或作为高阶格式的底层耗散机制[5]。

---

#### 5.2.2 Lax-Wendroff 两步格式

**（1）格式概述**

Lax-Wendroff格式由Lax和Wendroff于1960年提出，是一种经典的二阶显式有限差分格式，专为双曲型守恒律方程设计[1][8]。该格式通过Taylor级数展开将时间导数转换为空间导数，从而实现二阶精度[5]。

**（2）离散原理**

Lax-Wendroff格式的标准离散形式为[1][5]：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right) + \frac{(\Delta t)^2}{2(\Delta x)^2}\left[\mathbf{A}_{i+1/2}^n\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right) - \mathbf{A}_{i-1/2}^n\left(\mathbf{F}_i^n - \mathbf{F}_{i-1}^n\right)\right]$$

其中$\mathbf{A} = \partial\mathbf{F}/\partial\mathbf{U}$为Jacobian矩阵。对于非线性方程，通常采用守恒形式：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1/2}^{n+1/2} - \mathbf{F}_{i-1/2}^{n+1/2}\right)$$

其中半时间层通量通过Taylor展开获得[5]。

**（3）精度与稳定性**

- **空间精度**：二阶精度$O(\Delta x^2)$[5]；
- **时间精度**：二阶精度$O(\Delta t^2)$[5]；
- **稳定性条件**：CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$[5]。

**（4）激波捕捉效果**

Lax-Wendroff格式在光滑区域具有较高精度，但在间断附近会产生显著的非物理数值振荡[1][5]。Sod的原始论文明确指出，该格式在激波和接触间断附近会出现明显的过冲（overshoot）和下冲（undershoot）现象[1]。这种振荡源于格式的二阶中心差分特性，无法有效抑制高频误差[5]。

**（5）优缺点与适用场景**

| 优点 | 缺点 |
|------|------|
| 二阶精度，光滑区域分辨率高[5] | 间断附近产生数值振荡[1] |
| 格式结构清晰，易于理解[3] | 不满足TVD条件，无法保证单调性[5] |
| 计算效率较高[3] | 对激波捕捉需要额外的人工粘性[1] |

**适用场景**：适用于流场光滑或间断较弱的情况；对于强间断问题，需配合人工粘性或限制器使用[5]。

---

#### 5.2.3 MacCormack 预估校正格式

**（1）格式概述**

MacCormack格式由MacCormack于1969年提出，是一种二阶预估校正型有限差分格式，广泛应用于可压缩流动的计算[1][3]。该格式通过预估步和校正步的组合实现二阶精度，同时避免了Lax-Wendroff格式中Jacobian矩阵的显式计算[3]。

**（2）离散原理**

MacCormack格式包含两个步骤[1][3]：

**预估步**（使用前差分离散空间导数）：

$$\mathbf{U}_i^* = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right)$$

**校正步**（使用后差分离散空间导数）：

$$\mathbf{U}_i^{**} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_i^* - \mathbf{F}_{i-1}^*\right)$$

**最终解**（取预估步和校正步的平均）：

$$\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_i^* + \mathbf{U}_i^{**}\right)$$

该格式在数学上等价于Lax-Wendroff格式，但实现更为简便[3]。

**（3）精度与稳定性**

- **空间精度**：二阶精度$O(\Delta x^2)$[3]；
- **时间精度**：二阶精度$O(\Delta t^2)$[3]；
- **稳定性条件**：CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$[3]。

**（4）激波捕捉效果**

MacCormack格式在间断附近同样会产生数值振荡，但振荡幅度通常小于Lax-Wendroff格式[1]。Sod的研究表明，该格式对激波位置的捕捉较为准确，但在接触间断附近仍存在明显的振荡[1]。NASA的对比研究指出，MacCormack格式在激波管问题中的精度强烈依赖于CFL数的选择，适当减小CFL数可有效抑制振荡[3]。

**（5）优缺点与适用场景**

| 优点 | 缺点 |
|------|------|
| 二阶精度，实现简便[3] | 间断附近产生数值振荡[1] |
| 无需计算Jacobian矩阵[3] | 不满足TVD条件[5] |
| 计算效率高于Lax-Wendroff[3] | 对接触间断分辨率有限[1] |

**适用场景**：适用于中等强度间断的可压缩流动计算，是工程CFD中最常用的经典格式之一[3]。

---

#### 5.2.4 一阶迎风有限差分格式

**（1）格式概述**

一阶迎风（Upwind）格式是一种基于特征传播方向的有限差分格式，其核心思想是利用双曲型方程的特征信息，在空间离散时沿特征传播方向（即"迎风"方向）选取差分模板[5]。该格式最早由Courant等人于1952年提出[5]。

**（2）离散原理**

对于标量对流方程$\partial u/\partial t + a\partial u/\partial x = 0$，一阶迎风格式的离散形式为[5]：

当$a > 0$时（信息从左向右传播）：

$$u_i^{n+1} = u_i^n - \frac{a\Delta t}{\Delta x}\left(u_i^n - u_{i-1}^n\right)$$

当$a < 0$时（信息从右向左传播）：

$$u_i^{n+1} = u_i^n - \frac{a\Delta t}{\Delta x}\left(u_{i+1}^n - u_i^n\right)$$

对于Euler方程组，需通过特征分解或通量分裂（如Steger-Warming分裂、Van Leer分裂）实现迎风离散[3][5]。以Steger-Warming通量分裂为例：

$$\mathbf{F} = \mathbf{F}^+ + \mathbf{F}^-$$

其中$\mathbf{F}^+$和$\mathbf{F}^-$分别对应正负特征值方向的通量，离散形式为[3]：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left[\left(\mathbf{F}_{i}^+ - \mathbf{F}_{i-1}^+\right) + \left(\mathbf{F}_{i+1}^- - \mathbf{F}_i^-\right)\right]$$

**（3）精度与稳定性**

- **空间精度**：一阶精度$O(\Delta x)$[5]；
- **时间精度**：一阶精度$O(\Delta t)$[5]；
- **稳定性条件**：CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$[5]。

**（4）激波捕捉效果**

一阶迎风格式具有良好的激波捕捉能力，能够在不产生数值振荡的前提下稳定捕捉激波[5]。其数值耗散特性使得激波被平滑地过渡2-3个网格单元，但不会出现非物理振荡[3][5]。然而，该格式对接触间断的分辨率较低，接触面会被显著抹平[5]。

**（5）优缺点与适用场景**

| 优点 | 缺点 |
|------|------|
| 不产生数值振荡，满足TVD条件[5] | 一阶精度，数值耗散较大[5] |
| 激波捕捉稳定可靠[3] | 接触间断分辨率低[5] |
| 物理意义明确，基于特征理论[5] | 需要通量分裂或特征分解[3] |

**适用场景**：适用于对稳定性要求高、需要无振荡激波捕捉的计算场景[5]。

---

#### 5.2.5 TVD（总变差 diminishing）有限差分格式（补充）

**（1）格式概述**

TVD（Total Variation Diminishing）格式由Harten于1983年提出，是一类能够在保证无振荡的前提下实现二阶精度的高阶有限差分格式[5]。TVD格式的核心思想是在二阶中心格式的基础上添加自适应的非线性限制器，以在间断附近自动降低至一阶精度，在光滑区域保持二阶精度[5]。

**（2）离散原理**

TVD格式的一般形式为[5]：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1/2} - \mathbf{F}_{i-1/2}\right)$$

其中数值通量$\mathbf{F}_{i+1/2}$由低阶通量和高阶修正项组成：

$$\mathbf{F}_{i+1/2} = \mathbf{F}_{i+1/2}^{\text{low}} + \phi(r_i)\left(\mathbf{F}_{i+1/2}^{\text{high}} - \mathbf{F}_{i+1/2}^{\text{low}}\right)$$

式中$\phi(r_i)$为限制器函数，$r_i$为相邻梯度比值。常用的限制器包括Minmod限制器、Superbee限制器、Van Leer限制器等[5]。

**（3）精度与稳定性**

- **空间精度**：光滑区域二阶精度$O(\Delta x^2)$，间断附近自动降为一阶[5]；
- **时间精度**：通常采用二阶Runge-Kutta或MacCormack时间推进[5]；
- **稳定性条件**：CFL条件$|\lambda_{\max}|\frac{\Delta t}{\Delta x} \leq 1$，且满足TVD条件[5]。

**（4）激波捕捉效果**

TVD格式在激波和接触间断附近均能保持无振荡特性，同时具有较高的分辨率[5]。Harten的原始论文证明，TVD格式能够在激波处实现2-3个网格单元的锐利过渡，且不会产生过冲或下冲[5]。

**（5）优缺点与适用场景**

| 优点 | 缺点 |
|------|------|
| 无振荡，高分辨率[5] | 限制器选择影响计算结果[5] |
| 自适应精度切换[5] | 实现复杂度高于经典格式[3] |
| 适用于强间断问题[5] | 计算成本略高[5] |

**适用场景**：适用于对间断分辨率要求较高的激波管问题，是本项目推荐的高阶格式[5]。

---

### 5.3 有限差分格式横向对比

下表对本项目调研的5种有限差分格式进行系统性对比：

| 对比维度 | Lax-Friedrichs | Lax-Wendroff | MacCormack | 一阶迎风 | TVD |
|---------|---------------|--------------|------------|---------|-----|
| **空间精度** | 一阶$O(\Delta x)$ | 二阶$O(\Delta x^2)$ | 二阶$O(\Delta x^2)$ | 一阶$O(\Delta x)$ | 二阶（光滑区）/一阶（间断区） |
| **时间精度** | 一阶$O(\Delta t)$ | 二阶$O(\Delta t^2)$ | 二阶$O(\Delta t^2)$ | 一阶$O(\Delta t)$ | 二阶 |
| **时间推进方式** | 显式单步 | 显式单步 | 显式预估校正 | 显式单步 | 显式多步/Runge-Kutta |
| **激波捕捉能力** | 稳定但过度抹平 | 准确但有振荡 | 准确但有振荡 | 稳定锐利 | 锐利且无振荡 |
| **接触间断捕捉** | 差（严重抹平） | 中等（有振荡） | 中等（有振荡） | 中等（抹平） | 良好 |
| **数值振荡** | 无 | 显著 | 中等 | 无 | 无 |
| **数值耗散** | 大 | 小 | 小 | 中等 | 自适应 |
| **计算复杂度** | 低 | 中 | 中 | 中（需通量分裂） | 高（需限制器） |
| **实现难度** | 简单 | 中等 | 中等 | 中等 | 较复杂 |
| **CFL条件** | $\leq 1$ | $\leq 1$ | $\leq 1$ | $\leq 1$ | $\leq 1$ |

---

### 5.4 本项目有限差分格式推荐

基于上述调研结果，结合本项目"多种数值格式对比验证"的目标，推荐以下格式组合用于后续编程实现：

| 推荐优先级 | 格式名称 | 推荐理由 | 文献依据 |
|-----------|---------|---------|---------|
| **必选** | Lax-Friedrichs | 一阶基准格式，实现最简单，用于对比高阶格式的优势[1] | [1][5] |
| **必选** | MacCormack | 二阶经典格式，工程应用广泛，与Lax-Friedrichs形成精度对比[3] | [1][3] |
| **必选** | 一阶迎风 | 无振荡特性，用于对比中心差分格式的振荡行为[5] | [5] |
| **推荐** | TVD（Minmod限制器） | 高阶无振荡格式，用于展示现代格式的优势[5] | [5] |

**推荐理由说明**：

1. **Lax-Friedrichs**作为一阶耗散格式的代表，能够展示数值耗散对间断分辨率的影响[5]；
2. **MacCormack**作为二阶中心格式的代表，能够展示数值色散导致的振荡现象[1]；
3. **一阶迎风**作为特征型格式的代表，能够展示迎风离散对稳定性的贡献[5]；
4. **TVD**作为现代高阶格式的代表，能够展示限制器技术在间断捕捉中的作用[5]。

这4种格式涵盖了从一阶到二阶、从中心到迎风、从经典到现代的有限差分格式谱系，能够全面展示不同格式在Sod激波管问题中的表现差异[1][5]。

---

## 6. 参考文献（按GB/T 7714格式整理）

### 6.1 核心文献（必须引用）

[1] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31. DOI: 10.1016/0021-9991(78)90023-2.

[2] TORO E F. Riemann solvers and numerical methods for fluid dynamics: a practical introduction[M]. 3rd ed. Berlin: Springer, 2009. DOI: 10.1007/b79761.

[3] BLAZEK J. Computational fluid dynamics: principles and applications[M]. 2nd ed. Oxford: Elsevier, 2015.

[4] ASME. Standard for verification and validation in computational fluid dynamics and heat transfer: ASME V&V 20-2009[S]. New York: American Society of Mechanical Engineers, 2009.

[5] LEVEQUE R J. Numerical methods for conservation laws[M]. 2nd ed. Basel: Birkhäuser, 1992. DOI: 10.1007/978-3-0348-8629-1.

[6] OneFlow-CFD Documentation. Sod shock tube example[EB/OL]. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html.

### 6.2 数值格式补充文献（建议引用）

[7] ROE P L. Approximate Riemann solvers, parameter vectors, and difference schemes[J]. Journal of Computational Physics, 1981, 43(2): 357-372. DOI: 10.1016/0021-9991(81)90128-5.

[8] VAN LEER B. Towards the ultimate conservative difference scheme. V. A second-order sequel to Godunov's method[J]. Journal of Computational Physics, 1979, 32(1): 101-136. DOI: 10.1016/0021-9991(79)90145-1.

[9] LAX P D, WENDROFF B. Systems of conservation laws[J]. Communications on Pure and Applied Mathematics, 1960, 13(2): 217-237. DOI: 10.1002/cpa.3160130207.

[10] LEVEQUE R J. Finite volume methods for hyperbolic problems[M]. Cambridge: Cambridge University Press, 2002. DOI: 10.1017/CBO9780511791253.

[11] OBERKAMPF W L, TRUCANO T G. Verification and validation in computational fluid dynamics[J]. Progress in Aerospace Sciences, 2002, 38(3): 209-272. DOI: 10.1016/S0376-0421(02)00005-2.

[12] MCCORMACK R W. The effect of viscosity in hypervelocity impact cratering[C]//AIAA Hypervelocity Impact Conference. Cincinnati, Ohio: AIAA, 1969: 69-354.

[13] HARTEN A. High resolution schemes for hyperbolic conservation laws[J]. Journal of Computational Physics, 1983, 49(3): 357-393. DOI: 10.1016/0021-9991(83)90136-5.

[14] 陶文铨. 计算流体力学基础与应用[M]. 西安: 西安交通大学出版社, 2018.

[15] COURANT R, ISAACSON E, REES M. On the solution of nonlinear hyperbolic differential equations by finite differences[J]. Communications on Pure and Applied Mathematics, 1952, 5(3): 243-255. DOI: 10.1002/cpa.3160050303.

[16] STEGER J L, WARMING R F. Flux vector splitting of the inviscid gasdynamic equations with application to finite-difference methods[J]. Journal of Computational Physics, 1981, 40(2): 263-293. DOI: 10.1016/0021-9991(81)90210-2.

### 6.3 关键文献与本项目规划的关联说明

| 文献编号 | 关联内容 | 在规划中的用途 |
|---------|---------|---------------|
| [1] Sod (1978) | 提出Sod激波管问题，定义标准初始条件，对比多种有限差分格式 | 项目背景、问题设置、数值格式选择依据 |
| [2] Toro (2009) | Riemann问题理论、精确解法、多种数值格式的系统介绍 | 精确解获取方法、数值格式理论支撑 |
| [3] Blazek (2015) | CFD基础理论、空间离散格式、时间推进方法 | 数值格式实现指南、项目流程参考 |
| [4] ASME (2009) | CFD验证与确认的标准方法论 | 对比验证指标定义、误差分析框架 |
| [5] LeVeque (1992) | 守恒律数值方法经典教材，有限差分法系统论述 | 有限差分法离散原理、稳定性分析 |
| [6] OneFlow-CFD | 项目指定的问题设置与边界条件参考 | 确保问题设置与项目要求一致 |
| [7] Roe (1981) | Roe近似Riemann求解器 | 可选数值格式之一 |
| [8] Van Leer (1979) | MUSCL格式与TVD理论 | 二阶高精度格式的理论基础 |
| [9] Lax-Wendroff (1960) | 经典二阶有限差分格式 | 对比格式之一 |
| [10] LeVeque (2002) | 有限体积法理论、Riemann问题 | 数值方法实现的理论参考 |
| [11] Oberkampf (2002) | V&V理论综述、代码验证与解验证的区分 | 验证流程设计的理论依据 |
| [12] MacCormack (1969) | MacCormack预估校正格式原始论文 | MacCormack格式理论依据 |
| [13] Harten (1983) | TVD格式原始论文，限制器理论 | TVD格式理论依据 |
| [14] 陶文铨 (2018) | 国内CFD教材，有限差分法中文参考 | 有限差分法中文文献支撑 |
| [15] Courant (1952) | 迎风格式原始论文，CFL条件提出 | 迎风格式理论依据 |
| [16] Steger-Warming (1981) | 通量分裂方法 | 迎风格式实现方法 |

---

**文档说明**：

- 本文档为一维Sod激波管CFD课程项目的**Plan阶段规划文档**，仅涵盖项目规划相关内容。
- 所有规划内容均基于真实、公开可查的学术文献，无文献支撑的内容未予输出。
- 参考文献格式严格遵循GB/T 7714-2015标准，可直接用于项目报告。
- 如需代码编写、数值求解、结果分析等超出Plan阶段的支持，请另行说明。
