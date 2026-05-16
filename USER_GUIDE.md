# 软件用户使用手册

---

## 手册基础信息

| 项目 | 内容 |
|------|------|
| **软件名称** | 一维Sod激波管CFD求解器 |
| **软件版本** | v1.0.0 |
| **运行系统** | Windows/macOS/Linux |
| **开发用途** | 求解一维Sod激波管问题，对比验证多种有限差分数值格式 |
| **核心定位** | 计算流体力学教学与研究工具，数值格式验证平台 |
| **适用使用人群** | CFD研究人员、流体力学专业学生、数值计算工程师 |
| **软件核心主要功能** | 网格生成、流场初始化、多种数值格式求解、精确解计算、误差分析、结果可视化 |

---

## 一、手册前言与编写说明

### 1.1 手册目的

本手册旨在为用户提供一维Sod激波管CFD求解器的完整使用指南，涵盖软件安装、配置、操作、故障排查等方面，帮助用户快速上手并高效使用本软件。

### 1.2 目标读者

本手册面向以下用户群体：
- 初次接触CFD数值模拟的学生和研究人员
- 需要验证数值格式精度的工程师
- 进行流体力学教学演示的教师
- 希望了解激波管问题数值求解的技术人员

### 1.3 手册结构

本手册按功能模块组织，遵循从安装到高级应用的逻辑顺序：
- **基础篇**：环境配置、安装卸载、启动设置
- **操作篇**：界面介绍、核心功能使用教程
- **进阶篇**：参数配置、数据管理、高级技巧
- **维护篇**：故障排查、版本更新、安全须知

### 1.4 符号约定

| 符号 | 含义 |
|------|------|
| **【重点提示】** | 重要操作提示或注意事项 |
| **【操作步骤】** | 详细的操作流程说明 |
| **【示例】** | 命令行示例或代码片段 |
| **⚠️ 警告** | 可能导致数据丢失或程序异常的操作提醒 |
| **💡 提示** | 提高效率的技巧或建议 |

### 1.5 编写版本

| 版本 | 日期 | 修订内容 |
|------|------|---------|
| v1.0 | 2026-05-16 | 初始版本 |

---

## 二、软件整体概述

### 2.1 开发目的

本软件基于有限差分法（FDM）求解一维可压缩Euler方程组，用于求解经典的Sod激波管问题。主要目的包括：

1. **教学研究**：提供直观的CFD数值格式对比平台
2. **算法验证**：验证不同数值格式在激波捕捉方面的性能
3. **基准测试**：为CFD算法开发提供标准测试案例
4. **学术研究**：支持网格收敛性分析和误差量化评估

### 2.2 产品优势

| 优势 | 说明 |
|------|------|
| **多种数值格式** | 支持8种经典及现代数值格式对比 |
| **精确解验证** | 内置Riemann求解器计算精确解 |
| **量化误差分析** | 支持L1、L2、L∞三种误差范数 |
| **可视化输出** | 自动生成对比图和报告 |
| **配置灵活** | 支持配置文件和命令行参数 |
| **跨平台** | 支持Windows、macOS、Linux |

### 2.3 适用场景

| 场景类型 | 具体应用 |
|----------|----------|
| **教学演示** | 展示激波、接触间断、稀疏波的形成与传播 |
| **算法研究** | 对比不同数值格式的精度和稳定性 |
| **网格收敛性分析** | 评估数值格式的收敛阶数 |
| **代码验证** | 验证自定义CFD代码的正确性 |
| **性能测试** | 评估不同数值格式的计算效率 |

---

## 三、运行环境配置要求

### 3.1 硬件要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| **CPU** | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 |
| **内存** | 4GB RAM | 8GB RAM |
| **硬盘空间** | 500MB可用空间 | 1GB可用空间 |
| **显卡** | 集成显卡 | 独立显卡（可选） |

### 3.2 系统要求

| 操作系统 | 版本要求 |
|----------|---------|
| **Windows** | Windows 10 / Windows 11 |
| **macOS** | macOS 10.15 (Catalina) 及以上 |
| **Linux** | Ubuntu 18.04 / CentOS 7 及以上 |

### 3.3 依赖组件

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| **Python** | 3.8 及以上 | 编程语言环境 |
| **NumPy** | 1.21 及以上 | 数值计算库 |
| **Matplotlib** | 3.3 及以上 | 数据可视化库 |
| **PyYAML** | 5.4 及以上 | 配置文件解析库 |

### 3.4 网络要求

- **安装阶段**：需要联网下载Python依赖包
- **运行阶段**：无需网络连接

---

## 四、软件安装教程

### 4.1 获取安装包

【操作步骤】
1. 从指定渠道获取软件压缩包（格式：ZIP/TAR.GZ）
2. 保存到本地指定目录，建议路径不含中文和空格

### 4.2 解压部署

【操作步骤】
1. 右键点击压缩包，选择"解压到当前文件夹"
2. 确认解压后的目录结构包含以下文件：
   - `run_simulation.py`（主程序入口）
   - `config/simulation_config.yaml`（配置文件）
   - `src/`（源代码目录）
   - `requirements.txt`（依赖清单）

### 4.3 安装Python环境

【操作步骤】
1. 访问Python官方网站（https://www.python.org/downloads/）
2. 下载对应系统的Python安装包（建议3.9版本）
3. 运行安装程序，勾选"Add Python to PATH"选项
4. 完成安装后验证：
   ```bash
   python --version
   ```

### 4.4 安装依赖组件

【操作步骤】
1. 打开命令行终端，切换到软件目录
2. 执行依赖安装命令：
   ```bash
   pip install -r requirements.txt
   ```
3. 等待安装完成，检查是否有错误提示

### 4.5 权限设置（Linux/macOS）

【操作步骤】
1. 打开终端，切换到软件目录
2. 赋予执行权限：
   ```bash
   chmod +x run_simulation.py
   ```

### 4.6 安装验证

【操作步骤】
1. 在命令行执行：
   ```bash
   python run_simulation.py --n_points 50 --scheme lax_friedrichs
   ```
2. 检查输出是否正常，无报错信息即为安装成功

---

## 五、软件卸载方法

### 5.1 卸载步骤

【操作步骤】
1. 关闭所有运行中的软件进程
2. 删除软件所在的整个目录
3. 如需卸载Python环境，在系统控制面板中卸载

### 5.2 清理残留文件

【操作步骤】
1. 删除用户目录下的配置文件（如存在）：
   - Windows: `C:\Users\<用户名>\AppData\Roaming\sod-shocktube-cfd`
   - macOS: `~/Library/Application Support/sod-shocktube-cfd`
   - Linux: `~/.config/sod-shocktube-cfd`
2. 删除生成的结果文件（如需要保留则跳过）

---

## 六、软件启动与初始设置

### 6.1 启动方式

#### 方式一：命令行启动（推荐）

【操作步骤】
1. 打开命令行终端
2. 切换到软件目录：
   ```bash
   cd /path/to/sod-shocktube-cfd
   ```
3. 启动软件：
   ```bash
   python run_simulation.py
   ```

#### 方式二：快捷方式启动（Windows）

【操作步骤】
1. 在桌面空白处右键，选择"新建" -> "快捷方式"
2. 输入目标位置：
   ```
   python "C:\path\to\run_simulation.py"
   ```
3. 设置快捷方式名称，点击"完成"

### 6.2 首次运行设置

【操作步骤】
1. 首次运行前，检查配置文件 `config/simulation_config.yaml`
2. 根据需求修改网格点数、CFL数等参数
3. 运行软件，观察输出是否正常

【重点提示】首次运行会自动创建结果目录结构

---

## 七、账号登录/初始化配置教程

### 7.1 配置文件结构

【说明】本软件无需账号登录，通过配置文件进行初始化设置

配置文件位置：`config/simulation_config.yaml`

### 7.2 配置参数说明

| 参数类别 | 说明 |
|----------|------|
| **mesh** | 网格参数（节点数、边界） |
| **physics** | 物理参数（比热比、初始条件） |
| **simulation** | 仿真参数（终止时间、CFL数） |
| **schemes** | 数值格式列表 |
| **output** | 输出配置（目录路径） |

### 7.3 初始化配置步骤

【操作步骤】
1. 打开配置文件：
   ```bash
   notepad config/simulation_config.yaml  # Windows
   nano config/simulation_config.yaml    # Linux/macOS
   ```
2. 修改参数值（参考第10章详细说明）
3. 保存文件并退出

---

## 八、主界面布局详细介绍

### 8.1 界面概览

本软件为命令行工具，无图形界面，所有操作通过命令行参数或配置文件完成。

### 8.2 输出界面分区

#### 分区1：时间戳归档信息
- 显示当前运行的时间戳
- 显示数据、图片、精确解的保存目录

#### 分区2：仿真参数展示
- 网格节点数（N）
- CFL数
- 终止时间（t_final）
- 比热比（gamma）

#### 分区3：步骤进度指示
- 网格生成（步骤1）
- 流场初始化（步骤2）
- 时间迭代求解（步骤3）
- 误差计算（步骤4）
- 结果生成（步骤5-8）

#### 分区4：误差信息输出
- 显示各物理量（密度、速度、压力）的L1/L2误差
- 格式：`rho误差: L1=xxx, L2=xxx`

#### 分区5：归档说明
- 列出所有生成的文件路径
- 数据文件、图片文件、误差报告的位置

---

## 九、全部核心功能分步使用教程

### 9.1 功能概述

本软件包含以下核心功能模块：

| 功能 | 说明 | 调用方式 |
|------|------|---------|
| 网格生成 | 创建一维均匀网格 | 自动执行 |
| 流场初始化 | 设置Sod标准初始条件 | 自动执行 |
| 数值求解 | 使用指定格式求解Euler方程 | 自动执行 |
| 精确解计算 | 计算Riemann问题解析解 | 自动执行 |
| 误差分析 | 计算数值解与精确解的误差 | 自动执行 |
| 结果可视化 | 生成对比图和报告 | 自动执行 |

### 9.2 网格生成功能

【功能说明】根据配置的节点数生成一维均匀网格

【配置参数】
```yaml
mesh:
  n_points: 100    # 网格节点数
  x_left: 0.0     # 左边界坐标
  x_right: 1.0    # 右边界坐标
```

【操作步骤】
1. 在配置文件中设置网格参数
2. 运行软件，自动生成网格
3. 检查输出中的网格信息：
   ```
   [步骤1] 生成一维均匀网格...
   计算域: [0.0, 1.0], 节点数: 100, 间距: dx = 0.010101
   ```

### 9.3 流场初始化功能

【功能说明】根据配置的初始条件设置流场状态

【配置参数】
```yaml
physics:
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state:
    rho: 1.0
    u: 0.0
    p: 1.0
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
```

【操作步骤】
1. 在配置文件中设置初始条件
2. 运行软件，自动完成初始化
3. 检查输出中的初始状态信息

### 9.4 数值求解功能

【功能说明】使用指定的数值格式求解Euler方程组

【支持的数值格式】
| 格式名称 | 命令行参数 | 说明 |
|----------|-----------|------|
| Lax-Friedrichs | `lax_friedrichs` | 一阶中心耗散格式 |
| Lax-Wendroff | `lax_wendroff` | 二阶中心色散格式 |
| MacCormack | `macormack` | 二阶预估校正格式 |
| 一阶迎风 | `upwind` | 基于特征方向的格式 |
| Rusanov | `rusanov` | 局部Lax-Friedrichs格式 |
| Godunov | `godunov` | 精确Riemann求解器 |
| Roe | `roe` | 近似Riemann求解器 |
| HLLC | `hllc` | 恢复接触间断格式 |

【操作步骤】
1. 在配置文件中指定格式列表，或通过命令行参数指定
2. 运行软件，自动执行时间迭代
3. 观察迭代过程中的输出信息

### 9.5 精确解计算功能

【功能说明】使用Riemann求解器计算精确解，作为验证基准

【操作步骤】
1. 运行软件，自动在最后计算精确解
2. 精确解会保存到 `results/exact/<timestamp>/` 目录

### 9.6 误差分析功能

【功能说明】计算数值解与精确解之间的误差指标

【误差指标说明】
| 指标 | 公式 | 含义 |
|------|------|------|
| L1误差 | (1/N)Σ\|num - exact\| | 平均绝对误差 |
| L2误差 | √[(1/N)Σ(num - exact)²] | 均方根误差 |
| L∞误差 | max\|num - exact\| | 最大误差 |

【操作步骤】
1. 运行软件，自动计算各物理量的误差
2. 查看终端输出的误差信息
3. 误差报告会保存到 `results/error_report.csv`

### 9.7 结果可视化功能

【功能说明】生成数值解与精确解的对比图

【生成的图片类型】
| 图片类型 | 文件名 | 说明 |
|----------|--------|------|
| 单格式对比图 | `{timestamp}_plot_{scheme}.png` | 单个格式的对比 |
| 叠加对比图 | `{timestamp}_plot_all_schemes.png` | 所有格式叠加对比 |
| 密度分布图 | `density_{scheme}.png` | 密度分布对比 |
| 速度分布图 | `velocity_{scheme}.png` | 速度分布对比 |
| 压力分布图 | `pressure_{scheme}.png` | 压力分布对比 |

【操作步骤】
1. 运行软件，自动生成图片
2. 在 `results/figures/<timestamp>/` 目录查看结果

---

## 十、软件参数设置、自定义配置讲解

### 10.1 配置文件详解

配置文件位置：`config/simulation_config.yaml`

#### 10.1.1 网格参数配置

```yaml
mesh:
  n_points: 100      # 网格节点数，推荐值：100, 200, 400, 1000
  x_left: 0.0        # 计算域左边界，通常为0.0
  x_right: 1.0       # 计算域右边界，通常为1.0
```

【参数说明】
- **n_points**：网格点总数，影响计算精度和速度
- **x_left/x_right**：计算域范围，默认0到1

#### 10.1.2 物理参数配置

```yaml
physics:
  gamma: 1.4             # 比热比，理想气体取1.4
  diaphragm_pos: 0.5     # 隔膜位置，默认0.5（管道中央）
  left_state:            # 左区初始状态
    rho: 1.0             # 密度
    u: 0.0               # 速度
    p: 1.0               # 压力
  right_state:           # 右区初始状态
    rho: 0.125           # 密度
    u: 0.0               # 速度
    p: 0.1               # 压力
```

【参数说明】
- **gamma**：比热比，空气为1.4，单原子气体为1.67
- **diaphragm_pos**：初始间断位置
- **left_state/right_state**：左右两区的初始密度、速度、压力

#### 10.1.3 仿真参数配置

```yaml
simulation:
  t_final: 0.2    # 仿真终止时间，推荐0.2（标准Sod问题）
  cfl: 0.8        # CFL数，推荐0.8-0.95
```

【参数说明】
- **t_final**：仿真结束时间，t=0.2时波系结构清晰
- **cfl**：CFL数，控制时间步长，越小越稳定但越慢

#### 10.1.4 数值格式配置

```yaml
schemes:
  - lax_friedrichs    # 选择需要运行的数值格式
  - lax_wendroff
  - macormack
  - upwind
  - rusanov
  - godunov
  - roe
  - hllc
```

【说明】删除不需要的格式可减少运行时间

#### 10.1.5 输出配置

```yaml
output:
  data_dir: results/data        # 数值解数据目录
  exact_dir: results/exact       # 精确解数据目录
  figures_dir: results/figures   # 图片输出目录
  error_report: results/error_report.csv  # 误差报告路径
```

### 10.2 命令行参数

【命令行参数优先级】命令行参数 > 配置文件参数

#### 10.2.1 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--config` | 指定配置文件路径 | `--config my_config.yaml` |
| `--n_points` | 设置网格节点数 | `--n_points 200` |
| `--cfl` | 设置CFL数 | `--cfl 0.9` |
| `--scheme` | 指定单个格式 | `--scheme lax_friedrichs` |
| `--schemes` | 指定多个格式 | `--schemes macormack upwind` |

#### 10.2.2 使用示例

```bash
# 使用200个网格点，CFL=0.9，仅运行MacCormack格式
python run_simulation.py --n_points 200 --cfl 0.9 --scheme macormack

# 使用自定义配置文件
python run_simulation.py --config config/my_simulation.yaml

# 运行多个指定格式
python run_simulation.py --schemes lax_friedrichs lax_wendroff godunov
```

---

## 十一、数据保存、导出、导入使用方法

### 11.1 数据保存机制

【说明】软件自动按时间戳归档数据，无需手动保存

#### 11.1.1 数据文件结构

```
results/
├── data/
│   └── YYYYMMDD_HHMMSS/
│       ├── YYYYMMDD_HHMMSS_data_0.npy    # 第一个格式的数值解
│       ├── YYYYMMDD_HHMMSS_data_1.npy    # 第二个格式的数值解
│       └── ...
├── exact/
│   └── YYYYMMDD_HHMMSS/
│       └── YYYYMMDD_HHMMSS_data_exact.npy  # 精确解
├── figures/
│   └── YYYYMMDD_HHMMSS/
│       ├── YYYYMMDD_HHMMSS_plot_scheme1.png
│       ├── YYYYMMDD_HHMMSS_plot_scheme2.png
│       └── YYYYMMDD_HHMMSS_plot_all_schemes.png
└── error_report.csv  # 误差报告
```

### 11.2 数据格式说明

#### 11.2.1 NumPy数组格式（.npy）

- **数值解文件**：形状为 `(n_points, 3)`，列分别为密度、动量、能量
- **精确解文件**：形状为 `(n_points, 3)`，列分别为密度、速度、压力

#### 11.2.2 CSV格式

误差报告为CSV格式，包含以下列：
- Scheme：格式名称
- Variable：物理量（rho/u/p）
- L1_Error：L1误差值
- L2_Error：L2误差值
- Linf_Error：L∞误差值

### 11.3 数据导入方法

【操作步骤】
1. 使用Python读取数据：
   ```python
   import numpy as np
   
   # 读取数值解
   data = np.load('results/data/YYYYMMDD_HHMMSS/YYYYMMDD_HHMMSS_data_0.npy')
   rho_num = data[:, 0]  # 密度
   rhou_num = data[:, 1]  # 动量
   rhoE_num = data[:, 2]  # 能量
   
   # 读取精确解
   exact = np.load('results/exact/YYYYMMDD_HHMMSS/YYYYMMDD_HHMMSS_data_exact.npy')
   rho_exact = exact[:, 0]
   u_exact = exact[:, 1]
   p_exact = exact[:, 2]
   ```

### 11.4 数据导出方法

【操作步骤】
1. 在Python脚本中添加导出代码：
   ```python
   # 导出为文本文件
   np.savetxt('density_data.txt', rho_num)
   
   # 导出为CSV文件
   import pandas as pd
   df = pd.DataFrame({'rho': rho_num, 'u': u_num, 'p': p_num})
   df.to_csv('solution.csv', index=False)
   ```

---

## 十二、快捷键使用大全

【说明】本软件为命令行工具，无图形界面快捷键。以下为命令行常用操作：

| 快捷键 | 功能 | 适用场景 |
|--------|------|----------|
| Ctrl+C | 终止程序运行 | 仿真过程中需要中断 |
| Ctrl+D | 退出交互模式 | Python交互环境 |
| Ctrl+L | 清屏 | 终端输出过多时 |
| ↑ / ↓ | 上下切换命令历史 | 重复执行命令 |
| Tab | 自动补全命令/路径 | 输入命令时 |

---

## 十三、常见使用问题汇总及解决办法

### 13.1 安装问题

#### 问题1：pip安装失败

【现象】执行 `pip install -r requirements.txt` 时报错

【可能原因】网络问题、权限不足、Python版本不兼容

【解决办法】
1. 更新pip：`python -m pip install --upgrade pip`
2. 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
3. 检查Python版本：`python --version`（需3.8+）

#### 问题2：找不到Python命令

【现象】执行 `python --version` 提示"未找到命令"

【可能原因】Python未添加到系统PATH

【解决办法】
1. Windows：在安装Python时勾选"Add Python to PATH"
2. 手动添加路径：将Python安装目录添加到系统环境变量PATH中

### 13.2 运行问题

#### 问题3：仿真运行时间过长

【现象】运行后长时间无响应或进度缓慢

【可能原因】网格点数过多、格式数量过多、CFL数过小

【解决办法】
1. 减少网格点数：`--n_points 100`
2. 减少格式数量：`--scheme lax_friedrichs`
3. 增大CFL数：`--cfl 0.95`

#### 问题4：内存不足

【现象】运行时出现"MemoryError"或程序崩溃

【可能原因】网格点数过大（如超过10000）

【解决办法】
1. 减少网格点数：`--n_points 500`
2. 分批运行不同格式

#### 问题5：程序崩溃无输出

【现象】运行后立即退出，无任何输出

【可能原因】配置文件错误、依赖缺失、权限问题

【解决办法】
1. 检查配置文件格式是否正确
2. 重新安装依赖：`pip install -r requirements.txt`
3. 检查文件权限（Linux/macOS）

### 13.3 结果问题

#### 问题6：误差异常大

【现象】误差报告显示L2误差大于0.1

【可能原因】网格点数太少、CFL数过大导致不稳定、时间步过长

【解决办法】
1. 增加网格点数：`--n_points 400`
2. 降低CFL数：`--cfl 0.8`
3. 检查终止时间是否合理

#### 问题7：出现NaN或Inf值

【现象】结果中出现NaN或Inf

【可能原因】CFL数过大、数值格式不稳定、初始条件不合理

【解决办法】
1. 降低CFL数：`--cfl 0.5`
2. 使用更稳定的格式：`--scheme lax_friedrichs`
3. 检查配置文件中的初始条件

#### 问题8：结果图片不显示

【现象】运行完成后找不到图片文件

【可能原因】输出目录不存在、权限不足、Matplotlib配置问题

【解决办法】
1. 检查 `results/figures/` 目录是否存在
2. 确保有写入权限
3. 检查Matplotlib是否正确安装：`python -c "import matplotlib.pyplot as plt; print('OK')"`

---

## 十四、报错代码含义与故障排查方案

### 14.1 常见错误代码

| 错误代码 | 错误信息 | 含义 | 排查方案 |
|----------|---------|------|---------|
| 0 | 正常退出 | 程序正常完成 | 无需处理 |
| 1 | 配置文件错误 | YAML格式错误或参数缺失 | 检查配置文件语法 |
| 2 | 参数错误 | 命令行参数无效 | 运行 `python run_simulation.py --help` |
| 3 | 依赖缺失 | 缺少必要的Python库 | 重新安装依赖 |
| 4 | 内存错误 | 内存不足 | 减少网格点数 |
| 5 | 数值不稳定 | 计算过程发散 | 降低CFL数 |

### 14.2 错误信息解读

#### 错误类型1：YAML解析错误

【错误信息示例】
```
yaml.parser.ParserError: while parsing a block mapping
  in "config/simulation_config.yaml", line 5, column 3
expected <block end>, but found '<block mapping start>'
```

【含义】配置文件YAML语法错误

【排查方案】
1. 检查第5行附近的缩进是否正确
2. 确保冒号后有空格
3. 使用YAML验证工具检查格式

#### 错误类型2：参数类型错误

【错误信息示例】
```
TypeError: 'str' object cannot be interpreted as an integer
```

【含义】配置文件中参数类型错误（如将数字写成字符串）

【排查方案】
1. 检查配置文件中的数值参数（n_points、cfl等）
2. 确保数值参数不加引号
3. 检查是否有拼写错误

#### 错误类型3：数值发散

【错误信息示例】
```
RuntimeWarning: overflow encountered in double_scalars
```

【含义】计算过程中出现数值溢出

【排查方案】
1. 降低CFL数
2. 检查初始条件是否合理
3. 使用更稳定的数值格式

### 14.3 日志查看方法

【操作步骤】
1. 运行软件时记录输出：
   ```bash
   python run_simulation.py > simulation.log 2>&1
   ```
2. 查看日志文件：
   ```bash
   cat simulation.log  # Linux/macOS
   type simulation.log  # Windows
   ```

---

## 十五、软件更新升级教程

### 15.1 检查更新

【操作步骤】
1. 查看当前版本：
   ```bash
   python run_simulation.py --version
   ```
2. 检查官方更新渠道获取新版本信息

### 15.2 升级步骤

#### 方式一：Git仓库升级（推荐）

【操作步骤】
1. 确保当前工作目录干净：
   ```bash
   git status
   ```
2. 拉取最新代码：
   ```bash
   git pull origin cfj-builder
   ```
3. 更新依赖：
   ```bash
   pip install -r requirements.txt --upgrade
   ```

#### 方式二：手动下载升级

【操作步骤】
1. 下载最新版本压缩包
2. 备份当前配置文件和结果数据
3. 删除旧版本目录
4. 解压新版本压缩包
5. 恢复配置文件（如有自定义配置）

### 15.3 升级注意事项

⚠️ 警告：升级前请备份配置文件和重要数据

【升级检查清单】
- [ ] 备份 `config/simulation_config.yaml`
- [ ] 备份 `results/` 目录中的重要结果
- [ ] 记录当前使用的参数配置
- [ ] 确认新版本的兼容性说明

---

## 十六、使用注意事项与安全须知

### 16.1 使用注意事项

#### 16.1.1 计算资源管理

- 网格点数建议从100开始，逐步增加
- 长时间运行时建议监控系统资源占用
- 批量运行多个仿真时注意控制并行数量

#### 16.1.2 数据管理

- 定期清理过期的结果文件
- 重要结果建议单独备份
- 数据文件较大时注意存储空间

#### 16.1.3 结果验证

- 首次使用时建议与标准算例对比验证
- 异常结果需检查参数配置是否正确
- 网格收敛性需通过多尺度验证确认

### 16.2 安全须知

#### 16.2.1 文件安全

- 配置文件包含敏感参数，请勿随意分享
- 结果文件保存路径避免包含敏感信息
- 定期备份重要数据

#### 16.2.2 系统安全

- 仅从可信渠道获取软件和依赖
- 运行前检查文件完整性
- 避免在生产环境直接运行未经测试的版本

#### 16.2.3 网络安全

- 安装依赖时确保网络环境安全
- 避免使用未知来源的pip镜像
- 不向外部服务传输敏感数据

---

## 十七、版本更新日志

### v1.0.0（2026-05-16）

#### 新增功能
- ✅ 实现8种数值格式（Lax-Friedrichs、Lax-Wendroff、MacCormack、Upwind、Rusanov、Godunov、Roe、HLLC）
- ✅ 集成Riemann精确解求解器
- ✅ 实现L1、L2、L∞误差计算
- ✅ 自动生成对比图和误差报告
- ✅ 支持配置文件和命令行参数

#### 性能优化
- ✅ 优化时间步长计算
- ✅ 优化内存使用

#### 文档更新
- ✅ 完成用户手册编写
- ✅ 添加API文档注释

---

## 十八、版权声明与使用须知

### 18.1 版权声明

【版权信息】
- 版权所有 © 2026 [开发团队/个人]
- 保留所有权利

### 18.2 使用许可

本软件仅供以下用途使用：
- ✅ 学术研究和教学目的
- ✅ 非商业性个人使用
- ✅ 内部测试和验证

### 18.3 禁止用途

- ❌ 未经授权的商业使用
- ❌ 未经许可的分发和修改
- ❌ 用于违法或恶意目的

### 18.4 免责声明

【免责声明】
本软件仅供学习和研究使用，开发者不对以下情况负责：
- 使用本软件产生的任何直接或间接损失
- 因使用本软件导致的任何数据丢失
- 因软件错误导致的任何后果

### 18.5 联系方式

如有问题或建议，请联系：[联系方式]

---

**文档版本**: v1.0  
**最后更新**: 2026-05-16  
**软件版本**: v1.0.0

---

**附录：命令速查表**

| 命令 | 说明 |
|------|------|
| `python run_simulation.py` | 默认运行所有格式 |
| `python run_simulation.py --n_points 200` | 指定网格点数 |
| `python run_simulation.py --cfl 0.9` | 指定CFL数 |
| `python run_simulation.py --scheme macormack` | 运行单个格式 |
| `python run_simulation.py --help` | 显示帮助信息 |
