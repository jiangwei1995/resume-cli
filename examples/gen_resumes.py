"""生成一组「仿真」简历 PDF（虚构人物），用于演示与测试。

- 5 份中文 + 5 份英文，结构完整（基本信息 / 教育 / 技能 / 工作 / 项目）。
- 内容均为虚构，不含任何真实个人隐私。
- 中文通过嵌入 Arial Unicode 字体渲染，保证 pypdf 可正确提取文本。

依赖 reportlab（非项目运行时依赖）。生成方式：
    uv run --with reportlab python examples/gen_resumes.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT = "Uni"

OUT_DIR = Path(__file__).with_name("resumes")

ACCENT = colors.HexColor("#1a4f8a")


def _styles():
    return {
        "name": ParagraphStyle("name", fontName=FONT, fontSize=18, textColor=ACCENT, spaceAfter=2),
        "title": ParagraphStyle("title", fontName=FONT, fontSize=11, textColor=colors.HexColor("#444444"), spaceAfter=4),
        "contact": ParagraphStyle("contact", fontName=FONT, fontSize=9.5, textColor=colors.HexColor("#333333"), leading=14),
        "h": ParagraphStyle("h", fontName=FONT, fontSize=12, textColor=ACCENT, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=10, leading=15),
        "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=10, leading=15, leftIndent=10),
    }


def build(resume: dict) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    st = _styles()
    doc = SimpleDocTemplate(
        str(OUT_DIR / resume["file"]),
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
    )
    flow = [
        Paragraph(resume["name"], st["name"]),
        Paragraph(resume["title"], st["title"]),
        Paragraph(resume["contact"], st["contact"]),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1, color=ACCENT),
    ]
    for header, lines in resume["sections"]:
        flow.append(Paragraph(header, st["h"]))
        for line in lines:
            style = st["bullet"] if line.startswith(("• ", "- ")) else st["body"]
            flow.append(Paragraph(line, style))
    doc.build(flow)


RESUMES = [
    # ---------- 中文 5 份 ----------
    {
        "file": "zh_01_fullstack.pdf",
        "name": "陈子豪",
        "title": "全栈工程师",
        "contact": "电话：138-0011-2233 ｜ 邮箱：chenzihao.dev@example.com ｜ 城市：北京 ｜ GitHub: github.com/czh-dev",
        "sections": [
            ("教育背景", [
                "北京邮电大学 ｜ 软件工程 ｜ 本科 ｜ 2015.09 - 2019.06",
                "主修课程：数据结构、操作系统、数据库系统、计算机网络。",
            ]),
            ("专业技能", [
                "• 后端：Python(FastAPI/Django)、Node.js、Golang，熟悉 RESTful 与 gRPC。",
                "• 前端：React、TypeScript、Vite、TailwindCSS。",
                "• 数据库/中间件：PostgreSQL、MySQL、Redis、RabbitMQ。",
                "• 运维：Docker、Kubernetes、GitHub Actions、Nginx。",
            ]),
            ("工作经历", [
                "字节跳动 ｜ 全栈工程师 ｜ 2021.07 - 至今",
                "• 负责内容审核后台的前后端开发，服务日均处理请求 2000 万+。",
                "• 主导审核工作流重构，接口 P99 延迟由 480ms 降至 160ms。",
                "美团 ｜ 后端开发工程师 ｜ 2019.07 - 2021.06",
                "• 参与商家结算系统建设，负责对账与开票模块。",
            ]),
            ("项目经历", [
                "智能简历筛选平台（个人项目）",
                "• 基于大模型 API 实现简历解析与岗位匹配评分，Python + React 全栈实现。",
                "• 使用结构化输出保证 JSON 稳定，日均解析简历约 500 份。",
            ]),
        ],
    },
    {
        "file": "zh_02_backend.pdf",
        "name": "王思睿",
        "title": "高级后端工程师",
        "contact": "电话：139-2200-8899 ｜ 邮箱：wangsr@example.com ｜ 城市：上海",
        "sections": [
            ("教育背景", [
                "上海交通大学 ｜ 计算机科学与技术 ｜ 硕士 ｜ 2016.09 - 2019.03",
                "复旦大学 ｜ 计算机科学与技术 ｜ 本科 ｜ 2012.09 - 2016.06",
            ]),
            ("专业技能", [
                "• 语言：Java、Golang、Python。",
                "• 框架：Spring Boot、Spring Cloud、gRPC、Dubbo。",
                "• 存储：MySQL（分库分表）、TiDB、Redis、Elasticsearch、Kafka。",
                "• 熟悉高并发、分布式事务、微服务治理与可观测性建设。",
            ]),
            ("工作经历", [
                "阿里巴巴 ｜ 高级后端工程师 ｜ 2019.04 - 至今",
                "• 负责交易履约核心链路，支撑双十一峰值 58 万笔/秒下单。",
                "• 设计幂等与对账机制，资损率下降 90%。",
                "• 带 3 人小组完成订单中心服务化拆分。",
            ]),
            ("项目经历", [
                "分布式订单中心",
                "• 基于 Kafka + TiDB 构建，支持水平扩展与最终一致性对账。",
            ]),
        ],
    },
    {
        "file": "zh_03_frontend.pdf",
        "name": "林晓彤",
        "title": "前端工程师",
        "contact": "电话：137-6688-1020 ｜ 邮箱：linxt.fe@example.com ｜ 城市：深圳 ｜ 个人站：linxt.dev",
        "sections": [
            ("教育背景", [
                "华南理工大学 ｜ 数字媒体技术 ｜ 本科 ｜ 2017.09 - 2021.06",
            ]),
            ("专业技能", [
                "• 框架：React、Vue3、Next.js，熟悉状态管理与 SSR。",
                "• 语言与工具：TypeScript、Vite、Webpack、pnpm。",
                "• 工程化：微前端、组件库建设、单元测试(Vitest)、E2E(Playwright)。",
                "• 熟悉可视化(ECharts/D3) 与性能优化。",
            ]),
            ("工作经历", [
                "腾讯 ｜ 前端工程师 ｜ 2021.07 - 至今",
                "• 负责企业微信管理后台，主导组件库从 0 到 1 建设，覆盖 60+ 组件。",
                "• 首屏加载时间优化 45%，Lighthouse 性能分提升至 95。",
            ]),
            ("项目经历", [
                "数据看板可视化平台",
                "• 基于 React + ECharts，支持拖拽式配置与实时数据刷新。",
            ]),
        ],
    },
    {
        "file": "zh_04_ml.pdf",
        "name": "赵一鸣",
        "title": "机器学习工程师",
        "contact": "电话：135-9090-3344 ｜ 邮箱：zhaoym.ml@example.com ｜ 城市：杭州",
        "sections": [
            ("教育背景", [
                "浙江大学 ｜ 人工智能 ｜ 硕士 ｜ 2018.09 - 2021.06",
                "研究方向：自然语言处理、信息抽取。",
            ]),
            ("专业技能", [
                "• 语言：Python、C++。",
                "• 框架：PyTorch、TensorFlow、Hugging Face Transformers。",
                "• 方向：大模型微调、RAG、向量检索、Prompt 工程。",
                "• 工程：Docker、Ray、Triton Inference Server。",
            ]),
            ("工作经历", [
                "蚂蚁集团 ｜ 机器学习工程师 ｜ 2021.07 - 至今",
                "• 负责智能客服意图识别与检索增强问答，准确率提升 12%。",
                "• 落地大模型推理服务，QPS 提升 3 倍，成本下降 40%。",
            ]),
            ("项目经历", [
                "科研文献智能问答系统",
                "• 结合向量检索与大模型生成，支持中英文文献问答与引用溯源。",
            ]),
        ],
    },
    {
        "file": "zh_05_newgrad.pdf",
        "name": "孙佳怡",
        "title": "应届毕业生 ｜ 全栈方向",
        "contact": "电话：188-1234-5678 ｜ 邮箱：sunjiayi@example.com ｜ 城市：成都",
        "sections": [
            ("教育背景", [
                "电子科技大学 ｜ 计算机科学与技术 ｜ 本科 ｜ 2021.09 - 2025.06",
                "GPA 3.8/4.0，获国家奖学金、ACM 校赛金奖。",
            ]),
            ("专业技能", [
                "• 语言：Python、Java、JavaScript。",
                "• 熟悉 Flask、React，了解 Docker 与 Git 协作流程。",
                "• 有大模型 API 调用与 Prompt 设计的课程项目经验。",
            ]),
            ("实习经历", [
                "小米 ｜ 后端开发实习生 ｜ 2024.06 - 2024.09",
                "• 参与 IoT 设备管理后台开发，完成设备分组与批量控制接口。",
            ]),
            ("项目经历", [
                "校园二手交易小程序",
                "• 微信小程序 + Flask 后端，实现发布、搜索、即时聊天功能。",
                "AI 简历解析命令行工具",
                "• 读取 PDF 简历并调用大模型提取结构化信息，输出 JSON。",
            ]),
        ],
    },
    # ---------- 英文 5 份 ----------
    {
        "file": "en_01_fullstack.pdf",
        "name": "Michael Anderson",
        "title": "Senior Full-Stack Engineer",
        "contact": "Phone: +1 (415) 555-0148 | Email: m.anderson@example.com | City: San Francisco, CA | github.com/manderson",
        "sections": [
            ("EDUCATION", [
                "University of California, Berkeley | B.S. in Computer Science | 2013.09 - 2017.05",
            ]),
            ("SKILLS", [
                "• Backend: Node.js, Python (FastAPI), Go; REST and GraphQL APIs.",
                "• Frontend: React, TypeScript, Next.js, TailwindCSS.",
                "• Data: PostgreSQL, MongoDB, Redis, Kafka.",
                "• Cloud/DevOps: AWS, Docker, Kubernetes, Terraform, CI/CD.",
            ]),
            ("EXPERIENCE", [
                "Stripe | Senior Full-Stack Engineer | 2020.03 - Present",
                "• Led the redesign of the merchant dashboard serving 2M+ businesses.",
                "• Cut API p99 latency from 520ms to 180ms via caching and query tuning.",
                "Airbnb | Software Engineer | 2017.07 - 2020.02",
                "• Built payment reconciliation services processing $1B+ monthly.",
            ]),
            ("PROJECTS", [
                "AI Resume Screener (open source)",
                "• PDF parsing plus LLM-based extraction and JD scoring; Python + React.",
            ]),
        ],
    },
    {
        "file": "en_02_backend.pdf",
        "name": "Priya Sharma",
        "title": "Backend Software Engineer",
        "contact": "Phone: +1 (206) 555-0192 | Email: priya.sharma@example.com | City: Seattle, WA",
        "sections": [
            ("EDUCATION", [
                "Carnegie Mellon University | M.S. in Computer Science | 2016.08 - 2018.05",
                "University of Washington | B.S. in Computer Engineering | 2012.09 - 2016.06",
            ]),
            ("SKILLS", [
                "• Languages: Java, Go, Python.",
                "• Frameworks: Spring Boot, gRPC, Micronaut.",
                "• Infra: AWS, Kubernetes, Kafka, DynamoDB, Elasticsearch.",
                "• Focus: distributed systems, high availability, observability.",
            ]),
            ("EXPERIENCE", [
                "Amazon | Backend Engineer (SDE II) | 2018.06 - Present",
                "• Owned the order fulfillment pipeline handling 100k+ req/s at peak.",
                "• Designed an idempotent retry framework reducing duplicate charges by 95%.",
            ]),
            ("PROJECTS", [
                "Distributed Rate Limiter",
                "• Redis-backed token bucket used across 40+ internal services.",
            ]),
        ],
    },
    {
        "file": "en_03_frontend.pdf",
        "name": "Emily Carter",
        "title": "Frontend Engineer",
        "contact": "Phone: +1 (312) 555-0176 | Email: emily.carter@example.com | City: Chicago, IL | emilycarter.dev",
        "sections": [
            ("EDUCATION", [
                "University of Illinois Urbana-Champaign | B.S. in Computer Science | 2016.08 - 2020.05",
            ]),
            ("SKILLS", [
                "• Frameworks: React, Vue 3, Next.js; SSR and SPA architectures.",
                "• Languages/Tools: TypeScript, Vite, Webpack, Storybook.",
                "• Testing: Jest, Vitest, Playwright; accessibility (WCAG).",
                "• Visualization: D3.js, ECharts.",
            ]),
            ("EXPERIENCE", [
                "Shopify | Frontend Engineer | 2020.07 - Present",
                "• Built and maintained the merchant admin design system (70+ components).",
                "• Improved Largest Contentful Paint by 40% across key flows.",
            ]),
            ("PROJECTS", [
                "Realtime Analytics Dashboard",
                "• React + WebSocket dashboard with drag-and-drop widget configuration.",
            ]),
        ],
    },
    {
        "file": "en_04_ml.pdf",
        "name": "David Kim",
        "title": "Machine Learning Engineer",
        "contact": "Phone: +1 (650) 555-0133 | Email: david.kim@example.com | City: Palo Alto, CA",
        "sections": [
            ("EDUCATION", [
                "Stanford University | M.S. in Computer Science (AI track) | 2017.09 - 2019.06",
                "Georgia Institute of Technology | B.S. in Computer Science | 2013.08 - 2017.05",
            ]),
            ("SKILLS", [
                "• Languages: Python, C++.",
                "• Frameworks: PyTorch, JAX, Hugging Face Transformers.",
                "• Focus: LLM fine-tuning, RAG, vector search, prompt engineering.",
                "• Serving: Triton, Ray, Docker, ONNX Runtime.",
            ]),
            ("EXPERIENCE", [
                "OpenAI-adjacent startup | ML Engineer | 2019.07 - Present",
                "• Shipped a retrieval-augmented QA system improving accuracy by 14%.",
                "• Optimized inference serving, tripling throughput at 40% lower cost.",
            ]),
            ("PROJECTS", [
                "Document Intelligence Platform",
                "• Combined embeddings and LLM generation for cited, grounded answers.",
            ]),
        ],
    },
    {
        "file": "en_05_newgrad.pdf",
        "name": "Sophia Martinez",
        "title": "New Graduate | Software Engineer",
        "contact": "Phone: +1 (512) 555-0110 | Email: sophia.martinez@example.com | City: Austin, TX",
        "sections": [
            ("EDUCATION", [
                "University of Texas at Austin | B.S. in Computer Science | 2021.08 - 2025.05",
                "GPA 3.9/4.0; Dean's List; ACM ICPC regional finalist.",
            ]),
            ("SKILLS", [
                "• Languages: Python, Java, JavaScript.",
                "• Familiar with Flask, React, Docker, and Git workflows.",
                "• Coursework projects using LLM APIs and prompt design.",
            ]),
            ("INTERNSHIP", [
                "Dell Technologies | Software Engineering Intern | 2024.06 - 2024.08",
                "• Built internal tooling for device provisioning; added batch APIs.",
            ]),
            ("PROJECTS", [
                "Campus Marketplace App",
                "• React Native + Flask app with search and real-time chat.",
                "AI Resume Parser CLI",
                "• Reads PDF resumes and extracts structured JSON via an LLM API.",
            ]),
        ],
    },
]


if __name__ == "__main__":
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))
    for r in RESUMES:
        build(r)
        print(f"已生成 examples/resumes/{r['file']}")
    print(f"\n共生成 {len(RESUMES)} 份简历（中文 5 + 英文 5）到 examples/resumes/")
