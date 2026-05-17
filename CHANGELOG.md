# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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

[1.4.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/050610lzl/sod-shocktube-cfd/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/050610lzl/sod-shocktube-cfd/releases/tag/v1.0.0