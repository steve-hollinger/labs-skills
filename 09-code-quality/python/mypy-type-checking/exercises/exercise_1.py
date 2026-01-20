"""Exercise 1: Add Types to an Untyped Module

Goal: Add complete type annotations to the untyped code below.

Instructions:
1. Add type annotations to all functions
2. Add type annotations to all variables
3. Add type annotations to the class
4. Make sure the code passes `mypy --strict`

Requirements:
- All functions must have parameter and return type annotations
- Use appropriate types (str, int, list, dict, etc.)
- Handle optional values correctly with `| None`
- Use dataclass for the User class

Hints:
- Start with function return types
- Look at what's being passed to each function
- Use list[str] instead of just list
- Don't forget __init__ returns None
"""

# ============================================
# CODE TO ADD TYPES TO
# ============================================


def greet(name):
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


def calculate_total(prices, tax_rate=0.1):
    """Calculate total with tax."""
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)


def find_user(users, username):
    """Find a user by username, return None if not found."""
    for user in users:
        if user.username == username:
            return user
    return None


def process_items(items, transform=None):
    """Process items with optional transform function."""
    if transform is None:
        return items
    return [transform(item) for item in items]


class User:
    """A user with username and email."""

    def __init__(self, username, email, age=None):
        self.username = username
        self.email = email
        self.age = age

    def display_name(self):
        """Return display name."""
        return self.username.title()

    def is_adult(self):
        """Check if user is adult (18+)."""
        if self.age is None:
            return None
        return self.age >= 18


def get_user_emails(users):
    """Extract emails from list of users."""
    emails = []
    for user in users:
        emails.append(user.email)
    return emails


def merge_dicts(dict1, dict2):
    """Merge two dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result


# ============================================
# TEST YOUR SOLUTION
# ============================================

def verify_types() -> bool:
    """Verify the types are correct by running the code."""
    import subprocess

    # Write this file path
    result = subprocess.run(
        ["mypy", "--strict", __file__],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("SUCCESS: All type checks passed!")
        return True
    else:
        print("ERRORS:")
        print(result.stdout)
        print(result.stderr)
        return False


if __name__ == "__main__":
    print(__doc__)
    print("\nCode to add types to (see above in file)")
    print("\nRun: mypy --strict exercises/exercise_1.py")
    print("Or: python exercises/exercise_1.py  (to verify)")
