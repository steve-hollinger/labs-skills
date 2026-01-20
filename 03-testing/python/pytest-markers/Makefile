# pytest-markers - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 example-4 test test-slow test-fast test-unit test-integration lint clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	uv run python -m pytest_markers.examples.example_1_builtin

example-2:
	uv run python -m pytest_markers.examples.example_2_custom

example-3:
	uv run python -m pytest_markers.examples.example_3_parametrize

example-4:
	uv run python -m pytest_markers.examples.example_4_combinations

# Run all tests
test:
	uv run pytest -v

# Run only slow tests
test-slow:
	uv run pytest -v -m slow

# Run fast tests (not slow)
test-fast:
	uv run pytest -v -m "not slow"

# Run unit tests
test-unit:
	uv run pytest -v -m unit

# Run integration tests
test-integration:
	uv run pytest -v -m integration

# Run tests with coverage
coverage:
	uv run pytest --cov=pytest_markers --cov-report=term-missing

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

# Show available markers
show-markers:
	uv run pytest --markers
