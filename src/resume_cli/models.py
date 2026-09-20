"""结构化数据模型（Pydantic）。

这些模型同时用于：
1. 作为 Claude 结构化输出（output_config.format）的 schema，保证返回合法 JSON；
2. 在本地对返回结果做二次校验。
"""

from pydantic import BaseModel, Field


class Education(BaseModel):
    school: str = Field(default="", description="学校名称")
    major: str = Field(default="", description="专业")
    degree: str = Field(default="", description="学历，如 本科 / 硕士 / 博士")
    graduation_time: str = Field(default="", description="毕业时间，如 2023-06")


class ResumeInfo(BaseModel):
    """从简历中提取的结构化信息。缺失字段以空字符串 / 空列表表示。"""

    name: str = Field(default="", description="姓名")
    phone: str = Field(default="", description="电话")
    email: str = Field(default="", description="邮箱")
    city: str = Field(default="", description="所在城市")
    education: list[Education] = Field(default_factory=list, description="教育经历")
    skills: list[str] = Field(default_factory=list, description="技能关键词列表")


class ScoreResult(BaseModel):
    """简历与岗位描述（JD）的匹配评分结果。各项分值范围 0-100。"""

    overall_score: int = Field(description="综合匹配得分 0-100")
    skill_score: int = Field(description="技能匹配得分 0-100")
    experience_score: int = Field(description="经验匹配得分 0-100")
    education_score: int = Field(description="学历匹配得分 0-100")
    comment: str = Field(description="简要评语，说明打分理由")
    interview_questions: list[str] = Field(
        default_factory=list, description="针对该候选人建议的面试问题"
    )
