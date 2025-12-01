"""
NEB过渡态分析模块

提供NEB计算结果的分析功能。
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .energy_analysis import EnergyAnalyzer


class NEBAnalyzer:
    """NEB分析器"""
    
    def __init__(self, outcar_path: Path):
        """
        初始化NEB分析器
        
        Args:
            outcar_path: OUTCAR文件路径
        """
        self.outcar_path = Path(outcar_path)
        self.energy_analyzer = EnergyAnalyzer(self.outcar_path)
        self.outcar_data = None
        
    def load_data(self) -> None:
        """加载NEB数据"""
        self.outcar_data = self.energy_analyzer.load_data()
    
    def extract_neb_energies(self) -> List[float]:
        """
        从OUTCAR提取NEB能量
        
        Returns:
            NEB路径上各像的能量
        """
        energies = []
        
        try:
            with open(self.outcar_path, 'r') as f:
                lines = f.readlines()
            
            # 查找最后一次NEB能量输出
            neb_energy_lines = []
            for i, line in enumerate(lines):
                if "NEB: energies" in line or "image" in line.lower() and "energy" in line.lower():
                    neb_energy_lines.append((i, line))
            
            if neb_energy_lines:
                # 取最后一次的能量输出
                last_line_idx, last_line = neb_energy_lines[-1]
                
                # 尝试解析能量数据
                # 这里需要根据VASP的具体输出格式来实现
                # 简化版本：假设能量在行中以数字形式出现
                import re
                energy_pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
                found_energies = re.findall(energy_pattern, last_line)
                
                if found_energies:
                    energies = [float(e) for e in found_energies if abs(float(e)) > 1e-10]
                    
        except Exception:
            pass
        
        return energies
    
    def calculate_activation_energy(self, neb_energies: List[float]) -> Optional[float]:
        """
        计算活化能
        
        Args:
            neb_energies: NEB路径能量
            
        Returns:
            活化能 (eV)
        """
        if not neb_energies or len(neb_energies) < 3:
            return None
        
        initial_energy = neb_energies[0]
        max_energy = max(neb_energies)
        
        return max_energy - initial_energy
    
    def calculate_reaction_energy(self, neb_energies: List[float]) -> Optional[float]:
        """
        计算反应能
        
        Args:
            neb_energies: NEB路径能量
            
        Returns:
            反应能 (eV)
        """
        if not neb_energies or len(neb_energies) < 2:
            return None
        
        return neb_energies[-1] - neb_energies[0]
    
    def find_transition_state_index(self, neb_energies: List[float]) -> Optional[int]:
        """
        找到过渡态位置
        
        Args:
            neb_energies: NEB路径能量
            
        Returns:
            过渡态的像索引
        """
        if not neb_energies:
            return None
        
        return int(np.argmax(neb_energies))
    
    def calculate_reaction_coordinate(self, neb_energies: List[float]) -> List[float]:
        """
        计算反应坐标
        
        Args:
            neb_energies: NEB路径能量
            
        Returns:
            归一化的反应坐标
        """
        if not neb_energies:
            return []
        
        # 简单的线性反应坐标
        n_images = len(neb_energies)
        return [i / (n_images - 1) for i in range(n_images)]
    
    def analyze_neb_convergence(self) -> Dict[str, Any]:
        """
        分析NEB收敛性
        
        Returns:
            收敛性分析结果
        """
        if not self.outcar_data:
            self.load_data()
        
        convergence_info = {}
        
        # 检查基本收敛
        convergence_info["converged"] = self.outcar_data.get("convergence", False)
        
        # 分析离子步数
        ionic_steps = len(self.outcar_data.get("energies", []))
        convergence_info["ionic_steps"] = ionic_steps
        
        # 检查力收敛
        if hasattr(self.outcar, 'final_forces') and self.outcar.final_forces is not None:
            max_force = np.max(np.abs(self.outcar.final_forces))
            convergence_info["max_force"] = max_force
            convergence_info["force_converged"] = max_force < 0.05  # 0.05 eV/Å
        
        return convergence_info
    
    def analyze_transition_state(self) -> Dict[str, Any]:
        """
        综合分析过渡态搜索结果
        
        Returns:
            完整的过渡态分析结果
        """
        if not self.outcar_data:
            self.load_data()
        
        analysis = {}
        
        # 提取NEB能量
        neb_energies = self.extract_neb_energies()
        analysis["neb_energies"] = neb_energies
        
        if neb_energies:
            # 计算关键能量
            analysis["activation_energy"] = self.calculate_activation_energy(neb_energies)
            analysis["reaction_energy"] = self.calculate_reaction_energy(neb_energies)
            
            # 过渡态信息
            ts_index = self.find_transition_state_index(neb_energies)
            analysis["transition_state_index"] = ts_index
            
            if ts_index is not None:
                analysis["transition_state_energy"] = neb_energies[ts_index]
            
            # 反应坐标
            analysis["reaction_coordinate"] = self.calculate_reaction_coordinate(neb_energies)
            
            # 能垒分析
            analysis["forward_barrier"] = analysis["activation_energy"]
            if analysis["reaction_energy"] is not None and analysis["activation_energy"] is not None:
                analysis["reverse_barrier"] = analysis["activation_energy"] - analysis["reaction_energy"]
        
        # 收敛性分析
        convergence_analysis = self.analyze_neb_convergence()
        analysis.update(convergence_analysis)
        
        # 反应类型判断
        analysis["reaction_type"] = self._classify_reaction(analysis)
        
        return analysis
    
    def _classify_reaction(self, analysis: Dict[str, Any]) -> str:
        """分类反应类型"""
        reaction_energy = analysis.get("reaction_energy")
        activation_energy = analysis.get("activation_energy")
        
        if reaction_energy is None or activation_energy is None:
            return "unknown"
        
        if abs(reaction_energy) < 0.1:
            return "isomerization"
        elif reaction_energy < -0.1:
            return "exothermic"
        elif reaction_energy > 0.1:
            return "endothermic"
        else:
            return "thermoneutral"