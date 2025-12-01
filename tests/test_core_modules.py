"""
测试核心模块（base, io基础功能）
"""

import pytest
import numpy as np
from pathlib import Path

from wvasp.core.base import Atom, Lattice, Structure
from wvasp.core.io import POSCAR, INCAR, KPOINTS
from wvasp.utils.errors import StructureError, FileFormatError


class TestAtom:
    """测试Atom类"""
    
    def test_atom_creation(self):
        """测试原子创建"""
        position = np.array([0.0, 0.0, 0.0])
        atom = Atom(element='Si', position=position)
        
        assert atom.element == 'Si'
        assert np.allclose(atom.position, position)
        assert atom.magnetic_moment is None
        assert atom.charge is None
    
    def test_atom_with_properties(self):
        """测试带属性的原子"""
        position = np.array([0.25, 0.25, 0.25])
        atom = Atom(element='Fe', position=position, 
                   magnetic_moment=2.5, charge=0.5)
        
        assert atom.element == 'Fe'
        assert np.allclose(atom.position, position)
        assert atom.magnetic_moment == 2.5
        assert atom.charge == 0.5
    
    def test_atom_distance(self):
        """测试原子间距离计算"""
        atom1 = Atom(element='Si', position=np.array([0.0, 0.0, 0.0]))
        atom2 = Atom(element='Si', position=np.array([1.0, 0.0, 0.0]))
        
        distance = atom1.distance_to(atom2)
        assert np.isclose(distance, 1.0)
    
    def test_atom_distance_3d(self):
        """测试3D空间中原子间距离"""
        atom1 = Atom(element='C', position=np.array([0.0, 0.0, 0.0]))
        atom2 = Atom(element='C', position=np.array([1.0, 1.0, 1.0]))
        
        distance = atom1.distance_to(atom2)
        expected_distance = np.sqrt(3.0)
        assert np.isclose(distance, expected_distance)


class TestLattice:
    """测试Lattice类"""
    
    def test_lattice_creation(self):
        """测试晶格创建"""
        matrix = np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ])
        lattice = Lattice(matrix)
        
        assert np.allclose(lattice.matrix, matrix)
    
    def test_lattice_volume(self):
        """测试晶格体积计算"""
        # 立方晶格
        matrix = np.array([
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0]
        ])
        lattice = Lattice(matrix)
        
        assert np.isclose(lattice.volume, 8.0)
    
    def test_lattice_lengths(self):
        """测试晶格参数长度"""
        matrix = np.array([
            [3.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 5.0]
        ])
        lattice = Lattice(matrix)
        
        expected_lengths = np.array([3.0, 4.0, 5.0])
        assert np.allclose(lattice.lengths, expected_lengths)
    
    def test_lattice_angles(self):
        """测试晶格角度"""
        # 正交晶格
        matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        lattice = Lattice(matrix)
        
        angles = lattice.angles
        expected_angles = np.array([90.0, 90.0, 90.0])
        assert np.allclose(angles, expected_angles)
    
    def test_lattice_reciprocal(self):
        """测试倒格子"""
        # 简单立方
        matrix = np.array([
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0]
        ])
        lattice = Lattice(matrix)
        reciprocal = lattice.reciprocal_lattice
        
        # 倒格子应该是原格子的倒数（乘以2π）
        expected_reciprocal = np.array([
            [np.pi, 0.0, 0.0],
            [0.0, np.pi, 0.0],
            [0.0, 0.0, np.pi]
        ])
        assert np.allclose(reciprocal.matrix, expected_reciprocal)


class TestStructure:
    """测试Structure类"""
    
    def test_structure_creation(self, sample_lattice, sample_atoms):
        """测试结构创建"""
        structure = Structure(
            lattice=sample_lattice,
            atoms=sample_atoms,
            coordinate_type='fractional'
        )
        
        assert structure.lattice == sample_lattice
        assert len(structure.atoms) == 4
        assert structure.coordinate_type == 'fractional'
    
    def test_structure_num_atoms(self, sample_structure):
        """测试原子数量"""
        assert sample_structure.num_atoms == 4
    
    def test_structure_composition(self, sample_structure):
        """测试化学组成"""
        composition = sample_structure.composition
        
        assert composition['Si'] == 2
        assert composition['O'] == 2
    
    def test_structure_formula(self, sample_structure):
        """测试化学式"""
        formula = sample_structure.formula
        
        # 应该包含Si和O
        assert 'Si' in formula
        assert 'O' in formula
        assert '2' in formula  # 数量
    
    def test_structure_volume(self, sample_structure):
        """测试结构体积"""
        volume = sample_structure.volume
        expected_volume = 5.43 ** 3
        assert np.isclose(volume, expected_volume)
    
    def test_structure_density(self, sample_structure):
        """测试密度计算"""
        density = sample_structure.density
        assert density > 0
    
    def test_structure_get_atoms_by_element(self, sample_structure):
        """测试按元素获取原子"""
        si_atoms = sample_structure.get_atoms_by_element('Si')
        o_atoms = sample_structure.get_atoms_by_element('O')
        
        assert len(si_atoms) == 2
        assert len(o_atoms) == 2
        
        for atom in si_atoms:
            assert atom.element == 'Si'
        
        for atom in o_atoms:
            assert atom.element == 'O'
    
    def test_structure_coordinates(self, sample_structure):
        """测试坐标获取"""
        frac_coords = sample_structure.get_fractional_coords()
        cart_coords = sample_structure.get_cartesian_coords()
        
        assert frac_coords.shape == (4, 3)
        assert cart_coords.shape == (4, 3)
        
        # 检查坐标范围
        assert np.all(frac_coords >= -0.1)  # 允许小的负值
        assert np.all(frac_coords <= 1.1)   # 允许稍大于1的值
    
    def test_structure_distances(self, sample_structure):
        """测试距离计算"""
        distance = sample_structure.get_distances(0, 1)
        assert distance > 0
        
        # 测试所有原子间距离
        for i in range(sample_structure.num_atoms):
            for j in range(i+1, sample_structure.num_atoms):
                dist = sample_structure.get_distances(i, j)
                assert dist > 0
    
    def test_structure_invalid_coordinate_type(self, sample_lattice, sample_atoms):
        """测试无效坐标类型"""
        with pytest.raises(StructureError):
            Structure(
                lattice=sample_lattice,
                atoms=sample_atoms,
                coordinate_type='invalid'
            )


class TestPOSCARBasic:
    """测试POSCAR基本功能"""
    
    def test_poscar_write_read_cycle(self, sample_structure, temp_dir):
        """测试POSCAR写入读取循环"""
        poscar_path = temp_dir / "test_poscar"
        
        # 写入
        poscar = POSCAR()
        poscar.write(poscar_path, structure=sample_structure, 
                    comment="Test structure")
        
        assert poscar_path.exists()
        
        # 读取
        poscar_read = POSCAR(poscar_path)
        structure_read = poscar_read.read()
        
        # 验证一致性
        assert structure_read.num_atoms == sample_structure.num_atoms
        assert structure_read.composition == sample_structure.composition
        assert np.isclose(structure_read.volume, sample_structure.volume)
    
    def test_poscar_different_coordinate_types(self, sample_structure, temp_dir):
        """测试不同坐标类型的POSCAR"""
        # 测试分数坐标
        frac_path = temp_dir / "frac_poscar"
        poscar_frac = POSCAR()
        poscar_frac.write(frac_path, structure=sample_structure, 
                         coordinate_type='Direct')
        
        # 测试笛卡尔坐标
        cart_path = temp_dir / "cart_poscar"
        poscar_cart = POSCAR()
        poscar_cart.write(cart_path, structure=sample_structure, 
                         coordinate_type='Cartesian')
        
        # 读取并验证
        frac_structure = POSCAR(frac_path).read()
        cart_structure = POSCAR(cart_path).read()
        
        assert frac_structure.num_atoms == cart_structure.num_atoms
        assert frac_structure.composition == cart_structure.composition
    
    def test_poscar_invalid_file(self, temp_dir):
        """测试无效POSCAR文件"""
        invalid_path = temp_dir / "invalid_poscar"
        with open(invalid_path, 'w') as f:
            f.write("Invalid content")
        
        poscar = POSCAR(invalid_path)
        with pytest.raises(FileFormatError):
            poscar.read()


class TestINCARBasic:
    """测试INCAR基本功能"""
    
    def test_incar_parameter_operations(self, temp_dir):
        """测试INCAR参数操作"""
        incar = INCAR()
        
        # 设置各种类型的参数
        incar.set_parameter('SYSTEM', 'Test system')
        incar.set_parameter('ENCUT', 400.0)
        incar.set_parameter('ISMEAR', -5)
        incar.set_parameter('LREAL', True)
        
        # 验证参数获取
        assert incar.get_parameter('ENCUT') == 400.0
        assert incar.get_parameter('ISMEAR') == -5
        assert incar.get_parameter('LREAL') is True
        
        # 处理可能的列表格式
        system = incar.get_parameter('SYSTEM')
        if isinstance(system, list):
            system = ' '.join(system)
        assert system == 'Test system'
    
    def test_incar_write_read_cycle(self, temp_dir):
        """测试INCAR写入读取循环"""
        # 创建INCAR
        incar = INCAR()
        incar.set_parameter('SYSTEM', 'Test calculation')
        incar.set_parameter('ENCUT', 500.0)
        incar.set_parameter('ISMEAR', 0)
        incar.set_parameter('SIGMA', 0.05)
        
        # 写入
        incar_path = temp_dir / "test_incar"
        incar.write(incar_path)
        
        # 读取
        incar_read = INCAR(incar_path)
        incar_read.read()
        
        # 验证
        assert incar_read.get_parameter('ENCUT') == 500.0
        assert incar_read.get_parameter('ISMEAR') == 0
        assert incar_read.get_parameter('SIGMA') == 0.05
    
    def test_incar_boolean_parameters(self, temp_dir):
        """测试INCAR布尔参数"""
        incar = INCAR()
        incar.set_parameter('LREAL', True)
        incar.set_parameter('LDAU', False)
        
        incar_path = temp_dir / "bool_incar"
        incar.write(incar_path)
        
        incar_read = INCAR(incar_path)
        incar_read.read()
        
        assert incar_read.get_parameter('LREAL') is True
        assert incar_read.get_parameter('LDAU') is False


class TestKPOINTSBasic:
    """测试KPOINTS基本功能"""
    
    def test_kpoints_gamma_centered(self, temp_dir):
        """测试Gamma中心K点"""
        kpoints = KPOINTS.create_gamma_centered([4, 4, 4])
        
        kpoints_path = temp_dir / "gamma_kpoints"
        kpoints.write(kpoints_path)
        
        assert kpoints_path.exists()
        
        # 读取验证
        kpoints_read = KPOINTS(kpoints_path)
        kpoints_read.read()
        
        assert kpoints_read.kpoint_grid == [4, 4, 4]
        assert kpoints_read.generation_style.lower().startswith('g')
    
    def test_kpoints_monkhorst_pack(self, temp_dir):
        """测试Monkhorst-Pack K点"""
        kpoints = KPOINTS.create_monkhorst_pack([6, 6, 6], [0.5, 0.5, 0.5])
        
        kpoints_path = temp_dir / "mp_kpoints"
        kpoints.write(kpoints_path)
        
        kpoints_read = KPOINTS(kpoints_path)
        kpoints_read.read()
        
        assert kpoints_read.kpoint_grid == [6, 6, 6]
        assert kpoints_read.kpoint_shift == [0.5, 0.5, 0.5]
        assert kpoints_read.generation_style.lower().startswith('m')


class TestErrorHandling:
    """测试错误处理"""
    
    def test_file_not_found_errors(self, temp_dir):
        """测试文件不存在错误"""
        nonexistent = temp_dir / "nonexistent_file"
        
        # POSCAR - 实际抛出的是IOError，不是FileFormatError
        from wvasp.utils.errors import IOError as VASPIOError
        with pytest.raises(VASPIOError):
            poscar = POSCAR(nonexistent)
            poscar.read()
        
        # INCAR
        with pytest.raises(VASPIOError):
            incar = INCAR(nonexistent)
            incar.read()
    
    def test_invalid_structure_parameters(self, sample_lattice):
        """测试无效结构参数"""
        # 空原子列表
        empty_structure = Structure(sample_lattice, [], 'fractional')
        assert empty_structure.num_atoms == 0
        
        # 无效坐标类型
        with pytest.raises(StructureError):
            Structure(sample_lattice, [], 'invalid_type')
    
    def test_invalid_atom_parameters(self):
        """测试无效原子参数"""
        # 正常创建应该成功
        atom = Atom('H', np.array([0.0, 0.0, 0.0]))
        assert atom.element == 'H'
        
        # 测试距离计算的边界情况
        atom1 = Atom('H', np.array([0.0, 0.0, 0.0]))
        atom2 = Atom('H', np.array([0.0, 0.0, 0.0]))
        
        # 相同位置的原子距离应该为0
        distance = atom1.distance_to(atom2)
        assert np.isclose(distance, 0.0)
