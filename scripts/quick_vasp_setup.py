#!/usr/bin/env python3
"""
快速VASP计算设置脚本

用法:
python quick_vasp_setup.py structure.vasp --job-name my_calc --nodes 2 --time 24:00:00
"""

import argparse
from pathlib import Path
from wvasp.core.io import POSCAR, INCAR, KPOINTS, POTCAR
from wvasp.core.tasks.job_management import JobConfig, JobScriptGenerator

def main():
    parser = argparse.ArgumentParser(description='快速设置VASP计算')
    parser.add_argument('structure', help='结构文件路径 (POSCAR格式)')
    parser.add_argument('--job-name', default='vasp_calc', help='作业名称')
    parser.add_argument('--nodes', type=int, default=1, help='节点数')
    parser.add_argument('--ntasks-per-node', type=int, default=24, help='每节点核心数')
    parser.add_argument('--memory', default='32G', help='内存')
    parser.add_argument('--time', default='12:00:00', help='计算时间')
    parser.add_argument('--partition', default='normal', help='队列名称')
    parser.add_argument('--encut', type=float, default=400.0, help='截断能')
    parser.add_argument('--kpoints', nargs=3, type=int, default=[6, 6, 6], help='K点网格')
    parser.add_argument('--output-dir', default=None, help='输出目录 (默认为POSCAR文件所在目录)')
    parser.add_argument('--potcar-dir', default='/Users/wukai/Desktop/project/vasp/test/pot', help='POTCAR库路径')
    
    args = parser.parse_args()
    
    # 1. 验证结构文件
    structure_path = Path(args.structure)
    if not structure_path.exists():
        print(f"❌ 结构文件不存在: {structure_path}")
        return
    
    # 确定输出目录 - 默认为POSCAR文件所在目录
    if args.output_dir is None:
        output_dir = structure_path.parent
    else:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 设置VASP计算: {args.job_name}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 结构文件: {structure_path}")
    
    # 读取并验证结构
    poscar = POSCAR(structure_path)
    try:
        structure = poscar.read()
        print(f"✅ 结构文件读取成功: {structure.formula}")
    except Exception as e:
        print(f"❌ 结构文件读取失败: {e}")
        return
    
    # 如果输出目录不是POSCAR所在目录，则复制POSCAR文件
    if output_dir != structure_path.parent:
        poscar.write(output_dir / "POSCAR")
        print(f"📋 POSCAR已复制到: {output_dir / 'POSCAR'}")
    else:
        print(f"📋 使用现有POSCAR: {structure_path}")
    
    # 提取元素列表
    elements = list(structure.composition.keys())
    
    # 2. 创建INCAR文件
    incar = INCAR()
    incar.set_parameter('SYSTEM', f'{args.job_name} calculation')
    incar.set_parameter('ISTART', 0)
    incar.set_parameter('ICHARG', 2)
    incar.set_parameter('ENCUT', args.encut)
    incar.set_parameter('ISMEAR', 0)
    incar.set_parameter('SIGMA', 0.05)
    incar.set_parameter('EDIFF', 1e-6)
    incar.set_parameter('EDIFFG', -0.01)
    incar.set_parameter('NSW', 100)
    incar.set_parameter('IBRION', 2)
    incar.set_parameter('ISIF', 3)
    incar.set_parameter('LREAL', False)
    incar.set_parameter('PREC', 'Accurate')
    incar.write(output_dir / "INCAR")
    print("✅ INCAR文件已创建")
    
    # 3. 创建KPOINTS文件
    kpoints = KPOINTS.create_gamma_centered(args.kpoints)
    kpoints.write(output_dir / "KPOINTS")
    print(f"✅ KPOINTS文件已创建: {args.kpoints}")
    
    # 4. 创建POTCAR文件
    potcar_dir = Path(args.potcar_dir)
    if potcar_dir.exists():
        try:
            potcar = POTCAR.create_from_elements(elements, potcar_dir)
            potcar.write(output_dir / "POTCAR")
            print(f"✅ POTCAR文件已创建: {elements}")
            
            # 显示推荐的ENCUT
            recommended_encut = potcar.get_recommended_encut()
            if recommended_encut > args.encut:
                print(f"⚠️  建议ENCUT: {recommended_encut:.1f} eV (当前: {args.encut} eV)")
        except Exception as e:
            print(f"❌ POTCAR创建失败: {e}")
            print("   请检查POTCAR库路径和元素可用性")
    else:
        print(f"❌ POTCAR库路径不存在: {potcar_dir}")
    
    # 5. 创建作业脚本
    job_config = JobConfig(
        job_name=args.job_name,
        nodes=args.nodes,
        ntasks_per_node=args.ntasks_per_node,
        memory=args.memory,
        time=args.time,
        partition=args.partition,
        vasp_executable="vasp_std",
        additional_modules=["intel/2021", "vasp/6.3.0"]
    )
    
    script_generator = JobScriptGenerator(job_config)
    script_generator.generate_slurm_script(output_dir / "submit.sh")
    print("✅ SLURM脚本已创建")
    
    print(f"\n🎯 设置完成！")
    print(f"📂 生成的文件:")
    for file_path in output_dir.glob("*"):
        if file_path.is_file():
            print(f"   {file_path.name}")
    
    print(f"\n🚀 提交作业:")
    print(f"   cd {output_dir}")
    print(f"   sbatch submit.sh")
    
    # 检查是否所有文件都已创建
    required_files = ['INCAR', 'KPOINTS', 'POTCAR', 'submit.sh']
    
    # 检查POSCAR文件
    poscar_exists = False
    if (output_dir / "POSCAR").exists():
        poscar_exists = True
    elif output_dir == structure_path.parent and structure_path.exists():
        poscar_exists = True  # 使用原始POSCAR文件
    
    if poscar_exists:
        required_files.insert(0, 'POSCAR')
    
    missing_files = []
    for filename in required_files:
        file_path = output_dir / filename
        if filename == 'POSCAR' and output_dir == structure_path.parent:
            # 对于原地生成的情况，检查原始POSCAR文件
            if not structure_path.exists():
                missing_files.append(filename)
        elif not file_path.exists():
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️  缺少文件: {', '.join(missing_files)}")
    else:
        print(f"\n✅ 所有必要文件已创建完成！")

if __name__ == "__main__":
    main()
