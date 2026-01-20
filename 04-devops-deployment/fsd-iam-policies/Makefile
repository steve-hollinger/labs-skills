.PHONY: setup examples example-1 example-2 example-3 validate test lint clean

setup:
	uv sync

examples: example-1 example-2 example-3

example-1:
	uv run python -m fsd_iam_policies.examples.example_1

example-2:
	uv run python -m fsd_iam_policies.examples.example_2

example-3:
	uv run python -m fsd_iam_policies.examples.example_3

validate:
	uv run python -m fsd_iam_policies.validator

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/
	uv run mypy src/

clean:
	rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
