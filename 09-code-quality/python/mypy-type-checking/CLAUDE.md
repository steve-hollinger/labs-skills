# CLAUDE.md - MyPy Type Checking

This skill teaches static type checking with MyPy for catching errors before runtime.

## Key Concepts

- **Type Annotations**: Add types to variables, function parameters, and return values
- **Type Inference**: MyPy can infer types from context
- **Strict Mode**: Enables all strict checking flags
- **Generics**: Type variables for reusable typed functions/classes
- **Protocols**: Structural subtyping (duck typing with types)

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (basic annotations)
make example-2  # Run specific example (generics/protocols)
make example-3  # Run specific example (error fixes)
make test       # Run pytest
make lint       # Run ruff and mypy
make typecheck  # Run mypy only
make clean      # Remove build artifacts
```

## Project Structure

```
mypy-type-checking/
├── src/mypy_type_checking/
│   ├── __init__.py
│   └── examples/
│       ├── example_1.py    # Basic annotations
│       ├── example_2.py    # Generics/protocols
│       └── example_3.py    # Error fixes
├── exercises/
│   ├── exercise_1.py       # Add types to module
│   ├── exercise_2.py       # Fix type errors
│   ├── exercise_3.py       # Generic data structure
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Function Type Annotations
```python
def process_data(
    items: list[str],
    callback: Callable[[str], int],
) -> dict[str, int]:
    return {item: callback(item) for item in items}
```

### Pattern 2: Class Type Annotations
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str | None = None
```

### Pattern 3: Generic Functions
```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### Pattern 4: Protocols
```python
from typing import Protocol

class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool: ...

def min_item(items: list[Comparable]) -> Comparable:
    return min(items)
```

## Common Mistakes

1. **Using `Any` too liberally**
   - Why it happens: Quick fix for type errors
   - How to fix it: Use proper types or `# type: ignore` for edge cases

2. **Forgetting `None` in union types**
   - Why it happens: Not considering function might return None
   - How to fix it: Use `X | None` for optional returns

3. **Ignoring all errors instead of fixing**
   - Why it happens: Deadline pressure
   - How to fix it: Fix errors incrementally, use per-line ignores

4. **Not using strict mode**
   - Why it happens: Too many errors with legacy code
   - How to fix it: Enable gradually with per-module overrides

## When Users Ask About...

### "How do I get started?"
Point them to:
```bash
# Run mypy on your code
uv run mypy src/

# With strict mode (recommended)
uv run mypy --strict src/
```

### "What's the difference between type hints and runtime checking?"
- MyPy: Static analysis at "compile time" (no runtime overhead)
- Runtime: Use Pydantic or beartype for runtime validation
- Type hints don't affect runtime behavior by default

### "How do I type a dictionary with specific keys?"
```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str | None

user: UserDict = {"name": "Alice", "age": 30, "email": None}
```

### "How do I handle dynamic/complex types?"
```python
# Use overloads for different return types
from typing import overload

@overload
def parse(data: str) -> dict[str, Any]: ...
@overload
def parse(data: bytes) -> list[int]: ...

def parse(data: str | bytes) -> dict[str, Any] | list[int]:
    ...
```

### "MyPy is too strict, how do I relax it?"
Configure per-module in pyproject.toml:
```toml
[[tool.mypy.overrides]]
module = ["legacy_module.*"]
ignore_errors = true
```

## Testing Notes

- Tests verify type annotations are correct
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Examples include both correctly and incorrectly typed code

## Dependencies

Key dependencies in pyproject.toml:
- mypy: The type checker
- pytest: Testing framework
- ruff: Linting (complementary)
- types-*: Type stubs for libraries
