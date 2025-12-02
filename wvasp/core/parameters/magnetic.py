"""
磁矩管理模块

提供智能的初始磁矩设置功能，支持自动判断和手动覆盖。
"""

from typing import List, Dict, Optional, Union, Any

# 从constants导入磁矩数据
from ...utils.constants import DEFAULT_MAGNETIC_MOMENTS, MAGNETIC_ELEMENTS


class MagneticMomentManager:
    """磁矩管理器"""
    
    def __init__(self):
        self.default_moments = DEFAULT_MAGNETIC_MOMENTS.copy()
        
    def get_auto_magnetic_moments(self, structure, 
                                 oxidation_states: Optional[Dict[str, int]] = None) -> List[float]:
        """
        根据结构自动生成磁矩
        
        Args:
            structure: 结构对象
            oxidation_states: 氧化态字典 (可选)
            
        Returns:
            磁矩列表
        """
        moments = []
        
        for atom in structure.atoms:
            element = atom.element
            
            # 基础磁矩
            base_moment = self.default_moments.get(element, 0.0)
            
            # 根据氧化态调整 (如果提供)
            if oxidation_states and element in oxidation_states:
                adjusted_moment = self._adjust_for_oxidation_state(
                    element, base_moment, oxidation_states[element]
                )
                moments.append(adjusted_moment)
            else:
                moments.append(base_moment)
                
        return moments
    
    def _adjust_for_oxidation_state(self, element: str, base_moment: float, 
                                   oxidation_state: int) -> float:
        """根据氧化态调整磁矩"""
        # 简化的氧化态调整规则
        adjustments = {
            'Fe': {2: 4.0, 3: 5.0},  # Fe2+: 4μB, Fe3+: 5μB
            'Co': {2: 3.0, 3: 4.0},  # Co2+: 3μB, Co3+: 4μB  
            'Ni': {2: 2.0, 3: 1.0},  # Ni2+: 2μB, Ni3+: 1μB
            'Mn': {2: 5.0, 3: 4.0, 4: 3.0},  # 不同氧化态
        }
        
        if element in adjustments and oxidation_state in adjustments[element]:
            return adjustments[element][oxidation_state]
        
        return base_moment
    
    def create_magnetic_config(self, structure,
                              custom_moments: Optional[Dict[str, float]] = None,
                              magnetic_coupling: str = 'ferromagnetic') -> Dict[str, Union[List[float], bool]]:
        """
        创建完整的磁性配置
        
        Args:
            structure: 结构对象
            custom_moments: 自定义磁矩字典
            magnetic_coupling: 磁性耦合类型
            
        Returns:
            磁性配置字典
        """
        # 获取基础磁矩
        moments = self.get_auto_magnetic_moments(structure)
        
        # 应用自定义磁矩
        if custom_moments:
            for i, atom in enumerate(structure.atoms):
                element = atom.element
                if element in custom_moments:
                    moments[i] = custom_moments[element]
        
        # 应用磁性耦合
        elements = [atom.element for atom in structure.atoms]
        if magnetic_coupling == 'antiferromagnetic':
            moments = self._apply_antiferromagnetic_coupling(moments, elements)
        elif magnetic_coupling == 'ferrimagnetic':
            moments = self._apply_ferrimagnetic_coupling(moments, elements)
        
        # 检查是否需要自旋极化
        needs_spin_polarization = any(abs(m) > 0.1 for m in moments)
        
        return {
            'MAGMOM': moments,
            'ISPIN': 2 if needs_spin_polarization else 1,
            'needs_spin_polarization': needs_spin_polarization
        }
    
    def _apply_antiferromagnetic_coupling(self, moments: List[float], 
                                        elements: List[str]) -> List[float]:
        """应用反铁磁耦合"""
        coupled_moments = moments.copy()
        
        # 简单的反铁磁耦合：交替改变符号
        for i in range(1, len(coupled_moments), 2):
            if abs(coupled_moments[i]) > 0.1:  # 只对磁性原子应用
                coupled_moments[i] = -coupled_moments[i]
        
        return coupled_moments
    
    def _apply_ferrimagnetic_coupling(self, moments: List[float], 
                                     elements: List[str]) -> List[float]:
        """应用亚铁磁耦合"""
        coupled_moments = moments.copy()
        
        # 简单的亚铁磁耦合：不同元素不同方向
        element_signs = {}
        sign = 1
        
        for i, element in enumerate(elements):
            if element not in element_signs:
                element_signs[element] = sign
                sign *= -1  # 下一个新元素使用相反符号
            
            if abs(coupled_moments[i]) > 0.1:
                coupled_moments[i] *= element_signs[element]
        
        return coupled_moments
    
    def has_magnetic_elements(self, elements: List[str]) -> bool:
        """检查是否包含磁性元素"""
        magnetic_set = set()
        for category in MAGNETIC_ELEMENTS.values():
            magnetic_set.update(category)
        
        return any(element in magnetic_set for element in elements)
    
    def get_magnetic_info(self, element: str) -> Dict[str, Union[float, str, List[str]]]:
        """获取元素磁性信息"""
        info = {
            'element': element,
            'default_moment': self.default_moments.get(element, 0.0),
            'is_magnetic': element in self.default_moments and self.default_moments[element] != 0.0,
            'categories': []
        }
        
        # 查找元素所属的磁性类别
        for category, element_list in MAGNETIC_ELEMENTS.items():
            if element in element_list:
                info['categories'].append(category)
        
        return info
    
    def suggest_magnetic_setup(self, structure) -> Dict[str, Any]:
        """建议磁性设置"""
        elements = [atom.element for atom in structure.atoms]
        unique_elements = list(set(elements))
        
        suggestions = {
            'has_magnetic_elements': self.has_magnetic_elements(unique_elements),
            'magnetic_elements': [],
            'recommended_ispin': 1,
            'recommended_magmom': None,
            'notes': []
        }
        
        # 分析磁性元素
        for element in unique_elements:
            if element in self.default_moments and self.default_moments[element] != 0.0:
                suggestions['magnetic_elements'].append({
                    'element': element,
                    'default_moment': self.default_moments[element],
                    'count': elements.count(element)
                })
        
        # 给出建议
        if suggestions['magnetic_elements']:
            suggestions['recommended_ispin'] = 2
            suggestions['recommended_magmom'] = self.get_auto_magnetic_moments(structure)
            suggestions['notes'].append("检测到磁性元素，建议启用自旋极化计算")
            
            # 特殊建议
            if any(elem['element'] in ['Mn', 'Cr'] for elem in suggestions['magnetic_elements']):
                suggestions['notes'].append("包含Mn或Cr，可能需要考虑反铁磁耦合")
            
            if any(elem['element'] in MAGNETIC_ELEMENTS['lanthanides'] for elem in suggestions['magnetic_elements']):
                suggestions['notes'].append("包含镧系元素，可能需要DFT+U修正")
        
        return suggestions
