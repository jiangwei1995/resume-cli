"""日志配置。默认只输出到 stderr，避免污染 stdout 的 JSON 结果。"""

import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger = logging.getLogger("resume_cli")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
