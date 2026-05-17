# 第三方组件开源声明

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.5.1 |
| 发布日期 | 2026-05-16 |
| 项目版本 | v1.5.1 |
| 文档编号 | THIRD-PARTY-NOTICE-001 |

---

## 声明

本软件（Sod Shock Tube CFD v1.5.1）在开发过程中使用了以下第三方开源组件。本文件根据各第三方组件的许可证要求，向其版权所有者致谢，并提供许可证全文的获取方式。

> **重要提示**: 使用本软件即表示您同意遵守以下所有第三方组件的许可证条款。本软件本身以 MIT 许可证发布（参见 `LICENSE` 文件），但各第三方组件保持其各自的许可证。

---

## 第三方组件清单

### 1. NumPy

| 属性 | 内容 |
|------|------|
| **组件名称** | NumPy (Numerical Python) |
| **使用版本** | >=1.21.0, <2.0.0 |
| **许可证类型** | BSD-3-Clause |
| **SPDX 标识符** | BSD-3-Clause |
| **版权所有者** | NumPy Developers (2005-2024) |
| **用途** | 提供高效的多维数组对象、线性代数运算、数学函数，是本项目数值计算的核心基础库 |
| **官方网站** | https://numpy.org/ |
| **源代码仓库** | https://github.com/numpy/numpy |
| **许可证全文** | https://github.com/numpy/numpy/blob/main/LICENSE.txt |

**BSD-3-Clause 许可证核心条款**：
- 允许源代码和二进制形式的再分发和使用（无论是否修改）
- 再分发时必须保留版权声明、条件列表和免责声明
- 未经许可不得使用版权所有者名称进行背书

---

### 2. SciPy

| 属性 | 内容 |
|------|------|
| **组件名称** | SciPy (Scientific Python) |
| **使用版本** | >=1.7.0 |
| **许可证类型** | BSD-3-Clause |
| **SPDX 标识符** | BSD-3-Clause |
| **版权所有者** | SciPy Developers (2001-2024) |
| **用途** | 提供科学计算工具，本项目主要使用 `scipy.optimize.brentq` 函数进行 Riemann 精确解求解中的迭代求根 |
| **官方网站** | https://scipy.org/ |
| **源代码仓库** | https://github.com/scipy/scipy |
| **许可证全文** | https://github.com/scipy/scipy/blob/main/LICENSE.txt |

**备注**：SciPy 的 `brentq` 函数实现了 Brent 的求根算法（Brent 1973），是 Riemann 精确解求解器的关键依赖。

---

### 3. Matplotlib

| 属性 | 内容 |
|------|------|
| **组件名称** | Matplotlib |
| **使用版本** | >=3.5.0 |
| **许可证类型** | PSF-based (Python Software Foundation License 衍生) |
| **版权所有者** | Matplotlib Development Team (2002-2024) |
| **用途** | 提供数据可视化功能，用于生成密度/速度/压力对比图、叠加对比图等仿真结果图像 |
| **官方网站** | https://matplotlib.org/ |
| **源代码仓库** | https://github.com/matplotlib/matplotlib |
| **许可证全文** | https://matplotlib.org/stable/users/project/license.html |

**PSF 许可证核心条款**：
- 基于 Python Software Foundation License
- 允许自由使用、修改和分发
- 要求保留版权声明和免责声明

---

### 4. PyYAML

| 属性 | 内容 |
|------|------|
| **组件名称** | PyYAML (Python YAML Parser) |
| **使用版本** | >=6.0 |
| **许可证类型** | MIT |
| **SPDX 标识符** | MIT |
| **版权所有者** | Kirill Simonov (2006-2024) |
| **用途** | 解析 YAML 格式的仿真配置文件（`config/simulation_config.yaml`） |
| **官方网站** | https://pyyaml.org/ |
| **源代码仓库** | https://github.com/yaml/pyyaml |
| **许可证全文** | https://github.com/yaml/pyyaml/blob/main/LICENSE |

---

### 5. pytest

| 属性 | 内容 |
|------|------|
| **组件名称** | pytest |
| **使用版本** | >=7.0.0 |
| **许可证类型** | MIT |
| **SPDX 标识符** | MIT |
| **版权所有者** | Holger Krekel and pytest-dev team (2004-2024) |
| **用途** | 单元测试框架，用于自动运行 39 项测试用例（可选依赖，非运行时必需） |
| **官方网站** | https://pytest.org/ |
| **源代码仓库** | https://github.com/pytest-dev/pytest |
| **许可证全文** | https://github.com/pytest-dev/pytest/blob/main/LICENSE |

**备注**：pytest 为可选开发依赖，不影响本软件的正常运行。

---

### 6. flake8

| 属性 | 内容 |
|------|------|
| **组件名称** | flake8 |
| **使用版本** | >=5.0.0 |
| **许可证类型** | MIT |
| **SPDX 标识符** | MIT |
| **版权所有者** | flake8 Contributors (2011-2024) |
| **用途** | 代码风格检查工具，用于 CI 工作流中的代码质量保证（可选依赖，非运行时必需） |
| **官方网站** | https://flake8.pycqa.org/ |
| **源代码仓库** | https://github.com/PyCQA/flake8 |
| **许可证全文** | https://github.com/PyCQA/flake8/blob/main/LICENSE |

**备注**：flake8 为可选开发依赖，不影响本软件的正常运行。

---

## 许可证兼容性总览

| 第三方组件 | 许可证 | 与本项目 MIT 的兼容性 |
|-----------|:------:|:-------------------:|
| NumPy | BSD-3-Clause | **兼容** |
| SciPy | BSD-3-Clause | **兼容** |
| Matplotlib | PSF-based | **兼容** |
| PyYAML | MIT | **完全兼容** |
| pytest | MIT | **完全兼容** |
| flake8 | MIT | **完全兼容** |

所有第三方依赖均采用与 MIT 相兼容的宽松型开源许可证，无 GPL/LGPL/AGPL 等 Copyleft 型许可证依赖。

---

## 第三方组件未修改声明

本项目通过 Python 包管理工具（pip）以依赖方式引用上述第三方组件，**未对这些组件的源代码进行任何修改**。

组件的实际安装版本取决于用户环境中 pip 解析的最新兼容版本（在版本约束范围内）。

---

## 致谢

本项目开发者对以下开源项目和社区表示衷心感谢：

- **NumPy 团队**：提供了高性能的数值计算基础设施
- **SciPy 团队**：提供了可靠的科学计算算法
- **Matplotlib 团队**：提供了强大的数据可视化工具
- **PyYAML 维护者**：提供了稳定的配置文件解析方案
- **pytest 团队**：提供了高效的测试框架
- **flake8 团队**：提供了代码质量保障工具

没有这些开源项目的贡献，本项目的开发将变得极为困难。我们遵循开源社区的精神，以 MIT 许可证回馈社区。

---

## 获取完整许可证文本

各第三方组件的完整许可证文本可通过以下方式获取：

1. **在线查看**: 参见上表中各组件对应的"许可证全文"链接
2. **本地查看**: 安装后在 Python 环境的 `site-packages/<package>/` 目录下查找 LICENSE 或 COPYING 文件

例如：

```bash
# 查看 NumPy 许可证
python -c "import numpy; print(numpy.__path__[0])"
cat $(python -c "import numpy; print(numpy.__path__[0])")/LICENSE.txt
```

---

> **声明**: 本文件根据各第三方开源组件的许可证要求编制。如发现信息有误，请在 GitHub Issues 中提出修正。BSD-3-Clause 和 MIT 均为 Open Source Initiative (OSI) 批准的开源许可证。