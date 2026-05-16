"""
边界处理模块 (src/boundary_handler.py)
======================================
实现零梯度/外推边界条件。

依据: Build文档 §5.4
文献: Laney (1998) [3], OneFlow-CFD [4]
"""



def apply_boundary_condition(U):
    """
    施加零梯度外推边界条件。

    依据: Build文档 §5.4, Laney (1998) [3], OneFlow-CFD [4]

    实现规则:
        左边界: U[0] = U[1]
        右边界: U[N-1] = U[N-2]

    参数:
        U: 守恒变量数组, 形状 (N, 3)

    返回:
        U: 施加边界条件后的数组 (原地修改)
    """
    U[0, :] = U[1, :]       # 左边界外推
    U[-1, :] = U[-2, :]     # 右边界外推
    return U
