"""
包初始化文件 (src/__init__.py)
==============================
一维Sod激波管CFD项目（有限差分法）核心包

依据: Build文档 §3.1
"""

from .mesh_generator import generate_mesh
from .flow_initializer import initialize_flow
from .fd_schemes import FD_SCHEMES, solve_with_scheme
from .boundary_handler import apply_boundary_condition
from .time_marcher import compute_dt, time_march
from .exact_solver import sod_exact_solution
from .output_writer import save_results, save_exact_solution
from .validator import compute_errors, generate_comparison_plots, generate_error_report

__all__ = [
    'generate_mesh',
    'initialize_flow',
    'FD_SCHEMES',
    'solve_with_scheme',
    'apply_boundary_condition',
    'compute_dt',
    'time_march',
    'sod_exact_solution',
    'save_results',
    'save_exact_solution',
    'compute_errors',
    'generate_comparison_plots',
    'generate_error_report',
]
