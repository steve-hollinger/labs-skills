# Common Patterns

## Overview

This document covers common patterns and best practices for using MyPy effectively.

## Pattern 1: Gradual Typing

### When to Use

When adding types to an existing untyped codebase.

### Implementation

Start with critical code paths and expand gradually:

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
# Start without strict
warn_return_any = true
check_untyped_defs = true

# Ignore untyped modules initially
[[tool.mypy.overrides]]
module = ["legacy_module.*"]
ignore_errors = true
```

```python
# Add types to new code
def new_function(data: dict[str, int]) -> list[int]:
    return list(data.values())

# Mark untyped code for later
def legacy_function(data):  # type: ignore[no-untyped-def]
    ...
```

### Pitfalls to Avoid

- Don't use `Any` everywhere just to pass checks
- Fix errors incrementally, not all at once

## Pattern 2: TypedDict for Structured Dictionaries

### When to Use

When working with dictionaries that have known keys and types.

### Implementation

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: NotRequired[int]  # Optional key

def process_user(user: UserDict) -> str:
    # MyPy knows user["name"] is str
    return user["name"].upper()

# Usage
user: UserDict = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
}
```

### Pitfalls to Avoid

- TypedDict doesn't validate at runtime
- Use Pydantic if you need runtime validation

## Pattern 3: Callable Types

### When to Use

When functions accept callbacks or return functions.

### Implementation

```python
from collections.abc import Callable

# Simple callback
def apply(
    items: list[int],
    func: Callable[[int], int],
) -> list[int]:
    return [func(x) for x in items]

# Callback with multiple args
Handler = Callable[[str, int], bool]

def register_handler(handler: Handler) -> None:
    ...

# Callable with keyword args (use Protocol)
from typing import Protocol

class Processor(Protocol):
    def __call__(self, data: str, *, verbose: bool = False) -> int: ...
```

### Pitfalls to Avoid

- Callable doesn't support keyword-only arguments well
- Use Protocol for complex signatures

## Pattern 4: Overloaded Functions

### When to Use

When a function has different return types based on input types.

### Implementation

```python
from typing import overload

@overload
def parse(data: str) -> dict[str, str]: ...

@overload
def parse(data: bytes) -> list[int]: ...

@overload
def parse(data: None) -> None: ...

def parse(data: str | bytes | None) -> dict[str, str] | list[int] | None:
    if data is None:
        return None
    if isinstance(data, str):
        return {"raw": data}
    return list(data)

# MyPy knows the return type
result1 = parse("hello")  # dict[str, str]
result2 = parse(b"hello")  # list[int]
result3 = parse(None)      # None
```

### Pitfalls to Avoid

- Keep overloads in sync with implementation
- Order matters for overlapping signatures

## Pattern 5: Type Guards

### When to Use

When narrowing types in conditional statements.

### Implementation

```python
from typing import TypeGuard

def is_string_list(items: list[object]) -> TypeGuard[list[str]]:
    """Check if all items are strings."""
    return all(isinstance(item, str) for item in items)

def process(items: list[object]) -> str:
    if is_string_list(items):
        # MyPy knows items is list[str] here
        return ", ".join(items)
    return str(items)
```

### Pitfalls to Avoid

- TypeGuard functions must actually check what they claim
- No runtime enforcement

## Pattern 6: Generic Classes

### When to Use

When creating reusable container types.

### Implementation

```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Result(Generic[T]):
    """Result container with success/failure states."""

    def __init__(self, value: T | None = None, error: str | None = None) -> None:
        self._value = value
        self._error = error

    def is_ok(self) -> bool:
        return self._error is None

    def unwrap(self) -> T:
        if self._error is not None:
            raise ValueError(self._error)
        assert self._value is not None
        return self._value

# Usage
def divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Result(error="Division by zero")
    return Result(value=a / b)

result = divide(10, 2)
if result.is_ok():
    print(result.unwrap())  # 5.0
```

### Pitfalls to Avoid

- Keep generic type variables consistent
- Document type variable constraints

## Anti-Patterns

### Anti-Pattern 1: Using Any Everywhere

```python
# Bad - defeats purpose of typing
def process(data: Any) -> Any:
    return data.value

# Good - use proper types
def process(data: DataContainer) -> str:
    return data.value
```

### Better Approach

Use `object` or a Protocol when you need flexibility:
```python
def process(data: object) -> str:
    if hasattr(data, "value"):
        return str(getattr(data, "value"))
    return str(data)
```

### Anti-Pattern 2: Ignoring All Errors

```python
# Bad - hides real issues
# type: ignore

# Good - ignore specific errors with explanation
# type: ignore[arg-type]  # Legacy API requires string
```

### Anti-Pattern 3: Cast Instead of Fix

```python
from typing import cast

# Bad - hides the real issue
data = cast(dict[str, int], get_data())

# Good - fix the source
def get_data() -> dict[str, int]:
    return {"count": 1}
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Existing untyped code | Gradual Typing |
| JSON/API responses | TypedDict |
| Function parameters | Callable or Protocol |
| Different return types | Overload |
| Runtime type checks | TypeGuard |
| Reusable containers | Generic Classes |
