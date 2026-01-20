# Neo4j Cypher - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint clean coverage

# Neo4j connection settings
export NEO4J_URI ?= bolt://localhost:7687
export NEO4J_USER ?= neo4j
export NEO4J_PASSWORD ?= password

# Install dependencies
setup:
	uv sync --all-extras

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "=== Example 1: Basic CRUD Operations ==="
	uv run python -m examples.example_1_crud

example-2:
	@echo "=== Example 2: Pattern Matching ==="
	uv run python -m examples.example_2_patterns

example-3:
	@echo "=== Example 3: Aggregations and Paths ==="
	uv run python -m examples.example_3_aggregations

# Run tests
test:
	uv run pytest -v tests/

# Run only unit tests (no Neo4j required)
test-unit:
	uv run pytest -v tests/ -m "not integration"

# Run integration tests (requires Neo4j)
test-integration:
	uv run pytest -v tests/ -m integration

# Run tests with coverage
coverage:
	uv run pytest --cov=examples --cov-report=term-missing tests/

# Run linting
lint:
	uv run ruff check examples/ tests/
	uv run ruff format --check examples/ tests/
	uv run mypy examples/

# Format code
format:
	uv run ruff format examples/ tests/
	uv run ruff check --fix examples/ tests/

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf *.egg-info dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Check Neo4j connection
check-neo4j:
	@echo "Checking Neo4j connection..."
	@uv run python -c "from neo4j import GraphDatabase; d = GraphDatabase.driver('$(NEO4J_URI)', auth=('$(NEO4J_USER)', '$(NEO4J_PASSWORD)')); d.verify_connectivity(); print('Neo4j connected successfully!'); d.close()"

# Open Neo4j Browser
browser:
	@echo "Opening Neo4j Browser at http://localhost:7474"
	@open http://localhost:7474 2>/dev/null || xdg-open http://localhost:7474 2>/dev/null || echo "Visit http://localhost:7474"
