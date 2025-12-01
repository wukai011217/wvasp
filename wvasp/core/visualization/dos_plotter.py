"""
态密度绘图模块

提供态密度数据的可视化功能。
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from ..analysis.dos_analysis import DOSAnalyzer


class DOSPlotter:
    """态密度绘图器"""
    
    def __init__(self, dos_analyzer: DOSAnalyzer):
        """
        初始化DOS绘图器
        
        Args:
            dos_analyzer: DOS分析器
        """
        self.analyzer = dos_analyzer
        self.fig = None
        self.ax = None
        
    def setup_plot(self, figsize: Tuple[float, float] = (10, 6), 
                   style: str = 'seaborn-v0_8') -> None:
        """
        设置绘图环境
        
        Args:
            figsize: 图形尺寸
            style: 绘图样式
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
            
        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=300)
        
    def plot_total_dos(self, energy_range: Optional[Tuple[float, float]] = None,
                      show_fermi: bool = True, **kwargs) -> None:
        """
        绘制总态密度
        
        Args:
            energy_range: 能量范围 (emin, emax)，相对于费米能级
            show_fermi: 是否显示费米能级线
            **kwargs: matplotlib绘图参数
        """
        if not self.analyzer.dos_data:
            self.analyzer.load_data()
            
        if self.fig is None:
            self.setup_plot()
            
        energies = self.analyzer.dos_data.get('energies')
        total_dos = self.analyzer.dos_data.get('total_dos')
        fermi_energy = self.analyzer.fermi_energy
        
        if energies is None or total_dos is None:
            raise ValueError("无法获取DOS数据")
            
        # 相对于费米能级的能量
        if fermi_energy is not None:
            rel_energies = energies - fermi_energy
        else:
            rel_energies = energies
            
        # 能量范围筛选
        if energy_range is not None:
            mask = (rel_energies >= energy_range[0]) & (rel_energies <= energy_range[1])
            rel_energies = rel_energies[mask]
            total_dos = total_dos[mask] if len(total_dos.shape) == 1 else total_dos[mask]
            
        # 绘图参数
        plot_kwargs = {
            'linewidth': 1.5,
            'color': 'blue',
            'label': 'Total DOS'
        }
        plot_kwargs.update(kwargs)
        
        # 处理自旋极化
        if len(total_dos.shape) == 2:  # 自旋极化
            self.ax.plot(rel_energies, total_dos[:, 0], **plot_kwargs, label='Spin up')
            plot_kwargs['color'] = 'red'
            plot_kwargs['linestyle'] = '--'
            self.ax.plot(rel_energies, -total_dos[:, 1], **plot_kwargs, label='Spin down')
        else:
            self.ax.plot(rel_energies, total_dos, **plot_kwargs)
            
        # 费米能级线
        if show_fermi and fermi_energy is not None:
            self.ax.axvline(x=0, color='black', linestyle='--', alpha=0.7, label='Fermi level')
            
        # 设置标签和格式
        self.ax.set_xlabel('Energy - E$_F$ (eV)')
        self.ax.set_ylabel('DOS (states/eV)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
    def plot_projected_dos(self, atom_indices: Optional[List[int]] = None,
                          orbitals: Optional[List[str]] = None,
                          energy_range: Optional[Tuple[float, float]] = None,
                          **kwargs) -> None:
        """
        绘制投影态密度
        
        Args:
            atom_indices: 要绘制的原子索引
            orbitals: 要绘制的轨道
            energy_range: 能量范围
            **kwargs: 绘图参数
        """
        if not self.analyzer.dos_data:
            self.analyzer.load_data()
            
        if self.fig is None:
            self.setup_plot()
            
        projected_dos = self.analyzer.get_projected_dos(atom_indices, orbitals)
        
        if not projected_dos:
            print("没有投影DOS数据")
            return
            
        energies = self.analyzer.dos_data.get('energies')
        fermi_energy = self.analyzer.fermi_energy
        
        if energies is None:
            raise ValueError("无法获取能量数据")
            
        # 相对于费米能级的能量
        if fermi_energy is not None:
            rel_energies = energies - fermi_energy
        else:
            rel_energies = energies
            
        # 能量范围筛选
        if energy_range is not None:
            mask = (rel_energies >= energy_range[0]) & (rel_energies <= energy_range[1])
            rel_energies = rel_energies[mask]
            
        # 绘制每个投影DOS
        colors = plt.cm.Set1(np.linspace(0, 1, len(projected_dos)))
        
        for i, (label, dos_data) in enumerate(projected_dos.items()):
            if energy_range is not None:
                dos_data = dos_data[mask] if len(dos_data.shape) == 1 else dos_data[mask]
                
            plot_kwargs = {
                'linewidth': 1.5,
                'color': colors[i],
                'label': label,
                'alpha': 0.8
            }
            plot_kwargs.update(kwargs)
            
            if len(dos_data.shape) == 1:
                self.ax.plot(rel_energies, dos_data, **plot_kwargs)
            else:
                # 如果有多个轨道分量，可以堆叠绘制
                self.ax.plot(rel_energies, np.sum(dos_data, axis=1), **plot_kwargs)
                
        # 费米能级线
        if fermi_energy is not None:
            self.ax.axvline(x=0, color='black', linestyle='--', alpha=0.7, label='Fermi level')
            
        self.ax.set_xlabel('Energy - E$_F$ (eV)')
        self.ax.set_ylabel('Projected DOS (states/eV)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
    def plot_dos_comparison(self, other_analyzers: List[DOSAnalyzer], 
                           labels: List[str],
                           energy_range: Optional[Tuple[float, float]] = None) -> None:
        """
        比较多个DOS
        
        Args:
            other_analyzers: 其他DOS分析器列表
            labels: 标签列表
            energy_range: 能量范围
        """
        if self.fig is None:
            self.setup_plot()
            
        analyzers = [self.analyzer] + other_analyzers
        all_labels = ['Reference'] + labels
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(analyzers)))
        
        for i, (analyzer, label) in enumerate(zip(analyzers, all_labels)):
            if not analyzer.dos_data:
                analyzer.load_data()
                
            energies = analyzer.dos_data.get('energies')
            total_dos = analyzer.dos_data.get('total_dos')
            fermi_energy = analyzer.fermi_energy
            
            if energies is None or total_dos is None:
                continue
                
            # 相对于费米能级的能量
            if fermi_energy is not None:
                rel_energies = energies - fermi_energy
            else:
                rel_energies = energies
                
            # 能量范围筛选
            if energy_range is not None:
                mask = (rel_energies >= energy_range[0]) & (rel_energies <= energy_range[1])
                rel_energies = rel_energies[mask]
                total_dos = total_dos[mask] if len(total_dos.shape) == 1 else total_dos[mask]
                
            # 处理自旋
            if len(total_dos.shape) == 2:
                dos_to_plot = np.sum(total_dos, axis=1)
            else:
                dos_to_plot = total_dos
                
            self.ax.plot(rel_energies, dos_to_plot, 
                        linewidth=1.5, color=colors[i], 
                        label=label, alpha=0.8)
                        
        self.ax.set_xlabel('Energy - E$_F$ (eV)')
        self.ax.set_ylabel('DOS (states/eV)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
    def add_annotations(self, band_gap: Optional[float] = None,
                       dos_at_fermi: Optional[float] = None) -> None:
        """
        添加注释信息
        
        Args:
            band_gap: 带隙值
            dos_at_fermi: 费米能级处的DOS
        """
        if self.ax is None:
            return
            
        # 添加文本框
        textstr = []
        
        if band_gap is not None:
            if band_gap > 0.01:
                textstr.append(f'Band gap: {band_gap:.3f} eV')
            else:
                textstr.append('Metallic')
                
        if dos_at_fermi is not None:
            textstr.append(f'DOS(E$_F$): {dos_at_fermi:.3f} states/eV')
            
        if textstr:
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            self.ax.text(0.02, 0.98, '\n'.join(textstr), 
                        transform=self.ax.transAxes, fontsize=10,
                        verticalalignment='top', bbox=props)
                        
    def save_plot(self, filename: Path, **kwargs) -> None:
        """
        保存图形
        
        Args:
            filename: 文件名
            **kwargs: savefig参数
        """
        if self.fig is None:
            raise ValueError("没有可保存的图形")
            
        save_kwargs = {
            'dpi': 300,
            'bbox_inches': 'tight',
            'transparent': False
        }
        save_kwargs.update(kwargs)
        
        self.fig.savefig(filename, **save_kwargs)
        
    def show(self) -> None:
        """显示图形"""
        if self.fig is not None:
            plt.show()
            
    def close(self) -> None:
        """关闭图形"""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None