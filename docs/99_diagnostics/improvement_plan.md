# 一维Sod激波管CFD项目 改进计划（85分 -> 95分）

**制定日期**: 2026-05-06  
**项目路径**: `e:\trae_project\a\`  
**当前评分**: 85/100  
**目标评分**: 95/100  
**依据文献**: 基于前次验证报告（`results/validation_report.md`、`results/project_requirements_validation.md`）及学术文献

---

## 1. 改进项总览与优先级排序

| 优先级 | 编号 | 改进项 | 严重性 | 涉及类型 | 预计工作量 | 分值贡献 |
|--------|------|--------|--------|----------|------------|----------|
| **P0** | IMP-01 | 实现TVD格式（Minmod限制器） | 严重 | 代码实现 | 高 | +3~4 |
| **P0** | IMP-02 | 补充TVD格式网格收敛数据（N=100/200/400/800） | 严重 | 运行+文档 | 中 | +1~2 |
| **P1** | IMP-03 | 分析并改善MacCormack收敛阶（当前0.18，理论应为二阶） | 中等 | 代码+文档 | 中 | +1~2 |
| **P1** | IMP-04 | 补充CFL稳定性扫描验证（多CFL值系统测试） | 中等 | 代码+运行 | 中 | +1~2 |
| **P1** | IMP-05 | 完善requirements.txt（添加测试依赖与版本约束） | 中等 | 文档 | 低 | +0.5~1 |
| **P2** | IMP-06 | 补充4种扩展格式（Rusanov/Godunov/Roe/HLLC）的网格收敛数据 | 建议 | 运行+文档 | 中 | +1 |
| **P2** | IMP-07 | 补充所有8种格式在N=100下的完整误差报告CSV | 建议 | 运行 | 低 | +0.5 |
| **P2** | IMP-08 | 数值解/精确解增加CSV格式输出 | 建议 | 代码实现 | 低 | +0.5 |
| **P2** | IMP-09 | 补充质量守恒/能量守恒全局验证 | 建议 | 代码+文档 | 中 | +0.5~1 |
| **P3** | IMP-10 | 统一README命名与项目结构规范 | 轻微 | 文档 | 低 | +0.5 |

---

## 2. 逐项改进详细方案

### IMP-01 [P0-严重] 实现TVD格式（Minmod限制器）

**当前状态**: 项目规划文档（`CFD_Sod_ShockTube_Project_Plan.md` §5.4）明确推荐TVD格式，但代码中无任何TVD/MUSCL/限制器相关实现。这是前次验证报告指出的P0级问题。

**改进目标**: 在 `src/fd_schemes.py` 中实现TVD格式（Minmod限制器），使其与现有8种格式具有统一接口。

#### 2.1 技术方案

**（1）理论框架**

TVD（Total Variation Diminishing）格式由Harten（1983）提出，在光滑区保持二阶精度，间断附近自动降为一阶以抑制振荡[1]。本项目采用基于Roe格式+Minmod限制器的TVD实现：

数值通量形式：

$$\mathbf{F}_{i+1/2} = \mathbf{F}_{i+1/2}^{\text{low}} + \phi(r_i)\left(\mathbf{F}_{i+1/2}^{\text{high}} - \mathbf{F}_{i+1/2}^{\text{low}}\right)$$

其中低阶通量 $\mathbf{F}^{\text{low}}$ 采用Roe通量：

$$\mathbf{F}_{i+1/2}^{\text{Roe}} = \frac{1}{2}\left(\mathbf{F}_i + \mathbf{F}_{i+1}\right) - \frac{1}{2}|\widetilde{\mathbf{A}}_{i+1/2}|\left(\mathbf{U}_{i+1} - \mathbf{U}_i\right)$$

高阶修正项基于MUSCL重构：

$$\mathbf{F}_{i+1/2}^{\text{high}} - \mathbf{F}_{i+1/2}^{\text{low}} = -\frac{1}{2}|\widetilde{\mathbf{A}}_{i+1/2}|\left(\Delta\mathbf{U}_{i+1/2}^{\text{MUSCL}} - \Delta\mathbf{U}_{i+1/2}^{\text{linear}}\right)$$

**（2）Minmod限制器**

Minmod限制器是最保守的TVD限制器，确保总变差不增[1][2]：

$$\text{minmod}(a, b) = \begin{cases} \text{sgn}(a)\cdot\min(|a|, |b|), & \text{if } \text{sgn}(a) = \text{sgn}(b) \\ 0, & \text{otherwise} \end{cases}$$

梯度比 $r$ 定义为：

$$r_i = \frac{\mathbf{U}_i - \mathbf{U}_{i-1}}{\mathbf{U}_{i+1} - \mathbf{U}_i}$$

**（3）代码实现位置**

在 `src/fd_schemes.py` 中新增以下函数：

```python
def minmod_limiter(a, b):
    """Minmod限制器：minmod(a, b) = sgn(a)*max(0, min(|a|, sgn(a)*b))"""
    return 0.5 * (np.sign(a) + np.sign(b)) * np.minimum(np.abs(a), np.abs(b))

def tvd_minmod_step(U, dx, dt, gamma=GAMMA):
    """
    TVD格式时间推进（基于Roe通量+Minmod限制器）
    
    依据: Harten (1983) [1], Toro (2009) [2] 第11章
    """
    # 实现逻辑:
    # 1. 计算 Roe 低阶通量
    # 2. 计算 MUSCL 重构（左/右状态）
    # 3. 应用 Minmod 限制器
    # 4. 计算限制后的高阶通量
    # 5. 时间推进: U_new = U - dt/dx * (F_{i+1/2} - F_{i-1/2})
    pass
```

**（4）实现步骤**

1. 复用已有的 `_roe_average()` 函数计算Roe耗散项
2. 实现 `minmod_limiter()` 函数（标量/向量化版本）
3. 实现 MUSCL 重构：在每个界面 i+1/2 处，利用限制后的斜率重构左右状态
4. 计算 Roe 通量 $\mathbf{F}_{i+1/2}^{\text{Roe}}$
5. 计算限制器函数 $\phi(r)$
6. 组合低阶+高阶修正得到最终数值通量
7. 时间推进更新

**（5）注册到格式表**

在 `FD_SCHEMES` 字典中添加：

```python
'tvd_minmod': {
    'func': tvd_minmod_step,
    'order': 2,
    'description': 'TVD格式 (Roe通量 + Minmod限制器)',
    'reference': 'Harten (1983), Toro (2009)'
}
```

#### 2.2 需要的工作

- **代码实现**: 在 `src/fd_schemes.py` 中新增 `minmod_limiter()` 和 `tvd_minmod_step()` 函数
- **单元测试**: 在 `tests/test_fd_schemes.py` 中新增 `test_tvd_minmod_step()` 和 `test_minmod_limiter()`
- **文档补充**: 在 `docs/fdm_survey.md` 中补充TVD格式的详细理论推导
- **配置更新**: 在 `config/simulation_config.yaml` 的 schemes 列表中添加 `tvd_minmod`

#### 2.3 验收标准

- TVD格式在N=100、CFL=0.8下稳定运行至t=0.2
- 密度/速度/压力剖面与精确解对比图正常生成
- 激波附近无振荡（总变差不增）
- 光滑区（稀疏波）收敛阶接近二阶

---

### IMP-02 [P0-严重] 补充TVD格式网格收敛数据

**当前状态**: 现有收敛数据（`results/convergence_corrected.txt`）仅包含迎风格式。TVD格式缺少N=100/200/400/800的完整收敛性分析。

**改进目标**: 对TVD格式进行N=50/100/200/400/800五种分辨率的系统测试，记录误差并计算收敛阶。

#### 2.4 技术方案

**（1）运行参数**

| 分辨率 | N | CFL | t_final | 预期收敛阶 |
|--------|---|-----|---------|------------|
| 粗网格 | 50 | 0.8 | 0.2 | - |
| 基准 | 100 | 0.8 | 0.2 | - |
| 细网格 | 200 | 0.8 | 0.2 | ~1.5-2.0 |
| 更细 | 400 | 0.8 | 0.2 | ~1.5-2.0 |
| 最细 | 800 | 0.8 | 0.2 | ~1.5-2.0 |

**（2）收敛阶计算**

$$p = \log_2\left(\frac{E_{N_1}}{E_{N_2}}\right)$$

其中 $E$ 为L1误差范数，$N_1$、$N_2$ 为相邻分辨率。

**（3）输出要求**

将结果保存至 `results/convergence_tvd.txt`，格式与现有收敛数据文件一致：

```
N,dx,rho_L1,rho_L2,rho_Linf,u_L1,u_L2,u_Linf,p_L1,p_L2,p_Linf,n_steps
50,...
100,...
200,...
400,...
800,...
```

#### 2.5 需要的工作

- **运行测试**: 执行5种分辨率的TVD格式仿真
- **文档补充**: 将收敛数据整理为表格，添加到 `docs/project_final_report.md` 中
- **可视化**: 生成收敛阶对数图

#### 2.6 验收标准

- 收敛数据文件完整（N=50/100/200/400/800）
- 光滑区收敛阶接近二阶（>1.5）
- 全局收敛阶高于所有一阶格式（>0.8）

---

### IMP-03 [P1-中等] 分析并改善MacCormack收敛阶

**当前状态**: MacCormack格式的网格收敛阶仅为0.18，远低于理论二阶精度。现有报告中注明"数值振荡导致"[3]。

**改进目标**: 深入分析MacCormack收敛阶偏低的原因，并尝试改善。

#### 2.7 技术方案

**（1）原因分析**

MacCormack格式在间断附近产生Gibbs型数值振荡，其根本原因[3][4]：
- 二阶中心差分特性导致色散误差主导
- 接触间断处数值振荡随网格加密反而加剧（非单调收敛）
- L1/L2误差范数被振荡幅值放大

**（2）改善方案**

**方案A（推荐）: 添加选择性人工粘性**

在MacCormack格式中添加Harten型人工粘性项[1]：

$$\mathbf{U}_i^{n+1} = \mathbf{U}_i^{n+1,\text{MacCormack}} + \varepsilon_{i+1/2}(\mathbf{U}_{i+1} - \mathbf{U}_i) - \varepsilon_{i-1/2}(\mathbf{U}_i - \mathbf{U}_{i-1})$$

其中 $\varepsilon_{i+1/2}$ 为基于压力梯度的传感器：

$$\varepsilon_{i+1/2} = \kappa \frac{|p_{i+1} - 2p_i + p_{i-1}|}{p_{i+1} + 2p_i + p_{i-1}}$$

$\kappa$ 为可调参数（推荐0.01-0.1）。

**方案B: 记录并解释（最小修改）**

保持现有实现，在最终报告中详细分析：
- 给出MacCormack在各网格分辨率下的L1/L2误差表
- 绘制误差随网格密度的变化曲线
- 引用文献解释为何在含间断问题中二阶格式的实际收敛阶会退化
- 与TVD格式的收敛阶做对比

**（3）建议实施方案B**

原因：方案A需要修改核心格式实现，可能引入新的不确定性；方案B符合学术规范——如实记录并分析数值现象本身就是有价值的研究贡献。Sod原文中也明确记录了各格式在实际问题中的表现偏离理论预期的情况[4]。

#### 2.8 需要的工作

- **运行补充**: 对MacCormack格式运行N=50/100/200/400/800，记录完整收敛数据
- **文档补充**: 在 `docs/project_final_report.md` 第4章新增"MacCormack收敛阶分析"小节
- **可视化**: 生成MacCormack的振荡对比图（不同N下）

#### 2.9 验收标准

- 完整收敛数据表（至少5种分辨率）
- 报告中对收敛阶退化有文献支撑的深入分析
- 振荡可视化对比图

---

### IMP-04 [P1-中等] 补充CFL稳定性扫描验证

**当前状态**: 验证报告（`results/validation_report.md`）对迎风格式做了CFL测试，但缺少对其他格式的系统CFL稳定性扫描。

**改进目标**: 对所有8+1种格式进行CFL数系统扫描，确定各格式的稳定性边界。

#### 2.10 技术方案

**（1）测试参数**

| CFL数 | 测试目的 | 预期结果 |
|-------|----------|----------|
| 0.3 | 保守稳定区 | 所有格式稳定 |
| 0.5 | 常规稳定区 | 所有格式稳定 |
| 0.7 | 推荐工作点 | 所有格式稳定 |
| 0.8 | 默认配置 | 所有格式稳定 |
| 0.9 | 接近极限 | 大多数格式稳定 |
| 0.95 | 临界区 | 部分格式可能出现振荡 |
| 1.0 | 理论极限 | 格式开始不稳定 |
| 1.1 | 超限 | 不稳定 |

**（2）测试脚本**

创建 `run_cfl_scan.py` 脚本，自动对所有格式在不同CFL值下运行并记录：
- 是否稳定完成（无NaN/崩溃）
- 迭代步数
- 最终L1误差（rho/u/p）
- 运行时间

**（3）输出要求**

保存为 `results/cfl_stability_scan.csv`：

```
Scheme,CFL,Stable,n_steps,rho_L1,u_L1,p_L1,elapsed_s
lax_friedrichs,0.3,True,...
lax_friedrichs,0.5,True,...
...
macormack,0.95,True,...
macormack,1.0,False,...
```

#### 2.11 需要的工作

- **代码实现**: 编写CFL扫描脚本（可基于 `run_simulation.py` 扩展）
- **运行测试**: 对所有格式运行CFL扫描
- **文档补充**: 在 `docs/project_final_report.md` 中新增"CFL稳定性分析"小节

#### 2.12 验收标准

- CFL扫描数据完整（9种格式 x 8个CFL值 = 72组数据）
- 各格式的CFL稳定性边界清晰可辨
- 结果与理论预期一致（CFL <= 1稳定）

---

### IMP-05 [P1-中等] 完善requirements.txt

**当前状态**: 现有 `requirements.txt` 仅包含4个基本依赖：

```
numpy>=1.21.0
matplotlib>=3.5.0
pyyaml>=6.0
scipy>=1.7.0
```

**改进目标**: 补充测试、开发相关的依赖项，完善版本约束。

#### 2.13 技术方案

建议更新为：

```
# 核心依赖
numpy>=1.21.0,<2.0.0
matplotlib>=3.5.0
pyyaml>=6.0
scipy>=1.7.0

# 测试依赖
pytest>=7.0.0

# 开发工具（可选）
flake8>=5.0.0
```

**改进点**:
1. 添加 `pytest>=7.0.0`（项目有34项单元测试，但requirements.txt未包含测试框架）
2. 为 `numpy` 添加上限 `<2.0.0`（numpy 2.0有breaking changes）
3. 添加注释分组提高可读性
4. 可选添加代码检查工具

#### 2.14 需要的工作

- **文档更新**: 直接修改 `requirements.txt`

#### 2.15 验收标准

- `pip install -r requirements.txt` 成功安装所有依赖
- `pytest` 可通过requirements安装

---

### IMP-06 [P2-建议] 补充扩展格式的网格收敛数据

**当前状态**: 4种扩展格式（Rusanov、Godunov、Roe、HLLC）已有实现，但缺少N=100/200/400/800的收敛性数据。

**改进目标**: 对4种扩展格式进行系统收敛性分析。

#### 2.16 技术方案

对每种扩展格式运行N=50/100/200/400/800，记录误差并计算收敛阶。

- **Rusanov**: 预期收敛阶 ~0.5-0.8（一阶格式，含间断）
- **Godunov**: 预期收敛阶 ~0.5-0.8（精确Riemann求解器，理论最优一阶）
- **Roe**: 预期收敛阶 ~0.5-0.8（近似Riemann求解器）
- **HLLC**: 预期收敛阶 ~0.5-0.8（三波模型，接触间断分辨率优于一阶迎风）

**输出**: 保存至 `results/convergence_extended.txt`

#### 2.17 需要的工作

- **运行测试**: 对4种格式各运行5种分辨率
- **文档补充**: 将收敛数据添加到最终报告

#### 2.18 验收标准

- 完整收敛数据（4种格式 x 5种分辨率）
- 各格式收敛阶与理论预期一致
- HLLC的接触间断分辨率优于Rusanov/Godunov/Roe

---

### IMP-07 [P2-建议] 补充完整误差报告

**当前状态**: `results/error_report.csv` 仅包含upwind格式的数据（3行）。

**改进目标**: 生成所有8+1种格式在N=100下的完整误差报告。

#### 2.19 技术方案

直接运行 `python run_simulation.py` 使用所有格式，即可自动生成完整误差报告。确保输出包含所有8种已实现格式及新增的TVD格式。

预期输出应包含：
- 9种格式 x 3个变量（rho/u/p） x 3种误差范数（L1/L2/Linf）= 81行数据

#### 2.20 需要的工作

- **运行测试**: 执行全格式仿真

#### 2.21 验收标准

- `error_report.csv` 包含所有9种格式的完整误差数据

---

### IMP-08 [P2-建议] 数值解/精确解增加CSV格式输出

**当前状态**: 现有 `src/output_writer.py` 仅输出 `.npy` 格式。前次验证报告指出应同时提供CSV格式[5]。

**改进目标**: 在 `src/output_writer.py` 中新增CSV输出功能。

#### 2.22 技术方案

在 `save_results()` 函数中新增CSV保存逻辑：

```python
def save_results_csv(U, x, scheme_name, n_points, output_dir, timestamp, seq):
    """保存数值解为CSV格式 (x, rho, u, p, E)"""
    rho, u, p = conservative_to_primitive(U)
    E = p / ((GAMMA - 1.0) * rho) + 0.5 * u ** 2
    
    csv_path = os.path.join(output_dir, f'{timestamp}_data_{seq}.csv')
    with open(csv_path, 'w') as f:
        f.write('x,rho,u,p,E\n')
        for i in range(len(x)):
            f.write(f'{x[i]:.8e},{rho[i]:.8e},{u[i]:.8e},{p[i]:.8e},{E[i]:.8e}\n')
```

类似地，对精确解也增加CSV输出。

#### 2.23 需要的工作

- **代码实现**: 在 `src/output_writer.py` 中新增CSV输出函数
- **集成**: 在 `run_simulation.py` 中调用新增的CSV输出函数

#### 2.24 验收标准

- 每次仿真同时生成 `.npy` 和 `.csv` 文件
- CSV文件格式正确（含表头、数据完整）

---

### IMP-09 [P2-建议] 补充质量守恒/能量守恒全局验证

**当前状态**: 项目缺少对物理守恒律的全局验证。

**改进目标**: 添加质量守恒和总能量守恒的全局验证。

#### 2.25 技术方案

对于Sod激波管问题（封闭管道、零梯度边界），总质量和总能量应守恒：

$$M(t) = \int_0^1 \rho(x,t) dx \approx \sum_i \rho_i \Delta x$$

$$E_{\text{total}}(t) = \int_0^1 \rho E(x,t) dx \approx \sum_i (\rho E)_i \Delta x$$

**验证步骤**:
1. 计算初始时刻的总质量和总能量
2. 计算最终时刻的总质量和总能量
3. 计算相对误差

预期结果：一阶格式（Lax-Friedrichs、迎风）的守恒误差应 < 1%，二阶格式应 < 0.1%。

**实现位置**: 新增 `src/validator.py` 中的 `check_conservation()` 函数。

#### 2.26 需要的工作

- **代码实现**: 在 `src/validator.py` 中新增守恒验证函数
- **集成**: 在 `run_simulation.py` 中调用守恒验证
- **文档补充**: 将守恒验证结果添加到最终报告

#### 2.27 验收标准

- 各格式的质量守恒误差和能量守恒误差均有记录
- 结果与格式的理论耗散特性一致

---

### IMP-10 [P3-轻微] 统一README命名与项目结构规范

**当前状态**: 项目同时存在 `README.md` 和 `README_CODE.md`，名称不一致。

**改进目标**: 统一使用 `README.md` 作为项目主文档。

#### 2.28 技术方案

1. 将 `README_CODE.md` 的内容合并到 `README.md`
2. 在 `README.md` 中增加：
   - 项目成果概述（8+1种格式、34项测试通过、误差数据等）
   - 新增TVD格式说明
   - 收敛性分析结果摘要
3. 删除 `README_CODE.md`

#### 2.29 需要的工作

- **文档更新**: 合并并完善 `README.md`

#### 2.30 验收标准

- 项目根目录仅保留一个 `README.md`
- 内容涵盖项目全部功能与成果

---

## 3. 改进项分类汇总

### 3.1 需要代码实现的改进项

| 编号 | 改进项 | 涉及文件 |
|------|--------|----------|
| IMP-01 | 实现TVD格式 | `src/fd_schemes.py` |
| IMP-01 | TVD单元测试 | `tests/test_fd_schemes.py` |
| IMP-04 | CFL扫描脚本 | 新建 `run_cfl_scan.py` |
| IMP-08 | CSV输出功能 | `src/output_writer.py`, `run_simulation.py` |
| IMP-09 | 守恒验证 | `src/validator.py` |

### 3.2 需要文档补充的改进项

| 编号 | 改进项 | 涉及文件 |
|------|--------|----------|
| IMP-02 | TVD收敛数据 | `results/convergence_tvd.txt` |
| IMP-03 | MacCormack分析 | `docs/project_final_report.md` |
| IMP-04 | CFL稳定性分析 | `docs/project_final_report.md` |
| IMP-05 | requirements.txt完善 | `requirements.txt` |
| IMP-06 | 扩展格式收敛数据 | `results/convergence_extended.txt` |
| IMP-10 | README统一 | `README.md` |

### 3.3 需要运行测试的改进项

| 编号 | 改进项 | 运行内容 |
|------|--------|----------|
| IMP-02 | TVD收敛数据 | N=50/100/200/400/800 |
| IMP-03 | MacCormack收敛 | N=50/100/200/400/800 |
| IMP-04 | CFL稳定性扫描 | 9种格式 x 8个CFL值 |
| IMP-06 | 扩展格式收敛 | 4种格式 x 5种分辨率 |
| IMP-07 | 完整误差报告 | 所有9种格式 |

---

## 4. 实施顺序建议

按照依赖关系和优先级，建议分三阶段实施：

### 第一阶段（P0核心改进，预计2-3天）

1. **IMP-01**: 实现TVD格式（Minmod限制器）
2. **IMP-02**: 补充TVD格式收敛数据
3. **IMP-05**: 完善requirements.txt

### 第二阶段（P1重要改进，预计1-2天）

4. **IMP-03**: MacCormack收敛阶分析与报告
5. **IMP-04**: CFL稳定性扫描验证

### 第三阶段（P2/P3完善改进，预计1天）

6. **IMP-06**: 扩展格式收敛数据
7. **IMP-07**: 完整误差报告
8. **IMP-08**: CSV格式输出
9. **IMP-09**: 守恒验证
10. **IMP-10**: README统一

---

## 5. 风险评估

| 风险项 | 可能性 | 影响 | 缓解措施 |
|--------|--------|------|----------|
| TVD格式实现复杂度高 | 中 | 高 | 先实现核心逻辑，再优化性能 |
| CFL扫描耗时过长 | 低 | 中 | 可限制为N=100固定分辨率 |
| MacCormack收敛阶无法改善 | 高 | 低 | 采用方案B（记录并分析），学术价值不受影响 |
| 新增代码引入bug | 中 | 高 | 每个新增功能必须通过单元测试 |

---

## 6. 预期评分变化

| 评分维度 | 当前得分 | 改进后得分 | 改进项贡献 |
|----------|----------|------------|------------|
| 数值格式完整性 | 8/10 | 10/10 | IMP-01 (+2) |
| 收敛性分析 | 6/10 | 9/10 | IMP-02, IMP-03, IMP-06 (+3) |
| 验证与测试 | 7/10 | 9/10 | IMP-04, IMP-09 (+2) |
| 文档完整性 | 6/10 | 8/10 | IMP-05, IMP-10 (+2) |
| 代码规范性 | 7/10 | 8/10 | IMP-08 (+1) |
| 误差分析完整性 | 7/10 | 8/10 | IMP-07 (+1) |
| **总分** | **85/100** | **95/100** | **+10** |

---

## 参考文献

[1] HARTEN A. High resolution schemes for hyperbolic conservation laws[J]. Journal of Computational Physics, 1983, 49(3): 357-393.

[2] TORO E F. Riemann solvers and numerical methods for fluid dynamics: a practical introduction[M]. 3rd ed. Berlin: Springer, 2009.

[3] LANEY C B. Computational gasdynamics[M]. Cambridge: Cambridge University Press, 1998.

[4] SOD G A. A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws[J]. Journal of Computational Physics, 1978, 27(1): 1-31.

[5] LEVEQUE R J. Finite volume methods for hyperbolic problems[M]. Cambridge: Cambridge University Press, 2002.

---

*文档版本: v1.0*  
*制定时间: 2026-05-06*  
*改进计划状态: 待执行*
