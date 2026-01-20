# Core Concepts

## Overview

golangci-lint is a fast, configurable linters runner for Go. It combines 50+ linters into a single tool, running them in parallel and caching results for speed.

## Concept 1: Linter Categories

### What They Are

Linters fall into different categories based on what issues they detect:

| Category | Purpose | Examples |
|----------|---------|----------|
| Bug Detection | Find actual bugs | errcheck, govet, staticcheck |
| Style | Code formatting | gofmt, goimports |
| Complexity | Code complexity | gocyclo, funlen |
| Performance | Performance issues | prealloc, maligned |
| Security | Security vulnerabilities | gosec |

### Why They Matter

Different categories serve different purposes:
- **Bug Detection**: Must-have for any project - catches real issues
- **Style**: Ensures consistency across a team
- **Complexity**: Maintains code readability over time
- **Performance**: Critical for performance-sensitive applications
- **Security**: Essential for production applications

### How to Choose

```yaml
# Minimal setup (start here)
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused

# Add style enforcement
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gofmt
    - goimports

# Full production setup
linters:
  disable-all: true
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gofmt
    - goimports
    - gosimple
    - ineffassign
    - gocritic
    - gosec
```

## Concept 2: Configuration Files

### What It Is

golangci-lint uses YAML configuration files to define linter behavior. The default file is `.golangci.yml` in your project root.

### Why It Matters

Configuration files:
- Ensure consistent linting across environments
- Document team coding standards
- Allow fine-grained control over linter behavior
- Can be version-controlled with your code

### How It Works

```yaml
# .golangci.yml structure

# Run configuration
run:
  timeout: 5m
  tests: true

# Which linters to use
linters:
  enable:
    - errcheck
    - govet

# Individual linter settings
linters-settings:
  errcheck:
    check-type-assertions: true

# Issue filtering
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck
```

### Configuration Precedence

1. Command-line flags (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## Concept 3: Issue Management

### What It Is

Issue management controls how linting problems are reported and filtered.

### Why It Matters

- Reduces noise from irrelevant warnings
- Allows gradual adoption in existing projects
- Enables different rules for different file types

### How It Works

```yaml
issues:
  # Exclude by regex pattern
  exclude:
    - "Error return value of .*(Close|Log).* is not checked"

  # Exclude by path and linter
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck
        - gocritic

    - path: cmd/
      linters:
        - unused

  # Only show issues in new code (for gradual adoption)
  new: true
  new-from-rev: HEAD~1
```

### Inline Suppression

```go
// Suppress specific linter on a line
result, _ := doSomething() //nolint:errcheck // intentionally ignoring error

// Suppress multiple linters
func example() { //nolint:gocyclo,funlen // complex but necessary
    // ...
}

// Suppress for entire file
//nolint:errcheck // this file handles errors differently
package main
```

## Concept 4: CI/CD Integration

### What It Is

Running golangci-lint as part of your continuous integration pipeline.

### Why It Matters

- Catches issues before they reach main branch
- Enforces code quality automatically
- Provides consistent feedback to developers

### How It Works

**GitHub Actions:**
```yaml
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
          args: --timeout=5m
```

**GitLab CI:**
```yaml
lint:
  image: golangci/golangci-lint:latest
  script:
    - golangci-lint run --timeout=5m
```

**Pre-commit Hook:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.55.0
    hooks:
      - id: golangci-lint
```

## Concept 5: Performance Optimization

### What It Is

Configuring golangci-lint for optimal performance, especially in CI.

### Why It Matters

Slow linting:
- Increases CI pipeline duration
- Frustrates developers
- Wastes compute resources

### How It Works

```yaml
run:
  # Use all available CPUs
  concurrency: 0

  # Enable caching
  allow-parallel-runners: true

  # Skip slow linters if needed
  skip-dirs:
    - vendor
    - third_party
    - generated

linters:
  # Only enable what you need
  disable-all: true
  enable:
    - errcheck
    - govet
    - staticcheck
    # Don't enable slow linters unless needed:
    # - gosec (slow for large codebases)
    # - gocritic (many checks)
```

### Caching in CI

```yaml
# GitHub Actions with caching
- name: golangci-lint
  uses: golangci/golangci-lint-action@v4
  with:
    version: latest
    # Cache is built-in to the action
```

## Summary

Key takeaways:

1. **Start simple**: Enable basic linters first, add more as needed
2. **Configure for your team**: Customize rules to match your standards
3. **Manage issues wisely**: Use exclusions thoughtfully, not to hide problems
4. **Integrate early**: Add to CI from the start of a project
5. **Optimize performance**: Use caching and limit linters for speed
