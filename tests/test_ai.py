"""AI 模块的本地测试：mock 模式、JSON 修复、分值兜底。"""

import pytest
from pydantic import ValidationError

import resume_cli.ai as ai
from resume_cli.ai import extract_resume, repair_json, score_resume
from resume_cli.models import ResumeInfo, ScoreResult


def test_extract_mock():
    info = extract_resume("任意文本", mock=True)
    assert isinstance(info, ResumeInfo)
    assert info.name
    assert info.skills


def test_score_mock():
    result = score_resume("简历", "JD", mock=True)
    assert isinstance(result, ScoreResult)
    assert 0 <= result.overall_score <= 100
    assert result.interview_questions


def test_repair_json_strips_code_fence():
    raw = '```json\n{"a": 1, "b": [1, 2,]}\n```'
    assert repair_json(raw) == {"a": 1, "b": [1, 2]}


def test_repair_json_extracts_object_from_prose():
    raw = '好的，结果如下：{"name": "张三"} 希望有帮助'
    assert repair_json(raw) == {"name": "张三"}


def test_repair_json_invalid_raises():
    with pytest.raises(ValueError):
        repair_json("这不是 JSON")


def test_parse_falls_back_when_structured_output_raises_validation_error(monkeypatch):
    """当模型在 JSON 外夹带解释/markdown 时，SDK 会抛 ValidationError，
    应回退到普通消息 + repair_json 兜底，而不是直接崩溃。"""

    class _FakeTextBlock:
        type = "text"
        text = '好的，结果如下：\n```json\n{"name": "李四", "phone": "", "email": "", ' \
               '"city": "", "education": [], "skills": ["Python"]}\n```'

    class _FakeRawResp:
        content = [_FakeTextBlock()]

    class _FakeMessages:
        def parse(self, **kwargs):
            # 复现 SDK 内部对非纯 JSON 文本调用 pydantic 校验时抛出的错误
            raise ValidationError.from_exception_data("ResumeInfo", [])

        def create(self, **kwargs):
            return _FakeRawResp()

    class _FakeClient:
        messages = _FakeMessages()

    monkeypatch.setattr(ai, "_client", lambda: _FakeClient())

    info = extract_resume("任意简历文本", mock=False)
    assert isinstance(info, ResumeInfo)
    assert info.name == "李四"
    assert info.skills == ["Python"]
