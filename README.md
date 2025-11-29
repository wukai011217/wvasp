# WVasp - VASP计算工具

一个基于Python的VASP (Vienna Ab initio Simulation Package) 计算辅助工具。

## 功能特性

- 🔧 VASP文件读写和处理
- 📊 计算结果分析和可视化
- ⚡ 高性能数值计算
- 🎯 任务管理和工作流
- 📈 数据可视化和绘图

## 安装

```bash
pip install -e .
```

## 快速开始

```python
from wvasp.core.io import POSCAR
from wvasp.core.structure import Structure

# 读取POSCAR文件
poscar = POSCAR("POSCAR")
structure = poscar.read()

# 分析结构
print(f"晶胞体积: {structure.volume:.2f} Å³")
print(f"原子数量: {len(structure.atoms)}")
```

## 开发状态

🚧 项目正在开发中...

## 许可证

MIT License
