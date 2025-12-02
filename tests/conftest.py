"""
pytest配置文件

定义全局fixtures和测试配置。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.core.base import Atom, Lattice, Structure


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_atom():
    """创建示例原子"""
    return Atom("Fe", np.array([0.0, 0.0, 0.0]), magnetic_moment=5.0)


@pytest.fixture
def sample_lattice():
    """创建示例晶格"""
    matrix = np.array([
        [5.0, 0.0, 0.0],
        [0.0, 5.0, 0.0],
        [0.0, 0.0, 5.0]
    ])
    return Lattice(matrix)


@pytest.fixture
def sample_structure(sample_lattice):
    """创建示例结构"""
    atoms = [
        Atom("Fe", np.array([0.0, 0.0, 0.0])),
        Atom("Fe", np.array([0.5, 0.5, 0.5])),
        Atom("O", np.array([0.25, 0.25, 0.25])),
        Atom("O", np.array([0.75, 0.75, 0.75]))
    ]
    
    structure = Structure(sample_lattice, atoms, coordinate_type="fractional")
    structure.comment = "Fe2O2 Test Structure"
    return structure


@pytest.fixture
def sample_poscar_content():
    """示例POSCAR内容"""
    return """Fe2O3 Structure
1.0
5.0 0.0 0.0
0.0 5.0 0.0
0.0 0.0 5.0
Fe O
2 3
Direct
0.0 0.0 0.0
0.5 0.5 0.5
0.25 0.25 0.25
0.75 0.75 0.75
0.5 0.0 0.0
"""


@pytest.fixture
def sample_incar_content():
    """示例INCAR内容"""
    return """SYSTEM = Test Structure
ISTART = 0
ICHARG = 2
PREC = Accurate
ENCUT = 500.0
EDIFF = 1e-05
ALGO = Normal
NELM = 500
ISPIN = 2
ISMEAR = 0
SIGMA = 0.05
NSW = 100
IBRION = 2
ISIF = 3
"""


@pytest.fixture
def sample_kpoints_content():
    """示例KPOINTS内容"""
    return """Automatic mesh
0
Gamma
6 6 6
0.0 0.0 0.0
"""
