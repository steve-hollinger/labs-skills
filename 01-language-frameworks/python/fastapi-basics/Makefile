# FastAPI Basics - Python Skill Makefile

.PHONY: setup serve examples example-1 example-2 example-3 example-4 test lint clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run development server
serve:
	uv run uvicorn fastapi_basics.examples.example_1_basic_routes:app --reload --host 0.0.0.0 --port 8000

# Run all examples (as test demonstrations)
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	uv run python -m fastapi_basics.examples.example_1_basic_routes

example-2:
	uv run python -m fastapi_basics.examples.example_2_models

example-3:
	uv run python -m fastapi_basics.examples.example_3_dependencies

example-4:
	uv run python -m fastapi_basics.examples.example_4_async_middleware

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=fastapi_basics --cov-report=term-missing

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
