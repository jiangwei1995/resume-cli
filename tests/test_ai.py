"""AI 模块的本地测试：mock 模式、JSON 修复、分值兜底。"""

import pytest

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
