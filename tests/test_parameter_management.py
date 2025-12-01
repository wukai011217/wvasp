"""
测试参数管理系统
"""

import pytest
import json
from pathlib import Path

from wvasp.utils.parameter_manager import (
    ParameterConfig, ParameterManager,
    create_optimization_config, create_scf_config, create_dos_config,
    create_band_config, create_neb_config, create_md_config
)
from wvasp.utils.constants import VASPParameters, CALCULATION_TEMPLATES
from wvasp.utils.errors import ParameterError


class TestVASPParameters:
    """测试VASP参数验证类"""
    
    def test_parameter_validation_valid(self):
        """测试有效参数验证"""
        # 测试基本类型
        assert VASPParameters.validate_parameter('ENCUT', 400.0)
        assert VASPParameters.validate_parameter('NSW', 100)
        assert VASPParameters.validate_parameter('LREAL', False)
        assert VASPParameters.validate_parameter('SYSTEM', 'Test calculation')
        
        # 测试值范围
        assert VASPParameters.validate_parameter('ISMEAR', 0)
        assert VASPParameters.validate_parameter('ISMEAR', -5)
        assert VASPParameters.validate_parameter('IBRION', 2)
        
        # 测试枚举值
        assert VASPParameters.validate_parameter('PREC', 'Accurate')
        assert VASPParameters.validate_parameter('ALGO', 'Normal')
    
    def test_parameter_validation_invalid(self):
        """测试无效参数验证"""
        # 测试类型错误
        assert not VASPParameters.validate_parameter('ENCUT', '400')  # 应该是float
        assert not VASPParameters.validate_parameter('NSW', 100.5)    # 应该是int
        
        # 测试值范围错误
        assert not VASPParameters.validate_parameter('ENCUT', 50.0)   # 太小
        assert not VASPParameters.validate_parameter('ENCUT', 3000.0) # 太大
        assert not VASPParameters.validate_parameter('ISMEAR', 10)    # 超出范围
        
        # 测试枚举值错误
        assert not VASPParameters.validate_parameter('PREC', 'Invalid')
        assert not VASPParameters.validate_parameter('IBRION', 99)
    
    def test_get_default_values(self):
        """测试获取默认值"""
        assert VASPParameters.get_default('ENCUT') == 400.0
        assert VASPParameters.get_default('NSW') == 0
        assert VASPParameters.get_default('PREC') == 'Accurate'
        assert VASPParameters.get_default('NONEXISTENT') is None
    
    def test_get_parameter_info(self):
        """测试获取参数信息"""
        encut_info = VASPParameters.get_parameter_info('ENCUT')
        assert encut_info['type'] == float
        assert encut_info['min'] == 100.0
        assert encut_info['max'] == 2000.0
        assert encut_info['default'] == 400.0
        
        ismear_info = VASPParameters.get_parameter_info('ISMEAR')
        assert ismear_info['type'] == int
        assert ismear_info['min'] == -5
        assert ismear_info['max'] == 2


class TestParameterConfig:
    """测试参数配置类"""
    
    def test_basic_parameter_operations(self):
        """测试基本参数操作"""
        config = ParameterConfig()
        
        # 设置参数
        config.set_parameter('SYSTEM', 'Test calculation')
        config.set_parameter('ENCUT', 500.0)
        config.set_parameter('NSW', 100)
        
        # 获取参数
        assert config.get_parameter('SYSTEM') == 'Test calculation'
        assert config.get_parameter('ENCUT') == 500.0
        assert config.get_parameter('NSW') == 100
        assert config.get_parameter('NONEXISTENT') is None
        assert config.get_parameter('NONEXISTENT', 'default') == 'default'
    
    def test_parameter_validation_in_config(self):
        """测试配置中的参数验证"""
        config = ParameterConfig()
        
        # 有效参数应该成功
        config.set_parameter('ENCUT', 400.0)
        
        # 无效参数应该抛出异常
        with pytest.raises(ParameterError):
            config.set_parameter('ENCUT', 50.0)  # 太小
        
        with pytest.raises(ParameterError):
            config.set_parameter('ISMEAR', 10)   # 无效值
        
        with pytest.raises(ParameterError):
            config.set_parameter('UNKNOWN_PARAM', 'value')  # 未知参数
    
    def test_template_loading(self):
        """测试模板加载"""
        # 测试优化模板
        opt_config = ParameterConfig(template='optimization')
        assert opt_config.get_parameter('SYSTEM') == 'Structure optimization'
        assert opt_config.get_parameter('IBRION') == 2
        assert opt_config.get_parameter('NSW') == 500
        
        # 测试SCF模板
        scf_config = ParameterConfig(template='scf')
        assert scf_config.get_parameter('SYSTEM') == 'SCF calculation'
        assert scf_config.get_parameter('NSW') == 0
        
        # 测试无效模板
        with pytest.raises(ParameterError):
            ParameterConfig(template='invalid_template')
    
    def test_parameter_updates(self):
        """测试批量参数更新"""
        config = ParameterConfig(template='scf')
        
        updates = {
            'ENCUT': 600.0,
            'EDIFF': 1e-7,
            'ISMEAR': -5
        }
        
        config.update_parameters(updates)
        
        assert config.get_parameter('ENCUT') == 600.0
        assert config.get_parameter('EDIFF') == 1e-7
        assert config.get_parameter('ISMEAR') == -5
    
    def test_validation_methods(self):
        """测试验证方法"""
        config = ParameterConfig(template='optimization')
        
        # 有效配置
        assert config.validate_all()
        assert len(config.get_validation_errors()) == 0
        
        # 添加无效参数（绕过set_parameter的验证）
        config._parameters['INVALID_PARAM'] = 'invalid'
        
        assert not config.validate_all()
        errors = config.get_validation_errors()
        assert len(errors) > 0
    
    def test_config_copy_and_merge(self):
        """测试配置复制和合并"""
        config1 = ParameterConfig(template='scf')
        config2 = ParameterConfig()
        config2.set_parameter('ENCUT', 800.0)
        config2.set_parameter('ISMEAR', -5)
        
        # 测试复制
        config1_copy = config1.copy()
        assert config1_copy.get_parameter('SYSTEM') == config1.get_parameter('SYSTEM')
        
        # 修改复制的配置不应影响原配置
        config1_copy.set_parameter('ENCUT', 1000.0)
        assert config1.get_parameter('ENCUT') != 1000.0
        
        # 测试合并
        merged = config1.merge(config2)
        assert merged.get_parameter('SYSTEM') == 'SCF calculation'  # 来自config1
        assert merged.get_parameter('ENCUT') == 800.0  # 来自config2，覆盖config1
        assert merged.get_parameter('ISMEAR') == -5     # 来自config2
    
    def test_file_operations(self, temp_dir):
        """测试文件保存和加载"""
        config = ParameterConfig(template='optimization')
        config.set_parameter('ENCUT', 600.0)
        config.set_parameter('SYSTEM', 'File test')
        
        # 保存到文件
        config_file = temp_dir / "test_config.json"
        config.save_to_file(config_file)
        
        assert config_file.exists()
        
        # 从文件加载
        loaded_config = ParameterConfig()
        loaded_config.load_from_file(config_file)
        
        assert loaded_config.get_parameter('ENCUT') == 600.0
        assert loaded_config.get_parameter('SYSTEM') == 'File test'
        assert loaded_config.get_parameter('IBRION') == 2  # 来自模板


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_create_optimization_config(self):
        """测试创建优化配置"""
        config = create_optimization_config(ENCUT=600.0, NSW=1000)
        
        assert config.get_parameter('SYSTEM') == 'Structure optimization'
        assert config.get_parameter('ENCUT') == 600.0
        assert config.get_parameter('NSW') == 1000
        assert config.get_parameter('IBRION') == 2
    
    def test_create_scf_config(self):
        """测试创建SCF配置"""
        config = create_scf_config(ENCUT=500.0, EDIFF=1e-7)
        
        assert config.get_parameter('SYSTEM') == 'SCF calculation'
        assert config.get_parameter('ENCUT') == 500.0
        assert config.get_parameter('EDIFF') == 1e-7
        assert config.get_parameter('NSW') == 0
    
    def test_create_dos_config(self):
        """测试创建DOS配置"""
        config = create_dos_config(NEDOS=5000, LORBIT=12)
        
        assert config.get_parameter('SYSTEM') == 'DOS calculation'
        assert config.get_parameter('NEDOS') == 5000
        assert config.get_parameter('LORBIT') == 12
        assert config.get_parameter('ISMEAR') == -5
    
    def test_create_neb_config(self):
        """测试创建NEB配置"""
        config = create_neb_config(IMAGES=7, SPRING=-10.0)
        
        assert config.get_parameter('SYSTEM') == 'NEB calculation'
        assert config.get_parameter('IMAGES') == 7
        assert config.get_parameter('SPRING') == -10.0
        assert config.get_parameter('ICHAIN') == 0
    
    def test_create_md_config(self):
        """测试创建MD配置"""
        config = create_md_config(TEBEG=500.0, TEEND=500.0)
        
        assert config.get_parameter('SYSTEM') == 'Molecular dynamics'
        assert config.get_parameter('TEBEG') == 500.0
        assert config.get_parameter('TEEND') == 500.0
        assert config.get_parameter('IBRION') == 0


class TestParameterManager:
    """测试参数管理器"""
    
    def test_config_management(self):
        """测试配置管理"""
        manager = ParameterManager()
        
        # 创建配置
        config1 = manager.create_config('opt1', 'optimization', ENCUT=500.0)
        config2 = manager.create_config('scf1', 'scf', EDIFF=1e-7)
        
        # 验证配置创建
        assert len(manager.list_configs()) == 2
        assert 'opt1' in manager.list_configs()
        assert 'scf1' in manager.list_configs()
        
        # 获取配置
        retrieved_config = manager.get_config('opt1')
        assert retrieved_config.get_parameter('ENCUT') == 500.0
        
        # 设置当前配置
        manager.set_current_config('opt1')
        current = manager.get_current_config()
        assert current.get_parameter('ENCUT') == 500.0
        
        # 删除配置
        manager.delete_config('scf1')
        assert len(manager.list_configs()) == 1
        assert 'scf1' not in manager.list_configs()
    
    def test_config_validation_in_manager(self):
        """测试管理器中的配置验证"""
        manager = ParameterManager()
        
        # 创建有效配置
        manager.create_config('valid', 'optimization', ENCUT=500.0)
        is_valid, errors = manager.validate_config('valid')
        assert is_valid
        assert len(errors) == 0
        
        # 创建无效配置（通过直接修改绕过验证）
        config = manager.get_config('valid')
        config._parameters['ENCUT'] = 50.0  # 无效值
        
        is_valid, errors = manager.validate_config('valid')
        assert not is_valid
        assert len(errors) > 0
        
        # 验证不存在的配置
        is_valid, errors = manager.validate_config('nonexistent')
        assert not is_valid
        assert 'not found' in errors[0]
    
    def test_template_config_creation(self):
        """测试模板配置创建"""
        manager = ParameterManager()
        
        # 获取模板配置（不保存到管理器）
        template_config = manager.get_template_config('dos')
        
        assert template_config.get_parameter('SYSTEM') == 'DOS calculation'
        assert template_config.get_parameter('ISMEAR') == -5
        
        # 验证没有保存到管理器
        assert len(manager.list_configs()) == 0
    
    def test_directory_operations(self, temp_dir):
        """测试目录操作"""
        manager = ParameterManager()
        
        # 创建多个配置
        manager.create_config('opt1', 'optimization', ENCUT=500.0)
        manager.create_config('scf1', 'scf', EDIFF=1e-7)
        manager.create_config('dos1', 'dos', NEDOS=5000)
        
        # 保存所有配置到目录
        config_dir = temp_dir / "configs"
        manager.save_all_configs(config_dir)
        
        # 验证文件创建
        assert (config_dir / "opt1.json").exists()
        assert (config_dir / "scf1.json").exists()
        assert (config_dir / "dos1.json").exists()
        
        # 创建新管理器并加载配置
        new_manager = ParameterManager()
        new_manager.load_configs_from_directory(config_dir)
        
        # 验证加载的配置
        assert len(new_manager.list_configs()) == 3
        opt_config = new_manager.get_config('opt1')
        assert opt_config.get_parameter('ENCUT') == 500.0


class TestCalculationTemplates:
    """测试计算模板"""
    
    def test_all_templates_exist(self):
        """测试所有模板都存在"""
        expected_templates = ['optimization', 'scf', 'dos', 'band', 'neb', 'md']
        
        for template_name in expected_templates:
            assert template_name in CALCULATION_TEMPLATES
            template = CALCULATION_TEMPLATES[template_name]
            assert isinstance(template, dict)
            assert 'SYSTEM' in template
    
    def test_template_parameter_validity(self):
        """测试模板参数的有效性"""
        for template_name, template_params in CALCULATION_TEMPLATES.items():
            for param_name, param_value in template_params.items():
                is_valid = VASPParameters.validate_parameter(param_name, param_value)
                assert is_valid, f"Invalid parameter in {template_name}: {param_name}={param_value}"
    
    def test_template_specific_requirements(self):
        """测试模板特定要求"""
        # 优化模板应该有NSW > 0
        opt_template = CALCULATION_TEMPLATES['optimization']
        assert opt_template['NSW'] > 0
        assert opt_template['IBRION'] in [1, 2, 3]
        
        # SCF模板应该有NSW = 0
        scf_template = CALCULATION_TEMPLATES['scf']
        assert scf_template['NSW'] == 0
        
        # DOS模板应该有LORBIT和NEDOS
        dos_template = CALCULATION_TEMPLATES['dos']
        assert 'LORBIT' in dos_template
        assert 'NEDOS' in dos_template
        assert dos_template['ISMEAR'] == -5
        
        # NEB模板应该有NEB相关参数
        neb_template = CALCULATION_TEMPLATES['neb']
        assert 'IMAGES' in neb_template
        assert 'SPRING' in neb_template
        assert 'ICHAIN' in neb_template
        
        # MD模板应该有MD相关参数
        md_template = CALCULATION_TEMPLATES['md']
        assert 'MDALGO' in md_template
        assert 'TEBEG' in md_template
        assert 'TEEND' in md_template
