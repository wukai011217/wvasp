#!/usr/bin/env python3
"""
演示VASP参数管理系统的使用

展示如何使用新的参数管理系统来配置VASP计算参数
"""

import sys
from pathlib import Path

# 添加wvasp到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.utils.parameter_manager import (
    ParameterConfig, ParameterManager,
    create_optimization_config, create_scf_config, create_dos_config,
    create_band_config, create_neb_config, create_md_config
)
from wvasp.utils.constants import VASPParameters, CALCULATION_TEMPLATES


def demo_basic_parameter_usage():
    """演示基本参数使用"""
    print("🎯 基本参数管理演示")
    print("=" * 50)
    
    # 1. 创建基本配置
    config = ParameterConfig()
    
    # 2. 设置参数
    config.set_parameter('SYSTEM', 'My calculation')
    config.set_parameter('ENCUT', 500.0)
    config.set_parameter('ISMEAR', 0)
    config.set_parameter('SIGMA', 0.05)
    
    print("✅ 基本配置创建成功")
    print(f"参数数量: {len(config.get_all_parameters())}")
    print()
    
    # 3. 参数验证
    print("🔍 参数验证:")
    try:
        config.set_parameter('ENCUT', 50.0)  # 太小，应该失败
    except Exception as e:
        print(f"   ❌ 无效参数被正确拒绝: {e}")
    
    try:
        config.set_parameter('ISMEAR', 10)  # 无效值
    except Exception as e:
        print(f"   ❌ 无效值被正确拒绝: {e}")
    
    print("   ✅ 参数验证工作正常")
    print()


def demo_template_usage():
    """演示模板使用"""
    print("📋 模板配置演示")
    print("=" * 50)
    
    # 1. 使用不同的模板
    templates = ['optimization', 'scf', 'dos', 'band', 'neb', 'md']
    
    for template_name in templates:
        config = ParameterConfig(template=template_name)
        params = config.get_all_parameters()
        
        print(f"✅ {template_name.upper()} 模板:")
        print(f"   参数数量: {len(params)}")
        print(f"   SYSTEM: {params.get('SYSTEM')}")
        print(f"   NSW: {params.get('NSW', 'N/A')}")
        print(f"   IBRION: {params.get('IBRION', 'N/A')}")
        print()


def demo_convenience_functions():
    """演示便捷函数"""
    print("🚀 便捷函数演示")
    print("=" * 50)
    
    # 1. 结构优化配置
    opt_config = create_optimization_config(
        ENCUT=600.0,
        NSW=1000,
        EDIFFG=-0.005
    )
    
    print("✅ 结构优化配置:")
    print(f"   ENCUT: {opt_config.get_parameter('ENCUT')}")
    print(f"   NSW: {opt_config.get_parameter('NSW')}")
    print(f"   EDIFFG: {opt_config.get_parameter('EDIFFG')}")
    print()
    
    # 2. DOS计算配置
    dos_config = create_dos_config(
        NEDOS=5000,
        LORBIT=12
    )
    
    print("✅ DOS计算配置:")
    print(f"   NEDOS: {dos_config.get_parameter('NEDOS')}")
    print(f"   LORBIT: {dos_config.get_parameter('LORBIT')}")
    print(f"   ISMEAR: {dos_config.get_parameter('ISMEAR')}")
    print()
    
    # 3. NEB计算配置
    neb_config = create_neb_config(
        IMAGES=7,
        SPRING=-10.0,
        LCLIMB=True
    )
    
    print("✅ NEB计算配置:")
    print(f"   IMAGES: {neb_config.get_parameter('IMAGES')}")
    print(f"   SPRING: {neb_config.get_parameter('SPRING')}")
    print(f"   LCLIMB: {neb_config.get_parameter('LCLIMB')}")
    print()


def demo_parameter_manager():
    """演示参数管理器"""
    print("🗂️ 参数管理器演示")
    print("=" * 50)
    
    # 1. 创建参数管理器
    manager = ParameterManager()
    
    # 2. 创建多个配置
    manager.create_config('opt_high_precision', 'optimization', 
                         ENCUT=800.0, EDIFF=1e-7, EDIFFG=-0.001)
    
    manager.create_config('dos_fine', 'dos',
                         NEDOS=10000, SIGMA=0.01)
    
    manager.create_config('neb_long', 'neb',
                         IMAGES=9, NSW=1000, SPRING=-15.0)
    
    print("✅ 创建的配置:")
    for config_name in manager.list_configs():
        config = manager.get_config(config_name)
        print(f"   {config_name}: {len(config.get_all_parameters())} 参数")
    print()
    
    # 3. 配置验证
    print("🔍 配置验证:")
    for config_name in manager.list_configs():
        is_valid, errors = manager.validate_config(config_name)
        status = "✅ 有效" if is_valid else f"❌ 无效: {errors}"
        print(f"   {config_name}: {status}")
    print()


def demo_advanced_features():
    """演示高级功能"""
    print("⚡ 高级功能演示")
    print("=" * 50)
    
    # 1. 配置合并
    base_config = create_scf_config(ENCUT=400.0)
    custom_config = ParameterConfig()
    custom_config.set_parameter('ENCUT', 600.0)
    custom_config.set_parameter('ISMEAR', -5)
    
    merged_config = base_config.merge(custom_config)
    
    print("✅ 配置合并:")
    print(f"   基础 ENCUT: {base_config.get_parameter('ENCUT')}")
    print(f"   自定义 ENCUT: {custom_config.get_parameter('ENCUT')}")
    print(f"   合并后 ENCUT: {merged_config.get_parameter('ENCUT')}")
    print(f"   合并后 ISMEAR: {merged_config.get_parameter('ISMEAR')}")
    print()
    
    # 2. 参数信息查询
    print("📖 参数信息查询:")
    param_info = VASPParameters.get_parameter_info('ENCUT')
    print(f"   ENCUT 信息: {param_info}")
    
    default_encut = VASPParameters.get_default('ENCUT')
    print(f"   ENCUT 默认值: {default_encut}")
    print()
    
    # 3. 配置保存和加载
    temp_file = Path("temp_config.json")
    try:
        merged_config.save_to_file(temp_file)
        print(f"✅ 配置已保存到: {temp_file}")
        
        loaded_config = ParameterConfig()
        loaded_config.load_from_file(temp_file)
        print(f"✅ 配置已从文件加载，参数数量: {len(loaded_config.get_all_parameters())}")
        
        # 清理临时文件
        temp_file.unlink()
        print("✅ 临时文件已清理")
    except Exception as e:
        print(f"❌ 文件操作失败: {e}")
    print()


def demo_practical_usage():
    """演示实际使用场景"""
    print("🏗️ 实际使用场景演示")
    print("=" * 50)
    
    # 场景1: 高精度结构优化
    print("场景1: 高精度结构优化")
    high_precision_opt = create_optimization_config(
        ENCUT=800.0,
        EDIFF=1e-8,
        EDIFFG=-0.001,
        NSW=2000,
        PREC='Accurate'
    )
    
    print(f"   截断能: {high_precision_opt.get_parameter('ENCUT')} eV")
    print(f"   能量收敛: {high_precision_opt.get_parameter('EDIFF')}")
    print(f"   力收敛: {high_precision_opt.get_parameter('EDIFFG')} eV/Å")
    print()
    
    # 场景2: 快速预优化
    print("场景2: 快速预优化")
    fast_opt = create_optimization_config(
        ENCUT=300.0,
        EDIFF=1e-4,
        EDIFFG=-0.05,
        NSW=100,
        PREC='Normal'
    )
    
    print(f"   截断能: {fast_opt.get_parameter('ENCUT')} eV")
    print(f"   能量收敛: {fast_opt.get_parameter('EDIFF')}")
    print(f"   力收敛: {fast_opt.get_parameter('EDIFFG')} eV/Å")
    print()
    
    # 场景3: 磁性材料计算
    print("场景3: 磁性材料计算")
    magnetic_config = create_scf_config(
        ISPIN=2,
        MAGMOM=[5.0, -5.0, 0.0, 0.0],  # Fe原子的磁矩设置
        ISMEAR=1,
        SIGMA=0.2
    )
    
    print(f"   自旋极化: ISPIN = {magnetic_config.get_parameter('ISPIN')}")
    print(f"   磁矩设置: {magnetic_config.get_parameter('MAGMOM')}")
    print(f"   展宽方法: ISMEAR = {magnetic_config.get_parameter('ISMEAR')}")
    print()


def main():
    """主函数"""
    print("🎯 WVasp 参数管理系统演示")
    print("=" * 60)
    print()
    
    try:
        demo_basic_parameter_usage()
        demo_template_usage()
        demo_convenience_functions()
        demo_parameter_manager()
        demo_advanced_features()
        demo_practical_usage()
        
        print("🎉 所有演示完成！")
        print()
        print("💡 参数管理系统的主要优势:")
        print("   ✅ 参数验证和类型检查")
        print("   ✅ 预定义的计算模板")
        print("   ✅ 灵活的配置管理")
        print("   ✅ 配置保存和加载")
        print("   ✅ 参数合并和继承")
        print("   ✅ 便捷的API接口")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
