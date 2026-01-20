# Bandit Security - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint security baseline format clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	uv run python -m bandit_security.examples.example_1

example-2:
	uv run python -m bandit_security.examples.example_2

example-3:
	uv run python -m bandit_security.examples.example_3

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=bandit_security --cov-report=term-missing

# Run security scan (excluding example vulnerable code)
security:
	uv run bandit -r src/ -x "src/bandit_security/examples" --severity-level medium

# Run security scan with all findings
security-all:
	uv run bandit -r src/ -x "src/bandit_security/examples"

# Create/update baseline
baseline:
	uv run bandit -r src/ -x "src/bandit_security/examples" -f json -o .bandit_baseline.json

# Run linting (ruff + mypy)
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

# Demo Bandit commands (for learning)
demo-basic:
	@echo "=== Basic Bandit Usage ==="
	@echo "Scan directory: bandit -r src/"
	@echo "Medium+ only: bandit -r src/ -ll"
	@echo "JSON output: bandit -r src/ -f json -o report.json"

demo-config:
	@echo "=== Bandit Configuration ==="
	@echo "Show all tests: bandit --list"
	@echo "Specific tests: bandit -r src/ -t B101,B102"
	@echo "Skip tests: bandit -r src/ -s B101"

demo-ci:
	@echo "=== CI Integration ==="
	@echo "Strict mode: bandit -r src/ -ll -f json --exit-zero"
	@echo "With baseline: bandit -r src/ -b .bandit_baseline.json"
