"""Exercise 2: Fix Type Errors in Existing Code

Goal: Fix all the type errors in the code below without changing the logic.

Instructions:
1. Run `mypy --strict` on this file to see errors
2. Fix each error while preserving the intended behavior
3. Some fixes require changing types, others require adding checks

Common Fixes Needed:
- Add missing return types
- Handle None cases
- Fix incompatible type assignments
- Add proper type narrowing

Run: mypy --strict exercises/exercise_2.py
"""

from dataclasses import dataclass


# ERROR 1: Missing return type annotation
def get_greeting(name: str):
    return f"Hello, {name}!"


# ERROR 2: Incompatible return type
def parse_number(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return None  # Error: None is not int


# ERROR 3: Missing None check
@dataclass
class Product:
    name: str
    price: float


def get_product_name(product: Product | None) -> str:
    return product.name  # Error: product might be None


# ERROR 4: Incompatible types in assignment
def count_items(items: list[str]) -> int:
    count: str = 0  # Error: assigning int to str
    for item in items:
        count += 1
    return count


# ERROR 5: Mutable default argument
def append_to_list(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items


# ERROR 6: Missing return statement
def categorize_age(age: int) -> str:
    if age < 18:
        return "minor"
    elif age < 65:
        return "adult"
    # Missing return for age >= 65


# ERROR 7: Incompatible argument type
def process_numbers(numbers: list[int]) -> int:
    return sum(numbers)


def main() -> None:
    # This passes strings instead of ints
    result = process_numbers(["1", "2", "3"])
    print(result)


# ERROR 8: Dict access might fail
def get_config_value(config: dict[str, str], key: str) -> str:
    return config[key]  # Might raise KeyError


# ERROR 9: Return type too narrow
def find_in_list(items: list[str], target: str) -> str:
    for item in items:
        if item == target:
            return item
    # Implicit None return, but return type is str


# ERROR 10: Using Any (avoid in strict mode)
def process_data(data):  # Missing type annotations
    return data.upper()


# ============================================
# VERIFICATION
# ============================================

def verify_fixes() -> None:
    """Run mypy to verify all fixes."""
    import subprocess

    result = subprocess.run(
        ["mypy", "--strict", __file__],
        capture_output=True,
        text=True,
    )

    print("MyPy Output:")
    print("-" * 40)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print("-" * 40)

    if result.returncode == 0:
        print("SUCCESS: All type errors fixed!")
    else:
        print(f"REMAINING ERRORS: Fix {result.stdout.count('error')} error(s)")


if __name__ == "__main__":
    print(__doc__)
    verify_fixes()
