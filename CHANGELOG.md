# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.7.0] - 2026-05-17

### Added
- JSON 配置文件支持: `--config-json` CLI 参数 + 自动格式检测 (.yaml/.yml/.json)
- 配置文件参数验证: `validate_config()` 检查 cfl/gamma/schemes/boundary_type/n_points/t_final
- 3 个示例 JSON 配置: 默认Sod问题 / 自定义初边值条件 / HPC高分辨率
- 18 项配置加载与验证测试 (tests/test_config.py)

### Changed
- `load_config()` → `load_any_config()` 自动检测 YAML/JSON 格式
- `--config` 参数现在支持 .json 扩展名
- 测试总数从 81 项增至 99 项

## [1.6.0] - 2026-05-17

### Removed
- 移除遗留代码模块 (sod_solver.py, utils.py, validation.py, main.py)
- 清理 results/exact/ 28个旧时间戳目录

### Added
- 新增5种格式单元测试 (rusanov, godunov, roe, hllc, tvd_minmod) — 共10项
- 新增 time_marcher 模块单元测试 (7项)
- 新增 exact_solver 模块单元测试 (5项)
- 新增 tests/test_integration.py 端到端集成测试 (20项)
- bump_version.py 同步更新 pyproject.toml 和 README.md 徽章
- CI 版本一致性检查 (VERSION vs pyproject.toml)

### Changed
- 项目结构重组：25个诊断脚本归档至 tools/diagnostics/
- docs/ 诊断报告归档至 docs/99_diagnostics/，PNG图片归档至 docs/assets/images/
- CI integration job 从内联脚本改为调用 tests/test_integration.py
- 测试总数从 39 项增至 81 项

### Fixed
- 修复 pyproject.toml 版本号与 VERSION 不一致
- 修复 requirements.txt 中 flake8 被注释
- 修复 .gitignore 与实际项目结构不匹配
- 修复 bump_version.py 文件编码问题 (GBK → UTF-8)

## [1.5.2] - 2026-05-17

### Changed
- 代码架构清理：移除遗留代码 (sod_solver.py, utils.py, validation.py, main.py)
- 项目结构整合：诊断脚本归档至 tools/diagnostics/，诊断文档归档至 docs/99_diagnostics/
- 版本管理修复：bump_version.py 同步更新 pyproject.toml 和 README.md 徽章
- results/exact/ 旧时间戳目录清理，保留最新结果

### Fixed
- 修复 pyproject.toml 版本号与 VERSION 不一致问题
- 修复 requirements.txt 中 flake8 被注释问题
- 修复 .gitignore 与实际项目结构不匹配

## [1.5.1] - 2026-05-16

### Added
- docs/ 文档体系完善：新增各阶段文档子目录 (01_planning ~ 08_compliance)
- 诊断报告与 PNG 图表归档至 docs/99_diagnostics/ 和 docs/assets/images/
- CI lint job 新增 flake8 对 src/ 目录的代码风格检查

### Changed
- 项目最终报告与最终报告 PDF 移至 docs/07_delivery/
- 测试报告 v1.0 移至 docs/04_testing/

## [1.5.0] - 2026-05-16

### Added
- 多种边界条件支持：新增 reflection (固壁反射)、periodic (周期)、transmissive (无反射透射)
- 边界条件 CLI 参数 `--bc` / `--boundary` (可选 zero_gradient/reflective/periodic/transmissive)
- 初始条件 CLI 参数: `--left_rho`, `--left_u`, `--left_p`, `--right_rho`, `--right_u`, `--right_p`, `--diaphragm`
- 配置文件新增 `boundary_type` 配置项
- 5 项新单元测试覆盖全部边界条件类型

## [1.4.0] - 2026-05-16

### Added
- 完整软件交付文档体系 (27份新文档，覆盖8大类别):
  - 立项规划类: 需求规格说明书、可行性分析报告、业务流程图、立项申请书、项目计划书
  - 设计类: 总体架构设计、接口设计、模块详细设计、部署架构设计、不适用的文档说明
  - 开发类: 开发环境搭建手册、编码规范文档、源码说明文档
  - 测试类: 测试计划、性能测试报告、Bug清单与修复记录、测试用例清单
  - 部署运维类: 软件部署手册、故障排查手册
  - 使用培训类: 用户使用手册、常见问题FAQ
  - 交付验收类: 项目交付清单、功能验收确认单、项目总结报告、文档移交确认书、源代码授权说明
  - 合规附加类: 软件著作权申请材料、第三方组件开源声明

## [1.3.0] - 2026-05-16

### Added
- MIT 开源许可证 (LICENSE)
- 版本变更日志 (CHANGELOG.md)
- Python 包配置 (pyproject.toml, PEP 517/518/621)
- 贡献指南 (CONTRIBUTING.md)

### Changed
- 重写 README.md 为完整软件文档（项目背景、9种格式表、快速开始、配置说明、验证方法）

### Removed
- 移除冗余的 README_CODE.md（内容合并到 README.md）

## [1.2.0] - 2026-05-16

### Added
- 语义化版本号管理系统 (VERSION + bump_version.py)
- CI 集成版本号验证步骤

## [1.1.1] - 2026-05-16

### Fixed
- 修复 validator.py 中 f-string 语法错误
- 清理多余空行，统一代码风格

## [1.1.0] - 2026-05-16

### Added
- GitHub Actions CI 持续集成工作流
- 单元测试自动化运行
- Flake8 代码风格检查

### Fixed
- 修复全部 flake8 linting 错误
- 移除未使用的 import
- 修正续行缩进

## [1.0.1] - 2026-05-16

### Added
- 测试文档 (test.md)

## [1.0.0] - 2026-05-16

### Added
- 一维 Sod 激波管 CFD 求解器初始版本
- 9 种有限差分法数值格式:
  - Lax-Friedrichs (一阶中心耗散)
  - Lax-Wendroff (二阶中心色散)
  - MacCormack (二阶预估校正)
  - 一阶迎风 (Steger-Warming 通量分裂)
  - Rusanov (Local Lax-Friedrichs)
  - Godunov (精确 Riemann 求解器)
  - Roe (近似 Riemann 求解器)
  - HLLC (Harten-Lax-van Leer Contact)
  - TVD-Minmod (通量限制器)
- Sod 标准初始条件: 左态 (ρ=1, u=0, p=1), 右态 (ρ=0.125, u=0, p=0.1)
- Riemann 精确解求解器 (Toro 2009)
- YAML 配置文件支持
- 误差计算 (L1, L2, Linf 范数)
- 对比可视化绘图
- 时间戳归档机制
- 34 项单元测试
- 项目计划文档与构建文档

[1.7.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.5.2...v1.6.0
[1.5.2]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/050610lzl/sod-shocktube-cfd/releases/tag/v1.0.0