"""
使用真实数据测试IO模块
"""

import pytest
import numpy as np
from pathlib import Path

from wvasp.core.io import POSCAR, INCAR
from wvasp.core.base import Structure
from wvasp.utils.errors import FileFormatError


class TestRealDataPOSCAR:
    """使用真实数据测试POSCAR类"""
    
    def test_read_all_real_structure_files(self, real_structure_files):
        """测试读取所有真实结构文件"""
        successful_reads = 0
        results = {}
        
        for filename, file_path in real_structure_files.items():
            try:
                poscar = POSCAR(file_path)
                structure = poscar.read()
                
                # 验证结构的基本属性
                assert isinstance(structure, Structure)
                assert structure.num_atoms > 0
                assert structure.volume > 0
                assert len(structure.composition) > 0
                
                results[filename] = {
                    'formula': structure.formula,
                    'num_atoms': structure.num_atoms,
                    'volume': structure.volume,
                    'elements': list(structure.composition.keys())
                }
                
                successful_reads += 1
                
            except Exception as e:
                pytest.fail(f"Failed to read {filename}: {e}")
        
        # 至少应该成功读取一个文件
        assert successful_reads > 0, "No structure files were successfully read"
        
        # 验证读取的结构数据
        assert successful_reads == len(real_structure_files), \
            f"Only {successful_reads}/{len(real_structure_files)} files read successfully"
        
        # 打印结果用于验证
        for filename, data in results.items():
            print(f"✅ {filename}: {data['formula']} ({data['num_atoms']} atoms)")
    
    def test_contcar_structure_analysis(self, real_structure_files):
        """详细分析CONTCAR结构"""
        contcar_path = real_structure_files.get("CONTCAR")
        if not contcar_path:
            pytest.skip("CONTCAR file not available")
        
        poscar = POSCAR(contcar_path)
        structure = poscar.read()
        
        # 详细验证
        assert structure.formula == "C5H5N"  # 基于真实数据
        assert structure.num_atoms == 11
        assert abs(structure.volume - 1320.0) < 1.0  # 允许小误差
        
        # 验证元素组成
        composition = structure.composition
        assert 'C' in composition
        assert 'H' in composition
        assert 'N' in composition
        assert composition['C'] == 5
        assert composition['H'] == 5
        assert composition['N'] == 1
    
    def test_large_structure_file(self, real_structure_files):
        """测试大型结构文件（CONTCAR_fix）"""
        contcar_fix_path = real_structure_files.get("CONTCAR_fix")
        if not contcar_fix_path:
            pytest.skip("CONTCAR_fix file not available")
        
        poscar = POSCAR(contcar_fix_path)
        structure = poscar.read()
        
        # 这是一个大型结构
        assert structure.num_atoms == 152
        assert structure.formula == "Ce48H3NO99W"
        
        # 验证元素种类
        composition = structure.composition
        expected_elements = {'Ce', 'H', 'N', 'O', 'W'}
        assert set(composition.keys()) == expected_elements
        
        # 验证原子数量
        assert composition['Ce'] == 48
        assert composition['H'] == 3
        assert composition['N'] == 1
        assert composition['O'] == 99
        assert composition['W'] == 1
    
    def test_gold_cluster_structures(self, real_structure_files):
        """测试金团簇结构（POSCAR_FS和POSCAR_IS）"""
        for filename in ["POSCAR_FS", "POSCAR_IS"]:
            file_path = real_structure_files.get(filename)
            if not file_path:
                continue
            
            poscar = POSCAR(file_path)
            structure = poscar.read()
            
            # 验证金团簇结构
            assert structure.formula == "Au192"
            assert structure.num_atoms == 192
            assert len(structure.composition) == 1
            assert 'Au' in structure.composition
            assert structure.composition['Au'] == 192
            
            # 验证体积合理性
            assert structure.volume > 7000  # 大型金团簇
    
    def test_poscar_write_and_read_consistency(self, real_structure_files, temp_dir):
        """测试POSCAR写入和读取的一致性"""
        # 选择一个结构文件进行测试
        contcar_path = real_structure_files.get("CONTCAR")
        if not contcar_path:
            pytest.skip("CONTCAR file not available")
        
        # 读取原始结构
        original_poscar = POSCAR(contcar_path)
        original_structure = original_poscar.read()
        
        # 写入新文件
        output_path = temp_dir / "test_output_poscar"
        new_poscar = POSCAR()
        new_poscar.write(output_path, structure=original_structure, 
                        comment="Test output from real data")
        
        # 读取写入的文件
        read_poscar = POSCAR(output_path)
        read_structure = read_poscar.read()
        
        # 验证一致性
        assert read_structure.num_atoms == original_structure.num_atoms
        assert read_structure.composition == original_structure.composition
        assert abs(read_structure.volume - original_structure.volume) < 1e-6
    
    def test_coordinate_type_detection(self, real_structure_files):
        """测试坐标类型检测"""
        for filename, file_path in real_structure_files.items():
            poscar = POSCAR(file_path)
            structure = poscar.read()
            
            # 验证坐标类型
            assert structure.coordinate_type in ['fractional', 'cartesian']
            
            # 获取坐标
            frac_coords = structure.get_fractional_coords()
            cart_coords = structure.get_cartesian_coords()
            
            # 验证坐标形状
            assert frac_coords.shape == (structure.num_atoms, 3)
            assert cart_coords.shape == (structure.num_atoms, 3)
            
            # 分数坐标应该大致在0-1范围内（允许一些超出）
            assert np.all(frac_coords >= -0.1)
            assert np.all(frac_coords <= 1.1)


class TestRealDataINCAR:
    """使用真实数据测试INCAR类"""
    
    def test_read_real_incar(self, real_incar_path):
        """测试读取真实INCAR文件"""
        incar = INCAR(real_incar_path)
        incar.read()
        
        # 验证INCAR有效性
        assert incar.is_valid
        
        # 检查关键参数
        system = incar.get_parameter('SYSTEM')
        if isinstance(system, list):
            system = ' '.join(system)
        assert system is not None
        
        encut = incar.get_parameter('ENCUT')
        assert encut is not None
        assert isinstance(encut, (int, float))
        assert encut > 0
        
        ismear = incar.get_parameter('ISMEAR')
        assert ismear is not None
        assert isinstance(ismear, int)
        
        print(f"✅ INCAR parameters: SYSTEM={system}, ENCUT={encut}, ISMEAR={ismear}")
    
    def test_incar_parameter_types(self, real_incar_path):
        """测试INCAR参数类型解析"""
        incar = INCAR(real_incar_path)
        incar.read()
        
        # 测试不同类型的参数
        test_params = {
            'ENCUT': (int, float),
            'ISMEAR': int,
            'SIGMA': float,
            'NSW': int,
            'IBRION': int,
            'EDIFF': float,
            'PREC': (str, list)
        }
        
        for param_name, expected_types in test_params.items():
            value = incar.get_parameter(param_name)
            if value is not None:
                if isinstance(expected_types, tuple):
                    assert isinstance(value, expected_types), \
                        f"{param_name} should be {expected_types}, got {type(value)}"
                else:
                    assert isinstance(value, expected_types), \
                        f"{param_name} should be {expected_types}, got {type(value)}"
    
    def test_incar_write_and_read_consistency(self, real_incar_path, temp_dir):
        """测试INCAR写入和读取的一致性"""
        # 读取原始INCAR
        original_incar = INCAR(real_incar_path)
        original_incar.read()
        
        # 获取所有参数
        original_params = {}
        for key in ['SYSTEM', 'ENCUT', 'ISMEAR', 'SIGMA', 'NSW', 'IBRION', 'EDIFF', 'PREC']:
            value = original_incar.get_parameter(key)
            if value is not None:
                original_params[key] = value
        
        # 创建新的INCAR并设置参数
        new_incar = INCAR()
        for key, value in original_params.items():
            new_incar.set_parameter(key, value)
        
        # 写入文件
        output_path = temp_dir / "test_incar_output"
        new_incar.write(output_path)
        
        # 读取写入的文件
        read_incar = INCAR(output_path)
        read_incar.read()
        
        # 验证一致性
        for key, original_value in original_params.items():
            read_value = read_incar.get_parameter(key)
            
            # 处理字符串列表的情况
            if isinstance(original_value, list) and isinstance(read_value, list):
                assert original_value == read_value or ' '.join(original_value) == ' '.join(read_value)
            elif isinstance(original_value, list):
                assert ' '.join(original_value) == read_value
            elif isinstance(read_value, list):
                assert original_value == ' '.join(read_value)
            else:
                assert original_value == read_value, f"Mismatch for {key}: {original_value} != {read_value}"


class TestRealDataFileValidation:
    """真实数据文件验证测试"""
    
    def test_file_sizes_reasonable(self, demo_data_dir):
        """测试文件大小是否合理"""
        file_size_expectations = {
            'OUTCAR': (100_000, 10_000_000),      # 100KB - 10MB
            'DOSCAR_dos': (1_000_000, 100_000_000),  # 1MB - 100MB
            'CHGCAR': (1_000_000, 50_000_000),    # 1MB - 50MB
            'LOCPOT': (1_000_000, 50_000_000),    # 1MB - 50MB
            'CONTCAR': (500, 50_000),             # 500B - 50KB
            'INCAR_file': (100, 10_000),          # 100B - 10KB
        }
        
        for filename, (min_size, max_size) in file_size_expectations.items():
            file_path = demo_data_dir / filename
            if file_path.exists():
                file_size = file_path.stat().st_size
                assert min_size <= file_size <= max_size, \
                    f"{filename} size {file_size} not in expected range [{min_size}, {max_size}]"
                print(f"✅ {filename}: {file_size:,} bytes")
    
    def test_file_format_headers(self, demo_data_dir):
        """测试文件格式头部"""
        # 测试POSCAR格式文件
        poscar_files = ["CONTCAR", "POSCAR_FS", "POSCAR_IS"]
        for filename in poscar_files:
            file_path = demo_data_dir / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # POSCAR应该有足够的行数
                assert len(lines) >= 8, f"{filename} has too few lines"
                
                # 第二行应该是缩放因子
                try:
                    scale_factor = float(lines[1].strip())
                    assert scale_factor > 0, f"{filename} has invalid scale factor"
                except ValueError:
                    pytest.fail(f"{filename} line 2 is not a valid scale factor")
    
    def test_data_directory_structure(self, demo_data_dir):
        """测试数据目录结构"""
        # 检查必要的文件
        required_files = ["OUTCAR", "CONTCAR", "INCAR_file"]
        for filename in required_files:
            file_path = demo_data_dir / filename
            assert file_path.exists(), f"Required file {filename} not found"
            assert file_path.is_file(), f"{filename} is not a file"
            assert file_path.stat().st_size > 0, f"{filename} is empty"
        
        # 检查子目录
        expected_subdirs = ["dos", "neb", "band_kpath"]
        for dirname in expected_subdirs:
            dir_path = demo_data_dir / dirname
            if dir_path.exists():
                assert dir_path.is_dir(), f"{dirname} should be a directory"
    
    def test_no_python_files_in_data(self, demo_data_dir):
        """确保数据目录中没有Python文件"""
        python_files = list(demo_data_dir.rglob("*.py"))
        assert len(python_files) == 0, f"Found Python files in data directory: {python_files}"
        
        # 检查是否有其他不应该存在的文件
        unwanted_patterns = ["*.pyc", "*.pyo", "__pycache__", "*.log"]
        for pattern in unwanted_patterns:
            unwanted_files = list(demo_data_dir.rglob(pattern))
            assert len(unwanted_files) == 0, f"Found unwanted files: {unwanted_files}"
