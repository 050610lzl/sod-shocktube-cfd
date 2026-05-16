# 源代码授权说明

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.0 |
| 发布日期 | 2026-05-16 |
| 项目版本 | v1.3.0 |
| 文档编号 | SOURCE-LICENSE-001 |

---

## 1. 本项目许可证

### 1.1 MIT 许可证概要

本项目采用 **MIT 许可证**（Massachusetts Institute of Technology License）开源发布。

MIT 许可证是公认的最宽松的开源许可证之一，其核心条款如下：

**授予的权利**：
- **商业使用**: 允许将软件用于商业目的
- **分发**: 允许自由分发软件副本
- **修改**: 允许修改源代码并创建衍生作品
- **私人使用**: 允许在任何场景下使用
- **再许可**: 允许在修改后的版本中使用不同许可证

**限制条件**：
- 在软件的所有副本或实质性部分中必须包含原始版权声明和许可声明

**免责声明**：
- 软件按"原样"提供，不提供任何形式的明示或暗示担保
- 作者或版权持有人不对因使用软件而产生的任何索赔、损害或其他责任负责

### 1.2 完整许可证文本

```text
MIT License

Copyright (c) 2026 050610lzl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

完整许可证文本参见项目根目录下的 `LICENSE` 文件。

---

## 2. 第三方库许可证

本项目依赖于以下第三方 Python 库。使用本项目即表示您同意遵守这些第三方库各自的许可证条款。

### 2.1 NumPy

| 属性 | 内容 |
|------|------|
| **许可证** | BSD-3-Clause (Berkeley Software Distribution 3-Clause) |
| **版本要求** | >=1.21.0, <2.0.0 |
| **用途** | 数值计算（数组操作、线性代数、数学函数） |
| **许可证全文** | https://github.com/numpy/numpy/blob/main/LICENSE.txt |
| **版权方** | NumPy Developers |

### 2.2 SciPy

| 属性 | 内容 |
|------|------|
| **许可证** | BSD-3-Clause |
| **版本要求** | >=1.7.0 |
| **用途** | 科学计算（Brent 求根算法用于 Riemann 精确解） |
| **许可证全文** | https://github.com/scipy/scipy/blob/main/LICENSE.txt |
| **版权方** | SciPy Developers |

### 2.3 Matplotlib

| 属性 | 内容 |
|------|------|
| **许可证** | PSF-based (Python Software Foundation License 衍生) |
| **版本要求** | >=3.5.0 |
| **用途** | 数据可视化（密度/速度/压力对比图绘制） |
| **许可证全文** | https://matplotlib.org/stable/users/project/license.html |
| **版权方** | Matplotlib Development Team |

### 2.4 PyYAML

| 属性 | 内容 |
|------|------|
| **许可证** | MIT |
| **版本要求** | >=6.0 |
| **用途** | YAML 配置文件解析 |
| **许可证全文** | https://github.com/yaml/pyyaml/blob/main/LICENSE |
| **版权方** | Kirill Simonov |

### 2.5 pytest

| 属性 | 内容 |
|------|------|
| **许可证** | MIT |
| **版本要求** | >=7.0.0（可选依赖，仅开发/测试） |
| **用途** | 单元测试框架 |
| **许可证全文** | https://github.com/pytest-dev/pytest/blob/main/LICENSE |
| **版权方** | Holger Krekel and pytest-dev team |

### 2.6 flake8

| 属性 | 内容 |
|------|------|
| **许可证** | MIT |
| **版本要求** | >=5.0.0（可选依赖，仅开发） |
| **用途** | 代码风格检查 |
| **许可证全文** | https://github.com/PyCQA/flake8/blob/main/LICENSE |
| **版权方** | flake8 Contributors |

---

## 3. 许可证兼容性说明

| 本项目许可证 | 第三方库许可证 | 兼容性 |
|:-----------:|:------------:|:------:|
| MIT | BSD-3-Clause (NumPy, SciPy) | 兼容 - BSD-3-Clause 与 MIT 均为宽松型许可证 |
| MIT | PSF-based (Matplotlib) | 兼容 - PSF 许可证与 MIT 高度兼容 |
| MIT | MIT (PyYAML, pytest, flake8) | 完全兼容 - 同为 MIT 许可证 |

所有第三方依赖均使用宽松型开源许可证，与本项目的 MIT 许可证兼容，不产生许可证冲突。

---

## 4. 使用限制与免责声明

### 4.1 使用限制

1. **CFD 数值求解器性质**: 本项目是 CFD 教学/研究用数值求解器，不适用于工程安全关键场景。
2. **精度限制**: 数值解受限于有限差分法的离散误差和格式的数值耗散/色散特性，不可替代高保真 CFD 商业软件。
3. **第三方依赖**: 使用本项目需同时遵守所有第三方依赖库的许可证条款（参见第 2 节和 `docs/08_compliance/08_third_party_notice.md`）。

### 4.2 免责声明

本软件按"原样"（AS IS）提供，不提供任何形式的明示或暗示担保，包括但不限于：

- 适销性担保
- 特定用途适用性担保
- 非侵权性担保
- 数值结果准确性担保

在任何情况下，作者或版权持有人均不对因使用本软件而产生的任何索赔、损害或其他责任负责，无论是基于合同、侵权或其他法律理论。

### 4.3 学术引用

如在学术研究中使用本项目，请引用以下文献：

```
Sod Shock Tube CFD Solver v1.3.0.
https://github.com/050610lzl/sod-shocktube-cfd

Sod, G. A. (1978). A survey of several finite difference methods
for systems of nonlinear hyperbolic conservation laws.
Journal of Computational Physics, 27(1), 1-31.

Toro, E. F. (2009). Riemann Solvers and Numerical Methods for
Fluid Dynamics (3rd ed.). Springer.
```

---

## 5. 常见问题

**Q: 我可以将本项目用于商业产品吗？**

A: 可以。MIT 许可证允许商业使用，无需支付费用或获得额外许可。

**Q: 我修改了代码，需要公开我的修改吗？**

A: 不需要。MIT 许可证不要求公开修改后的源代码（与 GPL 不同）。但您需要在代码中保留原始版权声明。

**Q: 我可以在我的项目中使用本项目的部分代码吗？**

A: 可以。只需在您的项目中包含 MIT 许可证声明和原始版权信息即可。

**Q: 本项目使用的第三方库需要额外关注哪些许可证问题？**

A: 所有第三方库均使用宽松型开源许可证（BSD、MIT、PSF），对本项目的使用和分发无额外限制。详见 `docs/08_compliance/08_third_party_notice.md`。

---

> **更多信息**:
> - MIT 许可证全文: https://opensource.org/licenses/MIT
> - SPDX 标识符: MIT
> - Open Source Initiative 批准的许可证