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
    job_scheduler: str = "slurm"  # slurm 或 pbs
    nodes: int = 1
    ntasks_per_node: int = 24
    memory: str = "32G"
    time: str = "12:00:00"
    partition: str = "normal"
    vasp_executable: str = "vasp_std"
    
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
        self.incar = INCAR()
        self.kpoints = KPOINTS()
        self.poscar = POSCAR()
        self.potcar = None
        self.results = {}
        self.errors = []
    
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
        from .job_management import JobConfig, JobScriptGenerator
        
        # 转换任务配置为作业配置
        job_config = JobConfig(
            job_name=self.config.name,
            nodes=self.config.nodes,
            ntasks_per_node=self.config.ntasks_per_node,
            memory=self.config.memory,
            time=self.config.time,
            partition=self.config.partition,
            vasp_executable=self.config.vasp_executable
        )
        
        # 生成作业脚本
        generator = JobScriptGenerator(job_config)
        
        if self.config.job_scheduler.lower() == "slurm":
            script_content = generator.generate_slurm_script()
            script_filename = "submit.sh"
        elif self.config.job_scheduler.lower() == "pbs":
            script_content = generator.generate_pbs_script()
            script_filename = "submit.pbs"
        else:
            raise ValueError(f"不支持的作业调度器: {self.config.job_scheduler}")
        
        # 写入作业脚本
        script_path = self.config.work_dir / script_filename
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 设置执行权限
        script_path.chmod(0o755)
    
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
    def analyze_results(self) -> Dict[str, Any]:
        """
        分析计算结果
        
        Returns:
            分析结果字典
        """
        pass
    
    def get_status(self) -> TaskStatus:
        """获取任务状态"""
        return self.status
    
    def check_calculation_status(self) -> Dict[str, Any]:
        """
        通用的计算状态检查机制
        
        Returns:
            计算状态信息
        """
        status_info = {
            "files_exist": {},
            "calculation_completed": False,
            "errors_found": [],
            "warnings": []
        }
        
        # 检查基本文件
        required_files = ["OUTCAR", "POSCAR", "INCAR", "KPOINTS"]
        for filename in required_files:
            filepath = self.config.work_dir / filename
            status_info["files_exist"][filename] = filepath.exists()
        
        # 检查OUTCAR中的完成标志
        outcar_path = self.config.work_dir / "OUTCAR"
        if outcar_path.exists():
            try:
                with open(outcar_path, 'r') as f:
                    content = f.read()
                
                # 检查是否正常结束
                if "General timing and accounting informations for this job:" in content:
                    status_info["calculation_completed"] = True
                elif "ZBRENT: fatal error" in content:
                    status_info["errors_found"].append("ZBRENT fatal error")
                elif "VERY BAD NEWS" in content:
                    status_info["errors_found"].append("VERY BAD NEWS found")
                
                # 检查收敛
                if "reached required accuracy" in content:
                    status_info["converged"] = True
                elif "aborting loop" in content:
                    status_info["warnings"].append("Loop aborted - may not be converged")
                
            except Exception as e:
                status_info["errors_found"].append(f"OUTCAR读取失败: {e}")
        
        return status_info
    
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