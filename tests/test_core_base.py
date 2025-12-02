"""
测试core.base模块

测试基础数据结构：Atom, Lattice, Structure。
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.core.base import Atom, Lattice, Structure


class TestAtom:
    """测试Atom类"""
    
    def test_atom_init_basic(self):
        """测试基本原子初始化"""
        position = np.array([0.0, 0.5, 1.0])
        atom = Atom("Fe", position)
        
        assert atom.element == "Fe"
        assert np.allclose(atom.position, position)
        assert atom.magnetic_moment is None
        assert atom.charge is None

    def test_atom_init_with_properties(self):
        """测试带属性的原子初始化"""
        position = np.array([0.25, 0.25, 0.25])
        atom = Atom("Fe", position, magnetic_moment=5.0, charge=2.0)
        
        assert atom.element == "Fe"
        assert np.allclose(atom.position, position)
        assert atom.magnetic_moment == 5.0
        assert atom.charge == 2.0

    def test_distance_to(self):
        """测试原子间距离计算"""
        atom1 = Atom("Fe", np.array([0.0, 0.0, 0.0]))
        atom2 = Atom("O", np.array([1.0, 1.0, 1.0]))
        
        distance = atom1.distance_to(atom2)
        expected_distance = np.sqrt(3.0)  # sqrt(1^2 + 1^2 + 1^2)
        
        assert np.isclose(distance, expected_distance)

    def test_atomic_properties(self):
        """测试原子属性"""
        atom = Atom("Fe", np.array([0.0, 0.0, 0.0]))
        
        # 测试原子序数
        assert atom.atomic_number == 26  # Fe的原子序数
        
        # 测试原子质量
        assert atom.atomic_mass > 0

    def test_atom_str_repr(self):
        """测试原子字符串表示"""
        atom = Atom("Fe", np.array([0.5, 0.5, 0.5]))
        
        str_repr = str(atom)
        assert "Fe" in str_repr
        assert "0.5" in str_repr


class TestLattice:
    """测试Lattice类"""
    
    @pytest.fixture
    def cubic_lattice(self):
        """立方晶格"""
        matrix = np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ])
        return Lattice(matrix)

    @pytest.fixture
    def orthorhombic_lattice(self):
        """正交晶格"""
        matrix = np.array([
            [4.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 6.0]
        ])
        return Lattice(matrix)

    def test_lattice_init(self, cubic_lattice):
        """测试晶格初始化"""
        assert cubic_lattice.matrix.shape == (3, 3)
        assert np.allclose(cubic_lattice.matrix[0], [5.0, 0.0, 0.0])

    def test_lattice_volume(self, cubic_lattice, orthorhombic_lattice):
        """测试晶格体积计算"""
        # 立方晶格体积
        assert np.isclose(cubic_lattice.volume, 125.0)  # 5^3
        
        # 正交晶格体积
        assert np.isclose(orthorhombic_lattice.volume, 120.0)  # 4*5*6

    def test_lattice_lengths(self, cubic_lattice, orthorhombic_lattice):
        """测试晶格参数长度"""
        # 立方晶格
        lengths = cubic_lattice.lengths
        assert np.allclose(lengths, [5.0, 5.0, 5.0])
        
        # 正交晶格
        lengths = orthorhombic_lattice.lengths
        assert np.allclose(lengths, [4.0, 5.0, 6.0])

    def test_lattice_angles(self, cubic_lattice):
        """测试晶格角度"""
        # 立方晶格角度应该都是90度
        angles = cubic_lattice.angles
        assert np.allclose(angles, [90.0, 90.0, 90.0], atol=1e-10)

    def test_cart_to_frac(self, cubic_lattice):
        """测试笛卡尔坐标转分数坐标"""
        cart_coords = np.array([2.5, 2.5, 2.5])  # 晶胞中心
        frac_coords = cubic_lattice.cart_to_frac(cart_coords)
        
        expected = np.array([0.5, 0.5, 0.5])
        assert np.allclose(frac_coords, expected)

    def test_frac_to_cart(self, cubic_lattice):
        """测试分数坐标转笛卡尔坐标"""
        frac_coords = np.array([0.5, 0.5, 0.5])  # 晶胞中心
        cart_coords = cubic_lattice.frac_to_cart(frac_coords)
        
        expected = np.array([2.5, 2.5, 2.5])
        assert np.allclose(cart_coords, expected)

    def test_coordinate_conversion_roundtrip(self, cubic_lattice):
        """测试坐标转换往返"""
        test_coords = [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.5, 0.5, 0.5]),
            np.array([0.25, 0.75, 0.1]),
        ]
        
        for frac_coord in test_coords:
            # 分数 -> 笛卡尔 -> 分数
            cart_coord = cubic_lattice.frac_to_cart(frac_coord)
            frac_coord_back = cubic_lattice.cart_to_frac(cart_coord)
            assert np.allclose(frac_coord, frac_coord_back, atol=1e-10)


class TestStructure:
    """测试Structure类"""
    
    def test_structure_init(self, sample_structure):
        """测试结构初始化"""
        assert hasattr(sample_structure, 'comment')
        assert sample_structure.comment == "Fe2O2 Test Structure"
        assert len(sample_structure.atoms) == 4
        assert sample_structure.coordinate_type == "fractional"
        assert isinstance(sample_structure.lattice, Lattice)

    def test_structure_num_atoms(self, sample_structure):
        """测试原子数量"""
        assert sample_structure.num_atoms == 4

    def test_structure_volume(self, sample_structure):
        """测试结构体积"""
        expected_volume = 125.0  # 5^3
        assert np.isclose(sample_structure.volume, expected_volume)

    def test_structure_composition(self, sample_structure):
        """测试成分分析"""
        comp = sample_structure.composition
        assert comp == {"Fe": 2, "O": 2}

    def test_structure_formula(self, sample_structure):
        """测试化学式生成"""
        formula = sample_structure.formula
        # 化学式可能是Fe2O2或O2Fe2，取决于实现
        assert "Fe" in formula and "O" in formula
        assert "2" in formula

    def test_structure_str_repr(self, sample_structure):
        """测试结构字符串表示"""
        str_repr = str(sample_structure)
        assert "4" in str_repr  # 原子数量
        assert "Structure" in str_repr or "Fe" in str_repr


class TestStructureOperations:
    """测试结构操作"""
    
    def test_structure_creation_from_scratch(self):
        """测试从头创建结构"""
        # 创建晶格
        lattice = Lattice(np.array([
            [10.0, 0.0, 0.0],
            [0.0, 10.0, 0.0],
            [0.0, 0.0, 10.0]
        ]))
        
        # 创建原子
        atoms = [
            Atom("C", np.array([0.0, 0.0, 0.0])),
            Atom("O", np.array([0.5, 0.5, 0.5]))
        ]
        
        # 创建结构
        structure = Structure(lattice, atoms, coordinate_type="fractional")
        structure.comment = "CO molecule"
        
        assert structure.num_atoms == 2
        assert np.isclose(structure.volume, 1000.0)  # 10^3
        assert structure.coordinate_type == "fractional"

    def test_different_coordinate_types(self):
        """测试不同坐标类型"""
        lattice = Lattice(np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ]))
        
        atoms = [Atom("Fe", np.array([0.0, 0.0, 0.0]))]
        
        # 测试分数坐标
        structure_frac = Structure(lattice, atoms, coordinate_type="fractional")
        assert structure_frac.coordinate_type == "fractional"
        
        # 测试笛卡尔坐标
        structure_cart = Structure(lattice, atoms, coordinate_type="cartesian")
        assert structure_cart.coordinate_type == "cartesian"

    def test_invalid_coordinate_type(self):
        """测试无效坐标类型"""
        lattice = Lattice(np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ]))
        
        atoms = [Atom("Fe", np.array([0.0, 0.0, 0.0]))]
        
        with pytest.raises(Exception):  # 应该抛出StructureError
            Structure(lattice, atoms, coordinate_type="invalid")


class TestBaseIntegration:
    """基础模块集成测试"""
    
    def test_complex_structure_creation(self):
        """测试复杂结构创建"""
        # 创建六方晶格
        a = 3.0
        c = 5.0
        lattice = Lattice(np.array([
            [a, 0.0, 0.0],
            [-a/2, a*np.sqrt(3)/2, 0.0],
            [0.0, 0.0, c]
        ]))
        
        # 创建多种元素
        atoms = []
        elements = ["Ti", "O"]
        positions = [
            [0.0, 0.0, 0.0], [0.333, 0.667, 0.25],
            [0.667, 0.333, 0.75], [0.333, 0.667, 0.75]
        ]
        
        for i, pos in enumerate(positions):
            element = elements[i % len(elements)]
            atom = Atom(element, np.array(pos))
            atoms.append(atom)
        
        structure = Structure(lattice, atoms, coordinate_type="fractional")
        structure.comment = "TiO2 Hexagonal"
        
        # 验证结构
        assert structure.num_atoms == 4
        assert len(set(atom.element for atom in structure.atoms)) == 2
        assert structure.volume > 0

    def test_atom_lattice_structure_consistency(self):
        """测试原子、晶格、结构的一致性"""
        # 创建原子
        atom = Atom("Fe", np.array([0.25, 0.25, 0.25]), magnetic_moment=5.0)
        
        # 创建晶格
        lattice = Lattice(np.array([
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0]
        ]))
        
        # 创建结构
        structure = Structure(lattice, [atom], coordinate_type="fractional")
        
        # 验证一致性
        assert structure.atoms[0].element == atom.element
        assert np.allclose(structure.atoms[0].position, atom.position)
        assert structure.atoms[0].magnetic_moment == atom.magnetic_moment
        assert structure.lattice.volume == lattice.volume
