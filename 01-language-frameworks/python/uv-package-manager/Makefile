# UV Package Manager - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	uv run python -m uv_package_manager.examples.example_1

example-2:
	uv run python -m uv_package_manager.examples.example_2

example-3:
	uv run python -m uv_package_manager.examples.example_3

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=uv_package_manager --cov-report=term-missing

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

# Demo UV commands (for learning)
demo-init:
	@echo "=== UV Project Initialization Demo ==="
	@echo "Creating a new project would use: uv init demo-project"
	@echo "Creating a library would use: uv init --lib demo-library"

demo-add:
	@echo "=== UV Dependency Management Demo ==="
	@echo "Add production dep: uv add requests"
	@echo "Add dev dep: uv add --dev pytest"
	@echo "Add with version: uv add 'fastapi>=0.100'"
	@echo "Remove dep: uv remove requests"

demo-run:
	@echo "=== UV Run Commands Demo ==="
	@echo "Run Python: uv run python script.py"
	@echo "Run pytest: uv run pytest"
	@echo "Run module: uv run python -m module_name"
