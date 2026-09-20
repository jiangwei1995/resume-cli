"""score 命令四条要求的测试：

  1. 支持读取 JD 文本文件      -> CLI 能读入 JD 并产出 JSON
  2. 评分范围为 0-100          -> 越界分值被裁剪
  3. 评分结果需要包含简要理由  -> comment 被保留
  4. 对 JD 为空 / 不存在有处理 -> CLI 报错并以退出码 1 结束
"""

from types import SimpleNamespace

from typer.testing import CliRunner

from resume_cli import ai
from resume_cli.cli import app
from resume_cli.models import ScoreResult

runner = CliRunner()


# --- ai.score_resume 层：要求 2 & 3 ---


class _FakeMessages:
    def __init__(self, parse_result):
        self._r = parse_result

    def parse(self, **_):
        return self._r


def _patch_score(monkeypatch, result: ScoreResult):
    monkeypatch.setattr(
        ai,
        "_client",
        lambda: SimpleNamespace(
            messages=_FakeMessages(
                SimpleNamespace(parsed_output=result, stop_reason="end_turn")
            )
        ),
    )


def test_score_clamps_to_0_100(monkeypatch):
    # 模型返回越界分值，应被裁剪进 0-100
    raw = ScoreResult(
        overall_score=150,
        skill_score=-10,
        experience_score=88,
        education_score=200,
        comment="ok",
        interview_questions=["q"],
    )
    _patch_score(monkeypatch, raw)
    r = ai.score_resume("resume", "jd")
    assert r.overall_score == 100
    assert r.skill_score == 0
    assert r.education_score == 100
    assert 0 <= r.experience_score <= 100


def test_score_keeps_comment(monkeypatch):
    raw = ScoreResult(
        overall_score=80,
        skill_score=80,
        experience_score=80,
        education_score=80,
        comment="技能匹配，但缺少大模型经验",
        interview_questions=[],
    )
    _patch_score(monkeypatch, raw)
    r = ai.score_resume("resume", "jd")
    assert r.comment == "技能匹配，但缺少大模型经验"


# --- CLI 层：要求 1 & 4（用 --mock 避免真实调用，patch 掉 PDF 读取以隔离 JD 逻辑）---


def _patch_pdf(monkeypatch):
    monkeypatch.setattr("resume_cli.cli.extract_text", lambda _p: "简历文本")


def test_cli_score_reads_jd_and_outputs_json(monkeypatch, tmp_path):
    _patch_pdf(monkeypatch)
    jd = tmp_path / "jd.txt"
    jd.write_text("需要 Python 全栈工程师", encoding="utf-8")
    result = runner.invoke(app, ["--mock", "score", "x.pdf", "--jd", str(jd)])
    assert result.exit_code == 0
    assert "overall_score" in result.output  # 输出为 JSON


def test_cli_score_missing_jd(monkeypatch, tmp_path):
    _patch_pdf(monkeypatch)
    result = runner.invoke(
        app, ["--mock", "score", "x.pdf", "--jd", str(tmp_path / "none.txt")]
    )
    assert result.exit_code == 1


def test_cli_score_empty_jd(monkeypatch, tmp_path):
    _patch_pdf(monkeypatch)
    jd = tmp_path / "empty.txt"
    jd.write_text("   \n\t", encoding="utf-8")  # 仅空白
    result = runner.invoke(app, ["--mock", "score", "x.pdf", "--jd", str(jd)])
    assert result.exit_code == 1
