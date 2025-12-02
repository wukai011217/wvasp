"""
VASP参数配置管理器

提供参数验证、配置加载和模板管理功能
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json

from ..io import INCAR, KPOINTS, POTCAR
from ...utils.constants import (ALL_PARAMS, CALCULATION_TEMPLATES, DFT_PLUS_U_DATABASE, 
                                DEFAULT_MAGNETIC_MOMENTS, KPOINTS_TEMPLATES, POTCAR_TEMPLATES,
                                SLURM_TEMPLATES, SLURM_SCRIPT_TEMPLATE, OPTIMIZATION_PARAMS, MD_PARAMS,
                                DOS_PARAMS, NEB_PARAMS, PLUS_U_PARAMS, OUTPUT_PARAMS, PARALLEL_PARAMS, 
                                HYBRID_PARAMS, BASIC_PARAMS, ELECTRONIC_PARAMS)
from ...utils.errors import ParameterError
from ...utils.config import get_config
from .magnetic import MagneticMomentManager


class VASPParameterValidator:
    """VASP参数验证器"""
    
    # 所有参数合并
    ALL_PARAMS = {}
    ALL_PARAMS.update(BASIC_PARAMS)
    ALL_PARAMS.update(ELECTRONIC_PARAMS)
    ALL_PARAMS.update(OPTIMIZATION_PARAMS)
    ALL_PARAMS.update(MD_PARAMS)
    ALL_PARAMS.update(DOS_PARAMS)
    ALL_PARAMS.update(NEB_PARAMS)
    ALL_PARAMS.update(PLUS_U_PARAMS)
    ALL_PARAMS.update(OUTPUT_PARAMS)
    ALL_PARAMS.update(PARALLEL_PARAMS)
    ALL_PARAMS.update(HYBRID_PARAMS)
    
    @classmethod
    def validate_parameter(cls, name: str, value) -> bool:
        """验证参数值是否有效"""
        if name not in cls.ALL_PARAMS:
            return False
        
        param_def = cls.ALL_PARAMS[name]
        param_type = param_def['type']
        
        # 检查类型
        if isinstance(param_type, list):
            if not any(isinstance(value, t) for t in param_type):
                return False
        else:
            if not isinstance(value, param_type):
                return False
        
        # 检查值范围
        if 'values' in param_def:
            if value not in param_def['values']:
                return False
        
        if 'min' in param_def and isinstance(value, (int, float)):
            if value < param_def['min']:
                return False
        
        if 'max' in param_def and isinstance(value, (int, float)):
            if value > param_def['max']:
                return False
        
        return True
    
    @classmethod
    def get_default(cls, name: str):
        """获取参数默认值"""
        if name in cls.ALL_PARAMS:
            return cls.ALL_PARAMS[name].get('default')
        return None
    
    @classmethod
    def get_parameter_info(cls, name: str) -> dict:
        """获取参数信息"""
        return cls.ALL_PARAMS.get(name, {})


class ParameterConfig:
    """参数配置类"""
    
    def __init__(self, template: Optional[str] = None, **kwargs):
        """初始化参数配置"""
        self._parameters = {}
        
        # 加载模板
        if template:
            self.load_template(template)
        
        # 设置额外参数
        for key, value in kwargs.items():
            self.set_parameter(key, value)
    
    def load_template(self, template_name: str) -> None:
        """加载参数模板"""
        if template_name not in CALCULATION_TEMPLATES:
            available = list(CALCULATION_TEMPLATES.keys())
            raise ParameterError(f"Unknown template '{template_name}'. Available: {available}")
        
        template_params = CALCULATION_TEMPLATES[template_name].copy()
        self._parameters.update(template_params)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """设置参数"""
        if not VASPParameterValidator.validate_parameter(name, value):
            param_info = VASPParameterValidator.get_parameter_info(name)
            if param_info:
                raise ParameterError(f"Invalid value for {name}: {value}. Expected: {param_info}")
            else:
                # 允许未知参数，但发出警告
                print(f"Warning: Unknown parameter '{name}' with value '{value}'")
        
        self._parameters[name] = value
    
    def get_parameter(self, name: str, default=None):
        """获取参数值"""
        return self._parameters.get(name, default)
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """获取所有参数"""
        return self._parameters.copy()
    
    def update_parameters_from_command_line(self, param_list: List[List[str]]) -> None:
        """
        从命令行参数列表更新参数
        
        Args:
            param_list: 参数列表，格式为 [['PARAM1', 'VALUE1'], ['PARAM2', 'VALUE2'], ...]
        """
        if not param_list:
            return
        
        print(f"更新INCAR参数:")
        
        for param_pair in param_list:
            param_name = param_pair[0].upper()
            param_value_str = param_pair[1]
            
            try:
                # 使用智能类型转换
                param_value = self._smart_convert_parameter_value(param_name, param_value_str)
                
                # 验证参数
                if VASPParameterValidator.validate_parameter(param_name, param_value):
                    self.set_parameter(param_name, param_value)
                    print(f"  ✅ {param_name} = {param_value}")
                else:
                    # 验证失败，使用原始字符串值
                    self.set_parameter(param_name, param_value_str)
                    param_info = VASPParameterValidator.get_parameter_info(param_name)
                    print(f"  ⚠️  {param_name} = {param_value_str} (验证失败，期望: {param_info})")
                    
            except Exception as e:
                # 转换失败，使用原始字符串值
                self.set_parameter(param_name, param_value_str)
                print(f"  ⚠️  {param_name} = {param_value_str} (转换失败: {e})")
    
    def _smart_convert_parameter_value(self, param_name: str, value_str: str):
        """智能转换参数值"""
        from ...utils.constants import ALL_PARAMS
        
        # 如果参数在数据库中，使用类型信息转换
        if param_name in ALL_PARAMS:
            param_info = ALL_PARAMS[param_name]
            return self._convert_by_type_info(value_str, param_info)
        else:
            # 未知参数，使用通用转换
            return self._smart_convert_value(value_str)
    
    def _convert_by_type_info(self, value_str: str, param_info: dict):
        """根据参数信息转换值"""
        param_type = param_info['type']
        
        if param_type == bool or param_type == [bool]:
            return self._convert_bool_value(value_str)
        elif param_type == int or param_type == [int]:
            return int(value_str)
        elif param_type == float or param_type == [float]:
            return float(value_str)
        elif param_type == str or param_type == [str]:
            return value_str
        elif param_type == list or param_type == [list]:
            return self._convert_list_value(value_str)
        elif isinstance(param_type, list) and len(param_type) > 1:
            # 多种类型支持，尝试按顺序转换
            for t in param_type:
                try:
                    if t == bool:
                        return self._convert_bool_value(value_str)
                    elif t == int:
                        return int(value_str)
                    elif t == float:
                        return float(value_str)
                    elif t == str:
                        return value_str
                except:
                    continue
            return value_str
        else:
            return self._smart_convert_value(value_str)
    
    def _convert_bool_value(self, value_str: str) -> bool:
        """转换布尔值"""
        if value_str.upper() in ['TRUE', 'T', '.TRUE.', '1', 'YES', 'ON']:
            return True
        elif value_str.upper() in ['FALSE', 'F', '.FALSE.', '0', 'NO', 'OFF']:
            return False
        else:
            raise ValueError(f"无法将 '{value_str}' 转换为布尔值")
    
    def _convert_list_value(self, value_str: str) -> list:
        """转换列表值"""
        if ',' in value_str:
            return [self._smart_convert_value(v.strip()) for v in value_str.split(',')]
        else:
            return [self._smart_convert_value(v) for v in value_str.split()]
    
    def _smart_convert_value(self, value_str: str):
        """通用智能转换"""
        value_str = value_str.strip()
        
        # 尝试布尔值
        if value_str.upper() in ['TRUE', 'T', '.TRUE.']:
            return True
        elif value_str.upper() in ['FALSE', 'F', '.FALSE.']:
            return False
        
        # 尝试整数
        try:
            if '.' not in value_str and 'e' not in value_str.lower():
                return int(value_str)
        except ValueError:
            pass
        
        # 尝试浮点数
        try:
            return float(value_str)
        except ValueError:
            pass
        
        # 返回字符串
        return value_str
    
    def load_from_incar_file(self, incar_file_path: Path) -> None:
        """
        从INCAR文件加载参数
        
        Args:
            incar_file_path: INCAR文件路径
        """
        from ..io import INCAR
        
        if not incar_file_path.exists():
            raise FileNotFoundError(f"INCAR文件不存在: {incar_file_path}")
        
        incar = INCAR(incar_file_path)
        existing_params = incar.read()
        
        print(f"从INCAR文件加载参数: {incar_file_path}")
        
        # 加载现有参数，处理格式问题
        for param, value in existing_params.items():
            # 对于字符串类型的参数，如果是列表则合并为字符串
            if isinstance(value, list) and param in ['SYSTEM']:
                value = ' '.join(str(v) for v in value)
            
            # 直接设置参数，跳过验证以避免格式冲突
            self._parameters[param] = value
        
        print(f"  ✅ 加载了 {len(existing_params)} 个参数")
    
    def setup_dft_plus_u(self, elements: List[str], u_values: Optional[Dict[str, float]] = None) -> None:
        """
        设置DFT+U参数
        
        Args:
            elements: 元素列表，必须按照POSCAR文件中的元素顺序排列
            u_values: 可选的自定义U值字典，键为元素符号，值为U值
        
        Note:
            elements列表的顺序必须与POSCAR文件中元素的顺序完全一致，
            因为LDAUL、LDAUU、LDAUJ参数的顺序对应POSCAR中的元素顺序
        """
        if not elements:
            return
        
        # 启用DFT+U
        self.set_parameter('LDAU', True)
        self.set_parameter('LDAUTYPE', 2)
        
        # 设置L量子数和U值，顺序必须与POSCAR中元素顺序一致
        ldaul = []
        ldauu = []
        ldauj = []
        
        # 按照传入的elements顺序（应与POSCAR顺序一致）设置参数
        for element in elements:
            if element in DFT_PLUS_U_DATABASE:
                db_entry = DFT_PLUS_U_DATABASE[element]
                ldaul.append(db_entry['L'])
                
                # 使用用户提供的U值或数据库默认值
                if u_values and element in u_values:
                    ldauu.append(u_values[element])
                else:
                    ldauu.append(db_entry['U'])
                
                ldauj.append(db_entry.get('J', 0.0))
            else:
                # 未知元素，使用默认值（不启用DFT+U）
                ldaul.append(-1)
                ldauu.append(0.0)
                ldauj.append(0.0)
        
        self.set_parameter('LDAUL', ldaul)
        self.set_parameter('LDAUU', ldauu)
        self.set_parameter('LDAUJ', ldauj)
        
        # 添加调试信息
        print(f"DFT+U设置:")
        print(f"  元素顺序: {elements}")
        print(f"  LDAUL: {ldaul}")
        print(f"  LDAUU: {ldauu}")
        print(f"  LDAUJ: {ldauj}")
    
    def auto_setup_magnetism(self, structure) -> None:
        """自动设置磁性参数"""
        magnetic_manager = MagneticMomentManager()
        
        # 检查是否包含磁性元素
        elements = [atom.element for atom in structure.atoms]
        if magnetic_manager.has_magnetic_elements(elements):
            # 启用自旋极化
            self.set_parameter('ISPIN', 2)
            
            # 设置初始磁矩
            magnetic_moments = magnetic_manager.get_auto_magnetic_moments(structure)
            if magnetic_moments:
                self.set_parameter('MAGMOM', magnetic_moments)
    
    def to_incar_format(self) -> Dict[str, str]:
        """转换为INCAR格式"""
        incar_dict = {}
        
        for name, value in self._parameters.items():
            if value is None:
                continue
            
            # 格式化不同类型的值
            if isinstance(value, bool):
                incar_dict[name] = '.TRUE.' if value else '.FALSE.'
            elif isinstance(value, list):
                # 处理列表类型参数
                if all(isinstance(x, (int, float)) for x in value):
                    incar_dict[name] = ' '.join(map(str, value))
                else:
                    incar_dict[name] = ' '.join(str(x) for x in value)
            else:
                incar_dict[name] = str(value)
        
        return incar_dict
    
    def validate_all(self) -> List[str]:
        """验证所有参数"""
        errors = []
        
        for name, value in self._parameters.items():
            if not VASPParameterValidator.validate_parameter(name, value):
                errors.append(f"Invalid parameter {name}={value}")
        
        return errors


class ParameterManager:
    """参数管理器"""
    
    def __init__(self):
        self.templates = CALCULATION_TEMPLATES.copy()
    
    def create_config(self, template: str, **kwargs) -> ParameterConfig:
        """创建参数配置"""
        return ParameterConfig(template=template, **kwargs)
    
    def get_available_templates(self) -> List[str]:
        """获取可用模板列表"""
        return list(self.templates.keys())
    
    def add_custom_template(self, name: str, parameters: Dict[str, Any]) -> None:
        """添加自定义模板"""
        self.templates[name] = parameters
    
    def save_template(self, name: str, config: ParameterConfig, filepath: Path) -> None:
        """保存模板到文件"""
        template_data = {
            'name': name,
            'parameters': config.get_all_parameters()
        }
        
        with open(filepath, 'w') as f:
            json.dump(template_data, f, indent=2)
    
    def load_template_from_file(self, filepath: Path) -> Dict[str, Any]:
        """从文件加载模板"""
        with open(filepath, 'r') as f:
            template_data = json.load(f)
        
        return template_data.get('parameters', {})


class KPointsConfig:
    """KPOINTS配置管理器"""
    
    def __init__(self, template: str = None, method: str = "gamma", grid: List[int] = None, shift: List[float] = None):
        """
        初始化KPOINTS配置
        
        Args:
            template: 模板名称 (如 'gamma_medium', 'slab_2d' 等)
            method: K点生成方法 ("gamma" 或 "monkhorst")
            grid: K点网格 [nx, ny, nz]
            shift: K点偏移 [sx, sy, sz]
        """
        if template and template in KPOINTS_TEMPLATES:
            template_config = KPOINTS_TEMPLATES[template]
            self.method = template_config['method']
            self.grid = template_config['grid']
            self.shift = template_config['shift']
            print(f"✅ 使用KPOINTS模板: {template} - {template_config['description']}")
        else:
            self.method = method
            self.grid = grid or [4, 4, 4]
            self.shift = shift or [0.0, 0.0, 0.0]
    
    def update_from_command_line(self, grid: List[int] = None, method: str = None, shift: List[float] = None) -> None:
        """从命令行参数更新配置"""
        if grid:
            self.grid = grid
            print(f"  ✅ K点网格: {self.grid}")
        
        if method:
            self.method = method
            print(f"  ✅ K点方法: {self.method}")
        
        if shift:
            self.shift = shift
            print(f"  ✅ K点偏移: {self.shift}")
    
    def generate_kpoints(self, output_path: Path) -> None:
        """生成KPOINTS文件"""
        from ..io import KPOINTS
        
        if self.method == "gamma":
            kpoints = KPOINTS.create_gamma_centered(self.grid)
        else:
            kpoints = KPOINTS.create_monkhorst_pack(self.grid, self.shift)
        
        kpoints.write(output_path)
        print(f"✅ KPOINTS文件已生成: {output_path}")


class PotcarConfig:
    """POTCAR配置管理器"""
    
    def __init__(self, template: str = None, elements: List[str] = None, functional: str = "PBE"):
        """
        初始化POTCAR配置
        
        Args:
            template: 模板名称 (如 'PBE_standard', 'PBE_hard' 等)
            elements: 元素列表
            functional: 泛函类型
        """
        if template and template in POTCAR_TEMPLATES:
            template_config = POTCAR_TEMPLATES[template]
            self.functional = template_config['functional']
            self.suffix = template_config.get('suffix', '')
            print(f"✅ 使用POTCAR模板: {template} - {template_config['description']}")
        else:
            self.functional = functional
            self.suffix = ''
        
        self.elements = elements or []
    
    def update_from_command_line(self, elements: List[str] = None, functional: str = None) -> None:
        """从命令行参数更新配置"""
        if elements:
            self.elements = elements
            print(f"  ✅ 元素列表: {self.elements}")
        
        if functional:
            self.functional = functional
            print(f"  ✅ 泛函类型: {self.functional}")
    
    def update_from_poscar(self, poscar_path: Path) -> None:
        """从POSCAR文件获取元素"""
        from ..io import POSCAR
        
        poscar = POSCAR(poscar_path)
        structure = poscar.read()
        self.elements = structure.get_ordered_elements()
        print(f"  ✅ 从POSCAR获取元素: {self.elements}")
    
    def generate_potcar(self, output_path: Path) -> None:
        """生成POTCAR文件"""
        from ..io import POTCAR
        
        if not self.elements:
            raise ValueError("未指定元素列表")
        
        config = get_config()
        if not config.potcar_path or not Path(config.potcar_path).exists():
            raise FileNotFoundError("未配置POTCAR路径或路径不存在")
        
        potcar = POTCAR.create_from_elements(
            elements=self.elements,
            potcar_dir=Path(config.potcar_path),
            functional=self.functional
        )
        
        potcar.write(output_path)
        print(f"✅ POTCAR文件已生成: {output_path}")


class VASPFileManager:
    """VASP文件统一管理器"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.incar_config = ParameterConfig()
        self.kpoints_config = KPointsConfig()
        self.potcar_config = PotcarConfig()
    
    def setup_from_command_line_args(self, args) -> None:
        """从命令行参数统一设置所有配置"""
        print("配置VASP文件参数:")
        
        # 设置INCAR参数
        if hasattr(args, 'template') and args.template:
            self.incar_config = ParameterConfig(args.template)
            print(f"  ✅ 使用INCAR模板: {args.template}")
        
        if hasattr(args, 'encut') and args.encut:
            self.incar_config.set_parameter('ENCUT', args.encut)
            print(f"  ✅ ENCUT: {args.encut}")
        
        if hasattr(args, 'incar') and args.incar:
            self.incar_config.update_parameters_from_command_line(args.incar)
        
        # 设置KPOINTS参数
        if hasattr(args, 'kpoints') and args.kpoints:
            self.kpoints_config.update_from_command_line(grid=args.kpoints)
        
        if hasattr(args, 'method') and args.method:
            self.kpoints_config.update_from_command_line(method=args.method)
        
        if hasattr(args, 'shift') and args.shift:
            self.kpoints_config.update_from_command_line(shift=args.shift)
        
        # 设置POTCAR参数
        if hasattr(args, 'elements') and args.elements:
            self.potcar_config.update_from_command_line(elements=args.elements)
        
        if hasattr(args, 'functional') and args.functional:
            self.potcar_config.update_from_command_line(functional=args.functional)
    
    def generate_all_files(self, output_dir: Path, poscar_path: Path = None) -> None:
        """生成所有VASP文件"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成INCAR
        from ..io import INCAR
        incar = INCAR()
        for param, value in self.incar_config.get_all_parameters().items():
            incar.set_parameter(param, value)
        incar.write(output_dir / "INCAR")
        print(f"生成: {output_dir / 'INCAR'}")
        
        # 生成KPOINTS
        self.kpoints_config.generate_kpoints(output_dir / "KPOINTS")
        
        # 生成POTCAR (如果有POSCAR文件，自动获取元素)
        if poscar_path and poscar_path.exists():
            if not self.potcar_config.elements:
                self.potcar_config.update_from_poscar(poscar_path)
            
            try:
                self.potcar_config.generate_potcar(output_dir / "POTCAR")
            except Exception as e:
                print(f"⚠️  POTCAR生成失败: {e}")
        
        print(f"✅ 所有文件已生成到: {output_dir}")


class SlurmConfig:
    """SLURM作业脚本配置管理器"""
    
    def __init__(self, template: str = None, **kwargs):
        """
        初始化SLURM配置
        
        Args:
            template: 模板名称 (如 'standard', 'large_system', 'gpu_accelerated' 等)
            **kwargs: 其他配置参数
        """
        if template and template in SLURM_TEMPLATES:
            template_config = SLURM_TEMPLATES[template]
            self.job_name = template_config['job_name']
            self.nodes = template_config['nodes']
            self.ntasks_per_node = template_config['ntasks_per_node']
            self.memory = template_config['memory']
            self.time = template_config['time']
            self.partition = template_config['partition']
            self.vasp_cmd = template_config['vasp_cmd']
            self.modules = template_config['modules']
            self.extra_options = template_config.get('extra_options', [])
            print(f"✅ 使用SLURM模板: {template} - {template_config['description']}")
        else:
            # 默认配置
            self.job_name = kwargs.get('job_name', 'vasp_calc')
            self.nodes = kwargs.get('nodes', 1)
            self.ntasks_per_node = kwargs.get('ntasks_per_node', 24)
            self.memory = kwargs.get('memory', '32G')
            self.time = kwargs.get('time', '12:00:00')
            self.partition = kwargs.get('partition', 'normal')
            self.vasp_cmd = kwargs.get('vasp_cmd', 'vasp_std')
            self.modules = kwargs.get('modules', ['intel/2021', 'vasp/6.3.0'])
            self.extra_options = kwargs.get('extra_options', [])
    
    def update_from_command_line(self, **kwargs) -> None:
        """从命令行参数更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                print(f"  ✅ {key}: {value}")
    
    def generate_slurm_script(self, output_path: Path) -> None:
        """生成SLURM脚本文件"""
        # 准备模块加载命令
        module_commands = '\n'.join([f'module load {module}' for module in self.modules])
        
        # 准备额外选项
        extra_options = '\n'.join(self.extra_options) if self.extra_options else ''
        
        # 格式化脚本内容
        script_content = SLURM_SCRIPT_TEMPLATE.format(
            job_name=self.job_name,
            nodes=self.nodes,
            ntasks_per_node=self.ntasks_per_node,
            memory=self.memory,
            time=self.time,
            partition=self.partition,
            extra_options=extra_options,
            module_commands=module_commands,
            vasp_cmd=self.vasp_cmd
        )
        
        # 写入文件
        with open(output_path, 'w') as f:
            f.write(script_content)
        output_path.chmod(0o755)
        
        print(f"✅ SLURM脚本已生成: {output_path}")
        print(f"   作业名称: {self.job_name}")
        print(f"   节点配置: {self.nodes}节点 × {self.ntasks_per_node}核")
        print(f"   内存: {self.memory}")
        print(f"   时间: {self.time}")
        print(f"   队列: {self.partition}")
