"""Example 4: Model Composition

This example demonstrates model inheritance, nested models,
generic models, and discriminated unions.
"""

from datetime import datetime
from typing import Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing_extensions import Annotated


# =============================================================================
# Part 1: Model Inheritance
# =============================================================================


class BaseEntity(BaseModel):
    """Base model for all entities with common fields."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class TimestampMixin(BaseModel):
    """Mixin for adding timestamp behavior."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def touch(self) -> "TimestampMixin":
        """Update the updated_at timestamp."""
        return self.model_copy(update={"updated_at": datetime.now()})


class User(BaseEntity):
    """User model inheriting from BaseEntity."""

    username: str = Field(min_length=3, max_length=50)
    email: str
    is_active: bool = True


class AdminUser(User):
    """Admin user with additional permissions."""

    permissions: list[str] = Field(default_factory=list)
    admin_level: int = Field(default=1, ge=1, le=10)

    @computed_field
    @property
    def is_super_admin(self) -> bool:
        """Check if user is super admin."""
        return self.admin_level >= 9


# =============================================================================
# Part 2: Nested Models
# =============================================================================


class Address(BaseModel):
    """Address model for nesting."""

    street: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    postal_code: str
    country: str = "US"

    @computed_field
    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"


class ContactInfo(BaseModel):
    """Contact information with nested address."""

    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None


class Company(BaseModel):
    """Company with nested contact info and list of employees."""

    name: str
    contact: ContactInfo
    employees: list[User] = Field(default_factory=list)

    @computed_field
    @property
    def employee_count(self) -> int:
        """Get number of employees."""
        return len(self.employees)


# =============================================================================
# Part 3: Generic Models
# =============================================================================

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int = 1
    page_size: int = 10

    @computed_field
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.page_size - 1) // self.page_size

    @computed_field
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @computed_field
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Part 4: Discriminated Unions
# =============================================================================


class EmailNotification(BaseModel):
    """Email notification type."""

    type: Literal["email"] = "email"
    to: str
    subject: str
    body: str


class SMSNotification(BaseModel):
    """SMS notification type."""

    type: Literal["sms"] = "sms"
    phone_number: str
    message: str = Field(max_length=160)


class PushNotification(BaseModel):
    """Push notification type."""

    type: Literal["push"] = "push"
    device_token: str
    title: str
    body: str
    data: dict[str, str] = Field(default_factory=dict)


# Discriminated union - Pydantic uses 'type' field to determine which model
Notification = Annotated[
    Union[EmailNotification, SMSNotification, PushNotification],
    Field(discriminator="type"),
]


class NotificationBatch(BaseModel):
    """Batch of notifications of mixed types."""

    batch_id: str
    notifications: list[Notification]

    @computed_field
    @property
    def notification_counts(self) -> dict[str, int]:
        """Count notifications by type."""
        counts: dict[str, int] = {"email": 0, "sms": 0, "push": 0}
        for notification in self.notifications:
            counts[notification.type] += 1
        return counts


def main() -> None:
    """Run the model composition example."""
    print("Example 4: Model Composition")
    print("=" * 50)

    # Model inheritance
    print("\n1. Model Inheritance:")
    user = User(id=1, username="alice", email="alice@example.com")
    print(f"   User: {user.username}, created: {user.created_at.date()}")

    admin = AdminUser(
        id=2,
        username="admin",
        email="admin@example.com",
        permissions=["read", "write", "delete"],
        admin_level=9,
    )
    print(f"   Admin: {admin.username}, super admin: {admin.is_super_admin}")

    # Nested models
    print("\n2. Nested Models:")
    company = Company(
        name="TechCorp",
        contact=ContactInfo(
            email="info@techcorp.com",
            phone="555-0100",
            address=Address(
                street="123 Tech Lane",
                city="San Francisco",
                state="CA",
                postal_code="94102",
            ),
        ),
        employees=[
            User(id=10, username="emp1", email="emp1@techcorp.com"),
            User(id=11, username="emp2", email="emp2@techcorp.com"),
        ],
    )
    print(f"   Company: {company.name}")
    print(f"   Address: {company.contact.address.full_address}")
    print(f"   Employees: {company.employee_count}")

    # Parse nested from dict
    company_dict = {
        "name": "StartupXYZ",
        "contact": {"email": "hello@startup.xyz", "address": None},
    }
    parsed_company = Company.model_validate(company_dict)
    print(f"   Parsed company: {parsed_company.name}")

    # Generic models
    print("\n3. Generic Models:")
    users = [
        User(id=i, username=f"user{i}", email=f"user{i}@example.com") for i in range(1, 26)
    ]

    paginated = PaginatedResponse[User](
        items=users[:10],
        total=25,
        page=1,
        page_size=10,
    )
    print(f"   Total items: {paginated.total}")
    print(f"   Total pages: {paginated.total_pages}")
    print(f"   Has next: {paginated.has_next}")
    print(f"   Items on page: {len(paginated.items)}")

    # API Response wrapper
    api_success = APIResponse[User](
        success=True,
        data=User(id=1, username="alice", email="alice@example.com"),
    )
    print(f"   API success response: {api_success.success}, user: {api_success.data.username}")

    api_error = APIResponse[User](success=False, error="User not found")
    print(f"   API error response: {api_error.success}, error: {api_error.error}")

    # Discriminated unions
    print("\n4. Discriminated Unions:")
    batch = NotificationBatch(
        batch_id="batch-001",
        notifications=[
            EmailNotification(
                to="user@example.com",
                subject="Welcome!",
                body="Welcome to our platform.",
            ),
            SMSNotification(phone_number="+15551234567", message="Your code is 123456"),
            PushNotification(
                device_token="abc123",
                title="New Message",
                body="You have a new message",
                data={"message_id": "msg-001"},
            ),
            EmailNotification(
                to="other@example.com", subject="Update", body="Check out our new features."
            ),
        ],
    )
    print(f"   Batch ID: {batch.batch_id}")
    print(f"   Notification counts: {batch.notification_counts}")

    # Parse discriminated union from dict
    notification_data = {"type": "sms", "phone_number": "+15559876543", "message": "Hello!"}

    # The union type needs to be used in a model for proper parsing
    parsed_batch = NotificationBatch.model_validate(
        {"batch_id": "batch-002", "notifications": [notification_data]}
    )
    print(f"   Parsed notification type: {parsed_batch.notifications[0].type}")
    print(f"   Is SMS: {isinstance(parsed_batch.notifications[0], SMSNotification)}")

    # Serialization preserves types
    print("\n5. Serialization of composed models:")
    batch_dict = batch.model_dump()
    print(f"   Batch dict keys: {list(batch_dict.keys())}")
    print(f"   First notification type: {batch_dict['notifications'][0]['type']}")

    # JSON serialization
    batch_json = batch.model_dump_json(indent=2)
    print(f"   JSON length: {len(batch_json)} characters")

    # Re-parse maintains types
    reparsed_batch = NotificationBatch.model_validate_json(batch_json)
    print(f"   Reparsed counts: {reparsed_batch.notification_counts}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
