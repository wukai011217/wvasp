"""
作业脚本生成器

生成SLURM、PBS等集群作业提交脚本。
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class JobConfig:
    """作业配置类"""
    job_name: str = "vasp_job"
    nodes: int = 1
    ntasks_per_node: int = 24
    cpus_per_task: int = 1
    memory: str = "64G"
    time: str = "24:00:00"
    partition: str = "normal"
    account: Optional[str] = None
    email: Optional[str] = None
    email_type: str = "END,FAIL"
    output_file: str = "vasp_%j.out"
    error_file: str = "vasp_%j.err"
    
    # VASP相关配置
    vasp_executable: str = "vasp_std"
    mpi_command: str = "mpirun"
    additional_modules: List[str] = None
    environment_setup: List[str] = None


class JobScriptGenerator:
    """作业脚本生成器"""
    
    def __init__(self, config: JobConfig):
        """
        初始化作业脚本生成器
        
        Args:
            config: 作业配置
        """
        self.config = config
    
    def generate_slurm_script(self, output_path: Optional[Path] = None) -> str:
        """
        生成SLURM作业脚本
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            脚本内容字符串
        """
        script_lines = []
        
        # SLURM指令
        script_lines.append("#!/bin/bash")
        script_lines.append(f"#SBATCH --job-name={self.config.job_name}")
        script_lines.append(f"#SBATCH --nodes={self.config.nodes}")
        script_lines.append(f"#SBATCH --ntasks-per-node={self.config.ntasks_per_node}")
        script_lines.append(f"#SBATCH --cpus-per-task={self.config.cpus_per_task}")
        script_lines.append(f"#SBATCH --mem={self.config.memory}")
        script_lines.append(f"#SBATCH --time={self.config.time}")
        script_lines.append(f"#SBATCH --partition={self.config.partition}")
        
        if self.config.account:
            script_lines.append(f"#SBATCH --account={self.config.account}")
        
        if self.config.email:
            script_lines.append(f"#SBATCH --mail-user={self.config.email}")
            script_lines.append(f"#SBATCH --mail-type={self.config.email_type}")
        
        script_lines.append(f"#SBATCH --output={self.config.output_file}")
        script_lines.append(f"#SBATCH --error={self.config.error_file}")
        script_lines.append("")
        
        # 环境设置
        script_lines.append("# 环境设置")
        script_lines.append("set -e  # 遇到错误立即退出")
        script_lines.append("")
        
        # 加载模块
        if self.config.additional_modules:
            script_lines.append("# 加载必要模块")
            for module in self.config.additional_modules:
                script_lines.append(f"module load {module}")
            script_lines.append("")
        
        # 环境变量设置
        if self.config.environment_setup:
            script_lines.append("# 环境变量设置")
            for env_cmd in self.config.environment_setup:
                script_lines.append(env_cmd)
            script_lines.append("")
        
        # 作业信息
        script_lines.append("# 作业信息")
        script_lines.append("echo \"作业开始时间: $(date)\"")
        script_lines.append("echo \"节点信息: $SLURM_JOB_NODELIST\"")
        script_lines.append("echo \"作业ID: $SLURM_JOB_ID\"")
        script_lines.append("echo \"工作目录: $(pwd)\"")
        script_lines.append("")
        
        # 检查输入文件
        script_lines.append("# 检查必要的输入文件")
        script_lines.append("required_files=(\"POSCAR\" \"INCAR\" \"KPOINTS\" \"POTCAR\")")
        script_lines.append("for file in \"${required_files[@]}\"; do")
        script_lines.append("    if [[ ! -f \"$file\" ]]; then")
        script_lines.append("        echo \"错误: 缺少必要文件 $file\"")
        script_lines.append("        exit 1")
        script_lines.append("    fi")
        script_lines.append("done")
        script_lines.append("echo \"所有输入文件检查完毕\"")
        script_lines.append("")
        
        # 运行VASP
        total_cores = self.config.nodes * self.config.ntasks_per_node
        script_lines.append("# 运行VASP计算")
        script_lines.append(f"echo \"使用 {total_cores} 个核心运行VASP\"")
        script_lines.append(f"{self.config.mpi_command} -np {total_cores} {self.config.vasp_executable}")
        script_lines.append("")
        
        # 作业完成信息
        script_lines.append("# 作业完成")
        script_lines.append("echo \"作业完成时间: $(date)\"")
        script_lines.append("echo \"检查输出文件...\"")
        script_lines.append("")
        script_lines.append("if [[ -f \"OUTCAR\" ]]; then")
        script_lines.append("    if grep -q \"reached required accuracy\" OUTCAR; then")
        script_lines.append("        echo \"✅ VASP计算成功收敛\"")
        script_lines.append("    else")
        script_lines.append("        echo \"⚠️  VASP计算可能未收敛，请检查OUTCAR\"")
        script_lines.append("    fi")
        script_lines.append("else")
        script_lines.append("    echo \"❌ 未找到OUTCAR文件，计算可能失败\"")
        script_lines.append("fi")
        
        script_content = "\n".join(script_lines)
        
        # 写入文件
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_content)
            # 设置执行权限
            output_path.chmod(0o755)
        
        return script_content
    
    def generate_pbs_script(self, output_path: Optional[Path] = None) -> str:
        """
        生成PBS作业脚本
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            脚本内容字符串
        """
        script_lines = []
        
        # PBS指令
        script_lines.append("#!/bin/bash")
        script_lines.append(f"#PBS -N {self.config.job_name}")
        script_lines.append(f"#PBS -l nodes={self.config.nodes}:ppn={self.config.ntasks_per_node}")
        script_lines.append(f"#PBS -l mem={self.config.memory}")
        script_lines.append(f"#PBS -l walltime={self.config.time}")
        script_lines.append(f"#PBS -q {self.config.partition}")
        
        if self.config.account:
            script_lines.append(f"#PBS -A {self.config.account}")
        
        if self.config.email:
            script_lines.append(f"#PBS -M {self.config.email}")
            script_lines.append("#PBS -m abe")  # abort, begin, end
        
        script_lines.append(f"#PBS -o {self.config.output_file}")
        script_lines.append(f"#PBS -e {self.config.error_file}")
        script_lines.append("")
        
        # 切换到工作目录
        script_lines.append("# 切换到工作目录")
        script_lines.append("cd $PBS_O_WORKDIR")
        script_lines.append("")
        
        # 其余内容与SLURM类似
        script_lines.append("# 环境设置")
        script_lines.append("set -e")
        script_lines.append("")
        
        if self.config.additional_modules:
            script_lines.append("# 加载必要模块")
            for module in self.config.additional_modules:
                script_lines.append(f"module load {module}")
            script_lines.append("")
        
        # 运行VASP
        total_cores = self.config.nodes * self.config.ntasks_per_node
        script_lines.append("# 运行VASP计算")
        script_lines.append(f"echo \"使用 {total_cores} 个核心运行VASP\"")
        script_lines.append(f"{self.config.mpi_command} -np {total_cores} {self.config.vasp_executable}")
        
        script_content = "\n".join(script_lines)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_content)
            output_path.chmod(0o755)
        
        return script_content


class VASPJobManager:
    """VASP作业管理器"""
    
    def __init__(self, work_dir: Path):
        """
        初始化VASP作业管理器
        
        Args:
            work_dir: 工作目录
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_calculation(self, 
                         poscar_content: str,
                         incar_params: Dict[str, Any],
                         kpoints_grid: List[int],
                         elements: List[str],
                         potcar_dir: Path,
                         job_config: JobConfig) -> None:
        """
        设置完整的VASP计算
        
        Args:
            poscar_content: POSCAR文件内容
            incar_params: INCAR参数字典
            kpoints_grid: K点网格
            elements: 元素列表
            potcar_dir: POTCAR库目录
            job_config: 作业配置
        """
        from .io import POSCAR, INCAR, KPOINTS, POTCAR
        
        # 创建POSCAR文件
        poscar_path = self.work_dir / "POSCAR"
        with open(poscar_path, 'w') as f:
            f.write(poscar_content)
        
        # 创建INCAR文件
        incar = INCAR()
        for key, value in incar_params.items():
            incar.set_parameter(key, value)
        incar.write(self.work_dir / "INCAR")
        
        # 创建KPOINTS文件
        kpoints = KPOINTS.create_gamma_centered(kpoints_grid)
        kpoints.write(self.work_dir / "KPOINTS")
        
        # 创建POTCAR文件
        potcar = POTCAR.create_from_elements(elements, potcar_dir)
        potcar.write(self.work_dir / "POTCAR")
        
        # 生成作业脚本
        script_generator = JobScriptGenerator(job_config)
        script_generator.generate_slurm_script(self.work_dir / "submit.sh")
        
        print(f"✅ VASP计算设置完成，工作目录: {self.work_dir}")
        print("📁 生成的文件:")
        print("   - POSCAR: 结构文件")
        print("   - INCAR: 计算参数")
        print("   - KPOINTS: K点设置")
        print("   - POTCAR: 赝势文件")
        print("   - submit.sh: 作业提交脚本")
        print("\n🚀 提交作业命令: sbatch submit.sh")
    
    def check_calculation_status(self) -> Dict[str, Any]:
        """
        检查计算状态
        
        Returns:
            计算状态信息
        """
        status = {
            'input_files_exist': True,
            'calculation_running': False,
            'calculation_completed': False,
            'converged': False,
            'output_files': []
        }
        
        # 检查输入文件
        required_files = ['POSCAR', 'INCAR', 'KPOINTS', 'POTCAR']
        for filename in required_files:
            if not (self.work_dir / filename).exists():
                status['input_files_exist'] = False
                break
        
        # 检查输出文件
        output_files = ['OUTCAR', 'CONTCAR', 'OSZICAR', 'vasprun.xml']
        for filename in output_files:
            if (self.work_dir / filename).exists():
                status['output_files'].append(filename)
        
        # 检查是否完成
        outcar_path = self.work_dir / "OUTCAR"
        if outcar_path.exists():
            status['calculation_completed'] = True
            
            # 检查收敛性
            try:
                with open(outcar_path, 'r') as f:
                    content = f.read()
                    if "reached required accuracy" in content:
                        status['converged'] = True
            except:
                pass
        
        return status
