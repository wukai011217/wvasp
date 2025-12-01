"""
能量分析模块

提供OUTCAR文件的解析和能量相关分析功能。
"""

import re
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from ...utils.errors import FileFormatError


class EnergyAnalyzer:
    """能量分析器，处理OUTCAR文件"""
    
    def __init__(self, outcar_path: Path):
        """
        初始化能量分析器
        
        Args:
            outcar_path: OUTCAR文件路径
        """
        self.outcar_path = Path(outcar_path)
        self._data = None
        self._is_loaded = False
        
    def load_data(self) -> Dict[str, Any]:
        """
        加载OUTCAR数据
        
        Returns:
            包含能量和其他计算信息的字典
        """
        if not self.outcar_path.exists():
            raise FileFormatError(f"OUTCAR file not found: {self.outcar_path}")
        
        self._data = self._parse_outcar()
        self._is_loaded = True
        return self._data
    
    def _parse_outcar(self) -> Dict[str, Any]:
        """解析OUTCAR文件"""
        data = {
            'energies': [],
            'forces': [],
            'stress': [],
            'fermi_energy': None,
            'total_energy': None,
            'convergence': False,
            'ionic_steps': 0,
            'electronic_steps': [],
            'timing': {},
            'magnetic_moments': [],
        }
        
        with open(self.outcar_path, 'r') as f:
            lines = f.readlines()
        
        # 解析各种信息
        self._parse_energies(lines, data)
        self._parse_forces(lines, data)
        self._parse_stress(lines, data)
        self._parse_fermi_energy(lines, data)
        self._parse_magnetic_moments(lines, data)
        self._parse_timing(lines, data)
        self._check_convergence(lines, data)
        
        return data
    
    def _parse_energies(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析能量信息"""
        energy_pattern = re.compile(r'free  energy   TOTEN  =\s+(-?\d+\.\d+)\s+eV')
        
        for line in lines:
            match = energy_pattern.search(line)
            if match:
                energy = float(match.group(1))
                data['energies'].append(energy)
        
        if data['energies']:
            data['total_energy'] = data['energies'][-1]
    
    def _parse_forces(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析原子受力信息"""
        in_forces_section = False
        current_forces = []
        
        for line in lines:
            if 'TOTAL-FORCE (eV/Angst)' in line:
                in_forces_section = True
                current_forces = []
                continue
            
            if in_forces_section:
                if line.strip() == '' or '---' in line:
                    if current_forces:
                        data['forces'].append(np.array(current_forces))
                        current_forces = []
                    in_forces_section = False
                    continue
                
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        force = [float(parts[3]), float(parts[4]), float(parts[5])]
                        current_forces.append(force)
                    except (ValueError, IndexError):
                        continue
    
    def _parse_stress(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析应力信息"""
        stress_pattern = re.compile(r'in kB\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)')
        
        for i, line in enumerate(lines):
            if 'FORCE on cell =-STRESS in cart. coord.  units (eV):' in line:
                # 查找应力张量
                for j in range(i+1, min(i+10, len(lines))):
                    match = stress_pattern.search(lines[j])
                    if match:
                        stress_values = [float(x) for x in match.groups()]
                        if len(data['stress']) == 0 or len(data['stress'][-1]) < 6:
                            data['stress'].append(stress_values)
                        else:
                            data['stress'][-1].extend(stress_values)
    
    def _parse_fermi_energy(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析费米能级"""
        fermi_pattern = re.compile(r'E-fermi :\s+(-?\d+\.\d+)')
        
        for line in lines:
            match = fermi_pattern.search(line)
            if match:
                data['fermi_energy'] = float(match.group(1))
    
    def _parse_magnetic_moments(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析磁矩信息"""
        in_mag_section = False
        current_moments = []
        
        for line in lines:
            if 'magnetization (x)' in line:
                in_mag_section = True
                current_moments = []
                continue
            
            if in_mag_section:
                if line.strip() == '' or '---' in line:
                    if current_moments:
                        data['magnetic_moments'].append(current_moments)
                        current_moments = []
                    in_mag_section = False
                    continue
                
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        moment = float(parts[4])
                        current_moments.append(moment)
                    except (ValueError, IndexError):
                        continue
    
    def _parse_timing(self, lines: List[str], data: Dict[str, Any]) -> None:
        """解析计算时间信息"""
        timing_patterns = {
            'total_cpu_time': re.compile(r'Total CPU time used \(sec\):\s+(\d+\.\d+)'),
            'elapsed_time': re.compile(r'Elapsed time \(sec\):\s+(\d+\.\d+)'),
        }
        
        for line in lines:
            for key, pattern in timing_patterns.items():
                match = pattern.search(line)
                if match:
                    data['timing'][key] = float(match.group(1))
    
    def _check_convergence(self, lines: List[str], data: Dict[str, Any]) -> None:
        """检查计算收敛性"""
        for line in lines:
            if 'reached required accuracy' in line:
                data['convergence'] = True
                break
        
        # 统计离子步数和电子步数
        ionic_steps = 0
        electronic_steps = []
        current_electronic = 0
        
        for line in lines:
            if 'ITERATION' in line and 'ENERGY' in line:
                current_electronic = 0
            elif 'DAV:' in line or 'RMM:' in line:
                current_electronic += 1
            elif 'POSITION' in line and 'TOTAL-FORCE' in line:
                ionic_steps += 1
                if current_electronic > 0:
                    electronic_steps.append(current_electronic)
                    current_electronic = 0
        
        data['ionic_steps'] = ionic_steps
        data['electronic_steps'] = electronic_steps
    
    @property
    def total_energy(self) -> Optional[float]:
        """获取最终总能量"""
        if not self._is_loaded:
            self.load_data()
        return self._data.get('total_energy')
    
    @property
    def fermi_energy(self) -> Optional[float]:
        """获取费米能级"""
        if not self._is_loaded:
            self.load_data()
        return self._data.get('fermi_energy')
    
    @property
    def is_converged(self) -> bool:
        """检查计算是否收敛"""
        if not self._is_loaded:
            self.load_data()
        return self._data.get('convergence', False)
    
    def get_energy_evolution(self) -> List[float]:
        """获取能量演化过程"""
        if not self._is_loaded:
            self.load_data()
        return self._data.get('energies', [])
    
    def get_final_forces(self) -> Optional[np.ndarray]:
        """获取最终受力"""
        if not self._is_loaded:
            self.load_data()
        forces = self._data.get('forces', [])
        return forces[-1] if forces else None
    
    def get_final_stress(self) -> Optional[List[float]]:
        """获取最终应力"""
        if not self._is_loaded:
            self.load_data()
        stress = self._data.get('stress', [])
        return stress[-1] if stress else None
    
    def analyze_convergence(self) -> Dict[str, Any]:
        """分析收敛性"""
        if not self._is_loaded:
            self.load_data()
        
        energies = self.get_energy_evolution()
        forces = self._data.get('forces', [])
        
        analysis = {
            'is_converged': self.is_converged,
            'ionic_steps': self._data.get('ionic_steps', 0),
            'electronic_steps': self._data.get('electronic_steps', []),
            'energy_change': None,
            'max_force': None,
            'rms_force': None,
        }
        
        # 能量变化分析
        if len(energies) >= 2:
            analysis['energy_change'] = abs(energies[-1] - energies[-2])
        
        # 受力分析
        if forces:
            final_forces = forces[-1]
            analysis['max_force'] = np.max(np.linalg.norm(final_forces, axis=1))
            analysis['rms_force'] = np.sqrt(np.mean(np.sum(final_forces**2, axis=1)))
        
        return analysis
