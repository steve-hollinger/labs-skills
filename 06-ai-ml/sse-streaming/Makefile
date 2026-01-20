.PHONY: setup examples example-1 example-2 example-3 example-4 test lint clean run-server test-client

# Default target
all: setup lint test

# Install dependencies using UV
setup:
	uv sync --all-extras

# Run the SSE server
run-server:
	@echo "Starting SSE server on http://localhost:8000"
	uv run uvicorn sse_streaming.server:app --reload --host 0.0.0.0 --port 8000

# Test client against running server
test-client:
	uv run python -m sse_streaming.client

# Run all examples
examples: example-1 example-2 example-3 example-4

# Run individual examples
example-1:
	@echo "=== Example 1: Basic SSE Endpoint ==="
	uv run python -m sse_streaming.examples.example_1_basic_sse

example-2:
	@echo "=== Example 2: LLM Streaming ==="
	uv run python -m sse_streaming.examples.example_2_llm_streaming

example-3:
	@echo "=== Example 3: Client Consumption ==="
	uv run python -m sse_streaming.examples.example_3_client_consumption

example-4:
	@echo "=== Example 4: Production Patterns ==="
	uv run python -m sse_streaming.examples.example_4_production_patterns

# Run tests
test:
	uv run pytest -v --tb=short

# Run tests with coverage
coverage:
	uv run pytest --cov=src/sse_streaming --cov-report=term-missing --cov-report=html

# Run linting
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy src/ --ignore-missing-imports

# Format code
format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/**/__pycache__ tests/__pycache__
	rm -rf .coverage htmlcov/
	rm -rf dist/ build/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Run exercises
exercise-1:
	uv run python exercises/exercise_1_chat_endpoint.py

exercise-2:
	uv run python exercises/exercise_2_progress_streaming.py

exercise-3:
	uv run python exercises/exercise_3_multi_source.py
