"""
WVasp主入口

命令行界面和主要功能入口。
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .core.io import POSCAR, INCAR, KPOINTS, POTCAR
from .core.base import Structure
from .core.parameters import ParameterConfig, MagneticMomentManager, VASPParameterValidator, VASPFileManager, SlurmConfig
from .utils.constants import (COLORS, CALCULATION_TEMPLATES, DFT_PLUS_U_DATABASE, ALL_PARAMS,
                             BASIC_PARAMS, ELECTRONIC_PARAMS, OPTIMIZATION_PARAMS, MD_PARAMS,
                             DOS_PARAMS, OUTPUT_PARAMS, PARALLEL_PARAMS, HYBRID_PARAMS,
                             KPOINTS_TEMPLATES, POTCAR_TEMPLATES, SLURM_TEMPLATES)
from .utils.config import get_config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="WVasp - VASP计算工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"WVasp {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # POSCAR命令
    poscar_parser = subparsers.add_parser("poscar", help="POSCAR文件操作")
    poscar_parser.add_argument("file", help="POSCAR文件路径")
    poscar_parser.add_argument("--info", action="store_true", help="显示结构信息")
    poscar_parser.add_argument("--convert", choices=["cart", "frac"], help="转换坐标类型")
    
    # Build命令 - 简化版本，避免重复逻辑
    build_parser = subparsers.add_parser("build", help="构建VASP计算文件")
    build_parser.add_argument("poscar", help="POSCAR文件路径")
    build_parser.add_argument("template", choices=list(CALCULATION_TEMPLATES.keys()), help="计算模板")
    build_parser.add_argument("-o", "--output", default="./vasp_calc", help="输出目录")
    build_parser.add_argument("--encut", type=float, help="平面波截断能")
    build_parser.add_argument("--kpoints", type=int, nargs=3, help="K点网格")
    build_parser.add_argument("--incar", action="append", nargs=2, metavar=("PARAM", "VALUE"), 
                             help="设置任意INCAR参数，格式: --incar PARAM VALUE (可多次使用)")
    build_parser.add_argument("--auto-mag", action="store_true", help="自动设置磁矩")
    build_parser.add_argument("--dft-u", action="store_true", help="启用DFT+U")
    
    # INCAR命令 - 独立INCAR文件操作
    incar_parser = subparsers.add_parser("incar", help="INCAR文件操作")
    incar_parser.add_argument("action", choices=["create", "edit", "validate"], help="操作类型")
    incar_parser.add_argument("-t", "--template", choices=list(CALCULATION_TEMPLATES.keys()), help="使用模板")
    incar_parser.add_argument("-f", "--file", default="INCAR", help="INCAR文件路径")
    incar_parser.add_argument("-o", "--output", help="输出文件路径")
    incar_parser.add_argument("--param", action="append", nargs=2, metavar=("PARAM", "VALUE"), 
                             help="设置参数，格式: --param PARAM VALUE (可多次使用)")
    incar_parser.add_argument("--auto-mag", action="store_true", help="自动设置磁矩")
    incar_parser.add_argument("--dft-u", action="store_true", help="启用DFT+U")
    incar_parser.add_argument("--poscar", help="POSCAR文件路径(用于自动磁矩和DFT+U)")
    
    # KPOINTS命令 - 独立KPOINTS文件操作
    kpoints_parser = subparsers.add_parser("kpoints", help="KPOINTS文件操作")
    kpoints_parser.add_argument("action", choices=["create", "edit"], help="操作类型")
    kpoints_parser.add_argument("-t", "--template", choices=list(KPOINTS_TEMPLATES.keys()), help="使用KPOINTS模板")
    kpoints_parser.add_argument("-g", "--grid", type=int, nargs=3, default=[4, 4, 4], help="K点网格")
    kpoints_parser.add_argument("-m", "--method", choices=["gamma", "monkhorst"], default="gamma", help="K点生成方法")
    kpoints_parser.add_argument("-f", "--file", default="KPOINTS", help="KPOINTS文件路径")
    kpoints_parser.add_argument("-o", "--output", help="输出文件路径")
    kpoints_parser.add_argument("--shift", type=float, nargs=3, help="K点偏移")
    
    # POTCAR命令 - 独立POTCAR文件操作
    potcar_parser = subparsers.add_parser("potcar", help="POTCAR文件操作")
    potcar_parser.add_argument("action", choices=["create", "info"], help="操作类型")
    potcar_parser.add_argument("-t", "--template", choices=list(POTCAR_TEMPLATES.keys()), help="使用POTCAR模板")
    potcar_parser.add_argument("-e", "--elements", nargs="+", help="元素列表")
    potcar_parser.add_argument("-f", "--functional", default="PBE", help="泛函类型")
    potcar_parser.add_argument("-o", "--output", default="POTCAR", help="输出文件路径")
    potcar_parser.add_argument("--poscar", help="从POSCAR文件自动获取元素")
    
    # SLURM命令 - 独立作业脚本操作
    slurm_parser = subparsers.add_parser("slurm", help="SLURM作业脚本操作")
    slurm_parser.add_argument("action", choices=["create", "edit"], help="操作类型")
    slurm_parser.add_argument("--template", choices=list(SLURM_TEMPLATES.keys()), help="使用SLURM模板")
    slurm_parser.add_argument("-j", "--job-name", default="vasp_job", help="作业名称")
    slurm_parser.add_argument("-n", "--nodes", type=int, default=1, help="节点数")
    slurm_parser.add_argument("-c", "--ntasks-per-node", type=int, default=24, help="每节点核心数")
    slurm_parser.add_argument("-m", "--memory", default="32G", help="内存")
    slurm_parser.add_argument("-t", "--time", default="12:00:00", help="计算时间")
    slurm_parser.add_argument("-p", "--partition", default="normal", help="队列名称")
    slurm_parser.add_argument("-o", "--output", default="submit.sh", help="输出脚本路径")
    slurm_parser.add_argument("--vasp-cmd", default="vasp_std", help="VASP执行命令")
    
    # Info命令 - 显示信息
    info_parser = subparsers.add_parser("info", help="显示信息")
    info_parser.add_argument("type", choices=["magnetic", "dftu", "templates", "incar"], help="信息类型")
    info_parser.add_argument("--elements", nargs="+", help="元素列表")
    info_parser.add_argument("--param", help="查询特定INCAR参数信息")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        if args.command == "poscar":
            handle_poscar_command(args)
        elif args.command == "build":
            handle_build_command(args)
        elif args.command == "incar":
            handle_incar_command(args)
        elif args.command == "kpoints":
            handle_kpoints_command(args)
        elif args.command == "potcar":
            handle_potcar_command(args)
        elif args.command == "slurm":
            handle_slurm_command(args)
        elif args.command == "info":
            handle_info_command(args)
    except Exception as e:
        print(f"{COLORS['RED']}错误: {e}{COLORS['RESET']}")
        sys.exit(1)


def handle_poscar_command(args):
    """处理POSCAR命令"""
    poscar_file = Path(args.file)
    
    if not poscar_file.exists():
        raise FileNotFoundError(f"文件不存在: {poscar_file}")
    
    print(f"{COLORS['GREEN']}读取POSCAR文件: {poscar_file}{COLORS['RESET']}")
    
    poscar = POSCAR(poscar_file)
    structure = poscar.read()
    
    if args.info:
        print_structure_info(structure)
    
    if args.convert:
        try:
            output_file = poscar.convert_coordinates(args.convert)
            print(f"{COLORS['GREEN']}坐标转换完成: {output_file}{COLORS['RESET']}")
        except Exception as e:
            print(f"{COLORS['RED']}坐标转换失败: {e}{COLORS['RESET']}")


def print_structure_info(structure):
    """打印结构信息"""
    print(f"\n{COLORS['BOLD']}结构信息:{COLORS['RESET']}")
    print(f"  化学式: {structure.formula}")
    print(f"  原子数: {structure.num_atoms}")
    print(f"  晶胞体积: {structure.volume:.3f} Å³")
    print(f"  密度: {structure.density:.3f} g/cm³")
    print(f"  坐标类型: {structure.coordinate_type}")
    
    print(f"\n{COLORS['BOLD']}晶格参数:{COLORS['RESET']}")
    lengths = structure.lattice.lengths
    angles = structure.lattice.angles
    print(f"  a = {lengths[0]:.3f} Å")
    print(f"  b = {lengths[1]:.3f} Å") 
    print(f"  c = {lengths[2]:.3f} Å")
    print(f"  α = {angles[0]:.1f}°")
    print(f"  β = {angles[1]:.1f}°")
    print(f"  γ = {angles[2]:.1f}°")
    
    print(f"\n{COLORS['BOLD']}元素组成:{COLORS['RESET']}")
    for element, count in structure.composition.items():
        print(f"  {element}: {count}")



def handle_build_command(args):
    """处理构建命令 - 使用统一文件管理器"""
    print(f"构建VASP计算: {args.poscar} -> {args.output}")
    
    # 读取POSCAR
    poscar_file = Path(args.poscar)
    if not poscar_file.exists():
        raise FileNotFoundError(f"POSCAR文件不存在: {poscar_file}")
    
    poscar = POSCAR(poscar_file)
    structure = poscar.read()
    print(f"✅ 读取结构: {structure.formula}")
    
    # 创建统一文件管理器
    file_manager = VASPFileManager()
    
    # 从命令行参数设置所有配置
    file_manager.setup_from_command_line_args(args)
    
    # 处理磁矩设置
    if args.auto_mag:
        file_manager.incar_config.auto_setup_magnetism(structure)
        print("✅ 自动设置磁矩")
    
    # 处理DFT+U
    if args.dft_u:
        elements = structure.get_ordered_elements()
        file_manager.incar_config.setup_dft_plus_u(elements)
        print("✅ 设置DFT+U参数")
    
    # 创建输出目录并生成所有文件
    output_dir = Path(args.output)
    
    # 复制POSCAR文件
    poscar.write(output_dir / "POSCAR")
    print(f"生成: {output_dir / 'POSCAR'}")
    
    # 生成其他文件
    file_manager.generate_all_files(output_dir, poscar_file)




def handle_info_command(args):
    """处理信息查询命令"""
    if args.type == "magnetic":
        show_magnetic_info(args.elements or [])
    elif args.type == "dftu":
        show_dftu_info(args.elements or [])
    elif args.type == "templates":
        show_template_info()
    elif args.type == "incar":
        show_incar_info(args.param)


def show_magnetic_info(elements):
    """显示磁性信息"""
    print(f"\n{COLORS['BOLD']}磁性信息{COLORS['RESET']}")
    
    if elements:
        manager = MagneticMomentManager()
        for elem in elements:
            info = manager.get_magnetic_info(elem)
            print(f"  {elem}: {info['default_moment']} μB ({'磁性' if info['is_magnetic'] else '非磁性'})")
    else:
        print("请使用 --elements 指定元素")


def show_dftu_info(elements):
    """显示DFT+U信息"""
    print(f"\n{COLORS['BOLD']}DFT+U信息{COLORS['RESET']}")
    
    if elements:
        for elem in elements:
            if elem in DFT_PLUS_U_DATABASE:
                data = DFT_PLUS_U_DATABASE[elem]
                print(f"  {elem}: U={data['U']} eV, L={data['L']}")
            else:
                print(f"  {elem}: 无DFT+U数据")
    else:
        print("请使用 --elements 指定元素")


def show_template_info():
    """显示模板信息"""
    print(f"\n{COLORS['BOLD']}可用模板{COLORS['RESET']}")
    for name in CALCULATION_TEMPLATES.keys():
        print(f"  {name}")


def show_incar_info(param_name=None):
    """显示INCAR参数信息"""
    if param_name:
        # 显示特定参数信息
        param_name = param_name.upper()
        print(f"\n{COLORS['BOLD']}INCAR参数信息: {param_name}{COLORS['RESET']}")
        
        if param_name in ALL_PARAMS:
            param_info = ALL_PARAMS[param_name]
            print(f"  类型: {param_info['type']}")
            
            if 'default' in param_info:
                print(f"  默认值: {param_info['default']}")
            
            if 'values' in param_info:
                print(f"  可选值: {param_info['values']}")
            
            if 'min' in param_info and 'max' in param_info:
                print(f"  取值范围: {param_info['min']} - {param_info['max']}")
            elif 'min' in param_info:
                print(f"  最小值: {param_info['min']}")
            elif 'max' in param_info:
                print(f"  最大值: {param_info['max']}")
                
            # 显示参数分类
            for category, params in [
                ('基础参数', BASIC_PARAMS),
                ('电子结构参数', ELECTRONIC_PARAMS),
                ('结构优化参数', OPTIMIZATION_PARAMS),
                ('分子动力学参数', MD_PARAMS),
                ('DOS参数', DOS_PARAMS),
                ('输出参数', OUTPUT_PARAMS),
                ('并行参数', PARALLEL_PARAMS),
                ('混合泛函参数', HYBRID_PARAMS)
            ]:
                if param_name in params:
                    print(f"  分类: {category}")
                    break
        else:
            print(f"  {COLORS['YELLOW']}未知参数{COLORS['RESET']}")
            print(f"  {COLORS['CYAN']}提示: 使用 'python -m wvasp info incar' 查看所有可用参数{COLORS['RESET']}")
    else:
        # 显示所有参数分类
        print(f"\n{COLORS['BOLD']}INCAR参数分类{COLORS['RESET']}")
        
        categories = [
            ('基础参数', BASIC_PARAMS),
            ('电子结构参数', ELECTRONIC_PARAMS),
            ('结构优化参数', OPTIMIZATION_PARAMS),
            ('分子动力学参数', MD_PARAMS),
            ('DOS参数', DOS_PARAMS),
            ('输出参数', OUTPUT_PARAMS),
            ('并行参数', PARALLEL_PARAMS),
            ('混合泛函参数', HYBRID_PARAMS)
        ]
        
        for category_name, params in categories:
            print(f"\n{COLORS['CYAN']}{category_name}:{COLORS['RESET']}")
            for param in sorted(params.keys()):
                param_info = params[param]
                default = param_info.get('default', 'N/A')
                print(f"  {param:<12} (默认: {default})")
        
        print(f"\n{COLORS['CYAN']}使用方法:{COLORS['RESET']}")
        print(f"  查看特定参数: python -m wvasp info incar --param ENCUT")
        print(f"  设置参数: python -m wvasp build POSCAR template --incar ENCUT 500")


def handle_incar_command(args):
    """处理INCAR命令 - 使用统一配置管理器"""
    print(f"{COLORS['GREEN']}INCAR操作: {args.action}{COLORS['RESET']}")
    
    # 创建配置管理器
    if args.action in ["create", "edit"]:
        # 初始化配置
        if args.template:
            config = ParameterConfig(args.template)
            print(f"✅ 使用模板: {args.template}")
        else:
            config = ParameterConfig()
            print("✅ 使用默认配置")
        
        # 如果是编辑模式且文件存在，加载现有参数
        if args.action == "edit":
            incar_file = Path(args.file)
            if incar_file.exists() and not args.template:
                config.load_from_incar_file(incar_file)
                print("✅ 保持现有配置")
        
        # 统一处理命令行参数
        if args.param:
            config.update_parameters_from_command_line(args.param)
        
        # 处理结构相关设置
        if args.poscar and (args.auto_mag or args.dft_u):
            poscar = POSCAR(Path(args.poscar))
            structure = poscar.read()
            
            if args.auto_mag:
                config.auto_setup_magnetism(structure)
                print("✅ 自动设置磁矩")
            
            if args.dft_u:
                elements = structure.get_ordered_elements()
                config.setup_dft_plus_u(elements)
                print("✅ 设置DFT+U参数")
        
        # 生成文件
        output_file = Path(args.output) if args.output else Path(args.file)
        incar = INCAR()
        for param, value in config.get_all_parameters().items():
            incar.set_parameter(param, value)
        incar.write(output_file)
        
        action_text = "已更新" if args.action == "edit" else "已创建"
        print(f"✅ INCAR文件{action_text}: {output_file}")
        
    elif args.action == "validate":
        # 验证INCAR文件
        incar_file = Path(args.file)
        if not incar_file.exists():
            raise FileNotFoundError(f"INCAR文件不存在: {incar_file}")
        
        incar = INCAR(incar_file)
        parameters = incar.read()
        
        print(f"验证INCAR文件: {incar_file}")
        errors = []
        for param, value in parameters.items():
            if not VASPParameterValidator.validate_parameter(param, value):
                errors.append(f"  ❌ {param} = {value}")
            else:
                print(f"  ✅ {param} = {value}")
        
        if errors:
            print(f"\n{COLORS['RED']}发现错误:{COLORS['RESET']}")
            for error in errors:
                print(error)
        else:
            print(f"\n{COLORS['GREEN']}✅ INCAR文件验证通过{COLORS['RESET']}")


def handle_kpoints_command(args):
    """处理KPOINTS命令 - 使用统一配置管理器"""
    print(f"{COLORS['GREEN']}KPOINTS操作: {args.action}{COLORS['RESET']}")
    
    if args.action in ["create", "edit"]:
        # 使用KPointsConfig统一处理
        from .core.parameters import KPointsConfig
        
        kpoints_config = KPointsConfig(
            template=getattr(args, 'template', None),
            method=args.method,
            grid=args.grid,
            shift=args.shift
        )
        
        output_file = Path(args.output) if args.output else Path(args.file)
        kpoints_config.generate_kpoints(output_file)
        
        action_text = "已更新" if args.action == "edit" else "已创建"
        print(f"✅ KPOINTS文件{action_text}: {output_file}")
        print(f"   方法: {args.method}")
        print(f"   网格: {args.grid}")
        if args.shift:
            print(f"   偏移: {args.shift}")


def handle_potcar_command(args):
    """处理POTCAR命令 - 使用统一配置管理器"""
    print(f"{COLORS['GREEN']}POTCAR操作: {args.action}{COLORS['RESET']}")
    
    if args.action == "create":
        # 使用PotcarConfig统一处理
        from .core.parameters import PotcarConfig
        
        potcar_config = PotcarConfig(
            template=getattr(args, 'template', None),
            functional=args.functional
        )
        
        # 确定元素列表
        if args.poscar:
            potcar_config.update_from_poscar(Path(args.poscar))
        elif args.elements:
            potcar_config.update_from_command_line(elements=args.elements)
        else:
            raise ValueError("必须指定元素列表或POSCAR文件")
        
        # 生成POTCAR文件
        output_file = Path(args.output)
        potcar_config.generate_potcar(output_file)
        print(f"   元素: {potcar_config.elements}")
        print(f"   泛函: {potcar_config.functional}")
        
    elif args.action == "info":
        if args.elements:
            print(f"POTCAR信息查询: {args.elements}")
            config = get_config()
            if config.potcar_path and Path(config.potcar_path).exists():
                for element in args.elements:
                    potcar_path = Path(config.potcar_path) / element / "POTCAR"
                    if potcar_path.exists():
                        print(f"  ✅ {element}: {potcar_path}")
                    else:
                        print(f"  ❌ {element}: 未找到")
            else:
                print("❌ 未配置POTCAR路径")


def handle_slurm_command(args):
    """处理SLURM命令 - 使用统一配置管理器"""
    print(f"{COLORS['GREEN']}SLURM脚本操作: {args.action}{COLORS['RESET']}")
    
    if args.action in ["create", "edit"]:
        # 使用SlurmConfig统一处理
        slurm_config = SlurmConfig(
            template=getattr(args, 'template', None),
            job_name=args.job_name,
            nodes=args.nodes,
            ntasks_per_node=args.ntasks_per_node,
            memory=args.memory,
            time=args.time,
            partition=args.partition,
            vasp_cmd=args.vasp_cmd
        )
        
        output_file = Path(args.output)
        slurm_config.generate_slurm_script(output_file)


if __name__ == "__main__":
    main()
