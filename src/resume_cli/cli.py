"""命令行入口。提供 parse / extract / score 三个子命令。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .ai import DEFAULT_MODEL, extract_resume, score_resume
from .errors import InputError, ResumeCliError
from .logging_conf import setup_logging
from .pdf import extract_text

app = typer.Typer(
    add_completion=False,
    help="AI 简历解析 CLI —— 读取 PDF 简历，用 Claude 提取结构化信息并按 JD 匹配评分。",
    no_args_is_help=True,
)

# 各子命令共享的选项，用回调注入全局状态
_state = {"verbose": False, "model": DEFAULT_MODEL, "mock": False}


def _version_callback(value: bool):
    if value:
        typer.echo(f"resume-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="输出调试日志到 stderr"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="使用的 Claude 模型 ID"),
    mock: bool = typer.Option(
        False, "--mock", help="mock 模式：不调用真实 AI，用内置示例数据演示"
    ),
    _version: Optional[bool] = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True, help="显示版本并退出"
    ),
):
    """全局选项。"""
    _state["verbose"] = verbose
    _state["model"] = model
    _state["mock"] = mock
    setup_logging(verbose)


def _fail(msg: str) -> None:
    typer.secho(f"错误: {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


def _emit_json(data: dict, output: Optional[Path]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        typer.secho(f"结果已保存到 {output}", fg=typer.colors.GREEN, err=True)
    else:
        typer.echo(text)


def _read_pdf_or_fail(pdf_path: str) -> str:
    try:
        return extract_text(pdf_path)
    except ResumeCliError as e:
        _fail(str(e))


@app.command()
def parse(
    pdf_path: str = typer.Argument(..., help="PDF 简历文件路径"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="将文本保存到文件"),
):
    """读取本地 PDF 简历并提取纯文本。"""
    text = _read_pdf_or_fail(pdf_path)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        typer.secho(f"文本已保存到 {output}（{len(text)} 字符）", fg=typer.colors.GREEN, err=True)
    else:
        typer.echo(text)


@app.command()
def extract(
    pdf_path: str = typer.Argument(..., help="PDF 简历文件路径"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="将 JSON 保存到文件"),
):
    """调用 AI 从简历中提取结构化信息（姓名、联系方式、教育、技能等）。"""
    text = _read_pdf_or_fail(pdf_path)
    try:
        info = extract_resume(text, model=_state["model"], mock=_state["mock"])
    except ResumeCliError as e:
        _fail(str(e))
    _emit_json(info.model_dump(), output)


@app.command()
def score(
    pdf_path: str = typer.Argument(..., help="PDF 简历文件路径"),
    jd: Path = typer.Option(..., "--jd", help="岗位描述（JD）文本文件路径"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="将 JSON 保存到文件"),
):
    """根据简历与 JD 进行匹配评分。"""
    text = _read_pdf_or_fail(pdf_path)

    if not jd.exists() or not jd.is_file():
        _fail(f"JD 文件不存在: {jd}")
    jd_text = jd.read_text(encoding="utf-8", errors="ignore").strip()
    if not jd_text:
        _fail(f"JD 文件内容为空: {jd}")

    try:
        result = score_resume(text, jd_text, model=_state["model"], mock=_state["mock"])
    except ResumeCliError as e:
        _fail(str(e))
    _emit_json(result.model_dump(), output)


if __name__ == "__main__":
    app()
