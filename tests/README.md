# WVasp 测试套件

这个目录包含了WVasp项目的完整pytest测试套件，使用demo/data目录中的真实VASP数据进行测试。

## 📊 测试覆盖率

**当前覆盖率: 33%** 🎯

### 高覆盖率模块 (70%+)
- `core.base`: **87%** - 核心数据结构
- `io.poscar`: **87%** - POSCAR文件处理  
- `io.incar`: **91%** - INCAR文件处理
- `analysis.energy_analysis`: **72%** - 能量分析
- `io.kpoints`: **69%** - KPOINTS文件处理

### 中等覆盖率模块 (40-70%)
- `analysis.dos_analysis`: **46%** - DOS分析
- `io.base`: **75%** - IO基础类

## 📁 测试文件结构

```
tests/
├── conftest.py                 # pytest配置和共享fixtures
├── test_real_data_io.py       # 真实数据IO测试
├── test_real_data_analysis.py # 真实数据分析测试
├── test_core_modules.py       # 核心模块测试
└── README.md                  # 本文件
```

## 🧪 测试类别

### 1. 真实数据测试 (`test_real_data_*.py`)
使用demo/data目录中的真实VASP计算数据：

#### **结构文件测试**
- ✅ CONTCAR: C5H5N (11原子)
- ✅ CONTCAR_dos: CH4 (5原子)  
- ✅ CONTCAR_fix: Ce48H3NO99W (152原子)
- ✅ POSCAR_FS/IS: Au192 (192原子)

#### **分析文件测试**
- ✅ OUTCAR: 能量分析 (-71.52 eV, 费米能级 -5.31 eV)
- ✅ INCAR_file: 参数解析
- ⚠️ DOSCAR_dos: DOS分析 (部分功能)

### 2. 核心模块测试 (`test_core_modules.py`)
基础功能单元测试：

#### **数据结构测试**
- ✅ Atom类: 创建、属性、距离计算
- ✅ Lattice类: 体积、角度、倒格子
- ✅ Structure类: 组成、密度、坐标转换

#### **IO模块测试**
- ✅ POSCAR: 读写循环、坐标类型
- ✅ INCAR: 参数操作、类型解析
- ⚠️ KPOINTS: 基本功能 (需要修复)

## 🎯 测试特色

### 1. **真实数据驱动**
- 使用29.6MB真实VASP计算数据
- 涵盖多种材料体系和计算类型
- 验证实际使用场景

### 2. **全面的Fixtures**
```python
@pytest.fixture(scope="session")
def demo_data_dir():
    """真实数据目录"""
    
@pytest.fixture
def create_test_calculation_dir():
    """创建包含真实数据的测试计算目录"""
    
@pytest.fixture
def performance_test_files():
    """性能测试用的大文件"""
```

### 3. **性能测试**
- 大文件处理性能验证
- 内存使用监控
- 处理速度基准测试

### 4. **错误处理测试**
- 文件不存在处理
- 损坏文件处理
- 边界条件测试

## 🚀 运行测试

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行特定测试类
```bash
python -m pytest tests/test_real_data_io.py::TestRealDataPOSCAR -v
```

### 生成覆盖率报告
```bash
python -m pytest tests/ --cov=wvasp --cov-report=html
```

### 运行性能测试
```bash
python -m pytest tests/test_real_data_analysis.py::TestRealDataDOSAnalysis::test_dos_performance -v -s
```

## 📈 测试结果示例

```
✅ Demo data validation passed. Data dir: /Users/wukai/Desktop/project/vasp/wvasp/demo/data
✅ CONTCAR: C5H5N (11 atoms)
✅ CONTCAR_dos: CH4 (5 atoms)
✅ CONTCAR_fix: Ce48H3NO99W (152 atoms)
✅ POSCAR_FS: Au192 (192 atoms)
✅ Energy analysis: E_total=-71.516209 eV, E_fermi=-5.3131 eV, converged=True
✅ Convergence: True, ionic steps: 14
✅ Calculation time: 80.03 seconds
```

## 🔧 已知问题

1. ✅ ~~**KPOINTS测试**: `grid`和`style`属性访问需要修复~~ **已修复**
2. **DOS分析**: 部分DOSCAR解析功能需要完善
3. ✅ ~~**错误类型**: 某些测试期望`FileFormatError`但得到`IOError`~~ **已修复**

## 🎊 测试成就

- ✅ **56个测试用例全部通过** 🎉
- ✅ **33%代码覆盖率**
- ✅ **真实数据验证**
- ✅ **性能基准测试**
- ✅ **多材料体系支持**

## 💡 下一步改进

1. **修复失败测试**: 调整KPOINTS和错误处理测试
2. **提升DOS分析**: 完善DOSCAR解析功能
3. **添加tasks测试**: 提升tasks模块覆盖率
4. **集成测试**: 添加端到端工作流测试

这个测试套件为WVasp项目提供了坚实的质量保障基础！
