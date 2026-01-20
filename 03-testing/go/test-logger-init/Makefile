# Test Logger Init - Go Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-verbose test-race lint clean build

# Download dependencies
setup:
	go mod download
	go mod tidy

# Build all
build:
	go build -v ./...

# Run all examples (these run as tests)
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "=== Example 1: TestMain Basics ==="
	go test -v -run TestExample1 ./tests/...

example-2:
	@echo "=== Example 2: Test Fixtures ==="
	go test -v -run TestExample2 ./tests/...

example-3:
	@echo "=== Example 3: Logger Configuration ==="
	go test -v -run TestExample3 ./tests/...

# Run all tests
test:
	go test ./...

# Run tests with verbose output
test-verbose:
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
	go test -v ./exercises/exercise1/...

exercise-2:
	go test -v ./exercises/exercise2/...

exercise-3:
	go test -v ./exercises/exercise3/...

# Verify solutions
verify-solutions:
	go test -v ./exercises/solutions/...
