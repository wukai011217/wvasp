#!/usr/bin/env python3
"""
VASP结果分析脚本

用法:
python analyze_results.py /path/to/calculation/directory
"""

import argparse
from pathlib import Path
from wvasp.core.io import OUTCAR, DOSCAR, POSCAR

def analyze_calculation(calc_dir):
    """分析VASP计算结果"""
    calc_path = Path(calc_dir)
    
    if not calc_path.exists():
        print(f"❌ 计算目录不存在: {calc_path}")
        return
    
    print(f"🔍 分析计算结果: {calc_path}")
    print("=" * 60)
    
    # 检查文件存在性
    files_status = {}
    required_files = ['POSCAR', 'INCAR', 'KPOINTS', 'POTCAR']
    output_files = ['OUTCAR', 'CONTCAR', 'OSZICAR', 'DOSCAR', 'vasprun.xml']
    
    print("\n📁 文件检查:")
    for filename in required_files + output_files:
        file_path = calc_path / filename
        exists = file_path.exists()
        files_status[filename] = exists
        status = "✅" if exists else "❌"
        size = f"({file_path.stat().st_size / 1024:.1f} KB)" if exists else ""
        print(f"   {status} {filename} {size}")
    
    # 分析OUTCAR
    outcar_path = calc_path / "OUTCAR"
    if outcar_path.exists():
        print("\n📊 OUTCAR分析:")
        try:
            outcar = OUTCAR(outcar_path)
            results = outcar.read()
            
            print(f"   最终能量: {results.get('final_energy', '未找到')} eV")
            print(f"   收敛状态: {'✅ 已收敛' if results.get('convergence') else '❌ 未收敛'}")
            print(f"   费米能级: {outcar.fermi_energy} eV")
            print(f"   能量步数: {len(results.get('energies', []))}")
            print(f"   离子步数: {len(results.get('forces', []))}")
            
            # 计算信息
            calc_info = results.get('calculation_info', {})
            if calc_info:
                print("\n🔧 计算信息:")
                for key, value in calc_info.items():
                    print(f"   {key}: {value}")
            
            # 最终力信息
            final_forces = results.get('final_forces')
            if final_forces is not None:
                max_force = abs(final_forces).max()
                print(f"\n⚡ 力信息:")
                print(f"   最大力: {max_force:.6f} eV/Å")
                print(f"   力收敛: {'✅ 已收敛' if max_force < 0.01 else '❌ 未收敛'}")
            
            # 应力信息
            final_stress = results.get('final_stress')
            if final_stress is not None:
                max_stress = abs(final_stress).max()
                print(f"\n🔧 应力信息:")
                print(f"   最大应力: {max_stress:.6f} kBar")
                
        except Exception as e:
            print(f"   ❌ OUTCAR解析失败: {e}")
    
    # 分析DOSCAR
    doscar_path = calc_path / "DOSCAR"
    if doscar_path.exists():
        print("\n📈 DOSCAR分析:")
        try:
            doscar = DOSCAR(doscar_path)
            dos_data = doscar.read()
            
            print(f"   原子数: {dos_data.get('natoms', '未知')}")
            print(f"   能量点数: {dos_data.get('nedos', '未知')}")
            print(f"   费米能级: {dos_data.get('fermi_energy', '未知')} eV")
            print(f"   自旋极化: {'是' if dos_data.get('is_spin_polarized') else '否'}")
            
            # 费米能级处的态密度
            try:
                dos_at_fermi = doscar.get_dos_at_fermi()
                print(f"   费米能级处态密度: {dos_at_fermi:.6f}")
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ DOSCAR解析失败: {e}")
    
    # 分析结构变化
    poscar_path = calc_path / "POSCAR"
    contcar_path = calc_path / "CONTCAR"
    
    if poscar_path.exists() and contcar_path.exists():
        print("\n🏗️ 结构分析:")
        try:
            initial_poscar = POSCAR(poscar_path)
            final_poscar = POSCAR(contcar_path)
            
            initial_structure = initial_poscar.read()
            final_structure = final_poscar.read()
            
            print(f"   初始体积: {initial_structure['volume']:.3f} Å³")
            print(f"   最终体积: {final_structure['volume']:.3f} Å³")
            
            volume_change = (final_structure['volume'] - initial_structure['volume']) / initial_structure['volume'] * 100
            print(f"   体积变化: {volume_change:+.2f}%")
            
        except Exception as e:
            print(f"   ❌ 结构分析失败: {e}")
    
    # 计算状态总结
    print("\n📋 计算状态总结:")
    if files_status.get('OUTCAR'):
        if results.get('convergence'):
            print("   ✅ 计算成功完成并收敛")
        else:
            print("   ⚠️  计算完成但可能未收敛")
    else:
        print("   ❌ 计算未完成或失败")
    
    # 建议
    print("\n💡 建议:")
    if not files_status.get('OUTCAR'):
        print("   - 检查计算是否正在运行")
        print("   - 查看错误日志文件")
    elif not results.get('convergence'):
        print("   - 增加NSW步数")
        print("   - 调整EDIFF和EDIFFG参数")
        print("   - 检查结构是否合理")

def main():
    parser = argparse.ArgumentParser(description='分析VASP计算结果')
    parser.add_argument('directory', help='计算目录路径')
    parser.add_argument('--detailed', action='store_true', help='详细分析')
    
    args = parser.parse_args()
    
    analyze_calculation(args.directory)

if __name__ == "__main__":
    main()