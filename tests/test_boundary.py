"""
边界处理模块单元测试 (tests/test_boundary.py)
=============================================
验证多种边界条件类型的正确性:
  - zero_gradient  (零梯度/外推)
  - reflective     (固壁反射)
  - periodic       (周期)
  - transmissive   (无反射/透射)

依据: Build文档 §5.4, §7.1
文献: Laney (1998) [3], LeVeque (1992) [5], Anderson (1984) [2], OneFlow-CFD [4]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.boundary_handler import apply_boundary_condition, BOUNDARY_TYPES
from src.flow_initializer import initialize_flow


def setup_flow(n=100):
    """创建标准Sod激波管流场副本。"""
    x = np.linspace(0.0, 1.0, n)
    U = initialize_flow(x)
    return U.copy()


# =============================================================================
# 原有零梯度边界测试 (保持向后兼容)
# =============================================================================

def test_left_boundary_rho():
    """零梯度左边界密度外推。"""
    U = setup_flow()
    U[1, 0] = 0.5
    U = apply_boundary_condition(U)
    assert abs(U[0, 0] - U[1, 0]) < 1e-15


def test_left_boundary_momentum():
    """零梯度左边界动量外推。"""
    U = setup_flow()
    U[1, 1] = 0.3
    U = apply_boundary_condition(U)
    assert abs(U[0, 1] - U[1, 1]) < 1e-15


def test_left_boundary_energy():
    """零梯度左边界能量外推。"""
    U = setup_flow()
    U[1, 2] = 3.0
    U = apply_boundary_condition(U)
    assert abs(U[0, 2] - U[1, 2]) < 1e-15


def test_right_boundary_rho():
    """零梯度右边界密度外推。"""
    U = setup_flow()
    U[-2, 0] = 0.5
    U = apply_boundary_condition(U)
    assert abs(U[-1, 0] - U[-2, 0]) < 1e-15


def test_right_boundary_momentum():
    """零梯度右边界动量外推。"""
    U = setup_flow()
    U[-2, 1] = 0.3
    U = apply_boundary_condition(U)
    assert abs(U[-1, 1] - U[-2, 1]) < 1e-15


def test_right_boundary_energy():
    """零梯度右边界能量外推。"""
    U = setup_flow()
    U[-2, 2] = 3.0
    U = apply_boundary_condition(U)
    assert abs(U[-1, 2] - U[-2, 2]) < 1e-15


def test_all_components():
    """零梯度边界所有守恒变量分量同时外推。"""
    U = setup_flow()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])
    U = apply_boundary_condition(U)
    assert np.allclose(U[0, :], U[1, :])
    assert np.allclose(U[-1, :], U[-2, :])


def test_interior_preserved():
    """零梯度边界不修改内部节点。"""
    U = setup_flow()
    U_orig = U.copy()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])
    U = apply_boundary_condition(U)
    assert np.allclose(U[2:-2, :], U_orig[2:-2, :])


# =============================================================================
# 新增: 反射边界条件测试 (reflective)
# 依据: Anderson (1984) [2] §6.3, LeVeque (1992) [5] §7.1
# =============================================================================

def test_reflective_boundary():
    """固壁反射边界: 密度和能量不变, 动量(法向速度)反号。"""
    U = setup_flow()
    U_orig = U.copy()
    U[1, :] = np.array([2.0, 0.6, 5.0])   # rho=2, rho*u=0.6 -> u=0.3
    U[-2, :] = np.array([0.5, -0.2, 2.0])  # rho=0.5, rho*u=-0.2 -> u=-0.4
    U = apply_boundary_condition(U.copy(), bc_type='reflective')

    # 左边界: 密度和能量应与 U[1] 相同, 动量反号
    assert abs(U[0, 0] - U[1, 0]) < 1e-15, "左边界密度应等于内部"
    assert abs(U[0, 1] + U[1, 1]) < 1e-15, "左边界动量应反号"
    assert abs(U[0, 2] - U[1, 2]) < 1e-15, "左边界能量应等于内部"

    # 右边界: 密度和能量应与 U[-2] 相同, 动量反号
    assert abs(U[-1, 0] - U[-2, 0]) < 1e-15, "右边界密度应等于内部"
    assert abs(U[-1, 1] + U[-2, 1]) < 1e-15, "右边界动量应反号"
    assert abs(U[-1, 2] - U[-2, 2]) < 1e-15, "右边界能量应等于内部"

    # 验证内部节点未被修改
    assert np.allclose(U[2:-2, :], U_orig[2:-2, :]), "内部节点不应被修改"


# =============================================================================
# 新增: 周期边界条件测试 (periodic)
# 依据: LeVeque (1992) [5] §7.1, Laney (1998) [3] §5.4.2
# =============================================================================

def test_periodic_boundary():
    """周期边界: U[0] = U[-2], U[-1] = U[1]。"""
    U = setup_flow()
    U_orig = U.copy()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])
    U = apply_boundary_condition(U.copy(), bc_type='periodic')

    # 验证左边界取右内部值
    assert np.allclose(U[0, :], U[-2, :]), \
        f"左边界 U[0]={U[0,:]} 应等于 U[-2]={U[-2,:]}"
    # 验证右边界取左内部值
    assert np.allclose(U[-1, :], U[1, :]), \
        f"右边界 U[-1]={U[-1,:]} 应等于 U[1]={U[1,:]}"


# =============================================================================
# 新增: 透射边界条件测试 (transmissive)
# 依据: LeVeque (1992) [5] §7.1, Anderson (1984) [2] §6.4
# =============================================================================

def test_transmissive_boundary():
    """透射边界: 二阶线性外推 U[0] = 2*U[1] - U[2], U[-1] = 2*U[-2] - U[-3]。"""
    U = setup_flow()
    U_orig = U.copy()
    # 设置内部节点值以构造线性外推
    U[1, :] = np.array([1.0, 0.0, 2.5])
    U[2, :] = np.array([0.8, 0.0, 2.0])
    U[-2, :] = np.array([0.3, 0.0, 1.0])
    U[-3, :] = np.array([0.4, 0.0, 1.2])
    U = apply_boundary_condition(U.copy(), bc_type='transmissive')

    # 左边界: U[0] = 2*U[1] - U[2]
    expected_left = 2.0 * U[1, :] - U[2, :]
    assert np.allclose(U[0, :], expected_left), \
        f"左边界外推: 期望 {expected_left}, 实际 {U[0,:]}"

    # 右边界: U[-1] = 2*U[-2] - U[-3]
    expected_right = 2.0 * U[-2, :] - U[-3, :]
    assert np.allclose(U[-1, :], expected_right), \
        f"右边界外推: 期望 {expected_right}, 实际 {U[-1,:]}"


# =============================================================================
# 新增: 默认参数测试
# =============================================================================

def test_zero_gradient_default():
    """不指定bc_type参数时默认为zero_gradient。"""
    U = setup_flow()
    U[1, :] = np.array([0.5, 0.2, 1.0])
    U[-2, :] = np.array([0.3, 0.1, 2.0])

    # 带参数调用 zero_gradient
    U_explicit = apply_boundary_condition(U.copy(), bc_type='zero_gradient')
    # 不带参数调用 (使用默认值)
    U_default = apply_boundary_condition(U.copy())

    # 两次调用结果应完全相同
    assert np.allclose(U_explicit, U_default), \
        "默认参数调用应与显式指定 zero_gradient 结果一致"
    assert np.allclose(U_explicit[0, :], U[1, :]), "左边界应等于内部节点"
    assert np.allclose(U_explicit[-1, :], U[-2, :]), "右边界应等于内部节点"


# =============================================================================
# 新增: BOUNDARY_TYPES 注册表测试
# =============================================================================

def test_boundary_types_registry():
    """验证 BOUNDARY_TYPES 注册表包含所有4种类型。"""
    expected_types = {'zero_gradient', 'reflective', 'periodic', 'transmissive'}
    assert set(BOUNDARY_TYPES.keys()) == expected_types, \
        f"BOUNDARY_TYPES 应包含 {expected_types}"

    # 验证每种类型都有 description 和 reference
    for bc_type, info in BOUNDARY_TYPES.items():
        assert 'description' in info, f"{bc_type} 缺少 description"
        assert 'reference' in info, f"{bc_type} 缺少 reference"