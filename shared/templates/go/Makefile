# {{SKILL_NAME}} - Go Skill Makefile

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
	go run ./cmd/examples/example1/main.go

example-2:
	go run ./cmd/examples/example2/main.go

example-3:
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
