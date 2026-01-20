# CLAUDE.md - {{SKILL_NAME}}

This skill teaches [brief description].

## Key Concepts

- **Concept 1**: Brief explanation
- **Concept 2**: Brief explanation
- **Concept 3**: Brief explanation

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
{{SKILL_NAME}}/
├── cmd/examples/
│   ├── example1/main.go
│   ├── example2/main.go
│   └── example3/main.go
├── internal/
│   └── (internal packages)
├── pkg/
│   └── (reusable packages)
├── exercises/
│   ├── exercise1/
│   └── solutions/
├── tests/
│   └── *_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Pattern
```go
// Example implementation
```

### Pattern 2: Common Pattern
```go
// Example implementation
```

## Common Mistakes

1. **Mistake description**
   - Why it happens
   - How to fix it

2. **Another mistake**
   - Why it happens
   - How to fix it

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Why isn't X working?"
Check common mistakes above, verify setup completed successfully.

### "What's the best practice for Y?"
Refer to docs/patterns.md for recommended approaches.

## Testing Notes

- Use table-driven tests
- Run with race detector: `make test-race`
- Use testify for assertions

## Dependencies

Key dependencies in go.mod:
- dependency1: purpose
- dependency2: purpose
