"""PDF 解析的边界情况测试。"""

import pytest
from pypdf import PdfWriter

from resume_cli.errors import InputError, PDFError
from resume_cli.pdf import extract_text


def test_missing_file(tmp_path):
    with pytest.raises(InputError, match="文件不存在"):
        extract_text(tmp_path / "nope.pdf")


def test_not_a_pdf(tmp_path):
    f = tmp_path / "resume.txt"
    f.write_text("hello")
    with pytest.raises(InputError, match="不是 PDF"):
        extract_text(f)


def test_corrupt_pdf(tmp_path):
    # 后缀是 .pdf 但内容不是合法 PDF，应报「无法读取 / 解析失败」
    f = tmp_path / "broken.pdf"
    f.write_bytes(b"%PDF-1.4\nthis is not a valid pdf body")
    with pytest.raises(PDFError):
        extract_text(f)


def test_empty_text_pdf(tmp_path):
    # 构造一个只有空白页、没有文字的 PDF
    f = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(f, "wb") as fh:
        writer.write(fh)
    with pytest.raises(PDFError, match="文本为空"):
        extract_text(f)
