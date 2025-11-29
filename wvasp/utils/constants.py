"""
常量定义

定义WVasp工具中使用的各种常量。
"""

import numpy as np

# 物理常数
BOHR_TO_ANGSTROM = 0.529177249  # 玻尔半径到埃的转换
HARTREE_TO_EV = 27.211386245988  # 哈特里到电子伏特的转换
RYDBERG_TO_EV = 13.605693122994  # 里德伯到电子伏特的转换

# 数学常数
PI = np.pi
TWO_PI = 2 * np.pi

# 默认数值精度
DEFAULT_TOLERANCE = 1e-8
POSITION_TOLERANCE = 1e-6
ENERGY_TOLERANCE = 1e-6

# 文件相关常量
VASP_FILES = {
    'POSCAR': 'POSCAR',
    'CONTCAR': 'CONTCAR', 
    'OUTCAR': 'OUTCAR',
    'INCAR': 'INCAR',
    'KPOINTS': 'KPOINTS',
    'POTCAR': 'POTCAR',
    'DOSCAR': 'DOSCAR',
    'EIGENVAL': 'EIGENVAL',
    'CHGCAR': 'CHGCAR',
    'WAVECAR': 'WAVECAR',
}

# 元素信息
ATOMIC_NUMBERS = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
    'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18,
    'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26,
    'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34,
    'Br': 35, 'Kr': 36,
}

ATOMIC_MASSES = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.811, 'C': 12.011,
    'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
    'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996,
    'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38,
}

# 颜色定义
COLORS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
}

# 默认绘图参数
PLOT_DEFAULTS = {
    'figsize': (10, 6),
    'dpi': 300,
    'fontsize': 12,
    'linewidth': 2,
    'markersize': 6,
}
