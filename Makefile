.PHONY: install test demo lint clean

install:
	uv sync --extra dev

test:
	uv run pytest -q

# 无需 API Key 的演示（mock 模式）
demo:
	uv run resume-cli parse examples/resumes/zh_01_fullstack.pdf
	uv run resume-cli --mock extract examples/resumes/zh_01_fullstack.pdf
	uv run resume-cli --mock score examples/resumes/en_01_fullstack.pdf --jd examples/jd.txt

# 重新生成仿真简历（需要 reportlab，通过 uv --with 临时引入）
resumes:
	uv run --with reportlab python examples/gen_resumes.py

clean:
	rm -rf .pytest_cache dist build *.egg-info result.json
	find . -type d -name __pycache__ -exec rm -rf {} +
