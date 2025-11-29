"""
WVasp安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# 读取版本信息
version = "0.1.0"

setup(
    name="wvasp",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python toolkit for VASP calculations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wvasp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "wvasp=wvasp.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
