# Testcontainers - Go Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-integration lint clean build

# Download dependencies
setup:
	go mod download
	go mod tidy

# Build all
build:
	go build -v ./...

# Run all examples (these run as tests requiring Docker)
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "=== Example 1: PostgreSQL Container ==="
	go test -v -run TestExample1 -tags=integration ./tests/... || echo "Note: Requires Docker"

example-2:
	@echo "=== Example 2: DynamoDB Local Container ==="
	go test -v -run TestExample2 -tags=integration ./tests/... || echo "Note: Requires Docker"

example-3:
	@echo "=== Example 3: Kafka Container ==="
	go test -v -run TestExample3 -tags=integration ./tests/... || echo "Note: Requires Docker"

# Run unit tests (no Docker required)
test:
	go test -v ./... -tags=!integration

# Run integration tests (requires Docker)
test-integration:
	@echo "Running integration tests (requires Docker)..."
	go test -v -tags=integration ./...

# Run tests with race detector
test-race:
	go test -v -race -tags=integration ./...

# Run tests with coverage
coverage:
	go test -coverprofile=coverage.out -tags=integration ./...
	go tool cover -html=coverage.out -o coverage.html

# Run linting
lint:
	golangci-lint run ./...

# Format code
format:
	go fmt ./...
	goimports -w .

# Clean build artifacts
clean:
	go clean
	rm -f coverage.out coverage.html

# Check Docker is running
check-docker:
	@docker info > /dev/null 2>&1 || (echo "Docker is not running. Please start Docker." && exit 1)
	@echo "Docker is running"

# Run exercises (requires Docker)
exercise-1: check-docker
	go test -v -tags=integration ./exercises/exercise1/...

exercise-2: check-docker
	go test -v -tags=integration ./exercises/exercise2/...

exercise-3: check-docker
	go test -v -tags=integration ./exercises/exercise3/...

# Verify solutions
verify-solutions: check-docker
	go test -v -tags=integration ./exercises/solutions/...
