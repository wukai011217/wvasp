# WVasp 实用脚本

这个目录包含了基于WVasp类库构建的实用脚本，用于日常VASP计算工作流。

## 📁 脚本列表

### 1. `quick_vasp_setup.py` - 快速设置工具
快速为单个结构设置VASP计算。

**使用方法:**
```bash
python quick_vasp_setup.py structure.vasp --job-name my_calc --nodes 2 --time 24:00:00
```

**主要参数:**
- `structure`: 结构文件路径 (POSCAR格式)
- `--job-name`: 作业名称 (默认: vasp_calc)
- `--nodes`: 节点数 (默认: 1)
- `--ntasks-per-node`: 每节点核心数 (默认: 24)
- `--memory`: 内存 (默认: 32G)
- `--time`: 计算时间 (默认: 12:00:00)
- `--encut`: 截断能 (默认: 400.0)
- `--kpoints`: K点网格 (默认: [6, 6, 6])
- `--output-dir`: 输出目录 (默认: .)

**生成文件:**
- POSCAR: 结构文件
- INCAR: 计算参数
- KPOINTS: K点设置
- submit.sh: SLURM作业脚本

### 2. `analyze_results.py` - 结果分析工具
分析VASP计算结果，提供详细的状态报告。

**使用方法:**
```bash
python analyze_results.py /path/to/calculation/directory
```

**分析内容:**
- 文件完整性检查
- OUTCAR结果解析 (能量、收敛性、力、应力)
- DOSCAR态密度分析
- 结构变化分析
- 计算状态总结和建议

### 3. `batch_vasp.py` - 批量处理工具
批量设置多个VASP计算，支持模板配置。

**创建默认模板:**
```bash
python batch_vasp.py --create-template
```

**批量设置:**
```bash
python batch_vasp.py structures/ --template vasp_template.json --output-dir calculations
```

**主要参数:**
- `structures_dir`: 结构文件目录
- `--template`: 计算模板JSON文件
- `--output-dir`: 输出目录 (默认: calculations)
- `--pattern`: 结构文件匹配模式 (默认: *.vasp)

**模板格式 (vasp_template.json):**
```json
{
  "incar": {
    "ENCUT": 400.0,
    "ISMEAR": 0,
    "SIGMA": 0.05,
    "EDIFF": 1e-6,
    "NSW": 100,
    "IBRION": 2,
    "ISIF": 3
  },
  "kpoints": {
    "type": "gamma",
    "grid": [6, 6, 6]
  },
  "job": {
    "nodes": 1,
    "ntasks_per_node": 24,
    "memory": "32G",
    "time": "12:00:00",
    "partition": "normal",
    "vasp_executable": "vasp_std",
    "modules": ["intel/2021", "vasp/6.3.0"]
  }
}
```

## 🚀 典型工作流

### 单个计算
```bash
# 1. 快速设置
python scripts/quick_vasp_setup.py my_structure.vasp --job-name test_calc

# 2. 提交作业
sbatch submit.sh

# 3. 分析结果
python scripts/analyze_results.py .
```

### 批量计算
```bash
# 1. 创建模板
python scripts/batch_vasp.py --create-template

# 2. 编辑模板 (可选)
vim vasp_template.json

# 3. 批量设置
python scripts/batch_vasp.py structures/ --output-dir calculations

# 4. 批量提交
cd calculations
./submit_all.sh

# 5. 批量分析
for dir in */; do
    python ../scripts/analyze_results.py "$dir"
done
```

## 💡 使用提示

1. **POTCAR文件**: 这些脚本不会自动生成POTCAR文件，需要手动添加或指定POTCAR库路径。

2. **集群适配**: 根据你的集群环境修改作业脚本参数 (队列名称、模块名称等)。

3. **路径问题**: 如果从其他目录运行脚本，需要调整Python路径或使用绝对路径。

4. **权限设置**: 生成的submit.sh脚本会自动设置执行权限。

## 🔧 自定义扩展

这些脚本都是基于WVasp类库构建的，你可以:

1. **修改参数**: 直接编辑脚本中的默认参数
2. **添加功能**: 使用WVasp类库添加新的分析或设置功能
3. **创建新脚本**: 参考现有脚本创建适合你工作流的新工具

## 📚 相关文档

- [WVasp类库文档](../wvasp/)
- [示例脚本](../examples/)
- [测试用例](../tests/)