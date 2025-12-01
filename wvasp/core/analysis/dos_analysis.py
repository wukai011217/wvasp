"""
态密度分析模块

提供态密度数据的深度分析功能，包括DOSCAR文件的解析。
"""

import re
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from ...utils.errors import FileFormatError
from .energy_analysis import EnergyAnalyzer


class DOSAnalyzer:
    """态密度分析器，直接处理DOSCAR文件"""
    
    def __init__(self, calculation_dir: Path):
        """
        初始化态密度分析器
        
        Args:
            calculation_dir: 计算目录路径，包含DOSCAR和OUTCAR文件
        """
        self.calculation_dir = Path(calculation_dir)
        self.doscar_path = self.calculation_dir / "DOSCAR"
        self.outcar_path = self.calculation_dir / "OUTCAR"
        
        self.dos_data = None
        self.fermi_energy = None
        self._is_loaded = False
        
    def load_data(self) -> Dict[str, Any]:
        """加载DOS数据"""
        if not self.doscar_path.exists():
            raise FileFormatError(f"DOSCAR file not found: {self.doscar_path}")
        
        # 解析DOSCAR
        self.dos_data = self._parse_doscar()
        
        # 从OUTCAR获取费米能级
        if self.outcar_path.exists():
            energy_analyzer = EnergyAnalyzer(self.outcar_path)
            energy_data = energy_analyzer.load_data()
            self.fermi_energy = energy_data.get('fermi_energy')
        
        self._is_loaded = True
        return self.dos_data
    
    def _parse_doscar(self) -> Dict[str, Any]:
        """解析DOSCAR文件"""
        with open(self.doscar_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 6:
            raise FileFormatError("DOSCAR file too short")
        
        # 解析头部信息
        header = self._parse_header(lines)
        
        # 解析DOS数据
        dos_data = self._parse_dos_data(lines, header)
        
        return {
            'header': header,
            'total_dos': dos_data['total_dos'],
            'partial_dos': dos_data.get('partial_dos', {}),
            'energies': dos_data['energies'],
            'is_spin_polarized': header['ispin'] == 2,
        }
    
    def _parse_header(self, lines: List[str]) -> Dict[str, Any]:
        """解析DOSCAR头部信息"""
        # 第1行：原子数、体积等
        first_line = lines[0].split()
        natoms = int(first_line[0])
        
        # 第6行：NEDOS, EFERMI, etc.
        sixth_line = lines[5].split()
        nedos = int(sixth_line[2])
        efermi = float(sixth_line[3])
        
        # 从第5行推断ISPIN
        fifth_line = lines[4].split()
        ispin = 2 if len(fifth_line) > 4 else 1
        
        return {
            'natoms': natoms,
            'nedos': nedos,
            'efermi': efermi,
            'ispin': ispin,
        }
    
    def _parse_dos_data(self, lines: List[str], header: Dict[str, Any]) -> Dict[str, Any]:
        """解析DOS数据"""
        nedos = header['nedos']
        ispin = header['ispin']
        
        # 总DOS从第7行开始
        start_line = 6
        end_line = start_line + nedos
        
        energies = []
        total_dos = {'up': [], 'down': []} if ispin == 2 else {'total': []}
        
        for i in range(start_line, end_line):
            if i >= len(lines):
                break
            
            parts = lines[i].split()
            if len(parts) < 2:
                continue
            
            energy = float(parts[0])
            energies.append(energy)
            
            if ispin == 2:
                # 自旋极化
                dos_up = float(parts[1])
                dos_down = float(parts[2]) if len(parts) > 2 else 0.0
                total_dos['up'].append(dos_up)
                total_dos['down'].append(dos_down)
            else:
                # 非自旋极化
                dos_total = float(parts[1])
                total_dos['total'].append(dos_total)
        
        # 解析分波DOS（如果存在）
        partial_dos = self._parse_partial_dos(lines, header, end_line)
        
        return {
            'energies': np.array(energies),
            'total_dos': total_dos,
            'partial_dos': partial_dos,
        }
    
    def _parse_partial_dos(self, lines: List[str], header: Dict[str, Any], start_line: int) -> Dict[str, Any]:
        """解析分波DOS"""
        # 这里可以根据需要实现分波DOS的解析
        # 暂时返回空字典
        return {}
    
    def get_band_gap(self) -> Optional[float]:
        """
        计算带隙
        
        Returns:
            带隙值（eV），如果是金属则返回0
        """
        if not self.dos_data:
            self.load_data()
        
        energies = self.dos_data.get('energies')
        total_dos = self.dos_data.get('total_dos')
        
        if energies is None or total_dos is None or self.fermi_energy is None:
            return None
        
        # 将能量相对于费米能级
        rel_energies = energies - self.fermi_energy
        
        # 找到费米能级附近的DOS
        fermi_idx = np.argmin(np.abs(rel_energies))
        
        # 检查费米能级处的DOS
        fermi_dos = total_dos[fermi_idx] if len(total_dos.shape) == 1 else np.sum(total_dos[fermi_idx])
        
        # 如果费米能级处DOS很小，可能是绝缘体
        if fermi_dos < 0.01:  # 阈值可调
            # 寻找价带顶和导带底
            below_fermi = rel_energies < 0
            above_fermi = rel_energies > 0
            
            if np.any(below_fermi) and np.any(above_fermi):
                # 价带顶：费米能级以下最高能量处有显著DOS
                vb_energies = rel_energies[below_fermi]
                vb_dos = total_dos[below_fermi] if len(total_dos.shape) == 1 else np.sum(total_dos[below_fermi], axis=1)
                
                # 导带底：费米能级以上最低能量处有显著DOS
                cb_energies = rel_energies[above_fermi]
                cb_dos = total_dos[above_fermi] if len(total_dos.shape) == 1 else np.sum(total_dos[above_fermi], axis=1)
                
                # 找到有显著DOS的能量点
                vb_significant = vb_dos > 0.01
                cb_significant = cb_dos > 0.01
                
                if np.any(vb_significant) and np.any(cb_significant):
                    vbm = np.max(vb_energies[vb_significant])
                    cbm = np.min(cb_energies[cb_significant])
                    return cbm - vbm
        
        return 0.0  # 金属
    
    def get_dos_at_fermi(self) -> float:
        """
        获取费米能级处的态密度
        
        Returns:
            费米能级处的态密度值
        """
        if not self.dos_data:
            self.load_data()
        
        energies = self.dos_data.get('energies')
        total_dos = self.dos_data.get('total_dos')
        
        if energies is None or total_dos is None or self.fermi_energy is None:
            return 0.0
        
        fermi_idx = np.argmin(np.abs(energies - self.fermi_energy))
        
        if len(total_dos.shape) == 1:
            return total_dos[fermi_idx]
        else:
            return np.sum(total_dos[fermi_idx])
    
    def integrate_dos(self, energy_range: Tuple[float, float]) -> float:
        """
        在指定能量范围内积分态密度
        
        Args:
            energy_range: 能量范围 (emin, emax)，相对于费米能级
            
        Returns:
            积分值（电子数）
        """
        if not self.dos_data:
            self.load_data()
        
        energies = self.dos_data.get('energies')
        total_dos = self.dos_data.get('total_dos')
        
        if energies is None or total_dos is None or self.fermi_energy is None:
            return 0.0
        
        rel_energies = energies - self.fermi_energy
        mask = (rel_energies >= energy_range[0]) & (rel_energies <= energy_range[1])
        
        if not np.any(mask):
            return 0.0
        
        selected_energies = rel_energies[mask]
        selected_dos = total_dos[mask] if len(total_dos.shape) == 1 else np.sum(total_dos[mask], axis=1)
        
        # 使用梯形积分
        return np.trapz(selected_dos, selected_energies)
    
    def get_projected_dos(self, atom_indices: Optional[List[int]] = None, 
                         orbitals: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """
        获取投影态密度
        
        Args:
            atom_indices: 原子索引列表
            orbitals: 轨道列表 ['s', 'p', 'd', 'f']
            
        Returns:
            投影态密度数据
        """
        if not self.dos_data:
            self.load_data()
        
        projected_dos = self.dos_data.get('projected_dos', {})
        
        if not projected_dos:
            return {}
        
        result = {}
        
        # 按原子筛选
        if atom_indices is not None:
            for atom_idx in atom_indices:
                if atom_idx in projected_dos:
                    result[f'atom_{atom_idx}'] = projected_dos[atom_idx]
        else:
            result = projected_dos.copy()
        
        # 按轨道筛选（如果需要更细致的轨道分析）
        if orbitals is not None:
            # 这里需要根据DOSCAR的具体格式来实现轨道筛选
            pass
        
        return result
    
    def analyze_electronic_structure(self) -> Dict[str, Any]:
        """
        综合分析电子结构
        
        Returns:
            电子结构分析结果
        """
        if not self.dos_data:
            self.load_data()
        
        analysis = {
            'band_gap': self.get_band_gap(),
            'dos_at_fermi': self.get_dos_at_fermi(),
            'fermi_energy': self.fermi_energy,
            'is_metal': self.get_band_gap() == 0.0 if self.get_band_gap() is not None else None,
            'valence_electrons': self.integrate_dos((-20.0, 0.0)),  # 价带电子数
            'total_electrons': self.integrate_dos((-20.0, 20.0)),   # 总电子数（近似）
        }
        
        # 添加自旋信息
        if self.dos_data.get('is_spin_polarized', False):
            analysis['is_spin_polarized'] = True
            # 可以添加更多自旋相关的分析
        else:
            analysis['is_spin_polarized'] = False
        
        return analysis