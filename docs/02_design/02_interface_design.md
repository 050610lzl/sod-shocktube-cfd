# 接口设计文档

> 文档版本: v1.5.1  
> 项目: 一维Sod激波管CFD求解器 (sod-shocktube-cfd)  
> 文献依据: Sod (1978) [1], Toro (2009) [2], Laney (1998) [3], OneFlow-CFD [4]

---

## 1. CLI 接口

### 1.1 主入口: `run_simulation.py`

**文件路径**: [run_simulation.py](file:///e:/trae_project/a/run_simulation.py)

#### 命令行参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--config` | `str` | 否 | `config/simulation_config.yaml` | YAML 配置文件路径 |
| `--n_points` | `int` | 否 | `None` (使用配置文件) | 网格节点数, 覆盖配置文件中的 `mesh.n_points` |
| `--cfl` | `float` | 否 | `None` (使用配置文件) | CFL 数, 覆盖配置文件中的 `simulation.cfl` |
| `--scheme` | `str` | 否 | `None` (运行全部) | 指定单个格式运行. 可选值见 [1.2节](#12-可用的格式名称) |
| `--schemes` | `str` (nargs='+') | 否 | `None` | 指定多个格式运行 (空格分隔) |
| `--bc`, `--boundary` | `str` | 否 | `zero_gradient` | 边界条件类型. 可选值: `zero_gradient`, `reflective`, `periodic`, `transmissive` |
| `--left_rho` | `float` | 否 | `1.0` | 左侧初始密度 |
| `--left_u` | `float` | 否 | `0.0` | 左侧初始速度 |
| `--left_p` | `float` | 否 | `1.0` | 左侧初始压力 |
| `--right_rho` | `float` | 否 | `0.125` | 右侧初始密度 |
| `--right_u` | `float` | 否 | `0.0` | 右侧初始速度 |
| `--right_p` | `float` | 否 | `0.1` | 右侧初始压力 |
| `--diaphragm` | `float` | 否 | `0.5` | 隔膜位置 |

#### 用法示例

```bash
# 运行全部格式 (使用默认配置)
python run_simulation.py

# 指定配置文件
python run_simulation.py --config config/simulation_config.yaml

# 仅运行 Lax-Wendroff 格式
python run_simulation.py --scheme lax_wendroff

# 运行多个格式, 覆盖网格数和 CFL
python run_simulation.py --schemes lax_friedrichs roe hllc --n_points 200 --cfl 0.5

# 通过 pip 安装后使用 CLI 入口
sod-shocktube --scheme godunov --n_points 400
```

#### 1.2 可用的格式名称

`--scheme` 和 `--schemes` 参数接受以下值 (与 [fd_schemes.py](file:///e:/trae_project/a/src/fd_schemes.py#L933-L988) 中的 `FD_SCHEMES` 键一致):

| 格式键名 | 描述 | 阶数 |
|----------|------|------|
| `lax_friedrichs` | Lax-Friedrichs 格式 (一阶中心耗散) | 1 |
| `lax_wendroff` | Lax-Wendroff 格式 (二阶中心色散) | 2 |
| `macormack` | MacCormack 预估校正格式 (二阶) | 2 |
| `upwind` | 一阶迎风格式 (Steger-Warming 通量分裂) | 1 |
| `rusanov` | Rusanov 格式 (局部 Lax-Friedrichs) | 1 |
| `godunov` | Godunov 格式 (精确 Riemann 求解器) | 1 |
| `roe` | Roe 格式 (近似 Riemann 求解器) | 1 |
| `hllc` | HLLC 格式 (恢复接触间断) | 1 |
| `tvd_minmod` | TVD 格式 (Roe 通量 + Minmod 限制器) | 2 |

#### 1.3 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 正常完成 |
| 1 | 未知格式名称 (`ValueError`) |
| 2 | 配置文件解析错误 (`yaml.YAMLError`) |
| 其他 | Python 运行时异常 (如 `FileNotFoundError`) |

---

## 2. YAML 配置接口

**文件路径**: [config/simulation_config.yaml](file:///e:/trae_project/a/config/simulation_config.yaml)

### 2.1 完整配置项

```yaml
# 网格参数
mesh:
  n_points: 100          # int, 网格节点数
  x_left: 0.0            # float, 左边界坐标
  x_right: 1.0           # float, 右边界坐标

# 物理参数
physics:
  gamma: 1.4             # float, 比热比 (理想气体)
  diaphragm_pos: 0.5     # float, 隔膜位置
  left_state:
    rho: 1.0             # float, 左侧密度
    u: 0.0               # float, 左侧速度
    p: 1.0               # float, 左侧压力
  right_state:
    rho: 0.125           # float, 右侧密度
    u: 0.0               # float, 右侧速度
    p: 0.1               # float, 右侧压力

# 仿真参数
simulation:
  t_final: 0.2           # float, 仿真终止时间
  cfl: 0.8               # float, CFL 数
  boundary_type: zero_gradient  # str, 边界条件类型: zero_gradient/reflective/periodic/transmissive

# 数值格式列表
schemes:
  - lax_friedrichs
  - lax_wendroff
  - macormack
  - upwind
  - rusanov
  - godunov
  - roe
  - hllc

# 输出配置
output:
  data_dir: results/data
  exact_dir: results/exact
  figures_dir: results/figures
  error_report: results/error_report.csv
```

### 2.2 类型、默认值与约束

| 配置路径 | 类型 | 默认值 | 约束条件 |
|----------|------|--------|----------|
| `mesh.n_points` | `int` | 100 | >= 10, 建议 100/200/400 |
| `mesh.x_left` | `float` | 0.0 | < x_right |
| `mesh.x_right` | `float` | 1.0 | > x_left |
| `physics.gamma` | `float` | 1.4 | > 1.0 (理想气体) |
| `physics.diaphragm_pos` | `float` | 0.5 | 在 [x_left, x_right] 之间 |
| `physics.left_state.rho` | `float` | 1.0 | > 0 |
| `physics.left_state.u` | `float` | 0.0 | 无约束 |
| `physics.left_state.p` | `float` | 1.0 | > 0 |
| `physics.right_state.rho` | `float` | 0.125 | > 0 |
| `physics.right_state.u` | `float` | 0.0 | 无约束 |
| `physics.right_state.p` | `float` | 0.1 | > 0 |
| `simulation.t_final` | `float` | 0.2 | > 0 |
| `simulation.cfl` | `float` | 0.8 | (0, 1.0], 推荐 0.8~0.95 |
| `simulation.boundary_type` | `str` | `zero_gradient` | `zero_gradient` / `reflective` / `periodic` / `transmissive` |
| `schemes` | `list[str]` | 全部8种 | 每个元素必须是 FD_SCHEMES 中的键 |
| `output.data_dir` | `str` | `results/data` | 可写路径 |
| `output.exact_dir` | `str` | `results/exact` | 可写路径 |
| `output.figures_dir` | `str` | `results/figures` | 可写路径 |
| `output.error_report` | `str` | `results/error_report.csv` | 可写路径 |

### 2.3 加载方式

```python
import yaml

def load_config(config_path='config/simulation_config.yaml'):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
```

见 [run_simulation.py](file:///e:/trae_project/a/run_simulation.py#L33-L36)。

---

## 3. Python API 接口

**包入口**: [src/__init__.py](file:///e:/trae_project/a/src/__init__.py)

### 3.1 导出函数清单

`from src import *` 导出的全部公开函数:

| 函数 | 模块来源 | 说明 |
|------|----------|------|
| `generate_mesh` | mesh_generator | 生成一维均匀网格 |
| `initialize_flow` | flow_initializer | Sod 初始条件流场初始化 |
| `FD_SCHEMES` | fd_schemes | 格式注册表字典 |
| `solve_with_scheme` | fd_schemes | 使用指定格式求解 |
| `apply_boundary_condition` | boundary_handler | 施加边界条件 (支持4种类型) |
| `compute_dt` | time_marcher | CFL 时间步长 |
| `time_march` | time_marcher | 单步时间推进 |
| `sod_exact_solution` | exact_solver | Riemann 精确解 |
| `save_results` | output_writer | 保存数值解 .npy |
| `save_exact_solution` | output_writer | 保存精确解 .npy |
| `compute_errors` | validator | 计算 L1/L2/Linf 误差 |
| `generate_comparison_plots` | validator | 生成单格式对比图 |
| `generate_error_report` | validator | 生成 CSV 误差报告 |

### 3.2 函数签名详解

#### 3.2.1 `generate_mesh()`

```python
def generate_mesh(
    n_points: int = 100,
    x_left: float = 0.0,
    x_right: float = 1.0
) -> tuple[np.ndarray, float]:
    """
    生成一维均匀网格。

    参数:
        n_points: 网格节点数 (默认100)
        x_left: 左边界坐标 (默认0.0)
        x_right: 右边界坐标 (默认1.0)

    返回:
        x: 网格坐标数组, 形状 (N,)
        dx: 网格间距 (标量)
    """
```

#### 3.2.2 `initialize_flow()`

```python
def initialize_flow(
    x: np.ndarray,
    gamma: float = 1.4,
    diaphragm_pos: float = 0.5,
    left_state: Optional[dict] = None,
    right_state: Optional[dict] = None
) -> np.ndarray:
    """
    按Sod激波管标准初始条件初始化流场。

    初始条件:
        左态 (x < diaphragm_pos): rho_L=1.0, u_L=0.0, p_L=1.0
        右态 (x >= diaphragm_pos): rho_R=0.125, u_R=0.0, p_R=0.1

    参数:
        x: 网格坐标数组, 形状 (N,)
        gamma: 比热比 (默认1.4)
        diaphragm_pos: 隔膜位置 (默认0.5)
        left_state: 可选左侧状态字典 {'rho': ..., 'u': ..., 'p': ...}
        right_state: 可选右侧状态字典 {'rho': ..., 'u': ..., 'p': ...}

    返回:
        U: 守恒变量数组, 形状 (N, 3)
           U[:,0] = rho, U[:,1] = rho*u, U[:,2] = rho*E
    """
```

#### 3.2.3 `solve_with_scheme()`

```python
def solve_with_scheme(
    scheme_name: str,
    U: np.ndarray,
    x: np.ndarray,
    dx: float,
    t_final: float = 0.2,
    cfl: float = 0.8,
    gamma: float = 1.4
) -> tuple[np.ndarray, float, int]:
    """
    使用指定有限差分格式求解Sod激波管问题。

    参数:
        scheme_name: 格式名称 (FD_SCHEMES 中的键)
        U: 初始守恒变量, 形状 (N, 3)
        x: 网格坐标数组, 形状 (N,)
        dx: 网格间距
        t_final: 仿真终止时间 (默认0.2)
        cfl: CFL数 (默认0.8)
        gamma: 比热比 (默认1.4)

    返回:
        U: 最终守恒变量, 形状 (N, 3)
        t: 最终仿真时间
        n_steps: 总迭代步数

    异常:
        ValueError: 未知格式名称
    """
```

#### 3.2.4 `apply_boundary_condition()`

```python
def apply_boundary_condition(
    U: np.ndarray,
    bc_type: str = 'zero_gradient'
) -> np.ndarray:
    """
    施加边界条件，支持4种类型。

    边界条件类型:
        'zero_gradient'  (默认): 零梯度外推
           左边界: U[0] = U[1]
           右边界: U[N-1] = U[N-2]
        'reflective': 固壁反射
           左边界: U[0, 1] = -U[1, 1]，其余分量零梯度
           右边界: U[N-1, 1] = -U[N-2, 1]，其余分量零梯度
        'periodic': 周期边界
           左边界: U[0] = U[N-2]
           右边界: U[N-1] = U[1]
        'transmissive': 透射边界
           基于特征线方法的对外行波外推

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        bc_type: 边界条件类型字符串 (默认 'zero_gradient')

    返回:
        U: 施加边界条件后的数组 (原地修改)
    """
```

#### 3.2.5 `compute_dt()`

```python
def compute_dt(
    U: np.ndarray,
    dx: float,
    cfl: float = 0.8,
    gamma: float = 1.4
) -> float:
    """
    按CFL条件计算时间步长。

    公式: dt = CFL * dx / max(|u| + c)

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        dx: 网格间距
        cfl: CFL数 (默认0.8)
        gamma: 比热比 (默认1.4)

    返回:
        dt: 时间步长
    """
```

#### 3.2.6 `time_march()`

```python
def time_march(
    U: np.ndarray,
    dx: float,
    dt: float,
    scheme_func: Callable,
    gamma: float = 1.4
) -> np.ndarray:
    """
    执行一步时间推进。

    参数:
        U: 当前守恒变量, 形状 (N, 3)
        dx: 网格间距
        dt: 时间步长
        scheme_func: 差分格式函数, 签名 f(U, dx, dt, gamma) -> U_new
        gamma: 比热比 (默认1.4)

    返回:
        U_new: 下一时间层守恒变量 (不含边界)
    """
```

#### 3.2.7 `sod_exact_solution()`

```python
def sod_exact_solution(
    x: np.ndarray,
    t: float,
    gamma: float = 1.4
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    计算Sod激波管问题在时刻t的解析精确解。

    算法依据: Toro (2009) [2] 第4章 - Riemann问题精确解法

    参数:
        x: 网格坐标数组, 形状 (N,)
        t: 仿真时刻
        gamma: 比热比 (默认1.4)

    返回:
        rho_exact: 精确密度数组, 形状 (N,)
        u_exact: 精确速度数组, 形状 (N,)
        p_exact: 精确压力数组, 形状 (N,)
    """
```

#### 3.2.8 `compute_errors()`

```python
def compute_errors(
    U_num: np.ndarray,
    rho_exact: np.ndarray,
    u_exact: np.ndarray,
    p_exact: np.ndarray
) -> dict:
    """
    计算数值解与精确解的L1、L2、Linf误差范数。

    参数:
        U_num: 数值解守恒变量, 形状 (N, 3)
        rho_exact: 精确密度, 形状 (N,)
        u_exact: 精确速度, 形状 (N,)
        p_exact: 精确压力, 形状 (N,)

    返回:
        errors: 误差字典
            {
              'rho': {'L1': float, 'L2': float, 'Linf': float},
              'u':   {'L1': float, 'L2': float, 'Linf': float},
              'p':   {'L1': float, 'L2': float, 'Linf': float}
            }
    """
```

#### 3.2.9 `save_results()`

```python
def save_results(
    U: np.ndarray,
    x: np.ndarray,
    scheme_name: str,
    n_points: int,
    output_dir: str = 'results/data',
    timestamp: Optional[str] = None,
    seq: Optional[int] = None
) -> None:
    """
    保存数值解数据到 .npy 文件。

    参数:
        U: 守恒变量数组, 形状 (N, 3)
        x: 网格坐标数组, 形状 (N,)
        scheme_name: 格式名称
        n_points: 网格节点数
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档, 可选)
        seq: 序号 (用于归档, 可选)
    """
```

#### 3.2.10 `save_exact_solution()`

```python
def save_exact_solution(
    rho: np.ndarray,
    u: np.ndarray,
    p: np.ndarray,
    x: np.ndarray,
    n_points: int,
    output_dir: str = 'results/exact',
    timestamp: Optional[str] = None
) -> None:
    """
    保存精确解数据到 .npy 文件。

    参数:
        rho: 精确密度, 形状 (N,)
        u: 精确速度, 形状 (N,)
        p: 精确压力, 形状 (N,)
        x: 网格坐标, 形状 (N,)
        n_points: 网格节点数
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档, 可选)
    """
```

#### 3.2.11 `generate_comparison_plots()`

```python
def generate_comparison_plots(
    x: np.ndarray,
    U_num: np.ndarray,
    rho_exact: np.ndarray,
    u_exact: np.ndarray,
    p_exact: np.ndarray,
    scheme_name: str,
    n_points: int,
    t_final: float = 0.2,
    cfl: float = 0.8,
    output_dir: str = 'results/figures',
    timestamp: Optional[str] = None
) -> None:
    """
    生成密度/压力/速度/总能剖面对比图 (4张子图)。

    强制铁律1要求:
    - 必须包含: 密度(rho), 速度(u), 压力(p), 总能量(E) 4张子图
    - 精确解: 实线; 数值解: 圆圈标记
    - 标注: 格式名称, 网格点数, t=0.2, CFL数

    参数:
        x: 网格坐标, 形状 (N,)
        U_num: 数值解守恒变量, 形状 (N, 3)
        rho_exact, u_exact, p_exact: 精确解, 形状 (N,)
        scheme_name: 格式名称
        n_points: 网格节点数
        t_final: 终止时间 (默认0.2)
        cfl: CFL数 (默认0.8)
        output_dir: 输出目录
        timestamp: 时间戳 (用于归档, 可选)
    """
```

#### 3.2.12 `generate_error_report()`

```python
def generate_error_report(
    all_errors: dict,
    output_path: str = 'results/error_report.csv'
) -> None:
    """
    生成误差报告CSV文件。

    参数:
        all_errors: 错误字典 {scheme_name: {var: {'L1': ..., 'L2': ..., 'Linf': ...}}}
        output_path: 输出路径 (默认 results/error_report.csv)
    """
```

---

## 4. 内部模块接口

### 4.1 模块间的数据格式约定

所有模块间传递的守恒变量 `U` 均为 `numpy.ndarray`, shape 为 `(N, 3)`:

```
U[:, 0] = rho       # 密度
U[:, 1] = rho * u   # 动量密度
U[:, 2] = rho * E   # 总能量密度
```

原始变量 (rho, u, p) 均为 `numpy.ndarray`, shape 为 `(N,)`。

### 4.2 格式步进函数的签名约定

所有格式步进函数必须遵循统一签名:

```python
def xxx_step(U: np.ndarray, dx: float, dt: float, gamma: float = 1.4) -> np.ndarray:
    """执行一步时间推进。

    参数:
        U: 当前守恒变量, 形状 (N, 3), 含边界值
        dx: 网格间距
        dt: 时间步长
        gamma: 比热比

    返回:
        U_new: 下一时间层守恒变量, 形状 (N, 3)
               注意: 内部节点已更新, 边界节点为未定义值
               (调用方负责施加边界条件)
    """
```

### 4.3 内部模块调用关系矩阵

| 调用方 \ 被调用方 | mesh | flow_init | fd_sch | boundary | time_march | exact | writer | validator |
|-------------------|------|-----------|--------|----------|------------|-------|--------|-----------|
| run_simulation.py | [x] | [x] | [x] | | | [x] | [x] | [x] |
| fd_schemes.py | | | [x] | [x] | [x] | | | |
| validator.py | | | | | [x] | | | [x] |
| time_marcher.py | | | | | [x] | | | |

---

## 5. 文件 I/O 接口

### 5.1 输入文件

#### 5.1.1 YAML 配置文件

- **路径**: `config/simulation_config.yaml`
- **格式**: YAML 1.1, UTF-8 编码
- **解析器**: `yaml.safe_load()`
- **示例**: 见 [2.1节](#21-完整配置项)

### 5.2 输出文件

#### 5.2.1 数值解数据文件

- **格式**: NumPy `.npy` (二进制)
- **命名规则**: `{timestamp}_data_{seq}.npy`
- **存储位置**: `results/data/{timestamp}/`
- **内容**: `{'x': np.ndarray, 'U': np.ndarray}` 字典
- **示例文件名**: `20260516_083500_data_0.npy`
- **加载方式**: `data = np.load(path, allow_pickle=True).item()`

#### 5.2.2 精确解数据文件

- **格式**: NumPy `.npy` (二进制)
- **命名规则**: `{timestamp}_data_exact.npy`
- **存储位置**: `results/exact/{timestamp}/`
- **内容**: `{'x': np.ndarray, 'rho': np.ndarray, 'u': np.ndarray, 'p': np.ndarray}` 字典
- **加载方式**: `data = np.load(path, allow_pickle=True).item()`

#### 5.2.3 对比图文件

- **格式**: PNG 图像, DPI=300
- **单格式命名规则**: `{timestamp}_plot_{scheme_name}.png`
- **叠加图命名规则**: `{timestamp}_plot_all_schemes.png`
- **存储位置**: `results/figures/{timestamp}/`
- **内容规范**:
  - 4 个子图: rho, p, u, E
  - 精确解: 黑色实线 (`'k-'`)
  - 数值解: 黑色空心圆圈 (`'ko', fillstyle='none'`)
  - 标题: `{scheme_name} | N={n_points} | t={t_final} | CFL={cfl}`
  - Y 轴标签使用 LaTeX 数学符号

#### 5.2.4 误差报告文件

- **格式**: CSV (逗号分隔)
- **路径**: `results/error_report.csv`
- **列结构**:

```
Scheme,Variable,L1_Error,L2_Error,Linf_Error
lax_friedrichs,rho,1.23e-02,2.34e-03,4.56e-02
lax_friedrichs,u,5.67e-03,1.23e-03,8.90e-03
...
```

每行一个 (格式, 变量) 组合, 共 `N_formats x 3_variables` 行。

### 5.3 时间戳归档规则 (强制铁律2)

依据项目规范 (见 [CFD_Sod_ShockTube_Project_Plan.md](file:///e:/trae_project/a/CFD_Sod_ShockTube_Project_Plan.md)):

1. **时间戳格式**: `YYYYMMDD_HHMMSS` (例如: `20260516_083500`)
2. **每次仿真生成唯一时间戳**: 在 `run_simulation()` 开始时通过 `datetime.datetime.now().strftime()` 生成
3. **目录结构**:
   ```
   results/
   +-- data/
   |   +-- 20260516_083500/
   |   |   +-- 20260516_083500_data_0.npy  (格式1)
   |   |   +-- 20260516_083500_data_1.npy  (格式2)
   |   |   +-- ...
   |   +-- 20260516_090030/
   |       +-- ...
   +-- exact/
   |   +-- 20260516_083500/
   |   |   +-- 20260516_083500_data_exact.npy
   |   +-- 20260516_090030/
   |       +-- ...
   +-- figures/
   |   +-- 20260516_083500/
   |   |   +-- 20260516_083500_plot_lax_friedrichs.png
   |   |   +-- 20260516_083500_plot_lax_wendroff.png
   |   |   +-- 20260516_083500_plot_all_schemes.png
   |   +-- 20260516_090030/
   |       +-- ...
   +-- error_report.csv
   ```
4. **序号分配 (seq)**: `enumerate(schemes)` 的结果, 从 0 开始, 按配置文件中的格式列表顺序

---

## 6. setuptools 入口点

项目在 [pyproject.toml](file:///e:/trae_project/a/pyproject.toml#L55-L56) 中注册了 CLI 入口点:

```toml
[project.scripts]
sod-shocktube = "run_simulation:main"
```

安装后可通过 `sod-shocktube` 命令直接调用:

```bash
pip install -e .
sod-shocktube --scheme roe --n_points 200
```

---

## 参考文献

1. Sod, G. A. (1978). *Journal of Computational Physics*, 27(1), 1-31.
2. Toro, E. F. (2009). *Riemann Solvers and Numerical Methods for Fluid Dynamics* (3rd ed.). Springer.
3. Laney, C. B. (1998). *Computational Gasdynamics*. Cambridge University Press.
4. OneFlow-CFD Documentation. https://oneflow-cfd.readthedocs.io/en/latest/cfd/examples/sod.html
5. LeVeque, R. J. (1992). *Numerical Methods for Conservation Laws*. Birkhauser.