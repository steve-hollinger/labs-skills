# CLAUDE.md - golangci-lint

This skill teaches Go linting best practices using golangci-lint, including configuration, linter selection, and CI integration.

## Key Concepts

- **Linter Aggregation**: golangci-lint runs 50+ linters in parallel with shared caching
- **Configuration-Driven**: `.golangci.yml` centralizes all linter settings
- **Severity Levels**: Different linters catch bugs, style issues, or performance problems
- **CI Integration**: Seamless integration with GitHub Actions, GitLab CI, and pre-commit hooks

## Common Commands

```bash
make setup      # Install golangci-lint and dependencies
make examples   # Run all examples
make example-1  # Run basic linting example
make example-2  # Run custom configuration example
make example-3  # Run CI integration example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint on this skill
make clean      # Remove build artifacts
```

## Project Structure

```
golangci-lint/
├── cmd/examples/
│   ├── example1/main.go      # Basic linting setup
│   ├── example2/main.go      # Custom configuration
│   └── example3/main.go      # CI integration patterns
├── internal/
│   └── analyzer/             # Code analysis helpers
├── pkg/
│   └── config/               # Configuration utilities
├── exercises/
│   ├── exercise1/            # Basic config exercise
│   ├── exercise2/            # Fix linting issues
│   ├── exercise3/            # CI setup exercise
│   └── solutions/
├── tests/
│   └── *_test.go
├── docs/
│   ├── concepts.md
│   └── patterns.md
├── .golangci.yml             # Example configuration
└── .golangci.example.yml     # Documented example config
```

## Code Patterns

### Pattern 1: Minimal Configuration
```yaml
# .golangci.yml - minimal setup
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
```

### Pattern 2: Production Configuration
```yaml
# .golangci.yml - production setup
run:
  timeout: 5m
  tests: true

linters:
  disable-all: true
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true
```

### Pattern 3: GitHub Actions Integration
```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  golangci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - uses: golangci/golangci-lint-action@v4
        with:
          version: latest
```

## Common Mistakes

1. **Disabling too many linters**
   - Why it happens: Developers want to eliminate all warnings quickly
   - How to fix it: Address issues individually, only disable with good reason

2. **Not setting timeouts in CI**
   - Why it happens: Local runs are fast, but CI can be slow
   - How to fix it: Set `run.timeout` to at least 5m for CI

3. **Ignoring type assertion errors**
   - Why it happens: Code "works" without checking
   - How to fix it: Enable `errcheck.check-type-assertions: true`

4. **Missing nolint directives explanation**
   - Why it happens: Quick fixes without documentation
   - How to fix it: Use `//nolint:lintername // reason for disabling`

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Example 1 shows basic setup.

### "Which linters should I enable?"
Start with the default set (errcheck, govet, staticcheck, unused). Add more based on needs. See docs/concepts.md for linter categories.

### "Why isn't X linter working?"
1. Check if it's enabled in `.golangci.yml`
2. Verify the linter is supported: `golangci-lint linters`
3. Check for configuration errors: `golangci-lint run --verbose`

### "How do I suppress a specific warning?"
Use `//nolint:lintername // reason` on the line, or exclude patterns in config:
```yaml
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck
```

### "How do I integrate with my IDE?"
- VS Code: Use the official Go extension (automatic)
- GoLand: Settings > Tools > golangci-lint
- Vim/Neovim: Use ale or nvim-lint plugins

## Testing Notes

- Tests demonstrate linting behavior on sample code
- Run with race detector: `make test-race`
- Use testify for assertions
- Tests verify configuration parsing and linter output

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify: Testing assertions
- gopkg.in/yaml.v3: YAML configuration parsing

## Important Linters to Know

| Linter | Category | Description |
|--------|----------|-------------|
| errcheck | bugs | Checks unchecked errors |
| govet | bugs | Reports suspicious constructs |
| staticcheck | bugs | Advanced static analysis |
| unused | bugs | Finds unused code |
| gosimple | style | Simplification suggestions |
| gofmt | style | Formatting check |
| goimports | style | Import organization |
| gocyclo | complexity | Cyclomatic complexity |
| gosec | security | Security issues |
