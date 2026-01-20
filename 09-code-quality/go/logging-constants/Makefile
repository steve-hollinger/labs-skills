# logging-constants - Go Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-race lint clean build

# Download dependencies
setup:
	go mod download
	go mod tidy

# Build all examples
build:
	go build -v ./...

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "=== Example 1: Basic Logging Constants ==="
	go run ./cmd/examples/example1/main.go

example-2:
	@echo "=== Example 2: Log Level Management ==="
	go run ./cmd/examples/example2/main.go

example-3:
	@echo "=== Example 3: Context Propagation ==="
	go run ./cmd/examples/example3/main.go

# Run tests
test:
	go test -v ./...

# Run tests with race detector
test-race:
	go test -v -race ./...

# Run tests with coverage
coverage:
	go test -coverprofile=coverage.out ./...
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

# Run exercises
exercise-1:
	@echo "=== Exercise 1: Define Logging Constants ==="
	@echo "See exercises/exercise1/ for instructions"

exercise-2:
	@echo "=== Exercise 2: Refactor to Use Constants ==="
	@echo "See exercises/exercise2/ for instructions"

exercise-3:
	@echo "=== Exercise 3: Context-Aware Logging ==="
	@echo "See exercises/exercise3/ for instructions"
