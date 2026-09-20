"""extract 命令三条要求的针对性测试（不发真实请求，用假 client 注入各种场景）：

  1. AI 返回结果必须是 JSON —— 结构化输出 / 兜底修复后得到合法对象
  2. 对 AI 返回结果做基本校验 —— 非法内容会被 Pydantic 拦下并报错
  3. AI 调用失败要有清晰错误提示 —— 鉴权失败等抛出可读的 AIError
"""

from types import SimpleNamespace

import anthropic
import anthropic._base_client as _bc
import pytest

from resume_cli import ai
from resume_cli.errors import AIError
from resume_cli.models import ResumeInfo

# anthropic 内部 vendored 的 httpx（不作为顶层依赖暴露），用于构造异常对象
httpx = _bc.httpx2


def _text_block(t: str):
    return SimpleNamespace(type="text", text=t)


class _FakeMessages:
    def __init__(self, *, parse_result=None, parse_exc=None, create_text=None):
        self._parse_result = parse_result
        self._parse_exc = parse_exc
        self._create_text = create_text

    def parse(self, **_):
        if self._parse_exc:
            raise self._parse_exc
        return self._parse_result

    def create(self, **_):
        return SimpleNamespace(content=[_text_block(self._create_text)])


def _patch_client(monkeypatch, **kw):
    monkeypatch.setattr(
        ai, "_client", lambda: SimpleNamespace(messages=_FakeMessages(**kw))
    )


def _req():
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages")


# --- 要求 1 & 2：返回是合法 JSON，且经过 schema 校验 ---


def test_extract_returns_validated_object(monkeypatch):
    parsed = ResumeInfo(name="李四", skills=["Go", "Python"])
    _patch_client(
        monkeypatch,
        parse_result=SimpleNamespace(parsed_output=parsed, stop_reason="end_turn"),
    )
    info = ai.extract_resume("任意简历文本")
    assert isinstance(info, ResumeInfo)  # 通过 Pydantic 校验的对象
    assert info.name == "李四"
    assert info.skills == ["Go", "Python"]


# --- 要求 1：结构化路径失败时，兜底能从脏文本里修复出 JSON ---


def test_extract_fallback_repairs_dirty_json(monkeypatch):
    api_exc = anthropic.APIError("temporary", request=_req(), body=None)
    raw = '```json\n{"name": "王五", "skills": ["Python",]}\n```'  # 带围栏+尾逗号
    _patch_client(monkeypatch, parse_exc=api_exc, create_text=raw)
    info = ai.extract_resume("任意简历文本")
    assert info.name == "王五"
    assert info.skills == ["Python"]


# --- 要求 2：返回内容非法时，校验失败并给出清晰错误 ---


def test_extract_invalid_content_raises_clear_error(monkeypatch):
    api_exc = anthropic.APIError("temporary", request=_req(), body=None)
    _patch_client(monkeypatch, parse_exc=api_exc, create_text="这根本不是 JSON")
    with pytest.raises(AIError, match="无法解析"):
        ai.extract_resume("任意简历文本")


# --- 要求 3：调用失败（鉴权）给出可读提示 ---


def test_extract_auth_error_message(monkeypatch):
    resp = httpx.Response(401, request=_req())
    auth_exc = anthropic.AuthenticationError("invalid key", response=resp, body=None)
    _patch_client(monkeypatch, parse_exc=auth_exc)
    with pytest.raises(AIError, match="鉴权失败"):
        ai.extract_resume("任意简历文本")


# --- 要求 3：模型拒绝时也要有清晰提示 ---


def test_extract_refusal_raises(monkeypatch):
    _patch_client(
        monkeypatch,
        parse_result=SimpleNamespace(parsed_output=None, stop_reason="refusal"),
    )
    with pytest.raises(AIError, match="拒绝"):
        ai.extract_resume("任意简历文本")
