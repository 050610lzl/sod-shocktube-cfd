# 项目可行性分析报告

## 一维Sod激波管CFD数值格式对比项目

| 项目 | 内容 |
|------|------|
| 文档编号 | FA-SOD-CFD-1.0 |
| 版本号 | 1.0 |
| 编制日期 | 2026-05-16 |
| 编制人 | CFD课程项目组 |
| 项目名称 | 一维Sod激波管CFD数值格式对比 |
| 报告结论 | **可行** |

---

## 摘要

本报告对"一维Sod激波管CFD数值格式对比项目"从技术、经济、操作、进度四个维度进行系统可行性分析，并对潜在风险进行了识别与评估。分析结论为：项目完全可行。该结论基于以下核心判断：（1）Sod激波管问题已存在公认的解析精确解与丰富的数值格式文献支撑；（2）Python+NumPy+SciPy开源技术栈完全满足求解需求；（3）模块化架构支持增量开发与迭代验证。

---

## 1. 技术可行性

### 1.1 算法成熟度

本项目涉及的所有核心算法均为CFD领域的经典方法，在公开文献中已得到充分验证：

**（1）Sod激波管问题定义**

Sod激波管问题的标准初始条件由Sod(1978)在其经典论文中提出[1]。该问题已成为CFD领域最广泛使用的验证基准之一，近半个世纪来被数千篇学术论文引用。问题的初始条件、边界条件、输出时刻均已标准化，不存在模糊或争议。

**初始条件**（Sod, 1978[1]）：
$$(\rho_L, u_L, p_L) = (1.0, 0.0, 1.0), \quad (\rho_R, u_R, p_R) = (0.125, 0.0, 0.1), \quad x_{\text{diaphragm}} = 0.5, \quad \gamma = 1.4, \quad t_{\text{output}} = 0.2$$

**（2）Riemann精确解**

Toro(2009)在其权威教材[2]第4章中给出了Euler方程Riemann问题精确解的完整算法，包括压力方程$f(p_*)=0$的Newton迭代求解、稀疏波区等熵关系、激波Rankine-Hugoniot条件等。该算法可通过SciPy的`brentq`函数（Brent方法）直接实现，无需自行开发迭代器[2]。

**（3）9种数值格式**

本项目拟实现的9种有限差分格式均为CFD领域的经典方法，每种的离散公式均在公开文献中有明确记载：

| 编号 | 格式名称 | 核心文献 | 精度的理论阶 |
|------|---------|---------|------------|
| FDM-1 | Lax-Friedrichs | Sod(1978)[1], LeVeque(1992)[4] | $O(\Delta x) + O(\Delta t)$ |
| FDM-2 | Lax-Wendroff | Sod(1978)[1], Lax & Wendroff(1960) | $O(\Delta x^2) + O(\Delta t^2)$ |
| FDM-3 | MacCormack | Sod(1978)[1], MacCormack(1969) | $O(\Delta x^2) + O(\Delta t^2)$ |
| FDM-4 | 一阶迎风(Steger-Warming) | Laney(1998)[3], Steger & Warming(1981) | $O(\Delta x) + O(\Delta t)$ |
| FDM-5 | Rusanov(局部Lax-Friedrichs) | Toro(2009)[2], Rusanov(1961) | $O(\Delta x) + O(\Delta t)$ |
| FDM-6 | Godunov(精确Riemann) | Toro(2009)[2], Godunov(1959) | $O(\Delta x) + O(\Delta t)$ |
| FDM-7 | Roe(近似Riemann) | Toro(2009)[2], Roe(1981) | $O(\Delta x) + O(\Delta t)$ |
| FDM-8 | HLLC | Toro(2009)[2], Toro et al.(1994) | $O(\Delta x) + O(\Delta t)$ |
| FDM-9 | TVD-Minmod | Harten(1983)[5], Toro(2009)[2] | $O(\Delta x^2)$(光滑区) |

**判断**：所有算法均经过学术界长期验证与广泛使用，算法成熟度极高，不存在根本性的理论风险。

### 1.2 开源生态支撑

本项目的技术实现完全依赖Python开源科学计算生态：

| 依赖库 | 版本要求 | 在本项目中的用途 | 开源许可证 | 成熟度 |
|--------|---------|----------------|-----------|--------|
| NumPy | >= 1.20 | 多维数组运算、向量化计算 | BSD-3 | 极为成熟(2005年至今) |
| SciPy | >= 1.7 | `brentq`求解非线性方程（精确Riemann解） | BSD-3 | 极为成熟(2001年至今) |
| Matplotlib | >= 3.4 | 对比图绘制（4幅子图布局） | PSF-based | 极为成熟(2003年至今) |
| PyYAML | >= 5.4 | YAML配置文件解析 | MIT | 成熟(2006年至今) |

**判断**：全部依赖库均为Python科学计算的标准库，经过长期维护和广泛使用，稳定性与可靠性有充分保证。不依赖任何商业软件或专有库，符合开源合规要求。

### 1.3 文献支撑充分性

本项目已有以下核心文献的充分支撑：

- **Sod(1978)[1]**：问题的完整定义、7种格式的对比结果（作为本项目benchmark基准）
- **Toro(2009)[2]**：Riemann问题理论、精确解算法、Riemann求解器格式的完整推导
- **Laney(1998)[3]**：可压缩流CFD基础、离散格式的物理解释、验证方法论
- **LeVeque(1992)[4]**：守恒律数值方法的数学基础、稳定性分析
- **Harten(1983)[5]**：TVD格式的原始论文、Minmod限制器的完整定义
- **OneFlow-CFD文档[6]**：问题设置的外部参考源

此外，Roe(1981)、Steger & Warming(1981)、MacCormack(1969)等原始论文为各格式的实现提供了直接的第一手文献依据。

**判断**：文献支撑体系完整，覆盖问题的数学建模、算法推导到结果验证的全流程。所有关键决策点均有文献背书。

### 1.4 技术难度评估

| 技术挑战 | 难度评级 | 应对策略 |
|---------|---------|---------|
| 一维Euler方程离散化 | 低 | 各格式的离散公式在文献中有明确的数学表达式 |
| 精确Riemann解迭代求解 | 中 | 使用SciPy的`brentq`封装，无需手写迭代器[2] |
| Roe格式熵修复 | 中 | Toro(2009)[2]第11章提供了Harten熵修复的完整算法 |
| TVD限制器实现 | 中 | Minmod限制器为最简单的限制器，实现约10行代码[5] |
| 边界条件处理 | 低 | 已实现4种边界条件(zero_gradient/reflective/periodic/transmissive)，覆盖一维CFD仿真常见需求 |
| CFL自适应时间步长 | 低 | 经典公式$\Delta t = \text{CFL} \cdot \Delta x / \max(|u|+c)$ |

**判断**：总体技术难度适中，适合CFD课程项目的学习目标。最复杂的部分（精确Riemann解和TVD格式）在文献中均有详尽的算法描述。

---

## 2. 经济可行性

### 2.1 成本分析

| 成本类别 | 项目 | 费用 |
|---------|------|------|
| **软件许可** | Python 3.8+ | 免费（PSF License） |
| | NumPy | 免费（BSD） |
| | SciPy | 免费（BSD） |
| | Matplotlib | 免费（PSF-based） |
| | PyYAML | 免费（MIT） |
| **开发工具** | VS Code / PyCharm Community | 免费 |
| | Git (版本控制) | 免费 |
| **硬件** | 常规PC/笔记本电脑 | 学员自有设备 |
| **云服务** | 无（本机运行） | 0 |
| **文献获取** | 通过学校图书馆或SCI-Hub | 学校已订阅核心期刊 |
| **合计** | | **0元人民币** |

### 2.2 效益分析

虽然本项目为课程教学项目，不直接产生经济效益，但具有显著的学术与教育效益：

1. **教学效益**：通过亲手实现9种经典数值格式，学员可深入理解数值耗散、数值色散、CFL条件、TVD性质等CFD核心概念[3][4]。
2. **可复用性**：项目产出的代码可作为后续CFD课程的教学范例或学生的参考实现。
3. **学术积累**：系统的格式对比结果可作为小型学术论文或课程报告的主体内容。

### 2.3 经济可行性结论

项目采用**完全零成本的开源技术方案**，无需任何商业软件、云计算资源或专用硬件。经济层面不存在任何障碍，可行性评级为**高**。

---

## 3. 操作可行性

### 3.1 用户操作复杂度

本软件的操作入口极为简洁：

**方式一：命令行一键运行**
```bash
python main.py
```
该命令将自动完成网格生成、流场初始化、9种格式求解、精确解计算、误差分析、可视化输出的全流程。

**方式二：选择性运行单个格式**
```bash
python main.py --scheme roe --n_points 200
```

**方式三：通过YAML配置文件自定义参数**
```yaml
# config/simulation_config.yaml
mesh:
  n_points: 200
simulation:
  cfl: 0.9
schemes:
  - roe
  - hllc
```

### 3.2 环境搭建难度

| 步骤 | 操作 | 预计耗时 |
|------|------|---------|
| 安装Python 3.8+ | 从python.org下载安装包，双击安装 | 5分钟 |
| 安装依赖库 | `pip install -r requirements.txt` | 2分钟 |
| 验证环境 | `python -c "import numpy, scipy, matplotlib"` | 1分钟 |
| **合计** | | **约8分钟** |

### 3.3 用户体验保障

- 程序运行过程中输出进度信息（步数、当前时间、时间步长）
- 错误提示明确（无效格式名时输出可用格式列表、CFL超限时警告）
- 输出文件组织清晰（按数据类型分目录存放）
- 对比图标注完整（标题含格式名、网格数、时间、CFL数）

### 3.4 操作可行性结论

软件操作极为简便，仅需基础的命令行使用能力。环境搭建耗时短、依赖库安装自动化程度高。操作可行性评级为**高**。

---

## 4. 进度可行性

### 4.1 模块化架构的优势

本项目的模块化架构天然支持增量开发与迭代验证：

```
src/
├── mesh_generator.py      # 模块1: 网格生成 (独立, 无依赖)
├── flow_initializer.py    # 模块2: 流场初始化 (依赖模块1)
├── fd_schemes.py          # 模块3: 数值格式 (依赖模块2)
├── time_marcher.py        # 模块4: 时间推进 (依赖模块3)
├── boundary_handler.py    # 模块5: 边界条件 (依赖模块3)
├── exact_solver.py        # 模块6: 精确解 (独立)
├── validator.py           # 模块7: 误差分析 (依赖3+6)
└── output_writer.py       # 模块8: 结果输出 (依赖3+6+7)
```

### 4.2 增量交付计划

| 阶段 | 周次 | 交付物 | 可验证性 |
|------|------|--------|---------|
| Plan阶段 | 第1周 | 项目计划书、SRS文档、可行性报告 | 文档审查 |
| 基础框架 | 第2周 | 网格生成+流场初始化+精确解 | 精确解图像与Toro(2009)对比 |
| 简单格式 | 第3周 | Lax-Friedrichs + Lax-Wendroff + MacCormack | 与Sod(1978)原始结果对比 |
| 进阶格式 | 第4周 | Upwind + Rusanov + Godunov + Roe + HLLC | 间断面捕捉效果定性评估 |
| 高阶格式 | 第5周 | TVD-Minmod + 全格式误差分析 | 网格收敛性验证 |
| 收尾 | 第6周 | 完整报告撰写 | 报告完整性审查 |

### 4.3 关键风险评估

| 风险项 | 影响 | 缓解措施 |
|--------|------|---------|
| 精确解计算错误 | 导致所有格式的误差分析无效 | 用Toro(2009)中的标准算例结果进行交叉验证 |
| Roe格式跨音速异常 | 膨胀激波导致非物理解 | 参考文献[2]实现Harten熵修复 |
| MacCormack格式对称性 | 非对称数值耗散 | 实现交替方向策略（Laney, 1998[3]） |
| TVD格式密度/压力为负 | 数组运算崩溃 | 添加退化为低阶格式的保护机制[5] |

### 4.4 进度可行性结论

模块化架构支持每个模块的独立开发与测试，格式实现可依次增量添加。每增加一种格式后，可立即用精确解进行验证，形成"编码-验证"的快速迭代闭环。进度可行性评级为**高**。

---

## 5. 风险分析

### 5.1 风险识别与评估矩阵

风险等级 = 发生概率(P) x 影响程度(I)。评分标准：低(1)、中(2)、高(3)。

| 风险编号 | 风险描述 | 类别 | P | I | 等级 | 应对措施 |
|---------|---------|------|---|---|------|---------|
| R-01 | 精确Riemann解迭代不收敛 | 技术 | 1 | 3 | 中 | 使用SciPy的`brentq`并设置宽松容差；参考Toro(2009)的初始猜测策略[2] |
| R-02 | Roe格式在跨音速点产生膨胀激波 | 技术 | 2 | 2 | 中 | 实现Harten熵修复[5]，与无修复结果对比确认问题解决 |
| R-03 | 高CFL数下Lax-Wendroff格式振荡发散 | 技术 | 2 | 2 | 中 | 默认CFL=0.8，提供--cfl参数让用户自行调低 |
| R-04 | SciPy的brentq依赖导致环境安装失败 | 技术 | 1 | 2 | 低 | requirements.txt锁定版本，提供conda替代方案 |
| R-05 | N=100网格下求解超5秒 | 性能 | 1 | 2 | 低 | 使用NumPy向量化操作替代Python循环；预分配数组 |
| R-06 | Python环境差异导致跨平台行为不一致 | 兼容性 | 2 | 1 | 低 | 使用纯Python依赖，CI中包含Windows/macOS/Linux三平台测试 |
| R-07 | 进度因调试复杂格式而延误 | 进度 | 2 | 2 | 中 | 先实现简单格式快速产出结果，复杂格式逐步添加；预留缓冲时间 |
| R-08 | 错误报告中误差值异常（如负值或过大） | 质量 | 1 | 2 | 低 | 每个格式完成后立即运行validator模块验证误差合理性 |

### 5.2 风险应对策略详述

#### R-01: 精确Riemann解迭代不收敛

**原因分析**：压力方程$f(p_*)=0$在极端压力比下可能呈现病态[2]。
**缓解措施**：
- 使用SciPy的`brentq`函数，该算法对有界区间内的连续函数保证收敛
- 设置搜索区间为$[10^{-10}, \max(p_L, p_R) \times 2.0]$，覆盖Sod问题的理论$p_*$范围
- 如收敛失败，回退到PVRS（Primitive Variable Riemann Solver）近似解[2]

#### R-02: Roe格式膨胀激波

**原因分析**：Roe格式在特征值过零时不满足熵条件，可能在跨音速稀疏波处产生非物理的膨胀激波[2]。
**缓解措施**：实现Harten熵修复，将$|\lambda|$在零点附近的光滑化[5]：
$$|\lambda|_{\text{fix}} = \begin{cases} |\lambda|, & |\lambda| \ge \varepsilon \\ (\lambda^2 + \varepsilon^2)/(2\varepsilon), & |\lambda| < \varepsilon \end{cases}$$
其中$\varepsilon = \max(0, \lambda_R - \lambda_L)$为跨波特征值的变化量。

#### R-07: 进度延误

**缓解措施**：
- 第3周完成3种简单格式（Lax-Friedrichs, Lax-Wendroff, MacCormack），确保有可展示的初步结果
- 第4周完成剩余格式的实现，如时间不足可暂缓TVD格式（其功能可由Roe格式近似替代）
- 预留1周缓冲时间（总周期6周，实际工作量5周）

---

## 6. 综合结论

### 6.1 四维可行性汇总

| 可行性维度 | 评级 | 核心理由 |
|-----------|------|---------|
| 技术可行性 | **高** | 算法成熟(文献验证40+年)、Python科学计算生态完备、文献支撑充分 |
| 经济可行性 | **高** | 零成本开源方案，无任何商业软件、云服务或专用硬件需求 |
| 操作可行性 | **高** | 单一CLI入口、YAML配置简单、环境搭建约8分钟 |
| 进度可行性 | **高** | 模块化架构、增量交付、每阶段产出可独立验证 |

### 6.2 总体结论

**项目完全可行，建议批准立项。**

本项目具备以下显著优势：

1. **学术价值明确**：通过系统对比9种经典数值格式在Sod激波管问题上的表现，可直观展示数值耗散、数值色散、TVD性质等CFD核心概念[1][2][3]。
2. **风险可控**：所有技术难题在公开文献中均有成熟的解决方案，不存在需要自行探索的未知领域。
3. **资源需求低**：零成本开源方案，学员自有PC即可完成全部开发与运算。
4. **产出可复用**：项目代码可作为后续CFD教学的示范案例或学生实践的参考模板。

### 6.3 建议

1. **优先保证正确性**：建议优先确保精确解和简单格式（Lax-Friedrichs）的结果与Sod(1978)[1]的原始数据一致，再逐步添加其他格式。
2. **建立验证基准**：在第2周精确解完成后，立即用Toro(2009)[2]中的标准算例结果进行交叉验证，确保整个项目的基准正确。
3. **网格收敛性分析**：如时间允许，建议在N={100, 200, 400}三个分辨率上进行网格收敛性分析，以考察各格式的实际精度阶[4]。

---

## 参考文献

[1] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31.

[2] TORO E F. Riemann solvers and numerical methods for fluid dynamics: a practical introduction[M]. 3rd ed. Berlin: Springer, 2009.

[3] LANEY C B. Computational gasdynamics[M]. Cambridge: Cambridge University Press, 1998.

[4] LEVEQUE R J. Numerical methods for conservation laws[M]. 2nd ed. Basel: Birkhauser, 1992.

[5] HARTEN A. High resolution schemes for hyperbolic conservation laws[J]. Journal of Computational Physics, 1983, 49(3): 357-393.

[6] OneFlow-CFD Documentation. Sod shock tube example[EB/OL]. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html.

[7] ROE P L. Approximate Riemann solvers, parameter vectors, and difference schemes[J]. Journal of Computational Physics, 1981, 43(2): 357-372.

[8] STEGER J L, WARMING R F. Flux vector splitting of the inviscid gasdynamic equations with application to finite-difference methods[J]. Journal of Computational Physics, 1981, 40(2): 263-293.

[9] MACORMACK R W. The effect of viscosity in hypervelocity impact cratering[C]//AIAA Hypervelocity Impact Conference. Cincinnati, Ohio: AIAA, 1969: 69-354.

[10] OBERKAMPF W L, TRUCANO T G. Verification and validation in computational fluid dynamics[J]. Progress in Aerospace Sciences, 2002, 38(3): 209-272.

---

**文档控制信息**：
- 编制：CFD课程项目组 | 2026-05-16
- 审核：--（待审核）
- 批准：--（待批准）