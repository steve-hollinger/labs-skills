# Exercise 3: CI Configuration

## Objective

Create a complete CI integration for golangci-lint including GitHub Actions workflow and a production-ready configuration.

## Instructions

1. Create a `.golangci.yml` with production settings
2. Create a GitHub Actions workflow in `.github/workflows/lint.yml`
3. Include appropriate exclusions for test files
4. Set up caching for faster CI runs

## Requirements

### Configuration (.golangci.yml)

Must include:
- 10-minute timeout (CI needs more time)
- All recommended linters enabled
- Appropriate exclusions for tests
- Security linter (gosec) enabled

### GitHub Actions Workflow

Must include:
- Trigger on push and pull_request
- Go setup with caching
- golangci-lint-action usage
- Proper timeout handling

## Starting Point

The `main.go` and `main_test.go` files provide sample code to lint.

## Expected Output

When the workflow runs:
1. All linters should pass on main.go
2. Test files should have relaxed rules
3. Workflow should complete in reasonable time

## Hints

- Use `disable-all: true` then enable specific linters
- The `only-new-issues` option helps with legacy code
- Cache the golangci-lint cache directory

## Verification

```bash
# Verify config is valid
golangci-lint config verify

# Run lint locally to test
golangci-lint run

# Check workflow syntax (requires act or similar)
# act -n
```
