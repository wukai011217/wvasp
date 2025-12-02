# WVasp 环境配置指南

## 🚀 快速开始

WVasp 提供了完整的配置管理系统，帮助您轻松设置和管理 VASP 计算环境。

### 1. 运行环境设置向导

```bash
cd /path/to/wvasp
python setup_environment.py
```

这将启动交互式配置向导，帮助您设置：
- POTCAR 文件路径
- VASP 可执行文件
- 默认计算参数
- 作业调度器设置

### 2. 检查当前环境

```bash
# 使用设置脚本检查
python setup_environment.py check

# 或使用 CLI 命令
python -m wvasp config show
```

### 3. 验证环境配置

```bash
python -m wvasp config validate
```

## 📋 环境变量

WVasp 支持以下环境变量：

### VASP 相关
- `VASP_EXECUTABLE`: VASP 可执行文件名 (默认: vasp_std)
- `VASP_POTCAR_PATH`: POTCAR 文件库路径
- `VASP_PP_PATH`: VASP 伪势库路径 (别名)

### WVasp 默认设置
- `WVASP_DEFAULT_ENCUT`: 默认截断能 (默认: 500.0)
- `WVASP_DEFAULT_FUNCTIONAL`: 默认泛函 (默认: PBE)
- `WVASP_JOB_SCHEDULER`: 作业调度器 (默认: slurm)
- `WVASP_DEFAULT_PARTITION`: 默认分区 (默认: normal)

## 🔧 配置文件

WVasp 会在以下位置查找配置文件：

1. `~/.wvasp/config.yaml`
2. `~/.wvasp.yaml`
3. `./wvasp.yaml`
4. `./.wvasp.yaml`

### 配置文件示例

```yaml
# WVasp 配置文件
vasp_executable: "vasp_std"
potcar_path: "/opt/vasp/potcar"
default_encut: 500.0
default_ediff: 1.0e-5
default_functional: "PBE"
default_kpoints: [4, 4, 4]

# 作业调度器设置
job_scheduler: "slurm"
default_nodes: 1
default_ntasks_per_node: 24
default_memory: "32G"
default_time: "24:00:00"
default_partition: "normal"

# 输出设置
verbose: true
color_output: true
```

## 🛠️ CLI 配置管理

### 显示当前配置
```bash
wvasp config show
```

### 设置配置项
```bash
# 设置 POTCAR 路径
wvasp config set potcar_path "/path/to/potcar"

# 设置默认截断能
wvasp config set default_encut 600.0

# 设置默认 K 点网格
wvasp config set default_kpoints "6 6 6"
```

### 验证环境
```bash
wvasp config validate
```

## 📁 POTCAR 设置

POTCAR 文件是 VASP 计算的必需文件。WVasp 支持多种设置方式：

### 方法 1: 环境变量
```bash
export VASP_POTCAR_PATH="/path/to/potcar"
```

### 方法 2: 配置文件
```yaml
potcar_path: "/path/to/potcar"
```

### 方法 3: CLI 设置
```bash
wvasp config set potcar_path "/path/to/potcar"
```

### POTCAR 目录结构
```
potcar/
├── H/
│   └── POTCAR
├── C/
│   └── POTCAR
├── N/
│   └── POTCAR
├── O/
│   └── POTCAR
└── ...
```

## 🎯 使用示例

### 1. 完整环境设置
```bash
# 1. 运行设置向导
python setup_environment.py

# 2. 生成环境变量脚本
# 选择 y 生成脚本

# 3. 加载环境变量
source wvasp_env.sh

# 4. 验证配置
wvasp config validate
```

### 2. 快速配置
```bash
# 设置关键配置
wvasp config set potcar_path "/opt/vasp/potcar"
wvasp config set vasp_executable "vasp_std"
wvasp config set default_encut 500.0

# 验证配置
wvasp config validate
```

### 3. 使用配置进行计算
```bash
# 现在 POTCAR 会自动从配置的路径生成
wvasp build POSCAR -t optimization --dft-u -o calculation
```

## 🔍 故障排除

### 问题 1: POTCAR 路径未找到
```
⚠️  未设置POTCAR路径
   生成POTCAR指南文件
   提示: 运行 'python setup_environment.py' 配置环境
```

**解决方案:**
1. 运行 `python setup_environment.py` 设置路径
2. 或使用 `wvasp config set potcar_path "/path/to/potcar"`

### 问题 2: VASP 可执行文件未找到
```
vasp_executable: ❌
```

**解决方案:**
1. 确保 VASP 在 PATH 中
2. 或设置正确的可执行文件名: `wvasp config set vasp_executable "mpirun -np 24 vasp_std"`

### 问题 3: 配置文件权限问题
**解决方案:**
```bash
chmod 644 ~/.wvasp/config.yaml
```

## 📚 高级配置

### 多环境管理
可以为不同的项目使用不同的配置文件：

```bash
# 项目特定配置
cd /path/to/project
echo "potcar_path: /project/specific/potcar" > .wvasp.yaml
```

### 自定义作业脚本
```yaml
job_scheduler: "slurm"
default_nodes: 2
default_ntasks_per_node: 48
default_memory: "64G"
default_time: "48:00:00"
default_partition: "gpu"
```

### 批量设置
```bash
# 使用配置文件批量设置
cat > ~/.wvasp/config.yaml << EOF
potcar_path: "/opt/vasp/potcar"
default_encut: 600.0
default_kpoints: [6, 6, 6]
job_scheduler: "pbs"
EOF
```

## 🎉 完成

配置完成后，您就可以使用 WVasp 的所有功能了：

```bash
# 构建计算
wvasp build POSCAR -t optimization --auto-mag --dft-u

# 修改参数
wvasp modify INCAR --set ENCUT 600

# 查询信息
wvasp info magnetic Fe Co Ni
```

享受使用 WVasp！ 🚀
