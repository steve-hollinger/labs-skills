// Example 3: CI Pipeline Integration
//
// This example demonstrates how to integrate golangci-lint into CI/CD
// pipelines including GitHub Actions, GitLab CI, and pre-commit hooks.
package main

import (
	"fmt"
)

func main() {
	fmt.Println("Example 3: CI Pipeline Integration")
	fmt.Println("========================================")
	fmt.Println()

	// GitHub Actions setup
	showGitHubActionsConfig()

	// GitLab CI setup
	showGitLabCIConfig()

	// Pre-commit hook setup
	showPreCommitConfig()

	// Makefile integration
	showMakefileIntegration()

	// Tips for CI success
	showCITips()

	fmt.Println("\nExample completed successfully!")
}

func showGitHubActionsConfig() {
	fmt.Println("=== GitHub Actions Configuration ===")
	fmt.Println()
	fmt.Println("File: .github/workflows/lint.yml")
	fmt.Println()
	fmt.Println("```yaml")
	fmt.Print(`name: Lint

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  golangci-lint:
    name: golangci-lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true

      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest
          # Optional: golangci-lint command line arguments
          args: --timeout=5m
          # Optional: show only new issues for PRs
          only-new-issues: true
          # Optional: if set, only errors are reported
          # skip-pkg-cache: true
`)
	fmt.Println("```")
	fmt.Println()
	fmt.Println("Key features:")
	fmt.Println("  - Uses official golangci-lint-action")
	fmt.Println("  - Automatic Go module caching")
	fmt.Println("  - 'only-new-issues' perfect for legacy codebases")
	fmt.Println()
}

func showGitLabCIConfig() {
	fmt.Println("=== GitLab CI Configuration ===")
	fmt.Println()
	fmt.Println("File: .gitlab-ci.yml")
	fmt.Println()
	fmt.Println("```yaml")
	fmt.Print(`stages:
  - lint
  - test
  - build

variables:
  GOLANGCI_LINT_VERSION: "v1.55.0"

lint:
  stage: lint
  image: golangci/golangci-lint:${GOLANGCI_LINT_VERSION}
  script:
    - golangci-lint run --timeout=5m --out-format=line-number
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  cache:
    key: golangci-lint-cache
    paths:
      - .cache/golangci-lint

lint:new-only:
  stage: lint
  image: golangci/golangci-lint:${GOLANGCI_LINT_VERSION}
  script:
    - golangci-lint run --new-from-rev=origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME} --timeout=5m
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  allow_failure: true
`)
	fmt.Println("```")
	fmt.Println()
	fmt.Println("Key features:")
	fmt.Println("  - Uses official golangci-lint Docker image")
	fmt.Println("  - Separate job for new-issues-only on MRs")
	fmt.Println("  - Cache for faster subsequent runs")
	fmt.Println()
}

func showPreCommitConfig() {
	fmt.Println("=== Pre-commit Hook Configuration ===")
	fmt.Println()
	fmt.Println("Option 1: Using pre-commit framework")
	fmt.Println("File: .pre-commit-config.yaml")
	fmt.Println()
	fmt.Println("```yaml")
	fmt.Print(`repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.55.0
    hooks:
      - id: golangci-lint
        args: [--fast]  # Faster checks for commits
`)
	fmt.Println("```")
	fmt.Println()
	fmt.Println("Install with: pre-commit install")
	fmt.Println()

	fmt.Println("Option 2: Direct git hook")
	fmt.Println("File: .git/hooks/pre-commit")
	fmt.Println()
	fmt.Println("```bash")
	fmt.Print(`#!/bin/bash
# Pre-commit hook for golangci-lint

set -e

# Get list of staged Go files
STAGED_GO_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$' || true)

if [ -z "$STAGED_GO_FILES" ]; then
    echo "No Go files staged, skipping lint"
    exit 0
fi

echo "Running golangci-lint on staged files..."

# Run golangci-lint only on staged files
if ! golangci-lint run --fast $STAGED_GO_FILES; then
    echo ""
    echo "golangci-lint found issues. Please fix them before committing."
    echo "To bypass this check (not recommended), use: git commit --no-verify"
    exit 1
fi

echo "golangci-lint passed!"
`)
	fmt.Println("```")
	fmt.Println()
	fmt.Println("Make executable: chmod +x .git/hooks/pre-commit")
	fmt.Println()
}

func showMakefileIntegration() {
	fmt.Println("=== Makefile Integration ===")
	fmt.Println()
	fmt.Println("```makefile")
	fmt.Print(`# Linting targets
.PHONY: lint lint-fix lint-ci

# Check if golangci-lint is installed
GOLANGCI_LINT := $(shell command -v golangci-lint 2> /dev/null)

# Install golangci-lint if needed
install-lint:
ifndef GOLANGCI_LINT
	@echo "Installing golangci-lint..."
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
endif

# Run linting locally
lint: install-lint
	golangci-lint run ./...

# Run linting and attempt to fix issues
lint-fix: install-lint
	golangci-lint run --fix ./...

# Run linting for CI (stricter, with output format)
lint-ci: install-lint
	golangci-lint run \
		--timeout=10m \
		--out-format=github-actions \
		./...

# Run linting only on changed files (useful for large repos)
lint-diff: install-lint
	golangci-lint run --new-from-rev=origin/main ./...
`)
	fmt.Println("```")
	fmt.Println()
}

func showCITips() {
	fmt.Println("=== Tips for CI Success ===")
	fmt.Println()

	tips := []struct {
		title       string
		description string
		example     string
	}{
		{
			title:       "1. Set Appropriate Timeouts",
			description: "CI environments are often slower than local machines",
			example:     "golangci-lint run --timeout=10m",
		},
		{
			title:       "2. Use Caching",
			description: "golangci-lint supports caching for faster runs",
			example:     "Cache ~/.cache/golangci-lint between CI runs",
		},
		{
			title:       "3. Output Formats for CI",
			description: "Use CI-specific output formats for better integration",
			example:     "golangci-lint run --out-format=github-actions",
		},
		{
			title:       "4. Gradual Adoption",
			description: "Only check new code when adding to existing projects",
			example:     "golangci-lint run --new-from-rev=origin/main",
		},
		{
			title:       "5. Fail Fast",
			description: "Stop on first error to save CI time",
			example:     "golangci-lint run --max-issues-per-linter=1",
		},
		{
			title:       "6. Version Pinning",
			description: "Pin golangci-lint version for reproducible builds",
			example:     "uses: golangci/golangci-lint-action@v4 with version: v1.55.0",
		},
	}

	for _, tip := range tips {
		fmt.Printf("%s\n", tip.title)
		fmt.Printf("   %s\n", tip.description)
		fmt.Printf("   Example: %s\n", tip.example)
		fmt.Println()
	}

	fmt.Println("Output format options:")
	fmt.Println("  - colored-line-number : Default, good for local use")
	fmt.Println("  - github-actions      : GitHub Actions annotations")
	fmt.Println("  - line-number         : Plain text, CI-friendly")
	fmt.Println("  - json                : Machine-readable")
	fmt.Println("  - checkstyle          : Jenkins-compatible")
	fmt.Println("  - code-climate        : Code Climate compatible")
	fmt.Println()
}
