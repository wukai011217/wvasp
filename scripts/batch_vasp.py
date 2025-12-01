#!/usr/bin/env python3
"""
批量VASP计算脚本

用法:
python batch_vasp.py structures/ --template template.json
"""

import argparse
import json
from pathlib import Path
from wvasp.core.io import POSCAR, INCAR, KPOINTS
from wvasp.core.job_scripts import JobConfig, JobScriptGenerator

def load_template(template_file):
    """加载计算模板"""
    with open(template_file, 'r') as f:
        return json.load(f)

def setup_single_calculation(structure_file, template, base_dir):
    """设置单个计算"""
    structure_path = Path(structure_file)
    calc_name = structure_path.stem
    calc_dir = base_dir / calc_name
    calc_dir.mkdir(exist_ok=True)
    
    print(f"🔧 设置计算: {calc_name}")
    
    # 1. 复制结构文件
    poscar = POSCAR(structure_path)
    try:
        structure_data = poscar.read()
        poscar.write(calc_dir / "POSCAR")
        print(f"   ✅ 结构: {structure_data['formula']}")
    except Exception as e:
        print(f"   ❌ 结构文件错误: {e}")
        return False
    
    # 2. 创建INCAR
    incar = INCAR()
    incar_params = template.get('incar', {})
    incar_params['SYSTEM'] = f'{calc_name} calculation'
    
    for key, value in incar_params.items():
        incar.set_parameter(key, value)
    incar.write(calc_dir / "INCAR")
    print(f"   ✅ INCAR: {len(incar_params)} 参数")
    
    # 3. 创建KPOINTS
    kpoints_config = template.get('kpoints', {'grid': [6, 6, 6], 'type': 'gamma'})
    if kpoints_config['type'] == 'gamma':
        kpoints = KPOINTS.create_gamma_centered(kpoints_config['grid'])
    elif kpoints_config['type'] == 'mp':
        kpoints = KPOINTS.create_monkhorst_pack(kpoints_config['grid'])
    else:
        kpoints = KPOINTS.create_automatic(kpoints_config['grid'])
    
    kpoints.write(calc_dir / "KPOINTS")
    print(f"   ✅ KPOINTS: {kpoints_config['grid']}")
    
    # 4. 创建作业脚本
    job_template = template.get('job', {})
    job_config = JobConfig(
        job_name=calc_name,
        nodes=job_template.get('nodes', 1),
        ntasks_per_node=job_template.get('ntasks_per_node', 24),
        memory=job_template.get('memory', '32G'),
        time=job_template.get('time', '12:00:00'),
        partition=job_template.get('partition', 'normal'),
        vasp_executable=job_template.get('vasp_executable', 'vasp_std'),
        additional_modules=job_template.get('modules', [])
    )
    
    script_generator = JobScriptGenerator(job_config)
    script_generator.generate_slurm_script(calc_dir / "submit.sh")
    print(f"   ✅ 作业脚本: {job_config.nodes}节点")
    
    return True

def create_default_template():
    """创建默认模板"""
    template = {
        "incar": {
            "ISTART": 0,
            "ICHARG": 2,
            "ENCUT": 400.0,
            "ISMEAR": 0,
            "SIGMA": 0.05,
            "EDIFF": 1e-6,
            "EDIFFG": -0.01,
            "NSW": 100,
            "IBRION": 2,
            "ISIF": 3,
            "LREAL": False,
            "PREC": "Accurate"
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
    return template

def main():
    parser = argparse.ArgumentParser(description='批量设置VASP计算')
    parser.add_argument('structures_dir', help='结构文件目录')
    parser.add_argument('--template', help='计算模板JSON文件')
    parser.add_argument('--output-dir', default='calculations', help='输出目录')
    parser.add_argument('--pattern', default='*.vasp', help='结构文件匹配模式')
    parser.add_argument('--create-template', action='store_true', help='创建默认模板')
    
    args = parser.parse_args()
    
    # 创建默认模板
    if args.create_template:
        template = create_default_template()
        template_file = Path('vasp_template.json')
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"✅ 默认模板已创建: {template_file}")
        return
    
    # 加载模板
    if args.template:
        template = load_template(args.template)
        print(f"📋 使用模板: {args.template}")
    else:
        template = create_default_template()
        print("📋 使用默认模板")
    
    # 查找结构文件
    structures_dir = Path(args.structures_dir)
    if not structures_dir.exists():
        print(f"❌ 结构目录不存在: {structures_dir}")
        return
    
    structure_files = list(structures_dir.glob(args.pattern))
    if not structure_files:
        print(f"❌ 未找到匹配的结构文件: {args.pattern}")
        return
    
    print(f"🔍 找到 {len(structure_files)} 个结构文件")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    # 批量设置计算
    success_count = 0
    for structure_file in structure_files:
        if setup_single_calculation(structure_file, template, output_dir):
            success_count += 1
    
    print(f"\n🎯 批量设置完成!")
    print(f"   成功: {success_count}/{len(structure_files)}")
    print(f"   输出: {output_dir}")
    
    # 创建批量提交脚本
    submit_all_script = output_dir / "submit_all.sh"
    with open(submit_all_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# 批量提交所有VASP计算\n\n")
        
        for calc_dir in output_dir.iterdir():
            if calc_dir.is_dir() and (calc_dir / "submit.sh").exists():
                f.write(f"echo \"提交计算: {calc_dir.name}\"\n")
                f.write(f"cd {calc_dir}\n")
                f.write("sbatch submit.sh\n")
                f.write("cd ..\n\n")
    
    submit_all_script.chmod(0o755)
    print(f"✅ 批量提交脚本: {submit_all_script}")
    print(f"\n🚀 批量提交命令: ./{submit_all_script}")

if __name__ == "__main__":
    main()