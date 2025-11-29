"""
POSCAR文件处理测试
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from wvasp.core.io.poscar import POSCAR
from wvasp.core.base import Structure, Lattice, Atom


class TestPOSCAR:
    """POSCAR测试类"""
    
    def create_sample_poscar_content(self):
        """创建示例POSCAR内容"""
        return [
            "Si2\n",
            "1.0\n",
            "5.4 0.0 0.0\n",
            "0.0 5.4 0.0\n", 
            "0.0 0.0 5.4\n",
            "Si\n",
            "2\n",
            "Direct\n",
            "0.0 0.0 0.0\n",
            "0.25 0.25 0.25\n"
        ]
    
    def test_poscar_init(self):
        """测试POSCAR初始化"""
        poscar = POSCAR()
        assert poscar.filepath is None
        assert not poscar.is_valid
        
        poscar = POSCAR(Path("test.poscar"))
        assert poscar.filepath == Path("test.poscar")
    
    def test_poscar_parse(self):
        """测试POSCAR解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.poscar', delete=False) as f:
            f.writelines(self.create_sample_poscar_content())
            temp_path = Path(f.name)
        
        try:
            poscar = POSCAR(temp_path)
            structure = poscar.read()
            
            # 检查基本信息
            assert structure.formula == "Si2"
            assert structure.num_atoms == 2
            assert len(structure.atoms) == 2
            
            # 检查晶格
            expected_lattice = np.array([
                [5.4, 0.0, 0.0],
                [0.0, 5.4, 0.0],
                [0.0, 0.0, 5.4]
            ])
            np.testing.assert_array_almost_equal(structure.lattice.matrix, expected_lattice)
            
            # 检查原子
            assert all(atom.element == "Si" for atom in structure.atoms)
            assert structure.coordinate_type == "fractional"
            
            # 检查坐标
            expected_positions = np.array([
                [0.0, 0.0, 0.0],
                [0.25, 0.25, 0.25]
            ])
            positions = structure.get_fractional_coords()
            np.testing.assert_array_almost_equal(positions, expected_positions)
            
        finally:
            temp_path.unlink()
    
    def test_poscar_write(self):
        """测试POSCAR写入"""
        # 创建测试结构
        lattice = Lattice(np.array([
            [5.0, 0.0, 0.0],
            [0.0, 5.0, 0.0],
            [0.0, 0.0, 5.0]
        ]))
        
        atoms = [
            Atom("C", np.array([0.0, 0.0, 0.0])),
            Atom("C", np.array([0.5, 0.5, 0.5]))
        ]
        
        structure = Structure(lattice, atoms, coordinate_type="fractional")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.poscar', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            poscar = POSCAR()
            poscar.write(temp_path, structure=structure, comment="Test structure")
            
            # 读取并验证
            poscar2 = POSCAR(temp_path)
            structure2 = poscar2.read()
            
            assert structure2.formula == "C2"
            assert structure2.num_atoms == 2
            np.testing.assert_array_almost_equal(
                structure2.lattice.matrix, structure.lattice.matrix
            )
            
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
