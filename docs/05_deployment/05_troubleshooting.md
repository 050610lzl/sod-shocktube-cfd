# 故障排查手册

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.0 |
| 发布日期 | 2026-05-16 |
| 适用版本 | v1.3.0 |
| 文档编号 | TROUBLE-001 |

---

## 问题索引

| 编号 | 问题 | 严重程度 |
|------|------|---------|
| TS-01 | ImportError: No module named 'src' | 高 |
| TS-02 | numpy 版本不兼容 | 高 |
| TS-03 | 负密度/负压力崩溃 | 严重 |
| TS-04 | matplotlib 中文乱码 | 中 |
| TS-05 | Git 推送失败 | 中 |
| TS-06 | CI 失败排查 | 中 |
| TS-07 | CFL 条件违反导致发散 | 严重 |
| TS-08 | 接触间断过于模糊 | 低 |
| TS-09 | 激波附近数值振荡 | 中 |
| TS-10 | 仿真时间过长 | 低 |
| TS-11 | YAML 配置文件解析错误 | 中 |
| TS-12 | pytest 测试找不到模块 | 中 |
| TS-13 | 内存溢出 | 低 |
| TS-14 | matplotlib 图形保存失败 | 低 |
| TS-15 | 时间戳归档冲突 | 低 |
| TS-16 | scipy.brentq 收敛失败 | 中 |

---

## TS-01: ImportError: No module named 'src'

### 症状

```python
ModuleNotFoundError: No module named 'src'
```

在运行 `python run_simulation.py` 或 `python main.py` 时出现。

### 根因

Python 解释器找不到 `src` 包的路径。主要有以下可能原因：

1. **未以可编辑模式安装**: 未执行 `pip install -e .`，导致 `src` 包未注册到 Python 路径
2. **当前工作目录错误**: 未在项目根目录下运行脚本
3. **虚拟环境未激活**: 安装到了系统 Python 而非虚拟环境
4. **PYTHONPATH 未设置**: 使用 ide 或非标准方式运行时路径缺失

### 解决方案

**方案 A: 安装项目包（推荐）**

```bash
cd /path/to/sod-shocktube-cfd
pip install -e .
python run_simulation.py  # 正常运行
```

**方案 B: 手动设置 PYTHONPATH**

```bash
# Linux/macOS
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python run_simulation.py

# Windows PowerShell
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
python run_simulation.py
```

**方案 C: 在脚本中添加路径（不推荐，仅应急）**

在脚本开头添加：

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### 预防措施

- 始终使用 `pip install -e .` 安装项目
- 使用虚拟环境隔离依赖
- 在项目 README 中明确启动方式
- CI 流程中验证安装步骤

---

## TS-02: numpy 版本不兼容

### 症状

```python
AttributeError: module 'numpy' has no attribute '...'
# 或
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.0.0
```

### 根因

本项目严格要求 `numpy>=1.21.0,<2.0.0`（参见 `pyproject.toml` 和 `requirements.txt`）。NumPy 2.0.0 引入了大量 Breaking Changes，导致本项目（基于 NumPy 1.x API）无法正常运行。

具体原因：
1. NumPy 2.0 移除了多项已弃用的 API
2. NumPy 2.0 改变了默认数据类型提升规则
3. 部分标量属性被移除（如 `np.float` 改为 `np.float64`）

### 解决方案

**方案 A: 降级 numpy（推荐）**

```bash
pip install "numpy>=1.21.0,<2.0.0"
```

**方案 B: 从 requirements.txt 安装**

```bash
pip install -r requirements.txt
```

**方案 C: 检查当前版本**

```bash
python -c "import numpy; print(numpy.__version__)"
```

### 预防措施

- 始终通过 `requirements.txt` 或 `pyproject.toml` 安装依赖
- CI 流程中锁定 numpy 版本范围
- 未来版本（v2.0.0+）计划支持 NumPy 2.0

---

## TS-03: 负密度/负压力崩溃

### 症状

```python
RuntimeWarning: invalid value encountered in sqrt
# 或
AssertionError: Negative pressure detected!
# 或
ValueError: Negative density at cell i=XX
```

仿真运行过程中，密度或压力计算出负值，导致声速 `c = sqrt(gamma*p/rho)` 计算失败。

### 根因

| 原因 | 详细说明 |
|------|----------|
| **CFL 过大** | CFL 数超过稳定性极限（通常 > 1.0），显式格式发散 |
| **网格过粗** | 网格分辨率不足以解析激波结构，导致数值振荡放大 |
| **初始间断过于剧烈** | 压力比过大（PL/PR > 10），部分格式无法稳定处理 |
| **边界处理不当** | 边界外推实现有误，引入非物理波反射 |
| **格式本身限制** | Lax-Wendroff 和 MacCormack 在强间断处产生振荡，可能导致负值 |

### 解决方案

**方案 A: 降低 CFL 数**

```bash
# 将 CFL 从 0.8 降低到 0.5
python run_simulation.py --cfl 0.5 --scheme lax_wendroff
```

**方案 B: 增加网格分辨率**

```bash
# 从 N=100 增加到 N=200
python run_simulation.py --n_points 200 --cfl 0.8 --scheme macormack
```

**方案 C: 使用更稳定的格式**

```bash
# Lax-Friedrichs、Rusanov、Godunov 具有较强的数值耗散，更稳定
python run_simulation.py --scheme lax_friedrichs
python run_simulation.py --scheme rusanov
python run_simulation.py --scheme godunov
```

**方案 D: 检查初始条件**

确保初始条件符合标准 Sod 问题定义（来自 Sod 1978）：

```yaml
physics:
  left_state:
    rho: 1.0
    u: 0.0
    p: 1.0
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
```

### 预防措施

- CFL 数默认设为 0.8（为安全值）
- 在 `src/boundary_handler.py` 中添加防守性编程检查
- CI 流程中包含 CFL 稳定性检查步骤
- 使用一阶格式（Lax-Friedrichs、Rusanov、Godunov、Roe、HLLC）进行初步验证

---

## TS-04: matplotlib 中文乱码

### 症状

对比图中中文字符（标题、轴标签）显示为方框或乱码。

### 根因

系统中缺少中文字体，或 matplotlib 未正确配置字体回退方案。

### 解决方案

**方案 A: 安装中文字体（Linux）**

```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# CentOS/RHEL
sudo yum install wqy-microhei-fonts wqy-zenhei-fonts
```

**方案 B: 在代码中设置字体**

在绘图脚本中添加：

```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

**方案 C: 修改 matplotlibrc 配置文件**

在 `~/.matplotlib/matplotlibrc` 中添加：

```
font.sans-serif: SimHei, WenQuanYi Micro Hei, DejaVu Sans
axes.unicode_minus: False
```

### 预防措施

- 项目默认使用英文标签（无需中文字体）
- 在 validator.py 中已配置字体回退方案

---

## TS-05: Git 推送失败

### 症状

```bash
fatal: unable to access 'https://github.com/050610lzl/sod-shocktube-cfd.git/':
  The requested URL returned error: 403
# 或
remote: Permission to 050610lzl/sod-shocktube-cfd.git denied to <user>
# 或
fatal: Authentication failed
```

### 根因

| 原因 | 说明 |
|------|------|
| 未配置 GitHub 认证 | 需要 Personal Access Token 或 SSH Key |
| Token 过期 | GitHub 的 Personal Access Token 有有效期限制 |
| 无仓库写入权限 | 不是仓库的 Collaborator |
| 远程 URL 配置错误 | 使用了错误的远程仓库地址 |
| 网络代理问题 | 企业网络代理阻止 Git 连接 |

### 解决方案

**方案 A: 配置 Personal Access Token**

```bash
# 1. 在 GitHub Settings > Developer settings > Personal access tokens 生成 Token
# 2. 使用 Token 作为密码
git remote set-url origin https://<TOKEN>@github.com/050610lzl/sod-shocktube-cfd.git
git push origin master
```

**方案 B: 配置 SSH Key**

```bash
# 1. 生成 SSH Key
ssh-keygen -t ed25519 -C "your@email.com"

# 2. 将公钥添加到 GitHub Settings > SSH and GPG keys

# 3. 使用 SSH URL
git remote set-url origin git@github.com:050610lzl/sod-shocktube-cfd.git
git push origin master
```

**方案 C: 检查远程仓库配置**

```bash
# 查看当前远程 URL
git remote -v

# 测试连接
ssh -T git@github.com
```

### 预防措施

- 首次克隆时使用 SSH 协议
- 定期检查 Token 有效期
- 使用 Git Credential Manager 存储凭据

---

## TS-06: CI 失败排查

### 症状

GitHub Actions CI 工作流显示红色叉号（Failed）。

### 根因

CI 工作流包含多个 Job，任一 Job 失败都会导致整体标记为失败。

### 解决方案

**步骤 1: 定位失败 Job**

访问 `https://github.com/050610lzl/sod-shocktube-cfd/actions`，点击失败的运行记录。

**步骤 2: 分析日志**

| Job 名称 | 常见失败原因 | 排除方法 |
|----------|-------------|---------|
| `test` | 单元测试失败 | 查看 `Run unit tests` 步骤的详细输出 |
| `test` | CFL 检查失败（负密度/压力） | 检查 fmt 格式是否正确实现了边界条件 |
| `lint` | flake8 代码风格检查失败 | 运行 `flake8 src/ --max-line-length=120` 本地检查 |
| `integration` | 集成测试失败 | 检查某格式是否产生了非物理值 |
| `Verify version` | VERSION 文件格式错误 | 确保格式为 `MAJOR.MINOR.PATCH`（如 `1.3.0`） |

**步骤 3: 本地复现**

```bash
# 本地运行所有 CI 检查
python -m pytest tests/ -v --tb=short
flake8 src/ --max-line-length=120 --ignore=E501,W503,W504

# 运行集成测试
python -c "
import sys, numpy as np
sys.path.insert(0, '.')
from src.mesh_generator import generate_mesh
from src.flow_initializer import initialize_flow
from src.boundary_handler import apply_boundary_condition
from src.time_marcher import compute_dt
from src.fd_schemes import lax_friedrichs_step

x, dx = generate_mesh(n_points=100)
U = initialize_flow(x)
t, t_final = 0.0, 0.2
while t < t_final:
    dt = compute_dt(U, dx, cfl=0.8)
    if t + dt > t_final:
        dt = t_final - t
    U = lax_friedrichs_step(U, dx, dt)
    U = apply_boundary_condition(U)
    t += dt
rho = U[:, 0]
p = (1.4 - 1.0) * (U[:, 2] - 0.5 * U[:, 1]**2 / rho)
assert np.all(rho > 0) and np.all(p > 0), 'FAILED'
print('PASSED')
"
```

### 预防措施

- 提交前本地运行 `pytest tests/` 和 flake8 检查
- 使用 `pre-commit` 钩子自动检查
- 参考 CI 配置文件 `.github/workflows/ci.yml` 了解完整流程

---

## TS-07: CFL 条件违反导致发散

### 症状

仿真数值迅速增大到 `inf` 或 `nan`，通常在十几步内出现。

### 根因

CFL 条件要求 `CFL = max(|u|+c) * dt / dx <= 1.0`。本项目中：

- 一阶格式理论 CFL 上限为 1.0
- 二阶格式（Lax-Wendroff、MacCormack、TVD）实际稳定范围更窄（约 0.8）
- 如果 CFL 设置过高，格式数值不稳定性会迅速放大误差

### 解决方案

```bash
# 使用更保守的 CFL 值
python run_simulation.py --cfl 0.5

# 或修改配置文件
# config/simulation_config.yaml
simulation:
  cfl: 0.5
```

### 预防措施

- 默认 CFL 设为 0.8（已考虑安全余量）
- 在 `src/time_marcher.py` 中 `compute_dt` 函数已按 CFL 条件计算时间步长

---

## TS-08: 接触间断过于模糊

### 症状

密度对比图中，x=0.7 附近的接触间断过渡区域过宽（超过 10 个网格点）。

### 根因

- 一阶格式（Lax-Friedrichs、迎风、Rusanov）含大量数值耗散，会抹平接触间断
- 网格过粗也会导致接触间断分辨率下降

### 解决方案

| 方法 | 命令 |
|------|------|
| 使用高阶格式 | `python run_simulation.py --scheme tvd_minmod` |
| 使用 HLLC 格式 | `python run_simulation.py --scheme hllc` |
| 增加网格 | `python run_simulation.py --n_points 400 --scheme lax_friedrichs` |

### 预防措施

- 这是已知的数值行为，参考文献 Sod (1978), Toro (2009) 中已有讨论
- 对接触间断分辨率有要求时使用 HLLC 或 TVD 格式

---

## TS-09: 激波附近数值振荡

### 症状

密度分布图在 x=0.85（激波位置）附近出现锯齿状振荡。

### 根因

二阶格式（Lax-Wendroff、MacCormack）在间断附近不具备 TVD 性质，会产生 Gibbs 振荡。

### 解决方案

- 使用 TVD-Minmod 格式（无振荡的二阶精度）
- 或使用一阶格式（无振荡但分辨率低）

```bash
python run_simulation.py --scheme tvd_minmod
```

### 预防措施

- 在 validator.py 中添加振荡检测
- 文档中明确各格式的振荡特性

---

## TS-10: 仿真时间过长

### 症状

运行 `run_simulation.py` 全部 9 种格式耗时超过 5 分钟。

### 根因

- 网格分辨率过高（N > 400）
- 同时运行 9 种格式
- 精确 Riemann 求解器格式（Godunov）计算量大
- 计算机性能不足

### 解决方案

```bash
# 降低网格分辨率
python run_simulation.py --n_points 100

# 仅运行单个格式
python run_simulation.py --scheme upwind

# 使用快速格式（跳过 Godunov）
python run_simulation.py --schemes lax_friedrichs upwind rusanov
```

### 性能参考

| 格式 | N=100 耗时 | N=400 耗时 |
|------|-----------|-----------|
| Lax-Friedrichs | ~2秒 | ~10秒 |
| Godunov | ~5秒 | ~30秒 |
| TVD-Minmod | ~3秒 | ~15秒 |

### 预防措施

- 日常开发使用 N=100
- 最终验证使用 N=400
- 利用时间戳归档机制避免重复计算

---

## TS-11: YAML 配置文件解析错误

### 症状

```python
yaml.parser.ParserError: while parsing a block mapping
# 或
KeyError: 'mesh'
```

### 根因

- YAML 缩进错误（YAML 对缩进敏感）
- 缺少必需的配置键
- 文件编码问题

### 解决方案

```bash
# 验证 YAML 语法
python -c "import yaml; yaml.safe_load(open('config/simulation_config.yaml'))"

# 恢复默认配置
git checkout config/simulation_config.yaml
```

### 预防措施

- 参考默认配置文件 `config/simulation_config.yaml` 的格式
- 使用 YAML 编辑器插件检查语法

---

## TS-12: pytest 测试找不到模块

### 症状

```python
ModuleNotFoundError: No module named 'src.fd_schemes'
```

### 根因

测试文件运行时 Python 路径未包含项目根目录。

### 解决方案

```bash
# 安装项目包
pip install -e .

# 或从项目根目录运行
cd /path/to/sod-shocktube-cfd
python -m pytest tests/ -v
```

---

## TS-13: 内存溢出

### 症状

仿真运行到一半被系统终止，或内存使用率持续上升。

### 根因

通常发生在极端高分辨率（N > 10000）时，但这在常规使用中不会发生。

### 解决方案

```bash
python run_simulation.py --n_points 1000  # 使用合理分辨率
```

---

## TS-14: matplotlib 图形保存失败

### 症状

```python
FileNotFoundError: [Errno 2] No such file or directory: 'results/figures/...'
```

### 根因

目标目录不存在，或磁盘空间不足。

### 解决方案

```bash
mkdir -p results/figures
python run_simulation.py
```

---

## TS-15: 时间戳归档冲突

### 症状

同一秒内运行两次，数据被覆盖。

### 根因

时间戳精度到秒，一秒内运行两次会产生同一时间戳。

### 解决方案

等待至少 1 秒后重新运行，或手动指定时间戳。

实际上，代码中使用 `datetime.datetime.now()` 格式，精度到秒。一秒内连续运行两次是非常罕见的情况。

---

## TS-16: scipy.brentq 收敛失败

### 症状

```python
RuntimeError: Failed to converge after 100 iterations.
```

### 根因

Riemann 精确解求解器（`src/exact_solver.py`）中 Brent 求根算法未能在指定迭代次数内收敛。可能原因：
- 初始条件超出标准 Sod 问题范围
- 网格点恰好落在间断面上

### 解决方案

- 确保使用标准 Sod 初始条件
- 增加网格分辨率以减少间断面上网格点的采样问题

```bash
python run_simulation.py --n_points 200
```

---

## 附录 A: 诊断信息收集

当遇到无法自行解决的问题时，请收集以下信息提交 Issue：

```bash
# 1. Python 版本
python --version

# 2. 依赖版本
pip list | grep -E "numpy|scipy|matplotlib|pyyaml|pytest"

# 3. 操作系统
python -c "import platform; print(platform.platform())"

# 4. 错误复现命令
echo "python run_simulation.py --n_points 100 --scheme xxx"

# 5. 完整错误输出
python run_simulation.py --n_points 100 --scheme xxx 2>&1 | tee error.log
```

---

## 附录 B: 快速诊断流程图

```
仿真失败
  ├── ImportError? → TS-01 (PYTHONPATH)
  ├── numpy 错误? → TS-02 (版本兼容)
  ├── 负值/NaN? → TS-03 (CFL/网格), TS-07 (CFL 稳定性)
  ├── 中文乱码? → TS-04 (字体)
  ├── Git 推送失败? → TS-05 (认证)
  ├── CI 失败? → TS-06 (查看日志)
  ├── 仿真太慢? → TS-10 (性能)
  └── 其他? → 收集诊断信息(附录A) 提交 Issue
```

---

> **参考文献**:
> - Sod, G. A. (1978). JCP, 27(1), 1-31.
> - Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.
> - Python Packaging Authority. (2023). https://packaging.python.org/