.PHONY: install test demo lint clean

install:
	uv sync --extra dev

test:
	uv run pytest -q

# 无需 API Key 的演示（mock 模式）
demo:
	uv run resume-cli --mock extract examples/sample_resume.pdf || true
	uv run resume-cli --mock score examples/sample_resume.pdf --jd examples/jd.txt

clean:
	rm -rf .pytest_cache dist build *.egg-info result.json
	find . -type d -name __pycache__ -exec rm -rf {} +
