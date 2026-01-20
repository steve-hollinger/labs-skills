"""Example 2: Generics and Protocols

This example demonstrates advanced typing features: generics for
reusable typed code and protocols for structural subtyping.
"""

from collections.abc import Callable, Iterator
from typing import Generic, Protocol, TypeVar


def demonstrate_type_variables() -> None:
    """Show how to create and use type variables."""
    print("\n" + "=" * 60)
    print("STEP 1: Type Variables")
    print("=" * 60)

    print("""
TypeVar creates a placeholder for a type that's determined at use:

from typing import TypeVar

T = TypeVar("T")              # Any type
T_co = TypeVar("T_co", covariant=True)  # Covariant
T_contra = TypeVar("T_contra", contravariant=True)  # Contravariant

# Bounded type variables
Number = TypeVar("Number", int, float)  # Only int or float
Comparable = TypeVar("Comparable", bound="SupportsLessThan")

# Basic generic function
def first(items: list[T]) -> T | None:
    return items[0] if items else None

# Type is preserved
numbers: list[int] = [1, 2, 3]
n = first(numbers)  # n is int | None

strings: list[str] = ["a", "b"]
s = first(strings)  # s is str | None
""")


def demonstrate_generic_functions() -> None:
    """Show generic function examples."""
    print("\n" + "=" * 60)
    print("STEP 2: Generic Functions")
    print("=" * 60)

    print("""
Generic functions work with any type while preserving type info:

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

def identity(value: T) -> T:
    return value

def swap(pair: tuple[T, K]) -> tuple[K, T]:
    return (pair[1], pair[0])

def get_or_default(
    mapping: dict[K, V],
    key: K,
    default: V,
) -> V:
    return mapping.get(key, default)

# Multiple type variables
def zip_with(
    items1: list[T],
    items2: list[K],
    func: Callable[[T, K], V],
) -> list[V]:
    return [func(a, b) for a, b in zip(items1, items2)]
""")


def demonstrate_generic_classes() -> None:
    """Show generic class examples."""
    print("\n" + "=" * 60)
    print("STEP 3: Generic Classes")
    print("=" * 60)

    print("""
Generic classes are type-parameterized containers:

# Python 3.12+ syntax
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

# Older syntax with Generic base class
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def map(self, func: Callable[[T], K]) -> "Box[K]":
        return Box(func(self._value))

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value = int_stack.pop()  # int

str_box = Box("hello")
len_box = str_box.map(len)  # Box[int]
""")


def demonstrate_protocols() -> None:
    """Show protocol examples for structural subtyping."""
    print("\n" + "=" * 60)
    print("STEP 4: Protocols (Structural Subtyping)")
    print("=" * 60)

    print("""
Protocols define interfaces without inheritance (duck typing with types):

from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Sizeable(Protocol):
    def size(self) -> int: ...

# Any class with matching methods satisfies the protocol
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK - has draw()
render(Square())  # OK - has draw()
render("hello")   # Error - str has no draw()

# Protocol with attributes
class Named(Protocol):
    name: str

class User:
    def __init__(self, name: str) -> None:
        self.name = name

def greet(obj: Named) -> str:
    return f"Hello, {obj.name}"

greet(User("Alice"))  # OK
""")


def demonstrate_callable_protocol() -> None:
    """Show Callable and custom callable protocols."""
    print("\n" + "=" * 60)
    print("STEP 5: Callable Types")
    print("=" * 60)

    print("""
Type functions and callbacks with Callable or Protocol:

from collections.abc import Callable

# Simple callback
def apply_func(
    items: list[int],
    func: Callable[[int], int],
) -> list[int]:
    return [func(x) for x in items]

apply_func([1, 2, 3], lambda x: x * 2)

# Multi-argument callback
Comparator = Callable[[str, str], int]

def sort_with(items: list[str], cmp: Comparator) -> list[str]:
    ...

# Protocol for complex callables
class Processor(Protocol):
    def __call__(
        self,
        data: str,
        *,
        verbose: bool = False,
    ) -> int: ...

def run_processor(p: Processor) -> None:
    result = p("hello", verbose=True)
    print(result)
""")


# Live examples with actual code

T = TypeVar("T")


class Stack(Generic[T]):
    """A generic stack implementation."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push an item onto the stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Pop an item from the stack."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T | None:
        """Peek at the top item without removing it."""
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)


class Printable(Protocol):
    """Protocol for objects that can be printed."""

    def to_string(self) -> str:
        """Convert to string representation."""
        ...


class Document:
    """A document that can be printed."""

    def __init__(self, title: str, content: str) -> None:
        self.title = title
        self.content = content

    def to_string(self) -> str:
        return f"{self.title}\n{'=' * len(self.title)}\n{self.content}"


class Report:
    """A report that can be printed."""

    def __init__(self, name: str, data: dict[str, int]) -> None:
        self.name = name
        self.data = data

    def to_string(self) -> str:
        lines = [f"Report: {self.name}"]
        for key, value in self.data.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def print_item(item: Printable) -> None:
    """Print any object that satisfies Printable protocol."""
    print(item.to_string())


def demonstrate_live_examples() -> None:
    """Run live examples with generic and protocol types."""
    print("\n" + "=" * 60)
    print("STEP 6: Live Examples")
    print("=" * 60)

    # Generic Stack
    print("\nGeneric Stack:")
    int_stack: Stack[int] = Stack()
    int_stack.push(1)
    int_stack.push(2)
    int_stack.push(3)
    print(f"  Stack has {len(int_stack)} items")
    print(f"  Top item: {int_stack.peek()}")
    print(f"  Popped: {int_stack.pop()}")

    str_stack: Stack[str] = Stack()
    str_stack.push("hello")
    str_stack.push("world")
    print(f"  String stack top: {str_stack.peek()}")

    # Protocol usage
    print("\nProtocol Printable:")
    doc = Document("My Document", "This is the content.")
    report = Report("Sales", {"Q1": 100, "Q2": 150, "Q3": 200})

    print_item(doc)
    print()
    print_item(report)


def main() -> None:
    """Run the generics and protocols example."""
    print("Example 2: Generics and Protocols")
    print("=" * 60)

    print("""
This example covers advanced typing features:
- Type variables for generic code
- Generic functions and classes
- Protocols for structural subtyping
- Callable types for function parameters
""")

    demonstrate_type_variables()
    demonstrate_generic_functions()
    demonstrate_generic_classes()
    demonstrate_protocols()
    demonstrate_callable_protocol()
    demonstrate_live_examples()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Try creating your own generic class")
    print("  2. Run 'make example-3' to learn about common errors")
    print("  3. Complete Exercise 3 to implement a generic data structure")


if __name__ == "__main__":
    main()
