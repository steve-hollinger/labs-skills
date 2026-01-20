# CLAUDE.md - {{SKILL_NAME}}

This skill teaches [brief description].

## Key Concepts

- **Concept 1**: Brief explanation
- **Concept 2**: Brief explanation
- **Concept 3**: Brief explanation

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
{{SKILL_NAME}}/
├── src/{{SNAKE_NAME}}/
│   ├── __init__.py
│   └── examples/
│       ├── example_1.py
│       ├── example_2.py
│       └── example_3.py
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Pattern
```python
# Example implementation
```

### Pattern 2: Common Pattern
```python
# Example implementation
```

## Common Mistakes

1. **Mistake description**
   - Why it happens
   - How to fix it

2. **Another mistake**
   - Why it happens
   - How to fix it

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Why isn't X working?"
Check common mistakes above, verify setup completed successfully.

### "What's the best practice for Y?"
Refer to docs/patterns.md for recommended approaches.

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`

## Dependencies

Key dependencies in pyproject.toml:
- dependency1: purpose
- dependency2: purpose
