# Core Concepts

## Overview

MyPy is a static type checker for Python that analyzes your code without running it. It uses type annotations (PEP 484) to catch type-related bugs before they happen at runtime.

## Concept 1: Type Annotations

### What They Are

Type annotations are hints that tell MyPy (and other tools) what types variables, parameters, and return values should have.

### Why They Matter

- Catch bugs before runtime
- Serve as documentation
- Enable better IDE support (autocomplete, refactoring)
- Make code more maintainable

### How They Work

```python
# Variable annotations
name: str = "Alice"
age: int = 30
scores: list[int] = [95, 87, 92]

# Function annotations
def greet(name: str, formal: bool = False) -> str:
    if formal:
        return f"Good day, {name}."
    return f"Hi, {name}!"

# Class annotations
class User:
    name: str
    email: str | None

    def __init__(self, name: str, email: str | None = None) -> None:
        self.name = name
        self.email = email
```

## Concept 2: Type Inference

### What It Is

MyPy can often figure out types automatically from context, even without explicit annotations.

### Why It Matters

- Less boilerplate code
- Easier gradual adoption
- Still catches errors

### How It Works

```python
# MyPy infers these types
x = 5              # int
name = "Alice"     # str
items = [1, 2, 3]  # list[int]

# Inference from operations
total = x + 10     # int
upper = name.upper()  # str

# Function return inference (basic)
def double(n: int):
    return n * 2   # MyPy infers -> int
```

Note: In strict mode, explicit return types are required.

## Concept 3: Union Types and Optional

### What They Are

Union types represent values that can be one of several types. Optional is a special case for "type or None".

### Why They Matter

- Model real-world data accurately
- Handle nullable values safely
- Prevent None-related bugs

### How They Work

```python
# Union types (Python 3.10+)
def process(value: int | str) -> str:
    if isinstance(value, int):
        return str(value)
    return value

# Optional (equivalent to X | None)
def find_user(user_id: int) -> User | None:
    # Might return None if not found
    ...

# MyPy enforces None checks
user = find_user(123)
print(user.name)  # Error: might be None!

if user is not None:
    print(user.name)  # OK: narrowed type
```

## Concept 4: Generics

### What They Are

Generics allow you to write functions and classes that work with any type while maintaining type safety.

### Why They Matter

- Reusable typed code
- Type-safe containers
- Better abstraction

### How They Work

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """Return first item or None if empty."""
    return items[0] if items else None

# Usage - type is preserved
numbers: list[int] = [1, 2, 3]
n = first(numbers)  # n is int | None

names: list[str] = ["Alice", "Bob"]
s = first(names)    # s is str | None

# Generic classes
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

## Concept 5: Protocols

### What They Are

Protocols define structural subtyping (duck typing with types). A class matches a protocol if it has the required methods/attributes.

### Why They Matter

- Type-safe duck typing
- No inheritance required
- Flexible interfaces

### How They Work

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Both work - they have draw() method
render(Circle())  # OK
render(Square())  # OK
render("hello")   # Error: str has no draw()
```

## Concept 6: Strict Mode

### What It Is

Strict mode enables all optional checking flags, making MyPy catch more potential issues.

### Why It Matters

- Maximum type safety
- Catches subtle bugs
- Encourages complete annotations

### How It Works

```toml
[tool.mypy]
strict = true

# Strict mode enables:
# - disallow_untyped_defs
# - disallow_untyped_calls
# - disallow_incomplete_defs
# - check_untyped_defs
# - warn_return_any
# - warn_unused_ignores
# - no_implicit_optional
# And more...
```

```python
# Without strict mode, this passes:
def process(data):  # No type annotations
    return data.value

# With strict mode:
# error: Function is missing a type annotation
```

## Summary

Key takeaways:

1. **Annotations**: Add types to catch bugs before runtime
2. **Inference**: MyPy deduces types from context
3. **Union/Optional**: Handle multiple possible types safely
4. **Generics**: Write reusable typed code
5. **Protocols**: Duck typing with type safety
6. **Strict Mode**: Maximum type checking for high-quality code
