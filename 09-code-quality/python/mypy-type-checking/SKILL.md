---
name: type-checking-with-mypy
description: Static type checking with MyPy for catching errors before runtime. Use when writing or improving tests.
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


## Key Points
- Type Annotations
- Type Inference
- Strict Mode

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples