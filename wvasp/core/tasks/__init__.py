"""
任务管理模块

提供VASP计算任务的管理、调度和监控功能。
"""

# job_management模块已移除，功能整合到任务类中
from .base_task import BaseTask, TaskConfig, TaskStatus
from .calculation_tasks import (
    OptimizationTask, 
    DOSTask, 
    BandTask,
    SinglePointTask,
    MolecularDynamicsTask,
    TransitionStateTask
)

__all__ = [
    'BaseTask',
    'TaskConfig',
    'TaskStatus',
    'OptimizationTask',
    'DOSTask',
    'BandTask',
    'SinglePointTask',
    'MolecularDynamicsTask',
    'TransitionStateTask',
]