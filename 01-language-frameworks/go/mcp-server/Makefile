# MCP Server in Go - Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-race lint clean build

# Download dependencies
setup:
	go mod download
	go mod tidy

# Build all examples
build:
	go build -v ./...

# Run all examples (they run briefly then exit for demo)
examples: example-1 example-2 example-3

# Individual examples
example-1:
	@echo "Running Example 1: Basic Tool Server"
	@echo "Note: MCP servers are designed to run continuously. Press Ctrl+C to stop."
	@echo "---"
	go run ./cmd/examples/example1/main.go

example-2:
	@echo "Running Example 2: Resources and Templates"
	@echo "Note: MCP servers are designed to run continuously. Press Ctrl+C to stop."
	@echo "---"
	go run ./cmd/examples/example2/main.go

example-3:
	@echo "Running Example 3: Full-Featured Server"
	@echo "Note: MCP servers are designed to run continuously. Press Ctrl+C to stop."
	@echo "---"
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

# Build binaries for all examples
build-examples:
	go build -o bin/example1 ./cmd/examples/example1
	go build -o bin/example2 ./cmd/examples/example2
	go build -o bin/example3 ./cmd/examples/example3
