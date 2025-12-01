"""
pytest配置文件和共享fixtures
使用demo/data目录中的真实VASP数据进行测试
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

from wvasp.core.base import Atom, Lattice, Structure


@pytest.fixture(scope="session")
def demo_data_dir():
    """真实数据目录"""
    data_dir = Path(__file__).parent.parent / "demo" / "data"
    if not data_dir.exists():
        pytest.skip("Demo data directory not found")
    return data_dir


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_atoms():
    """示例原子列表"""
    return [
        Atom(element='Si', position=np.array([0.0, 0.0, 0.0])),
        Atom(element='Si', position=np.array([0.25, 0.25, 0.25])),
        Atom(element='O', position=np.array([0.5, 0.5, 0.0])),
        Atom(element='O', position=np.array([0.75, 0.75, 0.25])),
    ]


@pytest.fixture
def sample_lattice():
    """示例晶格"""
    matrix = np.array([
        [5.43, 0.0, 0.0],
        [0.0, 5.43, 0.0],
        [0.0, 0.0, 5.43]
    ])
    return Lattice(matrix)


@pytest.fixture
def sample_structure(sample_lattice, sample_atoms):
    """示例结构"""
    return Structure(
        lattice=sample_lattice,
        atoms=sample_atoms,
        coordinate_type='fractional'
    )


@pytest.fixture(scope="session")
def real_outcar_path(demo_data_dir):
    """真实OUTCAR文件路径"""
    outcar_path = demo_data_dir / "OUTCAR"
    if not outcar_path.exists():
        pytest.skip("Real OUTCAR file not found")
    return outcar_path


@pytest.fixture(scope="session")
def real_doscar_path(demo_data_dir):
    """真实DOSCAR文件路径"""
    doscar_path = demo_data_dir / "DOSCAR_dos"
    if not doscar_path.exists():
        pytest.skip("Real DOSCAR file not found")
    return doscar_path


@pytest.fixture(scope="session")
def real_incar_path(demo_data_dir):
    """真实INCAR文件路径"""
    incar_path = demo_data_dir / "INCAR_file"
    if not incar_path.exists():
        pytest.skip("Real INCAR file not found")
    return incar_path


@pytest.fixture(scope="session")
def real_structure_files(demo_data_dir):
    """真实结构文件路径字典"""
    structure_files = {}
    filenames = [
        "CONTCAR", "CONTCAR_dos", "CONTCAR_fix",
        "POSCAR_FS", "POSCAR_IS", "POSCAR_FS_sort", "POSCAR_IS_sort"
    ]
    
    for filename in filenames:
        file_path = demo_data_dir / filename
        if file_path.exists():
            structure_files[filename] = file_path
    
    return structure_files


@pytest.fixture
def create_test_calculation_dir(temp_dir, demo_data_dir):
    """创建包含真实数据的测试计算目录"""
    def _create_calc_dir(files_to_copy=None):
        """
        创建测试计算目录
        
        Args:
            files_to_copy: 要复制的文件列表，默认复制主要文件
        """
        if files_to_copy is None:
            files_to_copy = ["OUTCAR", "DOSCAR_dos", "INCAR_file", "CONTCAR"]
        
        calc_dir = temp_dir / "test_calculation"
        calc_dir.mkdir(exist_ok=True)
        
        copied_files = {}
        for filename in files_to_copy:
            src_path = demo_data_dir / filename
            if src_path.exists():
                if filename == "DOSCAR_dos":
                    dst_path = calc_dir / "DOSCAR"
                elif filename == "INCAR_file":
                    dst_path = calc_dir / "INCAR"
                else:
                    dst_path = calc_dir / filename
                
                shutil.copy2(src_path, dst_path)
                copied_files[filename] = dst_path
        
        return calc_dir, copied_files
    
    return _create_calc_dir


@pytest.fixture(scope="session")
def performance_test_files(demo_data_dir):
    """性能测试用的大文件"""
    large_files = {}
    filenames = [
        "DOSCAR_dos", "CHGCAR", "LOCPOT", 
        "AECCAR0", "AECCAR2", "XDATCAR"
    ]
    
    for filename in filenames:
        file_path = demo_data_dir / filename
        if file_path.exists():
            large_files[filename] = file_path
    
    return large_files


@pytest.fixture
def dos_subdirectory_data(demo_data_dir):
    """DOS子目录数据"""
    dos_dir = demo_data_dir / "dos"
    if not dos_dir.exists():
        pytest.skip("DOS subdirectory not found")
    return dos_dir


@pytest.fixture
def neb_subdirectory_data(demo_data_dir):
    """NEB子目录数据"""
    neb_dir = demo_data_dir / "neb"
    if not neb_dir.exists():
        pytest.skip("NEB subdirectory not found")
    return neb_dir


@pytest.fixture
def band_kpath_data(demo_data_dir):
    """能带K点路径数据"""
    band_dir = demo_data_dir / "band_kpath"
    if not band_dir.exists():
        pytest.skip("Band kpath directory not found")
    return band_dir


# 测试数据验证fixtures
@pytest.fixture(scope="session", autouse=True)
def validate_demo_data(demo_data_dir):
    """验证演示数据的完整性"""
    required_files = ["OUTCAR", "CONTCAR", "INCAR_file"]
    missing_files = []
    
    for filename in required_files:
        if not (demo_data_dir / filename).exists():
            missing_files.append(filename)
    
    if missing_files:
        pytest.skip(f"Missing required demo data files: {missing_files}")
    
    # 验证文件大小
    outcar_size = (demo_data_dir / "OUTCAR").stat().st_size
    if outcar_size < 1000:  # 至少1KB
        pytest.skip("OUTCAR file too small, may be corrupted")
    
    print(f"✅ Demo data validation passed. Data dir: {demo_data_dir}")


# 性能测试相关fixtures
@pytest.fixture
def performance_threshold():
    """性能测试阈值"""
    return {
        'file_read_time': 5.0,  # 秒
        'memory_usage': 100,    # MB
        'large_file_speed': 1.0  # MB/s
    }


# 错误处理测试fixtures
@pytest.fixture
def create_corrupted_files(temp_dir):
    """创建损坏的测试文件"""
    def _create_corrupted(file_type, content="corrupted content"):
        corrupted_path = temp_dir / f"corrupted_{file_type}"
        with open(corrupted_path, 'w') as f:
            f.write(content)
        return corrupted_path
    
    return _create_corrupted
