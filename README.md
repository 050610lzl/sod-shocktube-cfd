# Sod Shock Tube CFD

[![CI](https://github.com/050610lzl/sod-shocktube-cfd/actions/workflows/ci.yml/badge.svg)](https://github.com/050610lzl/sod-shocktube-cfd/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.6.0-brightgreen)](VERSION)

一维 Sod 激波管 CFD 求解器，基于有限差分法 (FDM) 实现 **9 种**经典数值格式，用于求解欧拉方程（可压缩无粘流体），并与 Riemann 精确解进行定量对比验证。

## 项目背景

Sod 激波管问题是计算流体力学 (CFD) 中的经典基准测试，由 Sod (1978) 提出。它模拟一个充满静止气体的管道，中间由隔膜分隔为高压区和低压区。隔膜破裂后，产生向右传播的激波、向左传播的稀疏波以及它们之间的接触间断。

### Sod 标准工况

| 物理量 | 左态 (高压区) | 右态 (低压区) |
|--------|-------------|-------------|
| 密度 ρ | 1.0 | 0.125 |
| 速度 u | 0.0 | 0.0 |
| 压力 p | 1.0 | 0.1 |

- 计算域: x ∈ [0, 1]
- 隔膜位置: x = 0.5
- 比热比: γ = 1.4
- 仿真时间: t = 0.2
- CFL 数: 0.8

---

## 快速开始

### 环境要求

- Python 3.9+ 
- pip

### 安装

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
pip install -e ".[test,dev]"
```

### 运行仿真

```bash
# 使用默认配置运行全部 9 种格式
python run_simulation.py

# 指定网格分辨率
python run_simulation.py --n_points 200

# 运行单个格式
python run_simulation.py --scheme upwind

# 运行多个格式
python run_simulation.py --schemes lax_friedrichs upwind roe

# 指定边界条件类型 (v1.5.0+)
python run_simulation.py --bc reflective

# 自定义初始条件 (v1.5.0+)
python run_simulation.py --left_rho 2.0 --left_p 2.0 --right_rho 0.25 --right_p 0.2
```

### 运行测试

```bash
python -m pytest tests/ -v
```

---

## 数值格式

| 序号 | 格式 | 精度 | 类型 | CLI 参数 | 文献 |
|------|------|------|------|----------|------|
| 1 | Lax-Friedrichs | 一阶 | 中心耗散 | `lax_friedrichs` | Sod (1978) |
| 2 | Lax-Wendroff | 二阶 | 中心色散 | `lax_wendroff` | Sod (1978) |
| 3 | MacCormack | 二阶 | 预估校正 | `macormack` | Sod (1978) |
| 4 | 一阶迎风 | 一阶 | Steger-Warming 分裂 | `upwind` | Laney (1998) |
| 5 | Rusanov | 一阶 | 局部 Lax-Friedrichs | `rusanov` | Rusanov (1961) |
| 6 | Godunov | 一阶 | 精确 Riemann 求解 | `godunov` | Godunov (1959) |
| 7 | Roe | 一阶 | 近似 Riemann 求解 | `roe` | Roe (1981) |
| 8 | HLLC | 一阶 | 恢复接触间断 | `hllc` | Toro et al. (1994) |
| 9 | TVD-Minmod | 二阶 | 通量限制高阶 | `tvd_minmod` | Harten (1983) |

---

## 边界条件

支持 4 种边界条件类型，通过 CLI 参数 `--bc` 或 YAML 配置 `boundary_type` 选择：

| 类型 | CLI 值 | 行为 | 适用场景 |
|------|--------|------|----------|
| 零梯度（默认） | `zero_gradient` | U[0]=U[1], U[-1]=U[-2] | 开放边界、Sod 标准 |
| 固壁反射 | `reflective` | 密度能量不变，速度反号 | 管道端壁 |
| 周期 | `periodic` | U[0]=U[-2], U[-1]=U[1] | 无限长管道近似 |
| 无反射透射 | `transmissive` | 二阶外推 | 波穿过边界不反射 |

---

## 自定义初始条件

支持通过 CLI 参数覆盖标准 Sod 工况的初始条件：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--left_rho` | 1.0 | 左态密度 |
| `--left_u` | 0.0 | 左态速度 |
| `--left_p` | 1.0 | 左态压力 |
| `--right_rho` | 0.125 | 右态密度 |
| `--right_u` | 0.0 | 右态速度 |
| `--right_p` | 0.1 | 右态压力 |
| `--diaphragm` | 0.5 | 隔膜位置 |

```bash
# 自定义初始条件 + 反射边界
python run_simulation.py --left_rho 5.0 --left_p 5.0 --right_rho 0.5 --right_p 0.5 --bc periodic
```

---

## 项目结构

```
sod-shocktube-cfd/
├── src/                          # 核心求解器源码
│   ├── mesh_generator.py         # 一维均匀网格生成
│   ├── flow_initializer.py       # Sod 初始条件赋值
│   ├── fd_schemes.py             # 9 种有限差分格式
│   ├── boundary_handler.py       # 多种边界条件 (4种类型)
│   ├── time_marcher.py           # CFL 时间步长推进
│   ├── exact_solver.py           # Riemann 精确解 (Toro 2009)
│   ├── output_writer.py          # 结果数据输出
│   └── validator.py              # 误差计算与可视化
├── tests/                        # 单元测试 (39 项)
│   ├── test_mesh.py
│   ├── test_initialization.py
│   ├── test_boundary.py
│   └── test_fd_schemes.py
├── config/
│   └── simulation_config.yaml    # 仿真参数配置
├── docs/                         # 项目文档与结果图片
├── results/                      # 仿真结果归档
├── .github/workflows/ci.yml      # CI 持续集成
├── pyproject.toml                # Python 包配置 (PEP 517/518/621)
├── run_simulation.py             # 主程序入口
├── bump_version.py               # 版本号管理工具
├── VERSION                       # 当前版本号
├── LICENSE                       # MIT 开源许可证
├── CHANGELOG.md                  # 版本变更日志
├── CONTRIBUTING.md               # 贡献指南
└── README.md                     # 本文件
```

---

## 配置文件

编辑 `config/simulation_config.yaml`:

```yaml
mesh:
  n_points: 100
  x_left: 0.0
  x_right: 1.0

physics:
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state: {rho: 1.0, u: 0.0, p: 1.0}
  right_state: {rho: 0.125, u: 0.0, p: 0.1}

simulation:
  t_final: 0.2
  cfl: 0.8
  boundary_type: zero_gradient  # 边界条件类型

schemes:
  - lax_friedrichs
  - lax_wendroff
  - macormack
  - upwind
  - rusanov
  - godunov
  - roe
  - hllc
  - tvd_minmod
```

---

## 验证方法

### 误差评估

对每种数值格式计算三种误差范数：

- **L₁ 误差**: 平均绝对误差
- **L₂ 误差**: 均方根误差  
- **L∞ 误差**: 最大绝对误差

分别对密度 (ρ)、速度 (u)、压力 (p) 进行评估。

### 收敛性测试

通过改变网格节点数 (N=50, 100, 200, 400) 验证数值格式的理论收敛阶：

- 一阶格式 (Lax-Friedrichs, 迎风, Rusanov, Godunov, Roe, HLLC): O(h)
- 二阶格式 (Lax-Wendroff, MacCormack, TVD-Minmod): O(h²)

---

## 版本管理

本项目遵循 [语义化版本规范 (SemVer 2.0.0)](https://semver.org/):

| 版本段 | 触发条件 |
|--------|----------|
| MAJOR | 不兼容的 API 变更 |
| MINOR | 向后兼容的新功能 |
| PATCH | Bug 修复与性能优化 |

```bash
python bump_version.py --show   # 查看当前版本
python bump_version.py patch    # 升级修订版本
python bump_version.py minor    # 升级次版本
python bump_version.py major    # 升级主版本
python bump_version.py patch --tag  # 升级并创建 git tag
```

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 参考文献

[1] Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. *Journal of Computational Physics*, 27(1), 1-31.

[2] Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.

[3] Laney, C. B. (1998). Computational Gasdynamics. Cambridge University Press.

[4] Anderson, J. D. (1984). Modern Compressible Flow: With Historical Perspective. McGraw-Hill.

[5] LeVeque, R. J. (1992). Numerical Methods for Conservation Laws. Birkhäuser.

[6] Roe, P. L. (1981). Approximate Riemann solvers, parameter vectors, and difference schemes. *Journal of Computational Physics*, 43(2), 357-372.

[7] Harten, A. (1983). High resolution schemes for hyperbolic conservation laws. *Journal of Computational Physics*, 49(3), 357-393.

[8] OneFlow-CFD Documentation. Sod's shock-tube problem. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html

---

## License

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。