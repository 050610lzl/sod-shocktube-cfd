# 部署架构设计文档

## 一、部署架构概述

本项目为Python CLI科学计算工具，部署架构极为简单——单机运行模式，无需服务器集群、容器编排或负载均衡。

```
┌──────────────────────────────────────────┐
│                用户工作站                  │
│  ┌────────────────────────────────────┐  │
│  │         Python 3.9+ Runtime        │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │    sod-shocktube-cfd (CLI)   │  │  │
│  │  │  ┌────────┐ ┌─────────────┐  │  │  │
│  │  │  │  src/  │ │  config/    │  │  │  │
│  │  │  │ 求解器  │ │  YAML配置   │  │  │  │
│  │  │  └────────┘ └─────────────┘  │  │  │
│  │  │  ┌────────┐ ┌─────────────┐  │  │  │
│  │  │  │results/│ │   docs/     │  │  │  │
│  │  │  │输出归档 │ │  项目文档   │  │  │  │
│  │  │  └────────┘ └─────────────┘  │  │  │
│  │  └──────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │         依赖库 (site-packages)      │  │
│  │  NumPy / SciPy / Matplotlib / ...  │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │          操作系统 (Win/Linux/macOS)  │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│            GitHub (远程仓库)              │
│  ┌────────────────┐ ┌─────────────────┐  │
│  │   Git仓库       │ │  GitHub Actions │  │
│  │  源码+文档+tag  │ │  CI/CD流水线    │  │
│  └────────────────┘ └─────────────────┘  │
└──────────────────────────────────────────┘
```

## 二、部署模式

### 2.1 本地开发部署

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
pip install -e ".[test,dev]"
```

适用于开发、调试、修改代码的场景。

### 2.2 用户使用部署

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
pip install -r requirements.txt
python run_simulation.py
```

适用于仅运行仿真、不修改代码的场景。

### 2.3 离线部署

将源码包拷贝到目标机器：
```bash
# 在联网机器上导出依赖
pip download -r requirements.txt -d ./offline_packages

# 拷贝源码包 + offline_packages 到目标机器
# 在目标机器上安装
pip install --no-index --find-links=./offline_packages -r requirements.txt
```

## 三、环境要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10 / Ubuntu 20.04 / macOS 12 | Windows 11 / Ubuntu 22.04 |
| Python | 3.9 | 3.11 |
| 内存 | 512 MB | 2 GB |
| 磁盘 | 100 MB | 500 MB |
| 网络 | 仅安装时需要 | 按需 |

## 四、CI/CD 部署架构

```
GitHub Push
     │
     ▼
GitHub Actions
     │
     ├── job: test (矩阵: Python 3.9, 3.10, 3.11)
     │   ├── Checkout code (actions/checkout@v4)
     │   ├── Verify version (VERSION文件验证)
     │   ├── Setup Python (actions/setup-python@v5)
     │   ├── Install dependencies (pip install -r requirements.txt)
     │   ├── Run unit tests (pytest --junitxml)
     │   ├── Run single scheme validation
     │   ├── Run CFL stability check
     │   └── Upload test artifacts
     │
     ├── job: lint
     │   ├── Checkout code
     │   ├── Setup Python 3.11
     │   └── Run flake8 src/
     │
     └── job: integration
         ├── Checkout code
         ├── Verify version
         ├── Setup Python 3.11
         ├── Install dependencies
         └── Run all 9 schemes integration test
```

## 五、版本发布流程

```
1. 本地开发 & 测试通过
         │
2. bump_version.py minor --tag
         │  (更新VERSION、创建git tag)
         │
3. git push origin master --tags
         │
4. GitHub Actions 自动运行CI
         │
5. CI全部通过
         │
6. GitHub Release 页面自动显示新tag
         │
7. 用户 git pull 获取最新版本
```

## 六、扩展性考虑

| 场景 | 方案 |
|------|------|
| 新增数值格式 | 在fd_schemes.py中添加step函数 → 注册到FD_SCHEMES → 添加测试 → bump_version minor |
| 新增2D求解器 | 新建模块 → 独立目录 → 复用现有网格/边界/验证框架 |
| 并行计算 | 引入Numba/MPI → 修改time_marcher → bump_version major |
| Web服务化 | FastAPI封装 → 新增web/目录 → 设计REST API → bump_version major |

## 七、监控与运维

本软件为离线CLI工具，无运行时监控需求。运维关注点：

| 关注点 | 方案 |
|--------|------|
| 版本追踪 | VERSION文件 + git tag + CHANGELOG.md |
| 错误日志 | 控制台输出 + 仿真参数日志 |
| 结果归档 | 时间戳文件夹 (results/data/YYYYMMDD_HHMMSS/) |
| 备份恢复 | Git仓库即为完整备份 |

---

*文档版本: v1.0 | 更新日期: 2026-05-16*