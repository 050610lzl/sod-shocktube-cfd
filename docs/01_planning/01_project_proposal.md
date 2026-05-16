# 项目立项申请书

## 一、项目基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 一维Sod激波管CFD求解器 (Sod Shock Tube CFD Solver) |
| 项目类型 | 科学计算软件开发 |
| 开发语言 | Python 3.9+ |
| 开源协议 | MIT License |
| 项目仓库 | https://github.com/050610lzl/sod-shocktube-cfd |
| 申报日期 | 2026年4月 |

## 二、项目背景

Sod激波管问题是计算流体力学(CFD)领域的经典基准测试，由G. A. Sod于1978年在《Journal of Computational Physics》上提出。该问题模拟一维管道中高压区与低压区之间的隔膜破裂后产生的波系传播过程，包含激波、接触间断和稀疏波三种典型流动特征。

本项目旨在开发一个模块化、可扩展的一维Sod激波管CFD求解器，实现多种经典有限差分法(FDM)数值格式，为CFD教学、算法研究和数值方法验证提供标准化工具。

## 三、项目目标

### 3.1 总体目标
构建一个功能完整的一维Sod激波管CFD求解软件，实现9种经典有限差分法数值格式，支持精确解对比、误差分析和可视化。

### 3.2 具体目标

| 目标 | 指标 | 验证方法 |
|------|------|----------|
| 格式完整性 | 实现9种FDM格式 | 全部格式通过集成测试 |
| 数值正确性 | 各格式L1误差 < 1e-2 (N=100) | 与Riemann精确解对比 |
| 收敛性 | 一阶格式收敛阶 ~1.0，二阶 ~2.0 | 网格加密测试 |
| 代码质量 | flake8零错误、34项单元测试通过 | CI自动检查 |
| 文档完备性 | 8大类40+份交付文档 | 文档清单核对 |
| 可复现性 | 一键运行、时间戳归档 | CI集成测试 |

## 四、技术方案概要

### 4.1 数值方法
- 控制方程：一维Euler方程（守恒形式）
- 离散方法：有限差分法(FDM)
- 数值格式：Lax-Friedrichs, Lax-Wendroff, MacCormack, Upwind(Steger-Warming), Rusanov, Godunov, Roe, HLLC, TVD-Minmod
- 精确解：基于Toro (2009)的Riemann精确求解器

### 4.2 技术选型
- Python 3.9+: 主编程语言
- NumPy: 数值计算核心
- SciPy: 非线形方程求解(brentq)
- Matplotlib: 可视化
- PyYAML: 配置文件解析
- pytest: 自动化测试
- GitHub Actions: CI/CD

### 4.3 项目周期
预计开发周期：8周（2026年4月–2026年6月）

## 五、预期成果

### 5.1 软件成果
- 核心求解器源码（8个模块，~2500行）
- 9种FDM格式的完整实现
- 34项单元测试（覆盖率>90%）
- CI/CD持续集成流水线

### 5.2 文档成果
- 需求规格说明书、架构设计文档、接口设计文档
- 模块详细设计文档、开发环境手册、编码规范
- 测试计划、性能测试报告、Bug清单
- 部署手册、用户手册、FAQ
- 交付清单、验收单、总结报告
- 著作权申请材料、第三方开源声明

### 5.3 学术价值
- 为CFD教学提供标准化基准求解器
- 验证经典文献(Sod 1978)的数值结论
- 提供多种格式的定量对比数据

## 六、项目组织

| 角色 | 职责 |
|------|------|
| 项目负责人 | 总体设计、算法实现、文档审核 |
| 数值算法开发 | 9种FDM格式实现与调优 |
| 测试验证 | 单元测试、集成测试、收敛性验证 |
| 文档编写 | 8大类软件交付文档 |

## 七、经费预算

本项目为开源学术软件，采用零成本方案：
- 开发工具：免费开源（Python, VS Code, Git）
- 计算资源：个人计算机即可满足
- 托管平台：GitHub免费仓库+Actions CI
- 总预算：0元

## 八、审批意见

| 角色 | 意见 | 签字 | 日期 |
|------|------|------|------|
| 项目负责人 | | | |
| 技术评审 | | | |
| 批准人 | | | |

## 参考文献

[1] Sod, G. A. (1978). A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws. J. Comput. Phys., 27(1), 1-31.
[2] Toro, E. F. (2009). Riemann Solvers and Numerical Methods for Fluid Dynamics. Springer.
[3] Laney, C. B. (1998). Computational Gasdynamics. Cambridge University Press.