# 有限差分格式数值方法调研报告

**调研日期**: 2026-05
**所属项目**: 一维Sod激波管CFD数值格式对比项目
**依据文献**: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], LeVeque (1992) [5], Steger & Warming (1981) [16]

---

## 1. 调研概述

### 1.1 调研目的

本报告对求解一维Sod激波管问题可采用的有限差分格式进行系统性调研，为项目代码实现提供理论支撑与选型依据。

### 1.2 调研范围

- 一维可压缩Euler方程有限差分法离散原理
- 5种经典有限差分格式的详细考察（Lax-Friedrichs、Lax-Wendroff、MacCormack、一阶迎风、TVD）
- 格式间横向对比（精度、稳定性、振荡特性、间断捕捉能力）

---

## 2. 控制方程与离散原理

### 2.1 一维可压缩Euler方程

守恒形式 [1]:

$$\frac{\partial \mathbf{U}}{\partial t} + \frac{\partial \mathbf{F}(\mathbf{U})}{\partial x} = 0$$

$$\mathbf{U} = \begin{bmatrix} \rho \\ \rho u \\ \rho E \end{bmatrix}, \quad \mathbf{F}(\mathbf{U}) = \begin{bmatrix} \rho u \\ \rho u^2 + p \\ u(\rho E + p) \end{bmatrix}$$

理想气体状态方程 [2]:

$$p = (\gamma - 1)\left(\rho E - \frac{1}{2}\rho u^2\right), \quad \gamma = 1.4$$

### 2.2 有限差分法基本思想

在均匀网格 $x_i = i\Delta x$ 和 $t^n = n\Delta t$ 上：

- **空间离散**: $\partial\mathbf{F}/\partial x|_i \approx \mathcal{D}(\mathbf{F})_i$
- **时间离散**: $\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \Delta t \cdot \mathcal{D}(\mathbf{F})_i$

### 2.3 激波管问题数值挑战

- **数值振荡**: 中心差分在间断附近产生Gibbs现象 [5]
- **数值耗散**: 一阶格式过度抹平间断 [3]
- **CFL限制**: 显式格式需 $\text{CFL} = |\lambda_{\max}|\Delta t/\Delta x \leq 1$ [5]

---

## 3. 格式详细调研

### 3.1 Lax-Friedrichs 格式 (一阶)

**离散公式** [1][5]:

$$\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_{i+1}^n + \mathbf{U}_{i-1}^n\right) - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right)$$

**特性**:

| 属性 | 值 |
|------|-----|
| 空间精度 | 一阶 $O(\Delta x)$ |
| 时间精度 | 一阶 $O(\Delta t)$ |
| 稳定性 | CFL $\leq$ 1 |
| 数值耗散 | 大 |
| 数值振荡 | 无 |
| 接触间断捕捉 | 差（严重抹平） |

### 3.2 Lax-Wendroff 格式 (二阶)

**离散公式** [1][5]:

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{2\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_{i-1}^n\right) + \frac{(\Delta t)^2}{2(\Delta x)^2}\left[\mathbf{A}_{i+1/2}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right) - \mathbf{A}_{i-1/2}\left(\mathbf{F}_i^n - \mathbf{F}_{i-1}^n\right)\right]$$

**特性**:

| 属性 | 值 |
|------|-----|
| 空间精度 | 二阶 $O(\Delta x^2)$ |
| 时间精度 | 二阶 $O(\Delta t^2)$ |
| 稳定性 | CFL $\leq$ 1 |
| 数值耗散 | 小 |
| 数值振荡 | 显著（间断附近过冲/下冲） |
| 接触间断捕捉 | 中等（有振荡） |

### 3.3 MacCormack 格式 (二阶预估校正)

**离散公式** [1][3]:

预估步: $\mathbf{U}_i^* = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1}^n - \mathbf{F}_i^n\right)$

校正步: $\mathbf{U}_i^{**} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_i^* - \mathbf{F}_{i-1}^*\right)$

最终解: $\mathbf{U}_i^{n+1} = \frac{1}{2}\left(\mathbf{U}_i^* + \mathbf{U}_i^{**}\right)$

**特性**:

| 属性 | 值 |
|------|-----|
| 空间精度 | 二阶 $O(\Delta x^2)$ |
| 时间精度 | 二阶 $O(\Delta t^2)$ |
| 稳定性 | CFL $\leq$ 1 |
| 数值耗散 | 小 |
| 数值振荡 | 中等（小于Lax-Wendroff） |
| 实现复杂度 | 中（无需Jacobian矩阵） |

### 3.4 一阶迎风格式 (Steger-Warming通量分裂)

**离散公式** [3][16]:

$$\mathbf{F} = \mathbf{F}^+ + \mathbf{F}^- = \mathbf{R}\boldsymbol{\Lambda}^+\mathbf{R}^{-1}\mathbf{U} + \mathbf{R}\boldsymbol{\Lambda}^-\mathbf{R}^{-1}\mathbf{U}$$

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left[\left(\mathbf{F}_{i}^+ - \mathbf{F}_{i-1}^+\right) + \left(\mathbf{F}_{i+1}^- - \mathbf{F}_i^-\right)\right]$$

特征值: $\lambda_1 = u-c,\ \lambda_2 = u,\ \lambda_3 = u+c$

右特征向量矩阵 (Toro 2009, 式3.42):

$$\mathbf{R} = \begin{pmatrix} 1 & 1 & 1 \\ u-c & u & u+c \\ H-uc & \frac{1}{2}u^2 & H+uc \end{pmatrix}$$

**特性**:

| 属性 | 值 |
|------|-----|
| 空间精度 | 一阶 $O(\Delta x)$ |
| 时间精度 | 一阶 $O(\Delta t)$ |
| 稳定性 | CFL $\leq$ 1 |
| 数值耗散 | 中等 |
| 数值振荡 | 无 |
| 激波捕捉 | 锐利（2-3网格） |
| 接触间断捕捉 | 中等（抹平） |

### 3.5 TVD格式 (推荐补充)

**概述**: TVD（Total Variation Diminishing）由Harten (1983)提出，在光滑区保持二阶精度，间断附近自动降为一阶 [5]。

**数值通量**:

$$\mathbf{F}_{i+1/2} = \mathbf{F}_{i+1/2}^{\text{low}} + \phi(r_i)\left(\mathbf{F}_{i+1/2}^{\text{high}} - \mathbf{F}_{i+1/2}^{\text{low}}\right)$$

常用限制器: Minmod、Superbee、Van Leer

Minmod限制器: $\phi(r) = \max(0, \min(1, r))$

---

## 4. 格式横向对比

| 维度 | Lax-Friedrichs | Lax-Wendroff | MacCormack | 一阶迎风 | TVD |
|------|---------------|--------------|------------|---------|-----|
| 空间精度 | 一阶 | 二阶 | 二阶 | 一阶 | 二阶/一阶 |
| 时间精度 | 一阶 | 二阶 | 二阶 | 一阶 | 二阶 |
| 激波捕捉 | 稳定/抹平 | 振荡 | 振荡 | 锐利 | 锐利无振荡 |
| 接触间断 | 差 | 中 | 中 | 中 | 良 |
| 数值振荡 | 无 | 显著 | 中等 | 无 | 无 |
| 数值耗散 | 大 | 小 | 小 | 中等 | 自适应 |
| 实现难度 | 简单 | 中 | 中 | 中 | 较复杂 |

---

## 5. 本项目的格式选型建议

| 优先级 | 格式 | 理由 |
|--------|------|------|
| 必选 | Lax-Friedrichs | 一阶耗散基准，展示数值耗散影响 |
| 必选 | MacCormack | 二阶经典格式，与一阶形成精度对比 |
| 必选 | 一阶迎风 | 无振荡特性，对比中心差分振荡行为 |
| 推荐 | Lax-Wendroff | 二阶经典，展示色散振荡 |
| 推荐 | TVD | 现代高阶格式，展示限制器技术优势 |

---

## 6. 参考文献

[1] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31.

[2] TORO E F. Riemann solvers and numerical methods for fluid dynamics[M]. 3rd ed. Berlin: Springer, 2009.

[3] LANEY C B. Computational gasdynamics[M]. Cambridge: Cambridge University Press, 1998.

[5] LEVEQUE R J. Numerical methods for conservation laws[M]. 2nd ed. Basel: Birkhauser, 1992.

[16] STEGER J L, WARMING R F. Flux vector splitting of the inviscid gasdynamic equations with application to finite-difference methods[J]. Journal of Computational Physics, 1981, 40(2): 263-293.
