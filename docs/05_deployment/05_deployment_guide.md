# 软件部署手册

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Sod Shock Tube CFD - 一维激波管有限差分法求解器 |
| 文档版本 | v1.0 |
| 发布日期 | 2026-05-16 |
| 适用版本 | v1.3.0 |
| 文档编号 | DEPLOY-GUIDE-001 |

---

## 1. 系统要求

### 1.1 操作系统支持

| 操作系统 | 最低版本 | 推荐版本 | 状态 |
|----------|---------|---------|------|
| Windows | Windows 10 | Windows 11 | 完全支持 |
| Linux (Ubuntu/Debian) | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS | 完全支持 |
| macOS | macOS 12 Monterey | macOS 14 Sonoma | 完全支持 |
| Linux (CentOS/RHEL) | CentOS 7 | Rocky Linux 9 | 支持 |

> **注意**: 本项目为纯 Python 实现，理论上支持任何可运行 Python 3.9+ 的操作系统。

### 1.2 软件依赖

| 依赖项 | 最低版本 | 最高版本 | 用途 |
|--------|---------|---------|------|
| Python | 3.9 | 3.11 | 主运行环境 |
| pip | 21.0 | - | 包管理器 |
| numpy | 1.21.0 | <2.0.0 | 数值计算（数组操作、线性代数） |
| matplotlib | 3.5.0 | - | 可视化绘图 |
| pyyaml | 6.0 | - | YAML 配置文件解析 (JSON 使用标准库 json) |
| scipy | 1.7.0 | - | 科学计算（Brent 求根算法等） |

### 1.3 硬件要求

| 硬件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 双核 1.5 GHz | 四核 2.5 GHz |
| 内存 | 2 GB | 4 GB |
| 磁盘空间 | 100 MB（含依赖） | 500 MB（含结果数据） |
| 网络 | 安装时需要 | - |

### 1.4 可选依赖

| 依赖项 | 版本 | 用途 |
|--------|------|------|
| pytest | >=7.0.0 | 单元测试框架 |
| flake8 | >=5.0.0 | 代码风格检查 |

---

## 2. 在线安装

### 2.1 通过 Git Clone + Pip 安装（推荐）

**步骤 1：克隆仓库**

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
```

**步骤 2：创建并激活虚拟环境（推荐）**

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**步骤 3：安装项目及依赖**

```bash
# 基础安装（仅运行仿真）
pip install -e .

# 完整安装（含测试和开发工具）
pip install -e ".[test,dev]"
```

**步骤 4：验证安装**

```bash
python -c "from src.mesh_generator import generate_mesh; print('安装成功')"
```

### 2.2 通过 PyPI 安装（未来支持）

```bash
pip install sod-shocktube-cfd
```

> **注意**: PyPI 发布计划在 v1.4.0 版本中实现。

---

## 3. 离线安装

### 3.1 下载源码包

从 GitHub Releases 页面下载最新版本的源码包：

- 下载地址: `https://github.com/050610lzl/sod-shocktube-cfd/releases`
- 选择 `Source code (zip)` 或 `Source code (tar.gz)`

或者使用 git 工具将已克隆的仓库打包：

```bash
git archive --format=zip --output=sod-shocktube-cfd-v1.3.0.zip HEAD
```

### 3.2 手动安装依赖

**步骤 1：在有网络的机器上下载依赖包**

```bash
# 创建 wheels 目录
mkdir wheels

# 下载所有依赖的 wheel 文件
pip download -r requirements.txt -d wheels/
pip download pytest -d wheels/
```

**步骤 2：将源码包和 wheels 目录复制到离线机器**

**步骤 3：在离线机器上安装**

```bash
# 解压源码包
unzip sod-shocktube-cfd-v1.3.0.zip
cd sod-shocktube-cfd-v1.3.0

# 安装本地 wheels（不访问网络）
pip install --no-index --find-links=../wheels -r requirements.txt

# 以可编辑模式安装项目
pip install -e . --no-deps
```

### 3.3 Conda 环境离线安装

```bash
# 在有网络的环境中导出环境
conda env export -n sod-cfd > environment.yml

# 下载 Conda 包
conda list --explicit > spec-file.txt
conda create --name sod-cfd-offline --file spec-file.txt --offline

# 在离线环境中还原
conda env create -f environment.yml
pip install -e . --no-deps
```

---

## 4. 验证部署

### 4.1 运行单元测试

```bash
# 运行全部测试（34 项）
python -m pytest tests/ -v

# 预期输出示例：
# ============================= test session starts =============================
# tests/test_mesh.py ..............                         [ 23%]
# tests/test_initialization.py .........                    [ 48%]
# tests/test_boundary.py .........                          [ 73%]
# tests/test_fd_schemes.py .........                       [100%]
# ======================= 34 passed in 2.50s =============================
```

### 4.2 运行快速仿真验证

```bash
# 使用迎风格式进行快速验证（约5秒完成）
python run_simulation.py --n_points 100 --cfl 0.8 --scheme upwind
```

**预期输出**：

- 终端无错误信息
- 输出目录 `results/` 下生成数据文件和图片文件
- 密度、压力、速度的数值解与精确解吻合良好

### 4.3 运行全部格式集成测试

```bash
# 运行全部 9 种格式（约2分钟完成）
python run_simulation.py --n_points 100
```

**验证标准**：

| 验证项 | 标准 | 方法 |
|--------|------|------|
| 单元测试全通过 | 34/34 passed | `pytest tests/ -v` |
| 无负密度/压力 | min(rho) > 0, min(p) > 0 | 仿真输出检查 |
| 误差在合理范围 | L1(rho) < 0.05 (N=100) | 误差报告检查 |
| 图表正常生成 | 9 张单格式图 + 1 张对比图 | `results/figures/` 检查 |

---

## 5. 启停脚本说明

### 5.1 运行仿真

#### 方式一：使用 run_simulation.py（推荐，带时间戳归档）

```bash
# 使用默认配置文件运行全部格式
python run_simulation.py

# 指定网格分辨率
python run_simulation.py --n_points 200

# 指定单个格式
python run_simulation.py --scheme upwind

# 指定多个格式
python run_simulation.py --schemes lax_friedrichs upwind roe

# 指定 CFL 数
python run_simulation.py --cfl 0.9

# 使用自定义配置文件
python run_simulation.py --config my_config.yaml
python run_simulation.py --config-json my_config.json  # v1.7.0+
```

#### 方式二：使用 main.py（简化版，固定目录输出）

```bash
# 使用默认参数运行
python main.py

# 运行指定格式
python main.py --scheme lax_friedrichs --n_points 200
```

#### 方式三：通过 setup.py 安装的命令行入口

```bash
# 安装后可使用 sod-shocktube 命令
sod-shocktube --n_points 100 --scheme upwind
```

### 5.2 中断仿真

- **Ctrl + C**: 键盘中断，终止当前仿真进程
- **关闭终端窗口**: 强制终止
- **pkill（Linux/macOS）**: `pkill -f run_simulation.py`
- **任务管理器（Windows）**: 结束 Python 进程

> **注意**: 仿真中断后，`results/` 目录下将保留已生成的部分结果文件，不会自动清理。

### 5.3 批量运行脚本

```bash
# Linux/macOS
#!/bin/bash
for N in 50 100 200 400; do
    python run_simulation.py --n_points $N
done
```

```powershell
# Windows PowerShell
foreach ($N in @(50, 100, 200, 400)) {
    python run_simulation.py --n_points $N
}
```

---

## 6. 日志查看

### 6.1 输出目录结构

仿真完成后，`results/` 目录结构如下：

```
results/
├── data/
│   └── 20260516_230000/           # 时间戳归档
│       ├── 20260516_230000_data_0.npy    # lax_friedrichs 数据
│       ├── 20260516_230000_data_1.npy    # lax_wendroff 数据
│       ├── 20260516_230000_data_2.npy    # macormack 数据
│       ├── ...（其他格式）
│       └── 20260516_230000_data_exact.npy # 精确解数据
├── exact/
│   └── 20260516_230000/
│       └── 20260516_230000_data_exact.npy
├── figures/
│   └── 20260516_230000/
│       ├── 20260516_230000_plot_lax_friedrichs.png
│       ├── 20260516_230000_plot_lax_wendroff.png
│       ├── ...
│       └── 20260516_230000_plot_all_schemes.png
└── error_report.csv               # 误差汇总报告
```

### 6.2 日志信息说明

- **终端输出**: 每个步骤的实时进度信息（步骤1-8）
- **时间戳归档**: 每次运行自动生成 `YYYYMMDD_HHMMSS` 格式的时间戳目录
- **错误报告**: 异常信息直接输出到终端 stderr

### 6.3 查看历史运行记录

```bash
# 列出所有运行记录
ls -l results/data/
ls -l results/figures/

# 查看最新误差报告
cat results/error_report.csv
```

---

## 7. 备份恢复方案

### 7.1 代码备份（Git）

```bash
# 查看当前状态
git status

# 提交本地更改
git add .
git commit -m "feat: 添加新功能"

# 推送到远程仓库
git push origin master

# 创建版本标签备份
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0
```

### 7.2 结果数据备份

#### 时间戳归档机制

所有仿真结果自动按时间戳归档，避免了同一次运行的结果被覆盖。

```bash
# 归档格式: results/data/YYYYMMDD_HHMMSS/
# 示例: results/data/20260516_230000/
```

#### 手动备份脚本

```powershell
# Windows PowerShell 备份脚本
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup_dir = "backups/backup_$timestamp"
New-Item -Path $backup_dir -ItemType Directory -Force
Copy-Item -Path "results/" -Destination "$backup_dir/results/" -Recurse
Copy-Item -Path "config/" -Destination "$backup_dir/config/" -Recurse
Copy-Item -Path "src/" -Destination "$backup_dir/src/" -Recurse
Write-Host "备份完成: $backup_dir"
```

#### 自动化备份（crontab / Task Scheduler）

```bash
# Linux crontab - 每日凌晨2点备份
0 2 * * * cd /path/to/sod-shocktube-cfd && tar -czf backups/backup_$(date +\%Y\%m\%d).tar.gz results/ config/ src/
```

### 7.3 恢复方案

#### 代码恢复

```bash
# 从 Git 恢复特定版本
git checkout v1.3.0

# 从备份压缩包恢复
tar -xzf sod-shocktube-cfd-backup-20260516.tar.gz
```

#### 结果数据恢复

```bash
# 从时间戳目录直接访问历史结果
cd results/data/20260516_230000/
python -c "import numpy as np; data = np.load('20260516_230000_data_0.npy', allow_pickle=True).item(); print(data.keys())"
```

### 7.4 备份策略建议

| 备份类型 | 频率 | 保留策略 | 存储位置 |
|----------|------|---------|---------|
| Git 代码推送 | 每次提交 | 永久 | GitHub 远程仓库 |
| 结果数据归档 | 每次仿真 | 30天 | 本地 + 云存储 |
| 全量备份 | 每周 | 3个月 | 外部硬盘/云存储 |
| 版本标签备份 | 每个 Release | 永久 | GitHub Releases |

---

## 8. 常见部署问题

| 问题 | 解决方案 |
|------|----------|
| `pip install` 速度慢 | 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .` |
| Python 版本不匹配 | 使用 `pyenv` 或 `conda` 安装 Python 3.9-3.11 |
| 虚拟环境问题 | 删除 `venv/` 目录后重新创建 |
| 权限不足 | Linux/macOS 使用 `--user` 参数或 `sudo` |
| Git 网络问题 | 使用 SSH 协议：`git clone git@github.com:050610lzl/sod-shocktube-cfd.git` |

---

> **参考文献**:
> - Python Packaging Authority. (2023). Python Packaging User Guide. https://packaging.python.org/
> - Git Documentation. (2023). https://git-scm.com/doc