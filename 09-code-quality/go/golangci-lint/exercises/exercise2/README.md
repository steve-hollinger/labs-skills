# Exercise 2: Fix Linting Issues

## Objective

Fix the linting issues in the provided code to make it pass golangci-lint.

## Instructions

1. Look at the `main.go` file in this directory - it has intentional issues
2. Run `golangci-lint run` to see the issues
3. Fix each issue while maintaining the code's functionality
4. Document what each issue was and how you fixed it

## The Issues

The code contains these types of issues:
1. Unchecked error returns
2. Unused variables
3. Ineffectual assignments
4. Shadow variables
5. Simplification opportunities

## Requirements

- Fix all linting issues
- Keep the code functionally equivalent
- Add comments explaining your fixes

## Starting Point

The `main.go` file contains problematic code. A `.golangci.yml` is provided.

## Expected Output

```bash
golangci-lint run
# Should output nothing (no issues)
```

## Hints

- Run `golangci-lint run --verbose` for more details
- Fix one issue at a time
- Test the code still works after each fix

## Verification

```bash
# Run linting
golangci-lint run

# Run the program to verify it still works
go run main.go
```
