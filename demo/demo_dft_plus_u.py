#!/usr/bin/env python3
"""
演示DFT+U参数管理功能

展示如何为La系等强关联电子体系配置DFT+U参数
"""

import sys
from pathlib import Path

# 添加wvasp到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.utils.parameter_manager import (
    create_dft_plus_u_config, get_dft_plus_u_recommendation, 
    print_dft_plus_u_info, get_available_dft_plus_u_elements,
    get_dft_plus_u_presets, ParameterConfig
)
from wvasp.utils.constants import DFT_PLUS_U_DATABASE


def demo_basic_dft_plus_u():
    """演示基本DFT+U配置"""
    print("🔬 基本DFT+U配置演示")
    print("=" * 50)
    
    # 1. La2O3体系
    print("1. La2O3 体系配置:")
    elements = ['La', 'La', 'O', 'O', 'O']
    config = create_dft_plus_u_config(elements, template='scf')
    
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   DFT+U 启用: {dft_u_info['enabled']}")
    print(f"   LDAUTYPE: {dft_u_info['type']}")
    print(f"   LDAUL: {dft_u_info['l_values']}")
    print(f"   LDAUU: {dft_u_info['u_values']}")
    print(f"   LDAUJ: {dft_u_info['j_values']}")
    print()
    
    # 2. CeO2体系
    print("2. CeO2 体系配置:")
    elements = ['Ce', 'O', 'O']
    config = create_dft_plus_u_config(elements, template='optimization')
    
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   LDAUL: {dft_u_info['l_values']}")
    print(f"   LDAUU: {dft_u_info['u_values']}")
    print()
    
    # 3. 普通体系（不需要DFT+U）
    print("3. SiO2 体系（不需要DFT+U）:")
    elements = ['Si', 'O', 'O']
    config = create_dft_plus_u_config(elements)
    
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   DFT+U 启用: {dft_u_info['enabled']}")
    print()


def demo_custom_u_values():
    """演示自定义U值"""
    print("⚙️ 自定义U值演示")
    print("=" * 50)
    
    # 使用自定义U值
    elements = ['La', 'Fe', 'O', 'O', 'O']
    custom_u = {'La': 5.5, 'Fe': 4.5, 'O': 0.0}
    
    config = create_dft_plus_u_config(
        elements=elements,
        template='scf',
        custom_u_values=custom_u,
        ISPIN=2,  # 考虑磁性
        MAGMOM=[3.0, 4.0, 0.0, 0.0, 0.0]  # 设置磁矩
    )
    
    dft_u_info = config.get_dft_plus_u_info()
    print("LaFeO3 体系（自定义U值）:")
    print(f"   元素顺序: {elements}")
    print(f"   自定义U值: {custom_u}")
    print(f"   LDAUL: {dft_u_info['l_values']}")
    print(f"   LDAUU: {dft_u_info['u_values']}")
    print(f"   ISPIN: {config.get_parameter('ISPIN')}")
    print(f"   MAGMOM: {config.get_parameter('MAGMOM')}")
    print()


def demo_different_presets():
    """演示不同的预设"""
    print("📋 不同预设演示")
    print("=" * 50)
    
    # 镧系预设
    print("1. 镧系元素预设:")
    elements = ['Nd', 'O', 'O', 'O']
    config = create_dft_plus_u_config(elements, preset='lanthanides_standard')
    print(f"   LMAXMIX: {config.get_parameter('LMAXMIX')}")
    print(f"   LDAUTYPE: {config.get_parameter('LDAUTYPE')}")
    print()
    
    # 过渡金属预设
    print("2. 过渡金属预设:")
    elements = ['Fe', 'O', 'O', 'O']
    config = create_dft_plus_u_config(elements, preset='transition_metals')
    print(f"   LMAXMIX: {config.get_parameter('LMAXMIX')}")
    print(f"   LDAUTYPE: {config.get_parameter('LDAUTYPE')}")
    print()
    
    # 自动检测预设
    print("3. 自动检测预设:")
    elements = ['U', 'O', 'O']
    config = create_dft_plus_u_config(elements, preset='auto')
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   检测到锕系元素，自动使用锕系预设")
    print(f"   LMAXMIX: {config.get_parameter('LMAXMIX')}")
    print()


def demo_parameter_recommendations():
    """演示参数推荐功能"""
    print("💡 参数推荐演示")
    print("=" * 50)
    
    # 不同体系的推荐
    test_systems = [
        (['La', 'O', 'O', 'O'], 'LaO3'),
        (['Ce', 'Fe', 'O', 'O', 'O'], 'CeFeO3'),
        (['Ti', 'O', 'O'], 'TiO2'),
        (['Si', 'O', 'O'], 'SiO2'),
        (['U', 'O', 'O'], 'UO2'),
    ]
    
    for elements, formula in test_systems:
        print(f"体系: {formula}")
        recommendations = get_dft_plus_u_recommendation(elements)
        
        if recommendations['needs_dft_plus_u']:
            print(f"   ✅ 需要DFT+U")
            print(f"   推荐元素: {recommendations['recommended_elements']}")
            print(f"   推荐预设: {recommendations['suggested_preset']}")
            if recommendations['warnings']:
                print(f"   注意事项: {recommendations['warnings'][0]}")
        else:
            print(f"   ❌ 不需要DFT+U")
        print()


def demo_detailed_analysis():
    """演示详细分析功能"""
    print("🔍 详细分析演示")
    print("=" * 50)
    
    # 复杂体系分析
    elements = ['La', 'Sr', 'Mn', 'O', 'O', 'O']
    print(f"分析体系: La-Sr-Mn-O (元素: {elements})")
    print()
    
    print_dft_plus_u_info(elements)


def demo_available_elements():
    """演示可用元素查询"""
    print("📚 可用元素数据库")
    print("=" * 50)
    
    database = get_available_dft_plus_u_elements()
    
    print("镧系元素:")
    lanthanides = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
    for elem in lanthanides:
        if elem in database:
            info = database[elem]
            print(f"   {elem}: U={info['U']} eV, L={info['L']}")
    print()
    
    print("过渡金属元素:")
    transition_metals = ['Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu']
    for elem in transition_metals:
        if elem in database:
            info = database[elem]
            print(f"   {elem}: U={info['U']} eV, L={info['L']}")
    print()
    
    print(f"总计支持 {len(database)} 种元素的DFT+U参数")
    print()


def demo_preset_information():
    """演示预设信息"""
    print("⚙️ 预设配置信息")
    print("=" * 50)
    
    presets = get_dft_plus_u_presets()
    
    for preset_name, preset_info in presets.items():
        print(f"{preset_name}:")
        print(f"   描述: {preset_info['description']}")
        print(f"   LDAUTYPE: {preset_info['LDAUTYPE']}")
        print(f"   LMAXMIX: {preset_info['LMAXMIX']}")
        print(f"   LDAUPRINT: {preset_info['LDAUPRINT']}")
        print()


def demo_practical_examples():
    """演示实际应用例子"""
    print("🏗️ 实际应用示例")
    print("=" * 50)
    
    print("示例1: LaFeO3 钙钛矿结构优化")
    elements = ['La', 'Fe', 'O', 'O', 'O']
    config = create_dft_plus_u_config(
        elements=elements,
        template='optimization',
        preset='lanthanides_standard',
        ISPIN=2,
        MAGMOM=[0.0, 4.0, 0.0, 0.0, 0.0],  # Fe的磁矩
        NSW=200,
        EDIFFG=-0.02
    )
    
    print("   配置参数:")
    print(f"   LDAU: {config.get_parameter('LDAU')}")
    print(f"   ISPIN: {config.get_parameter('ISPIN')}")
    print(f"   NSW: {config.get_parameter('NSW')}")
    print(f"   MAGMOM: {config.get_parameter('MAGMOM')}")
    
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   LDAUU: {dft_u_info['u_values']}")
    print()
    
    print("示例2: CeO2 表面DOS计算")
    elements = ['Ce', 'Ce', 'O', 'O', 'O', 'O']
    config = create_dft_plus_u_config(
        elements=elements,
        template='dos',
        preset='lanthanides_standard',
        NEDOS=5000,
        LORBIT=12
    )
    
    print("   配置参数:")
    print(f"   ISMEAR: {config.get_parameter('ISMEAR')}")
    print(f"   NEDOS: {config.get_parameter('NEDOS')}")
    print(f"   LORBIT: {config.get_parameter('LORBIT')}")
    
    dft_u_info = config.get_dft_plus_u_info()
    print(f"   DFT+U元素索引: {dft_u_info['plus_u_indices']}")
    print()


def main():
    """主函数"""
    print("🔬 WVasp DFT+U 参数管理演示")
    print("=" * 60)
    print()
    
    try:
        demo_basic_dft_plus_u()
        demo_custom_u_values()
        demo_different_presets()
        demo_parameter_recommendations()
        demo_detailed_analysis()
        demo_available_elements()
        demo_preset_information()
        demo_practical_examples()
        
        print("🎉 DFT+U演示完成！")
        print()
        print("💡 DFT+U管理系统的主要特性:")
        print("   ✅ 自动元素识别和U值推荐")
        print("   ✅ 多种预设配置（镧系、锕系、过渡金属）")
        print("   ✅ 自定义U值支持")
        print("   ✅ 智能参数验证")
        print("   ✅ 详细的配置分析和建议")
        print("   ✅ 与现有参数系统无缝集成")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
