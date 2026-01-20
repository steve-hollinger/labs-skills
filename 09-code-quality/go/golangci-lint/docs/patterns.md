# Common Patterns

## Overview

This document covers common patterns and best practices for configuring and using golangci-lint effectively.

## Pattern 1: Gradual Adoption

### When to Use

When adding golangci-lint to an existing project with many existing issues.

### Implementation

```yaml
# .golangci.yml
issues:
  # Only report issues in new code
  new: true
  new-from-rev: main

  # Or use a specific commit
  # new-from-rev: abc123

  # Or based on patch
  # new-from-patch: /path/to/patch
```

### Example

```yaml
# Phase 1: Start with new code only
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - govet

issues:
  new: true
  new-from-rev: main

# Phase 2: After a few weeks, remove "new" restrictions
# and fix existing issues gradually
```

### Pitfalls to Avoid

- Don't keep `new: true` forever - schedule time to fix existing issues
- Track technical debt of unfixed issues
- Consider creating tickets for existing issues

## Pattern 2: Team-Specific Configuration

### When to Use

When you need different linting rules for different parts of your codebase.

### Implementation

```yaml
# .golangci.yml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - govet
    - staticcheck

issues:
  exclude-rules:
    # Less strict for tests
    - path: _test\.go
      linters:
        - errcheck
        - gocritic

    # Allow unused code in examples
    - path: examples/
      linters:
        - unused
        - deadcode

    # Generated code has its own rules
    - path: generated/
      linters:
        - errcheck
        - govet
        - staticcheck

    # Internal tools can be less strict
    - path: tools/
      linters:
        - gosec
```

### Example

```yaml
# For a microservices project
issues:
  exclude-rules:
    # Proto-generated code
    - path: \.pb\.go$
      linters:
        - all

    # Mock files
    - path: mock_.*\.go$
      linters:
        - unused

    # CLI commands often have complex main functions
    - path: cmd/.*/main\.go$
      linters:
        - funlen
        - gocyclo
```

## Pattern 3: Custom Linter Groups

### When to Use

When you want to define custom groups of linters for different purposes.

### Implementation

Create multiple config files:

```yaml
# .golangci.yml - default, used locally
linters:
  enable:
    - errcheck
    - govet
    - staticcheck

# .golangci.ci.yml - stricter, used in CI
linters:
  disable-all: true
  enable:
    - errcheck
    - govet
    - staticcheck
    - gosec
    - gocyclo
    - funlen
```

Run with specific config:
```bash
# Local development
golangci-lint run

# CI pipeline
golangci-lint run -c .golangci.ci.yml
```

## Pattern 4: Security-Focused Configuration

### When to Use

For applications that handle sensitive data or are exposed to the internet.

### Implementation

```yaml
# .golangci.yml
linters:
  enable:
    - gosec       # Security-focused linter
    - errcheck    # Unchecked errors can be security issues
    - govet       # Some checks are security-related

linters-settings:
  gosec:
    # Include specific rules
    includes:
      - G101  # Hardcoded credentials
      - G102  # Bind to all interfaces
      - G103  # Unsafe block
      - G104  # Unhandled errors
      - G106  # SSH InsecureIgnoreHostKey
      - G107  # URL in variable for HTTP request
      - G108  # Profiling endpoint enabled
      - G109  # Integer overflow
      - G110  # Decompression bomb
      - G201  # SQL string formatting
      - G202  # SQL string concatenation
      - G203  # Unescaped HTML template
      - G204  # Subprocess with variable
      - G301  # Poor file permissions
      - G302  # chmod to 0666 or higher
      - G303  # File creation in shared tmp
      - G304  # File path from tainted input
      - G305  # Zip archive path traversal
      - G306  # Poor permissions on WriteFile
      - G307  # Defer file close without checking error
      - G401  # Weak crypto (MD5, SHA1)
      - G402  # TLS with InsecureSkipVerify
      - G403  # RSA keys < 2048 bits
      - G404  # Insecure random number
      - G501  # Blacklisted import (crypto/md5)
      - G502  # Blacklisted import (crypto/des)
      - G503  # Blacklisted import (crypto/rc4)
      - G504  # Blacklisted import (net/http/cgi)
      - G505  # Blacklisted import (crypto/sha1)
```

## Pattern 5: Pre-commit Integration

### When to Use

To catch issues before they're committed to the repository.

### Implementation

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.55.0
    hooks:
      - id: golangci-lint
        args: [--fast]  # Use fast mode for pre-commit
```

Or with a git hook directly:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run golangci-lint on staged Go files
staged_go_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$')

if [ -n "$staged_go_files" ]; then
    echo "Running golangci-lint..."
    golangci-lint run --fast $staged_go_files
    if [ $? -ne 0 ]; then
        echo "golangci-lint failed. Please fix the issues before committing."
        exit 1
    fi
fi
```

## Anti-Patterns

### Anti-Pattern 1: Disabling Everything

Description: Disabling linters wholesale to get a "clean" output.

```yaml
# DON'T DO THIS
issues:
  exclude:
    - ".*"  # Excludes everything!
```

### Better Approach

```yaml
# DO THIS: Be specific about what you exclude and why
issues:
  exclude-rules:
    # Specific exclusion with explanation
    - path: legacy/
      linters:
        - errcheck
      # TODO: Fix legacy code by Q2 2024
```

### Anti-Pattern 2: nolint Without Reason

Description: Using nolint comments without explaining why.

```go
// DON'T DO THIS
func process() {
    result, _ := doSomething() //nolint
}
```

### Better Approach

```go
// DO THIS: Explain why the lint is disabled
func process() {
    // Error is intentionally ignored because this is a best-effort
    // cleanup operation that shouldn't fail the main flow
    result, _ := doSomething() //nolint:errcheck // best-effort cleanup
}
```

### Anti-Pattern 3: Copy-Pasting Configs

Description: Using someone else's config without understanding it.

### Better Approach

1. Start with minimal config
2. Add linters one at a time
3. Understand what each linter does
4. Customize settings for your project

```yaml
# Start here and build up
linters:
  enable:
    - errcheck  # I understand this checks for unchecked errors
    - govet     # I understand this checks for suspicious constructs
```

### Anti-Pattern 4: Inconsistent CI and Local Config

Description: Having different behavior in CI vs local development.

### Better Approach

```yaml
# Use the same config everywhere
# .golangci.yml

run:
  timeout: 5m  # Generous timeout for both CI and local

linters:
  enable:
    - errcheck
    - govet
    - staticcheck

# Same config, same results everywhere
```

If you need different behavior, be explicit:
```bash
# Makefile
lint:
	golangci-lint run

lint-ci:
	golangci-lint run --timeout 10m --out-format github-actions
```
