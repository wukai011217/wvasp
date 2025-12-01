"""
VASP参数配置管理器

提供参数验证、配置加载和模板管理功能
"""

from typing import Dict, Any, Optional, Union
import json
from pathlib import Path

from .constants import VASPParameters, CALCULATION_TEMPLATES, DFT_PLUS_U_DATABASE, DFT_PLUS_U_PRESETS
from .errors import ParameterError


class ParameterConfig:
    """参数配置类"""
    
    def __init__(self, template: Optional[str] = None, **kwargs):
        """
        初始化参数配置
        
        Args:
            template: 模板名称 ('optimization', 'scf', 'dos', 'band', 'neb', 'md')
            **kwargs: 额外的参数设置
        """
        self._parameters = {}
        
        # 加载模板
        if template:
            self.load_template(template)
        
        # 设置额外参数
        for key, value in kwargs.items():
            self.set_parameter(key, value)
    
    def load_template(self, template_name: str) -> None:
        """
        加载参数模板
        
        Args:
            template_name: 模板名称
        """
        if template_name not in CALCULATION_TEMPLATES:
            available = list(CALCULATION_TEMPLATES.keys())
            raise ParameterError(f"Unknown template '{template_name}'. Available: {available}")
        
        template_params = CALCULATION_TEMPLATES[template_name].copy()
        self._parameters.update(template_params)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """
        设置参数
        
        Args:
            name: 参数名
            value: 参数值
            
        Raises:
            ParameterError: 参数无效时
        """
        # 验证参数
        if not VASPParameters.validate_parameter(name, value):
            param_info = VASPParameters.get_parameter_info(name)
            if not param_info:
                raise ParameterError(f"Unknown parameter: {name}")
            else:
                raise ParameterError(f"Invalid value for {name}: {value}. Expected: {param_info}")
        
        self._parameters[name] = value
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        获取参数值
        
        Args:
            name: 参数名
            default: 默认值
            
        Returns:
            参数值
        """
        if name in self._parameters:
            return self._parameters[name]
        
        # 尝试获取系统默认值
        system_default = VASPParameters.get_default(name)
        if system_default is not None:
            return system_default
        
        return default
    
    def remove_parameter(self, name: str) -> None:
        """移除参数"""
        if name in self._parameters:
            del self._parameters[name]
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """
        批量更新参数
        
        Args:
            params: 参数字典
        """
        for name, value in params.items():
            self.set_parameter(name, value)
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """获取所有参数"""
        return self._parameters.copy()
    
    def validate_all(self) -> bool:
        """
        验证所有参数
        
        Returns:
            是否所有参数都有效
        """
        for name, value in self._parameters.items():
            if not VASPParameters.validate_parameter(name, value):
                return False
        return True
    
    def get_validation_errors(self) -> list:
        """
        获取验证错误列表
        
        Returns:
            错误信息列表
        """
        errors = []
        for name, value in self._parameters.items():
            if not VASPParameters.validate_parameter(name, value):
                param_info = VASPParameters.get_parameter_info(name)
                errors.append(f"Invalid {name}={value}: {param_info}")
        return errors
    
    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """
        保存配置到文件
        
        Args:
            filepath: 文件路径
        """
        filepath = Path(filepath)
        with open(filepath, 'w') as f:
            json.dump(self._parameters, f, indent=2, default=str)
    
    def load_from_file(self, filepath: Union[str, Path]) -> None:
        """
        从文件加载配置
        
        Args:
            filepath: 文件路径
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            params = json.load(f)
        
        self.update_parameters(params)
    
    def copy(self) -> 'ParameterConfig':
        """创建配置副本"""
        new_config = ParameterConfig()
        new_config._parameters = self._parameters.copy()
        return new_config
    
    def merge(self, other: 'ParameterConfig') -> 'ParameterConfig':
        """
        合并配置
        
        Args:
            other: 另一个配置对象
            
        Returns:
            合并后的新配置
        """
        merged = self.copy()
        merged.update_parameters(other.get_all_parameters())
        return merged
    
    def __str__(self) -> str:
        """字符串表示"""
        lines = []
        for name, value in sorted(self._parameters.items()):
            lines.append(f"{name} = {value}")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"ParameterConfig({len(self._parameters)} parameters)"
    
    def setup_dft_plus_u(self, elements: list, preset: str = 'auto', custom_u_values: Optional[Dict[str, float]] = None) -> None:
        """
        设置DFT+U参数
        
        Args:
            elements: 元素列表，按POSCAR中的顺序
            preset: 预设类型 ('auto', 'lanthanides_standard', 'actinides_standard', 'transition_metals')
            custom_u_values: 自定义U值字典，格式为 {'La': 5.5, 'O': 0.0}
        """
        # 检查是否有需要DFT+U的元素
        plus_u_elements = []
        for element in elements:
            if element in DFT_PLUS_U_DATABASE or (custom_u_values and element in custom_u_values):
                plus_u_elements.append(element)
        
        if not plus_u_elements:
            # 没有需要DFT+U的元素，确保DFT+U关闭
            self.set_parameter('LDAU', False)
            return
        
        # 启用DFT+U
        self.set_parameter('LDAU', True)
        
        # 根据预设或自动检测设置基本参数
        if preset == 'auto':
            preset = self._auto_detect_preset(plus_u_elements)
        
        if preset in DFT_PLUS_U_PRESETS:
            preset_params = DFT_PLUS_U_PRESETS[preset]
            for param, value in preset_params.items():
                if param != 'description':
                    self.set_parameter(param, value)
        
        # 设置LDAUL, LDAUU, LDAUJ参数
        ldaul_list = []
        ldauu_list = []
        ldauj_list = []
        
        for element in elements:
            if element in plus_u_elements:
                if custom_u_values and element in custom_u_values:
                    # 使用自定义U值
                    u_value = custom_u_values[element]
                    if element in DFT_PLUS_U_DATABASE:
                        l_value = DFT_PLUS_U_DATABASE[element]['L']
                        j_value = DFT_PLUS_U_DATABASE[element].get('J', 0.0)
                    else:
                        # 默认值
                        l_value = 2 if element in ['Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn'] else 3
                        j_value = 0.0
                elif element in DFT_PLUS_U_DATABASE:
                    # 使用数据库中的值
                    db_entry = DFT_PLUS_U_DATABASE[element]
                    l_value = db_entry['L']
                    u_value = db_entry['U']
                    j_value = db_entry['J']
                else:
                    # 不应该到这里，但为了安全
                    l_value = -1
                    u_value = 0.0
                    j_value = 0.0
            else:
                # 非DFT+U元素
                l_value = -1
                u_value = 0.0
                j_value = 0.0
            
            ldaul_list.append(l_value)
            ldauu_list.append(u_value)
            ldauj_list.append(j_value)
        
        # 设置参数
        self.set_parameter('LDAUL', ldaul_list)
        self.set_parameter('LDAUU', ldauu_list)
        self.set_parameter('LDAUJ', ldauj_list)
    
    def _auto_detect_preset(self, elements: list) -> str:
        """
        自动检测合适的DFT+U预设
        
        Args:
            elements: 需要DFT+U的元素列表
            
        Returns:
            预设名称
        """
        lanthanides = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        actinides = ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu']
        transition_metals = ['Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Mo', 'W']
        
        has_lanthanides = any(elem in lanthanides for elem in elements)
        has_actinides = any(elem in actinides for elem in elements)
        has_transition_metals = any(elem in transition_metals for elem in elements)
        
        if has_lanthanides:
            return 'lanthanides_standard'
        elif has_actinides:
            return 'actinides_standard'
        elif has_transition_metals:
            return 'transition_metals'
        else:
            return 'lanthanides_standard'  # 默认
    
    def get_dft_plus_u_info(self) -> Dict[str, Any]:
        """
        获取当前DFT+U设置信息
        
        Returns:
            DFT+U设置信息字典
        """
        info = {
            'enabled': self.get_parameter('LDAU', False),
            'type': self.get_parameter('LDAUTYPE', 2),
            'print_level': self.get_parameter('LDAUPRINT', 1),
            'lmaxmix': self.get_parameter('LMAXMIX', 4),
        }
        
        if info['enabled']:
            ldaul = self.get_parameter('LDAUL', [])
            ldauu = self.get_parameter('LDAUU', [])
            ldauj = self.get_parameter('LDAUJ', [])
            
            info['l_values'] = ldaul
            info['u_values'] = ldauu
            info['j_values'] = ldauj
            
            # 分析哪些元素使用了DFT+U
            plus_u_indices = []
            for i, (l, u) in enumerate(zip(ldaul, ldauu)):
                if l >= 0 and u > 0:
                    plus_u_indices.append(i)
            
            info['plus_u_indices'] = plus_u_indices
        
        return info


class ParameterManager:
    """参数管理器"""
    
    def __init__(self):
        """初始化参数管理器"""
        self._configs = {}
        self._current_config = None
    
    def create_config(self, name: str, template: Optional[str] = None, **kwargs) -> ParameterConfig:
        """
        创建新配置
        
        Args:
            name: 配置名称
            template: 模板名称
            **kwargs: 额外参数
            
        Returns:
            参数配置对象
        """
        config = ParameterConfig(template=template, **kwargs)
        self._configs[name] = config
        return config
    
    def get_config(self, name: str) -> Optional[ParameterConfig]:
        """获取配置"""
        return self._configs.get(name)
    
    def set_current_config(self, name: str) -> None:
        """设置当前配置"""
        if name not in self._configs:
            raise ParameterError(f"Configuration '{name}' not found")
        self._current_config = name
    
    def get_current_config(self) -> Optional[ParameterConfig]:
        """获取当前配置"""
        if self._current_config:
            return self._configs.get(self._current_config)
        return None
    
    def list_configs(self) -> list:
        """列出所有配置名称"""
        return list(self._configs.keys())
    
    def delete_config(self, name: str) -> None:
        """删除配置"""
        if name in self._configs:
            del self._configs[name]
            if self._current_config == name:
                self._current_config = None
    
    def save_all_configs(self, directory: Union[str, Path]) -> None:
        """
        保存所有配置到目录
        
        Args:
            directory: 目录路径
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        for name, config in self._configs.items():
            filepath = directory / f"{name}.json"
            config.save_to_file(filepath)
    
    def load_configs_from_directory(self, directory: Union[str, Path]) -> None:
        """
        从目录加载所有配置
        
        Args:
            directory: 目录路径
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        for json_file in directory.glob("*.json"):
            config_name = json_file.stem
            config = ParameterConfig()
            config.load_from_file(json_file)
            self._configs[config_name] = config
    
    def get_template_config(self, template_name: str) -> ParameterConfig:
        """
        获取模板配置（不保存到管理器中）
        
        Args:
            template_name: 模板名称
            
        Returns:
            参数配置对象
        """
        return ParameterConfig(template=template_name)
    
    def validate_config(self, name: str) -> tuple:
        """
        验证配置
        
        Args:
            name: 配置名称
            
        Returns:
            (是否有效, 错误列表)
        """
        config = self.get_config(name)
        if not config:
            return False, [f"Configuration '{name}' not found"]
        
        errors = config.get_validation_errors()
        return len(errors) == 0, errors


# 全局参数管理器实例
parameter_manager = ParameterManager()


def create_optimization_config(**kwargs) -> ParameterConfig:
    """创建结构优化配置的便捷函数"""
    return ParameterConfig(template='optimization', **kwargs)


def create_scf_config(**kwargs) -> ParameterConfig:
    """创建SCF计算配置的便捷函数"""
    return ParameterConfig(template='scf', **kwargs)


def create_dos_config(**kwargs) -> ParameterConfig:
    """创建DOS计算配置的便捷函数"""
    return ParameterConfig(template='dos', **kwargs)


def create_band_config(**kwargs) -> ParameterConfig:
    """创建能带计算配置的便捷函数"""
    return ParameterConfig(template='band', **kwargs)


def create_neb_config(**kwargs) -> ParameterConfig:
    """创建NEB计算配置的便捷函数"""
    return ParameterConfig(template='neb', **kwargs)


def create_md_config(**kwargs) -> ParameterConfig:
    """创建分子动力学配置的便捷函数"""
    return ParameterConfig(template='md', **kwargs)


def create_dft_plus_u_config(elements: list, template: str = 'scf', 
                             preset: str = 'auto', 
                             custom_u_values: Optional[Dict[str, float]] = None,
                             **kwargs) -> ParameterConfig:
    """
    创建DFT+U计算配置的便捷函数
    
    Args:
        elements: 元素列表，按POSCAR中的顺序
        template: 基础模板 ('scf', 'optimization', 'dos' 等)
        preset: DFT+U预设 ('auto', 'lanthanides_standard', 'actinides_standard', 'transition_metals')
        custom_u_values: 自定义U值字典
        **kwargs: 额外的参数设置
        
    Returns:
        配置好DFT+U的参数配置对象
        
    Example:
        # La2O3的DFT+U配置
        config = create_dft_plus_u_config(
            elements=['La', 'La', 'O', 'O', 'O'],
            template='scf',
            preset='lanthanides_standard'
        )
        
        # 自定义U值
        config = create_dft_plus_u_config(
            elements=['La', 'O'],
            custom_u_values={'La': 5.5, 'O': 0.0}
        )
    """
    config = ParameterConfig(template=template, **kwargs)
    config.setup_dft_plus_u(elements, preset, custom_u_values)
    return config


def get_dft_plus_u_recommendation(elements: list) -> Dict[str, Any]:
    """
    获取DFT+U参数推荐
    
    Args:
        elements: 元素列表
        
    Returns:
        推荐信息字典
    """
    recommendations = {
        'needs_dft_plus_u': False,
        'recommended_elements': [],
        'suggested_preset': None,
        'element_info': {},
        'warnings': []
    }
    
    # 检查哪些元素需要DFT+U
    for element in set(elements):  # 去重
        if element in DFT_PLUS_U_DATABASE:
            recommendations['needs_dft_plus_u'] = True
            recommendations['recommended_elements'].append(element)
            recommendations['element_info'][element] = DFT_PLUS_U_DATABASE[element]
    
    if recommendations['needs_dft_plus_u']:
        # 创建临时配置来获取推荐的预设
        temp_config = ParameterConfig()
        preset = temp_config._auto_detect_preset(recommendations['recommended_elements'])
        recommendations['suggested_preset'] = preset
        
        # 添加警告和建议
        lanthanides = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        actinides = ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu']
        
        has_lanthanides = any(elem in lanthanides for elem in recommendations['recommended_elements'])
        has_actinides = any(elem in actinides for elem in recommendations['recommended_elements'])
        
        if has_lanthanides:
            recommendations['warnings'].append(
                "检测到镧系元素，强烈建议使用DFT+U方法处理4f电子的强关联效应"
            )
        
        if has_actinides:
            recommendations['warnings'].append(
                "检测到锕系元素，建议使用DFT+U方法处理5f电子的强关联效应"
            )
        
        if 'Fe' in recommendations['recommended_elements']:
            recommendations['warnings'].append(
                "铁元素可能需要考虑磁性，建议设置ISPIN=2和适当的MAGMOM"
            )
    
    return recommendations


def print_dft_plus_u_info(elements: list) -> None:
    """
    打印DFT+U信息和推荐
    
    Args:
        elements: 元素列表
    """
    recommendations = get_dft_plus_u_recommendation(elements)
    
    print("🔬 DFT+U 参数分析")
    print("=" * 50)
    
    if not recommendations['needs_dft_plus_u']:
        print("✅ 当前体系不需要DFT+U修正")
        return
    
    print(f"⚠️  检测到需要DFT+U修正的元素: {recommendations['recommended_elements']}")
    print(f"📋 推荐预设: {recommendations['suggested_preset']}")
    print()
    
    print("📊 元素DFT+U参数:")
    for element, info in recommendations['element_info'].items():
        print(f"   {element}: L={info['L']}, U={info['U']} eV, J={info['J']} eV ({info['description']})")
    print()
    
    if recommendations['warnings']:
        print("⚠️  注意事项:")
        for warning in recommendations['warnings']:
            print(f"   • {warning}")
        print()
    
    print("💡 使用示例:")
    print(f"   config = create_dft_plus_u_config(")
    print(f"       elements={elements},")
    print(f"       preset='{recommendations['suggested_preset']}'")
    print(f"   )")
    print()


def get_available_dft_plus_u_elements() -> Dict[str, Dict[str, Any]]:
    """获取所有可用的DFT+U元素信息"""
    return DFT_PLUS_U_DATABASE.copy()


def get_dft_plus_u_presets() -> Dict[str, Dict[str, Any]]:
    """获取所有DFT+U预设信息"""
    return DFT_PLUS_U_PRESETS.copy()
