# 开发环境搭建手册

> 文档版本: v1.0  
> 项目: 一维Sod激波管CFD求解器 (sod-shocktube-cfd)

---

## 1. 系统要求

### 1.1 操作系统

| 操作系统 | 最低版本 | 备注 |
|----------|----------|------|
| Windows | Windows 10 (64-bit) | PowerShell 5.1+ |
| macOS | macOS 11 (Big Sur) | 需要 Xcode Command Line Tools |
| Linux | Ubuntu 20.04 / CentOS 7 | glibc 2.17+ |

### 1.2 Python 版本

- **最低要求**: Python 3.9
- **推荐版本**: Python 3.10 或 3.11
- **不支持**: Python 2.x, Python 3.8 及以下

检查当前 Python 版本:

```bash
python --version
# 输出示例: Python 3.11.4
```

### 1.3 硬件要求

| 资源 | 最低要求 | 推荐配置 |
|------|----------|----------|
| RAM | 512 MB | 2 GB+ |
| 磁盘空间 | 100 MB | 500 MB+ (含生成结果) |
| CPU | 任意 x86_64/arm64 | 4 核+ (加速 Godunov 格式) |

项目为纯 CPU 计算, 无需 GPU。

### 1.4 网络要求

- 初始安装: 需要网络连接以下载依赖 (PyPI)
- 运行阶段: 不需要网络

---

## 2. Python 环境配置

### 2.1 使用 venv (推荐, 跨平台)

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# 3. 确认 Python 路径指向 venv
# Windows:
where python
# macOS / Linux:
which python
# 应输出: .../venv/bin/python (或 ...\venv\Scripts\python.exe)

# 4. 升级 pip (可选但推荐)
python -m pip install --upgrade pip setuptools wheel
```

### 2.2 使用 conda (可选)

```bash
# 1. 创建 conda 环境
conda create -n sod-cfd python=3.11 -y

# 2. 激活环境
conda activate sod-cfd

# 3. 确认版本
python --version
```

### 2.3 退出虚拟环境

```bash
# venv:
deactivate

# conda:
conda deactivate
```

---

## 3. 项目获取

```bash
# 克隆仓库
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd

# 或者直接使用本地目录
cd e:\trae_project\a
```

---

## 4. 依赖安装

### 4.1 核心依赖安装

```bash
# 方式1: 开发模式安装 (推荐, 代码修改即时生效)
pip install -e .

# 方式2: 标准安装
pip install .
```

此命令将安装 `pyproject.toml` 中 `dependencies` 列出的核心依赖:
- `numpy>=1.21.0,<2.0.0`
- `matplotlib>=3.5.0`
- `pyyaml>=6.0`
- `scipy>=1.7.0`

### 4.2 安装测试和开发依赖

```bash
# 安装测试依赖 (pytest)
pip install -e ".[test]"

# 安装开发依赖 (flake8)
pip install -e ".[dev]"

# 同时安装所有可选依赖
pip install -e ".[test,dev]"
```

### 4.3 从 requirements.txt 安装 (备选)

```bash
pip install -r requirements.txt
```

### 4.4 验证安装

```bash
# 检查核心包版本
python -c "import numpy; print('NumPy', numpy.__version__)"
python -c "import scipy; print('SciPy', scipy.__version__)"
python -c "import matplotlib; print('Matplotlib', matplotlib.__version__)"
python -c "import yaml; print('PyYAML', yaml.__version__)"

# 检查项目模块可导入
python -c "from src.mesh_generator import generate_mesh; print('mesh_generator OK')"
python -c "from src.flow_initializer import initialize_flow; print('flow_initializer OK')"
python -c "from src.fd_schemes import FD_SCHEMES; print('fd_schemes OK:', list(FD_SCHEMES.keys()))"
python -c "from src.boundary_handler import apply_boundary_condition; print('boundary_handler OK')"
python -c "from src.time_marcher import compute_dt; print('time_marcher OK')"
python -c "from src.exact_solver import sod_exact_solution; print('exact_solver OK')"
python -c "from src.output_writer import save_results; print('output_writer OK')"
python -c "from src.validator import compute_errors; print('validator OK')"
```

预期输出: 每个模块打印 "OK" 或格式列表。

---

## 5. IDE 配置

### 5.1 推荐 IDE

| IDE | 推荐度 | 说明 |
|-----|--------|------|
| VS Code | 强烈推荐 | 免费, Python 支持优秀, 扩展丰富 |
| PyCharm Professional | 推荐 | 强大的科学计算支持 |
| PyCharm Community | 可选 | 功能较 Pro 版少 |

### 5.2 VS Code 配置

#### 推荐扩展

在 VS Code 中安装以下扩展 (Ctrl+Shift+X):

| 扩展 ID | 用途 |
|---------|------|
| `ms-python.python` | Python 语言支持 |
| `ms-python.flake8` | 代码风格检查 |
| `ms-python.vscode-pylance` | 智能代码补全 |
| `tamasfe.even-better-toml` | pyproject.toml 支持 |
| `redhat.vscode-yaml` | YAML 语法高亮 |
| `eamodio.gitlens` | Git 增强工具 |

#### 工作区设置 (`.vscode/settings.json`)

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--max-line-length=120",
        "--extend-ignore=E203,W503"
    ],
    "python.formatting.provider": "none",
    "[python]": {
        "editor.rulers": [120],
        "editor.tabSize": 4,
        "editor.insertSpaces": true,
        "editor.detectIndentation": false
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### 启动配置 (`.vscode/launch.json`)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Simulation (Default Config)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run_simulation.py",
            "console": "integratedTerminal"
        },
        {
            "name": "Run Simulation (Single Scheme)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run_simulation.py",
            "args": ["--scheme", "roe", "--n_points", "100"],
            "console": "integratedTerminal"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### 5.3 PyCharm 配置

1. **设置 Python 解释器**: File > Settings > Project > Python Interpreter > 选择 `venv/bin/python`
2. **代码风格**: File > Settings > Editor > Code Style > Python
   - Tab size: 4
   - Hard wrap at: 120
3. **运行配置**: Run > Edit Configurations > 添加 Python 脚本 `run_simulation.py`

---

## 6. Git 配置与工作流

### 6.1 初始配置

```bash
# 设置用户信息
git config user.name "你的名字"
git config user.email "your.email@example.com"

# 设置默认分支名
git config init.defaultBranch main

# 查看配置
git config --list
```

### 6.2 分支模型

本项目采用简单的功能分支工作流:

```
main (stable)
  |
  +-- feature/xxx  (新功能开发)
  +-- fix/xxx      (Bug 修复)
  +-- docs/xxx     (文档更新)
```

### 6.3 工作流示例

```bash
# 1. 确保 main 分支最新
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/new-scheme

# 3. 开发和提交
# ... 编辑代码 ...
git add src/new_scheme.py
git commit -m "feat: add New Scheme for solving Sod problem"

# 4. 推送到远程
git push origin feature/new-scheme

# 5. 创建 Pull Request (在 GitHub 上操作)

# 6. 合并后删除分支
git checkout main
git pull origin main
git branch -d feature/new-scheme
```

### 6.4 提交规范

参见 [编码规范文档 §6 提交规范](03_coding_standards.md#6-提交规范)。

---

## 7. 验证安装

### 7.1 运行单元测试

```bash
# 安装测试依赖 (如果尚未安装)
pip install -e ".[test]"

# 运行全部测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_mesh.py -v
pytest tests/test_initialization.py -v
pytest tests/test_fd_schemes.py -v
pytest tests/test_boundary.py -v

# 显示测试覆盖率 (需要 pytest-cov)
pip install pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing
```

### 7.2 运行仿真验证

```bash
# 快速验证 (单个格式, 少量网格)
python run_simulation.py --scheme lax_friedrichs --n_points 100

# 完整验证 (所有格式)
python run_simulation.py

# 网格收敛性测试 (3种分辨率)
python run_simulation.py --schemes lax_friedrichs roe --n_points 100
python run_simulation.py --schemes lax_friedrichs roe --n_points 200
python run_simulation.py --schemes lax_friedrichs roe --n_points 400
```

### 7.3 代码风格检查

```bash
# 安装开发依赖 (如果尚未安装)
pip install -e ".[dev]"

# 运行 flake8 检查
flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
flake8 tests/ --max-line-length=120 --extend-ignore=E203,W503
```

### 7.4 完整的安装验证清单

运行以下命令, 全部通过则表示环境搭建成功:

```bash
# 1. Python 版本
python --version

# 2. 核心依赖
python -c "import numpy; print('numpy:', numpy.__version__)"
python -c "import scipy; print('scipy:', scipy.__version__)"
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"
python -c "import yaml; print('pyyaml:', yaml.__version__)"

# 3. 项目模块
python -c "from src import generate_mesh, initialize_flow, FD_SCHEMES, sod_exact_solution; print('All imports OK')"

# 4. 测试
pytest tests/ -v --tb=short

# 5. 仿真运行 (快速测试)
python run_simulation.py --scheme lax_friedrichs --n_points 50 --cfl 0.5
```

预期结果:
- 所有 import 成功, 无 `ModuleNotFoundError`
- 所有测试通过 (29 项单元测试)
- 仿真运行完成, 在 `results/` 下生成文件

---

## 8. 常见问题

### Q1: `pip install -e .` 报错 "No module named setuptools"

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -e .
```

### Q2: Matplotlib 报错 "UserWarning: Matplotlib is currently using agg"

这是正常的 —— 项目强制使用 `Agg` 后端 (无 GUI), 适合脚本和 CI 环境。如需交互式绘图, 注释 [validator.py](file:///e:/trae_project/a/src/validator.py#L12) 中的 `matplotlib.use('Agg')`。

### Q3: Windows PowerShell 执行策略阻止 venv 激活

```powershell
# 以管理员身份运行 PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q4: Godunov 格式运行非常慢

Godunov 格式每个界面都调用 `scipy.optimize.brentq` 求解非线性方程, 在 N=100 时需要约 99*(步数) 次迭代。这是预期行为。建议:
- 使用较小的网格 (`--n_points 50`) 进行 Godunov 调试
- 使用 Roe 或 HLLC 作为更快的替代方案

---

## 参考文献

1. OneFlow-CFD Documentation. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html
2. VS Code Python Tutorial. https://code.visualstudio.com/docs/python/python-tutorial