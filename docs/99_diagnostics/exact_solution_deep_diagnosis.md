# Sod激波管精确解深度诊断报告 -- 激波后区域(Shocked Region)

> 诊断日期: 2026-05-07
> 诊断范围: `src/exact_solver.py` 与 `utils.py` 中的 `sod_exact_solution` 函数

---

## 1. 诊断结论（核心发现）

**精确解求解代码在激波后区域（x_contact < x < x_shock）的实现完全正确，不存在逻辑错误。**

两个实现文件（`src/exact_solver.py` 与 `utils.py`）的区域5段赋值逻辑一致，所有物理量在5个区域内的值均与 Toro (2009) 第4章的理论预期完全吻合。

---

## 2. 理论基础（Toro 2009, 第4章）

### 2.1 Sod激波管问题的波系结构

Sod激波管问题的初始条件（Sod, 1977）在 x = 0.5 处存在间断：

| 区域 | 左态 (x < 0.5) | 右态 (x >= 0.5) |
|------|----------------|-----------------|
| rho  | 1.0            | 0.125           |
| u    | 0.0            | 0.0             |
| p    | 1.0            | 0.1             |

t > 0 时，初始间断分解为5个区域（Toro 2009, 第4.3节）：

```
区域1         区域2           区域3      区域4       区域5
(左未扰动)   (稀疏波)        (左星区)   (右星区)    (右未扰动)
x < x_head   x_head<x<x_tail  x_tail<x<x_contact  x_contact<x<x_shock  x > x_shock
ρ=1, u=0     ρ↓, u↑, p↓     ρ=ρ*_L     ρ=ρ*_R     ρ=0.125
p=1          (等熵变化)       u=u*       u=u*       u=0
                                          p=p*       p=0.1
```

### 2.2 关键物理量（t=0.2时刻，通过诊断脚本计算）

| 参数 | 数值 | 来源 |
|------|------|------|
| p*   | 0.303130 | Toro (2009), 式4.46 |
| u*   | 0.927453 | Toro (2009), 式4.47 |
| rho*_L | 0.426319 | 稀疏波尾部密度 |
| rho*_R | 0.265574 | 激波后密度(Rankine-Hugoniot) |
| x_head | 0.263357 | 稀疏波头 |
| x_tail | 0.485945 | 稀疏波尾 |
| x_contact | 0.685491 | 接触间断 |
| x_shock | 0.850431 | 右激波 |

---

## 3. 代码审查

### 3.1 `src/exact_solver.py` 步骤5（区域赋值）

文件: `e:\trae_project\a\src\exact_solver.py`，第104-133行

```python
for i in range(n):
    xi = x[i]

    if xi <= x_head:            # 区域1: 左未扰动
        rho_exact[i] = rho_L    # = 1.0
        u_exact[i] = u_L        # = 0.0
        p_exact[i] = p_L        # = 1.0

    elif xi <= x_tail_L:        # 区域2: 稀疏波（等熵）
        xi_local = (xi - 0.5) / t
        u_val = 2.0 / (gamma + 1.0) * (a_L + xi_local)
        a_val = a_L - (gamma - 1.0) / 2.0 * (u_val - u_L)
        rho_exact[i] = rho_L * (a_val / a_L) ** (2.0 / (gamma - 1.0))
        u_exact[i] = u_val
        p_exact[i] = p_L * (a_val / a_L) ** (2.0 * gamma / (gamma - 1.0))

    elif xi <= x_contact:       # 区域3: 左星区
        rho_exact[i] = rho_star_L   # = 0.426319
        u_exact[i] = u_star         # = 0.927453
        p_exact[i] = p_star         # = 0.303130

    elif xi <= x_shock:         # 区域4: 右星区（接触间断与激波之间）
        rho_exact[i] = rho_star_R   # = 0.265574
        u_exact[i] = u_star         # = 0.927453
        p_exact[i] = p_star         # = 0.303130

    else:                       # 区域5: 右未扰动
        rho_exact[i] = rho_R    # = 0.125
        u_exact[i] = u_R        # = 0.0
        p_exact[i] = p_R        # = 0.1
```

**区域4（x_contact < x < x_shock）的赋值：`rho=ρ*_R, u=u*, p=p*`**
这是正确的！因为接触间断和激波之间的区域是右星区（star region on the right），其压力和速度必须与左星区相等（p*=0.303, u*=0.927），只有密度不同（ρ*_R=0.266 vs ρ*_L=0.426）。

### 3.2 `utils.py` 步骤5（区域赋值）

文件: `e:\trae_project\a\utils.py`，第306-341行

`utils.py` 中的实现与 `src/exact_solver.py` 完全一致，没有任何差异。

### 3.3 数值验证结果

通过诊断脚本对36个测试点的逐点检查：

| x范围 | 区域 | rho | u | p | 是否正确 |
|-------|------|-----|---|---|----------|
| x < 0.263 | 左未扰动 | 1.0000 | 0.0000 | 1.0000 | 正确 |
| 0.263-0.486 | 稀疏波 | 连续变化 | 连续变化 | 连续变化 | 正确 |
| 0.486-0.685 | 左星区 | 0.4263 | 0.9275 | 0.3031 | 正确 |
| **0.685-0.850** | **右星区** | **0.2656** | **0.9275** | **0.3031** | **正确** |
| x > 0.850 | 右未扰动 | 0.1250 | 0.0000 | 0.1000 | 正确 |

**关键诊断点 x=0.9：** x=0.9 > x_shock=0.850，因此它位于右未扰动区域（区域5），期望值为 rho=0.125, u=0, p=0.1。代码返回值完全正确。

---

## 4. 用户原始问题的重新分析

### 4.1 用户描述的问题

用户报告从网格收敛图中观察到：
- "速度u在x>0.85处突然降到0" -- 用户认为应该是 u*=0.927
- "压力p在x>0.68处直接降到0.1" -- 用户认为应该是 p*=0.303 的平台直到 x_shock

### 4.2 问题澄清

用户的部分描述有误，部分是正确的观察：

1. **"速度u在x>0.85处降到0" -- 这是正确的！**
   x > x_shock ≈ 0.85 是右未扰动区域，u=0 是正确的物理行为。u*=0.927 只存在于 x_contact < x < x_shock 的右星区。

2. **"压力p在x>0.68处直接降到0.1" -- 这需要确认。**
   正确行为：p 应该在 x_contact < x < x_shock (0.685 < x < 0.850) 保持为 p*=0.303，然后在 x_shock 处跳到 p_R=0.1。如果图中 p 在 x > 0.68 立刻降到 0.1，那可能是**数值格式的耗散效应**导致的，而非精确解错误。一阶迎风格式具有强数值耗散，会显著模糊激波和接触间断的锐利度。

### 4.3 实际原因

诊断确认：**精确解代码完全正确**。用户看到的"异常"可能来源于：

1. **数值格式的数值耗散**：一阶迎风格式（Steger-Warming）在激波和接触间断处会产生显著的数值抹平效应，导致数值解的阶跃过渡区较宽。
2. **网格分辨率不足**：在低分辨率下（如N=100），接触间断和激波可能只跨越少数几个网格点，在视觉上看起来像是"过早"或"过晚"的跳跃。
3. **图的视觉误导**：当数值解（彩色线）与精确解（黑线）重叠绘制时，数值耗散造成的"斜坡"可能使精确解的阶跃看起来位置不对。

---

## 5. 与 OneFlow-CFD 示例的一致性

OneFlow-CFD 的 Sod 示例 (https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html) 同样使用 Toro (2009) 第4章的方法计算精确解，区域划分为5段。本实现与 OneFlow-CFD 的方法完全一致。

---

## 6. 可靠性结论

1. **`src/exact_solver.py`** -- 正确，无需修改
2. **`utils.py`** -- 正确，无需修改
3. **两个实现的精确解结果完全一致**（诊断脚本验证了所有测试点）
4. **数值解与精确解的偏差**来源于数值格式的固有特性（数值耗散/色散），而非精确解计算错误
5. 若要改善数值解与精确解的视觉一致性，建议使用更高阶格式（如TVD-Minmod、MacCormack等），或使用更细的网格

---

## 7. 附录：关键诊断数据

### 7.1 诊断脚本输出（节选）

```
接触间断压力 p* = 0.303130
接触间断速度 u* = 0.927453
接触间断左侧密度 rho*_L = 0.426319
接触间断右侧密度 rho*_R = 0.265574
稀疏波头 x_head = 0.263357
稀疏波尾 x_tail_L = 0.485945
接触间断 x_contact = 0.685491
激波位置 x_shock = 0.850431
```

### 7.2 右星区（x_contact 到 x_shock）逐点验证

```
x=0.6900: rho=0.2656, u=0.9275, p=0.3031 -> 右星区
x=0.7000: rho=0.2656, u=0.9275, p=0.3031 -> 右星区
...
x=0.8400: rho=0.2656, u=0.9275, p=0.3031 -> 右星区
x=0.8500: rho=0.2656, u=0.9275, p=0.3031 -> 右星区
x=0.8600: rho=0.1250, u=0.0000, p=0.1000 -> 右未扰动
```

从 x_contact=0.685 到 x_shock=0.850 之间的所有点都正确赋值为右星区状态（rho=0.2656, u=0.9275, p=0.3031），激波位置 x_shock=0.850 之后正确切换为右未扰动状态。

---

## 参考文献

1. Sod, G. A. (1977). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. Journal of Computational Physics, 27(1), 1-31.
2. Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics: A Practical Introduction (3rd ed.). Springer. Chapter 4.
3. OneFlow-CFD Documentation. Sod Shock Tube Example. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html
