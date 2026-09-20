"""PDF 简历文本提取。"""

from __future__ import annotations

import logging
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .errors import InputError, PDFError

log = logging.getLogger("resume_cli")


def extract_text(pdf_path: str | Path) -> str:
    """读取本地 PDF 并返回纯文本。

    对以下异常情况给出明确提示：文件不存在、非 PDF、无法读取、文本为空。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise InputError(f"文件不存在: {path}")
    if not path.is_file():
        raise InputError(f"不是一个文件: {path}")
    if path.suffix.lower() != ".pdf":
        raise InputError(f"文件不是 PDF（后缀为 {path.suffix or '空'}）: {path}")

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except PdfReadError as e:
        raise PDFError(f"PDF 无法读取（文件可能损坏或加密）: {e}") from e
    except Exception as e:  # noqa: BLE001 - pypdf 可能抛出多种底层异常
        raise PDFError(f"PDF 解析失败: {e}") from e

    text = "\n".join(pages).strip()
    log.debug("PDF 共 %d 页，提取到 %d 个字符", len(pages), len(text))

    if not text:
        raise PDFError("PDF 文本为空（可能是扫描件或图片型 PDF，无法直接提取文字）")

    return text
