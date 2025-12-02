# WVasp 更新日志

## [0.2.1] - 2025-12-02

### 🎯 重大更新
- **统一模板系统**: 为KPOINTS、POTCAR、SLURM添加了完整的模板支持
- **参数管理重构**: 创建了KPointsConfig、PotcarConfig、SlurmConfig类
- **命令行接口统一**: 所有命令都支持--template参数
- **测试框架建立**: 创建了完整的pytest测试基础设施

### ✨ 新增功能
- **23种统一模板**: INCAR(6) + KPOINTS(7) + POTCAR(5) + SLURM(5)
- **新配置类**: KPointsConfig、PotcarConfig、SlurmConfig
- **统一模板参数**: 所有命令支持--template选项
- **完整测试套件**: 108个测试用例，覆盖核心功能
- **环境配置**: 自动化环境设置和依赖管理

### 🔧 改进
- **代码重复消除**: 统一了SLURM脚本生成逻辑
- **API标准化**: 统一了配置管理器的接口
- **错误处理**: 改进了异常处理和用户提示
- **文档完善**: 添加了详细的使用指南和测试报告

### 🏗️ 架构变更
- **参数管理模块**: 从utils迁移到core/parameters/
- **模板系统**: 集中管理在utils/constants.py
- **测试框架**: 建立了完整的pytest基础设施
- **配置管理**: 新增utils/config.py环境配置

### 📊 测试覆盖
- **108个测试用例**: 覆盖基础结构、IO、参数管理、主程序
- **69%覆盖率**: core/base.py模块
- **17%整体覆盖率**: 为进一步提升奠定基础
- **完整测试框架**: pytest配置、fixtures、运行脚本

### 🔄 API变更
- **Structure构造函数**: 不再接受comment参数，需单独设置
- **Atom默认值**: magnetic_moment和charge默认为None
- **导入路径**: 参数管理从core.parameters导入
- **模板使用**: 统一的模板参数格式

### 📁 文件结构
```
wvasp/
├── core/
│   ├── parameters/          # 新增参数管理模块
│   │   ├── manager.py      # 统一配置管理器
│   │   └── magnetic.py     # 磁矩管理
│   └── ...
├── utils/
│   ├── constants.py        # 统一模板系统
│   └── config.py          # 新增环境配置
├── tests/                  # 重建测试框架
│   ├── conftest.py        # pytest配置
│   ├── test_core_base.py  # 基础结构测试
│   ├── test_core_io.py    # 文件IO测试
│   ├── test_parameters.py # 参数管理测试
│   └── test_main.py       # 主程序测试
├── pytest.ini            # pytest配置
├── run_tests.py          # 测试运行脚本
└── ENVIRONMENT_SETUP.md  # 环境设置指南
```

### 🚀 使用示例
```bash
# 统一的模板使用
python -m wvasp build POSCAR optimization
python -m wvasp incar create -t optimization
python -m wvasp kpoints create -t slab_2d
python -m wvasp potcar create -t PBE_hard -e Fe O
python -m wvasp slurm create --template gpu_accelerated

# 测试运行
python run_tests.py --coverage --html
pytest tests/ --cov=wvasp --cov-report=html
```

### 📈 性能提升
- **代码减少**: 消除了重复的文件生成逻辑
- **架构清晰**: 数据与逻辑分离，职责明确
- **易维护**: 统一的参数管理和文件生成流程
- **高质量**: 完整的测试覆盖保证代码质量

### 🔗 兼容性
- **Python**: 3.8+
- **依赖**: numpy, pathlib, argparse
- **测试**: pytest, pytest-cov
- **向后兼容**: 保持主要API兼容性

---

## [0.2.0] - 之前版本
- 基础VASP文件处理功能
- 基本命令行接口
- 核心数据结构定义
