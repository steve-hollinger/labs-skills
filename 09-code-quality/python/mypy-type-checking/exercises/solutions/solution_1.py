"""Solution for Exercise 1: Add Types to an Untyped Module

This solution shows the properly typed version of the code.
"""

from collections.abc import Callable
from dataclasses import dataclass


def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


def calculate_total(prices: list[float], tax_rate: float = 0.1) -> float:
    """Calculate total with tax."""
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)


@dataclass
class User:
    """A user with username and email."""

    username: str
    email: str
    age: int | None = None

    def display_name(self) -> str:
        """Return display name."""
        return self.username.title()

    def is_adult(self) -> bool | None:
        """Check if user is adult (18+)."""
        if self.age is None:
            return None
        return self.age >= 18


def find_user(users: list[User], username: str) -> User | None:
    """Find a user by username, return None if not found."""
    for user in users:
        if user.username == username:
            return user
    return None


def process_items(
    items: list[str],
    transform: Callable[[str], str] | None = None,
) -> list[str]:
    """Process items with optional transform function."""
    if transform is None:
        return items
    return [transform(item) for item in items]


def get_user_emails(users: list[User]) -> list[str]:
    """Extract emails from list of users."""
    emails: list[str] = []
    for user in users:
        emails.append(user.email)
    return emails


def merge_dicts(
    dict1: dict[str, int],
    dict2: dict[str, int],
) -> dict[str, int]:
    """Merge two dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result


# ============================================
# TEST THE SOLUTION
# ============================================

def main() -> None:
    """Test the typed functions."""
    # Test greet
    message = greet("Alice")
    print(f"Greeting: {message}")

    # Test calculate_total
    prices: list[float] = [10.0, 20.0, 30.0]
    total = calculate_total(prices)
    print(f"Total: ${total:.2f}")

    # Test User
    alice = User(username="alice", email="alice@example.com", age=30)
    bob = User(username="bob", email="bob@example.com")

    print(f"User: {alice.display_name()}")
    print(f"Is adult: {alice.is_adult()}")
    print(f"Bob is adult: {bob.is_adult()}")

    # Test find_user
    users = [alice, bob]
    found = find_user(users, "alice")
    if found is not None:
        print(f"Found: {found.username}")

    # Test process_items
    items = ["hello", "world"]
    processed = process_items(items, str.upper)
    print(f"Processed: {processed}")

    # Test get_user_emails
    emails = get_user_emails(users)
    print(f"Emails: {emails}")

    # Test merge_dicts
    dict1: dict[str, int] = {"a": 1, "b": 2}
    dict2: dict[str, int] = {"c": 3, "d": 4}
    merged = merge_dicts(dict1, dict2)
    print(f"Merged: {merged}")


if __name__ == "__main__":
    main()
