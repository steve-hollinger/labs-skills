"""Exercise 1: Create a User Profile Model

Create a comprehensive user profile model with proper validation.

Requirements:
1. Create a UserProfile model with the following fields:
   - username: string, 3-30 characters, alphanumeric with underscores allowed
   - email: valid email address
   - full_name: string, 1-100 characters
   - age: optional integer, 13-120 if provided
   - bio: optional string, max 500 characters
   - website: optional valid URL
   - created_at: datetime, defaults to now

2. Add a field validator for username that:
   - Converts to lowercase
   - Ensures it doesn't start with a number
   - Ensures it doesn't contain consecutive underscores

3. Add a computed field 'display_name' that returns:
   - full_name if provided
   - Otherwise, username with first letter capitalized

4. Ensure the model excludes the 'email' field when converted to JSON
   (hint: use Field(exclude=True) or custom serialization)

Expected behavior:
    profile = UserProfile(
        username="Alice_Smith",
        email="alice@example.com",
        full_name="Alice Smith",
        age=28
    )
    print(profile.username)  # "alice_smith"
    print(profile.display_name)  # "Alice Smith"

    # Should raise ValidationError:
    UserProfile(username="123start", ...)  # starts with number
    UserProfile(username="bad__name", ...)  # consecutive underscores

Hints:
- Use Field() with min_length, max_length, ge, le constraints
- Use @field_validator with @classmethod decorator
- Use @computed_field with @property
- Import EmailStr and HttpUrl from pydantic
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserProfile(BaseModel):
    """User profile model - implement this!"""

    # TODO: Add fields with appropriate types and constraints
    username: str
    email: str

    # TODO: Add validators

    # TODO: Add computed field


def test_user_profile() -> None:
    """Test your UserProfile implementation."""
    # Test 1: Basic creation
    profile = UserProfile(
        username="Alice_Smith",
        email="alice@example.com",
    )
    assert profile.username == "alice_smith", f"Expected 'alice_smith', got '{profile.username}'"
    print("Test 1 passed: Username normalized to lowercase")

    # Test 2: Add more tests as you implement features
    # TODO: Add tests for all requirements

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_user_profile()
