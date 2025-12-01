"""
分子动力学分析模块

提供MD轨迹的分析功能。
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .energy_analysis import EnergyAnalyzer


class MDAnalyzer:
    """分子动力学分析器"""
    
    def __init__(self, outcar_path: Path):
        """
        初始化MD分析器
        
        Args:
            outcar_path: OUTCAR文件路径
        """
        self.outcar_path = Path(outcar_path)
        self.energy_analyzer = EnergyAnalyzer(self.outcar_path)
        self.outcar_data = None
        
    def load_data(self) -> None:
        """加载MD数据"""
        self.outcar_data = self.energy_analyzer.load_data()
    
    def calculate_energy_drift(self, energies: List[float]) -> Optional[float]:
        """
        计算能量漂移
        
        Args:
            energies: 能量序列
            
        Returns:
            能量漂移率 (eV/step)
        """
        if len(energies) < 10:
            return None
        
        try:
            # 使用线性拟合计算能量漂移
            steps = np.arange(len(energies))
            slope, _ = np.polyfit(steps, energies, 1)
            return slope  # eV/step
        except Exception:
            return None
    
    def analyze_temperature_evolution(self, ionic_steps: List[Dict]) -> Dict[str, Any]:
        """
        分析温度演化
        
        Args:
            ionic_steps: 离子步信息列表
            
        Returns:
            温度分析结果
        """
        if not ionic_steps:
            return {}
        
        temperatures = [step.get("temperature", 0) for step in ionic_steps if "temperature" in step]
        
        if not temperatures:
            return {}
        
        temperatures = np.array(temperatures)
        
        analysis = {
            "average_temperature": np.mean(temperatures),
            "temperature_std": np.std(temperatures),
            "temperature_range": (np.min(temperatures), np.max(temperatures)),
            "temperature_drift": self._calculate_temperature_drift(temperatures),
            "equilibration_steps": self._estimate_equilibration(temperatures),
        }
        
        return analysis
    
    def _calculate_temperature_drift(self, temperatures: np.ndarray) -> Optional[float]:
        """计算温度漂移"""
        if len(temperatures) < 10:
            return None
        
        try:
            steps = np.arange(len(temperatures))
            slope, _ = np.polyfit(steps, temperatures, 1)
            return slope  # K/step
        except Exception:
            return None
    
    def _estimate_equilibration(self, temperatures: np.ndarray) -> int:
        """估计平衡步数"""
        if len(temperatures) < 50:
            return len(temperatures) // 4
        
        # 简单的平衡判断：前25%步数的温度方差 vs 后25%
        quarter = len(temperatures) // 4
        early_std = np.std(temperatures[:quarter])
        late_std = np.std(temperatures[-quarter:])
        
        # 如果后期温度更稳定，认为已平衡
        if late_std < early_std * 0.8:
            return quarter
        else:
            return len(temperatures) // 2
    
    def analyze_pressure_evolution(self, ionic_steps: List[Dict]) -> Dict[str, Any]:
        """
        分析压力演化
        
        Args:
            ionic_steps: 离子步信息列表
            
        Returns:
            压力分析结果
        """
        pressures = [step.get("pressure", 0) for step in ionic_steps if "pressure" in step]
        
        if not pressures:
            return {}
        
        pressures = np.array(pressures)
        
        return {
            "average_pressure": np.mean(pressures),
            "pressure_std": np.std(pressures),
            "pressure_range": (np.min(pressures), np.max(pressures)),
        }
    
    def analyze_trajectory(self) -> Dict[str, Any]:
        """
        综合分析MD轨迹
        
        Returns:
            完整的轨迹分析结果
        """
        if not self.outcar_data:
            self.load_data()
        
        analysis = {}
        
        # 基本信息
        energies = self.outcar_data.get("energies", [])
        ionic_steps = self.outcar.ionic_steps or []
        
        analysis.update({
            "md_steps_completed": len(energies),
            "energy_drift": self.calculate_energy_drift(energies),
            "final_energy": energies[-1] if energies else None,
        })
        
        # 温度分析
        temperature_analysis = self.analyze_temperature_evolution(ionic_steps)
        if temperature_analysis:
            analysis["temperature_analysis"] = temperature_analysis
        
        # 压力分析
        pressure_analysis = self.analyze_pressure_evolution(ionic_steps)
        if pressure_analysis:
            analysis["pressure_analysis"] = pressure_analysis
        
        # 系统稳定性评估
        analysis["system_stability"] = self._assess_stability(analysis)
        
        return analysis
    
    def _assess_stability(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估系统稳定性"""
        stability = {
            "energy_stable": False,
            "temperature_stable": False,
            "overall_stable": False
        }
        
        # 能量稳定性
        energy_drift = analysis.get("energy_drift")
        if energy_drift is not None and abs(energy_drift) < 1e-4:  # < 0.1 meV/step
            stability["energy_stable"] = True
        
        # 温度稳定性
        temp_analysis = analysis.get("temperature_analysis", {})
        temp_std = temp_analysis.get("temperature_std")
        if temp_std is not None and temp_std < 50:  # < 50K 标准差
            stability["temperature_stable"] = True
        
        # 整体稳定性
        stability["overall_stable"] = (
            stability["energy_stable"] and 
            stability["temperature_stable"]
        )
        
        return stability