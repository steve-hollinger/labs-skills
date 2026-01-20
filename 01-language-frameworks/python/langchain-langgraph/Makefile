.PHONY: setup examples example-1 example-2 example-3 example-4 test lint clean coverage

# Default target
all: setup lint test

# Install dependencies using UV
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3 example-4

# Run individual examples
example-1:
	@echo "=== Example 1: Simple Chain ==="
	uv run python -m langchain_langgraph.examples.example_1_simple_chain

example-2:
	@echo "=== Example 2: Tool-Using Agent ==="
	uv run python -m langchain_langgraph.examples.example_2_tool_agent

example-3:
	@echo "=== Example 3: LangGraph Workflow ==="
	uv run python -m langchain_langgraph.examples.example_3_langgraph_workflow

example-4:
	@echo "=== Example 4: Conversational Agent with Memory ==="
	uv run python -m langchain_langgraph.examples.example_4_memory_agent

# Run tests
test:
	uv run pytest -v --tb=short

# Run tests with coverage
coverage:
	uv run pytest --cov=src/langchain_langgraph --cov-report=term-missing --cov-report=html

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

# Run exercises (for validation)
exercise-1:
	uv run python exercises/exercise_1_summarization_chain.py

exercise-2:
	uv run python exercises/exercise_2_custom_tool_agent.py

exercise-3:
	uv run python exercises/exercise_3_document_pipeline.py
