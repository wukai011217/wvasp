#!/usr/bin/env python3
"""
WVasp环境设置脚本

帮助用户设置WVasp所需的环境变量和配置。
"""

import os
import sys
from pathlib import Path

# 添加wvasp到路径
sys.path.insert(0, str(Path(__file__).parent / 'wvasp'))

from wvasp.utils.config import WVaspConfig


def setup_environment():
    """交互式设置WVasp环境"""
    print("🚀 WVasp环境设置向导")
    print("=" * 50)
    
    config = WVaspConfig()
    
    # 1. 设置POTCAR路径
    print("\n1. 设置POTCAR路径")
    print("POTCAR文件是VASP计算必需的赝势文件。")
    
    current_potcar = config.potcar_path
    if current_potcar:
        print(f"当前POTCAR路径: {current_potcar}")
        if Path(current_potcar).exists():
            print("✅ 路径存在")
        else:
            print("❌ 路径不存在")
    else:
        print("当前未设置POTCAR路径")
    
    while True:
        new_path = input("请输入POTCAR路径 (回车跳过): ").strip()
        if not new_path:
            break
        
        path = Path(new_path).expanduser()
        if path.exists() and path.is_dir():
            config.potcar_path = str(path)
            print(f"✅ POTCAR路径设置为: {path}")
            break
        else:
            print("❌ 路径不存在，请重新输入")
    
    # 2. 设置VASP可执行文件
    print("\n2. 设置VASP可执行文件")
    print(f"当前VASP可执行文件: {config.vasp_executable}")
    
    new_executable = input("请输入VASP可执行文件名 (回车跳过): ").strip()
    if new_executable:
        config.vasp_executable = new_executable
        print(f"✅ VASP可执行文件设置为: {new_executable}")
    
    # 3. 设置默认参数
    print("\n3. 设置默认计算参数")
    
    # 截断能
    print(f"当前默认截断能: {config.default_encut} eV")
    new_encut = input("请输入默认截断能 (回车跳过): ").strip()
    if new_encut:
        try:
            config.default_encut = float(new_encut)
            print(f"✅ 默认截断能设置为: {config.default_encut} eV")
        except ValueError:
            print("❌ 无效的数值")
    
    # K点网格
    print(f"当前默认K点网格: {' '.join(map(str, config.default_kpoints))}")
    new_kpoints = input("请输入默认K点网格 (如: 6 6 6, 回车跳过): ").strip()
    if new_kpoints:
        try:
            kpoints = [int(x) for x in new_kpoints.split()]
            if len(kpoints) == 3:
                config.default_kpoints = kpoints
                print(f"✅ 默认K点网格设置为: {' '.join(map(str, kpoints))}")
            else:
                print("❌ 请输入3个整数")
        except ValueError:
            print("❌ 无效的K点网格")
    
    # 4. 设置作业调度器
    print("\n4. 设置作业调度器")
    print(f"当前作业调度器: {config.job_scheduler}")
    print("支持的调度器: slurm, pbs, local")
    
    new_scheduler = input("请选择作业调度器 (回车跳过): ").strip().lower()
    if new_scheduler in ['slurm', 'pbs', 'local']:
        config.job_scheduler = new_scheduler
        print(f"✅ 作业调度器设置为: {new_scheduler}")
    elif new_scheduler:
        print("❌ 不支持的调度器类型")
    
    # 5. 保存配置
    print("\n5. 保存配置")
    save_config = input("是否保存配置到文件? (y/N): ").strip().lower()
    if save_config in ['y', 'yes']:
        config.save_config()
        print("✅ 配置已保存")
    
    # 6. 生成环境变量设置脚本
    print("\n6. 生成环境变量设置")
    generate_env = input("是否生成环境变量设置脚本? (y/N): ").strip().lower()
    if generate_env in ['y', 'yes']:
        generate_env_scripts(config)
    
    # 7. 验证环境
    print("\n7. 环境验证")
    config.print_status()
    
    print("\n🎉 环境设置完成！")
    print("\n使用提示:")
    print("- 运行 'wvasp --help' 查看可用命令")
    print("- 运行 'wvasp info' 查看当前配置")
    print("- 如需重新配置，再次运行此脚本")


def generate_env_scripts(config: WVaspConfig):
    """生成环境变量设置脚本"""
    
    # 生成bash脚本
    bash_script = f"""#!/bin/bash
# WVasp环境变量设置脚本
# 使用方法: source wvasp_env.sh

# VASP相关路径
export VASP_EXECUTABLE="{config.vasp_executable}"
export VASP_POTCAR_PATH="{config.potcar_path or ''}"

# WVasp默认设置
export WVASP_DEFAULT_ENCUT="{config.default_encut}"
export WVASP_DEFAULT_FUNCTIONAL="{config.default_functional}"
export WVASP_JOB_SCHEDULER="{config.job_scheduler}"
export WVASP_DEFAULT_PARTITION="{config.default_partition}"

echo "WVasp环境变量已设置"
"""
    
    # 生成fish脚本
    fish_script = f"""#!/usr/bin/env fish
# WVasp环境变量设置脚本 (Fish Shell)
# 使用方法: source wvasp_env.fish

# VASP相关路径
set -gx VASP_EXECUTABLE "{config.vasp_executable}"
set -gx VASP_POTCAR_PATH "{config.potcar_path or ''}"

# WVasp默认设置
set -gx WVASP_DEFAULT_ENCUT "{config.default_encut}"
set -gx WVASP_DEFAULT_FUNCTIONAL "{config.default_functional}"
set -gx WVASP_JOB_SCHEDULER "{config.job_scheduler}"
set -gx WVASP_DEFAULT_PARTITION "{config.default_partition}"

echo "WVasp环境变量已设置 (Fish Shell)"
"""
    
    # 写入脚本文件
    bash_file = Path("wvasp_env.sh")
    fish_file = Path("wvasp_env.fish")
    
    with open(bash_file, 'w') as f:
        f.write(bash_script)
    bash_file.chmod(0o755)
    
    with open(fish_file, 'w') as f:
        f.write(fish_script)
    fish_file.chmod(0o755)
    
    print(f"✅ 生成环境变量脚本:")
    print(f"   Bash: {bash_file.absolute()}")
    print(f"   Fish: {fish_file.absolute()}")
    print(f"\n使用方法:")
    print(f"   Bash/Zsh: source {bash_file}")
    print(f"   Fish: source {fish_file}")


def check_environment():
    """检查当前环境设置"""
    print("🔍 WVasp环境检查")
    print("=" * 50)
    
    config = WVaspConfig()
    config.print_status()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_environment()
    else:
        setup_environment()
