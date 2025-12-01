"""
结构分析模块

提供晶体结构的几何和对称性分析功能。
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

from ..base import Structure, Atom, Lattice
from ..io import POSCAR
from .energy_analysis import EnergyAnalyzer


class StructureAnalyzer:
    """结构分析器"""
    
    def __init__(self, structure: Structure):
        """
        初始化结构分析器
        
        Args:
            structure: 待分析的结构
        """
        self.structure = structure
    
    @classmethod
    def from_poscar(cls, poscar_path: Path):
        """从POSCAR文件创建分析器"""
        poscar = POSCAR(poscar_path)
        structure = poscar.read()
        return cls(structure)
    
    def get_distances(self, atom1_idx: int, atom2_idx: int) -> float:
        """
        计算两个原子间的距离
        
        Args:
            atom1_idx: 原子1索引
            atom2_idx: 原子2索引
            
        Returns:
            原子间距离（Å）
        """
        if atom1_idx >= len(self.structure.atoms) or atom2_idx >= len(self.structure.atoms):
            raise ValueError("原子索引超出范围")
        
        pos1 = self.structure.atoms[atom1_idx].position
        pos2 = self.structure.atoms[atom2_idx].position
        
        # 转换为笛卡尔坐标
        if self.structure.coordinate_type == 'fractional':
            pos1 = self.structure.lattice.frac_to_cart(pos1.reshape(1, -1))[0]
            pos2 = self.structure.lattice.frac_to_cart(pos2.reshape(1, -1))[0]
        
        return np.linalg.norm(pos2 - pos1)
    
    def get_all_distances(self, max_distance: float = 5.0) -> List[Tuple[int, int, float]]:
        """
        计算所有原子对的距离
        
        Args:
            max_distance: 最大距离阈值（Å）
            
        Returns:
            (atom1_idx, atom2_idx, distance) 的列表
        """
        distances = []
        
        for i in range(len(self.structure.atoms)):
            for j in range(i + 1, len(self.structure.atoms)):
                dist = self.get_distances(i, j)
                if dist <= max_distance:
                    distances.append((i, j, dist))
        
        return sorted(distances, key=lambda x: x[2])
    
    def get_coordination_numbers(self, cutoff_distance: float = 3.0) -> Dict[int, int]:
        """
        计算配位数
        
        Args:
            cutoff_distance: 配位距离阈值（Å）
            
        Returns:
            每个原子的配位数
        """
        coordination = {i: 0 for i in range(len(self.structure.atoms))}
        
        distances = self.get_all_distances(cutoff_distance)
        
        for atom1_idx, atom2_idx, dist in distances:
            coordination[atom1_idx] += 1
            coordination[atom2_idx] += 1
        
        return coordination
    
    def get_bond_angles(self, center_atom: int, neighbor1: int, neighbor2: int) -> float:
        """
        计算键角
        
        Args:
            center_atom: 中心原子索引
            neighbor1: 邻居原子1索引
            neighbor2: 邻居原子2索引
            
        Returns:
            键角（度）
        """
        center_pos = self.structure.atoms[center_atom].position
        neighbor1_pos = self.structure.atoms[neighbor1].position
        neighbor2_pos = self.structure.atoms[neighbor2].position
        
        # 转换为笛卡尔坐标
        if self.structure.coordinate_type == 'fractional':
            center_pos = self.structure.lattice.frac_to_cart(center_pos.reshape(1, -1))[0]
            neighbor1_pos = self.structure.lattice.frac_to_cart(neighbor1_pos.reshape(1, -1))[0]
            neighbor2_pos = self.structure.lattice.frac_to_cart(neighbor2_pos.reshape(1, -1))[0]
        
        # 计算向量
        vec1 = neighbor1_pos - center_pos
        vec2 = neighbor2_pos - center_pos
        
        # 计算角度
        cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # 防止数值误差
        
        angle_rad = np.arccos(cos_angle)
        return np.degrees(angle_rad)
    
    def get_density(self) -> float:
        """
        计算密度
        
        Returns:
            密度（g/cm³）
        """
        return self.structure.density
    
    def get_packing_fraction(self, atomic_radii: Optional[Dict[str, float]] = None) -> float:
        """
        计算堆积系数
        
        Args:
            atomic_radii: 原子半径字典（Å）
            
        Returns:
            堆积系数
        """
        if atomic_radii is None:
            # 使用默认原子半径（简化版）
            atomic_radii = {
                'H': 0.37, 'He': 0.32, 'Li': 1.34, 'Be': 0.90, 'B': 0.82,
                'C': 0.77, 'N': 0.75, 'O': 0.73, 'F': 0.71, 'Ne': 0.69,
                'Na': 1.54, 'Mg': 1.30, 'Al': 1.18, 'Si': 1.11, 'P': 1.06,
                'S': 1.02, 'Cl': 0.99, 'Ar': 0.97, 'K': 1.96, 'Ca': 1.74,
                'Fe': 1.17, 'Ni': 1.15, 'Cu': 1.17, 'Zn': 1.25,
            }
        
        total_atomic_volume = 0.0
        
        for atom in self.structure.atoms:
            radius = atomic_radii.get(atom.element, 1.0)  # 默认半径1.0Å
            atomic_volume = (4/3) * np.pi * radius**3
            total_atomic_volume += atomic_volume
        
        cell_volume = self.structure.volume
        
        return total_atomic_volume / cell_volume if cell_volume > 0 else 0.0
    
    def analyze_symmetry(self) -> Dict[str, Any]:
        """
        简单的对称性分析
        
        Returns:
            对称性分析结果
        """
        # 这是一个简化版本，实际的对称性分析需要更复杂的算法
        analysis = {
            'lattice_type': self._classify_lattice(),
            'lattice_parameters': {
                'a': self.structure.lattice.lengths[0],
                'b': self.structure.lattice.lengths[1], 
                'c': self.structure.lattice.lengths[2],
                'alpha': self.structure.lattice.angles[0],
                'beta': self.structure.lattice.angles[1],
                'gamma': self.structure.lattice.angles[2],
            },
            'volume': self.structure.volume,
        }
        
        return analysis
    
    def _classify_lattice(self) -> str:
        """简单的晶格分类"""
        lengths = self.structure.lattice.lengths
        angles = self.structure.lattice.angles
        
        # 容差
        length_tol = 0.01
        angle_tol = 1.0  # 度
        
        a, b, c = lengths
        alpha, beta, gamma = angles
        
        # 检查长度关系
        a_eq_b = abs(a - b) < length_tol
        b_eq_c = abs(b - c) < length_tol
        a_eq_c = abs(a - c) < length_tol
        
        # 检查角度关系
        alpha_90 = abs(alpha - 90.0) < angle_tol
        beta_90 = abs(beta - 90.0) < angle_tol
        gamma_90 = abs(gamma - 90.0) < angle_tol
        gamma_120 = abs(gamma - 120.0) < angle_tol
        
        # 分类逻辑
        if a_eq_b and b_eq_c and alpha_90 and beta_90 and gamma_90:
            return "cubic"
        elif a_eq_b and alpha_90 and beta_90 and gamma_90:
            return "tetragonal"
        elif alpha_90 and beta_90 and gamma_90:
            return "orthorhombic"
        elif a_eq_b and alpha_90 and beta_90 and gamma_120:
            return "hexagonal"
        elif alpha_90 and gamma_90:
            return "monoclinic"
        else:
            return "triclinic"
    
    def compare_structures(self, other_structure: Structure, 
                          position_tolerance: float = 0.1) -> Dict[str, Any]:
        """
        比较两个结构
        
        Args:
            other_structure: 另一个结构
            position_tolerance: 位置容差（Å）
            
        Returns:
            结构比较结果
        """
        comparison = {
            'same_composition': self.structure.composition == other_structure.composition,
            'volume_change': other_structure.volume - self.structure.volume,
            'volume_change_percent': ((other_structure.volume - self.structure.volume) / 
                                    self.structure.volume * 100) if self.structure.volume > 0 else 0,
            'lattice_change': {
                'a': other_structure.lattice.lengths[0] - self.structure.lattice.lengths[0],
                'b': other_structure.lattice.lengths[1] - self.structure.lattice.lengths[1],
                'c': other_structure.lattice.lengths[2] - self.structure.lattice.lengths[2],
            }
        }
        
        # 原子位置变化（如果原子数相同）
        if len(self.structure.atoms) == len(other_structure.atoms):
            max_displacement = 0.0
            total_displacement = 0.0
            
            for i, (atom1, atom2) in enumerate(zip(self.structure.atoms, other_structure.atoms)):
                if atom1.element == atom2.element:
                    # 计算位移
                    pos1 = atom1.position
                    pos2 = atom2.position
                    
                    if self.structure.coordinate_type == 'fractional':
                        pos1 = self.structure.lattice.frac_to_cart(pos1.reshape(1, -1))[0]
                    if other_structure.coordinate_type == 'fractional':
                        pos2 = other_structure.lattice.frac_to_cart(pos2.reshape(1, -1))[0]
                    
                    displacement = np.linalg.norm(pos2 - pos1)
                    max_displacement = max(max_displacement, displacement)
                    total_displacement += displacement
            
            comparison.update({
                'max_atomic_displacement': max_displacement,
                'average_atomic_displacement': total_displacement / len(self.structure.atoms),
                'significant_structural_change': max_displacement > position_tolerance,
            })
        
        return comparison