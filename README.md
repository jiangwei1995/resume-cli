# resume-cli · AI 简历解析 CLI

一个命令行工具：读取 PDF 简历 → 调用 Claude 提取结构化信息 → 按岗位描述（JD）做匹配评分。

> 星使智算全栈笔试题实现。核心目标是「可运行、可演示、结构清晰」。

## 项目简介

`resume-cli` 提供三个核心命令：

| 命令 | 作用 |
| --- | --- |
| `resume-cli parse <pdf>` | 读取 PDF 并输出纯文本 |
| `resume-cli extract <pdf>` | 调用 AI 提取结构化信息（姓名 / 联系方式 / 教育 / 技能） |
| `resume-cli score <pdf> --jd <jd.txt>` | 简历与 JD 匹配评分，输出 0-100 分及理由、面试问题 |

## 技术选型

- **语言**：Python 3.10+
- **CLI 框架**：[Typer](https://typer.tiangolo.com/) —— 自动生成 `--help`、参数校验友好
- **PDF 解析**：[pypdf](https://pypdf.readthedocs.io/)
- **大模型**：[Anthropic Claude](https://docs.claude.com/)，默认 `claude-opus-4-8`
- **结构化输出**：`client.messages.parse()` + Pydantic schema，从协议层保证返回合法 JSON；
  另有本地 `repair_json` 兜底修复常见 JSON 格式问题
- **包管理**：[uv](https://docs.astral.sh/uv/)

### 目录结构

```
resume-cli/
├── src/resume_cli/
│   ├── cli.py          # 命令行入口（parse / extract / score）
│   ├── pdf.py          # PDF 文本提取 + 边界情况处理
│   ├── ai.py           # Claude 调用、结构化输出、mock、JSON 修复
│   ├── models.py       # Pydantic 数据模型（同时作为 AI 输出 schema）
│   ├── errors.py       # 统一异常类型
│   └── logging_conf.py # 日志（输出到 stderr，不污染 stdout 的 JSON）
├── tests/              # pytest 单元测试
├── examples/
│   ├── jd.txt          # 示例 JD
│   ├── resumes/        # 10 份仿真简历（中文 5 + 英文 5），供演示/测试
│   └── gen_resumes.py  # 生成上述简历的脚本（需 reportlab）
├── Makefile / Dockerfile
```

> 说明：`examples/resumes/` 里的简历均为**虚构人物**，内容结构接近真实简历（基本信息 / 教育 / 技能 / 工作 / 项目），中文通过嵌入 Unicode 字体渲染，`pypdf` 可正确提取。不含任何真实个人隐私。可用 `make resumes` 重新生成。

## 环境变量配置

| 变量 | 说明 |
| --- | --- |
| `ANTHROPIC_API_KEY` | 必填（`--mock` 模式除外）。Anthropic API Key |
| `RESUME_CLI_MODEL` | 可选。覆盖默认模型，如 `claude-sonnet-4-6` 更省成本 |

参考 `.env.example`。设置方式：

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxx
```

## 安装（第三方用户）

四种方式任选其一：

```bash
# 方式一：uv tool 全局安装（推荐，一行装好全局命令 resume-cli）
uv tool install "git+https://github.com/jiangwei1995/resume-cli.git"
resume-cli --help

# 方式二：uv 本地开发（克隆后在项目内运行）
git clone https://github.com/jiangwei1995/resume-cli.git
cd resume-cli && uv sync
uv run resume-cli --help

# 方式三：pipx 隔离安装为全局工具
pipx install "git+https://github.com/jiangwei1995/resume-cli.git"

# 方式四：Docker
docker build -t resume-cli .
docker run --rm -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v "$PWD/examples:/data" resume-cli extract /data/resumes/zh_01_fullstack.pdf
```

> 开发/测试请用 `uv sync --extra dev` 安装含 pytest 的开发依赖。

## 演示视频

约 50 秒的演示动画：[demo/resume-cli-demo.mp4](demo/resume-cli-demo.mp4)（含配音，覆盖安装 / parse / extract / score）。

## 一键演示

```bash
bash scripts/demo.sh          # 依次演示 parse / extract / score
```

有 `ANTHROPIC_API_KEY` 时走真实 AI，否则自动使用 `--mock`，方便录屏演示。

## CLI 命令说明与示例

```bash
# 1. 提取 PDF 文本（可直接用内置仿真简历）
resume-cli parse ./examples/resumes/zh_01_fullstack.pdf

# 2. 结构化提取（输出 JSON，可保存到文件）
resume-cli extract ./examples/resumes/en_01_fullstack.pdf --output result.json

# 3. JD 匹配评分
resume-cli score ./examples/resumes/zh_01_fullstack.pdf --jd ./examples/jd.txt

# 无需 API Key 的演示（mock 模式，全局选项，放在子命令前）
resume-cli --mock extract ./examples/resumes/zh_02_backend.pdf
resume-cli --mock score ./examples/resumes/en_02_backend.pdf --jd ./examples/jd.txt

# 调试日志
resume-cli --verbose extract ./examples/resumes/zh_04_ml.pdf
```

### 示例输出

`extract`：

```json
{
  "name": "张三",
  "phone": "13800000000",
  "email": "zhangsan@example.com",
  "city": "北京",
  "education": [
    {"school": "北京大学", "major": "计算机科学", "degree": "本科", "graduation_time": "2022-06"}
  ],
  "skills": ["Python", "Golang", "React", "PostgreSQL", "Docker"]
}
```

`score`：

```json
{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人具备较好的全栈开发基础，技能与岗位要求较匹配，但缺少明确的大模型应用经验。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验？"
  ]
}
```

## 错误处理

对以下情况均有清晰的中文提示并以非零退出码退出：

- 文件不存在 / 不是 PDF / PDF 无法读取 / PDF 文本为空
- JD 文件不存在或为空
- AI 鉴权失败（未设置 `ANTHROPIC_API_KEY`）、网络错误、返回不可解析
- 分值自动裁剪到 0-100 区间

## 测试

```bash
make test        # 或 uv run pytest -q
```

覆盖：PDF 边界情况、mock 提取/评分、JSON 修复逻辑。

## 已实现功能

- [x] `parse` / `extract` / `score` 三个核心命令
- [x] PDF 文本提取与完整边界情况处理
- [x] Claude 结构化输出（Pydantic schema，JSON 合法性有保证）
- [x] JD 匹配评分（0-100，含理由与面试问题）
- [x] `--output` 保存结果
- [x] `--mock` 无 Key 演示模式
- [x] `repair_json` 自动修复常见 JSON 格式错误（兜底）
- [x] `--verbose` 日志
- [x] Dockerfile / Makefile
- [x] 单元测试

## 已知限制

- 仅支持文字型 PDF；扫描件 / 图片型 PDF 无法直接提取文字（会给出提示）。
- 提取与评分质量依赖所选模型与简历排版。
- 未做多语言简历的专门优化。
