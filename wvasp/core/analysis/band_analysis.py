"""
能带分析模块

提供能带结构数据的分析功能。
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .energy_analysis import EnergyAnalyzer


class BandAnalyzer:
    """能带分析器"""
    
    def __init__(self, outcar_path: Path):
        """
        初始化能带分析器
        
        Args:
            outcar_path: OUTCAR文件路径
        """
        self.outcar_path = Path(outcar_path)
        self.energy_analyzer = EnergyAnalyzer(self.outcar_path)
        self.outcar_data = None
        self.fermi_energy = None
        self.eigenvalues = None
        self.kpoints = None
        
    def load_data(self) -> None:
        """加载能带数据"""
        self.outcar_data = self.energy_analyzer.load_data()
        self.fermi_energy = self.outcar_data.get('fermi_energy')
        # 注意：eigenvalues需要从能带计算的输出文件中解析，这里暂时设为None
        self.eigenvalues = None
        # 注意：kpoints需要从KPOINTS文件或OUTCAR中解析，这里暂时设为None
        self.kpoints = None
    
    def calculate_band_gap(self) -> Optional[float]:
        """
        计算带隙
        
        Returns:
            带隙值（eV），如果是金属则返回0
        """
        if not self.outcar_data:
            self.load_data()
            
        if self.eigenvalues is None or self.fermi_energy is None:
            return None
        
        try:
            # 处理不同的数据格式
            if isinstance(self.eigenvalues, list):
                # 如果是列表格式，转换为numpy数组
                all_eigenvalues = np.array(self.eigenvalues)
            else:
                all_eigenvalues = self.eigenvalues
            
            # 展平所有k点和能带的本征值
            if all_eigenvalues.ndim > 1:
                all_eigenvalues = all_eigenvalues.flatten()
            
            # 分离占据态和非占据态
            occupied = all_eigenvalues[all_eigenvalues <= self.fermi_energy]
            unoccupied = all_eigenvalues[all_eigenvalues > self.fermi_energy]
            
            if len(occupied) > 0 and len(unoccupied) > 0:
                vbm = np.max(occupied)  # 价带顶
                cbm = np.min(unoccupied)  # 导带底
                band_gap = cbm - vbm
                
                # 如果带隙很小，认为是金属
                if band_gap < 0.01:
                    return 0.0
                else:
                    return band_gap
            
        except Exception:
            pass
        
        return None
    
    def get_band_extrema(self) -> Dict[str, Any]:
        """
        获取能带极值信息
        
        Returns:
            包含VBM、CBM等信息的字典
        """
        if not self.outcar_data:
            self.load_data()
            
        extrema = {}
        
        if self.eigenvalues is not None and self.fermi_energy is not None:
            try:
                if isinstance(self.eigenvalues, list):
                    all_eigenvalues = np.array(self.eigenvalues)
                else:
                    all_eigenvalues = self.eigenvalues
                
                if all_eigenvalues.ndim > 1:
                    all_eigenvalues = all_eigenvalues.flatten()
                
                occupied = all_eigenvalues[all_eigenvalues <= self.fermi_energy]
                unoccupied = all_eigenvalues[all_eigenvalues > self.fermi_energy]
                
                if len(occupied) > 0:
                    extrema['vbm'] = np.max(occupied)
                    extrema['vbm_relative'] = extrema['vbm'] - self.fermi_energy
                
                if len(unoccupied) > 0:
                    extrema['cbm'] = np.min(unoccupied)
                    extrema['cbm_relative'] = extrema['cbm'] - self.fermi_energy
                
                extrema['fermi_energy'] = self.fermi_energy
                
            except Exception:
                pass
        
        return extrema
    
    def analyze_electronic_structure(self) -> Dict[str, Any]:
        """
        综合分析电子结构
        
        Returns:
            电子结构分析结果
        """
        if not self.outcar_data:
            self.load_data()
        
        analysis = {
            'band_gap': self.calculate_band_gap(),
            'band_extrema': self.get_band_extrema(),
            'fermi_energy': self.fermi_energy,
        }
        
        # 判断材料类型
        band_gap = analysis['band_gap']
        if band_gap is not None:
            if band_gap == 0.0:
                analysis['material_type'] = 'metal'
            elif band_gap < 0.5:
                analysis['material_type'] = 'semimetal'
            elif band_gap < 3.0:
                analysis['material_type'] = 'semiconductor'
            else:
                analysis['material_type'] = 'insulator'
        else:
            analysis['material_type'] = 'unknown'
        
        return analysis