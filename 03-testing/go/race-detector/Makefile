# Race Detector - Go Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-race lint clean build demo-race

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
	@echo "=== Example 1: Basic Race Detection ==="
	go run ./cmd/examples/example1/main.go

example-1-race:
	@echo "=== Example 1: With Race Detector ==="
	go run -race ./cmd/examples/example1/main.go || true

example-2:
	@echo "=== Example 2: Common Race Patterns ==="
	go run ./cmd/examples/example2/main.go

example-3:
	@echo "=== Example 3: Fixing Races ==="
	go run ./cmd/examples/example3/main.go

# Demonstrate race detection
demo-race:
	@echo "=== Demonstrating Race Detection ==="
	@echo "Running code with race detector to show detection output..."
	go run -race ./internal/race/demo.go 2>&1 || true

# Run tests
test:
	go test -v ./...

# Run tests with race detector (RECOMMENDED)
test-race:
	go test -v -race ./...

# Run tests with race detector multiple times to increase detection
test-race-thorough:
	go test -v -race -count=10 ./...

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

# Run exercises (without race detector to see issues)
exercise-1:
	go run ./exercises/exercise1/main.go

exercise-2:
	go run ./exercises/exercise2/main.go

exercise-3:
	go run ./exercises/exercise3/main.go

# Verify exercises with race detector
verify-exercise-1:
	go run -race ./exercises/solutions/solution1/main.go

verify-exercise-2:
	go run -race ./exercises/solutions/solution2/main.go

verify-exercise-3:
	go run -race ./exercises/solutions/solution3/main.go
