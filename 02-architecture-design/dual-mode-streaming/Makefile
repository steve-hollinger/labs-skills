# Dual-Mode Streaming - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 example-4 test lint clean coverage format

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	uv run python -m dual_mode_streaming.examples.example_1_basic_streaming

example-2:
	uv run python -m dual_mode_streaming.examples.example_2_mode_detection

example-3:
	uv run python -m dual_mode_streaming.examples.example_3_llm_streaming

example-4:
	uv run python -m dual_mode_streaming.examples.example_4_backpressure

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=dual_mode_streaming --cov-report=term-missing

# Run linting
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy src/

# Format code
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/*.egg-info dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
