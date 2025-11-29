"""
WVasp主入口

命令行界面和主要功能入口。
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .core.io import POSCAR
from .utils.constants import COLORS


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
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        if args.command == "poscar":
            handle_poscar_command(args)
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
        convert_coordinates(poscar, structure, args.convert)


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


def convert_coordinates(poscar, structure, coord_type):
    """转换坐标类型"""
    if coord_type == "cart":
        coord_type_name = "Cartesian"
        target_type = "cartesian"
    else:
        coord_type_name = "Direct"
        target_type = "fractional"
    
    if structure.coordinate_type == target_type:
        print(f"{COLORS['YELLOW']}坐标已经是{coord_type_name}类型{COLORS['RESET']}")
        return
    
    output_file = poscar.filepath.with_suffix(f".{coord_type}")
    print(f"{COLORS['GREEN']}转换为{coord_type_name}坐标并保存到: {output_file}{COLORS['RESET']}")
    
    poscar.write(output_file, coordinate_type=coord_type_name)


if __name__ == "__main__":
    main()
