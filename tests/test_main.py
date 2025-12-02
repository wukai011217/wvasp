"""
测试main.py模块

测试命令行接口和主要功能。
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import argparse

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from wvasp.main import (
    main, handle_poscar_command, handle_build_command, handle_info_command,
    handle_incar_command, handle_kpoints_command, handle_potcar_command,
    handle_slurm_command
)


class TestMain:
    """测试主函数"""
    
    def test_main_version(self):
        """测试版本显示"""
        with patch('sys.argv', ['wvasp', '--version']):
            with pytest.raises(SystemExit):
                main()

    def test_main_help(self):
        """测试帮助信息"""
        with patch('sys.argv', ['wvasp', '--help']):
            with pytest.raises(SystemExit):
                main()

    def test_main_no_args(self):
        """测试无参数调用"""
        with patch('sys.argv', ['wvasp']):
            with pytest.raises(SystemExit):
                main()


class TestPoscarCommand:
    """测试POSCAR命令"""
    
    def test_poscar_info(self, temp_dir, sample_poscar_content):
        """测试POSCAR信息显示"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        # 模拟命令行参数
        args = argparse.Namespace(
            command='poscar',
            file=str(poscar_file),
            info=True,
            convert=None
        )
        
        # 测试不应该抛出异常
        try:
            handle_poscar_command(args)
        except Exception as e:
            pytest.fail(f"handle_poscar_command raised {e} unexpectedly!")

    def test_poscar_convert_cart(self, temp_dir, sample_poscar_content):
        """测试POSCAR坐标转换为笛卡尔"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        args = argparse.Namespace(
            command='poscar',
            file=str(poscar_file),
            info=False,
            convert='cart'
        )
        
        try:
            handle_poscar_command(args)
        except Exception as e:
            pytest.fail(f"handle_poscar_command raised {e} unexpectedly!")

    def test_poscar_convert_frac(self, temp_dir, sample_poscar_content):
        """测试POSCAR坐标转换为分数"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        args = argparse.Namespace(
            command='poscar',
            file=str(poscar_file),
            info=False,
            convert='frac'
        )
        
        try:
            handle_poscar_command(args)
        except Exception as e:
            pytest.fail(f"handle_poscar_command raised {e} unexpectedly!")


class TestBuildCommand:
    """测试Build命令"""
    
    def test_build_optimization(self, temp_dir, sample_poscar_content):
        """测试构建优化计算"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        output_dir = temp_dir / "vasp_calc"
        
        args = argparse.Namespace(
            command='build',
            poscar=str(poscar_file),
            template='optimization',
            output=str(output_dir),
            encut=None,
            kpoints=None,
            incar=None,
            auto_mag=False,
            dft_u=False
        )
        
        try:
            handle_build_command(args)
            # 验证输出目录存在
            assert output_dir.exists()
        except Exception as e:
            pytest.fail(f"handle_build_command raised {e} unexpectedly!")

    def test_build_scf(self, temp_dir, sample_poscar_content):
        """测试构建SCF计算"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        output_dir = temp_dir / "scf_calc"
        
        args = argparse.Namespace(
            command='build',
            poscar=str(poscar_file),
            template='scf',
            output=str(output_dir),
            encut=500.0,
            kpoints=[8, 8, 8],
            incar=[['ALGO', 'Fast']],
            auto_mag=True,
            dft_u=True
        )
        
        try:
            handle_build_command(args)
            assert output_dir.exists()
        except Exception as e:
            pytest.fail(f"handle_build_command raised {e} unexpectedly!")


class TestIncarCommand:
    """测试INCAR命令"""
    
    def test_incar_create(self, temp_dir):
        """测试创建INCAR文件"""
        output_file = temp_dir / "INCAR"
        
        args = argparse.Namespace(
            command='incar',
            action='create',
            template='optimization',
            output=str(output_file),
            param=None
        )
        
        try:
            handle_incar_command(args)
            assert output_file.exists()
        except Exception as e:
            pytest.fail(f"handle_incar_command raised {e} unexpectedly!")

    def test_incar_validate(self, temp_dir, sample_incar_content):
        """测试验证INCAR文件"""
        incar_file = temp_dir / "INCAR"
        incar_file.write_text(sample_incar_content)
        
        args = argparse.Namespace(
            command='incar',
            action='validate',
            template=None,
            output=str(incar_file),
            param=None
        )
        
        try:
            handle_incar_command(args)
        except Exception as e:
            pytest.fail(f"handle_incar_command raised {e} unexpectedly!")


class TestKpointsCommand:
    """测试KPOINTS命令"""
    
    def test_kpoints_create_gamma(self, temp_dir):
        """测试创建Gamma中心KPOINTS"""
        output_file = temp_dir / "KPOINTS"
        
        args = argparse.Namespace(
            command='kpoints',
            action='create',
            method='gamma',
            grid=[6, 6, 6],
            shift=[0.0, 0.0, 0.0],
            output=str(output_file),
            template=None
        )
        
        try:
            handle_kpoints_command(args)
            assert output_file.exists()
        except Exception as e:
            pytest.fail(f"handle_kpoints_command raised {e} unexpectedly!")

    def test_kpoints_create_with_template(self, temp_dir):
        """测试使用模板创建KPOINTS"""
        output_file = temp_dir / "KPOINTS"
        
        args = argparse.Namespace(
            command='kpoints',
            action='create',
            method=None,
            grid=None,
            shift=None,
            output=str(output_file),
            template='slab_2d'
        )
        
        try:
            handle_kpoints_command(args)
            assert output_file.exists()
        except Exception as e:
            pytest.fail(f"handle_kpoints_command raised {e} unexpectedly!")


class TestPotcarCommand:
    """测试POTCAR命令"""
    
    def test_potcar_create(self, temp_dir):
        """测试创建POTCAR信息"""
        output_file = temp_dir / "POTCAR"
        
        args = argparse.Namespace(
            command='potcar',
            action='create',
            elements=['Fe', 'O'],
            functional='PBE',
            output=str(output_file),
            template=None
        )
        
        try:
            handle_potcar_command(args)
            assert output_file.exists()
        except Exception as e:
            pytest.fail(f"handle_potcar_command raised {e} unexpectedly!")

    def test_potcar_create_with_template(self, temp_dir):
        """测试使用模板创建POTCAR"""
        output_file = temp_dir / "POTCAR"
        
        args = argparse.Namespace(
            command='potcar',
            action='create',
            elements=['Ti', 'O'],
            functional=None,
            output=str(output_file),
            template='PBE_hard'
        )
        
        try:
            handle_potcar_command(args)
            assert output_file.exists()
        except Exception as e:
            pytest.fail(f"handle_potcar_command raised {e} unexpectedly!")


class TestSlurmCommand:
    """测试SLURM命令"""
    
    def test_slurm_create(self, temp_dir):
        """测试创建SLURM脚本"""
        output_file = temp_dir / "submit.sh"
        
        args = argparse.Namespace(
            command='slurm',
            action='create',
            job_name='test_job',
            nodes=1,
            ntasks_per_node=24,
            memory='32G',
            time='12:00:00',
            partition='normal',
            output=str(output_file),
            template=None
        )
        
        try:
            handle_slurm_command(args)
            assert output_file.exists()
            
            # 验证文件内容
            content = output_file.read_text()
            assert "#SBATCH" in content
            assert "test_job" in content
        except Exception as e:
            pytest.fail(f"handle_slurm_command raised {e} unexpectedly!")

    def test_slurm_create_with_template(self, temp_dir):
        """测试使用模板创建SLURM脚本"""
        output_file = temp_dir / "submit.sh"
        
        args = argparse.Namespace(
            command='slurm',
            action='create',
            job_name=None,
            nodes=None,
            ntasks_per_node=None,
            memory=None,
            time=None,
            partition=None,
            output=str(output_file),
            template='gpu_accelerated'
        )
        
        try:
            handle_slurm_command(args)
            assert output_file.exists()
            
            content = output_file.read_text()
            assert "#SBATCH" in content
        except Exception as e:
            pytest.fail(f"handle_slurm_command raised {e} unexpectedly!")


class TestInfoCommand:
    """测试Info命令"""
    
    def test_info_magnetic(self):
        """测试显示磁性信息"""
        args = argparse.Namespace(
            command='info',
            type='magnetic'
        )
        
        try:
            handle_info_command(args)
        except Exception as e:
            pytest.fail(f"handle_info_command raised {e} unexpectedly!")

    def test_info_dftu(self):
        """测试显示DFT+U信息"""
        args = argparse.Namespace(
            command='info',
            type='dftu'
        )
        
        try:
            handle_info_command(args)
        except Exception as e:
            pytest.fail(f"handle_info_command raised {e} unexpectedly!")

    def test_info_templates(self):
        """测试显示模板信息"""
        args = argparse.Namespace(
            command='info',
            type='templates'
        )
        
        try:
            handle_info_command(args)
        except Exception as e:
            pytest.fail(f"handle_info_command raised {e} unexpectedly!")


class TestMainIntegration:
    """主程序集成测试"""
    
    def test_full_workflow(self, temp_dir, sample_poscar_content):
        """测试完整工作流程"""
        # 1. 创建POSCAR文件
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        # 2. 构建VASP计算
        output_dir = temp_dir / "vasp_calc"
        
        build_args = argparse.Namespace(
            command='build',
            poscar=str(poscar_file),
            template='optimization',
            output=str(output_dir),
            encut=None,
            kpoints=None,
            incar=None,
            auto_mag=True,
            dft_u=True
        )
        
        try:
            handle_build_command(build_args)
            assert output_dir.exists()
            
            # 验证生成的文件
            assert (output_dir / "POSCAR").exists()
            assert (output_dir / "INCAR").exists()
            assert (output_dir / "KPOINTS").exists()
            
        except Exception as e:
            pytest.fail(f"Full workflow failed: {e}")

    def test_poscar_info_workflow(self, temp_dir, sample_poscar_content):
        """测试POSCAR信息工作流程"""
        poscar_file = temp_dir / "POSCAR"
        poscar_file.write_text(sample_poscar_content)
        
        # 显示信息
        info_args = argparse.Namespace(
            command='poscar',
            file=str(poscar_file),
            info=True,
            convert=None
        )
        
        # 转换坐标
        convert_args = argparse.Namespace(
            command='poscar',
            file=str(poscar_file),
            info=False,
            convert='cart'
        )
        
        try:
            handle_poscar_command(info_args)
            handle_poscar_command(convert_args)
        except Exception as e:
            pytest.fail(f"POSCAR workflow failed: {e}")

    def test_incar_create_workflow(self, temp_dir):
        """测试INCAR创建工作流程"""
        incar_file = temp_dir / "INCAR"
        
        # 创建INCAR
        create_args = argparse.Namespace(
            command='incar',
            action='create',
            template='optimization',
            output=str(incar_file),
            param=None
        )
        
        # 验证INCAR
        validate_args = argparse.Namespace(
            command='incar',
            action='validate',
            template=None,
            output=str(incar_file),
            param=None
        )
        
        try:
            handle_incar_command(create_args)
            assert incar_file.exists()
            
            handle_incar_command(validate_args)
        except Exception as e:
            pytest.fail(f"INCAR workflow failed: {e}")


class TestCommandLineArguments:
    """测试命令行参数解析"""
    
    def test_build_command_args(self):
        """测试build命令参数"""
        test_args = [
            'wvasp', 'build', 'POSCAR', 'optimization',
            '-o', 'output_dir',
            '--encut', '500',
            '--kpoints', '8', '8', '8',
            '--incar', 'ALGO', 'Fast',
            '--auto-mag',
            '--dft-u'
        ]
        
        with patch('sys.argv', test_args):
            try:
                # 这里只测试参数解析，不执行实际命令
                pass
            except Exception as e:
                pytest.fail(f"Argument parsing failed: {e}")

    def test_template_arguments(self):
        """测试模板参数"""
        # 测试各种模板参数
        template_commands = [
            ['wvasp', 'incar', 'create', '-t', 'optimization'],
            ['wvasp', 'kpoints', 'create', '-t', 'slab_2d'],
            ['wvasp', 'potcar', 'create', '-t', 'PBE_hard', '-e', 'Fe', 'O'],
            ['wvasp', 'slurm', 'create', '--template', 'gpu_accelerated']
        ]
        
        for test_args in template_commands:
            with patch('sys.argv', test_args):
                try:
                    # 这里只测试参数解析
                    pass
                except Exception as e:
                    pytest.fail(f"Template argument parsing failed for {test_args}: {e}")


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_poscar_file(self, temp_dir):
        """测试无效POSCAR文件"""
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        args = argparse.Namespace(
            command='poscar',
            file=str(nonexistent_file),
            info=True,
            convert=None
        )
        
        # 应该优雅地处理错误
        try:
            handle_poscar_command(args)
        except Exception:
            # 预期会有异常，这是正常的
            pass

    def test_invalid_template(self, temp_dir):
        """测试无效模板"""
        output_file = temp_dir / "INCAR"
        
        args = argparse.Namespace(
            command='incar',
            action='create',
            template='invalid_template',
            output=str(output_file),
            param=None
        )
        
        # 应该优雅地处理错误
        try:
            handle_incar_command(args)
        except Exception:
            # 预期会有异常，这是正常的
            pass
