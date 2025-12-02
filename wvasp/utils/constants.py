"""
常量定义

定义WVasp工具中使用的各种常量、参数定义和数据。
只包含纯数据，不包含方法实现。
"""

import numpy as np

# ============================================================================
# 物理和数学常数
# ============================================================================

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
    'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42,
    'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58,
    'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66,
    'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74,
    'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82,
    'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,
    'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98,
    'Es': 99, 'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103,
}

ATOMIC_MASSES = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.811, 'C': 12.011,
    'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
    'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996,
    'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38,
    'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 'Nb': 92.906, 'Mo': 95.95,
    'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.906, 'Pd': 106.42, 'Ag': 107.868, 'Cd': 112.414,
    'In': 114.818, 'Sn': 118.710, 'Sb': 121.760, 'Te': 127.60, 'I': 126.904, 'Xe': 131.293,
    'Cs': 132.905, 'Ba': 137.327, 'La': 138.905, 'Ce': 140.116, 'Pr': 140.908, 'Nd': 144.242,
    'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25, 'Tb': 158.925, 'Dy': 162.500,
    'Ho': 164.930, 'Er': 167.259, 'Tm': 168.934, 'Yb': 173.045, 'Lu': 174.967, 'Hf': 178.49,
    'Ta': 180.948, 'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217, 'Pt': 195.084,
    'Au': 196.967, 'Hg': 200.592, 'Tl': 204.383, 'Pb': 207.2, 'Bi': 208.980, 'Po': 209.0,
    'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.038,
    'Pa': 231.036, 'U': 238.029, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0,
    'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0, 'Md': 258.0, 'No': 259.0, 'Lr': 266.0,
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

# ============================================================================
# VASP参数定义
# ============================================================================

# 基础参数
BASIC_PARAMS = {
    'SYSTEM': {'type': str, 'default': 'VASP calculation'},
    'PREC': {'type': str, 'values': ['Low', 'Medium', 'High', 'Normal', 'Single', 'Accurate'], 'default': 'Accurate'},
    'ISTART': {'type': int, 'values': [0, 1, 2, 3], 'default': 0},
    'ICHARG': {'type': int, 'values': [0, 1, 2, 4, 11, 12], 'default': 2},
    'ENCUT': {'type': float, 'min': 100.0, 'max': 2000.0, 'default': 400.0},
    'EDIFF': {'type': float, 'min': 1e-8, 'max': 1e-3, 'default': 1e-5},
    'NELM': {'type': int, 'min': 1, 'max': 1000, 'default': 60},
    'NELMIN': {'type': int, 'min': 1, 'max': 100, 'default': 2},
}
    
# 电子结构参数
ELECTRONIC_PARAMS = {
        'ISMEAR': {'type': int, 'min': -5, 'max': 2, 'default': 0},
        'SIGMA': {'type': float, 'min': 0.001, 'max': 1.0, 'default': 0.05},
        'ISPIN': {'type': int, 'values': [1, 2], 'default': 1},
        'MAGMOM': {'type': list, 'default': None},
        'LREAL': {'type': [bool, str], 'values': [False, True, 'Auto', 'A', 'On', 'O'], 'default': False},
        'ALGO': {'type': str, 'values': ['Normal', 'VeryFast', 'Fast', 'Conjugate', 'All', 'Damped'], 'default': 'Normal'},
    }
    
# 结构优化参数
OPTIMIZATION_PARAMS = {
        'NSW': {'type': int, 'min': 0, 'max': 10000, 'default': 0},
        'IBRION': {'type': int, 'values': [-1, 0, 1, 2, 3, 5, 6, 7, 8, 44], 'default': 2},
        'ISIF': {'type': int, 'values': [0, 1, 2, 3, 4, 5, 6, 7], 'default': 2},
        'EDIFFG': {'type': float, 'min': -1.0, 'max': 0.0, 'default': -0.01},
        'POTIM': {'type': float, 'min': 0.01, 'max': 2.0, 'default': 0.5},
    }
    
# 分子动力学参数
MD_PARAMS = {
        'SMASS': {'type': [int, float], 'min': -3, 'default': -3},
        'MDALGO': {'type': int, 'values': [0, 1, 2, 3, 11, 21, 13], 'default': 0},
        'TEBEG': {'type': float, 'min': 0.0, 'max': 10000.0, 'default': 300.0},
        'TEEND': {'type': float, 'min': 0.0, 'max': 10000.0, 'default': 300.0},
    }
    
# DOS和能带参数
DOS_PARAMS = {
        'LORBIT': {'type': int, 'values': [0, 1, 2, 5, 10, 11, 12, 13, 14], 'default': 11},
        'NEDOS': {'type': int, 'min': 100, 'max': 10000, 'default': 3000},
    }
    
# NEB参数
NEB_PARAMS = {
        'IMAGES': {'type': int, 'min': 1, 'max': 20, 'default': 5},
        'SPRING': {'type': float, 'min': -50.0, 'max': 50.0, 'default': -5.0},
        'LCLIMB': {'type': bool, 'default': True},
        'MAXMOVE': {'type': float, 'min': 0.1, 'max': 2.0, 'default': 0.2},
        'ICHAIN': {'type': int, 'values': [0, 1, 2, 3], 'default': 0},
        'IOPT': {'type': int, 'values': [0, 1, 2, 3, 4, 7], 'default': 1},
    }
    
# DFT+U参数
PLUS_U_PARAMS = {
        'LDAU': {'type': bool, 'default': False},
        'LDAUTYPE': {'type': int, 'values': [1, 2, 4], 'default': 2},
        'LDAUL': {'type': list, 'default': None},
        'LDAUU': {'type': list, 'default': None},
        'LDAUJ': {'type': list, 'default': None},
        'LDAUPRINT': {'type': int, 'values': [0, 1, 2], 'default': 1},
        'LMAXMIX': {'type': int, 'min': 2, 'max': 6, 'default': 4},
    }
    
# 输出控制参数
OUTPUT_PARAMS = {
        'LWAVE': {'type': bool, 'default': False},
        'LCHARG': {'type': bool, 'default': False},
        'LAECHG': {'type': bool, 'default': False},
        'LVHAR': {'type': bool, 'default': False},
    }
    
# 并行化参数
PARALLEL_PARAMS = {
        'NPAR': {'type': int, 'min': 1, 'max': 1000, 'default': None},
        'NSIM': {'type': int, 'min': 1, 'max': 100, 'default': 4},
        'LPLANE': {'type': bool, 'default': False},
        'NCORE': {'type': int, 'min': 1, 'max': 1000, 'default': 4},
    }
    
# 混合泛函参数
HYBRID_PARAMS = {
        'LHFCALC': {'type': bool, 'default': False},
        'HFSCREEN': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.2},
        'PRECFOCK': {'type': str, 'values': ['Normal', 'Accurate', 'Fast', 'Medium'], 'default': 'Normal'},
    }
    
# 所有参数合并
ALL_PARAMS = {}
ALL_PARAMS.update(BASIC_PARAMS)
ALL_PARAMS.update(ELECTRONIC_PARAMS)
ALL_PARAMS.update(OPTIMIZATION_PARAMS)
ALL_PARAMS.update(MD_PARAMS)
ALL_PARAMS.update(DOS_PARAMS)
ALL_PARAMS.update(NEB_PARAMS)
ALL_PARAMS.update(PLUS_U_PARAMS)
ALL_PARAMS.update(OUTPUT_PARAMS)
ALL_PARAMS.update(PARALLEL_PARAMS)
ALL_PARAMS.update(HYBRID_PARAMS)

# ============================================================================
# DFT+U参数数据库
# ============================================================================
DFT_PLUS_U_DATABASE = {
    # 镧系元素 (Lanthanides)
    'La': {'L': 3, 'U': 5.3, 'J': 0.0, 'description': '镧，4f轨道'},
    'Ce': {'L': 3, 'U': 4.5, 'J': 0.0, 'description': '铈，4f轨道'},
    'Pr': {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '镨，4f轨道'},
    'Nd': {'L': 3, 'U': 6.2, 'J': 0.0, 'description': '钕，4f轨道'},
    'Pm': {'L': 3, 'U': 6.0, 'J': 0.0, 'description': '钷，4f轨道'},
    'Sm': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '钐，4f轨道'},
    'Eu': {'L': 3, 'U': 6.0, 'J': 0.0, 'description': '铕，4f轨道'},
    'Gd': {'L': 3, 'U': 6.2, 'J': 0.0, 'description': '钆，4f轨道'},
    'Tb': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '铽，4f轨道'},
    'Dy': {'L': 3, 'U': 6.0, 'J': 0.0, 'description': '镝，4f轨道'},
    'Ho': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '钬，4f轨道'},
    'Er': {'L': 3, 'U': 9.0, 'J': 0.0, 'description': '铒，4f轨道'},
    'Tm': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '铥，4f轨道'},
    'Yb': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '镱，4f轨道'},
    'Lu': {'L': 3, 'U': 7.0, 'J': 0.0, 'description': '镥，4f轨道'},
    
    # 锕系元素 (Actinides)
    'Ac': {'L': 3, 'U': 5.0, 'J': 0.0, 'description': '锕，5f轨道'},
    'Th': {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '钍，5f轨道'},
    'Pa': {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '镤，5f轨道'},
    'U':  {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '铀，5f轨道'},
    'Np': {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '镎，5f轨道'},
    'Pu': {'L': 3, 'U': 4.0, 'J': 0.0, 'description': '钚，5f轨道'},
    
    # 过渡金属元素 (Transition metals)
    'Ti': {'L': 2, 'U': 3.0, 'J': 0.0, 'description': '钛，3d轨道'},
    'V':  {'L': 2, 'U': 3.1, 'J': 0.0, 'description': '钒，3d轨道'},
    'Cr': {'L': 2, 'U': 3.5, 'J': 0.0, 'description': '铬，3d轨道'},
    'Mn': {'L': 2, 'U': 4.0, 'J': 0.0, 'description': '锰，3d轨道'},
    'Fe': {'L': 2, 'U': 4.3, 'J': 0.0, 'description': '铁，3d轨道'},
    'Co': {'L': 2, 'U': 3.3, 'J': 0.0, 'description': '钴，3d轨道'},
    'Ni': {'L': 2, 'U': 6.4, 'J': 0.0, 'description': '镍，3d轨道'},
    'Cu': {'L': 2, 'U': 4.0, 'J': 0.0, 'description': '铜，3d轨道'},
    'Zn': {'L': 2, 'U': 7.5, 'J': 0.0, 'description': '锌，3d轨道'},
    
    # 其他常用元素
    'Mo': {'L': 2, 'U': 4.4, 'J': 0.0, 'description': '钼，4d轨道'},
    'W':  {'L': 2, 'U': 4.0, 'J': 0.0, 'description': '钨，5d轨道'},
}

# 常用DFT+U参数组合
DFT_PLUS_U_PRESETS = {
    'lanthanides_standard': {
        'LDAU': True,
        'LDAUTYPE': 2,
        'LDAUPRINT': 1,
        'LMAXMIX': 6,
        'description': '镧系元素标准DFT+U设置'
    },
    'actinides_standard': {
        'LDAU': True,
        'LDAUTYPE': 2,
        'LDAUPRINT': 1,
        'LMAXMIX': 6,
        'description': '锕系元素标准DFT+U设置'
    },
    'transition_metals': {
        'LDAU': True,
        'LDAUTYPE': 2,
        'LDAUPRINT': 1,
        'LMAXMIX': 4,
        'description': '过渡金属标准DFT+U设置'
    }
}

# 预定义的参数配置模板
CALCULATION_TEMPLATES = {
    'optimization': {
        # 计算控制参数
        'SYSTEM': 'Structure optimization',  # 计算描述
        'ISTART': 0,                        # 读取波函数控制 (0=从头开始)
        'ICHARG': 2,                        # 电荷密度初始化 (2=原子电荷密度叠加)
        'PREC': 'Accurate',                 # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 500.0,                     # 平面波截断能 (eV)
        'EDIFF': 1e-5,                      # 电子自洽收敛判据 (eV)
        'ALGO': 'Normal',                   # 电子算法 (Normal=标准算法)
        'NELM': 500,                        # 最大电子步数
        'NELMIN': 8,                        # 最小电子步数
        'ISPIN': 2,                         # 自旋极化 (2=考虑自旋，1=不考虑)
        'ISMEAR': 0,                        # 展宽方法 (0=Gaussian)
        'SIGMA': 0.05,                      # 展宽参数 (eV)
        
        # 结构优化参数
        'NSW': 500,                         # 最大离子步数
        'IBRION': 2,                        # 离子弛豫算法 (2=CG共轭梯度)
        'ISIF': 2,                          # 优化自由度 (2=离子位置)
        'EDIFFG': -0.01,                    # 离子收敛判据 (eV/Å)
        'POTIM': 0.3,                       # 时间步长 (fs)
        
        # 性能优化参数
        'LREAL': 'A',                       # 实空间投影 (A=自动选择，适合大体系)
        'LPLANE': True,                     # 平面波并行 (True=开启平面波并行)
        'NCORE': 4,                         # 并行化设置 (每个轨道组的核数)
        
        # 输出控制参数
        'LWAVE': False,                     # 不输出WAVECAR (节省空间)
        'LCHARG': False,                    # 不输出CHGCAR (节省空间)
        'LAECHG': False,                    # 不输出全电子电荷密度
    },
    
    'scf': {
        # 计算控制参数
        'SYSTEM': 'SCF calculation',           # 计算描述
        'ISTART': 0,                          # 读取波函数控制 (0=从头开始)
        'ICHARG': 2,                          # 电荷密度初始化 (2=原子电荷密度叠加)
        'PREC': 'Accurate',                   # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 400.0,                       # 平面波截断能 (eV)
        'EDIFF': 1e-6,                        # 电子自洽收敛判据 (eV，高精度)
        'ISMEAR': 0,                          # 展宽方法 (0=Gaussian)
        'SIGMA': 0.05,                        # 展宽参数 (eV)
        
        # 离子步控制
        'NSW': 0,                             # 离子步数 (0=只做电子结构计算)
        
        # 性能优化参数
        'LREAL': False,                       # 实空间投影 (False=倒空间，更精确)
    },
    
    'dos': {
        # 计算控制参数
        'SYSTEM': 'DOS calculation',           # 计算描述
        'ISTART': 1,                          # 读取波函数控制 (1=读取WAVECAR)
        'ICHARG': 11,                         # 电荷密度控制 (11=读取CHGCAR，不更新)
        'PREC': 'Accurate',                   # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 400.0,                       # 平面波截断能 (eV)
        'EDIFF': 1e-6,                        # 电子自洽收敛判据 (eV，高精度)
        'ISMEAR': -5,                         # 展宽方法 (-5=四面体方法，适合DOS)
        'SIGMA': 0.05,                        # 展宽参数 (eV)
        
        # 离子步控制
        'NSW': 0,                             # 离子步数 (0=只做电子结构计算)
        
        # DOS特定参数
        'LORBIT': 11,                         # 轨道投影DOS (11=PDOS with phase)
        'NEDOS': 3000,                        # DOS能量点数
        
        # 性能优化参数
        'LREAL': False,                       # 实空间投影 (False=倒空间，更精确)
    },
    
    'band': {
        # 计算控制参数
        'SYSTEM': 'Band structure calculation', # 计算描述
        'ISTART': 1,                           # 读取波函数控制 (1=读取WAVECAR)
        'ICHARG': 11,                          # 电荷密度控制 (11=读取CHGCAR，不更新)
        'PREC': 'Accurate',                    # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 400.0,                        # 平面波截断能 (eV)
        'EDIFF': 1e-6,                         # 电子自洽收敛判据 (eV，高精度)
        'ISMEAR': 0,                           # 展宽方法 (0=Gaussian，适合能带)
        'SIGMA': 0.05,                         # 展宽参数 (eV)
        
        # 离子步控制
        'NSW': 0,                              # 离子步数 (0=只做电子结构计算)
        
        # 性能优化参数
        'LREAL': False,                        # 实空间投影 (False=倒空间，更精确)
    },
    
    'neb': {
        # 计算控制参数
        'SYSTEM': 'NEB calculation',           # 计算描述
        'ISTART': 0,                          # 读取波函数控制 (0=从头开始)
        'ICHARG': 2,                          # 电荷密度初始化 (2=原子电荷密度叠加)
        'PREC': 'Accurate',                   # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 400.0,                       # 平面波截断能 (eV)
        'EDIFF': 1e-5,                        # 电子自洽收敛判据 (eV)
        'ISMEAR': 0,                          # 展宽方法 (0=Gaussian)
        'SIGMA': 0.05,                        # 展宽参数 (eV)
        
        # NEB优化参数
        'NSW': 500,                           # 最大离子步数
        'IBRION': 3,                          # 离子弛豫算法 (3=Damped MD)
        'EDIFFG': -0.05,                      # 离子收敛判据 (eV/Å，NEB通常较宽松)
        
        # NEB特定参数
        'IMAGES': 5,                          # NEB中间像数
        'SPRING': -5.0,                       # 弹簧常数 (负值=变弹簧)
        'LCLIMB': True,                       # 爬坡像方法 (CI-NEB)
        'ICHAIN': 0,                          # NEB方法 (0=标准NEB)
        'IOPT': 1,                            # 优化算法 (1=LBFGS)
        
        # 性能优化参数
        'LREAL': False,                       # 实空间投影 (False=倒空间，更精确)
    },
    
    'md': {
        # 计算控制参数
        'SYSTEM': 'Molecular dynamics',        # 计算描述
        'ISTART': 0,                          # 读取波函数控制 (0=从头开始)
        'ICHARG': 2,                          # 电荷密度初始化 (2=原子电荷密度叠加)
        'PREC': 'Accurate',                   # 计算精度 (Accurate=高精度)
        
        # 电子结构参数
        'ENCUT': 400.0,                       # 平面波截断能 (eV)
        'EDIFF': 1e-5,                        # 电子自洽收敛判据 (eV)
        'ISMEAR': 0,                          # 展宽方法 (0=Gaussian)
        'SIGMA': 0.05,                        # 展宽参数 (eV)
        
        # MD运行参数
        'NSW': 1000,                          # MD步数
        'IBRION': 0,                          # MD算法 (0=分子动力学)
        'POTIM': 1.0,                         # 时间步长 (fs)
        
        # MD控制参数
        'MDALGO': 2,                          # MD算法 (2=Nose-Hoover)
        'SMASS': 0.0,                         # Nose质量参数 (0=自动)
        
        # 温度控制参数
        'TEBEG': 300.0,                       # 初始温度 (K)
        'TEEND': 300.0,                       # 最终温度 (K)
        
        # 性能优化参数
        'LREAL': False,                       # 实空间投影 (False=倒空间，更精确)
    },
}

# ============================================================================
# 磁矩数据
# ============================================================================

# 默认磁矩数据库 (基于实验和理论值)
DEFAULT_MAGNETIC_MOMENTS = {
    # 3d过渡金属 (高自旋态)
    'Ti': 2.0,   # Ti3+: d1
    'V': 3.0,    # V2+: d3  
    'Cr': 4.0,   # Cr2+: d4
    'Mn': 5.0,   # Mn2+: d5
    'Fe': 4.0,   # Fe2+: d6 (也可以是5.0用于Fe3+)
    'Co': 3.0,   # Co2+: d7
    'Ni': 2.0,   # Ni2+: d8
    'Cu': 1.0,   # Cu2+: d9
    'Zn': 0.0,   # Zn2+: d10
    
    # 4d过渡金属
    'Zr': 2.0, 'Nb': 3.0, 'Mo': 4.0, 'Tc': 5.0,
    'Ru': 4.0, 'Rh': 3.0, 'Pd': 0.0, 'Ag': 1.0,
    
    # 5d过渡金属  
    'Hf': 2.0, 'Ta': 3.0, 'W': 4.0, 'Re': 5.0,
    'Os': 4.0, 'Ir': 3.0, 'Pt': 2.0, 'Au': 1.0,
    
    # 镧系元素 (4f电子)
    'La': 0.0,   # La3+: f0
    'Ce': 1.0,   # Ce3+: f1
    'Pr': 2.0,   # Pr3+: f2
    'Nd': 3.0,   # Nd3+: f3
    'Pm': 4.0,   # Pm3+: f4
    'Sm': 5.0,   # Sm3+: f5
    'Eu': 6.0,   # Eu3+: f6
    'Gd': 7.0,   # Gd3+: f7
    'Tb': 6.0,   # Tb3+: f8
    'Dy': 5.0,   # Dy3+: f9
    'Ho': 4.0,   # Ho3+: f10
    'Er': 3.0,   # Er3+: f11
    'Tm': 2.0,   # Tm3+: f12
    'Yb': 1.0,   # Yb3+: f13
    'Lu': 0.0,   # Lu3+: f14
    
    # 锕系元素 (5f电子)
    'Ac': 0.0, 'Th': 0.0, 'Pa': 2.0, 'U': 3.0,
    'Np': 4.0, 'Pu': 5.0, 'Am': 6.0, 'Cm': 7.0,
    
    # 非磁性元素
    'H': 0.0, 'He': 0.0,
    'Li': 0.0, 'Be': 0.0, 'B': 0.0, 'C': 0.0, 'N': 0.0, 'O': 0.0, 'F': 0.0, 'Ne': 0.0,
    'Na': 0.0, 'Mg': 0.0, 'Al': 0.0, 'Si': 0.0, 'P': 0.0, 'S': 0.0, 'Cl': 0.0, 'Ar': 0.0,
    'K': 0.0, 'Ca': 0.0, 'Ga': 0.0, 'Ge': 0.0, 'As': 0.0, 'Se': 0.0, 'Br': 0.0, 'Kr': 0.0,
}

# 元素磁性分类
MAGNETIC_ELEMENTS = {
    'ferromagnetic': ['Fe', 'Co', 'Ni'],
    'antiferromagnetic': ['Mn', 'Cr'],
    'paramagnetic': ['Ti', 'V', 'Cu', 'Pd', 'Pt'],
    'lanthanides': ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu'],
    'actinides': ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm']
}

# KPOINTS模板
KPOINTS_TEMPLATES = {
    'gamma_low': {
        'method': 'gamma',
        'grid': [2, 2, 2],
        'shift': [0.0, 0.0, 0.0],
        'description': 'Gamma中心低密度K点网格，适用于大体系或快速测试'
    },
    'gamma_medium': {
        'method': 'gamma',
        'grid': [4, 4, 4],
        'shift': [0.0, 0.0, 0.0],
        'description': 'Gamma中心中等密度K点网格，适用于一般计算'
    },
    'gamma_high': {
        'method': 'gamma',
        'grid': [8, 8, 8],
        'shift': [0.0, 0.0, 0.0],
        'description': 'Gamma中心高密度K点网格，适用于精确计算'
    },
    'monkhorst_medium': {
        'method': 'monkhorst',
        'grid': [4, 4, 4],
        'shift': [0.5, 0.5, 0.5],
        'description': 'Monkhorst-Pack中等密度K点网格'
    },
    'monkhorst_high': {
        'method': 'monkhorst',
        'grid': [8, 8, 8],
        'shift': [0.5, 0.5, 0.5],
        'description': 'Monkhorst-Pack高密度K点网格'
    },
    'slab_2d': {
        'method': 'gamma',
        'grid': [8, 8, 1],
        'shift': [0.0, 0.0, 0.0],
        'description': '二维板状结构K点网格，z方向只有1个K点'
    },
    'wire_1d': {
        'method': 'gamma',
        'grid': [1, 1, 8],
        'shift': [0.0, 0.0, 0.0],
        'description': '一维线状结构K点网格，只在z方向有多个K点'
    }
}

# POTCAR配置模板
POTCAR_TEMPLATES = {
    'PBE_standard': {
        'functional': 'PBE',
        'description': 'PBE泛函标准POTCAR配置'
    },
    'PBE_hard': {
        'functional': 'PBE',
        'suffix': '_h',
        'description': 'PBE泛函硬核POTCAR配置，适用于高压计算'
    },
    'PBE_soft': {
        'functional': 'PBE',
        'suffix': '_s',
        'description': 'PBE泛函软核POTCAR配置，适用于快速计算'
    },
    'LDA_standard': {
        'functional': 'LDA',
        'description': 'LDA泛函标准POTCAR配置'
    },
    'PW91_standard': {
        'functional': 'PW91',
        'description': 'PW91泛函标准POTCAR配置'
    }
}

# SLURM作业脚本模板
SLURM_TEMPLATES = {
    'quick_test': {
        'job_name': 'vasp_test',
        'nodes': 1,
        'ntasks_per_node': 4,
        'memory': '8G',
        'time': '01:00:00',
        'partition': 'normal',
        'vasp_cmd': 'vasp_std',
        'modules': ['intel/2021', 'vasp/6.3.0'],
        'description': '快速测试配置，适用于小体系或参数测试'
    },
    'standard': {
        'job_name': 'vasp_calc',
        'nodes': 1,
        'ntasks_per_node': 24,
        'memory': '32G',
        'time': '12:00:00',
        'partition': 'normal',
        'vasp_cmd': 'vasp_std',
        'modules': ['intel/2021', 'vasp/6.3.0'],
        'description': '标准计算配置，适用于大多数VASP计算'
    },
    'large_system': {
        'job_name': 'vasp_large',
        'nodes': 2,
        'ntasks_per_node': 24,
        'memory': '64G',
        'time': '24:00:00',
        'partition': 'normal',
        'vasp_cmd': 'vasp_std',
        'modules': ['intel/2021', 'vasp/6.3.0'],
        'description': '大体系计算配置，适用于超过200原子的体系'
    },
    'gpu_accelerated': {
        'job_name': 'vasp_gpu',
        'nodes': 1,
        'ntasks_per_node': 8,
        'memory': '32G',
        'time': '12:00:00',
        'partition': 'gpu',
        'vasp_cmd': 'vasp_gpu',
        'modules': ['cuda/11.2', 'vasp/6.3.0-gpu'],
        'extra_options': ['#SBATCH --gres=gpu:2'],
        'description': 'GPU加速计算配置'
    },
    'long_job': {
        'job_name': 'vasp_long',
        'nodes': 1,
        'ntasks_per_node': 24,
        'memory': '32G',
        'time': '72:00:00',
        'partition': 'long',
        'vasp_cmd': 'vasp_std',
        'modules': ['intel/2021', 'vasp/6.3.0'],
        'description': '长时间计算配置，适用于收敛困难的体系'
    }
}

# SLURM脚本内容模板
SLURM_SCRIPT_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={ntasks_per_node}
#SBATCH --mem={memory}
#SBATCH --time={time}
#SBATCH --partition={partition}
#SBATCH --output=vasp_%j.out
#SBATCH --error=vasp_%j.err
{extra_options}

# 环境设置
set -e
{module_commands}

# 作业信息
echo "作业开始时间: $(date)"
echo "节点信息: $SLURM_JOB_NODELIST"
echo "作业ID: $SLURM_JOB_ID"
echo "工作目录: $(pwd)"

# 检查输入文件
required_files=("POSCAR" "INCAR" "KPOINTS" "POTCAR")
for file in "${{required_files[@]}}"; do
    if [[ ! -f "$file" ]]; then
        echo "错误: 缺少必要文件 $file"
        exit 1
    fi
done
echo "所有输入文件检查完毕"

# 运行VASP
total_cores=$((SLURM_NNODES * SLURM_NTASKS_PER_NODE))
echo "使用 $total_cores 个核心运行VASP"
mpirun -np $total_cores {vasp_cmd}

# 作业完成
echo "作业完成时间: $(date)"
if [[ -f "OUTCAR" ]]; then
    if grep -q "reached required accuracy" OUTCAR; then
        echo "✅ VASP计算成功收敛"
    else
        echo "⚠️  VASP计算可能未收敛，请检查OUTCAR"
    fi
else
    echo "❌ 未找到OUTCAR文件，计算可能失败"
fi
"""
