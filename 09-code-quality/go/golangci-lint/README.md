# golangci-lint

A comprehensive skill for mastering Go code linting with golangci-lint, the standard linter aggregator for Go projects.

## Learning Objectives

After completing this skill, you will be able to:
- Install and configure golangci-lint for your Go projects
- Understand and select appropriate linters for your needs
- Customize linter rules through `.golangci.yml` configuration
- Integrate golangci-lint into CI/CD pipelines
- Fix common linting issues and understand why they matter

## Prerequisites

- Go 1.22+
- Basic Go knowledge (functions, packages, error handling)
- Familiarity with command-line tools

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test

# Run lint on the skill itself
make lint
```

## Concepts

### What is golangci-lint?

golangci-lint is a fast linters runner for Go that runs multiple linters in parallel and reuses Go build cache. It combines 50+ linters into a single tool, making it the de-facto standard for Go code quality.

```bash
# Basic usage
golangci-lint run

# Run specific linters
golangci-lint run --enable=errcheck,ineffassign

# Check a specific file
golangci-lint run ./path/to/file.go
```

### Why Use golangci-lint?

1. **Performance**: Runs linters concurrently, caches results
2. **Consistency**: Single configuration for all linters
3. **Flexibility**: Enable/disable specific linters as needed
4. **CI-Friendly**: Easy integration with GitHub Actions, GitLab CI, etc.

### Configuration Basics

Configuration lives in `.golangci.yml` at your project root:

```yaml
run:
  timeout: 5m
  tests: true

linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused

linters-settings:
  errcheck:
    check-type-assertions: true
```

## Examples

### Example 1: Basic Linting Setup

This example demonstrates setting up golangci-lint with a basic configuration and running it on sample code.

```bash
make example-1
```

### Example 2: Custom Linter Configuration

Building on the basics with custom linter settings, exclusions, and project-specific rules.

```bash
make example-2
```

### Example 3: CI Pipeline Integration

Real-world CI integration patterns with GitHub Actions and pre-commit hooks.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Configure a basic `.golangci.yml` for a new project
2. **Exercise 2**: Fix linting issues in problematic code
3. **Exercise 3**: Create a custom CI configuration with golangci-lint

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Disabling Linters Without Understanding

Many developers disable linters because they produce warnings. Instead:
- Understand why the linter flags the issue
- Fix the underlying problem when possible
- Only disable with a documented reason

### Mistake 2: Not Customizing for Your Project

The default settings are generic. Customize based on:
- Your team's coding standards
- Project requirements
- Performance considerations

### Mistake 3: Ignoring Timeout Settings in CI

CI environments may be slower. Set appropriate timeouts:
```yaml
run:
  timeout: 10m  # More generous for CI
```

## Linter Categories

| Category | Linters | Purpose |
|----------|---------|---------|
| Bugs | staticcheck, govet, errcheck | Find actual bugs |
| Performance | prealloc, maligned | Performance optimization |
| Style | gofmt, goimports, whitespace | Code formatting |
| Complexity | gocyclo, funlen | Code complexity |
| Security | gosec | Security vulnerabilities |

## Further Reading

- [Official golangci-lint Documentation](https://golangci-lint.run/)
- [Available Linters](https://golangci-lint.run/usage/linters/)
- Related skills in this repository:
  - [Go Testing](../../03-testing/go/)
  - [Conventional Commits](../conventional-commits/)
