# MyPy Type Checking - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint typecheck format clean coverage

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	uv run python -m mypy_type_checking.examples.example_1

example-2:
	uv run python -m mypy_type_checking.examples.example_2

example-3:
	uv run python -m mypy_type_checking.examples.example_3

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=mypy_type_checking --cov-report=term-missing

# Run type checking only
typecheck:
	uv run mypy src/

# Run linting (includes mypy)
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

# Demo MyPy commands (for learning)
demo-basic:
	@echo "=== Basic MyPy Usage ==="
	@echo "Check files: mypy src/"
	@echo "Strict mode: mypy --strict src/"
	@echo "Show codes: mypy --show-error-codes src/"

demo-config:
	@echo "=== MyPy Configuration Demo ==="
	@echo "Show config: mypy --help"
	@echo "Verbose: mypy -v src/"
	@echo "Version: mypy --version"

demo-reports:
	@echo "=== MyPy Reports ==="
	@echo "HTML report: mypy --html-report report/ src/"
	@echo "XML report: mypy --xml-report report/ src/"
	@echo "Line count: mypy --lineprecision-report report/ src/"
