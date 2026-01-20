# AWS Secrets Manager - Python Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test lint clean coverage localstack-up localstack-down

# Install dependencies
setup:
	uv sync --all-extras

# Start LocalStack for local development
localstack-up:
	docker run -d --name localstack-secrets \
		-p 4566:4566 \
		-e SERVICES=secretsmanager \
		-e DEBUG=1 \
		localstack/localstack:latest
	@echo "Waiting for LocalStack to be ready..."
	@sleep 5
	@echo "LocalStack is ready at http://localhost:4566"

# Stop LocalStack
localstack-down:
	docker stop localstack-secrets || true
	docker rm localstack-secrets || true

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	uv run python -m secrets_manager.examples.example_1

example-2:
	uv run python -m secrets_manager.examples.example_2

example-3:
	uv run python -m secrets_manager.examples.example_3

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
coverage:
	uv run pytest --cov=secrets_manager --cov-report=term-missing

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
