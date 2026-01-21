---
name: testing-with-testify
description: Effective Go testing using the Testify testing toolkit. Use when writing or improving tests.
---

# Testify Framework

## Quick Start
```go
func TestWithProperPreconditions(t *testing.T) {
    // Use require for preconditions that would cause panics
    result, err := GetData()
    require.NoError(t, err)           // Stop if error
    require.NotNil(t, result)         // Stop if nil

    // Use assert for actual test assertions
    assert.Equal(t, "expected", result.Value)
    assert.Greater(t, result.Count, 0)
}
```


## Key Points
- assert
- require
- suite

## Common Mistakes
1. **Wrong assertion order** - Always use `assert.Equal(t, expected, actual)`
2. **Using assert when require is needed** - Use require for error checks and nil checks before accessing
3. **Forgetting mock.AssertExpectations** - Always call `mockObj.AssertExpectations(t)` at end

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples