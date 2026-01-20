"""Example 2: Custom Validators

This example demonstrates field validators and model validators
for implementing custom validation logic.
"""

from datetime import date, datetime
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class UserRegistration(BaseModel):
    """User registration with custom field validators."""

    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Ensure username is alphanumeric and lowercase."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_valid_domain(cls, v: str) -> str:
        """Validate email format and domain."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        local, domain = v.rsplit("@", 1)
        if "." not in domain:
            raise ValueError("Invalid email domain")
        # Normalize to lowercase
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Ensure password meets strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegistration":
        """Ensure password and confirmation match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class DateRange(BaseModel):
    """A date range with cross-field validation."""

    start_date: date
    end_date: date
    name: str = Field(default="")

    @model_validator(mode="after")
    def validate_date_range(self) -> "DateRange":
        """Ensure end_date is after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PriceWithDiscount(BaseModel):
    """Price model with validators that transform data."""

    original_price: float = Field(gt=0)
    discount_percent: float = Field(ge=0, le=100)

    @field_validator("original_price", "discount_percent", mode="before")
    @classmethod
    def convert_string_to_float(cls, v: Any) -> float:
        """Convert string prices to float."""
        if isinstance(v, str):
            # Remove currency symbols and whitespace
            v = v.replace("$", "").replace(",", "").strip()
            return float(v)
        return v

    @field_validator("original_price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


class Person(BaseModel):
    """Person model with mode='before' validator."""

    name: str
    birth_year: int

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: Any) -> str:
        """Clean and normalize name before validation."""
        if isinstance(v, str):
            # Remove extra whitespace and capitalize
            return " ".join(v.split()).title()
        return v

    @model_validator(mode="before")
    @classmethod
    def extract_from_dict(cls, data: Any) -> Any:
        """Handle alternative input formats."""
        if isinstance(data, dict):
            # Support 'full_name' as alternative to 'name'
            if "full_name" in data and "name" not in data:
                data["name"] = data.pop("full_name")
            # Support 'birthYear' as alternative to 'birth_year'
            if "birthYear" in data and "birth_year" not in data:
                data["birth_year"] = data.pop("birthYear")
        return data


class CreditCard(BaseModel):
    """Credit card with Luhn algorithm validation."""

    number: str = Field(min_length=13, max_length=19)
    expiry_month: int = Field(ge=1, le=12)
    expiry_year: int
    cvv: str = Field(min_length=3, max_length=4)

    @field_validator("number")
    @classmethod
    def validate_luhn(cls, v: str) -> str:
        """Validate card number using Luhn algorithm."""
        # Remove spaces and dashes
        digits = v.replace(" ", "").replace("-", "")

        if not digits.isdigit():
            raise ValueError("Card number must contain only digits")

        # Luhn algorithm
        total = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        if total % 10 != 0:
            raise ValueError("Invalid card number (failed Luhn check)")

        return digits

    @model_validator(mode="after")
    def validate_expiry(self) -> "CreditCard":
        """Ensure card is not expired."""
        today = datetime.now()
        # Card is valid through the end of the expiry month
        if self.expiry_year < today.year:
            raise ValueError("Card has expired")
        if self.expiry_year == today.year and self.expiry_month < today.month:
            raise ValueError("Card has expired")
        return self


def main() -> None:
    """Run the validators example."""
    print("Example 2: Custom Validators")
    print("=" * 50)

    # User registration with password matching
    print("\n1. User registration with field and model validators:")
    try:
        user = UserRegistration(
            username="Alice_Smith",
            email="ALICE@Example.COM",
            password="SecurePass123",
            password_confirm="SecurePass123",
        )
        print(f"   Username (normalized): {user.username}")
        print(f"   Email (normalized): {user.email}")
    except ValidationError as e:
        print(f"   Error: {e}")

    # Password mismatch
    print("\n2. Password mismatch validation:")
    try:
        UserRegistration(
            username="bob",
            email="bob@example.com",
            password="SecurePass123",
            password_confirm="DifferentPass123",
        )
    except ValidationError as e:
        print(f"   Error: {e.errors()[0]['msg']}")

    # Weak password
    print("\n3. Password strength validation:")
    try:
        UserRegistration(
            username="charlie",
            email="charlie@example.com",
            password="weakpassword",
            password_confirm="weakpassword",
        )
    except ValidationError as e:
        print(f"   Error: {e.errors()[0]['msg']}")

    # Date range validation
    print("\n4. Date range cross-field validation:")
    try:
        DateRange(start_date=date(2024, 12, 1), end_date=date(2024, 1, 1))
    except ValidationError as e:
        print(f"   Error: {e.errors()[0]['msg']}")

    valid_range = DateRange(
        start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), name="Year 2024"
    )
    print(f"   Valid range: {valid_range.start_date} to {valid_range.end_date}")

    # Price transformation
    print("\n5. Data transformation in validators:")
    price = PriceWithDiscount(original_price="$1,299.999", discount_percent="15")
    print(f"   Original price: ${price.original_price}")
    print(f"   Discount: {price.discount_percent}%")

    # Person with mode='before' validators
    print("\n6. Mode='before' validators for data normalization:")
    person1 = Person(name="  john   doe  ", birth_year=1990)
    print(f"   Cleaned name: {person1.name}")

    person2 = Person.model_validate({"full_name": "jane smith", "birthYear": 1985})
    print(f"   Alternative input format: {person2.name}, {person2.birth_year}")

    # Credit card validation
    print("\n7. Credit card Luhn validation:")
    try:
        # This is a test card number that passes Luhn
        card = CreditCard(
            number="4111 1111 1111 1111",  # Test Visa number
            expiry_month=12,
            expiry_year=2030,
            cvv="123",
        )
        print(f"   Valid card number: {card.number[:4]}...{card.number[-4:]}")
    except ValidationError as e:
        print(f"   Error: {e}")

    # Invalid card number
    print("\n8. Invalid card number (fails Luhn):")
    try:
        CreditCard(
            number="4111111111111112",  # Invalid
            expiry_month=12,
            expiry_year=2030,
            cvv="123",
        )
    except ValidationError as e:
        print(f"   Error: {e.errors()[0]['msg']}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
