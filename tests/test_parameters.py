"""
测试core.parameters模块

测试参数管理、磁矩管理和验证功能。
"""

import pytest
from pathlib import Path
import sys
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.core.parameters import (
    ParameterConfig, MagneticMomentManager, VASPParameterValidator,
    KPointsConfig, PotcarConfig, SlurmConfig
)
from wvasp.core.base import Structure, Lattice, Atom


class TestParameterConfig:
    """测试ParameterConfig类"""
    
    def test_init_with_template(self):
        """测试使用模板初始化"""
        config = ParameterConfig("optimization")
        
        assert config.template == "optimization"
        assert "SYSTEM" in config.parameters
        assert config.parameters["SYSTEM"] == "Structure optimization"

    def test_init_without_template(self):
        """测试不使用模板初始化"""
        config = ParameterConfig()
        
        assert config.template is None
        assert len(config.parameters) == 0

    def test_load_template(self):
        """测试加载模板"""
        config = ParameterConfig()
        config.load_template("scf")
        
        assert config.template == "scf"
        assert config.parameters["SYSTEM"] == "SCF calculation"

    def test_set_get_parameter(self):
        """测试设置和获取参数"""
        config = ParameterConfig()
        
        config.set_parameter("ENCUT", 500.0)
        config.set_parameter("ALGO", "Normal")
        
        assert config.get_parameter("ENCUT") == 500.0
        assert config.get_parameter("ALGO") == "Normal"
        assert config.get_parameter("NONEXISTENT") is None

    def test_get_all_parameters(self):
        """测试获取所有参数"""
        config = ParameterConfig("optimization")
        config.set_parameter("ENCUT", 500.0)
        
        all_params = config.get_all_parameters()
        
        assert isinstance(all_params, dict)
        assert "SYSTEM" in all_params
        assert "ENCUT" in all_params
        assert all_params["ENCUT"] == 500.0

    def test_update_parameters_from_command_line(self):
        """测试从命令行更新参数"""
        config = ParameterConfig("optimization")
        
        # 模拟命令行参数
        cmd_params = [["ENCUT", "600"], ["ALGO", "Fast"], ["EDIFF", "1e-6"]]
        
        config.update_parameters_from_command_line(cmd_params)
        
        assert config.get_parameter("ENCUT") == "600"
        assert config.get_parameter("ALGO") == "Fast"
        assert config.get_parameter("EDIFF") == "1e-6"

    def test_load_from_incar_file(self, temp_dir):
        """测试从INCAR文件加载参数"""
        # 创建INCAR文件
        incar_content = """SYSTEM = Test System
ISTART = 0
ICHARG = 2
ENCUT = 450.0
ALGO = Normal
"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(incar_content)
        
        config = ParameterConfig()
        config.load_from_incar_file(incar_file)
        
        assert config.get_parameter("SYSTEM") == "Test System"
        assert config.get_parameter("ENCUT") == "450.0"
        assert config.get_parameter("ALGO") == "Normal"

    def test_setup_dft_plus_u(self):
        """测试设置DFT+U参数"""
        config = ParameterConfig()
        elements = ["Fe", "O", "Ce"]
        
        config.setup_dft_plus_u(elements)
        
        assert config.get_parameter("LDAU") == ".TRUE."
        assert config.get_parameter("LDAUTYPE") == "2"
        
        # 检查LDAUL参数
        ldaul = config.get_parameter("LDAUL")
        assert ldaul is not None

    def test_auto_setup_magnetism(self, sample_structure):
        """测试自动设置磁性"""
        config = ParameterConfig()
        config.auto_setup_magnetism(sample_structure)
        
        assert config.get_parameter("ISPIN") == "2"
        
        magmom = config.get_parameter("MAGMOM")
        assert magmom is not None

    def test_to_incar_format(self):
        """测试转换为INCAR格式"""
        config = ParameterConfig("optimization")
        config.set_parameter("ENCUT", 500.0)
        config.set_parameter("ALGO", "Normal")
        
        incar_dict = config.to_incar_format()
        
        assert isinstance(incar_dict, dict)
        assert "SYSTEM" in incar_dict
        assert "ENCUT" in incar_dict
        assert incar_dict["ENCUT"] == "500.0"

    def test_validate_all(self):
        """测试验证所有参数"""
        config = ParameterConfig("optimization")
        config.set_parameter("ENCUT", 500.0)
        
        errors = config.validate_all()
        
        # 应该返回错误列表
        assert isinstance(errors, list)


class TestMagneticMomentManager:
    """测试MagneticMomentManager类"""
    
    @pytest.fixture
    def magnetic_structure(self):
        """创建包含磁性元素的结构"""
        lattice = Lattice(np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ]))
        
        atoms = [
            Atom("Fe", np.array([0.0, 0.0, 0.0])),
            Atom("Fe", np.array([0.5, 0.5, 0.5])),
            Atom("Ni", np.array([0.25, 0.25, 0.25])),
            Atom("O", np.array([0.75, 0.75, 0.75]))
        ]
        
        structure = Structure(lattice, atoms, coordinate_type="fractional")
        structure.comment = "Fe2NiO"
        return structure

    def test_get_auto_magnetic_moments(self, magnetic_structure):
        """测试自动获取磁矩"""
        manager = MagneticMomentManager()
        
        magmom_config = manager.get_auto_magnetic_moments(magnetic_structure)
        
        assert "magmom_list" in magmom_config
        assert "magmom_string" in magmom_config
        assert len(magmom_config["magmom_list"]) == 4
        
        # Fe的磁矩应该是5.0
        assert magmom_config["magmom_list"][0] == 5.0
        assert magmom_config["magmom_list"][1] == 5.0
        
        # Ni的磁矩应该是2.0
        assert magmom_config["magmom_list"][2] == 2.0
        
        # O的磁矩应该是0.0
        assert magmom_config["magmom_list"][3] == 0.0

    def test_create_magnetic_config(self, magnetic_structure):
        """测试创建磁性配置"""
        manager = MagneticMomentManager()
        
        config = manager.create_magnetic_config(magnetic_structure)
        
        assert "ISPIN" in config
        assert config["ISPIN"] == "2"
        assert "MAGMOM" in config

    def test_get_magnetic_info(self):
        """测试获取磁性信息"""
        manager = MagneticMomentManager()
        
        info = manager.get_magnetic_info("Fe")
        
        assert "element" in info
        assert info["element"] == "Fe"
        assert "magnetic_moment" in info
        assert info["magnetic_moment"] == 5.0

    def test_suggest_magnetic_setup(self, magnetic_structure):
        """测试建议磁性设置"""
        manager = MagneticMomentManager()
        
        suggestions = manager.suggest_magnetic_setup(magnetic_structure)
        
        assert "has_magnetic_elements" in suggestions
        assert suggestions["has_magnetic_elements"] is True
        assert "recommended_ispin" in suggestions
        assert suggestions["recommended_ispin"] == 2

    def test_has_magnetic_elements(self, magnetic_structure):
        """测试检查磁性元素"""
        manager = MagneticMomentManager()
        
        # 测试有磁性元素的结构
        assert manager.has_magnetic_elements(magnetic_structure) is True
        
        # 测试无磁性元素的结构
        lattice = Lattice(np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ]))
        
        atoms = [
            Atom("C", np.array([0.0, 0.0, 0.0])),
            Atom("O", np.array([0.5, 0.5, 0.5]))
        ]
        
        non_magnetic_structure = Structure(lattice, atoms, coordinate_type="fractional")
        assert manager.has_magnetic_elements(non_magnetic_structure) is False


class TestVASPParameterValidator:
    """测试VASPParameterValidator类"""
    
    def test_validate_parameter_valid(self):
        """测试验证有效参数"""
        # 测试有效的ENCUT值
        assert VASPParameterValidator.validate_parameter("ENCUT", "500") is True
        assert VASPParameterValidator.validate_parameter("ENCUT", 500.0) is True
        
        # 测试有效的ALGO值
        assert VASPParameterValidator.validate_parameter("ALGO", "Normal") is True
        assert VASPParameterValidator.validate_parameter("ALGO", "Fast") is True

    def test_validate_parameter_invalid(self):
        """测试验证无效参数"""
        # 测试无效的ENCUT值
        assert VASPParameterValidator.validate_parameter("ENCUT", "-100") is False
        assert VASPParameterValidator.validate_parameter("ENCUT", "invalid") is False

    def test_validate_parameter_unknown(self):
        """测试验证未知参数"""
        # 未知参数应该返回True（允许用户自定义参数）
        assert VASPParameterValidator.validate_parameter("UNKNOWN_PARAM", "value") is True

    def test_get_default(self):
        """测试获取默认值"""
        default_encut = VASPParameterValidator.get_default("ENCUT")
        assert default_encut is not None

    def test_get_parameter_info(self):
        """测试获取参数信息"""
        info = VASPParameterValidator.get_parameter_info("ENCUT")
        
        assert isinstance(info, dict)


class TestKPointsConfig:
    """测试KPointsConfig类"""
    
    def test_init_with_template(self):
        """测试使用模板初始化"""
        config = KPointsConfig(template="gamma_medium")
        
        assert config.template == "gamma_medium"
        assert config.method == "gamma"
        assert config.grid == [6, 6, 6]

    def test_init_without_template(self):
        """测试不使用模板初始化"""
        config = KPointsConfig(method="monkhorst", grid=[8, 8, 8])
        
        assert config.method == "monkhorst"
        assert config.grid == [8, 8, 8]

    def test_generate_kpoints(self, temp_dir):
        """测试生成KPOINTS文件"""
        config = KPointsConfig(template="gamma_high")
        output_file = temp_dir / "KPOINTS"
        
        config.generate_kpoints(output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Gamma" in content


class TestPotcarConfig:
    """测试PotcarConfig类"""
    
    def test_init_with_template(self):
        """测试使用模板初始化"""
        config = PotcarConfig(template="PBE_standard")
        
        assert config.template == "PBE_standard"
        assert config.functional == "PBE"

    def test_init_with_elements(self):
        """测试使用元素初始化"""
        config = PotcarConfig(elements=["Fe", "O"], functional="LDA")
        
        assert config.elements == ["Fe", "O"]
        assert config.functional == "LDA"

    def test_update_from_poscar(self, temp_dir, sample_poscar_content):
        """测试从POSCAR更新元素"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        config = PotcarConfig()
        config.update_from_poscar(poscar_file)
        
        assert config.elements == ["Fe", "O"]

    def test_update_from_command_line(self):
        """测试从命令行更新"""
        config = PotcarConfig()
        config.update_from_command_line(elements=["Ti", "O"], functional="PW91")
        
        assert config.elements == ["Ti", "O"]
        assert config.functional == "PW91"

    def test_generate_potcar_info(self, temp_dir):
        """测试生成POTCAR信息"""
        config = PotcarConfig(elements=["Fe", "O"], functional="PBE")
        output_file = temp_dir / "POTCAR"
        
        config.generate_potcar_info(output_file)
        
        assert output_file.exists()


class TestSlurmConfig:
    """测试SlurmConfig类"""
    
    def test_init_with_template(self):
        """测试使用模板初始化"""
        config = SlurmConfig(template="standard")
        
        assert config.template == "standard"
        assert config.nodes == 1
        assert config.ntasks_per_node == 24

    def test_init_with_custom_params(self):
        """测试使用自定义参数初始化"""
        config = SlurmConfig(
            job_name="test_job",
            nodes=2,
            ntasks_per_node=48,
            memory="64G",
            time="24:00:00"
        )
        
        assert config.job_name == "test_job"
        assert config.nodes == 2
        assert config.ntasks_per_node == 48
        assert config.memory == "64G"
        assert config.time == "24:00:00"

    def test_generate_slurm_script(self, temp_dir):
        """测试生成SLURM脚本"""
        config = SlurmConfig(template="gpu_accelerated")
        output_file = temp_dir / "submit.sh"
        
        config.generate_slurm_script(output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "#SBATCH" in content
        assert "vasp" in content.lower()


class TestParametersIntegration:
    """参数模块集成测试"""
    
    def test_full_parameter_workflow(self, sample_structure, temp_dir):
        """测试完整的参数配置工作流程"""
        # 1. 创建参数配置
        param_config = ParameterConfig("optimization")
        
        # 2. 设置自定义参数
        param_config.set_parameter("ENCUT", 500.0)
        param_config.set_parameter("ALGO", "Fast")
        
        # 3. 自动设置磁性
        param_config.auto_setup_magnetism(sample_structure)
        
        # 4. 设置DFT+U
        elements = [atom.element for atom in sample_structure.atoms]
        unique_elements = list(dict.fromkeys(elements))  # 保持顺序去重
        param_config.setup_dft_plus_u(unique_elements)
        
        # 5. 验证参数
        errors = param_config.validate_all()
        
        # 6. 生成INCAR格式
        incar_dict = param_config.to_incar_format()
        
        # 验证结果
        assert "SYSTEM" in incar_dict
        assert "ENCUT" in incar_dict
        assert incar_dict["ENCUT"] == "500.0"
        assert "ISPIN" in incar_dict
        assert incar_dict["ISPIN"] == "2"

    def test_magnetic_workflow(self, sample_structure):
        """测试磁性配置工作流程"""
        # 1. 创建磁矩管理器
        mag_manager = MagneticMomentManager()
        
        # 2. 检查是否有磁性元素
        has_magnetic = mag_manager.has_magnetic_elements(sample_structure)
        assert has_magnetic is True
        
        # 3. 获取磁性建议
        suggestions = mag_manager.suggest_magnetic_setup(sample_structure)
        assert suggestions["has_magnetic_elements"] is True
        
        # 4. 创建磁性配置
        mag_config = mag_manager.create_magnetic_config(sample_structure)
        assert "ISPIN" in mag_config
        assert "MAGMOM" in mag_config
        
        # 5. 获取自动磁矩
        magmom_config = mag_manager.get_auto_magnetic_moments(sample_structure)
        assert len(magmom_config["magmom_list"]) == 4

    def test_template_system_integration(self, temp_dir):
        """测试模板系统集成"""
        # 测试所有配置类的模板功能
        
        # INCAR模板
        incar_config = ParameterConfig("optimization")
        assert incar_config.template == "optimization"
        
        # KPOINTS模板
        kpoints_config = KPointsConfig(template="slab_2d")
        assert kpoints_config.template == "slab_2d"
        
        # POTCAR模板
        potcar_config = PotcarConfig(template="PBE_hard")
        assert potcar_config.template == "PBE_hard"
        
        # SLURM模板
        slurm_config = SlurmConfig(template="gpu_accelerated")
        assert slurm_config.template == "gpu_accelerated"
        
        # 生成文件测试
        kpoints_file = temp_dir / "KPOINTS"
        kpoints_config.generate_kpoints(kpoints_file)
        assert kpoints_file.exists()
        
        slurm_file = temp_dir / "submit.sh"
        slurm_config.generate_slurm_script(slurm_file)
        assert slurm_file.exists()
