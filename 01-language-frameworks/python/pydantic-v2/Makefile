# Pydantic v2 - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 example-4 test lint clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	uv run python -m pydantic_v2.examples.example_1_basic_models

example-2:
	uv run python -m pydantic_v2.examples.example_2_validators

example-3:
	uv run python -m pydantic_v2.examples.example_3_serialization

example-4:
	uv run python -m pydantic_v2.examples.example_4_composition

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=pydantic_v2 --cov-report=term-missing

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
