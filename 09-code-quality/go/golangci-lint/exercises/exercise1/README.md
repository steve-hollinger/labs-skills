# Exercise 1: Configure Basic Linting

## Objective

Create a basic `.golangci.yml` configuration file for a new Go project.

## Instructions

1. Look at the `main.go` file in this directory
2. Create a `.golangci.yml` configuration that:
   - Sets a 5-minute timeout
   - Includes test files in linting
   - Enables these linters: errcheck, govet, staticcheck, unused
3. Run `golangci-lint run` and verify it works
4. Document why each linter is important

## Requirements

Your configuration must:
- Be valid YAML
- Include the `run` section with timeout
- Include the `linters` section with specific enables
- Pass validation with `golangci-lint config verify`

## Starting Point

The `main.go` file contains code that should pass all enabled linters.

## Expected Output

When running `golangci-lint run`, you should see no issues reported.

## Hints

- Start with the minimal example from the docs
- Use `disable-all: true` followed by specific enables for clarity
- Test your config works before adding more complexity

## Verification

```bash
# From this directory
golangci-lint run
# Should output nothing (no issues)

golangci-lint config verify
# Should confirm valid configuration
```
