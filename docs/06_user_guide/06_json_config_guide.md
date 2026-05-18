# JSON 配置文件完整指南

> **文档编号**: SOD-CFD-UG-06
> **适用版本**: v1.7.0+
> **依赖**: Python 3.9+, `json` 标准库

---

## 目录

1. [概述](#1-概述)
2. [快速开始](#2-快速开始)
3. [JSON 配置结构 (Schema)](#3-json-配置结构-schema)
4. [配置项详解](#4-配置项详解)
5. [自定义场景示例](#5-自定义场景示例)
6. [参数验证规则](#6-参数验证规则)
7. [CLI 使用方式](#7-cli-使用方式)
8. [YAML ↔ JSON 迁移指南](#8-yaml--json-迁移指南)
9. [常见错误排查](#9-常见错误排查)

---

## 1. 概述

### 1.1 什么是 JSON 配置文件？

JSON 配置文件是 Sod 激波管 CFD 求解器的参数输入方式之一。通过一个结构化 JSON 文件，用户可以设定仿真所需的所有参数，包括网格、物理条件、数值格式、输出路径等，**无需修改任何 Python 代码**。

### 1.2 JSON vs YAML vs CLI

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **JSON 配置** | 团队协作、自动化脚本 | 严格语法校验、广泛工具支持、易于程序生成 | 手写时需注意逗号和引号 |
| **YAML 配置** | 手动编辑、快速实验 | 人类友好、支持注释 | 缩进敏感 |
| **CLI 参数** | 快速覆盖单个参数 | 无需编辑文件 | 无法保存配置组合 |

**优先级**：CLI 参数 > 配置文件（JSON 与 YAML 平级）。CLI 未指定时回退到配置文件值。

### 1.3 可用配置文件

| 文件 | 网格 | 初始条件 | 格式 |
|------|:---:|---------|:---:|
| `config/simulation_config.json` | 100 | Sod 标准 (1.0 / 0.125) | 8 种 |
| `config/simulation_config_custom_sod.json` | 200 | 高压比 (10.0 / 0.1) | 3 种 (Riemann) |
| `config/simulation_config_high_res.json` | 800 | Sod 标准 (1.0 / 0.125) | 3 种 (Riemann) |

---

## 2. 快速开始

### 2.1 使用默认 JSON 配置

```bash
python run_simulation.py --config config/simulation_config.json
```

### 2.2 创建自定义 JSON 配置

1. 复制默认配置作为模板：
```bash
cp config/simulation_config.json my_config.json
```

2. 用任意文本编辑器编辑 `my_config.json`，修改参数。

3. 运行：
```bash
python run_simulation.py --config-json my_config.json
```

### 2.3 最小 JSON 配置

以下是一个将 JSON 配置精简到最核心参数的示例（省略 output 将使用默认值）：

```json
{
  "mesh": {"n_points": 100},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": 0.0, "p": 1.0},
    "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
  },
  "simulation": {"t_final": 0.2, "cfl": 0.8},
  "schemes": ["roe", "hllc"],
  "output": {}
}
```

---

## 3. JSON 配置结构 (Schema)

### 3.1 顶层结构

一个完整的 JSON 配置文件必须包含 **5 个顶层节点**。缺失任何一个都会触发 `validate_config()` 校验失败。

```json
{
  "mesh":       { },
  "physics":    { },
  "simulation": { },
  "schemes":    [ ],
  "output":     { }
}
```

### 3.2 完整结构树

```
{
  "mesh": {
    "n_points": <int>,        // 网格节点数，≥ 10
    "x_left": <float>,        // 左边界坐标（可选，默认 0.0）
    "x_right": <float>        // 右边界坐标（可选，默认 1.0）
  },
  "physics": {
    "gamma": <float>,         // 比热比，(0.1, 5.0]，默认 1.4
    "diaphragm_pos": <float>, // 隔膜位置（可选，默认 0.5）
    "left_state": {
      "rho": <float>,         // 左态密度，> 0
      "u": <float>,           // 左态速度
      "p": <float>            // 左态压力，> 0
    },
    "right_state": {
      "rho": <float>,         // 右态密度，> 0
      "u": <float>,           // 右态速度
      "p": <float>            // 右态压力，> 0
    }
  },
  "simulation": {
    "t_final": <float>,       // 终止时间，[0.001, 10.0]
    "cfl": <float>,           // CFL 数，[0.01, 1.0]
    "boundary_type": <string> // 边界类型，4 选 1
  },
  "schemes": [
    "<string>",               // 格式名称列表，非空
    "..."
  ],
  "output": {
    "data_dir": <string>,     // 数值解输出目录
    "exact_dir": <string>,    // 精确解输出目录
    "figures_dir": <string>,  // 对比图输出目录
    "error_report": <string>  // 误差报告文件路径
  }
}
```

---

## 4. 配置项详解

### 4.1 `mesh` — 网格参数

| JSON 路径 | 类型 | 默认值 | 约束 | 说明 |
|-----------|------|:---:|------|------|
| `mesh.n_points` | int | 100 | ≥ 10 | 计算域内网格节点数。更多节点 → 更高精度 → 更慢计算 |
| `mesh.x_left` | float | 0.0 | — | 计算域左边界坐标 |
| `mesh.x_right` | float | 1.0 | — | 计算域右边界坐标 |

**推荐 n_points**：

| n_points | 适用场景 | 计算时间 |
|:--------:|---------|:------:|
| 100 | 快速测试、教学演示 | < 1s |
| 200 | 标准分析 | ~2s |
| 400 | 误差收敛研究 | ~10s |
| 800 | 高精度对比 | ~1min |

### 4.2 `physics` — 物理参数

| JSON 路径 | 类型 | 默认值 | 约束 | 说明 |
|-----------|------|:---:|------|------|
| `physics.gamma` | float | 1.4 | (0.1, 5.0] | 比热比。空气 ≈ 1.4，氦气 ≈ 1.667 |
| `physics.diaphragm_pos` | float | 0.5 | — | 隔膜位置（x=0 到 x=1 之间） |
| `physics.left_state.rho` | float | 1.0 | > 0 | 隔膜左侧密度 |
| `physics.left_state.u` | float | 0.0 | — | 隔膜左侧速度 |
| `physics.left_state.p` | float | 1.0 | > 0 | 隔膜左侧压力 |
| `physics.right_state.rho` | float | 0.125 | > 0 | 隔膜右侧密度 |
| `physics.right_state.u` | float | 0.0 | — | 隔膜右侧速度 |
| `physics.right_state.p` | float | 0.1 | > 0 | 隔膜右侧压力 |

**Sod 标准工况**：`left = (1.0, 0.0, 1.0), right = (0.125, 0.0, 0.1)`

此工况产生的波系结构：
- 左行稀疏波（膨胀波）
- 向右运动的接触间断
- 右行激波

### 4.3 `simulation` — 仿真控制参数

| JSON 路径 | 类型 | 默认值 | 约束 | 说明 |
|-----------|------|:---:|------|------|
| `simulation.t_final` | float | 0.2 | [0.001, 10.0] | 仿真终止时间。对于 Sod 问题，0.2s 时各波系已充分发展 |
| `simulation.cfl` | float | 0.8 | [0.01, 1.0] | CFL 数。值越大步长越大（更快），但超过 1.0 会不稳定 |
| `simulation.boundary_type` | str | `"zero_gradient"` | 4 选 1 | 边界条件类型（见下表） |

**边界条件类型**：

| 值 | 行为 | 适用场景 |
|----|------|---------|
| `"zero_gradient"` | U[0] = U[1], U[-1] = U[-2] | **Sod 标准**、开放边界 |
| `"reflective"` | 密度/能量不变，速度反号 | 管道端壁、固壁 |
| `"periodic"` | U[0] = U[-2], U[-1] = U[1] | 无限长管道近似 |
| `"transmissive"` | 二阶外推 | 波穿过边界不反射 |

### 4.4 `schemes` — 数值格式列表

**必填**：非空 JSON 字符串数组。每个元素必须是以下 9 种已注册格式之一。

| 序号 | 格式名称 | 精度 | 类型 | 文献 |
|:---:|---------|:---:|------|------|
| 1 | `"lax_friedrichs"` | 一阶 | 中心耗散 | Sod (1978) |
| 2 | `"lax_wendroff"` | 二阶 | 中心色散 | Sod (1978) |
| 3 | `"macormack"` | 二阶 | 预估-校正 | Sod (1978) |
| 4 | `"upwind"` | 一阶 | Steger-Warming 分裂 | Laney (1998) |
| 5 | `"rusanov"` | 一阶 | 局部 Lax-Friedrichs | Rusanov (1961) |
| 6 | `"godunov"` | 一阶 | 精确 Riemann 求解 | Godunov (1959) |
| 7 | `"roe"` | 一阶 | 近似 Riemann 求解 | Roe (1981) |
| 8 | `"hllc"` | 一阶 | 恢复接触间断 | Toro et al. (1994) |
| 9 | `"tvd_minmod"` | 二阶 | 通量限制高阶 | Harten (1983) |

### 4.5 `output` — 输出配置

| JSON 路径 | 类型 | 默认值 | 说明 |
|-----------|------|--------|------|
| `output.data_dir` | str | `"results/data"` | 数值解 `.csv` 数据输出目录 |
| `output.exact_dir` | str | `"results/exact"` | 精确解 `.npy` 数据输出目录 |
| `output.figures_dir` | str | `"results/figures"` | 对比图 `.png` 输出目录 |
| `output.error_report` | str | `"results/error_report.csv"` | L1/L2/L∞ 误差汇总报告路径 |

---

## 5. 自定义场景示例

### 5.1 Sod 标准工况（参考基准）

```json
{
  "mesh": {"n_points": 100},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": 0.0, "p": 1.0},
    "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
  },
  "simulation": {"t_final": 0.2, "cfl": 0.8, "boundary_type": "zero_gradient"},
  "schemes": ["lax_friedrichs", "godunov", "roe", "hllc"],
  "output": {
    "data_dir": "results/data",
    "exact_dir": "results/exact",
    "figures_dir": "results/figures",
    "error_report": "results/error_report.csv"
  }
}
```

### 5.2 强激波工况

增大左态压力，研究强激波下的格式鲁棒性：

```json
{
  "mesh": {"n_points": 200},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": 0.0, "p": 10.0},
    "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
  },
  "simulation": {"t_final": 0.15, "cfl": 0.5, "boundary_type": "transmissive"},
  "schemes": ["godunov", "roe", "hllc"],
  "output": {
    "data_dir": "results/data",
    "exact_dir": "results/exact",
    "figures_dir": "results/figures",
    "error_report": "results/error_report_strong.csv"
  }
}
```

### 5.3 高分辨率收敛性研究

使用 800 点网格 + Riemann 求解器研究网格收敛性：

```json
{
  "mesh": {"n_points": 800},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": 0.0, "p": 1.0},
    "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
  },
  "simulation": {"t_final": 0.2, "cfl": 0.8, "boundary_type": "zero_gradient"},
  "schemes": ["godunov", "roe", "hllc"],
  "output": {
    "data_dir": "results/data",
    "exact_dir": "results/exact",
    "figures_dir": "results/figures",
    "error_report": "results/error_report_hires.csv"
  }
}
```

### 5.4 速度间断工况

研究左右态存在速度差的复杂波系：

```json
{
  "mesh": {"n_points": 200},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": -0.5, "p": 1.0},
    "right_state": {"rho": 1.0, "u": 0.5, "p": 1.0}
  },
  "simulation": {"t_final": 0.3, "cfl": 0.8, "boundary_type": "zero_gradient"},
  "schemes": ["godunov", "roe", "hllc"],
  "output": {
    "data_dir": "results/data",
    "exact_dir": "results/exact",
    "figures_dir": "results/figures",
    "error_report": "results/error_report_vel.csv"
  }
}
```

### 5.5 反射边界条件研究

使用反射边界研究激波在固壁上的反射行为：

```json
{
  "mesh": {"n_points": 200},
  "physics": {
    "gamma": 1.4,
    "left_state": {"rho": 1.0, "u": 0.0, "p": 10.0},
    "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
  },
  "simulation": {"t_final": 0.4, "cfl": 0.5, "boundary_type": "reflective"},
  "schemes": ["godunov", "roe"],
  "output": {
    "data_dir": "results/data",
    "exact_dir": "results/exact",
    "figures_dir": "results/figures",
    "error_report": "results/error_report_refl.csv"
  }
}
```

---

## 6. 参数验证规则

配置文件加载时，`validate_config()` 自动检查所有参数的合法性。以下为完整验证表：

| JSON 路径 | 检查项 | 错误时抛出 |
|-----------|--------|:---:|
| 顶层节点 | 必须包含 `mesh`, `physics`, `simulation`, `schemes`, `output` | `ValueError` |
| `mesh.n_points` | 必须是 ≥ 10 的整数 | `ValueError` |
| `physics.gamma` | 必须在 (0.1, 5.0] 范围 | `ValueError` |
| `simulation.cfl` | 必须在 [0.01, 1.0] 范围 | `ValueError` |
| `simulation.t_final` | 必须在 [0.001, 10.0] 范围 | `ValueError` |
| `simulation.boundary_type` | 必须从 4 种有效类型中选择 | `ValueError` |
| `schemes` | 必须是非空列表 | `ValueError` |
| `schemes[i]` | 每一项必须在 9 种已注册格式中 | `ValueError` |

> **注意**：`left_state` 中的密度和压力必须 > 0，否则求解器会因物理无意义而发散（非 `validate_config` 检测，但求解器本身会通过 `np.maximum(data, 1e-15)` 防御）。

---

## 7. CLI 使用方式

### 7.1 加载 JSON 配置文件

```bash
# 方式 1: --config 自动检测格式（推荐）
python run_simulation.py --config config/simulation_config.json

# 方式 2: --config-json 显式指定 JSON
python run_simulation.py --config-json config/simulation_config.json

# 方式 3: 加载自定义 JSON 配置
python run_simulation.py --config-json my_custom_config.json
```

### 7.2 JSON 配置 + CLI 覆盖

CLI 参数优先级高于配置文件，可灵活覆盖特定参数：

```bash
# 使用 JSON 配置，但通过 CLI 覆盖 n_points 和 boundary_type
python run_simulation.py --config config/simulation_config.json \
    --n_points 400 --bc reflective
```

### 7.3 自动格式检测

`load_any_config()` 根据文件扩展名自动选择解析器：

| 扩展名 | 解析器 | 
|--------|--------|
| `.json` | `json.load()` (Python 标准库) |
| `.yaml` | `yaml.safe_load()` (PyYAML) |
| `.yml` | `yaml.safe_load()` (PyYAML) |
| 其他 | 抛出 `ValueError` |

---

## 8. YAML ↔ JSON 迁移指南

### 8.1 结构一致性

JSON 和 YAML 配置的结构**完全一致**，都是 5 个顶层节点。`boundary_type` 在两个格式中都位于 `simulation` 节点下。

### 8.2 语法对照表

| YAML | JSON |
|------|------|
| `n_points: 100` | `"n_points": 100` |
| `left_state: {rho: 1.0, u: 0.0, p: 1.0}` | `"left_state": {"rho": 1.0, "u": 0.0, "p": 1.0}` |
| `- lax_friedrichs` | `"lax_friedrichs"` (在数组中) |
| `# 这是注释` | 不支持注释（如需要注释建议用 `"_comment": "..."` 键） |
| 缩进表示嵌套 | 大括号 `{}` 表示嵌套 |

### 8.3 YAML → JSON 转换

```bash
# 使用 Python 一行命令将 YAML 转为 JSON
python -c "import yaml,json;json.dump(yaml.safe_load(open('config/simulation_config.yaml')),open('my_config.json','w'),indent=2)"
```

### 8.4 JSON → YAML 转换

```bash
# 使用 Python 一行命令将 JSON 转为 YAML
python -c "import yaml,json;yaml.dump(json.load(open('config/simulation_config.json')),open('my_config.yaml','w'),default_flow_style=False)"
```

---

## 9. 常见错误排查

### 9.1 JSON 语法错误

**错误信息**: `json.JSONDecodeError: Expecting ',' delimiter: line X column Y`

**原因**: JSON 对象内部缺少逗号、多余逗号、或括号不匹配。

**解决**:
```bash
# 验证 JSON 语法
python -m json.tool my_config.json > /dev/null
# 语法正确则无输出，有错误会显示具体行号
```

### 9.2 缺少必需配置节

**错误信息**: `ValueError: 缺少必需配置节: 'schemes'`

**原因**: 5 个顶层节点缺失其中一个。

**解决**: 确保 JSON 包含 `mesh`, `physics`, `simulation`, `schemes`, `output` 全部 5 个顶层键。

### 9.3 未知格式名称

**错误信息**: `ValueError: schemes 中包含未知格式 'xxx'`

**原因**: 格式名称拼写错误或使用未注册的格式。

**解决**: 检查格式名称是否为 `lax_friedrichs`, `lax_wendroff`, `macormack`, `upwind`, `rusanov`, `godunov`, `roe`, `hllc`, `tvd_minmod` 之一。

### 9.4 非法边界条件

**错误信息**: `ValueError: simulation.boundary_type 必须为 [...] 之一`

**原因**: `boundary_type` 值必须是 `"zero_gradient"`, `"reflective"`, `"periodic"`, `"transmissive"` 之一。

**解决**:
```json
{ "simulation": { "boundary_type": "zero_gradient" } }
```

### 9.5 CFL 超出范围

**错误信息**: `ValueError: simulation.cfl 必须在 [0.01, 1.0] 范围`

**解决**: 将 `cfl` 设置在 0.01 到 1.0 之间。值越大计算越快但不稳定，推荐 0.5-0.8。

### 9.6 负密度/负压力导致求解发散

**错误信息**: `AssertionError: negative density detected`

**原因**: 初始条件的密度或压力 ≤ 0，导致物理无意义。

**解决**: 确保 `left_state.rho`, `left_state.p`, `right_state.rho`, `right_state.p` 均 > 0。

---

> **文档版本**: v1.0 | **更新日期**: 2026-05-17 | **适用版本**: v1.7.0+