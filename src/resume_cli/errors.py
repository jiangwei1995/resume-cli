"""统一的异常类型，便于 CLI 层做友好的错误提示。"""


class ResumeCliError(Exception):
    """所有本工具已知错误的基类。"""


class InputError(ResumeCliError):
    """用户输入相关错误：文件不存在、类型不对、内容为空等。"""


class PDFError(ResumeCliError):
    """PDF 解析相关错误。"""


class AIError(ResumeCliError):
    """调用大模型相关错误：鉴权失败、网络错误、返回不可解析等。"""
