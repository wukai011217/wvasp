"""
具体计算任务类

实现常见的VASP计算任务，如结构优化、态密度计算、能带计算等。
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np

from .base_task import BaseTask, TaskConfig, TaskStatus
from ..analysis import EnergyAnalyzer


class OptimizationTask(BaseTask):
    """结构优化任务"""
    
    def __init__(self, config: TaskConfig, 
                 encut: float = 400.0,
                 kpoints: Tuple[int, int, int] = (6, 6, 6),
                 ediff: float = 1e-6,
                 ediffg: float = -0.01,
                 nsw: int = 100):
        """
        初始化结构优化任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpoints: K点网格
            ediff: 电子收敛标准
            ediffg: 离子收敛标准
            nsw: 最大离子步数
        """
        super().__init__(config)
        self.encut = encut
        self.kpoints_grid = kpoints
        self.ediff = ediff
        self.ediffg = ediffg
        self.nsw = nsw
    
    def setup_incar(self) -> None:
        """设置结构优化的INCAR参数"""
        from ...utils.parameter_manager import create_optimization_config
        
        # 创建优化配置模板
        param_config = create_optimization_config()
        
        # 从任务配置中覆盖参数
        if hasattr(self.config, 'incar_params') and self.config.incar_params:
            param_config.update_parameters(self.config.incar_params)
        
        # 设置任务特定的参数
        param_config.set_parameter('SYSTEM', f'{self.config.name} optimization')
        
        # 如果任务有自定义的参数，使用它们
        if hasattr(self, 'encut') and self.encut:
            param_config.set_parameter('ENCUT', self.encut)
        if hasattr(self, 'ediff') and self.ediff:
            param_config.set_parameter('EDIFF', self.ediff)
        if hasattr(self, 'ediffg') and self.ediffg:
            param_config.set_parameter('EDIFFG', self.ediffg)
        if hasattr(self, 'nsw') and self.nsw:
            param_config.set_parameter('NSW', self.nsw)
        
        # 验证所有参数
        if not param_config.validate_all():
            errors = param_config.get_validation_errors()
            raise ValueError(f"Invalid INCAR parameters: {errors}")
        
        # 应用所有参数到INCAR
        for name, value in param_config.get_all_parameters().items():
            self.incar.set_parameter(name, value)
    
    def setup_kpoints(self) -> None:
        """设置K点网格"""
        from ..io import KPOINTS
        self.kpoints = KPOINTS.create_gamma_centered(list(self.kpoints_grid))
    
    def check_results(self) -> Dict[str, Any]:
        """检查结构优化结果"""
        results = {}
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        if outcar_path.exists():
            try:
                outcar_data = energy_analyzer.read()
                
                results.update({
                    "converged": outcar_data.get("convergence", False),
                    "final_energy": outcar_data.get("final_energy"),
                    "energy_change": outcar_data.get("energies", [])[-1] - outcar_data.get("energies", [0])[0] if outcar_data.get("energies") else None,
                    "ionic_steps": len(outcar_data.get("energies", [])),
                    "max_force": np.max(np.abs(energy_analyzer.final_forces)) if energy_analyzer.final_forces is not None else None,
                    "volume_change": outcar_data.get("volume_change"),
                })
                
                self.status = TaskStatus.COMPLETED
                
            except Exception as e:
                self.errors.append(f"结果分析失败: {e}")
                self.status = TaskStatus.FAILED
        else:
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results


class DOSTask(BaseTask):
    """态密度计算任务"""
    
    def __init__(self, config: TaskConfig,
                 encut: float = 400.0,
                 kpoints: Tuple[int, int, int] = (8, 8, 8),
                 nedos: int = 2000):
        """
        初始化态密度计算任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpoints: K点网格
            nedos: 态密度能量点数
        """
        super().__init__(config)
        self.encut = encut
        self.kpoints_grid = kpoints
        self.nedos = nedos
    
    def setup_incar(self) -> None:
        """设置态密度计算的INCAR参数"""
        self.incar.set_parameter('SYSTEM', f'{self.config.name} DOS calculation')
        self.incar.set_parameter('ISTART', 0)
        self.incar.set_parameter('ICHARG', 2)
        self.incar.set_parameter('ENCUT', self.encut)
        self.incar.set_parameter('ISMEAR', -5)  # 四面体方法
        self.incar.set_parameter('LORBIT', 11)  # 输出DOSCAR和PROCAR
        self.incar.set_parameter('NEDOS', self.nedos)
        self.incar.set_parameter('EMIN', -10.0)
        self.incar.set_parameter('EMAX', 10.0)
        self.incar.set_parameter('NSW', 0)      # 静态计算
        self.incar.set_parameter('LREAL', False)
        self.incar.set_parameter('PREC', 'Accurate')
    
    def setup_kpoints(self) -> None:
        """设置密集K点网格"""
        from ..io import KPOINTS
        self.kpoints = KPOINTS.create_gamma_centered(list(self.kpoints_grid))
    
    def check_results(self) -> Dict[str, Any]:
        """检查计算完成状态和基本结果"""
        results = {}
        
        # 检查必要文件
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        doscar_path = self.config.work_dir / "DOSCAR"
        
        if not outcar_path.exists():
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
            return results
            
        if not doscar_path.exists():
            self.errors.append("DOSCAR文件不存在")
            self.status = TaskStatus.FAILED
            return results
        
        try:
            # 基本完成性检查
            outcar_data = energy_analyzer.read()
            
            # 检查计算是否正常完成
            if outcar_data.get("convergence", False):
                results["calculation_completed"] = True
                results["converged"] = True
            else:
                results["calculation_completed"] = True
                results["converged"] = False
                self.errors.append("计算未收敛")
            
            # 基本信息
            results["fermi_energy"] = energy_analyzer.fermi_energy
            results["total_energy"] = outcar_data.get("final_energy")
            
            self.status = TaskStatus.COMPLETED
            
        except Exception as e:
            self.errors.append(f"结果检查失败: {e}")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results
    
    def get_detailed_analysis(self):
        """获取详细的DOS分析 - 委托给analysis模块"""
        from ..analysis import DOSAnalyzer
        
        if self.status != TaskStatus.COMPLETED:
            raise ValueError("任务未完成，无法进行详细分析")
        
        doscar_path = self.config.work_dir / "DOSCAR"
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        
        analyzer = DOSAnalyzer(doscar_path, outcar_path)
        return analyzer.analyze_electronic_structure()


class BandTask(BaseTask):
    """能带计算任务"""
    
    def __init__(self, config: TaskConfig,
                 encut: float = 400.0,
                 kpath_density: int = 20):
        """
        初始化能带计算任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpath_density: K路径密度
        """
        super().__init__(config)
        self.encut = encut
        self.kpath_density = kpath_density
    
    def setup_incar(self) -> None:
        """设置能带计算的INCAR参数"""
        from ...utils.parameter_manager import create_band_config
        
        # 创建能带配置模板
        param_config = create_band_config()
        
        # 从任务配置中覆盖参数
        if hasattr(self.config, 'incar_params') and self.config.incar_params:
            param_config.update_parameters(self.config.incar_params)
        
        # 设置任务特定的参数
        param_config.set_parameter('SYSTEM', f'{self.config.name} band calculation')
        
        # 如果任务有自定义的参数，使用它们
        if hasattr(self, 'encut') and self.encut:
            param_config.set_parameter('ENCUT', self.encut)
        
        # 验证所有参数
        if not param_config.validate_all():
            errors = param_config.get_validation_errors()
            raise ValueError(f"Invalid INCAR parameters: {errors}")
        
        # 应用所有参数到INCAR
        for name, value in param_config.get_all_parameters().items():
            self.incar.set_parameter(name, value)
    
    def setup_kpoints(self) -> None:
        """设置能带K路径"""
        # 这里需要根据晶体结构生成高对称点路径
        # 简化版本，使用线性路径
        from ..io import KPOINTS
        kpoints_list = [
            [0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.0, 0.0, 0.0],
        ]
        weights = [1.0] * len(kpoints_list)
        self.kpoints = KPOINTS.create_explicit(kpoints_list, weights, "Band structure k-path")
    
    def check_results(self) -> Dict[str, Any]:
        """检查能带计算完成状态"""
        results = {}
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        if not outcar_path.exists():
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
            return results
        
        try:
            # 基本完成性检查
            outcar_data = energy_analyzer.read()
            
            # 检查计算是否正常完成
            if outcar_data.get("convergence", False):
                results["calculation_completed"] = True
                results["converged"] = True
            else:
                results["calculation_completed"] = True
                results["converged"] = False
                self.errors.append("计算未收敛")
            
            # 基本信息
            results["fermi_energy"] = energy_analyzer.fermi_energy
            results["has_eigenvalues"] = energy_analyzer.eigenvalues is not None
            results["has_kpoints"] = energy_analyzer.kpoints is not None
            
            self.status = TaskStatus.COMPLETED
            
        except Exception as e:
            self.errors.append(f"结果检查失败: {e}")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results
    
    def get_detailed_analysis(self):
        """获取详细的能带分析 - 委托给analysis模块"""
        from ..analysis import BandAnalyzer
        
        if self.status != TaskStatus.COMPLETED:
            raise ValueError("任务未完成，无法进行详细分析")
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        analyzer = BandAnalyzer(outcar_path)
        return analyzer.analyze_electronic_structure()


class SinglePointTask(BaseTask):
    """单点能量计算任务"""
    
    def __init__(self, config: TaskConfig,
                 encut: float = 400.0,
                 kpoints: Tuple[int, int, int] = (6, 6, 6),
                 ismear: int = 0,
                 sigma: float = 0.05):
        """
        初始化单点计算任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpoints: K点网格
            ismear: 展宽方法
            sigma: 展宽参数
        """
        super().__init__(config)
        self.encut = encut
        self.kpoints_grid = kpoints
        self.ismear = ismear
        self.sigma = sigma
    
    def setup_incar(self) -> None:
        """设置单点计算的INCAR参数"""
        self.incar.set_parameter('SYSTEM', f'{self.config.name} single point')
        self.incar.set_parameter('ISTART', 0)
        self.incar.set_parameter('ICHARG', 2)
        self.incar.set_parameter('ENCUT', self.encut)
        self.incar.set_parameter('ISMEAR', self.ismear)
        self.incar.set_parameter('SIGMA', self.sigma)
        self.incar.set_parameter('NSW', 0)      # 静态计算
        self.incar.set_parameter('IBRION', -1)  # 不进行离子移动
        self.incar.set_parameter('LREAL', False)
        self.incar.set_parameter('PREC', 'Accurate')
    
    def setup_kpoints(self) -> None:
        """设置K点网格"""
        from ..io import KPOINTS
        self.kpoints = KPOINTS.create_gamma_centered(list(self.kpoints_grid))
    
    def check_results(self) -> Dict[str, Any]:
        """检查单点计算结果"""
        results = {}
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        if outcar_path.exists():
            try:
                outcar_data = energy_analyzer.read()
                
                results.update({
                    "total_energy": outcar_data.get("final_energy"),
                    "fermi_energy": energy_analyzer.fermi_energy,
                    "forces": energy_analyzer.final_forces,
                    "stress": energy_analyzer.final_stress,
                    "electronic_steps": len(outcar_data.get("energies", [])),
                    "converged": outcar_data.get("convergence", False),
                })
                
                self.status = TaskStatus.COMPLETED
                
            except Exception as e:
                self.errors.append(f"单点计算分析失败: {e}")
                self.status = TaskStatus.FAILED
        else:
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results


class MolecularDynamicsTask(BaseTask):
    """分子动力学计算任务"""
    
    def __init__(self, config: TaskConfig,
                 encut: float = 400.0,
                 kpoints: Tuple[int, int, int] = (1, 1, 1),
                 temperature: float = 300.0,
                 time_step: float = 1.0,
                 md_steps: int = 1000,
                 ensemble: str = "NVT"):
        """
        初始化分子动力学任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpoints: K点网格
            temperature: 温度 (K)
            time_step: 时间步长 (fs)
            md_steps: MD步数
            ensemble: 系综类型 (NVT, NVE, NPT)
        """
        super().__init__(config)
        self.encut = encut
        self.kpoints_grid = kpoints
        self.temperature = temperature
        self.time_step = time_step
        self.md_steps = md_steps
        self.ensemble = ensemble.upper()
    
    def setup_incar(self) -> None:
        """设置分子动力学的INCAR参数"""
        self.incar.set_parameter('SYSTEM', f'{self.config.name} MD simulation')
        self.incar.set_parameter('ISTART', 0)
        self.incar.set_parameter('ICHARG', 2)
        self.incar.set_parameter('ENCUT', self.encut)
        self.incar.set_parameter('ISMEAR', 0)
        self.incar.set_parameter('SIGMA', 0.05)
        
        # MD相关参数
        self.incar.set_parameter('NSW', self.md_steps)
        self.incar.set_parameter('IBRION', 0)    # MD模式
        self.incar.set_parameter('POTIM', self.time_step)
        self.incar.set_parameter('TEBEG', self.temperature)
        self.incar.set_parameter('TEEND', self.temperature)
        
        # 系综设置
        if self.ensemble == "NVT":
            self.incar.set_parameter('MDALGO', 2)  # Nose-Hoover恒温器
        elif self.ensemble == "NVE":
            self.incar.set_parameter('MDALGO', 1)  # 微正则系综
        elif self.ensemble == "NPT":
            self.incar.set_parameter('MDALGO', 3)  # Langevin恒温恒压
            self.incar.set_parameter('PSTRESS', 0.0)
        
        self.incar.set_parameter('LREAL', 'Auto')  # MD通常使用实空间投影
        self.incar.set_parameter('PREC', 'Normal')
        self.incar.set_parameter('NWRITE', 2)     # 输出轨迹
    
    def setup_kpoints(self) -> None:
        """设置K点网格 (MD通常使用较少K点)"""
        from ..io import KPOINTS
        self.kpoints = KPOINTS.create_gamma_centered(list(self.kpoints_grid))
    
    def check_results(self) -> Dict[str, Any]:
        """检查MD计算完成状态"""
        results = {}
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        if not outcar_path.exists():
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
            return results
        
        try:
            # 基本完成性检查
            outcar_data = energy_analyzer.read()
            
            # 检查MD步数
            md_steps = len(outcar_data.get("energies", []))
            results["md_steps_completed"] = md_steps
            results["calculation_completed"] = md_steps > 0
            
            if md_steps > 0:
                results["final_energy"] = outcar_data.get("final_energy")
                self.status = TaskStatus.COMPLETED
            else:
                self.errors.append("MD计算未正常完成")
                self.status = TaskStatus.FAILED
            
        except Exception as e:
            self.errors.append(f"结果检查失败: {e}")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results
    
    def get_detailed_analysis(self):
        """获取详细的MD分析 - 委托给analysis模块"""
        from ..analysis import MDAnalyzer
        
        if self.status != TaskStatus.COMPLETED:
            raise ValueError("任务未完成，无法进行详细分析")
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        analyzer = MDAnalyzer(outcar_path)
        return analyzer.analyze_trajectory()


class TransitionStateTask(BaseTask):
    """过渡态搜索任务 (NEB方法)"""
    
    def __init__(self, config: TaskConfig,
                 encut: float = 400.0,
                 kpoints: Tuple[int, int, int] = (3, 3, 3),
                 nimages: int = 5,
                 spring_constant: float = -5.0,
                 climbing_image: bool = True):
        """
        初始化过渡态搜索任务
        
        Args:
            config: 任务配置
            encut: 截断能
            kpoints: K点网格
            nimages: 中间像数量
            spring_constant: 弹簧常数
            climbing_image: 是否使用climbing image
        """
        super().__init__(config)
        self.encut = encut
        self.kpoints_grid = kpoints
        self.nimages = nimages
        self.spring_constant = spring_constant
        self.climbing_image = climbing_image
    
    def setup_incar(self) -> None:
        """设置NEB计算的INCAR参数"""
        self.incar.set_parameter('SYSTEM', f'{self.config.name} NEB calculation')
        self.incar.set_parameter('ISTART', 0)
        self.incar.set_parameter('ICHARG', 2)
        self.incar.set_parameter('ENCUT', self.encut)
        self.incar.set_parameter('ISMEAR', 0)
        self.incar.set_parameter('SIGMA', 0.05)
        
        # NEB相关参数
        self.incar.set_parameter('IMAGES', self.nimages)
        self.incar.set_parameter('LNEB', True)
        self.incar.set_parameter('SPRING', self.spring_constant)
        
        if self.climbing_image:
            self.incar.set_parameter('LCLIMB', True)
        
        # 优化参数
        self.incar.set_parameter('NSW', 200)
        self.incar.set_parameter('IBRION', 3)    # 快速下降法
        self.incar.set_parameter('EDIFFG', -0.05)  # 较松的收敛标准
        
        self.incar.set_parameter('LREAL', False)
        self.incar.set_parameter('PREC', 'Accurate')
    
    def setup_kpoints(self) -> None:
        """设置K点网格 (NEB通常使用较少K点)"""
        from ..io import KPOINTS
        self.kpoints = KPOINTS.create_gamma_centered(list(self.kpoints_grid))
    
    def check_results(self) -> Dict[str, Any]:
        """检查NEB计算完成状态"""
        results = {}
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        if not outcar_path.exists():
            self.errors.append("OUTCAR文件不存在")
            self.status = TaskStatus.FAILED
            return results
        
        try:
            # 基本完成性检查
            outcar_data = energy_analyzer.read()
            
            # 检查计算是否正常完成
            results["converged"] = outcar_data.get("convergence", False)
            results["ionic_steps"] = len(outcar_data.get("energies", []))
            results["calculation_completed"] = results["ionic_steps"] > 0
            
            if not results["converged"]:
                self.errors.append("NEB计算未收敛")
            
            self.status = TaskStatus.COMPLETED
            
        except Exception as e:
            self.errors.append(f"结果检查失败: {e}")
            self.status = TaskStatus.FAILED
        
        self.results = results
        return results
    
    def get_detailed_analysis(self):
        """获取详细的NEB分析 - 委托给analysis模块"""
        from ..analysis import NEBAnalyzer
        
        if self.status != TaskStatus.COMPLETED:
            raise ValueError("任务未完成，无法进行详细分析")
        
        outcar_path = self.config.work_dir / "OUTCAR"
        energy_analyzer = EnergyAnalyzer(outcar_path)
        analyzer = NEBAnalyzer(outcar_path)
        return analyzer.analyze_transition_state()