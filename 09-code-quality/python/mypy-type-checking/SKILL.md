---
name: type-checking-with-mypy
description: This skill teaches static type checking with MyPy for catching errors before runtime. Use when writing or improving tests.
---

# Mypy Type Checking

## Quick Start
```python
def process_data(
    items: list[str],
    callback: Callable[[str], int],
) -> dict[str, int]:
    return {item: callback(item) for item in items}
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (basic annotations)
make example-2  # Run specific example (generics/protocols)
make example-3  # Run specific example (error fixes)
make test       # Run pytest
```

## Key Points
- Type Annotations
- Type Inference
- Strict Mode

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples