# Sod激波管精确解计算错误诊断与修复报告

**日期**: 2026-05-07  
**文件**: `e:\trae_project\a\utils.py`  
**影响范围**: 所有依赖 `utils.sod_exact_solution()` 的图表和验证

---

## 1. 问题描述

用户报告网格收敛性验证图中精确解（黑线）存在严重错误：

| 参数 | 错误值 | 理论值 (Toro 2009) | 偏差 |
|------|--------|-------------------|------|
| u* (接触间断速度) | ~0.28 | 0.92745258 | 70% |
| x_contact (接触间断位置) | ~0.57 | 0.68549052 | 17% |
| x_shock (激波位置) | ~0.57 | 0.85043110 | 33% |

数值解反而比精确解更接近正确值，说明精确解计算存在根本性错误。

---

## 2. 诊断过程

### 2.1 初步排查

对比了两个精确解实现：
- `src/exact_solver.py::sod_exact_solution()` - **计算正确**
- `utils.py::sod_exact_solution()` - **计算错误**

诊断脚本输出对比：
```
utils.py结果:
  u范围: [0.00000000, 0.27815453]  ← 错误！
  rho范围: [0.41700504, 1.00000000]
  p范围: [0.71383369, 1.00000000]

src/exact_solver.py结果:
  u范围: [0.00000000, 0.92745262]  ← 正确！
  rho范围: [0.12500000, 1.00000000]
  p范围: [0.10000000, 1.00000000]
```

### 2.2 根因定位

`utils.py` 中存在**两处激波分支公式错误**，均出现在 `p* > p_L` 的激波分支中：

#### 错误1: pressure_function 中 f_L 和 f_R 的计算

**错误代码**:
```python
f_L = (p_star - p_L) / np.sqrt(A_L * (p_star + B_L))   # 错误
f_R = (p_star - p_R) / np.sqrt(A_R * (p_star + B_R))   # 错误
```

**正确公式** (Toro 2009, 式4.46):
```python
f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))   # 正确
f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))   # 正确
```

**数学推导** (Toro 2009, 式4.46):

对于激波，Riemann不变量函数为：
$$f(p_*) = (p_* - p_K) \sqrt{\frac{A_K}{p_* + B_K}}$$

其中：
$$A_K = \frac{2}{(\gamma + 1)\rho_K}, \quad B_K = \frac{\gamma - 1}{\gamma + 1}p_K$$

错误代码使用了：
$$\frac{p_* - p_K}{\sqrt{A_K(p_* + B_K)}} = (p_* - p_K) \cdot \frac{1}{\sqrt{A_K(p_* + B_K)}}$$

而正确公式是：
$$(p_* - p_K) \cdot \sqrt{\frac{A_K}{p_* + B_K}} = (p_* - p_K) \cdot \frac{\sqrt{A_K}}{\sqrt{p_* + B_K}}$$

两者相差一个因子 $A_K$，即比值为 $\frac{1}{A_K}$。

对于左态：$A_L = \frac{2}{(1.4+1)\times 1.0} = \frac{2}{2.4} = 0.8333...$，因此错误公式会引入约1.2倍的偏差。

#### 错误2: u_star 的计算

**错误代码**:
```python
u_star = u_L - (p_star - p_L) / np.sqrt(A_L * (p_star + B_L))   # 错误
```

**正确公式** (Toro 2009, 式4.47):
```python
u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))   # 正确
```

数学上与错误1相同的问题。

### 2.3 错误影响链

1. pressure_function错误 → p*计算错误 (0.7138 vs 0.3031)
2. p*错误 → u_star计算错误 (0.278 vs 0.927)
3. u_star错误 → x_contact位置错误 (0.556 vs 0.685)
4. p*错误 → 密度/压力平台值错误
5. 所有依赖精确解的图表和误差计算全部错误

---

## 3. 修复内容

### 3.1 修复文件

`e:\trae_project\a\utils.py`

### 3.2 修复细节

**修复1** (第242行):
```diff
-             f_L = (p_star - p_L) / np.sqrt(A_L * (p_star + B_L))
+             f_L = (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))
```

**修复2** (第251行):
```diff
-             f_R = (p_star - p_R) / np.sqrt(A_R * (p_star + B_R))
+             f_R = (p_star - p_R) * np.sqrt(A_R / (p_star + B_R))
```

**修复3** (第265行):
```diff
-         u_star = u_L - (p_star - p_L) / np.sqrt(A_L * (p_star + B_L))
+         u_star = u_L - (p_star - p_L) * np.sqrt(A_L / (p_star + B_L))
```

**修复4**: 注释更新以标明公式来源
```diff
-         # 激波
+         # 激波 - 公式: (p*-p_L) * sqrt(A_L / (p*+B_L)), Toro (2009) 式4.46
```

---

## 4. 修复验证

### 4.1 精确解关键参数对比

| 参数 | 修复前 | 修复后 | 理论值 (Toro 2009) | 误差 |
|------|--------|--------|-------------------|------|
| p* | 0.71383369 | **0.30313018** | 0.30313018 | 1.95e-09 |
| u* | 0.27815453 | **0.92745262** | 0.92745258 | 4.00e-08 |
| rho*_L | 0.41700504 | **0.42631943** | 0.42631943 | 1.82e-09 |
| rho*_R | 0.53227928 | **0.26557371** | 0.26557361 | 1.02e-07 |
| x_contact | 0.555631 | **0.685491** | 0.68549052 | 4.01e-09 |
| x_shock | 0.574392 | **0.850431** | 0.85043110 | 4.64e-08 |

### 4.2 波系位置验证

- 左稀疏波头 x_head = 0.263357 (正确)
- 左稀疏波尾 x_tail = 0.485945 (正确)
- 接触间断 x_contact = 0.685491 (正确)
- 激波位置 x_shock = 0.850431 (正确)

### 4.3 数值解vs精确解

修复后，数值解与精确解的对比图显示：
- 密度：精确解正确显示接触间断跳变 (0.426 → 0.266)
- 速度：精确解正确显示平台值 u* ≈ 0.927
- 压力：精确解正确显示平台值 p* ≈ 0.303

---

## 5. 文献依据

所有公式均来自：
- **Toro, E. F. (2009).** *Riemann Solvers and Numerical Methods for Fluid Dynamics* (3rd ed.), Springer.
  - 式4.46: pressure_function (p*求解方程)
  - 式4.47: u*计算公式
  - 式4.54: 激波速度S_R计算

- **Sod, G. A. (1977).** A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. *JCP*, 27(1), 1-31.

---

## 6. 结论

**根因**: `utils.py` 中的 `sod_exact_solution()` 函数在激波分支中错误地将乘法写成了除法，导致 p* 和 u* 计算值严重偏离理论值。

**影响**: 所有使用 `utils.sod_exact_solution()` 的图表（网格收敛性图、CFL影响图、波系验证图等）和误差计算均受影响。

**修复**: 将3处错误的除法公式更正为乘法公式，与 Toro (2009) 式4.46-4.47 完全一致。

**验证**: 修复后精确解所有关键参数与理论值误差 < 1e-7，完全通过验证。
