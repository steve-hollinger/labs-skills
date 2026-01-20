"""Example 3: Common Type Errors and Fixes

This example demonstrates common MyPy errors and how to fix them.
"""


def demonstrate_incompatible_types() -> None:
    """Show incompatible type errors and fixes."""
    print("\n" + "=" * 60)
    print("ERROR 1: Incompatible Types")
    print("=" * 60)

    print("""
Error: Incompatible types in assignment

# Wrong
def get_age() -> int:
    return "30"  # Error: str is not int

# Fix 1: Return correct type
def get_age() -> int:
    return 30

# Fix 2: Change return annotation
def get_age() -> str:
    return "30"

# Wrong
count: int = "5"  # Error: str is not int

# Fix
count: int = 5
# or
count: str = "5"
""")


def demonstrate_missing_return() -> None:
    """Show missing return type errors."""
    print("\n" + "=" * 60)
    print("ERROR 2: Missing Return Statement")
    print("=" * 60)

    print("""
Error: Missing return statement

# Wrong
def divide(a: int, b: int) -> float:
    if b != 0:
        return a / b
    # Error: implicit None return, but return type is float

# Fix 1: Return a default value
def divide(a: int, b: int) -> float:
    if b != 0:
        return a / b
    return 0.0

# Fix 2: Change return type to allow None
def divide(a: int, b: int) -> float | None:
    if b != 0:
        return a / b
    return None

# Fix 3: Raise an exception
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")


def demonstrate_none_handling() -> None:
    """Show None-related errors and fixes."""
    print("\n" + "=" * 60)
    print("ERROR 3: Optional Value May Be None")
    print("=" * 60)

    print("""
Error: Item may be None

# Wrong
def get_name(user: User | None) -> str:
    return user.name  # Error: user might be None

# Fix 1: Add None check
def get_name(user: User | None) -> str:
    if user is None:
        return "Unknown"
    return user.name

# Fix 2: Use assertion
def get_name(user: User | None) -> str:
    assert user is not None
    return user.name

# Fix 3: Use walrus operator
def get_name(user: User | None) -> str:
    if (name := user.name if user else None) is not None:
        return name
    return "Unknown"

# Wrong - accessing dict that might not have key
def get_value(data: dict[str, int]) -> int:
    return data["key"]  # Might raise KeyError

# Fix: Use .get() with proper types
def get_value(data: dict[str, int]) -> int | None:
    return data.get("key")

def get_value_with_default(data: dict[str, int]) -> int:
    return data.get("key", 0)
""")


def demonstrate_argument_type_errors() -> None:
    """Show argument type errors and fixes."""
    print("\n" + "=" * 60)
    print("ERROR 4: Argument Type Mismatch")
    print("=" * 60)

    print("""
Error: Argument has incompatible type

# Wrong
def process(items: list[int]) -> int:
    return sum(items)

data = ["1", "2", "3"]
result = process(data)  # Error: list[str] vs list[int]

# Fix 1: Convert the data
result = process([int(x) for x in data])

# Fix 2: Change function signature
def process(items: list[int] | list[str]) -> int:
    return sum(int(x) for x in items)

# Wrong - dict vs TypedDict
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int

def create_user(data: UserDict) -> None:
    ...

# This fails because regular dict isn't UserDict
create_user({"name": "Alice", "age": 30})  # Error in strict mode

# Fix: Explicitly type the dict
user_data: UserDict = {"name": "Alice", "age": 30}
create_user(user_data)
""")


def demonstrate_mutable_default() -> None:
    """Show mutable default argument errors."""
    print("\n" + "=" * 60)
    print("ERROR 5: Mutable Default Argument")
    print("=" * 60)

    print("""
Error: Do not use mutable default argument

# Wrong - MyPy with B006 rule catches this
def append_item(items: list[int] = []) -> list[int]:
    items.append(1)
    return items

# The issue: All calls share the same list!
# append_item()  # [1]
# append_item()  # [1, 1]  Unexpected!

# Fix: Use None as default
def append_item(items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(1)
    return items

# Now each call gets a fresh list
# append_item()  # [1]
# append_item()  # [1]  Correct!
""")


def demonstrate_override_errors() -> None:
    """Show method override errors."""
    print("\n" + "=" * 60)
    print("ERROR 6: Incompatible Override")
    print("=" * 60)

    print("""
Error: Signature incompatible with supertype

# Wrong
class Animal:
    def speak(self, volume: int) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:  # Error: missing volume parameter
        return "Woof!"

# Fix: Match parent signature
class Dog(Animal):
    def speak(self, volume: int = 5) -> str:
        return "Woof!" * volume

# Wrong - return type must be same or narrower
class Processor:
    def process(self, data: str) -> str | None:
        return data

class StrictProcessor(Processor):
    def process(self, data: str) -> str:  # OK - narrower return
        return data.upper()

class BrokenProcessor(Processor):
    def process(self, data: str) -> int:  # Error - incompatible return
        return len(data)
""")


def demonstrate_type_narrowing() -> None:
    """Show type narrowing patterns."""
    print("\n" + "=" * 60)
    print("PATTERN: Type Narrowing")
    print("=" * 60)

    print("""
MyPy narrows types based on control flow:

# isinstance narrows type
def process(value: int | str) -> str:
    if isinstance(value, int):
        # value is int here
        return str(value * 2)
    # value is str here
    return value.upper()

# None checks narrow type
def get_length(text: str | None) -> int:
    if text is None:
        return 0
    # text is str here
    return len(text)

# Truthiness narrows type
def first_item(items: list[str]) -> str:
    if items:  # Narrows to non-empty list
        return items[0]
    return ""

# Using assert
def must_have_name(user: User | None) -> str:
    assert user is not None  # Narrows to User
    return user.name

# TypeGuard for custom narrowing
from typing import TypeGuard

def is_string_list(items: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in items)

def join_items(items: list[object]) -> str:
    if is_string_list(items):
        return ", ".join(items)  # items is list[str] here
    return str(items)
""")


def demonstrate_configuration_options() -> None:
    """Show MyPy configuration for handling errors."""
    print("\n" + "=" * 60)
    print("CONFIGURATION: Handling Errors")
    print("=" * 60)

    print("""
Configuration options for managing type errors:

# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true

# Per-module configuration
[[tool.mypy.overrides]]
module = ["legacy_module.*"]
ignore_errors = true

[[tool.mypy.overrides]]
module = ["third_party_lib"]
ignore_missing_imports = true

# Inline ignores (use sparingly)
x = something()  # type: ignore[assignment]

# With explanation
x = something()  # type: ignore[assignment]  # Legacy API

# Ignore specific error
def func() -> int:
    return "5"  # type: ignore[return-value]

# Reveal type for debugging
x = some_complex_expression()
reveal_type(x)  # MyPy will print the inferred type
""")


def main() -> None:
    """Run the common errors and fixes example."""
    print("Example 3: Common Type Errors and Fixes")
    print("=" * 60)

    print("""
This example covers common MyPy errors and how to fix them:
- Incompatible type assignments
- Missing return statements
- None handling issues
- Argument type mismatches
- Mutable default arguments
- Override errors
""")

    demonstrate_incompatible_types()
    demonstrate_missing_return()
    demonstrate_none_handling()
    demonstrate_argument_type_errors()
    demonstrate_mutable_default()
    demonstrate_override_errors()
    demonstrate_type_narrowing()
    demonstrate_configuration_options()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'uv run mypy --strict src/' on your own projects")
    print("  2. Fix errors using the patterns shown here")
    print("  3. Complete Exercise 2 to practice fixing type errors")


if __name__ == "__main__":
    main()
