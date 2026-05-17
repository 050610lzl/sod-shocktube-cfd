# 常见问题 FAQ

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.1 |
| 发布日期 | 2026-05-17 |
| 适用版本 | v1.5.1 |
| 文档编号 | FAQ-001 |

---

## 基础概念

### FAQ-01: 什么是 Sod 激波管？

**答**: Sod 激波管是计算流体力学（CFD）中最经典的验证基准问题之一，由 Gary A. Sod 于 1978 年提出。它模拟一根管道被隔膜分隔为高压区和低压区，隔膜瞬间破裂后，产生三种典型的流体动力学波系：向左传播的稀疏波、向右传播的接触间断和激波。该问题存在解析精确解（可通过 Riemann 求解器获得），因此被广泛用于检验数值格式的精度和稳定性。

**参考文献**: Sod, G. A. (1978). JCP, 27(1), 1-31.

---

### FAQ-02: 什么是 CFL 数？如何选择？

**答**: CFL（Courant-Friedrichs-Lewy）数是显式时间推进格式的稳定性条件参数，定义为：

```
CFL = max(|u| + c) * dt / dx
```

其中 u 为流速，c 为声速，dt 为时间步长，dx 为空间步长。

**选择建议**：
- **推荐值**: 0.8（平衡稳定性与效率）
- **安全值**: 0.5（调试和新格式验证时使用）
- **最大值**: 一阶格式 1.0，二阶格式约 0.9
- **不要超过 1.0**：超过后数值解会发散

**参考文献**: Anderson, J. D. (1995). Computational Fluid Dynamics. McGraw-Hill.

---

### FAQ-03: 9 种数值格式中哪个最好？

**答**: "最好"取决于评价标准：

| 评价标准 | 最佳格式 |
|----------|----------|
| 激波锐利度 | TVD-Minmod |
| 接触间断分辨率 | HLLC |
| 无振荡 | Lax-Friedrichs, Rusanov, 迎风, Godunov, Roe, HLLC |
| 计算速度 | Lax-Friedrichs（最简单） |
| 总体精度（光滑区） | TVD-Minmod（二阶） |
| 综合推荐 | TVD-Minmod（无振荡 + 高精度） |
| 学术参考 | Roe（CFD 领域经典） |

**参考文献**: Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.

---

### FAQ-04: 为什么需要精确解对比？

**答**: 精确解对比是 CFD 验证（Verification）的核心环节：
1. 确保代码实现正确（代码验证）
2. 定量评估数值误差大小
3. 评估不同格式在激波、接触间断、稀疏波处的表现差异
4. 研究网格收敛性（随网格加密误差减小）

**参考文献**: ASME V&V 20-2009. Standard for Verification and Validation in CFD.

---

## 使用操作

### FAQ-05: 如何修改初始条件？

**答**: 有三种方式：

**方式 A: 修改配置文件**（推荐）

编辑 `config/simulation_config.yaml`：

```yaml
physics:
  left_state:
    rho: 1.0    # 修改左态密度
    u: 0.0      # 修改左态速度
    p: 2.0      # 修改左态压力（增大压力比）
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
```

**方式 B: 命令行参数**（v1.5.1 新增）

```bash
# 直接通过 CLI 覆盖初始条件，无需修改 YAML
python run_simulation.py --left_rho 1.0 --left_u 0.0 --left_p 5.0 \
    --right_rho 0.125 --right_u 0.0 --right_p 0.1 \
    --diaphragm 0.5 --cfl 0.5
```

可用的 CLI 参数：`--left_rho`, `--left_u`, `--left_p`, `--right_rho`, `--right_u`, `--right_p`, `--diaphragm`

**方式 C: 编程接口**

```python
from src.flow_initializer import initialize_flow

U0 = initialize_flow(
    x,
    gamma=1.4,
    left_state={'rho': 1.0, 'u': 0.0, 'p': 2.0},
    right_state={'rho': 0.125, 'u': 0.0, 'p': 0.1}
)
```

> **注意**: 修改初始条件后建议适当降低 CFL 数以防发散。

---

### FAQ-06: 如何增加网格分辨率？

**答**: 通过命令行参数或配置文件：

```bash
# 命令行方式
python run_simulation.py --n_points 400

# 配置文件方式
# 编辑 config/simulation_config.yaml:
# mesh:
#   n_points: 400
```

**推荐分辨率**：
- N=100: 日常开发
- N=200: 精度验证
- N=400: 最终报告
- N=800: 收敛性研究

---

### FAQ-07: 如何仅运行某一种格式？

**答**:

```bash
# 方式 A: 使用 --scheme 参数
python run_simulation.py --scheme roe

# 方式 B: 使用 --schemes 参数
python run_simulation.py --schemes roe

# 方式 C: 修改配置文件 schemes 列表
# config/simulation_config.yaml:
# schemes:
#   - roe
```

---

### FAQ-08: 如何批量运行多种配置？

**答**: 编写简单的脚本循环：

```bash
# Linux/macOS
#!/bin/bash
for N in 50 100 200 400; do
    for scheme in lax_friedrichs roe hllc tvd_minmod; do
        python run_simulation.py --n_points $N --scheme $scheme
    done
done
```

```powershell
# Windows PowerShell
foreach ($N in @(50, 100, 200, 400)) {
    foreach ($scheme in @("lax_friedrichs", "roe", "hllc", "tvd_minmod")) {
        python run_simulation.py --n_points $N --scheme $scheme
    }
}
```

---

### FAQ-09: 仿真运行太慢怎么办？

**答**: 几种加速方法：

1. **降低网格分辨率**: `--n_points 100`（从 400 降到 100，约快 8 倍）
2. **仅运行快速格式**: 跳过 Godunov（精确 Riemann 求解器最慢）
   ```bash
   python run_simulation.py --schemes lax_friedrichs upwind rusanov
   ```
3. **增大 CFL 数**: `--cfl 0.9`（但需注意稳定性）
4. **仅运行单个格式**: `--scheme upwind`

---

## 结果解读

### FAQ-10: 为什么密度图上有三个波？

**答**: Sod 激波管在 t=0.2 时刻的解包含三个特征波系：

| 波系 | 位置 x | 类型 | 密度特征 |
|------|--------|------|----------|
| 左稀疏波 | 0.15-0.45 | 膨胀扇区 | 密度平滑下降 |
| 接触间断 | ~0.58 | 密度跳变 | 密度不连续但压力/速度连续 |
| 右激波 | ~0.85 | 强间断 | 密度、压力、速度同时跳变 |

**参考文献**: Toro, E. F. (2009). Springer. Chapter 4.

---

### FAQ-11: 为什么接触间断被"抹平"了？

**答**: 这是已知的数值行为：

- **一阶格式**（Lax-Friedrichs、迎风等）含有数值耗散，注定会抹平接触间断
- **二阶格式**（Lax-Wendroff、MacCormack）在间断处会产生振荡
- **HLLC 格式**：专门设计用于恢复接触间断，效果最好
- **TVD 格式**：通过限制器在无振荡和分辨率之间平衡

**解决方法**: 使用 HLLC 格式（`--scheme hllc`）或 TVD-Minmod 格式（`--scheme tvd_minmod`）。

**参考文献**: Toro, E. F., Spruce, M., & Speares, W. (1994). Shock Waves, 4(1), 25-34.

---

### FAQ-12: 激波处为什么有振荡？

**答**: 这是二阶中心格式（Lax-Wendroff、MacCormack）的经典行为——Gibbs 现象。这些格式在光滑区精度高，但在间断处会产生非物理的过冲和下冲。

**解决方法**:
- 使用 TVD 格式（具备保单调性）
- 或使用一阶格式（无振荡但激波被抹平）

---

### FAQ-13: 误差报告中的 L1、L2、Linf 分别代表什么？

**答**: 三种误差范数定义了不同的误差度量方式：

| 范数 | 公式 | 含义 | 敏感性 |
|------|------|------|--------|
| L1 | sum(abs(num - exact)) / N | 平均绝对偏差 | 均匀权重 |
| L2 | sqrt(sum((num - exact)^2) / N) | 均方根偏差 | 惩罚大偏差 |
| Linf | max(abs(num - exact)) | 最大局部偏差 | 仅关注最差一点 |

**L1 适用于整体精度评估，Linf 适用于激波位置精度评估。**

---

## 配置与定制

### FAQ-14: 如何修改仿真终止时间？

**答**:

```bash
# 命令行
python run_simulation.py  # 无法直接覆盖（请修改配置文件）

# 配置文件
# config/simulation_config.yaml:
simulation:
  t_final: 0.3    # 从 0.2 改为 0.3
```

或使用 `main.py`：

```bash
python main.py --t_final 0.3
```

---

### FAQ-15: 如何添加自定义数值格式？

**答**: 按照以下步骤：

1. 在 `src/fd_schemes.py` 中实现新的 `xxx_step(U, dx, dt, gamma)` 函数
2. 在 `FD_SCHEMES` 字典中注册新格式
3. 在 `tests/test_fd_schemes.py` 中添加测试
4. 更新 `config/simulation_config.yaml` 中的 schemes 列表

**详细步骤**: 参见 `CONTRIBUTING.md` 中的"添加新数值格式"章节。

---

### FAQ-16: 如何更改输出目录？

**答**: 修改 `config/simulation_config.yaml`：

```yaml
output:
  data_dir: my_results/data
  exact_dir: my_results/exact
  figures_dir: my_results/figures
  error_report: my_results/error_report.csv
```

---

## 故障排查

### FAQ-17: 运行报错 "No module named 'src'"？

**答**: 这是因为 Python 无法找到 src 包。解决方案：

```bash
# 安装项目（推荐）
pip install -e .

# 或手动设置路径
# Linux/macOS:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Windows PowerShell:
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
```

详见故障排查手册 TS-01。

---

### FAQ-18: 出现负密度/负压力错误？

**答**: 最可能的原因是 CFL 数过大或网格过粗。

```bash
# 降低 CFL
python run_simulation.py --cfl 0.5 --scheme lax_wendroff

# 增加网格
python run_simulation.py --n_points 200 --cfl 0.8 --scheme macormack

# 使用更稳定的格式
python run_simulation.py --scheme lax_friedrichs
```

详见故障排查手册 TS-03。

---

### FAQ-19: 如何验证安装是否正确？

**答**:

```bash
# 1. 基础导入检查
python -c "from src.mesh_generator import generate_mesh; print('OK')"

# 2. 单元测试
python -m pytest tests/ -v --tb=short

# 3. 快速仿真验证
python run_simulation.py --n_points 100 --scheme upwind
```

39 项测试全部通过且仿真正常完成即为安装正确。

---

### FAQ-20: 可以把这个项目用于学术论文吗？

**答**: 可以。本项目基于 MIT 许可证开源，使用前请注意：

1. **引用本项目**:
   ```
   Sod Shock Tube CFD Solver v1.5.1.
   https://github.com/050610lzl/sod-shocktube-cfd
   ```

2. **引用关键文献**: 务必引用 Sod (1978), Toro (2009) 等核心文献

3. **验证结果**: 建议自行验证计算结果（本项目的精确解和格式实现已经过校验）

---

### FAQ-21: 为什么 Godunov 格式比 Roe 慢？

**答**: Godunov 格式需要在每个网格界面处求解精确 Riemann 问题，涉及迭代求根（Brent 算法），计算量远大于 Roe 格式的代数近似。但 Godunov 格式具有严格的保正性和熵条件满足性。

| 格式 | 每步计算 | 相对速度 |
|------|----------|:--------:|
| Lax-Friedrichs | 简单代数 | 1x |
| Roe | 3x3 矩阵特征分解 | ~3x |
| HLLC | 代数 + 条件分支 | ~5x |
| Godunov | 迭代求根 | ~10x |

---

### FAQ-22: 能否在 Jupyter Notebook 中使用？

**答**: 可以。安装后直接在 Notebook 中导入：

```python
import sys
sys.path.insert(0, '.')
from src.mesh_generator import generate_mesh
from src.fd_schemes import solve_with_scheme

x, dx = generate_mesh(n_points=100)
# ... 继续使用所有 src 模块
```

或使用 `pip install -e .` 安装后直接导入（无需设置 path）。

---

### FAQ-23: 如何查看历史仿真结果？

**答**: 所有仿真结果按时间戳归档，在相应目录下直接查看：

```bash
# 列出所有历史运行
ls results/data/
ls results/figures/

# 查看特定运行的结果
ls results/figures/20260516_230000/
```

---

### FAQ-24: 项目支持 Python 3.12+ 吗？

**答**: 当前版本（v1.5.1）仅正式支持 Python 3.9-3.11。Python 3.12 和 3.13 未经过充分测试，但鉴于项目的纯 Python 实现，有很大可能性可以直接运行。建议使用 3.9-3.11 以确保 CI 兼容。

---

### FAQ-25: 如何选择边界条件类型？

**答**: 项目支持 4 种边界条件类型（v1.5.1 新增），选择建议如下：

| 边界类型 | CLI / YAML 参数值 | 适用场景 | 典型行为 |
|----------|:-----------------:|----------|----------|
| 零梯度外推 | `zero_gradient`（默认） | 标准 Sod 问题、开放出口 | U[0] = U[1], U[-1] = U[-2]（一阶外推） |
| 固壁反射 | `reflective` | 管道端壁、对称面、固壁边界 | 密度/能量对称，动量反号（模拟壁面反弹） |
| 周期边界 | `periodic` | 周期性流动、无限管道 | U[0] = U[-2], U[-1] = U[1]（首尾衔接） |
| 透射边界 | `transmissive` | 亚/超音速出口、无反射边界 | U[0] = 2*U[1] - U[2]（二阶外推） |

**使用方式**：

```bash
# CLI 方式
python run_simulation.py --bc reflective
python run_simulation.py --boundary periodic

# YAML 配置方式
# config/simulation_config.yaml:
# boundary:
#   boundary_type: transmissive
```

**选择建议**：

- **标准 Sod 激波管验证**：使用默认 `zero_gradient`，与经典文献 [1] 一致
- **管道端壁效应研究**：使用 `reflective`，观察激波在壁面反射
- **长时间模拟或周期性管道**：使用 `periodic`，避免边界扰动累积
- **出口边界**：使用 `transmissive`，允许波系无反射地流出计算域

**参考文献**: Hirsch, C. (1990). Numerical Computation of Internal and External Flows, Vol. 2. John Wiley & Sons.

---

### FAQ-26: 如何自定义初始条件？（CLI vs YAML）

**答**: v1.5.1 提供了两种方式自定义 Sod 激波管的初始条件：

**方式 A: 命令行参数**（适合快速实验，v1.5.1 新增）

```bash
# 所有参数均可通过 CLI 覆盖
python run_simulation.py \
    --left_rho 1.0 --left_u 0.0 --left_p 3.0 \
    --right_rho 0.1 --right_u 0.0 --right_p 0.05 \
    --diaphragm 0.4 \
    --cfl 0.5 \
    --scheme roe
```

| CLI 参数 | 含义 | Sod 标准值 |
|----------|------|:----------:|
| `--left_rho` | 左态密度 | 1.0 |
| `--left_u` | 左态速度 | 0.0 |
| `--left_p` | 左态压力 | 1.0 |
| `--right_rho` | 右态密度 | 0.125 |
| `--right_u` | 右态速度 | 0.0 |
| `--right_p` | 右态压力 | 0.1 |
| `--diaphragm` | 隔膜位置 | 0.5 |

> **注意**：压力比（p_L/p_R）过大时建议降低 CFL（如 0.3-0.5）以防发散。

**方式 B: YAML 配置文件**（适合保存和重复使用）

编辑 `config/simulation_config.yaml`：

```yaml
physics:
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state:
    rho: 1.0
    u: 0.0
    p: 3.0       # 增大高压侧压力
  right_state:
    rho: 0.1      # 降低低压侧密度
    u: 0.0
    p: 0.05      # 降低低压侧压力
```

**优先级**：CLI 参数 > YAML 配置文件。当 CLI 未指定时，回退到 YAML 值。

**典型变体问题**：

| 名称 | p_L/p_R | rho_L/rho_R | 特点 |
|------|:-------:|:-----------:|------|
| Sod 标准 | 10 | 8 | 经典基准问题 |
| 强激波 | 100 | 8 | 激波更强，需降低 CFL |
| 密度型 | 10 | 3 | 接触间断更强 |

**参考文献**: Sod, G. A. (1978). JCP, 27(1), 1-31.

---

## 附录: 快速参考卡片

```bash
# 最常用的 5 个命令

# 1. 快速测试
python run_simulation.py --n_points 100 --scheme upwind

# 2. 运行全部格式
python run_simulation.py --n_points 100

# 3. 精度验证
python run_simulation.py --n_points 200 --scheme tvd_minmod

# 4. 格式对比
python run_simulation.py --schemes lax_friedrichs roe hllc tvd_minmod

# 5. 运行测试
python -m pytest tests/ -v --tb=short
```

---

> **参考文献**:
> [1] Sod, G. A. (1978). JCP, 27(1), 1-31.
> [2] Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.
> [3] Toro, E. F., Spruce, M., & Speares, W. (1994). Shock Waves, 4(1), 25-34.
> [4] Anderson, J. D. (1995). Computational Fluid Dynamics. McGraw-Hill.
> [5] ASME V&V 20-2009. Standard for Verification and Validation in CFD.