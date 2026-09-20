"""调用 Claude 完成结构化信息提取与 JD 匹配评分。

优先使用 Anthropic 的结构化输出（client.messages.parse + Pydantic schema），
从协议层面保证返回合法 JSON。若结构化解析意外失败，则回退到普通消息 +
本地 JSON 修复（repair_json），尽最大努力拿到可用结果。
"""

from __future__ import annotations

import json
import logging
import os
import re

import anthropic

from .errors import AIError
from .models import ResumeInfo, ScoreResult

log = logging.getLogger("resume_cli")

# 默认使用当前最强的 Opus 模型；可通过环境变量覆盖（如切换到更省成本的 Sonnet）。
DEFAULT_MODEL = os.environ.get("RESUME_CLI_MODEL", "claude-opus-4-8")

_EXTRACT_SYSTEM = (
    "你是一个专业的简历解析助手。请从用户提供的简历原文中提取结构化信息。"
    "只依据原文，不要编造；无法确定的字段用空字符串或空列表表示。"
    "技能字段应为去重后的关键词列表。"
)

_SCORE_SYSTEM = (
    "你是一位资深技术招聘官。请根据候选人简历与岗位描述（JD）进行匹配评分。"
    "所有分值均为 0-100 的整数：overall_score 为综合得分，"
    "skill_score / experience_score / education_score 分别为技能、经验、学历维度得分。"
    "comment 用一两句中文说明打分理由，interview_questions 给出 2-4 个针对该候选人的面试问题。"
    "务必客观，紧扣 JD 与简历事实。"
)


def _client() -> anthropic.Anthropic:
    # Anthropic() 在缺少 API Key 时不会立刻报错，真正的鉴权错误在请求时抛出。
    return anthropic.Anthropic()


def _clamp_score(value: int) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


def repair_json(raw: str) -> dict:
    """尽力从一段可能不规范的文本中修复出 JSON 对象。

    处理常见问题：markdown 代码围栏、对象前后多余文字、尾随逗号。
    """
    s = raw.strip()

    # 去掉 ```json ... ``` 围栏
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s).strip()

    # 截取第一个 { 到最后一个 } 之间的内容
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end > start:
        s = s[start : end + 1]

    # 去掉对象/数组结尾的多余逗号，如 {"a":1,}
    s = re.sub(r",(\s*[}\]])", r"\1", s)

    return json.loads(s)


def _parse_with_fallback(system: str, prompt: str, schema, model: str):
    """先用结构化输出，失败再回退到普通消息 + 本地修复。返回 schema 实例。"""
    client = _client()

    try:
        resp = client.messages.parse(
            model=model,
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
        )
        if resp.stop_reason == "refusal":
            raise AIError("模型基于安全策略拒绝了本次请求")
        if resp.parsed_output is None:
            raise AIError("模型未返回可解析的结构化结果")
        return resp.parsed_output
    except anthropic.AuthenticationError as e:
        raise AIError("鉴权失败：请检查环境变量 ANTHROPIC_API_KEY 是否正确设置") from e
    except anthropic.APIError as e:
        # 结构化路径出错，尝试普通消息 + JSON 修复兜底
        log.warning("结构化输出失败，尝试普通消息兜底: %s", e)
        return _parse_raw_fallback(client, system, prompt, schema, model, cause=e)


def _parse_raw_fallback(client, system, prompt, schema, model, *, cause):
    hint = (
        "请只输出一个 JSON 对象，不要包含任何解释或 markdown 代码块，"
        f"字段需符合以下结构：{list(schema.model_fields.keys())}"
    )
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=2000,
            system=system + "\n" + hint,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next((b.text for b in resp.content if b.type == "text"), "")
        data = repair_json(text)
        return schema.model_validate(data)
    except anthropic.APIError as e:
        raise AIError(f"调用大模型失败: {e}") from e
    except (json.JSONDecodeError, ValueError) as e:
        raise AIError(f"模型返回内容无法解析为有效 JSON: {e}") from cause


def extract_resume(resume_text: str, *, model: str = DEFAULT_MODEL, mock: bool = False) -> ResumeInfo:
    """从简历文本中提取结构化信息。"""
    if mock:
        log.info("使用 mock 模式，不调用真实 AI")
        return _mock_resume()

    prompt = f"以下是简历原文，请提取结构化信息：\n\n{resume_text}"
    result = _parse_with_fallback(_EXTRACT_SYSTEM, prompt, ResumeInfo, model)
    log.info("已提取候选人信息：%s", result.name or "(姓名未知)")
    return result


def score_resume(
    resume_text: str, jd_text: str, *, model: str = DEFAULT_MODEL, mock: bool = False
) -> ScoreResult:
    """根据简历与 JD 进行匹配评分。"""
    if mock:
        log.info("使用 mock 模式，不调用真实 AI")
        return _mock_score()

    prompt = (
        f"【岗位描述 JD】\n{jd_text}\n\n"
        f"【候选人简历】\n{resume_text}\n\n"
        "请对候选人与该岗位的匹配度进行评分。"
    )
    result = _parse_with_fallback(_SCORE_SYSTEM, prompt, ScoreResult, model)

    # 本地兜底：确保分值落在 0-100
    result.overall_score = _clamp_score(result.overall_score)
    result.skill_score = _clamp_score(result.skill_score)
    result.experience_score = _clamp_score(result.experience_score)
    result.education_score = _clamp_score(result.education_score)
    return result


# --- mock 数据：便于在没有 API Key 的情况下演示整条链路 ---


def _mock_resume() -> ResumeInfo:
    from .models import Education

    return ResumeInfo(
        name="张三",
        phone="13800000000",
        email="zhangsan@example.com",
        city="北京",
        education=[
            Education(school="北京大学", major="计算机科学", degree="本科", graduation_time="2022-06")
        ],
        skills=["Python", "Golang", "React", "PostgreSQL", "Docker"],
    )


def _mock_score() -> ScoreResult:
    return ScoreResult(
        overall_score=82,
        skill_score=88,
        experience_score=80,
        education_score=75,
        comment="候选人具备较好的全栈开发基础，技能与岗位要求较匹配，但缺少明确的大模型应用经验。",
        interview_questions=[
            "请介绍一个你主导过的全栈项目。",
            "你是否有调用大模型 API 的实际经验？",
        ],
    )
