"""
基础任务类

定义VASP计算任务的抽象基类和通用接口。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..base import Structure
from ..io import INCAR, KPOINTS, POSCAR, POTCAR


class TaskStatus(Enum):
    """任务状态枚举"""
    CREATED = "created"
    PREPARED = "prepared"
    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskConfig:
    """任务配置基类"""
    name: str
    work_dir: Path
    structure: Structure
    potcar_dir: Optional[Path] = None
    # 作业脚本配置
    generate_job_script: bool = True
    # 作业调度器配置 - 从WVaspConfig获取默认值
    job_scheduler: Optional[str] = None
    nodes: Optional[int] = None
    ntasks_per_node: Optional[int] = None
    memory: Optional[str] = None
    time: Optional[str] = None
    partition: Optional[str] = None
    vasp_executable: Optional[str] = None
    
    def __post_init__(self):
        self.work_dir = Path(self.work_dir)
        if self.potcar_dir:
            self.potcar_dir = Path(self.potcar_dir)


class BaseTask(ABC):
    """
    VASP计算任务基类
    
    定义所有VASP计算任务的通用接口和行为。
    """
    
    def __init__(self, config: TaskConfig):
        """
        初始化任务
        
        Args:
            config: 任务配置
        """
        self.config = config
        self.status = TaskStatus.CREATED
        
        # 从WVaspConfig获取默认值
        self._apply_default_config()
        
        # 初始化VASP文件对象
        self.incar = INCAR()
        self.kpoints = KPOINTS()
        self.poscar = POSCAR()
        self.potcar = None
        self.results = {}
        self.errors = []
    
    def _apply_default_config(self):
        """从WVaspConfig应用默认配置"""
        from ...utils.config import get_config
        
        wvasp_config = get_config()
        
        # 应用默认的作业调度器配置
        if self.config.job_scheduler is None:
            self.config.job_scheduler = wvasp_config.job_scheduler
        if self.config.nodes is None:
            self.config.nodes = wvasp_config.default_nodes
        if self.config.ntasks_per_node is None:
            self.config.ntasks_per_node = wvasp_config.default_ntasks_per_node
        if self.config.memory is None:
            self.config.memory = wvasp_config.default_memory
        if self.config.time is None:
            self.config.time = wvasp_config.default_time
        if self.config.partition is None:
            self.config.partition = wvasp_config.default_partition
        if self.config.vasp_executable is None:
            self.config.vasp_executable = wvasp_config.vasp_executable
    
    @abstractmethod
    def setup_incar(self) -> None:
        """设置INCAR参数"""
        pass
    
    @abstractmethod
    def setup_kpoints(self) -> None:
        """设置KPOINTS"""
        pass
    
    def setup_poscar(self) -> None:
        """设置POSCAR"""
        self.poscar.structure = self.config.structure
    
    def setup_potcar(self) -> None:
        """设置POTCAR"""
        if self.config.potcar_dir:
            elements = list(self.config.structure.composition.keys())
            self.potcar = POTCAR.create_from_elements(elements, self.config.potcar_dir)
    
    def setup_job_script(self) -> None:
        """设置作业脚本"""
        if self.config.job_scheduler.lower() == "slurm":
            script_content = self._generate_slurm_script()
            script_filename = "submit.sh"
        elif self.config.job_scheduler.lower() == "pbs":
            script_content = self._generate_pbs_script()
            script_filename = "submit.pbs"
        else:
            raise ValueError(f"不支持的作业调度器: {self.config.job_scheduler}")
        
        # 写入作业脚本
        script_path = self.config.work_dir / script_filename
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 设置执行权限
        script_path.chmod(0o755)
    
    def _generate_slurm_script(self) -> str:
        """生成SLURM作业脚本"""
        total_cores = self.config.nodes * self.config.ntasks_per_node
        
        script_content = f"""#!/bin/bash
#SBATCH --job-name={self.config.name}
#SBATCH --nodes={self.config.nodes}
#SBATCH --ntasks-per-node={self.config.ntasks_per_node}
#SBATCH --mem={self.config.memory}
#SBATCH --time={self.config.time}
#SBATCH --partition={self.config.partition}
#SBATCH --output=vasp_%j.out
#SBATCH --error=vasp_%j.err

# 环境设置
set -e

# 作业信息
echo "作业开始时间: $(date)"
echo "节点信息: $SLURM_JOB_NODELIST"
echo "作业ID: $SLURM_JOB_ID"
echo "工作目录: $(pwd)"

# 检查输入文件
required_files=("POSCAR" "INCAR" "KPOINTS" "POTCAR")
for file in "${{required_files[@]}}"; do
    if [[ ! -f "$file" ]]; then
        echo "错误: 缺少必要文件 $file"
        exit 1
    fi
done
echo "所有输入文件检查完毕"

# 运行VASP
echo "使用 {total_cores} 个核心运行VASP"
mpirun -np {total_cores} {self.config.vasp_executable}

# 作业完成
echo "作业完成时间: $(date)"
if [[ -f "OUTCAR" ]]; then
    if grep -q "reached required accuracy" OUTCAR; then
        echo "✅ VASP计算成功收敛"
    else
        echo "⚠️  VASP计算可能未收敛，请检查OUTCAR"
    fi
else
    echo "❌ 未找到OUTCAR文件，计算可能失败"
fi
"""
        return script_content
    
    def _generate_pbs_script(self) -> str:
        """生成PBS作业脚本"""
        total_cores = self.config.nodes * self.config.ntasks_per_node
        
        script_content = f"""#!/bin/bash
#PBS -N {self.config.name}
#PBS -l nodes={self.config.nodes}:ppn={self.config.ntasks_per_node}
#PBS -l mem={self.config.memory}
#PBS -l walltime={self.config.time}
#PBS -q {self.config.partition}
#PBS -o vasp_%j.out
#PBS -e vasp_%j.err

# 切换到工作目录
cd $PBS_O_WORKDIR

# 环境设置
set -e

# 运行VASP
echo "使用 {total_cores} 个核心运行VASP"
mpirun -np {total_cores} {self.config.vasp_executable}
"""
        return script_content
    
    def prepare(self) -> None:
        """
        准备计算文件
        
        创建工作目录并生成所有必要的输入文件。
        """
        try:
            # 创建工作目录
            self.config.work_dir.mkdir(parents=True, exist_ok=True)
            
            # 设置各个文件
            self.setup_poscar()
            self.setup_incar()
            self.setup_kpoints()
            self.setup_potcar()
            
            # 写入文件
            self.poscar.write(self.config.work_dir / "POSCAR")
            self.incar.write(self.config.work_dir / "INCAR")
            self.kpoints.write(self.config.work_dir / "KPOINTS")
            
            if self.potcar:
                self.potcar.write(self.config.work_dir / "POTCAR")
            
            # 生成作业脚本
            if self.config.generate_job_script:
                self.setup_job_script()
            
            self.status = TaskStatus.PREPARED
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.errors.append(f"准备阶段失败: {e}")
            raise
    
    def validate(self) -> List[str]:
        """
        验证任务设置
        
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必要文件
        required_files = ["POSCAR", "INCAR", "KPOINTS"]
        for filename in required_files:
            filepath = self.config.work_dir / filename
            if not filepath.exists():
                errors.append(f"缺少文件: {filename}")
        
        # 检查POTCAR
        if not self.potcar and not (self.config.work_dir / "POTCAR").exists():
            errors.append("缺少POTCAR文件")
        
        return errors
    
    @abstractmethod
    def check_results(self) -> Dict[str, Any]:
        """
        检查计算结果
        
        Returns:
            结果检查字典
        """
        pass
    
    def get_status(self) -> TaskStatus:
        """获取任务状态"""
        return self.status
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取任务摘要
        
        Returns:
            任务摘要信息
        """
        return {
            "name": self.config.name,
            "status": self.status.value,
            "work_dir": str(self.config.work_dir),
            "structure_formula": self.config.structure.formula,
            "errors": self.errors,
            "results": self.results
        }