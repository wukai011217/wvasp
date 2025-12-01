"""
测试DFT+U参数管理功能
"""

import pytest
from wvasp.utils.parameter_manager import (
    ParameterConfig, create_dft_plus_u_config,
    get_dft_plus_u_recommendation, get_available_dft_plus_u_elements,
    get_dft_plus_u_presets
)
from wvasp.utils.constants import DFT_PLUS_U_DATABASE, DFT_PLUS_U_PRESETS


class TestDFTPlusUDatabase:
    """测试DFT+U数据库"""
    
    def test_database_structure(self):
        """测试数据库结构"""
        for element, data in DFT_PLUS_U_DATABASE.items():
            assert isinstance(element, str)
            assert len(element) <= 2  # 元素符号最多2个字符
            
            assert 'L' in data
            assert 'U' in data
            assert 'J' in data
            assert 'description' in data
            
            assert isinstance(data['L'], int)
            assert isinstance(data['U'], (int, float))
            assert isinstance(data['J'], (int, float))
            assert isinstance(data['description'], str)
            
            # L值应该在合理范围内
            assert data['L'] in [-1, 0, 1, 2, 3]
            # U值应该为正数或零
            assert data['U'] >= 0.0
            # J值通常为零或正数
            assert data['J'] >= 0.0
    
    def test_lanthanides_coverage(self):
        """测试镧系元素覆盖"""
        lanthanides = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        
        for element in lanthanides:
            assert element in DFT_PLUS_U_DATABASE
            data = DFT_PLUS_U_DATABASE[element]
            assert data['L'] == 3  # 4f轨道
            assert data['U'] > 0.0  # 应该有正的U值
    
    def test_actinides_coverage(self):
        """测试锕系元素覆盖"""
        actinides = ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu']
        
        for element in actinides:
            assert element in DFT_PLUS_U_DATABASE
            data = DFT_PLUS_U_DATABASE[element]
            assert data['L'] == 3  # 5f轨道
            assert data['U'] > 0.0
    
    def test_transition_metals_coverage(self):
        """测试过渡金属覆盖"""
        transition_metals = ['Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu']
        
        for element in transition_metals:
            assert element in DFT_PLUS_U_DATABASE
            data = DFT_PLUS_U_DATABASE[element]
            assert data['L'] == 2  # 3d轨道
            assert data['U'] > 0.0


class TestDFTPlusUPresets:
    """测试DFT+U预设"""
    
    def test_preset_structure(self):
        """测试预设结构"""
        for preset_name, preset_data in DFT_PLUS_U_PRESETS.items():
            assert isinstance(preset_name, str)
            assert isinstance(preset_data, dict)
            
            # 必须包含的参数
            assert 'LDAU' in preset_data
            assert 'LDAUTYPE' in preset_data
            assert 'LDAUPRINT' in preset_data
            assert 'LMAXMIX' in preset_data
            assert 'description' in preset_data
            
            # 参数值检查
            assert preset_data['LDAU'] is True
            assert preset_data['LDAUTYPE'] in [1, 2, 4]
            assert preset_data['LDAUPRINT'] in [0, 1, 2]
            assert isinstance(preset_data['LMAXMIX'], int)
            assert preset_data['LMAXMIX'] >= 2
    
    def test_required_presets_exist(self):
        """测试必需的预设存在"""
        required_presets = ['lanthanides_standard', 'actinides_standard', 'transition_metals']
        
        for preset in required_presets:
            assert preset in DFT_PLUS_U_PRESETS


class TestParameterConfigDFTPlusU:
    """测试ParameterConfig的DFT+U功能"""
    
    def test_setup_dft_plus_u_basic(self):
        """测试基本DFT+U设置"""
        config = ParameterConfig()
        elements = ['La', 'O', 'O', 'O']
        
        config.setup_dft_plus_u(elements)
        
        # 检查DFT+U是否启用
        assert config.get_parameter('LDAU') is True
        assert config.get_parameter('LDAUTYPE') == 2
        
        # 检查LDAU参数
        ldaul = config.get_parameter('LDAUL')
        ldauu = config.get_parameter('LDAUU')
        ldauj = config.get_parameter('LDAUJ')
        
        assert len(ldaul) == len(elements)
        assert len(ldauu) == len(elements)
        assert len(ldauj) == len(elements)
        
        # La应该有DFT+U，O不应该有
        assert ldaul[0] == 3  # La的L值
        assert ldauu[0] == 5.3  # La的U值
        assert ldaul[1] == -1  # O的L值（不使用DFT+U）
        assert ldauu[1] == 0.0  # O的U值
    
    def test_setup_dft_plus_u_no_plus_u_elements(self):
        """测试不需要DFT+U的元素"""
        config = ParameterConfig()
        elements = ['Si', 'O', 'O']
        
        config.setup_dft_plus_u(elements)
        
        # DFT+U应该被关闭
        assert config.get_parameter('LDAU') is False
    
    def test_setup_dft_plus_u_custom_values(self):
        """测试自定义U值"""
        config = ParameterConfig()
        elements = ['La', 'Fe', 'O']
        custom_u = {'La': 5.5, 'Fe': 4.5, 'O': 0.0}
        
        config.setup_dft_plus_u(elements, custom_u_values=custom_u)
        
        ldauu = config.get_parameter('LDAUU')
        assert ldauu[0] == 5.5  # 自定义La的U值
        assert ldauu[1] == 4.5  # 自定义Fe的U值
        assert ldauu[2] == 0.0  # 自定义O的U值
    
    def test_setup_dft_plus_u_different_presets(self):
        """测试不同预设"""
        elements = ['Fe', 'O', 'O']
        
        # 过渡金属预设
        config1 = ParameterConfig()
        config1.setup_dft_plus_u(elements, preset='transition_metals')
        assert config1.get_parameter('LMAXMIX') == 4
        
        # 镧系预设
        config2 = ParameterConfig()
        config2.setup_dft_plus_u(elements, preset='lanthanides_standard')
        assert config2.get_parameter('LMAXMIX') == 6
    
    def test_auto_detect_preset(self):
        """测试自动预设检测"""
        config = ParameterConfig()
        
        # 测试镧系元素
        lanthanide_elements = ['La', 'O']
        preset = config._auto_detect_preset(['La'])
        assert preset == 'lanthanides_standard'
        
        # 测试锕系元素
        actinide_elements = ['U', 'O']
        preset = config._auto_detect_preset(['U'])
        assert preset == 'actinides_standard'
        
        # 测试过渡金属
        transition_elements = ['Fe', 'O']
        preset = config._auto_detect_preset(['Fe'])
        assert preset == 'transition_metals'
    
    def test_get_dft_plus_u_info(self):
        """测试获取DFT+U信息"""
        config = ParameterConfig()
        elements = ['La', 'Fe', 'O']
        
        config.setup_dft_plus_u(elements)
        
        info = config.get_dft_plus_u_info()
        
        assert info['enabled'] is True
        assert info['type'] == 2
        assert len(info['l_values']) == 3
        assert len(info['u_values']) == 3
        assert len(info['j_values']) == 3
        
        # 检查哪些位置使用了DFT+U
        plus_u_indices = info['plus_u_indices']
        assert 0 in plus_u_indices  # La
        assert 1 in plus_u_indices  # Fe
        assert 2 not in plus_u_indices  # O


class TestDFTPlusUConvenienceFunctions:
    """测试DFT+U便捷函数"""
    
    def test_create_dft_plus_u_config(self):
        """测试创建DFT+U配置"""
        elements = ['La', 'O', 'O', 'O']
        config = create_dft_plus_u_config(elements, template='scf')
        
        # 检查基础模板参数
        assert config.get_parameter('SYSTEM') == 'SCF calculation'
        assert config.get_parameter('NSW') == 0
        
        # 检查DFT+U参数
        assert config.get_parameter('LDAU') is True
        ldauu = config.get_parameter('LDAUU')
        assert ldauu[0] == 5.3  # La的U值
    
    def test_get_dft_plus_u_recommendation(self):
        """测试获取DFT+U推荐"""
        # 需要DFT+U的体系
        elements = ['La', 'O', 'O']
        recommendations = get_dft_plus_u_recommendation(elements)
        
        assert recommendations['needs_dft_plus_u'] is True
        assert 'La' in recommendations['recommended_elements']
        assert recommendations['suggested_preset'] == 'lanthanides_standard'
        assert 'La' in recommendations['element_info']
        assert len(recommendations['warnings']) > 0
        
        # 不需要DFT+U的体系
        elements = ['Si', 'O', 'O']
        recommendations = get_dft_plus_u_recommendation(elements)
        
        assert recommendations['needs_dft_plus_u'] is False
        assert len(recommendations['recommended_elements']) == 0
    
    def test_get_available_dft_plus_u_elements(self):
        """测试获取可用元素"""
        elements = get_available_dft_plus_u_elements()
        
        assert isinstance(elements, dict)
        assert len(elements) > 0
        assert 'La' in elements
        assert 'Fe' in elements
        
        # 检查返回的是副本
        original_count = len(DFT_PLUS_U_DATABASE)
        elements['TEST'] = {'L': 0, 'U': 0.0, 'J': 0.0, 'description': 'test'}
        assert len(DFT_PLUS_U_DATABASE) == original_count
    
    def test_get_dft_plus_u_presets(self):
        """测试获取预设"""
        presets = get_dft_plus_u_presets()
        
        assert isinstance(presets, dict)
        assert len(presets) > 0
        assert 'lanthanides_standard' in presets
        assert 'transition_metals' in presets
        
        # 检查返回的是副本
        original_count = len(DFT_PLUS_U_PRESETS)
        presets['test'] = {'LDAU': True, 'description': 'test'}
        assert len(DFT_PLUS_U_PRESETS) == original_count


class TestDFTPlusUIntegration:
    """测试DFT+U集成功能"""
    
    def test_complex_system_configuration(self):
        """测试复杂体系配置"""
        # LaFeO3钙钛矿
        elements = ['La', 'Fe', 'O', 'O', 'O']
        config = create_dft_plus_u_config(
            elements=elements,
            template='optimization',
            preset='lanthanides_standard',
            ISPIN=2,
            MAGMOM=[0.0, 4.0, 0.0, 0.0, 0.0]
        )
        
        # 检查所有参数
        assert config.get_parameter('LDAU') is True
        assert config.get_parameter('ISPIN') == 2
        assert config.get_parameter('MAGMOM') == [0.0, 4.0, 0.0, 0.0, 0.0]
        assert config.get_parameter('IBRION') == 2  # 来自optimization模板
        
        # 检查DFT+U参数
        ldauu = config.get_parameter('LDAUU')
        assert ldauu[0] == 5.3  # La
        assert ldauu[1] == 4.3  # Fe
        assert ldauu[2] == 0.0  # O
    
    def test_mixed_element_types(self):
        """测试混合元素类型"""
        # 包含镧系、过渡金属和普通元素
        elements = ['La', 'Mn', 'Ti', 'O', 'O']
        config = create_dft_plus_u_config(elements, preset='auto')
        
        ldaul = config.get_parameter('LDAUL')
        ldauu = config.get_parameter('LDAUU')
        
        assert ldaul[0] == 3   # La (4f)
        assert ldaul[1] == 2   # Mn (3d)
        assert ldaul[2] == 2   # Ti (3d)
        assert ldaul[3] == -1  # O (不使用)
        assert ldaul[4] == -1  # O (不使用)
        
        assert ldauu[0] > 0.0  # La
        assert ldauu[1] > 0.0  # Mn
        assert ldauu[2] > 0.0  # Ti
        assert ldauu[3] == 0.0 # O
        assert ldauu[4] == 0.0 # O
    
    def test_parameter_validation_with_dft_plus_u(self):
        """测试DFT+U参数验证"""
        config = ParameterConfig()
        elements = ['La', 'O']
        
        config.setup_dft_plus_u(elements)
        
        # 所有参数应该有效
        assert config.validate_all()
        
        # 获取验证错误（应该为空）
        errors = config.get_validation_errors()
        assert len(errors) == 0
    
    def test_dft_plus_u_with_different_templates(self):
        """测试DFT+U与不同模板的组合"""
        elements = ['Ce', 'O', 'O']
        
        # SCF + DFT+U
        scf_config = create_dft_plus_u_config(elements, template='scf')
        assert scf_config.get_parameter('NSW') == 0
        assert scf_config.get_parameter('LDAU') is True
        
        # DOS + DFT+U
        dos_config = create_dft_plus_u_config(elements, template='dos')
        assert dos_config.get_parameter('ISMEAR') == -5
        assert dos_config.get_parameter('LORBIT') == 11
        assert dos_config.get_parameter('LDAU') is True
        
        # Optimization + DFT+U
        opt_config = create_dft_plus_u_config(elements, template='optimization')
        assert opt_config.get_parameter('IBRION') == 2
        assert opt_config.get_parameter('NSW') == 500
        assert opt_config.get_parameter('LDAU') is True
