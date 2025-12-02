#!/usr/bin/env python3
"""
WVasp测试运行脚本

提供多种测试运行选项和覆盖率报告。
"""

import sys
import subprocess
from pathlib import Path
import argparse


def run_command(cmd, description=""):
    """运行命令并处理输出"""
    print(f"\n{'='*60}")
    if description:
        print(f"🚀 {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="WVasp测试运行器")
    
    parser.add_argument(
        "--module", "-m",
        choices=["all", "main", "io", "parameters", "base"],
        default="all",
        help="选择要测试的模块"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="生成覆盖率报告"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="快速测试（跳过慢速测试）"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="生成HTML覆盖率报告"
    )
    
    args = parser.parse_args()
    
    # 确保在正确的目录中
    project_root = Path(__file__).parent
    if not (project_root / "wvasp").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 选择测试模块
    if args.module == "main":
        cmd.extend(["tests/test_main_fixed.py"])
    elif args.module == "io":
        cmd.extend(["tests/test_core_io.py"])
    elif args.module == "parameters":
        cmd.extend(["tests/test_parameters.py"])
    elif args.module == "base":
        cmd.extend(["tests/test_core_base.py"])
    else:
        cmd.extend(["tests/"])
    
    # 添加选项
    if args.verbose:
        cmd.extend(["-v", "-s"])
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.coverage:
        cmd.extend([
            "--cov=wvasp",
            "--cov-report=term-missing"
        ])
        
        if args.html:
            cmd.extend(["--cov-report=html:htmlcov"])
    
    # 运行测试
    success = run_command(cmd, f"运行{args.module}模块测试")
    
    if success:
        print("\n✅ 测试完成!")
        
        if args.coverage and args.html:
            html_report = project_root / "htmlcov" / "index.html"
            if html_report.exists():
                print(f"📊 HTML覆盖率报告: {html_report}")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
