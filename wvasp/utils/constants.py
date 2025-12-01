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

# VASP参数定义和验证
class VASPParameters:
    """VASP参数管理类，提供参数验证和默认值"""
    
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
    
    @classmethod
    def validate_parameter(cls, name: str, value) -> bool:
        """
        验证参数值是否有效
        
        Args:
            name: 参数名
            value: 参数值
            
        Returns:
            是否有效
        """
        if name not in cls.ALL_PARAMS:
            return False
        
        param_def = cls.ALL_PARAMS[name]
        param_type = param_def['type']
        
        # 检查类型
        if isinstance(param_type, list):
            if not any(isinstance(value, t) for t in param_type):
                return False
        else:
            if not isinstance(value, param_type):
                return False
        
        # 检查值范围
        if 'values' in param_def:
            if value not in param_def['values']:
                return False
        
        if 'min' in param_def and isinstance(value, (int, float)):
            if value < param_def['min']:
                return False
        
        if 'max' in param_def and isinstance(value, (int, float)):
            if value > param_def['max']:
                return False
        
        return True
    
    @classmethod
    def get_default(cls, name: str):
        """获取参数默认值"""
        if name in cls.ALL_PARAMS:
            return cls.ALL_PARAMS[name].get('default')
        return None
    
    @classmethod
    def get_parameter_info(cls, name: str) -> dict:
        """获取参数信息"""
        return cls.ALL_PARAMS.get(name, {})

# DFT+U参数数据库
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
        'SYSTEM': 'Structure optimization',
        'ISTART': 0,
        'ICHARG': 2,
        'ENCUT': 400.0,
        'ISMEAR': 0,
        'SIGMA': 0.05,
        'EDIFF': 1e-5,
        'EDIFFG': -0.01,
        'NSW': 500,
        'IBRION': 2,
        'ISIF': 3,
        'LREAL': False,
        'PREC': 'Accurate',
    },
    
    'scf': {
        'SYSTEM': 'SCF calculation',
        'ISTART': 0,
        'ICHARG': 2,
        'ENCUT': 400.0,
        'ISMEAR': 0,
        'SIGMA': 0.05,
        'EDIFF': 1e-6,
        'NSW': 0,
        'LREAL': False,
        'PREC': 'Accurate',
    },
    
    'dos': {
        'SYSTEM': 'DOS calculation',
        'ISTART': 1,
        'ICHARG': 11,
        'ENCUT': 400.0,
        'ISMEAR': -5,
        'SIGMA': 0.05,
        'EDIFF': 1e-6,
        'NSW': 0,
        'LORBIT': 11,
        'NEDOS': 3000,
        'LREAL': False,
        'PREC': 'Accurate',
    },
    
    'band': {
        'SYSTEM': 'Band structure calculation',
        'ISTART': 1,
        'ICHARG': 11,
        'ENCUT': 400.0,
        'ISMEAR': 0,
        'SIGMA': 0.05,
        'EDIFF': 1e-6,
        'NSW': 0,
        'LREAL': False,
        'PREC': 'Accurate',
    },
    
    'neb': {
        'SYSTEM': 'NEB calculation',
        'ISTART': 0,
        'ICHARG': 2,
        'ENCUT': 400.0,
        'ISMEAR': 0,
        'SIGMA': 0.05,
        'EDIFF': 1e-5,
        'EDIFFG': -0.05,
        'NSW': 500,
        'IBRION': 3,
        'IMAGES': 5,
        'SPRING': -5.0,
        'LCLIMB': True,
        'ICHAIN': 0,
        'IOPT': 1,
        'LREAL': False,
        'PREC': 'Accurate',
    },
    
    'md': {
        'SYSTEM': 'Molecular dynamics',
        'ISTART': 0,
        'ICHARG': 2,
        'ENCUT': 400.0,
        'ISMEAR': 0,
        'SIGMA': 0.05,
        'EDIFF': 1e-5,
        'NSW': 1000,
        'IBRION': 0,
        'POTIM': 1.0,
        'SMASS': 0.0,
        'MDALGO': 2,
        'TEBEG': 300.0,
        'TEEND': 300.0,
        'LREAL': False,
        'PREC': 'Accurate',
    },
}
