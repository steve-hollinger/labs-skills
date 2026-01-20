# Exercise 2: Refactor to Use Logging Constants

## Objective

Refactor existing code with magic strings to use logging constants.

## Instructions

1. Look at the `main.go` file - it has magic strings throughout
2. Create appropriate log key and message constants
3. Replace all magic strings with constants
4. Ensure logs are consistent and searchable

## Requirements

- All log field names must use constants
- Common log messages must use constants
- No magic strings should remain in log calls
- Maintain the same log output (just use constants)

## The Problems to Fix

The code has these issues:
1. Inconsistent key naming (userId vs user_id vs UserID)
2. Duplicate string literals
3. No way to search for all uses of a key
4. Typos would not be caught at compile time

## Starting Point

The `main.go` file contains code with magic strings that needs refactoring.

## Expected Output

After refactoring:
- Code uses constants throughout
- Same log output as before
- Code is more maintainable

## Hints

- Start by identifying all unique log keys
- Group related keys together
- Look for repeated log messages
- Use IDE "Find and Replace" to update consistently

## Verification

```bash
# Run before and after - output should be the same
go run main.go

# Search for magic strings - should find none in log calls
grep -n '"user_id"' main.go  # Should only be in const definitions
```
