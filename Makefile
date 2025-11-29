# WVasp开发工具

.PHONY: help install install-dev test test-cov lint format clean build upload

help:  ## 显示帮助信息
	@echo "WVasp开发工具"
	@echo ""
	@echo "可用命令:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## 安装包
	pip install -e .

install-dev:  ## 安装开发依赖
	pip install -e ".[dev]"
	pre-commit install

test:  ## 运行测试
	pytest tests/

test-cov:  ## 运行测试并生成覆盖率报告
	pytest --cov=wvasp --cov-report=html --cov-report=term tests/

lint:  ## 代码检查
	flake8 wvasp/ tests/
	mypy wvasp/

format:  ## 格式化代码
	black wvasp/ tests/

clean:  ## 清理构建文件
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## 构建包
	python -m build

upload:  ## 上传到PyPI (需要先构建)
	python -m twine upload dist/*

demo:  ## 运行演示
	@echo "创建演示POSCAR文件..."
	@mkdir -p demo
	@echo "Si2" > demo/POSCAR
	@echo "1.0" >> demo/POSCAR
	@echo "5.4 0.0 0.0" >> demo/POSCAR
	@echo "0.0 5.4 0.0" >> demo/POSCAR
	@echo "0.0 0.0 5.4" >> demo/POSCAR
	@echo "Si" >> demo/POSCAR
	@echo "2" >> demo/POSCAR
	@echo "Direct" >> demo/POSCAR
	@echo "0.0 0.0 0.0" >> demo/POSCAR
	@echo "0.25 0.25 0.25" >> demo/POSCAR
	@echo "运行WVasp演示..."
	python -m wvasp poscar demo/POSCAR --info
