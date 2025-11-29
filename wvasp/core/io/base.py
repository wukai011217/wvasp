"""
文件I/O基础类

定义VASP文件处理的抽象基类和通用功能。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any

from ...utils.errors import FileFormatError, IOError


class VASPFile(ABC):
    """
    VASP文件抽象基类
    
    定义所有VASP文件类的通用接口。
    """
    
    def __init__(self, filepath: Optional[Path] = None):
        """
        初始化VASP文件对象
        
        Args:
            filepath: 文件路径
        """
        self.filepath = Path(filepath) if filepath else None
        self._data = None
        self._is_loaded = False
    
    @abstractmethod
    def read(self, filepath: Optional[Path] = None) -> Any:
        """
        读取文件内容
        
        Args:
            filepath: 文件路径，如果为None则使用初始化时的路径
            
        Returns:
            解析后的数据
            
        Raises:
            FileFormatError: 文件格式错误
            IOError: 文件读取错误
        """
        pass
    
    @abstractmethod
    def write(self, filepath: Optional[Path] = None, **kwargs) -> None:
        """
        写入文件内容
        
        Args:
            filepath: 文件路径，如果为None则使用初始化时的路径
            **kwargs: 额外的写入参数
            
        Raises:
            IOError: 文件写入错误
        """
        pass
    
    @property  # 用于定义只读属性的装饰器
    @abstractmethod  # 用于声明抽象方法的装饰器
    def is_valid(self) -> bool:
        """
        检查文件内容是否有效
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _check_file_exists(self, filepath: Optional[Path] = None) -> Path:
        """
        检查文件是否存在
        
        Args:
            filepath: 文件路径
            
        Returns:
            验证后的文件路径
            
        Raises:
            IOError: 文件不存在或路径无效
        """
        path = filepath if filepath else self.filepath
        if path is None:
            raise IOError("No file path specified")
        
        path = Path(path)
        if not path.exists():
            raise IOError(f"File not found: {path}")
        
        if not path.is_file():
            raise IOError(f"Path is not a file: {path}")
        
        return path
    
    def _read_lines(self, filepath: Optional[Path] = None) -> list:
        """
        读取文件所有行
        
        Args:
            filepath: 文件路径
            
        Returns:
            文件行列表
        """
        path = self._check_file_exists(filepath)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(path, 'r', encoding='latin-1') as f:
                return f.readlines()
        except Exception as e:
            raise IOError(f"Failed to read file {path}: {e}")
    
    def _write_lines(self, lines: list, filepath: Optional[Path] = None) -> None:
        """
        写入文件行
        
        Args:
            lines: 要写入的行列表
            filepath: 文件路径
        """
        path = filepath if filepath else self.filepath
        if path is None:
            raise IOError("No file path specified")
        
        path = Path(path)
        try:
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            raise IOError(f"Failed to write file {path}: {e}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.filepath})"
