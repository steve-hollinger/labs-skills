# Neo4j Go Driver - Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 test test-race lint clean build

# Neo4j connection settings
export NEO4J_URI ?= bolt://localhost:7687
export NEO4J_USER ?= neo4j
export NEO4J_PASSWORD ?= password

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
	@echo "=== Example 1: Basic CRUD Operations ==="
	go run ./cmd/examples/example1/main.go

example-2:
	@echo "=== Example 2: Transaction Patterns ==="
	go run ./cmd/examples/example2/main.go

example-3:
	@echo "=== Example 3: Graph Patterns ==="
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

# Check Neo4j connection
check-neo4j:
	@echo "Checking Neo4j connection..."
	@go run -e 'package main; import ("context"; "fmt"; "github.com/neo4j/neo4j-go-driver/v5/neo4j"); func main() { ctx := context.Background(); d, _ := neo4j.NewDriverWithContext("$(NEO4J_URI)", neo4j.BasicAuth("$(NEO4J_USER)", "$(NEO4J_PASSWORD)", "")); if err := d.VerifyConnectivity(ctx); err != nil { fmt.Println("Failed:", err) } else { fmt.Println("Connected!") }; d.Close(ctx) }'

# Run exercises
exercise-1:
	go run ./exercises/exercise1/main.go

exercise-2:
	go run ./exercises/exercise2/main.go

exercise-3:
	go run ./exercises/exercise3/main.go

# Run solutions
solution-1:
	go run ./exercises/solutions/solution1/main.go

solution-2:
	go run ./exercises/solutions/solution2/main.go

solution-3:
	go run ./exercises/solutions/solution3/main.go
