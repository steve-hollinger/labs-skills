# Four-Layer Prompts - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 example-4 test lint clean coverage format

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	uv run python -m four_layer_prompts.examples.example_1_basic_layers

example-2:
	uv run python -m four_layer_prompts.examples.example_2_template_management

example-3:
	uv run python -m four_layer_prompts.examples.example_3_composition_patterns

example-4:
	uv run python -m four_layer_prompts.examples.example_4_version_management

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=four_layer_prompts --cov-report=term-missing

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
