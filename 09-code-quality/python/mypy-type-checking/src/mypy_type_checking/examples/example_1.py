"""Example 1: Basic Type Annotations

This example demonstrates fundamental type annotations in Python
and how MyPy uses them to catch errors.
"""

from dataclasses import dataclass


def demonstrate_basic_types() -> None:
    """Show basic type annotations for variables."""
    print("\n" + "=" * 60)
    print("STEP 1: Basic Type Annotations")
    print("=" * 60)

    print("""
Basic types in Python:

# Variable annotations
name: str = "Alice"
age: int = 30
height: float = 5.8
is_active: bool = True

# Without initial value (declaration only)
count: int  # Must assign before use

# Common container types
items: list[str] = ["a", "b", "c"]
scores: dict[str, int] = {"math": 95, "science": 87}
coordinates: tuple[int, int] = (10, 20)
unique_ids: set[int] = {1, 2, 3}
""")


def demonstrate_function_annotations() -> None:
    """Show function type annotations."""
    print("\n" + "=" * 60)
    print("STEP 2: Function Type Annotations")
    print("=" * 60)

    print("""
Function annotations specify parameter and return types:

def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def process_items(
    items: list[str],
    prefix: str = "",
) -> list[str]:
    return [prefix + item for item in items]

# None return type
def log_message(message: str) -> None:
    print(message)

# Multiple return types (union)
def divide(a: int, b: int) -> float | None:
    if b == 0:
        return None
    return a / b
""")


def demonstrate_optional_types() -> None:
    """Show optional and union types."""
    print("\n" + "=" * 60)
    print("STEP 3: Optional and Union Types")
    print("=" * 60)

    print("""
Union types for values that can be multiple types:

# Python 3.10+ syntax
def find_user(user_id: int) -> User | None:
    ...

# Equivalent using Optional (older style)
from typing import Optional
def find_user(user_id: int) -> Optional[User]:
    ...

# Multiple types
def process(value: int | str | None) -> str:
    if value is None:
        return "nothing"
    return str(value)

# MyPy enforces None checks
user = find_user(123)
print(user.name)  # Error: user might be None!

# Correct way
if user is not None:
    print(user.name)  # OK!

# Or using assert
assert user is not None
print(user.name)  # OK!
""")


def demonstrate_class_annotations() -> None:
    """Show class type annotations."""
    print("\n" + "=" * 60)
    print("STEP 4: Class Type Annotations")
    print("=" * 60)

    print("""
Class attributes and methods need annotations:

class User:
    # Class variable
    count: int = 0

    # Instance variables (can declare in class body)
    name: str
    email: str | None

    def __init__(self, name: str, email: str | None = None) -> None:
        self.name = name
        self.email = email
        User.count += 1

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

    @classmethod
    def create_anonymous(cls) -> "User":
        return cls("Anonymous")

    @staticmethod
    def validate_email(email: str) -> bool:
        return "@" in email

# Using dataclasses (recommended for data containers)
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    price: float
    in_stock: bool = True
""")


@dataclass
class Person:
    """Example typed dataclass."""

    name: str
    age: int
    email: str | None = None


def greet_person(person: Person) -> str:
    """Greet a person by name."""
    return f"Hello, {person.name}!"


def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def find_person_by_name(people: list[Person], name: str) -> Person | None:
    """Find a person by name, or return None if not found."""
    for person in people:
        if person.name == name:
            return person
    return None


def demonstrate_live_examples() -> None:
    """Run live examples with type-annotated code."""
    print("\n" + "=" * 60)
    print("STEP 5: Live Examples")
    print("=" * 60)

    # Create typed instances
    alice = Person(name="Alice", age=30, email="alice@example.com")
    bob = Person(name="Bob", age=25)

    print(f"Created: {alice}")
    print(f"Created: {bob}")

    # Use typed functions
    print(f"\nGreeting: {greet_person(alice)}")

    numbers: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    avg = calculate_average(numbers)
    print(f"Average of {numbers}: {avg}")

    # Demonstrate None handling
    people = [alice, bob]
    found = find_person_by_name(people, "Alice")
    if found is not None:
        print(f"Found: {found.name}, age {found.age}")

    not_found = find_person_by_name(people, "Charlie")
    if not_found is None:
        print("Charlie not found")


def show_mypy_commands() -> None:
    """Display common MyPy commands."""
    print("\n" + "=" * 60)
    print("STEP 6: Running MyPy")
    print("=" * 60)

    print("""
Common MyPy commands:

# Basic check
mypy src/

# Strict mode (recommended for new projects)
mypy --strict src/

# Show error codes (for targeted ignores)
mypy --show-error-codes src/

# Check specific file
mypy path/to/file.py

# With configuration from pyproject.toml
mypy src/  # Automatically reads pyproject.toml

# Verbose output
mypy -v src/

# Generate HTML report
mypy --html-report report/ src/
""")


def main() -> None:
    """Run the basic type annotations example."""
    print("Example 1: Basic Type Annotations")
    print("=" * 60)

    print("""
This example covers fundamental type annotations in Python.
MyPy uses these annotations to catch type errors before runtime.

Benefits of type annotations:
- Catch bugs during development, not production
- Serve as documentation
- Enable better IDE support
- Make refactoring safer
""")

    demonstrate_basic_types()
    demonstrate_function_annotations()
    demonstrate_optional_types()
    demonstrate_class_annotations()
    demonstrate_live_examples()
    show_mypy_commands()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'uv run mypy src/' to check this project")
    print("  2. Run 'make example-2' to learn about generics/protocols")
    print("  3. Complete Exercise 1 to practice adding types")


if __name__ == "__main__":
    main()
