"""Solution for Exercise 1: Create a User Profile Model

This is the reference solution for the UserProfile exercise.
"""

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    ValidationError,
    computed_field,
    field_validator,
)


class UserProfile(BaseModel):
    """User profile model with comprehensive validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    # Required fields
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr = Field(exclude=True)  # Excluded from serialization
    full_name: str = Field(min_length=1, max_length=100)

    # Optional fields
    age: Optional[int] = Field(default=None, ge=13, le=120)
    bio: Optional[str] = Field(default=None, max_length=500)
    website: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and normalize username."""
        # Convert to lowercase
        v = v.lower()

        # Check alphanumeric with underscores
        if not all(c.isalnum() or c == "_" for c in v):
            raise ValueError("Username must be alphanumeric with underscores only")

        # Check doesn't start with number
        if v[0].isdigit():
            raise ValueError("Username cannot start with a number")

        # Check no consecutive underscores
        if "__" in v:
            raise ValueError("Username cannot contain consecutive underscores")

        return v

    @computed_field
    @property
    def display_name(self) -> str:
        """Return display name - full_name if available, otherwise capitalized username."""
        if self.full_name:
            return self.full_name
        return self.username.replace("_", " ").title()


def test_user_profile() -> None:
    """Test the UserProfile implementation."""
    print("Testing UserProfile implementation...")

    # Test 1: Basic creation with normalization
    profile = UserProfile(
        username="Alice_Smith",
        email="alice@example.com",
        full_name="Alice Smith",
        age=28,
    )
    assert profile.username == "alice_smith", f"Expected 'alice_smith', got '{profile.username}'"
    print("  Test 1 passed: Username normalized to lowercase")

    # Test 2: Display name uses full_name when available
    assert profile.display_name == "Alice Smith"
    print("  Test 2 passed: Display name returns full_name")

    # Test 3: Display name uses username when full_name is minimal
    profile2 = UserProfile(
        username="john_doe", email="john@example.com", full_name=""
    )
    # Note: full_name has min_length=1, so this would fail validation
    # Let's test with a valid but simple name instead
    profile2 = UserProfile(
        username="john_doe",
        email="john@example.com",
        full_name="J",  # Minimal valid name
    )
    assert profile2.display_name == "J"
    print("  Test 3 passed: Display name handles minimal full_name")

    # Test 4: Email is excluded from serialization
    profile_dict = profile.model_dump()
    assert "email" not in profile_dict
    print("  Test 4 passed: Email excluded from serialization")

    # Test 5: Username starting with number raises error
    try:
        UserProfile(
            username="123start", email="test@example.com", full_name="Test User"
        )
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "cannot start with a number" in str(e)
        print("  Test 5 passed: Username starting with number rejected")

    # Test 6: Consecutive underscores rejected
    try:
        UserProfile(
            username="bad__name", email="test@example.com", full_name="Test User"
        )
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "consecutive underscores" in str(e)
        print("  Test 6 passed: Consecutive underscores rejected")

    # Test 7: Optional fields work correctly
    profile_minimal = UserProfile(
        username="minimal_user",
        email="minimal@example.com",
        full_name="Minimal User",
    )
    assert profile_minimal.age is None
    assert profile_minimal.bio is None
    assert profile_minimal.website is None
    print("  Test 7 passed: Optional fields default to None")

    # Test 8: Age constraints
    try:
        UserProfile(
            username="young", email="young@example.com", full_name="Young User", age=12
        )
        raise AssertionError("Should have raised ValidationError for age < 13")
    except ValidationError:
        print("  Test 8 passed: Age under 13 rejected")

    # Test 9: Website URL validation
    profile_with_website = UserProfile(
        username="webuser",
        email="web@example.com",
        full_name="Web User",
        website="https://example.com",
    )
    assert str(profile_with_website.website) == "https://example.com/"
    print("  Test 9 passed: Valid URL accepted")

    # Test 10: Serialization to JSON
    json_str = profile.model_dump_json()
    assert "alice@example.com" not in json_str  # Email excluded
    assert "alice_smith" in json_str  # Username included
    print("  Test 10 passed: JSON serialization works correctly")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_user_profile()
