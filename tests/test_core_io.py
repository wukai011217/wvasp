"""
测试core.io模块

测试VASP文件的读写功能。
"""

import pytest
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.core.io import POSCAR, INCAR, KPOINTS, POTCAR
from wvasp.core.base import Structure


class TestPOSCAR:
    """测试POSCAR类"""
    
    def test_poscar_init(self, temp_dir):
        """测试POSCAR初始化"""
        poscar_file = temp_dir / "POSCAR"
        poscar = POSCAR(poscar_file)
        
        assert poscar.file_path == poscar_file

    def test_poscar_read(self, temp_dir, sample_poscar_content):
        """测试POSCAR读取"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        poscar = POSCAR(poscar_file)
        structure = poscar.read()
        
        assert isinstance(structure, Structure)
        assert len(structure.atoms) == 5
        assert structure.atoms[0].element == "Fe"
        assert structure.atoms[2].element == "O"

    def test_poscar_write(self, temp_dir, sample_structure):
        """测试POSCAR写入"""
        poscar_file = temp_dir / "POSCAR_output"
        poscar = POSCAR(poscar_file)
        
        poscar.write(sample_structure)
        
        assert poscar_file.exists()
        
        # 验证写入的内容可以读取
        poscar_new = POSCAR(poscar_file)
        structure_new = poscar_new.read()
        
        assert len(structure_new.atoms) == len(sample_structure.atoms)

    def test_poscar_convert_coordinates(self, temp_dir, sample_poscar_content):
        """测试坐标转换"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        poscar = POSCAR(poscar_file)
        output_file = temp_dir / "POSCAR_cart"
        
        poscar.convert_coordinates("cart", output_file)
        
        assert output_file.exists()

    def test_poscar_get_elements(self, temp_dir, sample_poscar_content):
        """测试获取元素列表"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        poscar = POSCAR(poscar_file)
        elements = poscar.get_elements()
        
        assert elements == ["Fe", "O"]

    def test_poscar_get_composition(self, temp_dir, sample_poscar_content):
        """测试获取成分"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        poscar = POSCAR(poscar_file)
        composition = poscar.get_composition()
        
        assert composition == {"Fe": 2, "O": 3}


class TestINCAR:
    """测试INCAR类"""
    
    def test_incar_init(self, temp_dir):
        """测试INCAR初始化"""
        incar_file = temp_dir / "INCAR"
        incar = INCAR(incar_file)
        
        assert incar.file_path == incar_file

    def test_incar_read(self, temp_dir, sample_incar_content):
        """测试INCAR读取"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(sample_incar_content)
        
        incar = INCAR(incar_file)
        parameters = incar.read()
        
        assert parameters["SYSTEM"] == "Test Structure"
        assert parameters["ISTART"] == "0"
        assert parameters["ENCUT"] == "500.0"
        assert parameters["PREC"] == "Accurate"

    def test_incar_write(self, temp_dir):
        """测试INCAR写入"""
        incar_file = temp_dir / "INCAR"
        incar = INCAR(incar_file)
        
        parameters = {
            "SYSTEM": "Test System",
            "ISTART": "0",
            "ICHARG": "2",
            "ENCUT": "400.0"
        }
        
        incar.write(parameters)
        
        assert incar_file.exists()
        
        # 验证写入的内容
        incar_new = INCAR(incar_file)
        params_new = incar_new.read()
        
        assert params_new["SYSTEM"] == "Test System"
        assert params_new["ENCUT"] == "400.0"

    def test_incar_set_parameter(self, temp_dir, sample_incar_content):
        """测试设置参数"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(sample_incar_content)
        
        incar = INCAR(incar_file)
        
        incar.set_parameter("ENCUT", "600.0")
        incar.set_parameter("NEW_PARAM", "test_value")
        
        parameters = incar.read()
        assert parameters["ENCUT"] == "600.0"
        assert parameters["NEW_PARAM"] == "test_value"

    def test_incar_get_parameter(self, temp_dir, sample_incar_content):
        """测试获取参数"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(sample_incar_content)
        
        incar = INCAR(incar_file)
        
        assert incar.get_parameter("SYSTEM") == "Test Structure"
        assert incar.get_parameter("ENCUT") == "500.0"
        assert incar.get_parameter("NONEXISTENT") is None

    def test_incar_update_from_dict(self, temp_dir, sample_incar_content):
        """测试从字典更新参数"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(sample_incar_content)
        
        incar = INCAR(incar_file)
        
        updates = {
            "ENCUT": "550.0",
            "ALGO": "Fast",
            "NEW_PARAM": "new_value"
        }
        
        incar.update_from_dict(updates)
        parameters = incar.read()
        
        assert parameters["ENCUT"] == "550.0"
        assert parameters["ALGO"] == "Fast"
        assert parameters["NEW_PARAM"] == "new_value"


class TestKPOINTS:
    """测试KPOINTS类"""
    
    def test_kpoints_init(self, temp_dir):
        """测试KPOINTS初始化"""
        kpoints_file = temp_dir / "KPOINTS"
        kpoints = KPOINTS(kpoints_file)
        
        assert kpoints.file_path == kpoints_file

    def test_kpoints_read(self, temp_dir, sample_kpoints_content):
        """测试KPOINTS读取"""
        kpoints_file = temp_dir / "KPOINTS"
        kpoints_file.write_text(sample_kpoints_content)
        
        kpoints = KPOINTS(kpoints_file)
        data = kpoints.read()
        
        assert data["comment"] == "Automatic mesh"
        assert data["method"] == "Gamma"
        assert data["grid"] == [6, 6, 6]
        assert data["shift"] == [0.0, 0.0, 0.0]

    def test_kpoints_write_gamma(self, temp_dir):
        """测试写入Gamma中心K点"""
        kpoints_file = temp_dir / "KPOINTS"
        kpoints = KPOINTS(kpoints_file)
        
        kpoints.write_gamma_centered([8, 8, 8], [0.0, 0.0, 0.0])
        
        assert kpoints_file.exists()
        
        # 验证写入的内容
        kpoints_new = KPOINTS(kpoints_file)
        data = kpoints_new.read()
        
        assert data["method"] == "Gamma"
        assert data["grid"] == [8, 8, 8]

    def test_kpoints_write_monkhorst_pack(self, temp_dir):
        """测试写入Monkhorst-Pack K点"""
        kpoints_file = temp_dir / "KPOINTS"
        kpoints = KPOINTS(kpoints_file)
        
        kpoints.write_monkhorst_pack([4, 4, 4], [0.5, 0.5, 0.5])
        
        assert kpoints_file.exists()
        
        # 验证写入的内容
        kpoints_new = KPOINTS(kpoints_file)
        data = kpoints_new.read()
        
        assert data["method"] == "Monkhorst-Pack"
        assert data["grid"] == [4, 4, 4]

    def test_kpoints_write_line_mode(self, temp_dir):
        """测试写入线模式K点"""
        kpoints_file = temp_dir / "KPOINTS"
        kpoints = KPOINTS(kpoints_file)
        
        kpath = [
            {"label": "G", "coord": [0.0, 0.0, 0.0]},
            {"label": "X", "coord": [0.5, 0.0, 0.0]},
            {"label": "M", "coord": [0.5, 0.5, 0.0]},
            {"label": "G", "coord": [0.0, 0.0, 0.0]}
        ]
        
        kpoints.write_line_mode(kpath, 20)
        
        assert kpoints_file.exists()


class TestPOTCAR:
    """测试POTCAR类"""
    
    def test_potcar_init(self, temp_dir):
        """测试POTCAR初始化"""
        potcar_file = temp_dir / "POTCAR"
        potcar = POTCAR(potcar_file)
        
        assert potcar.file_path == potcar_file

    def test_potcar_get_elements_from_poscar(self, temp_dir, sample_poscar_content):
        """测试从POSCAR获取元素"""
        # 创建POSCAR文件
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        potcar_file = temp_dir / "POTCAR"
        potcar = POTCAR(potcar_file)
        
        elements = potcar.get_elements_from_poscar(poscar_file)
        assert elements == ["Fe", "O"]

    def test_potcar_generate_info(self, temp_dir):
        """测试生成POTCAR信息"""
        potcar_file = temp_dir / "POTCAR"
        potcar = POTCAR(potcar_file)
        
        elements = ["Fe", "O"]
        functional = "PBE"
        
        info = potcar.generate_potcar_info(elements, functional)
        
        assert "Fe" in info
        assert "O" in info
        assert "PBE" in info


class TestIOIntegration:
    """IO模块集成测试"""
    
    def test_full_io_workflow(self, temp_dir, sample_structure):
        """测试完整的IO工作流程"""
        # 写入POSCAR
        poscar_file = temp_dir / "POSCAR"
        poscar = POSCAR(poscar_file)
        poscar.write(sample_structure)
        
        # 读取POSCAR
        structure_read = poscar.read()
        assert len(structure_read.atoms) == 4
        
        # 创建INCAR
        incar_file = temp_dir / "INCAR"
        incar = INCAR(incar_file)
        incar_params = {
            "SYSTEM": "Fe2O2 Test",
            "ISTART": "0",
            "ICHARG": "2",
            "ENCUT": "500.0"
        }
        incar.write(incar_params)
        
        # 创建KPOINTS
        kpoints_file = temp_dir / "KPOINTS"
        kpoints = KPOINTS(kpoints_file)
        kpoints.write_gamma_centered([6, 6, 6], [0.0, 0.0, 0.0])
        
        # 验证所有文件都存在
        assert poscar_file.exists()
        assert incar_file.exists()
        assert kpoints_file.exists()
        
        # 验证文件内容
        incar_read = INCAR(incar_file)
        params_read = incar_read.read()
        assert params_read["SYSTEM"] == "Fe2O2 Test"
        
        kpoints_read = KPOINTS(kpoints_file)
        kpoints_data = kpoints_read.read()
        assert kpoints_data["grid"] == [6, 6, 6]

    def test_file_error_handling(self, temp_dir):
        """测试文件错误处理"""
        # 测试读取不存在的文件
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        poscar = POSCAR(nonexistent_file)
        with pytest.raises(Exception):  # 应该抛出FileNotFoundError或相关异常
            poscar.read()

    def test_invalid_file_format(self, temp_dir):
        """测试无效文件格式"""
        # 创建无效的POSCAR文件
        invalid_poscar = temp_dir / "POSCAR"
        invalid_poscar.write_text("This is not a valid POSCAR file")
        
        poscar = POSCAR(invalid_poscar)
        with pytest.raises(Exception):  # 应该抛出格式错误
            poscar.read()

    def test_empty_file_handling(self, temp_dir):
        """测试空文件处理"""
        empty_file = temp_dir / "INCAR"
        empty_file.write_text("")
        
        incar = INCAR(empty_file)
        parameters = incar.read()
        
        # 空文件应该返回空字典
        assert isinstance(parameters, dict)
        assert len(parameters) == 0
