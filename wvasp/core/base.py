"""
基础数据结构

定义WVasp工具的核心数据结构：Atom, Lattice, Structure等。
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Tuple
import numpy as np

from ..utils.constants import ATOMIC_NUMBERS, ATOMIC_MASSES, DEFAULT_TOLERANCE
from ..utils.errors import StructureError


@dataclass
class Atom:
    """
    原子类
    
    表示单个原子的基本信息。
    
    Attributes:
        element: 元素符号
        position: 原子位置坐标 (3D numpy数组)
        magnetic_moment: 磁矩 (可选)
        charge: 电荷 (可选)
        velocity: 速度 (可选，用于MD计算)
    """
    element: str
    position: np.ndarray
    magnetic_moment: Optional[float] = None
    charge: Optional[float] = None
    velocity: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """
        __post_init__ 方法会在对象初始化之后立即被调用。
        与 __init__ 方法不同，它不需要显式调用 super().__init__()。
        
        这里可以用来进行一些额外的验证或初始化操作。
        """
        """初始化后的验证"""
        if self.element not in ATOMIC_NUMBERS:
            raise StructureError(f"Unknown element: {self.element}")
        
        if len(self.position) != 3:
            raise StructureError("Position must be a 3D vector")
        
        self.position = np.array(self.position, dtype=float)
        
        if self.velocity is not None:
            if len(self.velocity) != 3:
                raise StructureError("Velocity must be a 3D vector")
            self.velocity = np.array(self.velocity, dtype=float)
    
    @property
    def atomic_number(self) -> int:
        """原子序数"""
        return ATOMIC_NUMBERS[self.element]
    
    @property
    def atomic_mass(self) -> float:
        """原子质量"""
        return ATOMIC_MASSES.get(self.element, 0.0)
    
    def distance_to(self, other: 'Atom') -> float:
        """计算到另一个原子的距离"""
        return np.linalg.norm(self.position - other.position)
    
    def __repr__(self) -> str:
        return f"Atom({self.element}, {self.position})"


@dataclass
class Lattice:
    """
    晶格类
    
    表示晶体的晶格信息。
    
    Attributes:
        matrix: 3x3晶格矩阵，每行代表一个晶格矢量
    """
    matrix: np.ndarray
    
    def __post_init__(self):
        """初始化后的验证"""
        self.matrix = np.array(self.matrix, dtype=float)
        if self.matrix.shape != (3, 3):
            raise StructureError("Lattice matrix must be 3x3")
    
    @property
    def volume(self) -> float:
        """晶胞体积"""
        return abs(np.linalg.det(self.matrix))
    
    @property
    def lengths(self) -> np.ndarray:
        """晶格矢量长度"""
        return np.linalg.norm(self.matrix, axis=1)
    
    @property
    def angles(self) -> np.ndarray:
        """晶格角度 (alpha, beta, gamma) in degrees"""
        a, b, c = self.matrix
        alpha = np.arccos(np.dot(b, c) / (np.linalg.norm(b) * np.linalg.norm(c)))
        beta = np.arccos(np.dot(a, c) / (np.linalg.norm(a) * np.linalg.norm(c)))
        gamma = np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        return np.degrees([alpha, beta, gamma])
    
    @property
    def reciprocal_lattice(self) -> 'Lattice':
        """倒格子"""
        reciprocal_matrix = 2 * np.pi * np.linalg.inv(self.matrix).T
        return Lattice(reciprocal_matrix)
    
    def cart_to_frac(self, cart_coords: np.ndarray) -> np.ndarray:
        """笛卡尔坐标转分数坐标"""
        return np.linalg.solve(self.matrix.T, cart_coords.T).T
    
    def frac_to_cart(self, frac_coords: np.ndarray) -> np.ndarray:
        """分数坐标转笛卡尔坐标"""
        return np.dot(frac_coords, self.matrix)
    
    def __repr__(self) -> str:
        return f"Lattice(volume={self.volume:.3f})"


class Structure:
    """
    结构类
    
    表示完整的晶体结构，包含晶格和原子信息。
    
    Attributes:
        lattice: 晶格对象
        atoms: 原子列表
        coordinate_type: 坐标类型 ('cartesian' 或 'fractional')
    """
    
    def __init__(self, 
                 lattice: Lattice, 
                 atoms: List[Atom],
                 coordinate_type: str = 'fractional'):
        """
        初始化结构
        
        Args:
            lattice: 晶格对象
            atoms: 原子列表
            coordinate_type: 坐标类型
        """
        self.lattice = lattice
        self.atoms = atoms
        self.coordinate_type = coordinate_type.lower()
        
        if self.coordinate_type not in ['cartesian', 'fractional']:
            raise StructureError("coordinate_type must be 'cartesian' or 'fractional'")
    
    @property
    def num_atoms(self) -> int:
        """原子总数"""
        return len(self.atoms)
    
    @property
    def volume(self) -> float:
        """晶胞体积"""
        return self.lattice.volume
    
    @property
    def density(self) -> float:
        """密度 (g/cm³)"""
        total_mass = sum(atom.atomic_mass for atom in self.atoms)
        volume_cm3 = self.volume * 1e-24  # Å³ to cm³
        avogadro = 6.022e23
        return total_mass / (volume_cm3 * avogadro)
    
    @property
    def composition(self) -> dict:
        """成分统计"""
        comp = {}
        for atom in self.atoms:
            comp[atom.element] = comp.get(atom.element, 0) + 1
        return comp
    
    @property
    def formula(self) -> str:
        """化学式"""
        comp = self.composition
        formula_parts = []
        for element in sorted(comp.keys()):
            count = comp[element]
            if count == 1:
                formula_parts.append(element)
            else:
                formula_parts.append(f"{element}{count}")
        return "".join(formula_parts)
    
    def get_cartesian_coords(self) -> np.ndarray:
        """获取笛卡尔坐标"""
        positions = np.array([atom.position for atom in self.atoms])
        if self.coordinate_type == 'fractional':
            return self.lattice.frac_to_cart(positions)
        return positions
    
    def get_fractional_coords(self) -> np.ndarray:
        """获取分数坐标"""
        positions = np.array([atom.position for atom in self.atoms])
        if self.coordinate_type == 'cartesian':
            return self.lattice.cart_to_frac(positions)
        return positions
    
    def get_atoms_by_element(self, element: str) -> List[Atom]:
        """根据元素获取原子"""
        return [atom for atom in self.atoms if atom.element == element]
    
    def get_distances(self, atom1_idx: int, atom2_idx: int) -> float:
        """计算两个原子间的距离"""
        if atom1_idx >= len(self.atoms) or atom2_idx >= len(self.atoms):
            raise StructureError("Atom index out of range")
        
        pos1 = self.atoms[atom1_idx].position
        pos2 = self.atoms[atom2_idx].position
        
        if self.coordinate_type == 'fractional':
            pos1 = self.lattice.frac_to_cart(pos1)
            pos2 = self.lattice.frac_to_cart(pos2)
        
        return np.linalg.norm(pos1 - pos2)
    
    def copy(self) -> 'Structure':
        """创建结构的深拷贝"""
        import copy
        return copy.deepcopy(self)
    
    def __len__(self) -> int:
        return self.num_atoms
    
    def __repr__(self) -> str:
        return f"Structure({self.formula}, {self.num_atoms} atoms)"
