# 编码规范文档

> 文档版本: v1.0  
> 项目: 一维Sod激波管CFD求解器 (sod-shocktube-cfd)

---

## 1. Python 代码风格

### 1.1 基础规范: PEP 8

本项目严格遵循 [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/), 并在以下方面做了项目级定制。

### 1.2 行宽

- **最大行宽**: 120 字符 (非 PEP 8 默认的 79)
- 理由: 科学计算代码常包含长公式和 NumPy 索引, 79 字符过于严格
- Flake8 配置: `--max-line-length=120`

### 1.3 缩进

- **缩进方式**: 4 个空格 (禁止 Tab)
- **续行缩进**: 与起始括号对齐 或 悬挂缩进 4 空格

```python
# 正确: 与起始括号对齐
result = some_long_function_name(arg1, arg2,
                                 arg3, arg4)

# 正确: 悬挂缩进
result = some_long_function_name(
    arg1, arg2, arg3, arg4
)

# 错误: Tab 缩进
result = some_function(arg1,  # <-- Tab 字符
        arg2)
```

### 1.4 空行

- 顶级函数/类定义之间: 2 个空行
- 类内方法定义之间: 1 个空行
- 函数内部逻辑分组之间: 1 个空行
- 文件末尾: 恰好 1 个空行, 无多余空行

### 1.5 空格

- 运算符两侧加空格: `a = b + c`, `x, y = 1, 2`
- 逗号后加空格: `[1, 2, 3]`
- 函数参数列表逗号后加空格: `f(a, b, c)`
- 索引/切片不加空格: `U[i, :]`, `x[1:-1]`
- 关键字参数不加空格: `func(arg=value)` 而非 `func(arg = value)`

### 1.6 字符串引号

- 统一使用双引号 `"..."` 用于文档字符串
- 字符串内部包含双引号时, 使用单引号 `'...'`
- 推荐 f-string 用于格式化: `f"结果: {value:.4f}"`

---

## 2. 命名规范

### 2.1 模块名 (文件名)

- **规则**: `snake_case` (全小写 + 下划线)
- **示例**: `mesh_generator.py`, `flow_initializer.py`, `boundary_handler.py`

### 2.2 类名

- **规则**: `PascalCase` (每个单词首字母大写)
- **示例**: `FD_SCHEMES` (此项目中不使用类, 仅用字典和函数)

### 2.3 函数名

- **规则**: `snake_case` (全小写 + 下划线)
- **公开函数**: 描述性动词短语
  - `generate_mesh()`, `initialize_flow()`, `compute_dt()`, `apply_boundary_condition()`
- **私有/内部函数**: 以下划线开头
  - `_riemann_flux_godunov()`, `_roe_average()`, `_hllc_flux()`, `_entropy_fix_eigenvalue()`

### 2.4 变量名

- **规则**: `snake_case`
- **循环变量**: 单字母可接受 (`i`, `j`, `k`)
- **物理量**: 使用标准记号
  - `rho` (密度), `u` (速度), `p` (压力), `c` (声速)
  - `U` (守恒变量), `F` (通量), `E` (总能)
- **避免**: 单个 `l` (易与 `1` 混淆), 单个 `O` (易与 `0` 混淆)

### 2.5 常量名

- **规则**: `UPPER_SNAKE_CASE` (全大写 + 下划线)
- **示例**: `GAMMA = 1.4`, `FD_SCHEMES = {...}`
- 全局常量和配置级别的字典使用此规则

### 2.6 命名对照表

| 类型 | 规则 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| 模块 | snake_case | `mesh_generator.py` | `MeshGenerator.py` |
| 函数 | snake_case | `compute_dt()` | `computeDt()` |
| 私有函数 | _snake_case | `_roe_average()` | `roeAverage()` |
| 变量 | snake_case | `n_points` | `nPoints` |
| 常量 | UPPER_SNAKE | `GAMMA = 1.4` | `gamma = 1.4` (模块级) |
| 字典常量 | UPPER_SNAKE | `FD_SCHEMES` | `fdSchemes` |

---

## 3. 文档字符串规范

### 3.1 规范: Google 风格

本项目采用 **Google Python Style Guide** 的文档字符串格式。

### 3.2 模块级文档字符串

```python
"""
模块名称 (src/module_name.py)
==============================
简要描述模块的核心功能。

依据: Build文档 §X.Y
文献: Author (Year) [N], Author (Year) [M]
"""
```

### 3.3 函数文档字符串

```python
def function_name(param1, param2, param3=default):
    """
    简要描述函数功能 (一行)。

    详细描述 (可选, 多行)。

    依据: Build文档 §X.Y, Author (Year) [N]

    参数:
        param1: 参数1的说明
        param2: 参数2的说明
        param3: 参数3的说明 (默认: default_value)

    返回:
        return_value: 返回值的说明

    异常:
        ValueError: 什么情况下抛出
    """
```

### 3.4 实际示例

项目中实际使用的文档字符串示例:

```python
def compute_dt(U, dx, cfl=0.8, gamma=GAMMA):
    """
    按CFL条件计算时间步长。

    依据: Build文档 §4.4, §5.5, LeVeque (1992) [5]

    公式: dt = CFL * dx / max(|u| + c)

    参数:
        U: 守恒变量数组
        dx: 网格间距
        cfl: CFL数 (默认0.8)
        gamma: 比热比

    返回:
        dt: 时间步长
    """
```

### 3.5 文献引用格式

在文档字符串中使用缩写文献标记:

| 标记 | 含义 |
|------|------|
| `[1]` | Sod (1978) -- 有限差分格式综述 |
| `[2]` | Toro (2009) -- Riemann 求解器 (第3版) |
| `[3]` | Laney (1998) -- 计算气体动力学 |
| `[4]` | OneFlow-CFD -- 在线文档 |
| `[5]` | LeVeque (1992) -- 守恒律数值方法 |
| `[7]` | Roe (1981) -- 近似 Riemann 求解器 |
| `[8]` | Toro et al. (1994) -- HLLC 格式 |

---

## 4. 导入规范

### 4.1 导入顺序

按以下三组排列, 组间用空行分隔:

```python
# 第一组: 标准库
import os
import sys
import datetime

# 第二组: 第三方库
import numpy as np
import yaml
from scipy.optimize import brentq

# 第三组: 本地模块
from .mesh_generator import generate_mesh
from .time_marcher import compute_dt
from .boundary_handler import apply_boundary_condition
```

### 4.2 导入原则

- **避免 `from module import *`**: 始终使用显式导入
- **NumPy 约定**: `import numpy as np`
- **Matplotlib 约定**: `import matplotlib.pyplot as plt`
- **避免循环导入**: 将导入放在函数内部 (`from .module import func`) 而不是模块顶层, 当模块间有交叉依赖时使用
- **`__init__.py` 导出**: 在 [src/\_\_init\_\_.py](file:///e:/trae_project/a/src/__init__.py) 中集中管理公开接口

### 4.3 `__init__.py` 的导入模式

```python
from .mesh_generator import generate_mesh
from .flow_initializer import initialize_flow
# ... 其他模块 ...

__all__ = [
    'generate_mesh',
    'initialize_flow',
    # ... 其他导出 ...
]
```

这使用户可以通过 `from src import generate_mesh` 简洁地访问核心函数。

---

## 5. 注释规范

### 5.1 何时添加注释

| 情况 | 是否注释 | 注释类型 |
|------|----------|----------|
| 复杂算法实现 | 必须 | 算法步骤说明 + 公式 |
| 非直觉的数值处理 | 必须 | 解释为何这样做 |
| 文献公式的实现 | 必须 | 标注公式出处 |
| 防御性代码 (如 `np.maximum(..., 1e-15)`) | 必须 | 解释保护目的 |
| 简单的变量赋值 | 不需要 | -- |
| 显而易见的控制流 | 不需要 | -- |

### 5.2 注释语言 (中文/英文)

- **文档字符串**: 中文 (面向中文开发团队)
- **行内注释**: 中文, 但公式和引用保持英文
- **代码 (变量/函数名)**: 英文
- **提交消息**: 英文 (Conventional Commits)

### 5.3 注释风格示例

**块注释** (用于分隔代码区域):

```python
# =============================================================================
# 格式1: Lax-Friedrichs 有限差分格式 (一阶)
# 依据: Build文档 §4.3 FDM-1, Sod (1978) [1], Laney (1998) [3]
# 离散公式:
#   U_i^{n+1} = 0.5*(U_{i+1}^n + U_{i-1}^n) - dt/(2*dx)*(F_{i+1}^n - F_{i-1}^n)
# =============================================================================
```

**行内注释** (解释数值处理):

```python
c = np.sqrt(np.maximum(gamma * p / rho, 1e-15))  # 声速, 防除零
```

**公式注释**:

```python
# 总能: E = p/((gamma-1)*rho) + 0.5*u^2  (依据: Anderson (1984) [2])
E = p / ((gamma - 1.0) * rho) + 0.5 * u ** 2
```

---

## 6. 提交规范

### 6.1 规范: Conventional Commits

本项目遵循 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) 规范。

### 6.2 提交消息格式

```
<type>(<scope>): <subject>

<body> (可选)

<footer> (可选)
```

### 6.3 Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: add HLLC Riemann solver` |
| `fix` | Bug 修复 | `fix: correct entropy fix in Roe scheme` |
| `docs` | 文档更新 | `docs: add module design specification` |
| `style` | 代码风格 (不影响功能) | `style: fix flake8 E501 line too long` |
| `refactor` | 代码重构 | `refactor: extract flux computation to helper` |
| `test` | 测试相关 | `test: add convergence test for Lax-Wendroff` |
| `chore` | 构建/工具/CI | `chore: update numpy version constraint` |
| `perf` | 性能优化 | `perf: vectorize Roe dissipation computation` |

### 6.4 提交示例

```bash
# 新功能
git commit -m "feat: add TVD-Minmod scheme with MUSCL reconstruction"

# Bug 修复
git commit -m "fix: prevent negative pressure in TVD MUSCL extrapolation"

# 文档
git commit -m "docs: create architecture design document"

# 代码风格
git commit -m "style: fix trailing whitespace and blank line issues"

# 测试
git commit -m "test: add boundary condition unit tests"

# CI
git commit -m "chore: add pytest to GitHub Actions workflow"
```

### 6.5 提交粒度

- 每次提交应该是**逻辑上原子化**的: 一个提交对应一个明确的变更
- 避免将不相关的修改混入同一提交
- 在提交前使用 `git diff --staged` 检查暂存的变更

---

## 7. 版本管理规范

### 7.1 规范: Semantic Versioning 2.0.0

本项目遵循 [SemVer 2.0.0](https://semver.org/)。

### 7.2 版本号格式

```
MAJOR.MINOR.PATCH
```

| 段 | 何时递增 | 示例 |
|----|----------|------|
| MAJOR | 不兼容的 API 变更 (修改函数签名、移除格式、改变 I/O 格式) | 1.2.0 -> 2.0.0 |
| MINOR | 向后兼容的新功能 (新增格式、新增分析工具、新增 CLI 选项) | 1.2.0 -> 1.3.0 |
| PATCH | 向后兼容的 Bug 修复 (修正数值错误、代码风格修复、性能优化) | 1.2.0 -> 1.2.1 |

### 7.3 bump_version.py 工具使用

**文件**: [bump_version.py](file:///e:/trae_project/a/bump_version.py)

```bash
# 升级修订版本号 (1.2.0 -> 1.2.1)
python bump_version.py patch

# 升级次版本号 (1.2.1 -> 1.3.0)
python bump_version.py minor

# 升级主版本号 (1.3.0 -> 2.0.0)
python bump_version.py major

# 预览操作 (不实际修改文件)
python bump_version.py patch --dry-run

# 升级并自动创建 git tag
python bump_version.py minor --tag

# 查看当前版本
python bump_version.py --show
```

### 7.4 版本号存储

- **VERSION 文件**: 位于项目根目录 [VERSION](file:///e:/trae_project/a/VERSION), 纯文本存储 (如 `1.3.0`)
- **pyproject.toml**: 同步 `project.version` 字段
- **CHANGELOG.md**: 记录每个版本的变更 (Keep a Changelog 格式)

### 7.5 Git Tag

版本升级后应创建带注释的 Git tag:

```bash
# 手动创建
git tag -a v1.3.0 -m "Release v1.3.0"

# 或使用 bump_version.py
python bump_version.py minor --tag

# 推送 tag
git push origin v1.3.0
```

---

## 8. 项目特定约定

### 8.1 数值常数

- **浮点数显式标注**: 使用 `1.0` 而非 `1`, `0.5` 而非 `.5`
- **小量**: 使用 `1e-15` 作为数值保护 (不由 `eps` 变量)
- **Gamma**: 模块级常量 `GAMMA = 1.4`

### 8.2 NumPy 数组约定

- 守恒变量 `U`: shape `(N, 3)`, dtype `float64`
- 网格坐标 `x`: shape `(N,)`, dtype `float64`
- 原始变量 `(rho, u, p)`: shape `(N,)`, 各自独立的 1-D 数组
- 切片: 使用 `U[1:-1, :]` 选取内部节点, 不使用 `U[1:N-1]`

### 8.3 文件编码

所有源文件使用 **UTF-8** 编码, 包含中文注释的文件在顶部声明:

```python
# -*- coding: utf-8 -*-
```

### 8.4 Shebang

可执行脚本 (如 `run_simulation.py`, `bump_version.py`) 首行为:

```python
#!/usr/bin/env python3
```

---

## 9. 代码审查清单

提交 Pull Request 前, 确认以下各项:

- [ ] 通过所有单元测试: `pytest tests/ -v`
- [ ] 通过 Flake8: `flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503`
- [ ] 新增代码包含文档字符串 (Google 风格)
- [ ] 更新了 `CHANGELOG.md`
- [ ] 如有 API 变更, 运行 `python bump_version.py` 更新版本号
- [ ] 提交消息符合 Conventional Commits 规范
- [ ] 无 `print()` 调试遗留 (除仿真进度报告外)
- [ ] 所有 `TODO` 注释已解决或转为 Issue

---

## 参考文献

1. PEP 8 -- Style Guide for Python Code. https://peps.python.org/pep-0008/
2. Google Python Style Guide. https://google.github.io/styleguide/pyguide.html
3. Conventional Commits 1.0.0. https://www.conventionalcommits.org/
4. Semantic Versioning 2.0.0. https://semver.org/
5. Keep a Changelog. https://keepachangelog.com/