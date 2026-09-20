"""生成一个用于演示的文字型 PDF 简历（英文内容，保证基础字体可渲染）。

用法: python examples/make_sample.py
"""

from pathlib import Path

LINES = [
    "Zhang San",
    "Phone: 13800000000   Email: zhangsan@example.com   City: Beijing",
    "",
    "Education:",
    "Peking University, Computer Science, Bachelor, 2022-06",
    "",
    "Skills: Python, Golang, React, PostgreSQL, Docker",
    "",
    "Experience:",
    "Built a full-stack web app with a Python backend and React frontend.",
    "Integrated large language model APIs for a document assistant.",
]


def _escape(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_pdf() -> bytes:
    # 文本内容流：逐行输出
    text_ops = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    for line in LINES:
        text_ops.append(f"({_escape(line)}) Tj")
        text_ops.append("T*")
    text_ops.append("ET")
    content = "\n".join(text_ops).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        b"trailer\n<< /Size "
        + str(len(objects) + 1).encode()
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_pos).encode()
        + b"\n%%EOF"
    )
    return bytes(out)


if __name__ == "__main__":
    target = Path(__file__).with_name("sample_resume.pdf")
    target.write_bytes(build_pdf())
    print(f"已生成 {target}")
