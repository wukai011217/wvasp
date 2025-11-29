"""
WVasp - VASP计算工具

一个专业的VASP计算辅助工具包，提供文件处理、数据分析和可视化功能。
"""

__version__ = "0.1.0"
__author__ = "wukai"
__email__ = "y20230047@mail.ecust.edu.cn"

from .core.base import Atom, Lattice, Structure
from .core.io import POSCAR, OUTCAR, INCAR

__all__ = [
    "Atom",
    "Lattice", 
    "Structure",
    "POSCAR",
    "OUTCAR",
    "INCAR",
]
