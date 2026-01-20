# Ruff Linting - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint format clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	uv run python -m ruff_linting.examples.example_1

example-2:
	uv run python -m ruff_linting.examples.example_2

example-3:
	uv run python -m ruff_linting.examples.example_3

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=ruff_linting --cov-report=term-missing

# Run linting (check only)
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy src/

# Format code (modify files)
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/*.egg-info dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Demo Ruff commands (for learning)
demo-check:
	@echo "=== Ruff Check Demo ==="
	@echo "Basic check: ruff check src/"
	@echo "With fixes: ruff check --fix src/"
	@echo "Show diff: ruff check --diff src/"
	@echo "Statistics: ruff check --statistics src/"

demo-format:
	@echo "=== Ruff Format Demo ==="
	@echo "Format files: ruff format src/"
	@echo "Check only: ruff format --check src/"
	@echo "Show diff: ruff format --diff src/"

demo-rules:
	@echo "=== Ruff Rules Demo ==="
	@echo "List all rules: ruff rule --all"
	@echo "Explain rule: ruff rule E501"
	@echo "List by category: ruff rule --select F"
