#!/usr/bin/env bash
#
# 一键演示脚本：用于录制演示视频。
# 依次展示 安装/版本 -> parse -> extract -> score -> 项目结构。
# 有 ANTHROPIC_API_KEY 则走真实 AI，否则自动使用 --mock 模式。
#
# 用法：
#   bash scripts/demo.sh
#
set -euo pipefail

cd "$(dirname "$0")/.."

ZH=examples/resumes/zh_01_fullstack.pdf
EN=examples/resumes/en_01_fullstack.pdf
JD=examples/jd.txt

# 无 Key 时自动切 mock，保证录制不中断
MOCK=""
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  MOCK="--mock"
fi

pause() { sleep "${DEMO_PAUSE:-1.5}"; }
say()   { printf '\n\033[1;36m# %s\033[0m\n' "$1"; pause; }
run()   { printf '\033[1;32m$ %s\033[0m\n' "$*"; eval "$*"; pause; }

say "0) 环境与版本"
run "uv run resume-cli --version"
if [ -n "$MOCK" ]; then
  printf '\033[1;33m(未检测到 ANTHROPIC_API_KEY，extract/score 将以 --mock 演示)\033[0m\n'; pause
fi

say "1) parse —— 读取 PDF 简历并提取纯文本（中文简历）"
run "uv run resume-cli parse $ZH | head -6"

say "2) extract —— 调用 AI 提取结构化信息（姓名/联系方式/教育/技能）"
run "uv run resume-cli $MOCK extract $ZH"

say "3) score —— 简历与 JD 匹配评分（英文简历 + 中文 JD）"
run "uv run resume-cli $MOCK score $EN --jd $JD"

say "4) 项目结构一览"
run "find src tests examples -type f -not -name '*.pdf' | sort"

printf '\n\033[1;36m# 演示结束。仓库：https://github.com/jiangwei1995/resume-cli\033[0m\n'
