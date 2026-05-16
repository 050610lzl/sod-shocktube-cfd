# Contributing to Sod Shock Tube CFD

感谢你对本项目的关注！欢迎提交 Issue、Pull Request 或提出改进建议。

## 开发环境搭建

```bash
git clone https://github.com/050610lzl/sod-shocktube-cfd.git
cd sod-shocktube-cfd
pip install -e ".[test,dev]"
```

## 代码风格

- 遵循 PEP 8 规范
- 最大行宽 120 字符
- 运行 `flake8 src/ --max-line-length=120 --ignore=E501,W503,W504` 检查代码风格

## 提交规范

使用约定式提交 (Conventional Commits):

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码风格调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链变更

## 版本号管理

本项目遵循语义化版本规范 (SemVer 2.0.0):

```bash
# Bug 修复 → PATCH 升级
python bump_version.py patch --tag

# 新功能 → MINOR 升级
python bump_version.py minor --tag

# 不兼容变更 → MAJOR 升级
python bump_version.py major --tag
```

## 运行测试

```bash
python -m pytest tests/ -v --tb=short
```

## Pull Request 流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feat/new-scheme`)
3. 提交改动并升级版本号
4. 确保测试通过 (`pytest tests/`)
5. 推送到你的分支 (`git push origin feat/new-scheme`)
6. 提交 Pull Request 到 `master` 分支

## 添加新数值格式

1. 在 `src/fd_schemes.py` 中实现新的 step 函数
2. 在 `FD_SCHEMES` 字典中注册新格式
3. 在 `tests/test_fd_schemes.py` 中添加单元测试
4. 运行完整集成测试验证
5. 更新 README.md 中的格式列表

## 参考文献

[1] Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. *Journal of Computational Physics*, 27(1), 1-31.

[2] Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.

[3] Laney, C. B. (1998). Computational Gasdynamics. Cambridge University Press.