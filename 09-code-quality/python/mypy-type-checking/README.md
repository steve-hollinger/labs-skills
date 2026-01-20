# MyPy Type Checking

Learn static type checking with MyPy, Python's most popular type checker. MyPy analyzes your code to catch type errors before runtime, improving code quality and maintainability.

## Learning Objectives

After completing this skill, you will be able to:
- Add type annotations to Python code
- Configure MyPy with strict mode settings
- Use generics, protocols, and advanced types
- Fix common type errors
- Integrate MyPy into CI/CD pipelines

## Prerequisites

- Python 3.11+
- UV package manager
- Basic Python development experience

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Basic Type Annotations

Add types to function signatures and variables:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

count: int = 0
items: list[str] = ["a", "b", "c"]
```

### Running MyPy

Check your code with MyPy:

```bash
# Check specific files
mypy src/

# Strict mode (recommended)
mypy --strict src/

# Show error codes
mypy --show-error-codes src/

# Generate report
mypy --html-report report/ src/
```

### Configuration

Configure MyPy in pyproject.toml:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

## Examples

### Example 1: Basic Type Annotations

Add types to functions and variables.

```bash
make example-1
```

### Example 2: Generics and Protocols

Use advanced typing features.

```bash
make example-2
```

### Example 3: Common Errors and Fixes

Learn to fix typical type errors.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Add types to an untyped module
2. **Exercise 2**: Fix type errors in existing code
3. **Exercise 3**: Implement a generic data structure

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Type Annotation Quick Reference

| Type | Example |
|------|---------|
| Basic | `int`, `str`, `float`, `bool` |
| Optional | `str \| None` or `Optional[str]` |
| List | `list[int]` |
| Dict | `dict[str, int]` |
| Tuple | `tuple[int, str]` |
| Callable | `Callable[[int, str], bool]` |
| Any | `Any` (avoid when possible) |

## Common Mistakes

### Mistake 1: Using mutable default arguments

MyPy catches this common Python gotcha:

```python
# Wrong
def append_item(items: list[int] = []) -> list[int]:
    items.append(1)
    return items

# Correct
def append_item(items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(1)
    return items
```

### Mistake 2: Forgetting return type annotations

```python
# Wrong - MyPy infers Any
def get_name(user):
    return user.name

# Correct
def get_name(user: User) -> str:
    return user.name
```

## Further Reading

- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- Related skills in this repository:
  - [Ruff Linting](../ruff-linting/)
  - [Pydantic V2](../../../01-language-frameworks/python/pydantic-v2/)
