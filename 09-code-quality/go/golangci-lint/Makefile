# golangci-lint - Go Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-race lint clean build install-golangci-lint

# Check if golangci-lint is installed
GOLANGCI_LINT := $(shell command -v golangci-lint 2> /dev/null)

# Install golangci-lint if not present
install-golangci-lint:
ifndef GOLANGCI_LINT
	@echo "Installing golangci-lint..."
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
else
	@echo "golangci-lint is already installed"
endif

# Download dependencies and install golangci-lint
setup: install-golangci-lint
	go mod download
	go mod tidy

# Build all examples
build:
	go build -v ./...

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "=== Example 1: Basic Linting Setup ==="
	go run ./cmd/examples/example1/main.go

example-2:
	@echo "=== Example 2: Custom Linter Configuration ==="
	go run ./cmd/examples/example2/main.go

example-3:
	@echo "=== Example 3: CI Pipeline Integration ==="
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

# Run linting on this skill
lint: install-golangci-lint
	golangci-lint run ./...

# Run linting with verbose output
lint-verbose: install-golangci-lint
	golangci-lint run -v ./...

# Show available linters
linters:
	golangci-lint linters

# Format code
format:
	go fmt ./...
	goimports -w .

# Clean build artifacts
clean:
	go clean
	rm -f coverage.out coverage.html

# Validate the .golangci.yml configuration
validate-config:
	golangci-lint config verify

# Run exercises
exercise-1:
	@echo "=== Exercise 1: Configure Basic Linting ==="
	@echo "See exercises/exercise1/ for instructions"

exercise-2:
	@echo "=== Exercise 2: Fix Linting Issues ==="
	@echo "See exercises/exercise2/ for instructions"

exercise-3:
	@echo "=== Exercise 3: CI Configuration ==="
	@echo "See exercises/exercise3/ for instructions"
