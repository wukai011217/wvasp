"""
自定义异常类

定义WVasp工具的异常体系，提供清晰的错误信息。
"""


class WVaspError(Exception):
    """WVasp基础异常类"""
    pass


class FileFormatError(WVaspError):
    """文件格式错误"""
    pass


class CalculationError(WVaspError):
    """计算错误"""
    pass


class StructureError(WVaspError):
    """结构错误"""
    pass


class ParameterError(WVaspError):
    """参数错误"""
    pass


class IOError(WVaspError):
    """输入输出错误"""
    pass


class TaskError(WVaspError):
    """任务执行错误"""
    pass
