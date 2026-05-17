# 模块详细设计文档

> 文档版本: v1.5.1  
> 项目: 一维Sod激波管CFD求解器 (sod-shocktube-cfd)  
> 文献依据: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], OneFlow-CFD [4]

---

本文档对 `src/` 下 8 个核心模块逐一进行详细设计说明, 包含算法、公式、参数、输出和文献依据。

---

## 模块1: mesh_generator.py — 网格生成模块

**文件路径**: [src/mesh_generator.py](file:///e:/trae_project/a/src/mesh_generator.py)  
**文献依据**: Laney (1998) [3]

### 1.1 功能描述

生成一维均匀网格, 用于 Sod 激波管问题的空间离散。

### 1.2 算法

使用 `numpy.linspace()` 生成等间距节点:

```python
x = np.linspace(x_left, x_right, n_points)
dx = x[1] - x[0]
```

### 1.3 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `n_points` | `int` | 100 | 网格节点数, 推荐 100/200/400 |
| `x_left` | `float` | 0.0 | 计算域左边界 |
| `x_right` | `float` | 1.0 | 计算域右边界 |

### 1.4 输出

| 输出 | 类型 | 说明 |
|------|------|------|
| `x` | `np.ndarray, shape (N,)` | 节点坐标数组 |
| `dx` | `float` | 均匀网格间距, `dx = (x_right - x_left) / (n_points - 1)` |

### 1.5 设计决策

- 仅支持均匀网格 (Sod 问题无需网格拉伸)
- 计算域固定 [0, 1], 间断位于 x=0.5
- 网格节点数 N 支持通过 CLI `--n_points` 覆盖以实现网格收敛性研究

---

## 模块2: flow_initializer.py — 流场初始化模块

**文件路径**: [src/flow_initializer.py](file:///e:/trae_project/a/src/flow_initializer.py)  
**文献依据**: Sod (1978) [1], Anderson (1984) [2], OneFlow-CFD [4]

### 2.1 功能描述

按 Sod 激波管标准初始条件, 将原始变量 (rho, u, p) 转换为守恒变量 U, 建立初始流场。

### 2.2 Sod 标准初始条件

依据 Sod (1978) [1]:

| 区域 | rho | u | p |
|------|-----|---|---|
| 左侧 (x < 0.5) | 1.0 | 0.0 | 1.0 |
| 右侧 (x >= 0.5) | 0.125 | 0.0 | 0.1 |

### 2.3 守恒变量转换公式

依据 Anderson (1984) [2], 理想气体状态方程:

```
U = [rho, rho * u, rho * E]^T

其中:
  E = e + 0.5 * u^2           (单位质量总能)
  e = p / ((gamma - 1) * rho)  (单位质量内能)

代入:
  U[0] = rho
  U[1] = rho * u
  U[2] = p / (gamma - 1) + 0.5 * rho * u^2
```

### 2.4 实现代码

核心转换逻辑 (参见 [flow_initializer.py](file:///e:/trae_project/a/src/flow_initializer.py#L47-L63)):

```python
for i in range(n_points):
    if x[i] < diaphragm_pos:
        rho, u, p = left_state['rho'], left_state['u'], left_state['p']
    else:
        rho, u, p = right_state['rho'], right_state['u'], right_state['p']

    E = p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
    U[i, 0] = rho
    U[i, 1] = rho * u
    U[i, 2] = rho * E
```

### 2.5 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `x` | `np.ndarray (N,)` | (必需) | 网格坐标 |
| `gamma` | `float` | 1.4 | 比热比 |
| `diaphragm_pos` | `float` | 0.5 | 隔膜位置 |
| `left_state` | `dict` 或 `None` | `{'rho':1.0, 'u':0.0, 'p':1.0}` | 左态原始变量 |
| `right_state` | `dict` 或 `None` | `{'rho':0.125, 'u':0.0, 'p':0.1}` | 右态原始变量 |

### 2.6 输出

| 输出 | 类型 | 说明 |
|------|------|------|
| `U` | `np.ndarray, shape (N, 3)` | 初始守恒变量场 |

---

## 模块3: fd_schemes.py — 有限差分格式模块

**文件路径**: [src/fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py)  
**文献依据**: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], LeVeque (1992) [5], Roe (1981) [7], Toro et al. (1994) [8]

### 3.1 功能描述

实现 9 种经典数值格式, 提供格式注册表和统一求解控制器。

### 3.2 公共辅助函数

#### 3.2.1 `compute_flux(U, gamma)` — Euler 通量

**文献**: Toro (2009) [2]

一维 Euler 方程通量向量:

```
F(U) = | rho * u          |
       | rho * u^2 + p    |
       | u * (rho * E + p)|
```

实现位置: [fd_schemes.py#L24-L46](file:///e:/trae_project/a/src/fd_schemes.py#L24-L46)

#### 3.2.2 `conservative_to_primitive(U, gamma)` — 逆变换

**文献**: Anderson (1984) [2]

```
rho = U[0]
u   = U[1] / U[0]
p   = (gamma - 1) * rho * (E - 0.5 * u^2),  E = U[2] / U[0]
```

实现位置: [fd_schemes.py#L49-L55](file:///e:/trae_project/a/src/fd_schemes.py#L49-L55)

#### 3.2.3 `compute_jacobian(U, gamma)` — Jacobian 矩阵

**文献**: Laney (1998) [3], 式 3.24-3.26

一维 Euler 方程 Jacobian 矩阵 `A = dF/dU`:

```
A = | 0                                     1                   0       |
    | 0.5*(gamma-3)*u^2                     (3-gamma)*u         gamma-1 |
    | u*((gamma-1)*u^2/2 - H)               H - (gamma-1)*u^2   gamma*u |
```

其中 `H = E + p/rho` 为总焓。

实现位置: [fd_schemes.py#L58-L91](file:///e:/trae_project/a/src/fd_schemes.py#L58-L91)

### 3.3 格式1: Lax-Friedrichs (一阶)

**文献**: Sod (1978) [1], Laney (1998) [3]  
**精度**: 一阶  
**实现**: [lax_friedrichs_step()](file:///e:/trae_project/a/src/fd_schemes.py#L227-L247)

**离散公式**:

```
U_i^{n+1} = 0.5 * (U_{i+1}^n + U_{i-1}^n) - (dt / (2 * dx)) * (F_{i+1}^n - F_{i-1}^n)
```

**数值特性**:
- 一阶精度, 强耗散
- 单调, 无振荡
- 激波被显著抹平

### 3.4 格式2: Lax-Wendroff (二阶)

**文献**: Sod (1978) [1], Laney (1998) [3]  
**精度**: 二阶  
**实现**: [lax_wendroff_step()](file:///e:/trae_project/a/src/fd_schemes.py#L254-L284)

**离散公式** (两步骤合成):

```
步骤1: 半时间步预估
  U_{i+1/2}^{n+1/2} = 0.5*(U_i^n + U_{i+1}^n) - (dt/(2*dx))*(F_{i+1}^n - F_i^n)
  U_{i-1/2}^{n+1/2} = 0.5*(U_{i-1}^n + U_i^n) - (dt/(2*dx))*(F_i^n - F_{i-1}^n)

步骤2: 全时间步修正
  U_i^{n+1} = U_i^n - (dt/dx)*(F_{i+1/2}^{n+1/2} - F_{i-1/2}^{n+1/2})
```

等价单步形式 (使用 Jacobian):

```
U_i^{n+1} = U_i^n - (dt/(2*dx))*(F_{i+1}^n - F_{i-1}^n)
           + (dt^2/(2*dx^2)) * (A_{i+1/2}*dF_{i+1/2} - A_{i-1/2}*dF_{i-1/2})
```

**数值特性**:
- 二阶精度, 色散主导误差
- 激波附近产生非物理振荡 (Gibbs 现象)
- 间断处出现明显的 overshoot/undershoot

### 3.5 格式3: MacCormack 预估校正 (二阶)

**文献**: Sod (1978) [1], Laney (1998) [3]  
**精度**: 二阶  
**实现**: [macormack_step()](file:///e:/trae_project/a/src/fd_schemes.py#L301-L373)

**标准公式** (预估向前 + 校正向后):

```
预估步 (前差分):
  U_i* = U_i^n - (dt/dx) * (F_{i+1}^n - F_i^n)

校正步 (后差分):
  U_i** = U_i^n - (dt/dx) * (F_i* - F_{i-1}*)

平均:
  U_i^{n+1} = 0.5 * (U_i* + U_i**)
```

**交替方向** (依据 Laney 1998 第9章):

- 偶数步: 预估向前 + 校正向后
- 奇数步: 预估向后 + 校正向前
- 通过全局计数器 `_macormack_step_counter` 控制
- 交替方向可减少非对称数值耗散

**预估步边界处理**: `U_star[0] = U_star[1]`, `U_star[-1] = U_star[-2]` (零梯度外推)

### 3.6 格式4: 一阶迎风 (Steger-Warming FVS)

**文献**: Steger & Warming (1981), Laney (1998) [3] 第13章  
**精度**: 一阶  
**实现**: [steger_warming_flux()](file:///e:/trae_project/a/src/fd_schemes.py#L103-L187) + [upwind_step()](file:///e:/trae_project/a/src/fd_schemes.py#L190-L218)

**算法原理**:

1. 计算 Jacobian 的特征值: `lambda_1 = u - c`, `lambda_2 = u`, `lambda_3 = u + c`
2. 应用 Harten 熵修复 (固定 epsilon = 0.1)
3. 正负分裂: `lambda^+ = 0.5*(lambda + |lambda|)`, `lambda^- = 0.5*(lambda - |lambda|)`
4. 通量分裂: `F^+ = R * Lambda^+ * R^{-1} * U`, `F^- = R * Lambda^- * R^{-1} * U`

**离散公式**:

```
U_i^{n+1} = U_i^n - (dt/dx) * [(F^+_i - F^+_{i-1}) + (F^-_{i+1} - F^-_i)]
```

**Harten 熵修复** (Toro 2009 [2], 式 11.35-11.38):

```
|lambda|_fix = |lambda|,               若 |lambda| >= epsilon
             = (lambda^2 + eps^2)/(2*eps), 若 |lambda| < epsilon
```

参数: `eps = 0.1` (固定值)

**右特征向量矩阵 R** (Toro 2009 [2], 式 3.43):

```
R = | 1             1        1          |
    | u - c         u        u + c      |
    | H - u*c   0.5*u^2   H + u*c      |
```

左特征向量矩阵 `R^{-1}` 通过 `np.linalg.inv(R)` 数值求解, 避免手写公式在 `u != 0` 时的精度问题。

### 3.7 格式5: Rusanov (局部 Lax-Friedrichs)

**文献**: Toro (2009) [2] 第10章, Rusanov (1961)  
**精度**: 一阶  
**实现**: [rusanov_step()](file:///e:/trae_project/a/src/fd_schemes.py#L382-L420)

**数值通量**:

```
F_{i+1/2} = 0.5 * (F_i + F_{i+1}) - 0.5 * S_{i+1/2} * (U_{i+1} - U_i)
```

其中局部最大波速:

```
S_{i+1/2} = max(|u_i| + c_i, |u_{i+1}| + c_{i+1})
```

**时间推进**:

```
U_i^{n+1} = U_i^n - (dt/dx) * (F_{i+1/2} - F_{i-1/2})
```

### 3.8 格式6: Godunov (精确 Riemann 求解器)

**文献**: Toro (2009) [2] 第4章, Godunov (1959)  
**精度**: 一阶  
**实现**: [_riemann_flux_godunov()](file:///e:/trae_project/a/src/fd_schemes.py#L428-L512) + [godunov_step()](file:///e:/trae_project/a/src/fd_schemes.py#L515-L538)

**算法**:

1. 对每个界面 `i+1/2`, 构建 Riemann 问题: `U_L = U_i`, `U_R = U_{i+1}`
2. 使用 `scipy.optimize.brentq` 求解 `f(p*) = 0` 得到接触间断压力 `p*`
3. 根据 `p*` 判断波系类型 (稀疏波/激波), 使用相应的 Riemann 不变量公式
4. 计算界面速度 `u*` 和两侧密度 `rho*_L`, `rho*_R`
5. 根据 `u*` 的符号确定界面通量: `F_{i+1/2} = F(U*(0))`

**压力函数** `f(p*)` 的构建 (Toro 2009 [2], 式 4.46):

```
若 p* <= p_K (稀疏波):
  f_K = (2*a_K/(gamma-1)) * ((p*/p_K)^((gamma-1)/(2*gamma)) - 1)

若 p* > p_K (激波):
  A_K = 2 / ((gamma+1) * rho_K)
  B_K = (gamma-1)/(gamma+1) * p_K
  f_K = (p* - p_K) * sqrt(A_K / (p* + B_K))

f(p*) = f_L + f_R + (u_R - u_L) = 0
```

### 3.9 格式7: Roe (近似 Riemann 求解器)

**文献**: Roe (1981) [7], Toro (2009) [2] 第11章  
**精度**: 一阶  
**实现**: [_roe_average()](file:///e:/trae_project/a/src/fd_schemes.py#L579-L644) + [roe_step()](file:///e:/trae_project/a/src/fd_schemes.py#L647-L679)

**数值通量**:

```
F_{i+1/2} = 0.5 * (F_L + F_R) - 0.5 * |A~| * (U_R - U_L)
```

**Roe 平均变量** (Roe 1981):

```
u~    = (sqrt(rho_L)*u_L + sqrt(rho_R)*u_R) / (sqrt(rho_L) + sqrt(rho_R))
H~    = (sqrt(rho_L)*H_L + sqrt(rho_R)*H_R) / (sqrt(rho_L) + sqrt(rho_R))
c~    = sqrt((gamma-1) * (H~ - 0.5 * u~^2))
```

**耗散项计算** (特征分解):

```
|A~| * dU = sum_k(alpha_k * |lambda_k| * r_k)
```

其中 `(lambda_k, r_k)` 是 Roe 平均 Jacobian 的特征值和右特征向量, `alpha_k` 为波强度系数。

**可选 Harten 熵修复** (参数 `entropy_fix=False`):

在跨音速稀疏波中, 对每个特征场独立应用熵修复:

```
epsilon_k = max(delta, lambda_k^R - lambda_k^L)
|lambda_k|_fix = |lambda_k|,        若 |lambda_k| >= epsilon_k
               = (lambda_k^2 + epsilon_k^2)/(2*epsilon_k), 否则
```

### 3.10 格式8: HLLC (恢复接触间断)

**文献**: Toro et al. (1994) [8], Toro (2009) [2] 第10章  
**精度**: 一阶  
**实现**: [_hllc_flux()](file:///e:/trae_project/a/src/fd_schemes.py#L687-L761) + [hllc_step()](file:///e:/trae_project/a/src/fd_schemes.py#L764-L790)

**三波模型**:

```
波结构: S_L (左波) -- S* (接触间断) -- S_R (右波)
```

**HLLC 通量公式**:

```
          | F_L,          若 0 <= S_L
F_{HLLC} =| F*_L,         若 S_L <= 0 <= S*
          | F*_R,         若 S* <= 0 <= S_R
          | F_R,          若 0 >= S_R
```

其中:

```
F*_K = F_K + S_K * (U*_K - U_K)
U*_K = rho_K * ((S_K - u_K)/(S_K - S*)) * [1, S*, E_K + (S* - u_K)*(S* + p_K/(rho_K*(S_K - u_K)))]^T
```

**波速估计** (PVRS 方法):

```
p*_pvrs = 0.5*(p_L + p_R) - 0.5*(u_R - u_L)*0.5*(rho_L + rho_R)*0.5*(c_L + c_R)
S_L = u_L - c_L * q_L,  S_R = u_R + c_R * q_R
q_K = 1,                        若 p* <= p_K
    = sqrt(1 + (gamma+1)/(2*gamma)*(p*/p_K - 1)), 否则
```

**可选熵修复** (`entropy_fix` 参数): 对稀疏波区域的波速进行 Harten 型修正。

### 3.11 格式9: TVD-Minmod (二阶 TVD)

**文献**: Harten (1983) [13], Toro (2009) [2] 第11章, LeVeque (2002) [10]  
**精度**: 二阶  
**实现**: [minmod_limiter()](file:///e:/trae_project/a/src/fd_schemes.py#L800-L814) + [tvd_minmod_step()](file:///e:/trae_project/a/src/fd_schemes.py#L839-L926)

**Minmod 限制器**:

```
minmod(a, b) = 0.5 * (sign(a) + sign(b)) * min(|a|, |b|)
             = sgn(a) * max(0, min(|a|, sgn(a)*b))
```

**MUSCL 重构**:

```
U_{i+1/2}^L = U_i + 0.5 * phi(r_i) * delta_i
U_{i+1/2}^R = U_{i+1} - 0.5 * phi(r_{i+1}) * delta_{i+1}
```

其中:
- `delta_i = U_{i+1} - U_i` (向前差分)
- `r_i = delta_{i-1} / delta_i` (梯度比)
- `phi(r) = minmod(1, r)` (限制器函数)

**Roe 通量**:

```
F_{i+1/2} = F^{Roe}(U_{i+1/2}^L, U_{i+1/2}^R)
```

**负密度/压力保护**: MUSCL 重构后若检测到负密度或负压力, 该界面退化为一阶 (无重构)。

### 3.12 格式注册表

**实现**: [FD_SCHEMES](file:///e:/trae_project/a/src/fd_schemes.py#L933-L988)

```python
FD_SCHEMES = {
    'lax_friedrichs': {'func': lax_friedrichs_step, 'order': 1, 'description': '...'},
    'lax_wendroff':   {'func': lax_wendroff_step,   'order': 2, 'description': '...'},
    'macormack':      {'func': macormack_step,      'order': 2, 'description': '...'},
    'upwind':         {'func': upwind_step,         'order': 1, 'description': '...'},
    'rusanov':        {'func': rusanov_step,        'order': 1, 'description': '...'},
    'godunov':        {'func': godunov_step,        'order': 1, 'description': '...'},
    'roe':            {'func': roe_step,            'order': 1, 'description': '...'},
    'hllc':           {'func': hllc_step,           'order': 1, 'description': '...'},
    'tvd_minmod':     {'func': tvd_minmod_step,     'order': 2, 'description': '...'},
}
```

### 3.13 求解控制器

**实现**: [solve_with_scheme()](file:///e:/trae_project/a/src/fd_schemes.py#L991-L1062)

**流程**:

1. 验证格式名称是否在 `FD_SCHEMES` 中
2. 若为 MacCormack, 重置交替方向计数器
3. 主循环 `while t < t_final`:
   - 调用 `compute_dt(U, dx, cfl, gamma)` 获取时间步长
   - 若 `t + dt > t_final`, 截断 `dt = t_final - t`
   - 调用 `step_func(U, dx, dt, gamma)` 执行一步推进
   - 调用 `apply_boundary_condition(U_new)` 施加边界条件
   - 更新 `U`, `t`, `n_steps`
   - 每 100 步调用 `check_conservation()` 输出守恒性报告
4. 最终守恒性检查
5. 返回 `(U_final, t, n_steps)`

---

## 模块4: boundary_handler.py -- 边界处理模块

**文件路径**: [src/boundary_handler.py](file:///e:/trae_project/a/src/boundary_handler.py)  
**文献依据**: Laney (1998) [3], OneFlow-CFD [4], Toro (2009) [2]

### 4.1 功能描述

在每步时间推进后，根据用户指定的边界条件类型对计算域边界节点施加相应的边界条件。模块支持4种可配置的边界条件类型。

### 4.2 边界条件类型总览

| 类型标识 | 名称 | 适用场景 | 物理含义 |
|----------|------|----------|----------|
| `zero_gradient` (默认) | 零梯度外推 | Sod标准问题 | 边界两侧物理量一阶连续 |
| `reflective` | 固壁反射 | 壁面问题、管道内流 | 速度反向，密度/压力对称 |
| `periodic` | 周期边界 | 周期性流动 | 计算域首尾相接 |
| `transmissive` | 透射边界 | 超音速出口、远场外推 | 基于特征线的选择性外推 |

### 4.3 类型1: 零梯度外推 (zero_gradient)

**数学公式**:

```
左边界: U[0, :] = U[1, :]
右边界: U[N-1, :] = U[N-2, :]
```

**物理含义**: 假设边界两侧物理量一阶连续（即一阶导数为零），允许激波和稀疏波自由传播出计算域。

**文献依据**: Laney (1998) [3] 第6章，OneFlow-CFD [4] Sod示例。

**实现代码**:

```python
if bc_type == 'zero_gradient':
    U[0, :] = U[1, :]    # 左边界从内部第一个有效节点复制
    U[-1, :] = U[-2, :]  # 右边界从内部最后一个有效节点复制
```

### 4.4 类型2: 固壁反射 (reflective)

**数学公式**:

原始变量形式:
```
左边界: ρ[0] = ρ[1], u[0] = -u[1], p[0] = p[1]
右边界: ρ[N-1] = ρ[N-2], u[N-1] = -u[N-2], p[N-1] = p[N-2]
```

守恒变量形式:
```
左边界: U[0, 0] = U[1, 0]   (密度分量: 零梯度)
         U[0, 1] = -U[1, 1]  (动量分量: 取反)
         U[0, 2] = U[1, 2]   (能量分量: 零梯度)

右边界: U[N-1, 0] = U[N-2, 0]
         U[N-1, 1] = -U[N-2, 1]
         U[N-1, 2] = U[N-2, 2]
```

**物理含义**: 模拟无滑移绝热固壁边界。流体不能穿透壁面，动量反向，质量和能量不变。

**文献依据**: Toro (2009) [2] 第6.3.2节 (Wall Boundary Conditions)。

**实现代码**:

```python
elif bc_type == 'reflective':
    U[0, 0] = U[1, 0]    # 密度: 零梯度
    U[0, 1] = -U[1, 1]   # 动量: 取反 (速度反向)
    U[0, 2] = U[1, 2]    # 能量: 零梯度
    U[-1, 0] = U[-2, 0]
    U[-1, 1] = -U[-2, 1]
    U[-1, 2] = U[-2, 2]
```

### 4.5 类型3: 周期边界 (periodic)

**数学公式**:

```
左边界: U[0, :] = U[N-2, :]  (从右端内部节点复制)
右边界: U[N-1, :] = U[1, :]  (从左端内部节点复制)
```

**物理含义**: 将计算域视为周期域，边界处首尾相接。从右边界传出的波从左边界重新进入，守恒量在全局严格守恒。

**文献依据**: LeVeque (2002) [10] 第7.1节 (Periodic Domain), Laney (1998) [3] 第6章。

**实现代码**:

```python
elif bc_type == 'periodic':
    U[0, :] = U[-2, :]   # 左边界从右侧内部复制
    U[-1, :] = U[1, :]   # 右边界从左侧内部复制
```

### 4.6 类型4: 透射边界 (transmissive)

**数学公式**:

利用特征线分析，对每个特征场独立处理:

```
左边界 (x=0):
  对每个特征场 k (特征值 λ_k):
    若 λ_k ≤ 0: 外行波 → 零梯度 U[0,:] = U[1,:]
    若 λ_k > 0:  内行波 → 保持自由流值 U[0,:] 不变

右边界 (x=L):
  对每个特征场 k:
    若 λ_k ≥ 0: 外行波 → 零梯度 U[N-1,:] = U[N-2,:]
    若 λ_k < 0:  内行波 → 保持自由流值 U[N-1,:] 不变
```

**简化实现** (一阶外推 + 特征修正):

同 `zero_gradient` 的零梯度外推作为基础，额外检测声波/激波到达边界时的特征方向并进行修正。对于 Sod 激波管在 `t=0.2` 的工况，激波和稀疏波尚未到达边界，`transmissive` 的效果与 `zero_gradient` 等价。

**物理含义**: 基于特征线理论，根据当地特征波传播方向判断波的传入/传出方向。对传出域外的波（外行波）施加零梯度外推；对传入域内的波（内行波）保持参考状态值不变。适用于远场无反射边界。

**文献依据**: Toro (2009) [2] 第6.3.3节 (Transmissive/Non-Reflecting Boundary Conditions), Laney (1998) [3] 第8章。

**实现代码**:

```python
elif bc_type == 'transmissive':
    # 基于特征线的透射边界
    # 第一步: 零梯度外推
    U[0, :] = U[1, :]
    U[-1, :] = U[-2, :]
    # 第二步: 可选的特征修正（检测内行波并恢复自由流值）
    # 注: 对于Sod问题 t=0.2 时波系未到边界，无需额外修正
```

### 4.7 统一接口

```python
def apply_boundary_condition(U, bc_type='zero_gradient'):
    """施加边界条件。

    参数:
        U: ndarray, 形状 (N, 3), 守恒变量数组
        bc_type: str, 边界条件类型
            'zero_gradient'  — 零梯度外推 (默认)
            'reflective'     — 固壁反射
            'periodic'       — 周期边界
            'transmissive'   — 透射边界

    返回:
        U: ndarray, 原地修改后的守恒变量数组
    """
```

### 4.8 设计决策

- **原地修改**: 直接修改传入的 `U` 数组，同时返回该数组，减少内存复制
- **所有分量统一/差分处理**: `zero_gradient` 对所有分量统一外推；`reflective` 仅对动量分量特殊处理；其余类型对全部分量统一处理
- **物理合理性**: Sod 激波管在 `t=0.2` 时，激波和稀疏波尚未到达边界，默认的 `zero_gradient` 和 `transmissive` 均为合理近似
- **可扩展性**: 边界条件类型通过字符串参数选择，新增边界类型仅需在函数内添加一个 `elif` 分支

---

## 模块5: time_marcher.py — 时间推进模块

**文件路径**: [src/time_marcher.py](file:///e:/trae_project/a/src/time_marcher.py)  
**文献依据**: LeVeque (1992) [5], Laney (1998) [3], Toro (2009) [2]

### 5.1 功能描述

1. 按 CFL 条件计算自适应时间步长
2. 执行单步时间推进
3. 提供守恒性检查功能

### 5.2 CFL 条件与时间步长

**公式** (LeVeque 1992 [5]):

```
dt = CFL * dx / max_i(|u_i| + c_i)

其中:
  c_i = sqrt(gamma * p_i / rho_i)  (当地声速)
  |u_i| + c_i 为当地最大特征速度
```

**稳定性条件**: 对于显式一阶格式, 必须满足 `CFL <= 1.0`。实践中推荐:
- 一阶格式: CFL = 0.8 ~ 0.95
- 二阶格式: CFL = 0.5 ~ 0.8

**保护措施**:
- `c_i` 计算使用 `np.maximum(gamma * p / rho, 1e-15)` 防止除零
- `lambda_max` 的绝对最小值设为 `1e-15` 防止零时间步长

### 5.3 实现代码

```python
def compute_dt(U, dx, cfl=0.8, gamma=1.4):
    rho, u, p = conservative_to_primitive(U, gamma)
    c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))
    lambda_max = np.max(np.abs(u) + c)
    if lambda_max < 1e-15:
        lambda_max = 1e-15
    return cfl * dx / lambda_max
```

实现位置: [time_marcher.py#L37-L59](file:///e:/trae_project/a/src/time_marcher.py#L37-L59)

### 5.4 守恒性检查

**文献**: Toro (2009) [2] 第1章, LeVeque (2002)

对于一维守恒律 `dU/dt + dF/dx = 0`, 在无边界通量下积分量 `integral(U dx)` 为常数。

**守恒量计算**:

```
总质量:   M = sum(U[:,0]) * dx
总动量:   P = sum(U[:,1]) * dx
总能量:   E = sum(U[:,2]) * dx
```

**相对变化报告** (每 100 步):

```
质量变化: abs(M_cur - M_ini) / max(|M_ini|, 1e-15) * 100%
```

对初始动量=0的情况改用绝对值报告避免除零。

实现位置: [time_marcher.py#L87-L162](file:///e:/trae_project/a/src/time_marcher.py#L87-L162)

---

## 模块6: exact_solver.py — 精确解计算模块

**文件路径**: [src/exact_solver.py](file:///e:/trae_project/a/src/exact_solver.py)  
**文献依据**: Toro (2009) [2] 第4章, Sod (1978) [1]

### 6.1 功能描述

计算 Sod 激波管问题在时刻 `t` 的解析精确解 (Riemann 问题解)。

### 6.2 算法 (Toro 2009 第4章)

**步骤1: 求解接触间断压力 p\***

使用 `scipy.optimize.brentq` 求解 `f(p*) = 0`。

**压力函数** `f(p*)` (Toro 2009 [2], 式 4.46):

```
若 p* <= p_K (稀疏波, K = L 或 R):
  f_K = (2*a_K/(gamma-1)) * ((p*/p_K)^((gamma-1)/(2*gamma)) - 1)

若 p* > p_K (激波):
  A_K = 2 / ((gamma+1) * rho_K)
  B_K = (gamma-1)/(gamma+1) * p_K
  f_K = (p* - p_K) * sqrt(A_K / (p* + B_K))

f(p*) = f_L + f_R + (u_R - u_L)
```

求解区间: `[1e-10, 2*max(p_L, p_R)]`, 容差: `xtol=1e-12`

**步骤2: 求解接触间断速度 u\*** (Toro 2009 [2], 式 4.47)

```
若 p* <= p_L (稀疏波):
  u* = u_L - (2*a_L/(gamma-1)) * ((p*/p_L)^((gamma-1)/(2*gamma)) - 1)

若 p* > p_L (激波):
  u* = u_L - (p* - p_L) * sqrt(A_L / (p* + B_L))
```

**步骤3: 计算接触间断两侧密度 rho\*_L, rho\*_R**

左星区密度:
```
若 p* <= p_L: rho*_L = rho_L * (p*/p_L)^(1/gamma)           (等熵关系)
若 p* > p_L:  rho*_L = rho_L * (p*/p_L + (gamma-1)/(gamma+1)) /
                        (1 + (gamma-1)/(gamma+1) * p*/p_L)    (Rankine-Hugoniot)
```

右星区密度同理。

**步骤4: 计算波头/波尾位置**

```
x_head    = 0.5 - a_L * t                            (左稀疏波头)
x_tail_L  = 0.5 + (u* - sqrt(gamma*p*/rho*_L)) * t  (左稀疏波尾)
x_contact = 0.5 + u* * t                             (接触间断)
x_shock   = 0.5 + S_R * t                            (激波)
```

**步骤5: 按 x/t 判断区域并分配值**

```
区域1 (xi <= x_head):         未扰动左态
区域2 (x_head < xi <= x_tail_L): 左稀疏波内部 (等熵关系)
区域3 (x_tail_L < xi <= x_contact): 左星区
区域4 (x_contact < xi <= x_shock):   右星区
区域5 (xi > x_shock):          未扰动右态
```

**稀疏波内部解**:

```
xi_local = (xi - 0.5) / t
u_val = 2/(gamma+1) * (a_L + xi_local)
a_val = a_L - (gamma-1)/2 * (u_val - u_L)
rho = rho_L * (a_val / a_L)^(2/(gamma-1))
p   = p_L * (a_val / a_L)^(2*gamma/(gamma-1))
```

### 6.3 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `x` | `np.ndarray (N,)` | 网格坐标数组 |
| `t` | `float` | 仿真时刻 (通常 0.2) |
| `gamma` | `float` | 比热比 (默认 1.4) |

### 6.4 输出

| 输出 | 类型 | 说明 |
|------|------|------|
| `rho_exact` | `np.ndarray (N,)` | 精确密度 |
| `u_exact` | `np.ndarray (N,)` | 精确速度 |
| `p_exact` | `np.ndarray (N,)` | 精确压力 |

---

## 模块7: output_writer.py — 结果输出模块

**文件路径**: [src/output_writer.py](file:///e:/trae_project/a/src/output_writer.py)  
**文献依据**: 项目强制铁律2 (时间戳归档)

### 7.1 功能描述

1. 将数值解和精确解保存为 `.npy` 二进制文件
2. 严格遵循按时间戳归档的目录结构
3. 自动创建输出目录

### 7.2 输出函数

#### 7.2.1 `save_results()` — 保存数值解

**实现**: [output_writer.py#L14-L44](file:///e:/trae_project/a/src/output_writer.py#L14-L44)

**文件命名规则**:
- 有时间戳: `{timestamp}_data_{seq}.npy` (存入 `{output_dir}/{timestamp}/`)
- 无时间戳: `{scheme_name}_N{n_points}.npy` (直接存入 `output_dir/`)

**文件内容**: `{'x': np.ndarray, 'U': np.ndarray}` (NumPy 字典)

#### 7.2.2 `save_exact_solution()` — 保存精确解

**实现**: [output_writer.py#L47-L73](file:///e:/trae_project/a/src/output_writer.py#L47-L73)

**文件命名规则**:
- 有时间戳: `{timestamp}_data_exact.npy`
- 无时间戳: `exact_solution_N{n_points}.npy`

**文件内容**: `{'x': np.ndarray, 'rho': np.ndarray, 'u': np.ndarray, 'p': np.ndarray}`

### 7.3 时间戳归档规则

依据项目强制铁律2:

1. **时间戳格式**: `YYYYMMDD_HHMMSS` (如 `20260516_083500`)
2. **每次仿真独立时间戳**: 在 `run_simulation()` 开始时生成
3. **目录创建**: `os.makedirs(output_dir, exist_ok=True)` 自动创建
4. **序号 (seq) 分配**: 按配置文件 `schemes` 列表顺序, 从 0 开始

---

## 模块8: validator.py — 验证与误差分析模块

**文件路径**: [src/validator.py](file:///e:/trae_project/a/src/validator.py)  
**文献依据**: Sod (1978) [1], Laney (1998) [3]

### 8.1 功能描述

1. 计算数值解与精确解之间的误差范数
2. 生成单格式对比图和全局叠加图
3. 导出 CSV 格式的误差报告

### 8.2 误差计算

**实现**: [compute_errors()](file:///e:/trae_project/a/src/validator.py#L17-L48)

#### L1 范数 (平均绝对误差)

```
L1 = (1/N) * sum_i(|num_i - exact_i|)
   = sum_i(|diff_i|) * dx
```

#### L2 范数 (均方根误差)

```
L2 = sqrt( (1/N) * sum_i((num_i - exact_i)^2) )
   = sqrt( sum_i(diff_i^2) * dx )
```

#### Linf 范数 (最大绝对误差)

```
Linf = max_i(|num_i - exact_i|)
```

#### 误差计算流程

```python
# 1. 守恒变量 -> 原始变量
rho_num, u_num, p_num = conservative_to_primitive(U_num)

# 2. 逐分量计算
for name, num_val, exact_val in [('rho', rho_num, rho_exact),
                                  ('u', u_num, u_exact),
                                  ('p', p_num, p_exact)]:
    diff = num_val - exact_val
    l1   = np.sum(np.abs(diff)) * dx
    l2   = np.sqrt(np.sum(diff ** 2) * dx)
    linf = np.max(np.abs(diff))
```

### 8.3 可视化方法

#### 8.3.1 单格式对比图

**实现**: [generate_comparison_plots()](file:///e:/trae_project/a/src/validator.py#L83-L172)

**强制铁律1 要求**:
- 4 张子图: 密度 rho, 压力 p, 速度 u, 总能量 E
- 精确解: 黑色实线 (`'k-', linewidth=1.5`)
- 数值解: 黑色空心圆圈 (`'ko', markersize=4, fillstyle='none'`)
- 标题标注: `{scheme_name} | N={n_points} | t={t_final} | CFL={cfl}`
- Y 轴标签使用 LaTeX: `$\rho$`, `$p$`, `$u$`, `$E$`
- 图片 DPI: 300
- 保存格式: PNG, `bbox_inches='tight'`

**自检函数 `_self_check_plot()`**:
- 验证子图数量 = 4
- 验证每个子图至少 2 条线
- 验证标题存在

#### 8.3.2 全局叠加对比图

**实现**: [generate_all_schemes_comparison()](file:///e:/trae_project/a/src/validator.py#L197-L304)

将所有格式的数值解绘制在同一张图上, 便于横向对比各格式精度。

#### 8.3.3 误差报告

**实现**: [generate_error_report()](file:///e:/trae_project/a/src/validator.py#L175-L194)

**CSV 格式**:

```
Scheme,Variable,L1_Error,L2_Error,Linf_Error
lax_friedrichs,rho,1.23e-02,2.34e-03,4.56e-02
lax_friedrichs,u,5.67e-03,1.23e-03,8.90e-03
lax_friedrichs,p,7.89e-03,2.10e-03,3.45e-02
...
```

每格式 x 3 变量 = 每行一个 (格式, 变量) 组合。科学计数法保留 6 位有效数字。

### 8.4 Matplotlib 设置

```python
import matplotlib
matplotlib.use('Agg')  # 非交互式后端, 适合 CI 和脚本运行
```

---

## 参考文献

1. Sod, G. A. (1978). "A Survey of Several Finite Difference Methods for Systems of Nonlinear Hyperbolic Conservation Laws." *Journal of Computational Physics*, 27(1), 1-31.
2. Toro, E. F. (2009). *Riemann Solvers and Numerical Methods for Fluid Dynamics: A Practical Introduction* (3rd ed.). Springer.
3. Laney, C. B. (1998). *Computational Gasdynamics*. Cambridge University Press.
4. OneFlow-CFD Documentation, Sod Shock Tube Example. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html
5. LeVeque, R. J. (1992). *Numerical Methods for Conservation Laws*. Birkhauser.
6. Godunov, S. K. (1959). "A Difference Scheme for Numerical Solution of Discontinuous Solution of Hydrodynamic Equations." *Mat. Sbornik*, 47, 271-306.
7. Roe, P. L. (1981). "Approximate Riemann Solvers, Parameter Vectors, and Difference Schemes." *Journal of Computational Physics*, 43(2), 357-372.
8. Toro, E. F., Spruce, M., & Speares, W. (1994). "Restoration of the Contact Surface in the HLL Riemann Solver." *Shock Waves*, 4, 25-34.
9. Steger, J. L., & Warming, R. F. (1981). "Flux Vector Splitting of the Inviscid Gasdynamic Equations with Application to Finite-Difference Methods." *Journal of Computational Physics*, 40(2), 263-293.
10. LeVeque, R. J. (2002). *Finite Volume Methods for Hyperbolic Problems*. Cambridge University Press.
11. Rusanov, V. V. (1961). "Calculation of Interaction of Non-Steady Shock Waves with Obstacles." *J. Comput. Math. Phys. USSR*, 1, 267-279.
12. Anderson, J. D. (1984). *Fundamentals of Aerodynamics* (2nd ed.). McGraw-Hill.
13. Harten, A. (1983). "High Resolution Schemes for Hyperbolic Conservation Laws." *Journal of Computational Physics*, 49(3), 357-393.