"""
WVasp配置管理模块

管理环境变量、默认设置和用户配置。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import yaml


@dataclass
class WVaspConfig:
    """WVasp配置类"""
    
    # VASP相关路径
    vasp_executable: str = "vasp_std"
    potcar_path: Optional[str] = None
    vasp_pp_path: Optional[str] = None  # VASP伪势库路径
    
    # 默认计算参数
    default_kpoints: list = field(default_factory=lambda: [4, 4, 4])
    default_encut: float = 500.0
    default_ediff: float = 1e-5
    default_functional: str = "PBE"
    
    # 作业调度器设置
    job_scheduler: str = "slurm"  # slurm, pbs, local
    default_nodes: int = 1
    default_ntasks_per_node: int = 24
    default_memory: str = "32G"
    default_time: str = "24:00:00"
    default_partition: str = "normal"
    
    # 输出设置
    verbose: bool = True
    color_output: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量读取设置
        self._load_from_environment()
        
        # 尝试从配置文件读取
        self._load_from_config_file()
    
    def _load_from_environment(self):
        """从环境变量加载配置"""
        # VASP相关环境变量
        if os.environ.get('VASP_EXECUTABLE'):
            self.vasp_executable = os.environ['VASP_EXECUTABLE']
        
        if os.environ.get('VASP_POTCAR_PATH'):
            self.potcar_path = os.environ['VASP_POTCAR_PATH']
        
        if os.environ.get('VASP_PP_PATH'):
            self.vasp_pp_path = os.environ['VASP_PP_PATH']
        
        # 如果没有设置POTCAR路径，尝试常见位置
        if not self.potcar_path:
            self.potcar_path = self._find_potcar_path()
        
        # 计算参数
        if os.environ.get('WVASP_DEFAULT_ENCUT'):
            try:
                self.default_encut = float(os.environ['WVASP_DEFAULT_ENCUT'])
            except ValueError:
                pass
        
        if os.environ.get('WVASP_DEFAULT_FUNCTIONAL'):
            self.default_functional = os.environ['WVASP_DEFAULT_FUNCTIONAL']
        
        # 作业调度器设置
        if os.environ.get('WVASP_JOB_SCHEDULER'):
            self.job_scheduler = os.environ['WVASP_JOB_SCHEDULER']
        
        if os.environ.get('WVASP_DEFAULT_PARTITION'):
            self.default_partition = os.environ['WVASP_DEFAULT_PARTITION']
    
    def _find_potcar_path(self) -> Optional[str]:
        """尝试找到POTCAR路径"""
        common_paths = [
            "/opt/vasp/potcar",
            "/usr/local/vasp/potcar", 
            "/home/vasp/potcar",
            "~/vasp/potcar",
            "./potcar"
        ]
        
        for path_str in common_paths:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_dir():
                return str(path)
        
        return None
    
    def _load_from_config_file(self):
        """从配置文件加载设置"""
        config_paths = [
            Path.home() / ".wvasp" / "config.yaml",
            Path.home() / ".wvasp.yaml",
            Path.cwd() / "wvasp.yaml",
            Path.cwd() / ".wvasp.yaml"
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    if config_data:
                        self._update_from_dict(config_data)
                    break
                except Exception as e:
                    if self.verbose:
                        print(f"警告: 无法读取配置文件 {config_path}: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def save_config(self, config_path: Optional[Path] = None):
        """保存配置到文件"""
        if config_path is None:
            config_path = Path.home() / ".wvasp" / "config.yaml"
        
        # 创建配置目录
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 准备配置数据
        config_data = {
            'vasp_executable': self.vasp_executable,
            'potcar_path': self.potcar_path,
            'vasp_pp_path': self.vasp_pp_path,
            'default_kpoints': self.default_kpoints,
            'default_encut': self.default_encut,
            'default_ediff': self.default_ediff,
            'default_functional': self.default_functional,
            'job_scheduler': self.job_scheduler,
            'default_nodes': self.default_nodes,
            'default_ntasks_per_node': self.default_ntasks_per_node,
            'default_memory': self.default_memory,
            'default_time': self.default_time,
            'default_partition': self.default_partition,
            'verbose': self.verbose,
            'color_output': self.color_output
        }
        
        # 写入配置文件
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        if self.verbose:
            print(f"配置已保存到: {config_path}")
    
    def get_potcar_path(self) -> Optional[Path]:
        """获取POTCAR路径"""
        if self.potcar_path:
            path = Path(self.potcar_path)
            if path.exists():
                return path
        return None
    
    def validate_environment(self) -> Dict[str, bool]:
        """验证环境配置"""
        status = {}
        
        # 检查VASP可执行文件
        status['vasp_executable'] = self._check_executable(self.vasp_executable)
        
        # 检查POTCAR路径
        potcar_path = self.get_potcar_path()
        status['potcar_path'] = potcar_path is not None and potcar_path.exists()
        
        # 检查常见元素的POTCAR
        if status['potcar_path']:
            common_elements = ['H', 'C', 'N', 'O', 'Fe', 'Ni', 'Cu']
            status['common_potcars'] = self._check_potcars(potcar_path, common_elements)
        else:
            status['common_potcars'] = False
        
        return status
    
    def _check_executable(self, executable: str) -> bool:
        """检查可执行文件是否存在"""
        import shutil
        return shutil.which(executable) is not None
    
    def _check_potcars(self, potcar_path: Path, elements: list) -> bool:
        """检查POTCAR文件是否存在"""
        for element in elements:
            element_dir = potcar_path / element
            if not element_dir.exists():
                return False
            
            potcar_file = element_dir / "POTCAR"
            if not potcar_file.exists():
                return False
        
        return True
    
    def print_status(self):
        """打印配置状态"""
        print("WVasp配置状态:")
        print("=" * 50)
        
        # VASP设置
        print(f"VASP可执行文件: {self.vasp_executable}")
        print(f"POTCAR路径: {self.potcar_path or '未设置'}")
        print(f"默认泛函: {self.default_functional}")
        print(f"默认截断能: {self.default_encut} eV")
        print(f"默认K点网格: {' '.join(map(str, self.default_kpoints))}")
        
        # 作业调度器设置
        print(f"\n作业调度器: {self.job_scheduler}")
        print(f"默认节点数: {self.default_nodes}")
        print(f"默认核心数: {self.default_ntasks_per_node}")
        print(f"默认内存: {self.default_memory}")
        print(f"默认时间: {self.default_time}")
        print(f"默认分区: {self.default_partition}")
        
        # 环境验证
        print("\n环境验证:")
        status = self.validate_environment()
        for key, value in status.items():
            status_str = "✅" if value else "❌"
            print(f"  {key}: {status_str}")


# 全局配置实例
_global_config = None


def get_config() -> WVaspConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = WVaspConfig()
    return _global_config


def reload_config():
    """重新加载配置"""
    global _global_config
    _global_config = WVaspConfig()
    return _global_config
